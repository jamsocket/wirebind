from diffusers import StableDiffusionPipeline, EulerDiscreteScheduler
import torch
from diffusers.loaders import TextualInversionLoaderMixin
from diffusers.utils import randn_tensor
from typing import Optional
from threading import Thread
import io

from wirebind.rpc import expose
from wirebind.binds.atom import Atom
from wirebind.sender import Sender


MODEL_ID = "stabilityai/stable-diffusion-2"

class StableDiffusion:
    prompt = Atom("two dogs playing tug with a french baguette")
    result = Atom(None)
    thread: Optional[Thread] = None
    pipe: StableDiffusionPipeline
    latents: torch.Tensor
    prompt_embeds: torch.Tensor
    num_timesteps: int = 50
    current_timestep: int = 0

    def prepare_latents(self):
        self.latents = self.pipe.prepare_latents(
            1,
            self.pipe.unet.config.in_channels,
            self.pipe.unet.config.sample_size * self.pipe.vae_scale_factor,
            self.pipe.unet.config.sample_size * self.pipe.vae_scale_factor,
            torch.float16,
            self.pipe._execution_device,
            None,
            None,
        )


    def prepare_prompt_embeds(self):
        self.prompt_embeds = self.pipe._encode_prompt(
            self.prompt.get(),
            self.pipe._execution_device,
            1,
            True,
        )


    def __init__(self):
        self.pipe = StableDiffusionPipeline.from_pretrained(MODEL_ID, torch_dtype=torch.float16)
        self.pipe.to("cuda")
        self.prepare_latents()
        self.prepare_prompt_embeds()

        self.thread = Thread(target=self.run_diffusion)
        self.thread.start()


    def latents_to_image(self):
        latents = 1 / self.pipe.vae.config.scaling_factor * self.latents
        image = self.pipe.vae.decode(latents).sample
        image = (image / 2 + 0.5).clamp(0, 1)
        # we always cast to float32 as this does not cause significant overhead and is compatible with bfloat16
        image = image.cpu().detach().permute(0, 2, 3, 1).float().numpy()
        image, _ = self.pipe.run_safety_checker(image, 'cuda', self.prompt_embeds.dtype)
        image = self.pipe.numpy_to_pil(image)
        return image[0]


    def update_image(self):
        image = self.latents_to_image()
        bytes = io.BytesIO()
        image.save(bytes, format='jpeg')
        self.result.set(bytes.getvalue())


    @torch.no_grad()
    def run_diffusion(self):
        self.pipe.scheduler.set_timesteps(50)
        timesteps = self.pipe.scheduler.timesteps
        prompt_embeds = self.prompt_embeds

        guidance_scale = 7.5
        do_classifier_free_guidance = True

        extra_step_kwargs = self.pipe.prepare_extra_step_kwargs(None, 0.0)

        for i, t in enumerate(timesteps):
            print(i)
            # expand the latents if we are doing classifier free guidance
            latent_model_input = torch.cat([self.latents] * 2) if do_classifier_free_guidance else self.latents
            latent_model_input = self.pipe.scheduler.scale_model_input(latent_model_input, t)

            # predict the noise residual
            noise_pred = self.pipe.unet(
                latent_model_input,
                t,
                encoder_hidden_states=prompt_embeds,
                return_dict=False,
            )[0]

            # perform guidance
            if do_classifier_free_guidance:
                noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
                noise_pred = noise_pred_uncond + guidance_scale * (noise_pred_text - noise_pred_uncond)

            # # compute the previous noisy sample x_t -> x_t-1
            self.latents = self.pipe.scheduler.step(noise_pred, t, self.latents, **extra_step_kwargs, return_dict=False)[0]

            if i % 10 == 0:
               self.update_image()
        self.update_image()


STABLE_DIFFUSION = StableDiffusion()


def root(message: any):
    reply = message["reply"]

    result = {
        "prompt": STABLE_DIFFUSION.prompt,
        "result": STABLE_DIFFUSION.result,
    }
    
    reply.send(result)

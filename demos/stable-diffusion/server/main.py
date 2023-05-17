from diffusers import StableDiffusionPipeline
import torch
from typing import Optional
from threading import Thread, Event
import io

from wirebind.binds.atom import Atom
from wirebind.sender import Sender


MODEL_ID = "stabilityai/stable-diffusion-2"


class StableDiffusion:
    prompts = Atom([
        {"prompt": "a hamburger", "weight": 1.0},
        {"prompt": "an ice cream sandwich", "weight": 1.0},
    ])
    progress = Atom(0)
    prompts_dirty: Event
    result = Atom(None)
    thread: Optional[Thread] = None
    pipe: StableDiffusionPipeline
    latents: torch.Tensor
    prompt_embeds: torch.Tensor
    num_timesteps: int = 10
    current_timestep: int = 0


    def __init__(self):
        self.pipe = StableDiffusionPipeline.from_pretrained(MODEL_ID, torch_dtype=torch.float16)
        self.pipe.to("cuda")

        self.prompts_dirty = Event()
        self.prompts_dirty.set()

        self.prepare_latents()

        self.prompts.add_listener(Sender(lambda _: self.prompts_dirty.set()))

        self.thread = Thread(target=self.run_diffusion)
        self.thread.start()


    def prepare_latents(self, _=None):
        self.prompts_dirty.set()
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
        embedded_prompts = [
            (p["weight"], self.pipe._encode_prompt(p["prompt"], self.pipe._execution_device, 1, True))
            for p in self.prompts.get()
        ]

        desired_norm = sum(p.norm() * w for (w, p) in embedded_prompts) / sum(w for (w, _) in embedded_prompts)
        pp = sum(w * pe for (w, pe) in embedded_prompts)
        pp = pp * desired_norm / pp.norm()
        self.prompt_embeds = pp


    def latents_to_image(self, latents):
        latents = 1 / self.pipe.vae.config.scaling_factor * latents
        image = self.pipe.vae.decode(latents).sample
        image = (image / 2 + 0.5).clamp(0, 1)
        image = image.cpu().detach().permute(0, 2, 3, 1).float().numpy()
        image, _ = self.pipe.run_safety_checker(image, 'cuda', self.prompt_embeds.dtype)
        image = self.pipe.numpy_to_pil(image)
        return image[0]


    def update_image(self, latents):
        image = self.latents_to_image(latents)
        bytes = io.BytesIO()
        image.save(bytes, format='jpeg')
        self.result.set(bytes.getvalue())


    def run_diffusion(self):
        with torch.no_grad():
            while True:
                self.prompts_dirty.clear()
                self.prepare_prompt_embeds()

                self.pipe.scheduler.set_timesteps(self.num_timesteps)
                timesteps = self.pipe.scheduler.timesteps
                prompt_embeds = self.prompt_embeds

                guidance_scale = 7.5
                do_classifier_free_guidance = True

                extra_step_kwargs = self.pipe.prepare_extra_step_kwargs(None, 0.0)
                latents = self.latents.clone()

                for i, t in enumerate(timesteps):
                    if self.prompts_dirty.is_set():
                        break

                    print(i)
                    latent_model_input = torch.cat([latents] * 2) if do_classifier_free_guidance else self.latents
                    latent_model_input = self.pipe.scheduler.scale_model_input(latent_model_input, t)

                    noise_pred = self.pipe.unet(
                        latent_model_input,
                        t,
                        encoder_hidden_states=prompt_embeds,
                        return_dict=False,
                    )[0]

                    if do_classifier_free_guidance:
                        noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
                        noise_pred = noise_pred_uncond + guidance_scale * (noise_pred_text - noise_pred_uncond)

                    latents = self.pipe.scheduler.step(noise_pred, t, latents, **extra_step_kwargs, return_dict=False)[0]

                    if i % 2 == 0:
                        self.update_image(latents)
                    self.progress.set(i / (len(timesteps) - 1))

                self.update_image(latents)

                print("waiting")
                self.prompts_dirty.wait()
                print("done waiting")


STABLE_DIFFUSION = StableDiffusion()


def root(message: any):
    reply = message["reply"]

    result = {
        "prompts": STABLE_DIFFUSION.prompts,
        "result": STABLE_DIFFUSION.result,
        "progress": STABLE_DIFFUSION.progress,
        "shuffle_latents": Sender(STABLE_DIFFUSION.prepare_latents),
    }
    
    reply.send(result)

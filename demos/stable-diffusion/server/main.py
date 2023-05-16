from diffusers import StableDiffusionPipeline
import torch
from typing import Optional
from threading import Thread, Event
import io
import numpy as np

from wirebind.binds.atom import Atom
from wirebind.sender import Sender


MODEL_ID = "stabilityai/stable-diffusion-2"

def slerp(t, v0, v1, DOT_THRESHOLD=0.9995):
    """ helper function to spherically interpolate two arrays v1 v2 """

    if not isinstance(v0, np.ndarray):
        inputs_are_torch = True
        input_device = v0.device
        v0 = v0.cpu().numpy()
        v1 = v1.cpu().numpy()

    dot = np.sum(v0 * v1 / (np.linalg.norm(v0) * np.linalg.norm(v1)))
    if np.abs(dot) > DOT_THRESHOLD:
        v2 = (1 - t) * v0 + t * v1
    else:
        theta_0 = np.arccos(dot)
        sin_theta_0 = np.sin(theta_0)
        theta_t = theta_0 * t
        sin_theta_t = np.sin(theta_t)
        s0 = np.sin(theta_0 - theta_t) / sin_theta_0
        s1 = sin_theta_t / sin_theta_0
        v2 = s0 * v0 + s1 * v1

    if inputs_are_torch:
        v2 = torch.from_numpy(v2).to(input_device)

    return v2


class StableDiffusion:
    prompts = Atom([
        {"prompt": "two dogs playing tug with a french baguette", "weight": 1.0},
        {"prompt": "an ice cream sandwich", "weight": 1.0},
    ])
    prompts_dirty: Event
    result = Atom(None)
    thread: Optional[Thread] = None
    pipe: StableDiffusionPipeline
    latents: torch.Tensor
    prompt_embeds: torch.Tensor
    num_timesteps: int = 45
    current_timestep: int = 0


    def __init__(self):
        self.pipe = StableDiffusionPipeline.from_pretrained(MODEL_ID, torch_dtype=torch.float16)
        self.pipe.to("cuda")
        self.prepare_latents()

        self.prompts_dirty = Event()
        self.prompts_dirty.set()

        self.prompts.add_listener(Sender(lambda _: self.prompts_dirty.set()))

        self.thread = Thread(target=self.run_diffusion)
        self.thread.start()


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
        [p1, p2] = self.prompts.get()
        p1embeds = self.pipe._encode_prompt(
            p1["prompt"],
            self.pipe._execution_device,
            1,
            True,
        )

        p2embeds = self.pipe._encode_prompt(
            p2["prompt"],
            self.pipe._execution_device,
            1,
            True,
        )
        f = p1["weight"] / (p1["weight"] + p2["weight"])

        self.prompt_embeds = slerp(
            1-f,
            p1embeds,
            p2embeds,
        )


    def latents_to_image(self):
        latents = 1 / self.pipe.vae.config.scaling_factor * self.latents
        image = self.pipe.vae.decode(latents).sample
        image = (image / 2 + 0.5).clamp(0, 1)
        image = image.cpu().detach().permute(0, 2, 3, 1).float().numpy()
        image, _ = self.pipe.run_safety_checker(image, 'cuda', self.prompt_embeds.dtype)
        image = self.pipe.numpy_to_pil(image)
        return image[0]


    def update_image(self):
        image = self.latents_to_image()
        bytes = io.BytesIO()
        image.save(bytes, format='jpeg')
        self.result.set(bytes.getvalue())


    def run_diffusion(self):
        with torch.no_grad():
            while True:
                self.prompts_dirty.clear()
                self.prepare_latents()
                self.prepare_prompt_embeds()

                self.pipe.scheduler.set_timesteps(self.num_timesteps)
                timesteps = self.pipe.scheduler.timesteps
                prompt_embeds = self.prompt_embeds

                guidance_scale = 7.5
                do_classifier_free_guidance = True

                extra_step_kwargs = self.pipe.prepare_extra_step_kwargs(None, 0.0)

                for i, t in enumerate(timesteps):
                    if self.prompts_dirty.is_set():
                        break

                    print(i)
                    latent_model_input = torch.cat([self.latents] * 2) if do_classifier_free_guidance else self.latents
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

                    self.latents = self.pipe.scheduler.step(noise_pred, t, self.latents, **extra_step_kwargs, return_dict=False)[0]

                    if i % 10 == 0:
                        self.update_image()

                self.update_image()

                print("waiting")
                self.prompts_dirty.wait()
                print("done waiting")


STABLE_DIFFUSION = StableDiffusion()


def root(message: any):
    reply = message["reply"]

    result = {
        "prompts": STABLE_DIFFUSION.prompts,
        "result": STABLE_DIFFUSION.result,
    }
    
    reply.send(result)

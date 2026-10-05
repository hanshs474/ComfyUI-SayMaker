import io
import os
import time

import numpy as np
import torch
from PIL import Image

from . import saymaker_client as sm

RATIOS = ["1:1", "16:9", "9:16", "4:3", "3:4"]

KEY_TOOLTIP = (
    "Key from saymaker.ai/settings/apikeys (new accounts get sign-up credits). "
    "Leave empty to read SAYMAKER_API_KEY from the environment."
)


def _to_tensor(data: bytes) -> torch.Tensor:
    img = Image.open(io.BytesIO(data)).convert("RGB")
    return torch.from_numpy(np.asarray(img).astype(np.float32) / 255.0)[None, ...]


def _to_png(image: torch.Tensor) -> bytes:
    arr = (image[0].cpu().numpy().clip(0, 1) * 255).astype(np.uint8)
    buf = io.BytesIO()
    Image.fromarray(arr).save(buf, format="PNG")
    return buf.getvalue()


def _output_dir() -> str:
    try:
        import folder_paths  # ComfyUI's own module, present when running inside ComfyUI

        return folder_paths.get_output_directory()
    except ImportError:
        return os.getcwd()


class SayMakerGenerateImage:
    CATEGORY = "SayMaker"
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "url")
    FUNCTION = "generate"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "default": "matte black ceramic mug on pale oak, soft window light"}),
                "aspect_ratio": (RATIOS, {"default": "1:1"}),
                "model": ("STRING", {"default": "saymaker-image-v1", "tooltip": "e.g. nano-banana-2, gpt-image-2-5-flare, seedream-5-pro"}),
            },
            "optional": {
                "api_key": ("STRING", {"default": "", "tooltip": KEY_TOOLTIP}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFF, "tooltip": "Change to force a new run"}),
            },
        }

    def generate(self, prompt, aspect_ratio, model, api_key="", seed=0):
        url = sm.generate(prompt, aspect_ratio=aspect_ratio, model=model or None, api_key=api_key or None)
        return (_to_tensor(sm.download(url)), url)


class SayMakerEditImage:
    CATEGORY = "SayMaker"
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "url")
    FUNCTION = "edit"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "instruction": ("STRING", {"multiline": True, "default": "put the product on a white marble surface; keep the label unchanged"}),
                "model": ("STRING", {"default": "nano-banana-2-lite", "tooltip": "e.g. nano-banana-2, gpt-image-2-5-flare, seedream-5-pro"}),
            },
            "optional": {
                "api_key": ("STRING", {"default": "", "tooltip": KEY_TOOLTIP}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFF, "tooltip": "Change to force a new run"}),
            },
        }

    def edit(self, image, instruction, model, api_key="", seed=0):
        source = sm.upload_png(_to_png(image))
        url = sm.generate(instruction, image_url=source, model=model or None, api_key=api_key or None)
        return (_to_tensor(sm.download(url)), url)


class SayMakerImageToVideo:
    """Animate an image into a clip. Saves the MP4 to ComfyUI's output folder and returns its path and URL."""

    CATEGORY = "SayMaker"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("video_path", "url")
    FUNCTION = "animate"
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "prompt": ("STRING", {"multiline": True, "default": "the camera slowly orbits the subject while soft light sweeps across it"}),
                "model": ("STRING", {"default": "minimax-h3-fast", "tooltip": "minimax-h3-fast runs on a free account; veo-3-1, kling-3-0, seedance-2 need a plan or a credit pack"}),
                "duration": ("INT", {"default": 6, "min": 2, "max": 30, "tooltip": "Seconds, where the model offers a choice"}),
            },
            "optional": {
                "api_key": ("STRING", {"default": "", "tooltip": KEY_TOOLTIP}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFF, "tooltip": "Change to force a new run"}),
            },
        }

    def animate(self, image, prompt, model, duration, api_key="", seed=0):
        source = sm.upload_png(_to_png(image))
        url = sm.generate_video(prompt, image_url=source, model=model or sm.DEFAULT_VIDEO_MODEL, duration=duration, api_key=api_key or None)
        path = os.path.join(_output_dir(), f"saymaker-{int(time.time())}.mp4")
        with open(path, "wb") as f:
            f.write(sm.download(url))
        return {"ui": {"text": [url]}, "result": (path, url)}


NODE_CLASS_MAPPINGS = {
    "SayMakerGenerateImage": SayMakerGenerateImage,
    "SayMakerEditImage": SayMakerEditImage,
    "SayMakerImageToVideo": SayMakerImageToVideo,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "SayMakerGenerateImage": "SayMaker Generate Image",
    "SayMakerEditImage": "SayMaker Edit Image",
    "SayMakerImageToVideo": "SayMaker Image to Video",
}

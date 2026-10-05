# ComfyUI-SayMaker

ComfyUI nodes that run [SayMaker](https://saymaker.ai/?utm_source=comfyui&utm_medium=node)'s image and video models from a graph: generate an image, edit one, or animate it into a clip with Veo 3.1, Kling 3.0, Seedance 2.0 or MiniMax H3. One API key covers the whole shelf, including Nano Banana 2, GPT Image 2.5 and Seedream 5.0. No local GPU, no model downloads.

| Node | Inputs | Outputs |
|---|---|---|
| **SayMaker Generate Image** | prompt, aspect ratio, model | IMAGE, url |
| **SayMaker Edit Image** | IMAGE, instruction, model | IMAGE, url |
| **SayMaker Image to Video** | IMAGE, prompt, model, duration | path of the saved MP4 (in ComfyUI's output folder), url |

## Install

ComfyUI Manager: search **ComfyUI-SayMaker**. Or clone into `custom_nodes`:

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/hanshs474/ComfyUI-SayMaker
```

No extra Python dependencies: the client uses the standard library, and the nodes use the torch, numpy and Pillow that ComfyUI already ships.

## API key

Sign up on [saymaker.ai](https://saymaker.ai/?utm_source=comfyui&utm_medium=node) (new accounts get sign-up credits), create a key at [saymaker.ai/settings/apikeys](https://saymaker.ai/settings/apikeys?utm_source=comfyui&utm_medium=node), and either paste it into the node's `api_key` field or set `SAYMAKER_API_KEY` before starting ComfyUI.

## Models

- Images: `saymaker-image-v1` (cheapest), `nano-banana-2-lite` (default for edits), `nano-banana-2`, `gpt-image-2-5-flare`, `seedream-5-pro`, `qwen-image-3-pro`
- Video: `minimax-h3-fast` (runs on a free account), `veo-3-1`, `kling-3-0`, `seedance-2`, `seedance-2-5`, `wan-3-0`. The ones beyond `minimax-h3-fast` need a plan or a credit pack ([pricing](https://saymaker.ai/pricing?utm_source=comfyui&utm_medium=node)).

For an edit, the instruction names the change **and what must stay** ("keep the label unchanged"). That second half is what decides whether the edit holds.

Runs on a free account wait in a queue before they start, and video takes minutes; the node blocks until the file is ready. Change `seed` to force a new run with the same inputs. Every run also lands in your library at [saymaker.ai/history](https://saymaker.ai/history?utm_source=comfyui&utm_medium=node).

MIT licensed.

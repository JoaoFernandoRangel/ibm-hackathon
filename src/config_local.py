import torch

MODEL_LOCAL_NAME = "ibm-granite/granite-3.0-2b-instruct"

LOCAL_MODEL_CONFIG = {
    "load_in_4bit": True,
    "device_map": "auto",
    "torch_dtype": torch.float16
}

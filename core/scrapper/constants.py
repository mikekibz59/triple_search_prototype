from enum import Enum


class SupportedLLMs(Enum):
    GROQ_CLOUD_DEEPSEEK_R1 = "groq/deepseek-r1-distill-llama-70b"


class SupportedBrowersers(Enum):
    CHROMIUM = "chromium"


class Extractors(Enum):
    GENERIC = "generic"

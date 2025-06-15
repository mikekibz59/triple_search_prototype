class GenericExtractorBaseException(Exception):
    """Base exception class for Generic extractor"""


class GenericExtractorImproperlyConfiguredException(GenericExtractorBaseException):
    message = "GROQ_CLOUD_API_KEY is not missing or not set"

    def __init__(self):
        super().__init__(self.message)


class ScrapperServiceException(Exception):
    pass

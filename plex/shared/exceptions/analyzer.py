from plex.shared.exceptions.base import PLEXError


class AnalyzerInitializationError(PLEXError):
    def __init__(self, message: str = "Failed to construct the LLM from provided configs"):
        self.message = message
        super().__init__(self.message)

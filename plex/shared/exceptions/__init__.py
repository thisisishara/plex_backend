class PLEXError(Exception):
    def __init__(self, message: str = "PLEX Base Error."):
        self.message = message
        super().__init__(self.message)

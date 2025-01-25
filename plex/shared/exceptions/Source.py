from plex.shared.exceptions import PLEXError


class SourceFileNotSpecifiedError(PLEXError):
    def __init__(self, message: str = "A valid source file is not attached"):
        self.message = message
        super().__init__(self.message)


class EmptySourceFileContentError(PLEXError):
    def __init__(self, message: str = "Attached source file content is empty"):
        self.message = message
        super().__init__(self.message)


class SourceFileExistsError(PLEXError):
    def __init__(self, message: str = "The source file already exists"):
        self.message = message
        super().__init__(self.message)

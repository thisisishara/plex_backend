from plex.shared.exceptions.base import PLEXError


class DataFileNotSpecifiedError(PLEXError):
    def __init__(self, message: str = "A valid reference data file is not attached"):
        self.message = message
        super().__init__(self.message)


class InsufficientDataPointsError(PLEXError):
    def __init__(self, message: str = "Insufficient data points for evaluation"):
        self.message = message
        super().__init__(self.message)


class ColumnCountMismatchError(PLEXError):
    def __init__(self, message: str = "Mismatch in column counts between extracted and reference data"):
        self.message = message
        super().__init__(self.message)


class CSVParsingError(PLEXError):
    def __init__(self, message: str = "Could not parse the CSV file data"):
        self.message = message
        super().__init__(self.message)

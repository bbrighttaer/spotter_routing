class ApplicationError(Exception):
    def __init__(self, message, extra=None):
        super().__init__(message)

        self.message = message
        self.extra = extra or {}

    def __str__(self):
        return f"{self.message} - {self.extra}"

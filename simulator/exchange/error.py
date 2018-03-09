class Error(Exception):
    """Base class for exception in this module"""
    pass


class NotSupportedTokenError(Error):
    """Raise when user request a token that is not supported"""
    pass

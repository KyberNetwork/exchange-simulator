class Error(Exception):
    """Base class for exception in this module"""
    pass


class NotSupportedTokenError(Error):
    """Raise when user request a token that is not supported"""
    pass


class TradeError(Exception):
    """Raise when exchange is disable trade function"""
    pass


class WithdrawError(Exception):
    """Raise when exchange is disable withdrawal"""
    pass


class OrderNotFoundError(Exception):
    """Raise when order id is not exist in db"""
    pass

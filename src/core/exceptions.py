class WalletBaseException(Exception):
    pass

class WalletNotFoundError(WalletBaseException):
    pass

class InsufficientFundsError(WalletBaseException):
    pass

class NegativeBalanceError(WalletBaseException):
    pass
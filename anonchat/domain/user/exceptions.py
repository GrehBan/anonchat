from anonchat.domain.base.exceptions import DomainException


class UserNotFoundException(DomainException):
    pass

class UserAlreadyInChatException(DomainException):
    pass


class UserIsBusyException(DomainException):
    pass


class UserIsSelfException(DomainException):
    pass

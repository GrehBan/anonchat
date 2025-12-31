from anonchat.domain.base.exceptions import NotFoundException, PermissionDeniedException, ConcurrencyException, SystemIsBusyException


class UserNotFoundException(NotFoundException):
    pass


class UserAlreadyInChatException(ConcurrencyException):
    pass


class UserIsBusyException(SystemIsBusyException):
    pass


class UserIsSelfException(PermissionDeniedException):
    pass

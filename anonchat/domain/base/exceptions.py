class DomainException(Exception):
    pass


class PermissionDeniedException(DomainException):
    pass


class ValidationException(DomainException):
    pass


class NotFoundException(DomainException):
    pass


class ConcurrencyException(DomainException):
    pass


class SystemIsBusyException(DomainException):
    pass

class BookNotFoundError(Exception):
    pass


class MemberNotFoundError(Exception):
    pass


class BookNotAvailableError(Exception):
    pass


class BookAlreadyExistsError(Exception):
    pass


class MemberAlreadyExistsError(Exception):
    pass


class InvalidCopyNumberError(Exception):
    pass


class BookNotBorrowedError(Exception):
    pass
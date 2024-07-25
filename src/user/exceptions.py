class NotAuthorizedException(Exception):
    message = "Not Authorized"


class UserNotFoundException(Exception):
    message = "User Not Found"


class UserVersionConflictException(Exception):
    message = "User Version Conflict"

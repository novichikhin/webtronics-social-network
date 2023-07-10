from webtronics_social_network.types.errors.common import Error


class NotValidateCredentials(Error):
    detail: str = "Could not validate credentials"


class AuthenticationUserNotFound(Error):
    detail: str = "Authentication user not found"


class UserNotFound(Error):
    detail: str = "User not found"


class WrongUsernameOrPassword(Error):
    detail: str = "Wrong username (email) or password"


class UsernameAlreadyExists(Error):
    detail: str = "User username already exists"

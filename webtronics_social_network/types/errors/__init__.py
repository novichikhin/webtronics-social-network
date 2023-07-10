from webtronics_social_network.types.errors.common import Validation, SomethingWentWrong
from webtronics_social_network.types.errors.user import (
    NotValidateCredentials,
    AuthenticationUserNotFound,
    UserNotFound,
    WrongUsernameOrPassword,
    UsernameAlreadyExists
)
from webtronics_social_network.types.errors.post import (
    PostNotFound,
    PostNotFoundOrNotCreator,
    UnableUpdatePost
)
from webtronics_social_network.types.errors.reaction import (
    ReactionNotFound,
    CanOnlyPostReactionsOtherPeoplesPosts
)

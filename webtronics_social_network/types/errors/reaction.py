from webtronics_social_network.types.errors.common import Error


class ReactionNotFound(Error):
    detail: str = "Reaction not found"


class CanOnlyPostReactionsOtherPeoplesPosts(Error):
    detail: str = "You can only post reactions to other people's posts"

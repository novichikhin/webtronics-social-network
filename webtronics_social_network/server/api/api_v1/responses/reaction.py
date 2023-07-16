from webtronics_social_network.server.api.api_v1.responses.common import Error


class ReactionNotFound(Error):
    detail: str = "Reaction not found"


class CanOnlyPostReactionsOtherPeoplesPosts(Error):
    detail: str = "You can only post reactions to other people's posts"

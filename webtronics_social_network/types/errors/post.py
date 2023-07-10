from webtronics_social_network.types.errors.common import Error


class PostNotFound(Error):
    detail: str = "Post not found"


class PostNotFoundOrNotCreator(Error):
    detail: str = "Post not found or you are not the creator of this post"


class UnableUpdatePost(Error):
    detail: str = "Unable to update post"

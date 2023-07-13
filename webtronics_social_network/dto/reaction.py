import uuid
from dataclasses import dataclass

from webtronics_social_network import enums


@dataclass
class Reaction:
    id: uuid.UUID

    post_id: uuid.UUID
    user_id: uuid.UUID
    type: enums.ReactionType

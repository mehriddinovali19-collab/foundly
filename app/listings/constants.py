from enum import Enum

class ListingType(str, Enum):
    LOST = "LOST"
    FOUND = "FOUND"


class ListingStatus(str, Enum):
    ACTIVE = "ACTIVE"
    CLAIMED = "CLAIMED"
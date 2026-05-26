from enum import Enum


class GenderEnum(str, Enum):
    male = "male"
    female = "female"
    other = "other"
    prefer_not_to_say = "prefer_not_to_say"


class VisibilityEnum(str, Enum):
    private = "private"
    public = "public"


class SortOrderEnum(str, Enum):
    asc = "asc"
    desc = "desc"
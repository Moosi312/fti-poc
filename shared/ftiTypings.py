from typing import TypedDict, Dict, List


class Label(TypedDict):
    short: str
    source: str
    text: str
    io: str
    unit: str
    unit_short: str
    name_a: str

class String(TypedDict):
    i: List[str]
    wt: Dict[str, List[str]]

LABELS_TYPE = Dict[str, Label]

STRINGS_TYPE = Dict[str, String]

INDICATOR_TYPE = Dict[str, str]

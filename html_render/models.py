from typing import List, NamedTuple, TypedDict


class CardInformation(NamedTuple):
    id: str
    title: str
    contentsHtmlText: str

class WmlDocumentInformation(TypedDict):
    cards: List[CardInformation]
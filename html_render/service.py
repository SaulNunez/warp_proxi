from typing import List

from html_render.link_creator import ProxiLinkCreator
from html_render.models import CardInformation, WmlDocumentInformation
from html_render.render import RenderToHtml
from warp.wml import parse_from_string

def process_wap_text(text: str, base_url: str = "") -> WmlDocumentInformation:
    page = parse_from_string(text)
      
    link_creator = ProxiLinkCreator(base_url=base_url)
    cards_representation: List[CardInformation] = []
    for card in page.cards: 
        contents = RenderToHtml(card, link_creator).generate()
        card_id = (card.id or "card").strip()
        cards_representation.append(CardInformation(card_id, card.title or "", contents))
    
    return {'cards': cards_representation }
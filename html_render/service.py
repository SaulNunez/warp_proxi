import os
import socket
from typing import List

from html_render.link_creator import ProxiLinkCreator
from html_render.models import CardInformation, WmlDocumentInformation
from html_render.render import RenderToHtml
from warp.wml import parse_from_string

def get_system_ip_address() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip_address = s.getsockname()[0]
    s.close()
    return ip_address

host = os.environ.get("HOST_DOMAIN", get_system_ip_address())

def process_wap_text(text: str) -> WmlDocumentInformation:
    page = parse_from_string(text)
      
    link_creator = ProxiLinkCreator(host)
    cards_representation: List[CardInformation] = []
    for card in page.cards: 
        contents = RenderToHtml(card, link_creator).generate()
        cards_representation.append((card.id, card.title, contents))
    
    return {'cards': cards_representation }
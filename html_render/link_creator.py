from urllib.parse import urlencode, urljoin, urlparse

class ProxiLinkCreator:
    def __init__(self, base_url: str = "", proxi_route: str = "/wml_to_html"):
        self.base_url = base_url
        self.proxi_route = proxi_route
        
    @staticmethod
    def is_relative_url(url: str) -> bool:
        parsed = urlparse(url)
        return not parsed.scheme and not parsed.netloc
    
    def create_for_url(self, href: str) -> str:
        if not href:
            return "#"
        if href.startswith("#"):
            return href
        if self.is_relative_url(href):
            original_wap_server = urljoin(self.base_url, href) if self.base_url else href
        else:
            original_wap_server = href
        proxi_query = urlencode({'wml_url': original_wap_server})
        return f"{self.proxi_route}?{proxi_query}"
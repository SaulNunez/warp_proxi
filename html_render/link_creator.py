from urllib.parse import urlencode, urljoin, urlparse, urlunparse

class ProxiLinkCreator:
    def __init__(self, domain: str, proxi_route: str = "/wml_to_html"):
        self.domain = domain
        self.proxi_route = proxi_route
        
    @staticmethod
    def is_relative_url(url):
        parsed = urlparse(url)
        # A URL is relative if it lacks a scheme and netloc
        return not parsed.scheme and not parsed.netloc
    
    def create_for_url(self, href: str) -> str:
        original_wap_server: str = ""
        if self.is_relative_url(href):
            original_wap_server = urljoin(self.domain, href)
        else:
            original_wap_server = href
        proxi_query = urlencode({'wml_url', original_wap_server})
        proxi_redirect_parts = ('http', self.domain, self.proxi_route, "", proxi_query)
        proxi_url = urlunparse(proxi_redirect_parts)
        return proxi_url
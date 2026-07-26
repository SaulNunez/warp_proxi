from urllib.parse import parse_qsl, urlencode, urljoin, urlparse, urlunparse

class ProxiLinkCreator:
    def __init__(self, base_url: str = "", proxi_route: str = "/wml_to_html"):
        self.base_url = base_url
        self.proxi_route = proxi_route
        
    @staticmethod
    def is_relative_url(url: str) -> bool:
        parsed = urlparse(url)
        return not parsed.scheme and not parsed.netloc
    
    def create_for_url(self, href: str, extra_params: dict[str, str] | None = None) -> str:
        if not href:
            return "#"
        if href.startswith("#"):
            return href
            
        if self.is_relative_url(href):
            target_url = urljoin(self.base_url, href) if self.base_url else href
        else:
            target_url = href
            
        if extra_params:
            parsed_target = urlparse(target_url)
            existing_query = dict(parse_qsl(parsed_target.query))
            existing_query.update(extra_params)
            new_query = urlencode(existing_query)
            target_url = urlunparse((
                parsed_target.scheme,
                parsed_target.netloc,
                parsed_target.path,
                parsed_target.params,
                new_query,
                parsed_target.fragment,
            ))
            
        proxi_query = urlencode({'wml_url': target_url})
        return f"{self.proxi_route}?{proxi_query}"
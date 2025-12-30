from urllib.parse import urlparse

def get_root_domain(url):
    parsed = urlparse(url)
    domain = parsed.netloc.lower()

    if domain.startswith("www."):
        domain = domain[4:]

    return domain    
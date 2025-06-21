import re
from urllib.parse import urljoin


def extract_link(text: str, base_url: str) -> str:
    match = re.search(r"window\.open\('([^']*)'", text)
    if match:
        relative_link = match.group(1)
        full_link = urljoin(base_url, relative_link)
        return full_link
    return None

import os
from urllib.parse import urljoin


def get_endpoint(name: str):
    endpoint = os.getenv("API_ENDPOINT")
    assert endpoint is not None, "API_ENDPOINT is not set"
    return urljoin(endpoint, name)

"""
Defines the HttpClientError class
"""


class HttpClientError(Exception):
    """HTTP client error"""

    pass


class HttpClientRetryError(HttpClientError):
    """HTTP client retry error"""

    def __init__(self, retries: int, *args, **kwargs):
        self.retries = retries
        super().__init__(*args, **kwargs)

    def __str__(self):
        return f"Request failed after {self.retries} retries"


class HttpClientTimeoutError(HttpClientError):
    """HTTP client timeout error"""

    def __init__(self, timeout: int, *args, **kwargs):
        self.timeout = timeout
        super().__init__(*args, **kwargs)

    def __str__(self):
        return f"Request timed out after {self.timeout} seconds"

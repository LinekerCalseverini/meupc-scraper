from infrastructure.gateways.meupcnet.adapters.base import (
    build_headers,
    build_cookies,
    build_form_token,
)


def test_build_headers() -> None:
    api_path_cases = ["", "/armazenamentos"]
    last_headers = {}
    for case in api_path_cases:
        headers = build_headers(case)
        assert headers["referer"] == f"https://meupc.net{case}"
        last_headers = headers

    assert last_headers["accept-encoding"] == "gzip, deflate, br, zstd"
    assert (
        last_headers["Content-Type"]
        == "multipart/form-data; boundary=----WebKitFormBoundary"
    )


def test_build_cookies() -> None:
    cookies = build_cookies("abc123", "def456")
    assert cookies["ci_csrf_cookie"] == "abc123"
    assert cookies["meupcnet"] == "def456"


def test_build_form_token() -> None:
    form_token_str = build_form_token("abc123").decode("utf8")
    assert "ci_csrf_token" in form_token_str
    assert "abc123" in form_token_str
    assert "----WebKitFormBoundary" in form_token_str

def build_headers() -> dict[str, str]:
    return {
        "accept-encoding": "gzip, deflate, br, zstd",
        "referer": "https://meupc.net/armazenamentos",
        "Content-Type": "multipart/form-data; boundary=----WebKitFormBoundary",
    }


def build_cookies(csrf_token: str, meupc_token: str) -> dict[str, str]:
    return {
        "meupcnet": meupc_token,
        "ci_csrf_cookie": csrf_token,
    }


def build_form_token(csrf_token: str) -> bytes:
    boundary = "----WebKitFormBoundary"
    body_str = (
        f"--{boundary}\n"
        f'Content-Disposition: form-data; name="ci_csrf_token"\n\n'
        f"{csrf_token}\n"
        f"--{boundary}--\n"
    )
    body_bytes = body_str.encode("utf-8")
    return body_bytes

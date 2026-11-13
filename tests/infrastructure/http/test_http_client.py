from infrastructure.http.http_client import HttpClient, HttpClientResponse


class DummyResponse(HttpClientResponse):
    def json(self) -> dict:
        super().json()  # type: ignore[safe-super]
        return {}


class DummyClient(HttpClient):
    async def request(self, method, url, **kwargs) -> HttpClientResponse:
        await super().request(method, url, **kwargs)  # type: ignore[safe-super]
        return DummyResponse()

    async def get(self, url, **kwargs) -> HttpClientResponse:
        await super().get(url, **kwargs)  # type: ignore[safe-super]
        return DummyResponse()

    async def post(self, url, **kwargs) -> HttpClientResponse:
        await super().post(url, **kwargs)  # type: ignore[safe-super]
        return DummyResponse()


async def test_http_client_abstract_methods() -> None:
    client = DummyClient()
    resp = await client.request("GET", "https://example.com")
    assert resp.json() == {}
    assert await client.get("https://example.com") is not None
    assert await client.post("https://example.com") is not None

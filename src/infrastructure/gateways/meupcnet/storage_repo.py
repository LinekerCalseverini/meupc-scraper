from domain.interfaces.storage_repo import StorageRepo

from infrastructure.http.http_client import HttpClient


class MeupcnetStorageRepo(StorageRepo):
    def __init__(self, url: str, csrf_token: str, http_client: HttpClient):
        self._http_client = http_client
        self._url = url
        self._csrf_token = csrf_token

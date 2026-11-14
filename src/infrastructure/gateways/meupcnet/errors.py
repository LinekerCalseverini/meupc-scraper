class MeuPCApiError(Exception):
    pass


class MeuPCUnexpectedResponseError(MeuPCApiError):
    def __init__(self, response):
        super().__init__(f"Unexpected response from MeuPC API: {response}")

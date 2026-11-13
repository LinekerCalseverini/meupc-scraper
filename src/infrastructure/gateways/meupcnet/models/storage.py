from pydantic import BaseModel, Field


class StorageApiResponseModel(BaseModel):
    descricao: str
    serie: str
    formato: str
    tipo: str
    capacidade_padrao: int
    leitura: int | None = None
    gravacao: int | None = None
    slug: str
    hash_: str = Field(alias="hash")
    preco: float | None = None
    preco_boleto: float | None = None
    patrocinado: int | None = None
    small: str | None = None
    medium: str | None = None
    large: str | None = None

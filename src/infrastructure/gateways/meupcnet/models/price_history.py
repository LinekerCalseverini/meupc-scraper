from pydantic import BaseModel, Field


class DatasetApiResponseModel(BaseModel):
    label: str = Field(alias="label")
    data: list[float | None] = Field(alias="data")


class PriceHistoryApiResponseModel(BaseModel):
    labels: list[str | None] = Field(alias="labels")
    datasets: list[DatasetApiResponseModel]

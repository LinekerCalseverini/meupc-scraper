from datetime import datetime

from domain.entities.dataseries import DataPoint
from infrastructure.gateways.meupcnet.models.price_history import (
    PriceHistoryApiResponseModel,
)


def to_dataseries(
    sku_hash: str, price_history: PriceHistoryApiResponseModel
) -> list[DataPoint]:
    if not price_history.datasets:
        return []

    result = []
    for d, v in zip(price_history.labels, price_history.datasets[0].data):
        if d is not None and v is not None:
            result.append(
                DataPoint(
                    sku_hash=sku_hash,
                    date=int(datetime.strptime(d, "%Y-%m-%d").timestamp()),
                    value=int(round(v * 100)),
                )
            )
    return result


def build_uri_params(sku_hash: str) -> dict[str, str]:
    return {"hash": sku_hash, "tipo_preco": "menor_dia"}

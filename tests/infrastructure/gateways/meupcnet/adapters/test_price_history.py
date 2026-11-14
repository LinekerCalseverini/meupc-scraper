from infrastructure.gateways.meupcnet.adapters.price_history import (
    to_dataseries,
    build_uri_params,
)

from infrastructure.gateways.meupcnet.models.price_history import (
    PriceHistoryApiResponseModel,
    DatasetApiResponseModel,
)

EXPECTED_COUNT = 2
EXPECTED_VALUE_1 = 1050
EXPECTED_VALUE_2 = 2000


def test_build_uri_params():
    params = build_uri_params("abc123hash")
    assert params == {"hash": "abc123hash", "tipo_preco": "menor_dia"}


def test_to_dataseries_empty():
    model = PriceHistoryApiResponseModel(labels=[], datasets=[])
    assert to_dataseries("hash1", model) == []


def test_to_dataseries_valid():
    dataset = DatasetApiResponseModel(label="test", data=[10.5, None, 20.0])

    model = PriceHistoryApiResponseModel(
        labels=["2026-01-01", "2026-01-02", "2026-01-03"],
        datasets=[dataset],
    )
    result = to_dataseries("hash1", model)
    assert len(result) == EXPECTED_COUNT
    assert result[0].sku_hash == "hash1"
    assert result[0].value == EXPECTED_VALUE_1
    assert result[1].value == EXPECTED_VALUE_2

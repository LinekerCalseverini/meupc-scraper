# use pytest to test
from domain.entities.dataseries import DataPoint


def test_data_point_date_str():
    data_point = DataPoint("sku_hash", 1609459200, 1)
    assert data_point.date_str() == "2021-01-01"

from domain.entities.storage.types import StorageInterfaces
from infrastructure.gateways.meupcnet.adapters.storage import (
    to_domain_storage_many,
    build_uri_params,
    to_meupc_storage_interface,
)


def test_to_domain_storage_many() -> None:
    meupc_storage_data = [
        {
            "descricao": "Husky Gaming 512GB",
            "serie": "Gaming",
            "formato": '2.5"',
            "tipo": "SSD",
            "capacidade": "512 GB",
            "capacidade_padrao": "512",
            "leitura": "520",
            "gravacao": "450",
            "slug": "ssd-husky-gaming-gaming-512gb",
            "hash": "tVmUSN",
            "preco": "588.20",
            "preco_boleto": "499.99",
            "preco_gb": "0.98",
            "patrocinado": "1",
            "loja_patrocinado": "KaBuM!",
            "link_patrocinado": "link/Kabum/tVmUSN",
            "small": "ssd-husky-gaming-gaming-512gb-Yxf-128p.jpg",
            "medium": "ssd-husky-gaming-gaming-512gb-Yxf-256p.jpg",
            "large": "ssd-husky-gaming-gaming-512gb-Yxf-512p.jpg",
        },
        {
            "descricao": "Kingston NV3 1TB",
            "serie": "NV3",
            "formato": "M.2-2280",
            "tipo": "SSD",
            "capacidade": "1 TB",
            "capacidade_padrao": "1024",
            "leitura": "6000",
            "gravacao": "4000",
            "slug": "ssd-kingston-nv3-nv3-1tb",
            "hash": "HOeL4x",
            "preco": "966.00",
            "preco_boleto": "966.00",
            "preco_gb": "0.94",
            "recente": "0",
            "popularidade": "18685",
            "popularidade_percent": "1.0000",
            "small": "ssd-kingston-nv3-nv3-1tb-5TA-128p.jpg",
            "medium": "ssd-kingston-nv3-nv3-1tb-5TA-256p.jpg",
            "large": "ssd-kingston-nv3-nv3-1tb-5TA-512p.jpg",
        },
    ]

    domain_storages = to_domain_storage_many(meupc_storage_data)

    assert domain_storages[0].hash_ == "tVmUSN"
    assert domain_storages[0].slug == "ssd-husky-gaming-gaming-512gb"
    assert domain_storages[0].description == "Husky Gaming 512GB"
    assert domain_storages[0].series == "Gaming"
    assert domain_storages[0].format_ == '2.5"'
    assert domain_storages[0].type_ == "SSD"
    assert domain_storages[0].capacity_gb == int(512)
    assert domain_storages[0].read == int(520)
    assert domain_storages[0].write == int(450)
    assert domain_storages[0].price_cents == int(58820)
    assert domain_storages[0].price_slip_cents == int(49999)
    assert domain_storages[0].sponsored

    assert domain_storages[1].hash_ == "HOeL4x"
    assert domain_storages[1].slug == "ssd-kingston-nv3-nv3-1tb"
    assert domain_storages[1].description == "Kingston NV3 1TB"
    assert domain_storages[1].series == "NV3"
    assert domain_storages[1].format_ == "M.2-2280"
    assert domain_storages[1].type_ == "SSD"
    assert domain_storages[1].capacity_gb == int(1024)
    assert domain_storages[1].read == int(6000)
    assert domain_storages[1].write == int(4000)
    assert domain_storages[1].price_cents == int(96600)
    assert domain_storages[1].price_slip_cents == int(96600)
    assert not domain_storages[1].sponsored


def test_to_meupc_storage_interface() -> None:
    assert to_meupc_storage_interface(StorageInterfaces.M2_PCIE_40_X4) == int(42)


def test_build_uri_params() -> None:
    assert build_uri_params(capacity_gb_min=1, capacity_gb_max=2) == {"cap": "1,2"}
    assert build_uri_params(storage_interface=StorageInterfaces.M2_PCIE_40_X4) == {
        "int": 42
    }
    assert build_uri_params() == {}
    assert build_uri_params(capacity_gb_min=1) == {"cap": "1"}
    assert build_uri_params(capacity_gb_max=2) == {"cap": "2"}
    assert build_uri_params(storage_interface=StorageInterfaces.M2_PCIE_40_X4) == {
        "int": 42
    }

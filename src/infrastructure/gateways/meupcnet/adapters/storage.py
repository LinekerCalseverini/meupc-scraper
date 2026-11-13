import logging

from domain.entities.storage.types import StorageInterfaces
from domain.entities.products import Storage
from infrastructure.gateways.meupcnet.models.storage import StorageApiResponseModel

# Define the translation map as a constant dictionary


_STORAGE_INTERFACE_EXTERNAL_MAP: dict[StorageInterfaces, int] = {
    StorageInterfaces.M2_PCIE_40_X4: 42,
}

logger = logging.getLogger(__name__)


def to_meupc_storage_interface(storage_interface: StorageInterfaces) -> int | None:
    """


    Translates a domain storage interface enum into the external API's integer ID.


    Returns None if the interface has no corresponding external mapping.
    """

    return _STORAGE_INTERFACE_EXTERNAL_MAP.get(storage_interface)


def build_uri_params(
    capacity_gb_min: int | None = None,
    capacity_gb_max: int | None = None,
    storage_interface: StorageInterfaces | None = None,
) -> dict[str, int | None]:
    """
    Translates a domain storage interface enum into the external API's integer ID.
    Returns None if the interface has no corresponding external mapping.
    """

    params = {}
    capacity_str = [
        str(capacity)
        for capacity in (capacity_gb_min, capacity_gb_max)
        if capacity is not None
    ]
    if capacity_str:
        params["cap"] = ",".join(capacity_str)

    if storage_interface is not None:
        params["int"] = to_meupc_storage_interface(storage_interface)

    return params


def to_domain_storage(data: dict) -> Storage:
    """
    Adapts raw API dictionary into a domain Storage entity.
    """
    api_model = StorageApiResponseModel(**data)

    # Convert prices to cents if they exist (e.g., 150.50 -> 15050), or 0 if None
    price_cents = int(api_model.preco * 100) if api_model.preco is not None else 0
    price_slip_cents = (
        int(api_model.preco_boleto * 100) if api_model.preco_boleto is not None else 0
    )
    sponsored = api_model.patrocinado == 1

    return Storage(
        hash_=api_model.hash_,
        slug=api_model.slug,
        description=api_model.descricao,
        series=api_model.serie,
        format_=api_model.formato,
        type_=api_model.tipo,
        capacity_gb=api_model.capacidade_padrao,
        read=api_model.leitura,
        write=api_model.gravacao,
        price_cents=price_cents,
        price_slip_cents=price_slip_cents,
        sponsored=sponsored,
    )


def to_domain_storage_many(data: list[dict]) -> list[Storage]:
    # return [to_domain_storage(d) for d in data]
    result: list[Storage] = []
    for d in data:
        try:
            result.append(to_domain_storage(d))
        except Exception as e:
            logger.error({"data": d, "error": e})
    return result

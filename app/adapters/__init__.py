from app.adapters.base import PrinterAdapter
from app.adapters.datecs_dp05c import DatecsDP05CAdapter
from app.adapters.datecs_dp150x import DatecsDP150XAdapter
from app.adapters.datecs_dp25x import DatecsDP25XAdapter
from app.adapters.datecs_fmp350x import DatecsFMP350XAdapter
from app.adapters.datecs_fmp55x import DatecsFMP55XAdapter
from app.adapters.datecs_1to1 import DatecsOneToOneAdapter
from app.adapters.datecs_fp2000 import DatecsFP2000Adapter
from app.adapters.datecs_fp2000_base import DatecsFP2000BaseAdapter
from app.adapters.datecs_fp800 import DatecsFP800Adapter
from app.adapters.datecs_fp650 import DatecsFP650Adapter
from app.adapters.datecs_sk1_21f import DatecsSK121FAdapter
from app.adapters.datecs_sk1_31f import DatecsSK131FAdapter
from app.adapters.datecs_fmp10 import DatecsFMP10Adapter
from app.adapters.datecs_fp700 import DatecsFP700Adapter
from app.adapters.datecs_fp700mx import DatecsFP700MXAdapter
from app.adapters.datecs_fp700x import DatecsFP700XAdapter
from app.adapters.datecs_fp700xe import DatecsFP700XEAdapter
from app.adapters.datecs_wp25x import DatecsWP25XAdapter
from app.adapters.datecs_wp500x import DatecsWP500XAdapter
from app.adapters.datecs_wp50x import DatecsWP50XAdapter
from app.adapters.datecspay_bluepad import DatecsPayBluePadAdapter

ADAPTERS: dict[str, type[PrinterAdapter]] = {
    DatecsOneToOneAdapter.model: DatecsOneToOneAdapter,
    DatecsFMP350XAdapter.model: DatecsFMP350XAdapter,
    DatecsFMP55XAdapter.model: DatecsFMP55XAdapter,
    DatecsFP700XAdapter.model: DatecsFP700XAdapter,
    DatecsFP700XEAdapter.model: DatecsFP700XEAdapter,
    DatecsWP500XAdapter.model: DatecsWP500XAdapter,
    DatecsWP50XAdapter.model: DatecsWP50XAdapter,
    DatecsDP25XAdapter.model: DatecsDP25XAdapter,
    DatecsWP25XAdapter.model: DatecsWP25XAdapter,
    DatecsDP150XAdapter.model: DatecsDP150XAdapter,
    DatecsDP05CAdapter.model: DatecsDP05CAdapter,
    DatecsFP700MXAdapter.model: DatecsFP700MXAdapter,
    DatecsFP2000Adapter.model: DatecsFP2000Adapter,
    DatecsFP800Adapter.model: DatecsFP800Adapter,
    DatecsFP650Adapter.model: DatecsFP650Adapter,
    DatecsSK121FAdapter.model: DatecsSK121FAdapter,
    DatecsSK131FAdapter.model: DatecsSK131FAdapter,
    DatecsFMP10Adapter.model: DatecsFMP10Adapter,
    DatecsFP700Adapter.model: DatecsFP700Adapter,
    DatecsPayBluePadAdapter.model: DatecsPayBluePadAdapter,
}

DATECS_1TO1_FAMILY = {
    "datecs_fmp350x",
    "datecs_fmp55x",
    "datecs_fp700x",
    "datecs_fp700xe",
    "datecs_wp500x",
    "datecs_wp50x",
    "datecs_dp25x",
    "datecs_wp25x",
    "datecs_dp150x",
    "datecs_dp05c",
}


def get_adapter(model: str, config: dict | None = None) -> PrinterAdapter:
    key = (model or "").lower()
    adapter_cls = ADAPTERS.get(key)
    if not adapter_cls:
        raise ValueError(f"Unsupported printer model: {model}")
    return adapter_cls(config or {})


def list_supported_models() -> list[str]:
    models = sorted(ADAPTERS.keys())
    if DatecsOneToOneAdapter.model in models:
        models = [model for model in models if model not in DATECS_1TO1_FAMILY]
    return models

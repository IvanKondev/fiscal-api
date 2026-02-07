from app.adapters.datecs_base import DatecsBaseAdapter
from app.builders import DatecsDataBuilder, FP2000DataBuilder


class DatecsFP2000BaseAdapter(DatecsBaseAdapter):
    """
    Base adapter for DATECS FP-2000 printer family.
    
    Supported models:
    - FP-800
    - FP-2000
    - FP-650
    - SK1-21F
    - SK1-31F
    - FMP-10
    - FP-700 (Version 2.00BG)
    
    Protocol: Version 2.00BG
    Reference: DATECS FP-800/FP-2000/FP-650/SK1-21F/SK1-31F/FMP-10/FP-700
    
    Key characteristics:
    - 6-byte status field
    - 8 tax groups (A-H)
    - Electronic Journal (EJ) support
    - GPRS modem support
    - Supports fiscal receipts, storno, reports
    - Maximum 512 sales per receipt
    - Department support (1-1200)
    """
    model = "datecs_fp2000_base"
    default_encoding = "cp1251"
    protocol_format = "byte"
    status_length = 6

    @property
    def data_builder(self) -> DatecsDataBuilder:
        return FP2000DataBuilder()

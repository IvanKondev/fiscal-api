from app.adapters.datecs_fp2000_base import DatecsFP2000BaseAdapter


class DatecsFP700Adapter(DatecsFP2000BaseAdapter):
    """
    DATECS FP-700 (Version 2.00BG protocol)
    Note: Different from FP-700X/FP-700MX which use a different protocol version.
    """
    model = "datecs_fp700"

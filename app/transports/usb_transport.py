from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from app.app_logging import log_info

try:
    import usb.core
    import usb.util
except ImportError:  # pragma: no cover
    usb = None


@dataclass
class USBConfig:
    vendor_id: int
    product_id: int
    interface: int = 0
    endpoint_out: Optional[int] = None
    timeout_ms: int = 5000


class USBTransport:
    def __init__(self, config: USBConfig, dry_run: bool = False) -> None:
        self.config = config
        self.dry_run = dry_run

    def write(self, data: bytes) -> None:
        if self.dry_run:
            log_info("DRY_RUN_USB_WRITE", {"bytes_hex": data.hex(), "length": len(data)})
            return
        if usb is None:
            raise RuntimeError("PyUSB is not installed. Install pyusb to use USB transport.")
        device = usb.core.find(idVendor=self.config.vendor_id, idProduct=self.config.product_id)
        if device is None:
            raise RuntimeError("USB device not found for the provided vendor/product IDs.")
        device.set_configuration()
        cfg = device.get_active_configuration()
        interface = usb.util.find_descriptor(cfg, bInterfaceNumber=self.config.interface)
        if interface is None:
            raise RuntimeError("USB interface not found for the device.")
        endpoint = self.config.endpoint_out
        if endpoint is None:
            endpoint = usb.util.find_descriptor(
                interface,
                custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress)
                == usb.util.ENDPOINT_OUT,
            )
            if endpoint is None:
                raise RuntimeError("USB OUT endpoint not found.")
            endpoint = endpoint.bEndpointAddress
        device.write(endpoint, data, timeout=self.config.timeout_ms)

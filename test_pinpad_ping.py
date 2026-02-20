"""Test script: PING the BluePad 50 Plus on COM6 using the new DatecsPay protocol."""
import sys
import time

# Add project root to path
sys.path.insert(0, ".")

from app.transports.serial_transport import SerialConfig, SerialTransport
from app.datecspay_protocol import (
    build_packet, parse_response_packet, _xor_checksum,
    CMD_BORICA, BorCmd, START_BYTE,
    ping, get_pinpad_info, get_card_reader_state,
    PinpadError, PinpadTimeoutError,
)

PORT = "COM6"
BAUDRATES = [115200, 57600, 38400, 19200, 9600]

def test_ping_raw(port: str, baudrate: int) -> bool:
    """Send raw PING packet and check for response."""
    config = SerialConfig(port=port, baudrate=baudrate, timeout_ms=3000)
    transport = SerialTransport(config)
    try:
        transport.open()
        # Build PING: 0x3D cmd, subcmd 0x00
        # Packet: 3E 3D 00 00 01 00 CSUM
        # Data for Borica cmd: [0x00] (PING subcmd)
        data = bytes([BorCmd.PING])
        packet = build_packet(CMD_BORICA, data)
        print(f"  TX [{baudrate}]: {packet.hex(' ')}")
        
        # Verify our packet matches the documented example
        expected = bytes([0x3E, 0x3D, 0x00, 0x00, 0x01, 0x00, 0x02])
        if packet == expected:
            print(f"  ✓ Packet matches protocol doc example")
        else:
            print(f"  ✗ Packet mismatch! Expected: {expected.hex(' ')}")
        
        transport.write(packet)
        
        # Wait for response
        time.sleep(0.5)
        response = bytearray()
        deadline = time.monotonic() + 3.0
        while time.monotonic() < deadline:
            chunk = transport.read(1)
            if chunk:
                response.extend(chunk)
                # Check if we have a complete packet
                if len(response) >= 6 and response[0] == START_BYTE:
                    lh = response[3]
                    ll = response[4]
                    data_len = (lh << 8) | ll
                    total = 5 + data_len + 1
                    if len(response) >= total:
                        break
            else:
                time.sleep(0.01)
        
        if response:
            print(f"  RX [{baudrate}]: {bytes(response).hex(' ')}")
            try:
                resp = parse_response_packet(bytes(response))
                print(f"  ✓ Status: 0x{resp.status:02X} ({resp.status_name})")
                print(f"  ✓ Data: {resp.data.hex(' ') if resp.data else '(empty)'}")
                return True
            except Exception as e:
                print(f"  Parse error: {e}")
        else:
            print(f"  ✗ No response at {baudrate} baud")
        return False
    except Exception as e:
        print(f"  Error [{baudrate}]: {e}")
        return False
    finally:
        transport.close()


def test_high_level(port: str, baudrate: int):
    """Test using high-level functions."""
    config = SerialConfig(port=port, baudrate=baudrate, timeout_ms=5000)
    transport = SerialTransport(config)
    try:
        transport.open()
        
        print(f"\n--- High-level PING ---")
        alive = ping(transport, "test-ping")
        print(f"  Ping result: {'ALIVE' if alive else 'NO RESPONSE'}")
        
        if alive:
            print(f"\n--- GET PINPAD INFO ---")
            try:
                info = get_pinpad_info(transport, "test-info")
                print(f"  Model:    {info.model}")
                print(f"  Serial:   {info.serial_number}")
                print(f"  Software: {info.software_version}")
                print(f"  Terminal: {info.terminal_id}")
                print(f"  Menu:     {info.menu_type}")
            except Exception as e:
                print(f"  Error: {e}")
            
            print(f"\n--- GET CARD READER STATE ---")
            try:
                state = get_card_reader_state(transport, "test-state")
                print(f"  State: {state.name} (code={state.state})")
            except Exception as e:
                print(f"  Error: {e}")
    except Exception as e:
        print(f"  Error: {e}")
    finally:
        transport.close()


if __name__ == "__main__":
    print("=" * 60)
    print("DatecsPay BluePad 50 Plus PING Test")
    print(f"Port: {PORT}")
    print("=" * 60)
    
    # First verify our packet building
    data = bytes([BorCmd.PING])
    packet = build_packet(CMD_BORICA, data)
    expected = bytes([0x3E, 0x3D, 0x00, 0x00, 0x01, 0x00, 0x02])
    print(f"\nPacket verification:")
    print(f"  Built:    {packet.hex(' ')}")
    print(f"  Expected: {expected.hex(' ')}")
    print(f"  Match:    {packet == expected}")
    
    # Try each baud rate
    found_baudrate = None
    for br in BAUDRATES:
        print(f"\n--- Testing {br} baud ---")
        if test_ping_raw(PORT, br):
            found_baudrate = br
            break
    
    if found_baudrate:
        print(f"\n{'=' * 60}")
        print(f"SUCCESS! Device responds at {found_baudrate} baud")
        test_high_level(PORT, found_baudrate)
    else:
        print(f"\n{'=' * 60}")
        print("No response at any baud rate.")
        print("Check: device powered on, correct COM port, cable connected.")

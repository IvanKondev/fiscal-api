#!/usr/bin/env python3
"""Test all operations using the new DataBuilder architecture."""

import sys
from app.builders.fp2000 import FP2000DataBuilder
from app.transports.serial_transport import SerialTransport, SerialConfig
from app.datecs_protocol import send_command, next_seq

PORT = "COM5"
BAUDRATE = 115200
PROTOCOL = "byte"
STATUS_LEN = 6
TIMEOUT_S = 5.0

CMD_STATUS = 0x4A
CMD_OPEN_NONFISCAL = 0x26
CMD_PRINT_TEXT = 0x2A
CMD_CLOSE_NONFISCAL = 0x27
CMD_OPEN_FISCAL = 0x30
CMD_SELL_ITEM = 0x31
CMD_PAYMENT = 0x35
CMD_CLOSE_FISCAL = 0x38
CMD_CASH = 0x46

builder = FP2000DataBuilder()


def send(transport, cmd, data_str, seq, label):
    """Send command with string data, return (next_seq, response)."""
    data = data_str.encode("cp1251") if data_str else None
    print(f"  [{label}] cmd=0x{cmd:02X} data={repr(data_str)}")
    response = send_command(
        transport, cmd=cmd, data=data, seq=seq,
        timeout_s=TIMEOUT_S, protocol_format=PROTOCOL, status_length=STATUS_LEN,
    )
    print(f"  [{label}] OK  status={response.status.hex()} fields={response.fields}")
    return next_seq(seq), response


def test_status(transport, seq):
    print("\n" + "="*60)
    print("TEST 1: STATUS")
    print("="*60)
    data = builder.status_data()
    seq, resp = send(transport, CMD_STATUS, data, seq, "status")
    print("✅ Status OK")
    return seq


def test_nonfiscal(transport, seq):
    print("\n" + "="*60)
    print("TEST 2: NON-FISCAL RECEIPT")
    print("="*60)
    seq, _ = send(transport, CMD_OPEN_NONFISCAL, None, seq, "open")
    for text in ["=== ТЕСТ ===", "Ред 1: Български", "Ред 2: English", "=== КРАЙ ==="]:
        data = builder.nonfiscal_text(text)
        seq, _ = send(transport, CMD_PRINT_TEXT, data, seq, f"text: {text}")
    seq, _ = send(transport, CMD_CLOSE_NONFISCAL, None, seq, "close")
    print("✅ Non-fiscal OK")
    return seq


def test_fiscal(transport, seq):
    print("\n" + "="*60)
    print("TEST 3: FISCAL RECEIPT")
    print("="*60)
    # Open
    open_data = builder.open_receipt("1", "0000", "1")
    seq, _ = send(transport, CMD_OPEN_FISCAL, open_data, seq, "open")
    # Sell
    sale_data = builder.sale({"name": "Тест артикул", "tax": "B", "price": 1.00, "qty": "1.000"})
    seq, _ = send(transport, CMD_SELL_ITEM, sale_data, seq, "sell")
    # Payment
    pay_data = builder.payment({"type": "P", "amount": 1.00})
    seq, _ = send(transport, CMD_PAYMENT, pay_data, seq, "payment")
    # Close
    seq, _ = send(transport, CMD_CLOSE_FISCAL, "", seq, "close")
    print("✅ Fiscal receipt OK")
    return seq


def test_cash(transport, seq):
    print("\n" + "="*60)
    print("TEST 4: CASH IN/OUT")
    print("="*60)
    in_data = builder.cash({"amount": 0.01, "direction": "in"})
    seq, _ = send(transport, CMD_CASH, in_data, seq, "cash in")
    out_data = builder.cash({"amount": 0.01, "direction": "out"})
    seq, _ = send(transport, CMD_CASH, out_data, seq, "cash out")
    print("✅ Cash in/out OK")
    return seq


def main():
    print("="*60)
    print("FP-2000 BUILDER TEST")
    print(f"Using: FP2000DataBuilder")
    print("="*60)

    # Show builder output for each command
    print("\n--- Builder output samples ---")
    print(f"  status_data()         = {repr(builder.status_data())}")
    print(f"  nonfiscal_text('Hi')  = {repr(builder.nonfiscal_text('Hi'))}")
    print(f"  open_receipt(1,0000,1)= {repr(builder.open_receipt('1','0000','1'))}")
    print(f"  sale(item)            = {repr(builder.sale({'name':'Test','tax':'B','price':5.00,'qty':'2.000'}))}")
    print(f"  payment(cash 5.00)    = {repr(builder.payment({'type':'P','amount':5.00}))}")
    print(f"  cash(in 1.00)         = {repr(builder.cash({'amount':1.00,'direction':'in'}))}")
    print(f"  report(z)             = {repr(builder.report({'type':'z'}))}")

    config = SerialConfig(port=PORT, baudrate=BAUDRATE, timeout_ms=int(TIMEOUT_S * 1000))
    transport = SerialTransport(config)

    try:
        transport.open()
        print(f"\n✅ Port {PORT} opened")
        seq = 0x20
        results = []

        try:
            seq = test_status(transport, seq)
            results.append(("Status", True))
        except Exception as e:
            print(f"❌ Status FAILED: {e}")
            results.append(("Status", False))

        try:
            seq = test_nonfiscal(transport, seq)
            results.append(("Non-fiscal", True))
        except Exception as e:
            print(f"❌ Non-fiscal FAILED: {e}")
            results.append(("Non-fiscal", False))

        try:
            seq = test_cash(transport, seq)
            results.append(("Cash", True))
        except Exception as e:
            print(f"❌ Cash FAILED: {e}")
            results.append(("Cash", False))

        try:
            seq = test_fiscal(transport, seq)
            results.append(("Fiscal", True))
        except Exception as e:
            print(f"❌ Fiscal FAILED: {e}")
            results.append(("Fiscal", False))

        print("\n" + "="*60)
        print("RESULTS")
        print("="*60)
        for name, ok in results:
            print(f"  {'✅' if ok else '❌'} {name}")
        passed = sum(1 for _, ok in results if ok)
        print(f"\n  {passed}/{len(results)} passed")
        return 0 if passed == len(results) else 1

    except Exception as e:
        print(f"\n❌ CRITICAL: {e}")
        import traceback; traceback.print_exc()
        return 1
    finally:
        transport.close()

if __name__ == "__main__":
    sys.exit(main())

"""Scan COM6 BluePad 50 Plus - try wake up with DTR/RTS and various protocols."""
import serial
import time
import sys

PORT = 'COM6'
BAUD = 115200

print(f"Opening {PORT} at {BAUD}...")
ser = serial.Serial(PORT, BAUD, timeout=2, bytesize=8, parity='N', stopbits=1)

# Toggle DTR/RTS to wake up device
print("Toggling DTR/RTS to wake device...")
ser.dtr = False
ser.rts = False
time.sleep(0.5)
ser.dtr = True
ser.rts = True
time.sleep(1)

# Flush any startup data
startup = ser.read(500)
if startup:
    print(f"Startup data: {startup.hex()}")
    try:
        print(f"  ASCII: {startup.decode('cp1251', errors='replace')}")
    except:
        pass


def try_send(label, data, wait=2):
    ser.reset_input_buffer()
    ser.write(data)
    time.sleep(wait)
    resp = ser.read(1000)
    if resp:
        print(f"  [{label}] Response ({len(resp)} bytes): hex={resp.hex()}")
        try:
            print(f"    ASCII: {resp.decode('cp1251', errors='replace')}")
        except:
            pass
        return True
    else:
        print(f"  [{label}] No response")
        return False


def datecs_packet(cmd, data_str='', seq=32):
    data = data_str.encode('cp1251')
    length = 0x20 + 4 + len(data)
    preamble = bytes([0x01, length, seq, cmd])
    postamble = bytes([0x05, 0x03])
    bcc_data = preamble[1:] + data + postamble[:1]
    bcc = 0
    for b in bcc_data:
        bcc ^= b
    bcc_bytes = bytes([0x30 + ((bcc >> 4) & 0x0F), 0x30 + (bcc & 0x0F)])
    return preamble + data + postamble + bcc_bytes


# Test 1: ENQ after wake
print("\n--- 1. ENQ after DTR/RTS wake ---")
try_send("ENQ", bytes([0x05]))

# Test 2: Datecs protocol
print("\n--- 2. Datecs status (0x4A) ---")
try_send("0x4A", datecs_packet(0x4A, 'X'))

# Test 3: Datecs diagnostic (0x5A)
print("\n--- 3. Datecs diagnostic (0x5A) ---")
try_send("0x5A", datecs_packet(0x5A))

# Test 4: SYN character (some POS terminals use 0x16)
print("\n--- 4. SYN (0x16) ---")
try_send("SYN", bytes([0x16]))

# Test 5: EOT (0x04)
print("\n--- 5. EOT (0x04) ---")
try_send("EOT", bytes([0x04]))

# Test 6: Common POS ECR protocol - STX LEN CMD DATA ETX LRC
# Transaction inquiry
print("\n--- 6. ECR POS - Transaction inquiry ---")
# Some ECR-POS protocols use: STX(02) + payload + ETX(03) + LRC
# Try with a simple "status" or "echo" command
for cmd_byte in [b'00', b'01', b'10', b'20', b'50', b'80', b'90', b'99']:
    payload = cmd_byte
    msg = bytes([0x02]) + payload + bytes([0x03])
    lrc = 0
    for b in payload + bytes([0x03]):
        lrc ^= b
    msg += bytes([lrc])
    if try_send(f"ECR cmd={cmd_byte.decode()}", msg, wait=0.5):
        break

# Test 7: Nexo-style / ISO 8583 basic
print("\n--- 7. Various single bytes ---")
for b in [0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x10, 0x11, 0x15, 0x16, 0x1B]:
    resp = try_send(f"byte 0x{b:02X}", bytes([b]), wait=0.3)
    if resp:
        break

# Test 8: Try all bauds with DTR/RTS
print("\n--- 8. All bauds with DTR/RTS wake ---")
for baud in [9600, 19200, 38400, 57600, 115200, 230400, 460800]:
    ser.close()
    try:
        ser = serial.Serial(PORT, baud, timeout=1, bytesize=8, parity='N', stopbits=1)
        ser.dtr = True
        ser.rts = True
        time.sleep(0.3)
        ser.reset_input_buffer()
        ser.write(bytes([0x05]))  # ENQ
        time.sleep(0.5)
        resp = ser.read(100)
        if resp:
            print(f"  [{baud}] Got response: {resp.hex()}")
            break
    except Exception as e:
        print(f"  [{baud}] Error: {e}")
    finally:
        if not ser.is_open:
            ser = serial.Serial(PORT, 115200, timeout=2)

# Test 9: Passive listen for 3 seconds
print("\n--- 9. Passive listen 3s ---")
ser.close()
ser = serial.Serial(PORT, 115200, timeout=3, bytesize=8, parity='N', stopbits=1)
ser.dtr = True
ser.rts = True
data = ser.read(1000)
if data:
    print(f"  Received: {data.hex()}")
else:
    print("  Nothing received")

ser.close()
print("\n=== DONE ===")
print("If no responses at all, the device may be:")
print("  1. Powered off or in deep sleep (press a button on it)")
print("  2. Not connected via USB-Serial (check cables)")
print("  3. Using Bluetooth only (not RS232)")

"""Scan COM6 for BluePad 50 Plus - try various protocols."""
import serial
import time

ser = serial.Serial('COM6', 115200, timeout=3, bytesize=8, parity='N', stopbits=1)
print('COM6 opened at 115200')


def datecs_packet(cmd, data_str='', seq=32):
    """Build a Datecs fiscal protocol packet."""
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


def try_send(label, data, wait=1.5):
    ser.reset_input_buffer()
    ser.write(data)
    time.sleep(wait)
    resp = ser.read(1000)
    if resp:
        print(f"  [{label}] Response ({len(resp)} bytes): {resp.hex()}")
        try:
            print(f"    ASCII: {resp.decode('cp1251', errors='replace')}")
        except:
            pass
    else:
        print(f"  [{label}] No response")
    return resp


# 1. Datecs fiscal protocol - ENQ
print("\n--- Test 1: ENQ (0x05) ---")
try_send("ENQ", bytes([0x05]))

# 2. Datecs status command 0x4A
print("\n--- Test 2: Datecs CMD 0x4A (status) ---")
try_send("Datecs 0x4A", datecs_packet(0x4A, 'X'))

# 3. Datecs diagnostic 0x5A
print("\n--- Test 3: Datecs CMD 0x5A (diagnostic) ---")
try_send("Datecs 0x5A", datecs_packet(0x5A))

# 4. ACK / NAK
print("\n--- Test 4: ACK (0x06) ---")
try_send("ACK", bytes([0x06]))

print("\n--- Test 5: NAK (0x15) ---")
try_send("NAK", bytes([0x15]))

# 5. STX/ETX wrapper (common POS protocol)
print("\n--- Test 6: STX-ETX empty ---")
try_send("STX-ETX", bytes([0x02, 0x03]))

# 6. STX + length + command + ETX + LRC  (Borica-like)
print("\n--- Test 7: Borica-style packet ---")
# Typical: STX(02) + data + ETX(03) + LRC
# Try a simple status/ping
msg = bytes([0x02]) + b'00' + bytes([0x03])
lrc = 0
for b in msg[1:]:
    lrc ^= b
msg += bytes([lrc])
try_send("Borica-style", msg)

# 7. AT commands (modem-style)
print("\n--- Test 8: AT command ---")
try_send("AT", b'AT\r\n')

# 8. Raw newline
print("\n--- Test 9: CR+LF ---")
try_send("CRLF", b'\r\n')

# 9. Try different baud rates with ENQ
for baud in [9600, 19200, 38400, 57600]:
    ser.close()
    ser = serial.Serial('COM6', baud, timeout=2, bytesize=8, parity='N', stopbits=1)
    print(f"\n--- Test baud {baud}: ENQ + Datecs status ---")
    try_send(f"ENQ@{baud}", bytes([0x05]))
    try_send(f"Datecs@{baud}", datecs_packet(0x4A, 'X'))

# 10. Listen passively
ser.close()
ser = serial.Serial('COM6', 115200, timeout=5, bytesize=8, parity='N', stopbits=1)
print("\n--- Test 10: Passive listen 5s at 115200 ---")
resp = ser.read(1000)
if resp:
    print(f"  Received: {resp.hex()}")
else:
    print("  Nothing received")

ser.close()
print("\nDone. If no responses, the device may need to be woken up or uses a different protocol.")

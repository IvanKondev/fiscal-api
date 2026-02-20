---
title: "DatecsPay card readers communication protocol (Version 1.9) — AI-ready Markdown"
version: "1.9"
source_file: "Pinpad Commands_v1.9.pdf"
generated_at: "2026-02-11"
notes:
  - "This file is a Markdown transformation of the provided PDF, preserving the original wording as much as possible."
  - "Hex examples are kept as code blocks to be machine-parseable."
---

# Overview

This document describes the communication protocol for **DatecsPay** card readers (pinpads), version **1.9**.

## Quick reference (normalized)

### Roles
- **EXT DEVICE**: external device talking to the reader (mobile / tablet / PC)
- **CARD READER / PINPAD**: DatecsPay card reader

### Packet format (byte-level)
#### EXT DEVICE -> CARD READER
```text
'>' CMD 00 LH LL <DATA> CSUM
```
- `'>'`: start packet, ASCII `0x3E`
- `CMD`: command number
- `LH LL`: data length in bytes (big-endian: `LH` high, `LL` low)
- `CSUM`: XOR of all bytes in the packet (including `0x3E`, excluding nothing)

Example:
```text
3E 3D 00 00 01 00 02
```

#### CARD READER -> EXT DEVICE
```text
'>' 00 ST LH LL <DATA> CSUM
```
- `ST`: status / error code (see **ERROR CODES** section)
- `LH LL`: length of `<DATA>`
- `CSUM`: XOR of all bytes in the packet

Example:
```text
3E 00 00 00 00 3E
```

### Timing
- Inter-byte timeout: **2 seconds**
- Recommended response wait timeout after sending a command: **5 seconds**

### High-level commands you can send
- `0x3D` — **Borica** command (transactions, info, reports, configuration)
- `0x40` — **External internet** command (socket/data tunneling features)

### Asynchronous events you may receive
- `0x0E` — Borica event
- `0x0F` — External internet event

### TLV encoding (overview)
Many parameters are provided as **TLV**:
- `T` (Tag): 1 or more bytes (e.g. `0x81`, `0x9F04`, `0xDF03`)
- `L` (Length): 1 byte for these examples
- `V` (Value): `L` bytes


## Table of contents (from the original PDF)

- **1. Packet format** (p. 5)
- **2. 0x3D: Borica subcommands** (p. 6)
  - 1. 0x00: PING (p. 6)
  - 2. 0x01: TRANSACTION START (p. 7)
  - 1. 0x01: START PURCHASE (p. 8)
  - 2. 0x01: START PURCHASE + GRATUITY / TIP (p. 9)
  - 3. 0x02: START PURCHASE + CASHBACK (p. 9)
  - 4. 0x03: START PURCHASE + REFERENCE (p. 10)
  - 5. 0x04: START CASH ADVANCE (p. 11)
  - 6. 0x05: START AUTHORIZATION (p. 11)
  - 7. 0x06: START PURCHASE + CODE (p. 12)
  - 8. 0x07: START VOID OF PURCHASE (p. 13)
  - 9. 0x07: START VOID OF PURCHASE + GRATUITY / TIP (p. 14)
  - 10. 0x07: START VOID OF PURCHASE + CASHBACK (p. 15)
  - 11. 0x08: START VOID OF CASH ADVANCE (p. 16)
  - 12. 0x09: START VOID OF AUTHORIZATION (p. 16)
  - 13. 0x0A: START END OF DAY (p. 17)
  - 14. 0x0B: START LOYALTY BALANCE (p. 18)
  - 15. 0x0C: START LOYALTY SPEND (p. 19)
  - 16. 0x0D: START VOID OF LOYALTY SPEND (p. 19)
  - 17. 0x0E: START TEST CONNECTION (p. 20)
  - 18. 0x0F: START TMS UPDATE (p. 21)
- **3. 0x02: GET RECEIPT TAGS** (p. 21)
  - 4. 0x03: TRANSACTION END (p. 22)
- **5. 0x04: GET REPORT TAGS** (p. 23)
  - 6. 0x05: GET REPORT INFO (p. 24)
  - 7. 0x06: GET PINPAD INFO (p. 25)
  - 8. 0x07: GET RTC (p. 26)
  - 9. 0x08: SET RTC (p. 27)
  - 10. 0x0B: DELETE BATCH (p. 28)
  - 11. 0x0C: CLEAR REVERSAL (p. 28)
  - 12. 0x1A: GET PINPAD STATUS (p. 29)
  - 13. 0x1D: GET MENU INFO (p. 30)
  - 14. 0x1E: GET PUBLIC KEYS LIST (p. 32)
  - 15. 0x1F: GET SYMMETRIC KEYS LIST (p. 33)
  - 16. 0x20: EDIT COMMUNICATION PARAMETERS (p. 33)
  - 17. 0x21: KEYS COMMAND (p. 34)
  - 18. 0x23: CHECK PASSWORD (p. 35)
- **19. 0x24: GET REPORT TAGS BY STAN** (p. 36)
  - 20. 0x25: SELECT CHIP APPLICATION (p. 38)
  - 21. 0x26: GET CARD READER STATE (p. 38)
- **22. 0x27: GET TERMINAL TAGS** (p. 39)
- **3. 0x40: External internet subcommands** (p. 40)
  - 1. 0x01: RECEIVE DATA (p. 40)
  - 2. 0x02: EVENT CONFIRM (p. 42)
  - 3. 0x03: GET MAX MTU (p. 43)
- **4. 0x0E: Borica subevents** (p. 44)

---

# Full text (extracted and structured)

DatecsPay card readers communication protocol
Version: 1.9

Change log

Version

Changes

1.1

1.2

1.3

1.4

1.5

1.6

1.7

1.8

1.9

Added "Note" and "Note 2" descriptions in subcommand "0x01: RECEIVE
DATA".
Added "Note" descriptions in subcommands "0x01: START PURCHASE +
GRATUITY / TIP" and "0x02: START PURCHASE + CASHBACK".
Added tags 0x9F04, 0xDF7D, 0xDF7E and 0xDF7F in the "7. TAGS” section.
Updated the document structure and added few other updated descriptions.

Added section “10. TRANSACTION FLOW.
Added “Note” description in section “11. EXAMPLE TRANSACTION”.

Added the following subcommands:
0x0B: DELETE BATCH
0x0C: CLEAR REVERSAL
0x1D: GET MENU INFO
0x1E: GET PUBLIC KEYS LIST
0x1F: GET SYMMETRIC KEYS LIST
0x20: EDIT COMMUNICATION PARAMETERS
0x21: KEYS COMMAND

Added the following subcommand:
0x23: GET PASSWORDS

0x23: GET PASSWORDS changed to 0x23: CHECK PASSWORD

Added the following subcommands:
0x25: SELECT CHIP APPLICATION
0x26: GET CARD READER STATE

Added the following subevent:
0x3F: SELECT CHIP APPLICATION

Added the following sections:
# 12. CARD READER ERROR STRINGS
# 13. HOST ERROR STRINGS

Updated section “6.Display result message”!
Added tags DF8004 - DF8006 in “1. 0x01: TRANSACTION COMPLETE”
Added subevent “1.0x82: USER INTERFACE”
Added “Note” in “10. Transaction flow” → “Transaction loop”

Added subcommand “4. 0x03: START PURCHASE + REFERENCE”
Added subevent “3. 0x03: PRINT HANG TRANSACTION RECEIPT”
Added “Note” in “13. 0x0A: START END OF DAY”

Added tags 0x9F1E and 0xDF32 in section “7. TAGS”
Added subcommand “0x27: GET TERMINAL TAGS”

Date

10.09.2020

11.09.2020

01.02.2021

02.02.2021

05.02.2021

16.02.2021

12.01.2022

18.07.2022

08.11.2022


---

Content
1.Packet format..........................................................................................................................................5
## 2. 0x3D: Borica subcommands...................................................................................................................6
## 1. 0x00: PING.........................................................................................................................................6
## 2. 0x01: TRANSACTION START.........................................................................................................7
### 1. 0x01: START PURCHASE...........................................................................................................8
### 2. 0x01: START PURCHASE + GRATUITY / TIP..........................................................................9
### 3. 0x02: START PURCHASE + CASHBACK.................................................................................9
### 4. 0x03: START PURCHASE + REFERENCE..............................................................................10
### 5. 0x04: START CASH ADVANCE................................................................................................11
### 6. 0x05: START AUTHORIZATION..............................................................................................11
### 7. 0x06: START PURCHASE + CODE..........................................................................................12
### 8. 0x07: START VOID OF PURCHASE........................................................................................13
### 9. 0x07: START VOID OF PURCHASE + GRATUITY / TIP.......................................................14
### 10. 0x07: START VOID OF PURCHASE + CASHBACK............................................................15
### 11. 0x08: START VOID OF CASH ADVANCE.............................................................................16
### 12. 0x09: START VOID OF AUTHORIZATION...........................................................................16
### 13. 0x0A: START END OF DAY....................................................................................................17
### 14. 0x0B: START LOYALTY BALANCE......................................................................................18
### 15. 0x0C: START LOYALTY SPEND............................................................................................19
### 16. 0x0D: START VOID OF LOYALTY SPEND...........................................................................19
### 17. 0x0E: START TEST CONNECTION.......................................................................................20
### 18. 0x0F: START TMS UPDATE...................................................................................................21
### 3. 0x02: GET RECEIPT TAGS............................................................................................................21
### 4. 0x03: TRANSACTION END...........................................................................................................22
### 5. 0x04: GET REPORT TAGS.............................................................................................................23
### 6. 0x05: GET REPORT INFO..............................................................................................................24
### 7. 0x06: GET PINPAD INFO...............................................................................................................25
### 8. 0x07: GET RTC................................................................................................................................26
### 9. 0x08: SET RTC................................................................................................................................27
### 10. 0x0B: DELETE BATCH................................................................................................................28
### 11. 0x0C: CLEAR REVERSAL...........................................................................................................28
### 12. 0x1A: GET PINPAD STATUS.......................................................................................................29
### 13. 0x1D: GET MENU INFO..............................................................................................................30
### 14. 0x1E: GET PUBLIC KEYS LIST..................................................................................................32
### 15. 0x1F: GET SYMMETRIC KEYS LIST........................................................................................33
### 16. 0x20: EDIT COMMUNICATION PARAMETERS......................................................................33
### 17. 0x21: KEYS COMMAND.............................................................................................................34
### 18. 0x23: CHECK PASSWORD..........................................................................................................35
### 19. 0x24: GET REPORT TAGS BY STAN..........................................................................................36
### 20. 0x25: SELECT CHIP APPLICATION...........................................................................................38
### 21. 0x26: GET CARD READER STATE............................................................................................38
### 22. 0x27: GET TERMINAL TAGS......................................................................................................39
### 3. 0x40: External internet subcommands..................................................................................................40
### 1. 0x01: RECEIVE DATA....................................................................................................................40
### 2. 0x02: EVENT CONFIRM................................................................................................................42
### 3. 0x03: GET MAX MTU....................................................................................................................43
### 4. 0x0E: Borica subevents.........................................................................................................................44


---

### 1. 0x01: TRANSACTION COMPLETE (PAYMENT RESULT) - NO CONFIRMATION NEEDED
.............................................................................................................................................................44
### 2. 0x02: INTERMEDIATE TRANSACTION COMPLETE (PAYMENT RESULT) - NO
CONFIRMATION NEEDED..............................................................................................................45
### 3. 0x03: PRINT HANG TRANSACTION RECEIPT.........................................................................45
### 4. 0x10: SEND LOG DATA.................................................................................................................46
### 5. 0x3F: SELECT CHIP APPLICATION.............................................................................................46
### 5. 0x0F: External internet subevents.........................................................................................................47
### 1. 0x01: SOCKET OPEN.....................................................................................................................47
### 2. 0x02: SOCKET CLOSE...................................................................................................................48
### 3. 0x03: SEND DATA..........................................................................................................................49
6.ERROR CODES...................................................................................................................................49
7.TAGS.....................................................................................................................................................51
8.REFERENCES......................................................................................................................................52
1.TRANSACTION_RESULTS...........................................................................................................52
2.INTERFACES..................................................................................................................................52
3.CL CARD SCHEMES.....................................................................................................................52
4.TRANSACTION TYPES.................................................................................................................52
5.SIGNATURE TYPES.......................................................................................................................53
6.CARD ISSUERS..............................................................................................................................53
7.TO TYPES........................................................................................................................................53
9.TLV STRUCTURE...............................................................................................................................53
10.TRANSACTION FLOW....................................................................................................................56
1.Check if the reader is connected.......................................................................................................58
2.Start a transaction.............................................................................................................................58
3.Transaction loop...............................................................................................................................58
4.Get additional information...............................................................................................................59
5.Finish the transaction........................................................................................................................59
6.Display result message.....................................................................................................................59
7.Display error message......................................................................................................................60
11.EXAMPLE TRANSACTION.............................................................................................................60
12.CARD READER ERROR STRINGS.................................................................................................62
13.HOST ERROR STRINGS..................................................................................................................63
### 14. 0x0B: EMV subevents........................................................................................................................64
### 1. 0x82: USER INTERFACE...............................................................................................................64


---

# 1. Packet format

For convenience, we will use “card reader” or “pinpad” for indicating the DatecsPay card reader, and
“ext device” for indicating the external device, which is communicating with the card reader (this can
be a mobile device, tablet, PC and etc).

• EXT DEVICE TO CARD READER:

'>' CMD 00 LH LL <DATA> CSUM

'>':
**CMD:**
LH:LL
**CSUM:**

start paket (ASCII symbol '>')
command number
length of DATA
xor of all bytes in the packet

Example:

```text
3E 3D 00 00 01 00 02
```

• CARD READER TO EXT DEVICE:

'>' 00 ST LH LL <DATA> CSUM

'>':
**ST:**
LH:LL
**CSUM:**

start paket (ASCII symbol '>')
status (see error codes)
length of DATA
xor of all bytes in the packet

Example:

```text
3E 00 00 00 00 3E
```

The timeout between different bytes is 2 seconds.
Once the card reader receives a valid packet, it will return a response to the external device, where the
field ST in the response will indicate if the command is executed successfully or if there is any error,
which occurred. The external device can set timeout = 5 seconds for awaiting a response from the card
reader after any kind of command was sent to the card reader.

Commands, which can be sent to the card reader:

•
•

0x3D – Borica command
0x40 – External internet command

Events, which can be received unexpectedly from the card reader:

•
•

0x0E – Borica event
0x0F – External internet event


---

Every command can contain multiple subcommands and every event can contain multiple subevents.
All   subcommands   and   subevents   are   packed   in   the   <DATA>   field   –   usually  the   first   byte   of   the
<DATA> field (DATA[0]).

# 2. 0x3D: Borica subcommands

Borica   command   contains   multiple   subcommands,   which   are   associated   with   almost   all   activities,
which   are   possible   to   be   executed   from   the   card   reader,   like   for   example   loading   configurations,
starting transactions, getting information for already started or already finished transactions and etc.

## 1. 0x00: PING

**DESCRIPTION:**

Ping the card reader.

**EXT DEVICE:**

3D 00 LH LL [SUBCMD]

**CARD READER:**

00 ST LH LL

**EXAMPLE:**

(EXT DEVICE -> CARD READER)
(CARD READER -> EXT DEVICE)

```text
>> 3E 3D 00 00 01 00 02
<< 3E 00 00 00 00 3E
```

**CLARIFICATION:**

(EXT DEVICE -> CARD READER):
'>':
**CMD:**
**00:**
**LH LL:**
**SUBCMD:**
**CSUM:**

0x3E - Start packet.
0x3D - Borica command.
0x00 - Fixed value '00'.
0x00 0x01 - The data length is 1 byte.
0x00 - PING subcommand.
0x02 - Xor of all bytes (3E 3D 00 00 01 00).

(CARD READER -> EXT DEVICE):
'>':
**00:**
**ST:**
**LH LL:**
**CSUM:**

0x3E - Start packet.
0x00 - Fixed value '00'.
0x00 - No error (ERROR CODES).
0x00 0x00 - The data length is 0 bytes.
0x3E - Xor of all bytes (3E 00 00 00 00).

## 2. 0x01: TRANSACTION START

**DESCRIPTION:**

Start a transaction.

**EXT DEVICE:**

3D 00 LH LL [SUBCMD] <DATA: VAR>


---

<DATA>:

[Transaction type]:

[1..14] TRANSACTION TYPE
01 - PURCHASE
02 - PURCHASE + CASHBACK
03 - PURCHASE + REFERENCE
04 - CASH ADVANCE
05 - AUTHORIZATION
06 - PURCHASE + CODE
07 - VOID OF PURCHASE
08 - VOID OF CASH ADVANCE
09 - VOID OF AUTHORIZATION
10 - END OF DAY
11 - LOYALTY BALANCE
12 - LOYALTY SPEND
13 - VOID OF LOYALTY SPEND
14 - TEST CONNECTION
15 - TMS UPDATE

<Transaction parameters: VAR>:

Tags, encoded in TLV format, depending from the transaction type (For
reference see "TLV STRUCTURE" section below):

BOR_CMD_TAG_AMOUNT
BOR_CMD_TAG_CASHBACK
BOR_CMD_TAG_RRN
BOR_CMD_TAG_AUTH_ID
BOR_CMD_TAG_REF
BOR_CMD_TAG_TIP

0x81
0x9F04
0xDF01
0xDF02
0xDF03
0xDF63

- [HEX BIG ENDIAN - 4 bytes]
- [HEX BIG ENDIAN - 4 bytes]
- [STRING]
- [STRING]
- [STRING]
- [HEX BIG ENDIAN - 4 bytes]

**CARD READER:**

00 ST LH LL

### 1. 0x01: START PURCHASE

NEEDED TAGS: 0x81

**EXAMPLE:**

(EXT DEVICE -> CARD READER) >>
(CARD READER -> EXT DEVICE) <<

```text
3E 3D 00 00 08 01 01 81 04 00 00 00 32 BC
3E 00 00 00 00 3E
```

**CLARIFICATION:**

(EXT DEVICE -> CARD READER):

'>':
**CMD:**
**00:**
**LH LL:**

0x3E - Start packet.
0x3D - Borica command.
0x00 - Fixed value '00'.
0x00 0x08 - The data length is 8 bytes.


---

**SUBCMD:**
[TRANS TYPE]:
<TRANS PARAMS: VAR>:
**CSUM:**

0x01 - TRANSACTION START subcommand.
0x01 - HEX format, PURCHASE

'81 04 00 00 00 32' - AMOUNT (tag 0x81) = 50 (0.50)

0xBC - Xor of all bytes (3E 3D 00 ..... 00 32).

(CARD READER -> EXT DEVICE):

'>':
**00:**
**ST:**
**LH LL:**
**CSUM:**

0x3E - Start packet.
0x00 - Fixed value '00'.
0x00 - No error (ERROR CODES).
0x00 0x00 - The data length is 0 bytes.
0x3E - Xor of all bytes (3E 00 00 00 00).

### 2. 0x01: START PURCHASE + GRATUITY / TIP

NEEDED TAGS: 0x81, 0xDF63

**EXAMPLE:**

(EXT DEVICE -> CARD READER) >>

(CARD READER -> EXT DEVICE) <<

**CLARIFICATION:**

(EXT DEVICE -> CARD READER):

```text
3E 3D 00 00 0F 01 01 81 04 00 00 00 1E DF 63 04
00 00 00 0A 25
3E 00 00 00 00 3E
```

'>':
**CMD:**
**00:**
**LH LL:**
**SUBCMD:**
[TRANS TYPE]:

0x3E - Start packet.
0x3D - Borica command.
0x00 - Fixed value '00'.
0x00 0x0F - The data length is 15 bytes.
0x01 - TRANSACTION START subcommand.
0x01 - HEX format, PURCHASE

<TRANS PARAMS: VAR>:

'81 04 00 00 00 1E DF 63 04 00 00 00 0A' - AMOUNT
(tag 0x81) = 30 (0.30) and GRATUITY / TIP (tag
0xDF63) = 10 (0.10)

**CSUM:**

0x25 - Xor of all bytes (3E 3D 00 ..... 00 0A).

(CARD READER -> EXT DEVICE):

'>':
**00:**
**ST:**
**LH LL:**
**CSUM:**

0x3E - Start packet.
0x00 - Fixed value '00'.
0x00 - No error (ERROR CODES).
0x00 0x00 - The data length is 0 bytes.
0x3E - Xor of all bytes (3E 00 00 00 00).

Note: Tag 0x81 should contain the total <Amount> + <Gratuity>. If you need to start a transaction for
total amount = 1.10 (1.00 amount + 0.10 Gratuity), then tag 0x81 should have value = '00 00 00 6E' and
tag 0xDF63 should have value = ' 00 00 00 0A'.


---

### 3. 0x02: START PURCHASE + CASHBACK

**NEEDED TAGS:**

0x81, 0x9F04

**EXAMPLE:**

(EXT DEVICE -> CARD READER) >>

(CARD READER -> EXT DEVICE) <<

```text
3E 3D 00 00 0F 01 02 81 04 00 00 00 32 9F 04 04
00 00 00 14 33
3E 00 00 00 00 3E
```

**CLARIFICATION:**

(EXT DEVICE -> CARD READER):

'>':
**CMD:**
**00:**
**LH LL:**
**SUBCMD:**
[TRANS TYPE]:

0x3E - Start packet.
0x3D - BORICA CMD command.
0x00 - Fixed value '00'.
0x00 0x0F - The data length is 15 bytes.
0x01 - TRANSACTION START subcommand.
0x02 - HEX format, PURCHASE + CASHBACK

<TRANS PARAMS: VAR>:

'81 04 00 00 00 32 9F 04 04 00 00 00 14' - AMOUNT (tag

0x81) = 50 (0.50) and CASHBACK (tag 9F04) = 20 (0.20)

**CSUM:**

0x33 - Xor of all bytes (3E 3D 00 ..... 00 14).

(CARD READER -> EXT DEVICE):

'>':
**00:**
**ST:**
**LH LL:**
**CSUM:**

0x3E - Start packet.
0x00 - Fixed value '00'.
0x00 - No error (ERROR CODES).
0x00 0x00 - The data length is 0 bytes.
0x3E - Xor of all bytes (3E 00 00 00 00).

Note: Tag 0x81 should contain only the <Amount>. If you need to start a transaction for total amount
= 1.10 (1.00 amount + 0.10 Cashback), then tag 0x81 should have value = '00 00 00 64' and tag 0x9F04
should have value = '00 00 00 0A'.

### 4. 0x03: START PURCHASE + REFERENCE

**NEEDED TAGS:**

0x81, 0xDF03

**EXAMPLE:**

(EXT DEVICE -> CARD READER) >>

(CARD READER -> EXT DEVICE) <<

```text
3E 3D 00 00 15 01 03 81 04 00 00 00 64 DF 03 0A
31 32 33 34 35 36 37 38 39 30 22
3E 00 00 00 00 3E
```

**CLARIFICATION:**

(EXT DEVICE -> CARD READER):

'>':
**CMD:**

0x3E - Start packet.
0x3D - BORICA CMD command.


---

**00:**
**LH LL:**
**SUBCMD:**
[TRANS TYPE]:

0x00 - Fixed value '00'.
0x00 0x15 - The data length is 21 bytes.
0x01 - TRANSACTION START subcommand.
0x03 - HEX format, PURCHASE + REFERENCE

<TRANS PARAMS: VAR>:

'81 04 00 00 00 64 DF 03 0A 31 32 33 34 35 36 37 38 39
30' - AMOUNT (tag 0x81) = 100 (1.00) and REFERENCE (tag
DF03) = "1234567890"

**CSUM:**

0x22 - Xor of all bytes (3E 3D 00 ..... 39 30).

(CARD READER -> EXT DEVICE):

'>':
**00:**
**ST:**
**LH LL:**
**CSUM:**

0x3E - Start packet.
0x00 - Fixed value '00'.
0x00 - No error (ERROR CODES).
0x00 0x00 - The data length is 0 bytes.
0x3E - Xor of all bytes (3E 00 00 00 00).

### 5. 0x04: START CASH ADVANCE

This transaction means cash withdrawals (such as ATM withdrawals).

**NEEDED TAGS:**
0x81

**EXAMPLE:**

(EXT DEVICE -> CARD READER) >>
(CARD READER -> EXT DEVICE) <<

```text
3E 3D 00 00 08 01 04 81 04 00 00 00 64 EF
3E 00 00 00 00 3E
```

**CLARIFICATION:**

(EXT DEVICE -> CARD READER):

'>':
**CMD:**
**00:**
**LH LL:**
**SUBCMD:**
[TRANS TYPE]:

0x3E - Start packet.
0x3D - Borica command.
0x00 - Fixed value '00'.
0x00 0x08 - The data length is 8 bytes.
0x01 - TRANSACTION START subcommand.
0x04 - HEX format, CASH ADVANCE

<TRANS PARAMS: VAR>:

'81 04 00 00 00 64' - AMOUNT (tag 0x81) = 100 (1.00)

**CSUM:**

0xEF - Xor of all bytes (3E 3D 00 ..... 00 64).

(CARD READER -> EXT DEVICE):

'>':
**00:**
**ST:**
**LH LL:**
**CSUM:**

0x3E - Start packet.
0x00 - Fixed value '00'.
0x00 - No error (ERROR CODES).
0x00 0x00 - The data length is 0 bytes.
0x3E - Xor of all bytes (3E 00 00 00 00).


---

### 6. 0x05: START AUTHORIZATION

This transaction doesn't withdraw the money from the account. It only blocks them. After that the
money can be returned with VOID OF AUTHORIZATION, or they can finally be withdrawed with the
transaction PURCHASE + CODE. These types of transactions are used in Hotels for example.

**NEEDED TAGS:**
0x81

**EXAMPLE:**

(EXT DEVICE -> CARD READER) >>
(CARD READER -> EXT DEVICE) <<

```text
3E 3D 00 00 08 01 05 81 04 00 00 00 64 EE
3E 00 00 00 00 3E
```

**CLARIFICATION:**

(EXT DEVICE -> CARD READER):

'>':
**CMD:**
**00:**
**LH LL:**
**SUBCMD:**
[TRANS TYPE]:

0x3E - Start packet.
0x3D - Borica command.
0x00 - Fixed value '00'.
0x00 0x08 - The data length is 8 bytes.
0x01 - TRANSACTION START subcommand.
0x05 - HEX format, AUTHORIZATION

<TRANS PARAMS: VAR>:

'81 04 00 00 00 64' - AMOUNT (tag 0x81) = 100 (1.00)

**CSUM:**

0xEE - Xor of all bytes (3E 3D 00 ..... 00 64).

(CARD READER -> EXT DEVICE):

'>':
**00:**
**ST:**
**LH LL:**
**CSUM:**

0x3E - Start packet.
0x00 - Fixed value '00'.
0x00 - No error (ERROR CODES).
0x00 0x00 - The data length is 0 bytes.
0x3E - Xor of all bytes (3E 00 00 00 00).

### 7. 0x06: START PURCHASE + CODE

When AUTHORIZATION has been done successfully, the Amount of the transaction was blocked, but
still  not  withdrawed  from the  account.  In  order to  withdraw   the  blocked  Amount,  PURCHASE  +
CODE needs to be done. That is why this type of transaction can successfully be done only after
successful  AUTHORIZATION   before   it.  When   the  AUTHORIZATION   is   being   approved,   unique
RRN and Authorization ID are returned from the host. They should be printed on the receipt. Then
when starting PURCHASE + CODE, these RRN and Authorization ID from the first transaction need
to be used in the command for starting a transaction. The amount also needs to be the same as in the
AUTHORIZATION.

NEEDED TAGS: 0x81, 0xDF01, 0xDF02


---

**EXAMPLE:**

(EXT DEVICE -> CARD READER) >>

(CARD READER -> EXT DEVICE) <<

**CLARIFICATION:**

(EXT DEVICE -> CARD READER):

```text
3E 3D 00 00 1B 01 06 81 04 00 00 00 64 DF 01 07
36 36 38 30 36 33 35 DF 02 06 39 32 30 32 31 32
CE
3E 00 00 00 00 3E
```

'>':
**CMD:**
**00:**
**LH LL:**
**SUBCMD:**
[TRANS TYPE]:

0x3E - Start packet.
0x3D - Borica command.
0x00 - Fixed value '00'.
0x00 0x1B - The data length is 27 bytes.
0x01 - TRANSACTION START subcommand.
0x06 - HEX format, PURCHASE + CODE

<TRANS PARAMS: VAR>:

'81 04 00 00 00 64 DF 01 07 36 36 38 30 36 33 35 DF 02
06 39 32 30 32 31 32' - AMOUNT (tag 0x81) =  100
(1.00), RRN (tag 0xDF01) = "6680635", Authorization ID
(tag 0xDF02) = "920212"

**CSUM:**

0xCE - Xor of all bytes (3E 3D 00 ..... 31 32).

(CARD READER -> EXT DEVICE):

'>':
**00:**
**ST:**
**LH LL:**
**CSUM:**

0x3E - Start packet.
0x00 - Fixed value '00'.
0x00 - No error (ERROR CODES).
0x00 0x00 - The data length is 0 bytes.
0x3E - Xor of all bytes (3E 00 00 00 00).

### 8. 0x07: START VOID OF PURCHASE

Voiding a Purchase. The Amount, RRN and Authorization ID, which are used here, need to be taken
from the Purchase, which will be voided. After sending the command, if the PINPAD discovers a
transaction, saved in the memory, which has the same Amount, RRN and Authorization ID as those,
which are sent in the command, the CARD READER will send the Purchase for voiding without
waiting for a card. But if the CARD READER doesn't discover such a transaction in the memory, it
will prompt for a card and after this it will send the data for voiding to the server. This way it can void
Purchase from previous days.
**NEEDED TAGS:**

0x81, 0xDF01, 0xDF02

**EXAMPLE:**

(EXT DEVICE -> CARD READER) >>

(CARD READER -> EXT DEVICE) <<

**CLARIFICATION:**

(EXT DEVICE -> CARD READER):

```text
3E 3D 00 00 1B 01 07 81 04 00 00 00 64 DF 01 07
36 36 38 30 36 33 35 DF 02 06 39 32 30 32 31 32
CF
3E 00 00 00 00 3E
```


---

'>':
**CMD:**
**00:**
**LH LL:**
**SUBCMD:**
[TRANS TYPE]:

0x3E - Start packet.
0x3D - Borica command.
0x00 - Fixed value '00'.
0x00 0x1B - The data length is 27 bytes.
0x01 - TRANSACTION START subcommand.
0x07 - HEX format, VOID OF PURCHASE

<TRANS PARAMS: VAR>:

'81 04 00 00 00 64 DF 01 07 36 36 38 30 36 33 35 DF 02

06 39 32 30 32 31 32' - AMOUNT (tag 0x81) = 100 (1.00),
RRN (tag 0xDF01) = "6680635", Authorization ID (tag
0xDF02) = "920212"

**CSUM:**

0xCF - Xor of all bytes (3E 3D 00 ..... 31 32).

(CARD READER -> EXT DEVICE):

'>':
**00:**
**ST:**
**LH LL:**
**CSUM:**

0x3E - Start packet.
0x00 - Fixed value '00'.
0x00 - No error (ERROR CODES).
0x00 0x00 - The data length is 0 bytes.
0x3E - Xor of all bytes (3E 00 00 00 00).

### 9. 0x07: START VOID OF PURCHASE + GRATUITY / TIP

Voiding a Purchase + Gratuity. The Amount, Gratuity, RRN and Authorization ID, which are used here,
need to be taken from the Purchase + Gratuity, which will be voided. After sending the command, if the
CARD READER discovers a transaction, saved in the memory, which has the same Amount, Gratuity,
RRN and Authorization ID as those, which are sent in the command, the CARD READER will send
the Purchase for voiding without waiting for a card. But if the CARD READER doesn't discover such a
transaction in the memory, it will prompt for a card and after this it will send the data for voiding to the
server. This way it can void Purchase from previous days.

**NEEDED TAGS:**

0x81, 0xDF63, 0xDF01, 0xDF02

**EXAMPLE:**

(EXT DEVICE -> CARD READER) >>

(CARD READER -> EXT DEVICE) <<

**CLARIFICATION:**

(EXT DEVICE -> CARD READER):

```text
3E 3D 00 00 22 01 07 81 04 00 00 00 64 DF 63 04
00 00 00 0A DF 01 07 36 36 38 30 36 33 35 DF 02
06 39 32 30 32 31 32 44
3E 00 00 00 00 3E
```

'>':
**CMD:**
**00:**
**LH LL:**
**SUBCMD:**

0x3E - Start packet.
0x3D - Borica command.
0x00 - Fixed value '00'.
0x00 0x22 - The data length is 34 bytes.
0x01 - TRANSACTION START subcommand.


---

[TRANS TYPE]:

0x07 - HEX format, VOID OF PURCHASE

<TRANS PARAMS: VAR>:

'81 04 00 00 00 64 DF 63 04 00 00 00 0A DF 01 07 36 36
38 30 36 33 35 DF 02 06 39 32 30 32 31 32' - AMOUNT
(tag 0x81) = 100 (1.00), Gratuity (tag 0xDF63) = 10
(0.10), RRN (tag 0xDF01) = "6680635", Authorization ID
(tag 0xDF02) = "920212"

**CSUM:**

0x44 - Xor of all bytes (3E 3D 00 ..... 31 32).

(CARD READER -> EXT DEVICE):

'>':
**00:**
**ST:**
**LH LL:**
**CSUM:**

0x3E - Start packet.
0x00 - Fixed value '00'.
0x00 - No error (ERROR CODES).
0x00 0x00 - The data length is 0 bytes.
0x3E - Xor of all bytes (3E 00 00 00 00).

10.

0x07: START VOID OF PURCHASE + CASHBACK

Voiding a Purchase + Cashback. The Amount, Cashback, RRN and Authorization ID, which are used
here,   need   to   be   taken   from   the   Purchase   +   Cashback,   which   will   be   voided.  After   sending   the
command, if the PINPAD discovers a transaction, saved in the memory, which has the same Amount,
RRN and Authorization ID as those, which are sent in the command, the CARD READER will
the Purchase for voiding without waiting for a card. But if the CARD READER doesn't discover such a
transaction in the memory, it will prompt for a card and after this it will send the data for voiding to the
server. This way it can void Purchase from previous days.

send

**NEEDED TAGS:**

0x81, 0x9F04, 0xDF01, 0xDF02

**EXAMPLE:**

(EXT DEVICE -> CARD READER) >>

(CARD READER -> EXT DEVICE) <<

**CLARIFICATION:**

```text
3E 3D 00 00 22 01 07 81 04 00 00 00 32 9F 04 04
00 00 00 14 DF 01 07 36 36 38 30 36 33 35 DF 02
06 39 32 30 32 31 32 2B
3E 00 00 00 00 3E
```

(EXT DEVICE -> CARD READER):
'>':
**CMD:**
**00:**
**LH LL:**
**SUBCMD:**
[TRANS TYPE]:

0x3E - Start packet.
0x3D - Borica command.
0x00 - Fixed value '00'.
0x00 0x22 - The data length is 34 bytes.
0x01 - TRANSACTION START subcommand.
0x07 - HEX format, VOID OF PURCHASE

<TRANS PARAMS: VAR>:

'81 04 00 00 00 32 9F 04 04 00 00 00 14 DF 01 07 36 36 38 30 36
33 35 DF 02 06 39 32 30 32 31 32' - AMOUNT (tag 0x81) = 50


---

(0.50), Cashback (tag 0x9F04) = 20 (0.20), RRN (tag 0xDF01) =
"6680635", Authorization ID (tag 0xDF02) = "920212"

**CSUM:**

0x2B - Xor of all bytes (3E 3D 00 ..... 31 32).

(CARD READER -> EXT DEVICE):

'>':
**00:**
**ST:**
**LH LL:**
**CSUM:**

0x3E - Start packet.
0x00 - Fixed value '00'.
0x00 - No error (ERROR CODES).
0x00 0x00 - The data length is 0 bytes.
0x3E - Xor of all bytes (3E 00 00 00 00).

11.

0x08: START VOID OF CASH ADVANCE

Voiding a Cash Advance. The Amount, RRN and Authorization ID, which are used here, need to be
taken   from   the   Cash  Advance,   which   will   be   voided.  After   sending   the   command,   if   the   CARD
READER   discovers   a   transaction,   saved   in   the   memory,   which   has   the   same  Amount,   RRN   and
Authorization ID as those, which are sent in the command, the CARD READER will
the
Cash Advance for voiding without waiting for a card.

send

**NEEDED TAGS:**

0x81, 0xDF01, 0xDF02

**EXAMPLE:**

(EXT DEVICE -> CARD READER) >>

(CARD READER -> EXT DEVICE) <<

**CLARIFICATION:**

(EXT DEVICE -> CARD READER):

```text
3E 3D 00 00 1B 01 08 81 04 00 00 00 64 DF 01 07
36 36 38 30 36 33 35 DF 02 06 39 32 30 32 31 32
C0
3E 00 00 00 00 3E
```

'>':
**CMD:**
**00:**
**LH LL:**
**SUBCMD:**
[TRANS TYPE]:

0x3E - Start packet.
0x3D - Borica command.
0x00 - Fixed value '00'.
0x00 0x1B - The data length is 27 bytes.
0x01 - TRANSACTION START subcommand.
0x08 - HEX format, VOID OF CASH ADVANCE

<TRANS PARAMS: VAR>:

'81 04 00 00 00 64 DF 01 07 36 36 38 30 36 33 35 DF 02

06 39 32 30 32 31 32' - AMOUNT (tag 0x81) = 100 (1.00),
RRN (tag 0xDF01) = "6680635", Authorization ID (tag
0xDF02) = "920212"

**CSUM:**

0xC0 - Xor of all bytes (3E 3D 00 ..... 31 32).

(CARD READER -> EXT DEVICE):

'>':
**00:**
**ST:**

0x3E - Start packet.
0x00 - Fixed value '00'.
0x00 - No error (ERROR CODES).


---

**LH LL:**
**CSUM:**

0x00 0x00 - The data length is 0 bytes.
0x3E - Xor of all bytes (3E 00 00 00 00).

12.

0x09: START VOID OF AUTHORIZATION

Voiding an Authorization. The Amount, RRN and Authorization ID, which are used here, need to be
taken   from   the  Authorization,   which   will   be   voided.  After   sending   the   command,   if   the   CARD
READER   discovers   a   transaction,   saved   in   the   memory,   which   has   the   same  Amount,   RRN   and
the
Authorization ID as those, which are sent in the command, the CARD READER will
Authorization for voiding without waiting for a card. But if the CARD READER doesn't discover such
a transaction in the memory, it will prompt for a card and after this it will send the data for voiding to
the server. This way it can void Authorization from previous days.

send

**NEEDED TAGS:**

0x81, 0xDF01, 0xDF02

**EXAMPLE:**

(EXT DEVICE -> CARD READER) >>

(CARD READER -> EXT DEVICE) <<

**CLARIFICATION:**

(EXT DEVICE -> CARD READER):

```text
3E 3D 00 00 1B 01 09 81 04 00 00 00 64 DF 01 07
36 36 38 30 36 33 35 DF 02 06 39 32 30 32 31 32
C1
3E 00 00 00 00 3E
```

'>':
**CMD:**
**00:**
**LH LL:**
**SUBCMD:**
[TRANS TYPE]:

0x3E - Start of the packet.
0x3D - Borica command.
0x00 - Fixed value '00'.
0x00 0x1B - The data length is 27 bytes.
0x01 - TRANSACTION START subcommand.
0x09 - HEX format, VOID OF AUTHORIZATION

<TRANS PARAMS: VAR>:

'81 04 00 00 00 64 DF 01 07 36 36 38 30 36 33 35 DF 02

06 39 32 30 32 31 32' - AMOUNT (tag 0x81) = 100 (1.00),
RRN (tag 0xDF01) = "6680635", Authorization ID (tag
0xDF02) = "920212"

**CSUM:**

0xC1 - Xor of all bytes (3E 3D 00 ..... 31 32).

(CARD READER -> EXT DEVICE):

'>':
**00:**
**ST:**
**LH LL:**
**CSUM:**

0x3E - Start of the packet.
0x00 - Fixed value '00'.
0x00 - No error (ERROR CODES).
0x00 0x00 - The data length is 0 bytes.
0x3E - Xor of all bytes (3E 00 00 00 00).


---

13.

0x0A: START END OF DAY

Note: Before starting End of day and before printing the Daily Report receipt, containing all the sums,
the command “0x1A: GET PINPAD STATUS” should be sent to the Card reader and if the response
contains “'C': HANG TRANSACTION 'C'”, then a Test connection should be executed first (0x0E:
START TEST CONNECTION). After the Test connection, the receipt can be now constructed and
printed and End of day can be executed.

Before   performing   End   Of   Day,   Daily   Report   receipt   needs   to   be   printed.   It   needs   to   be   printed
BEFORE the transaction, because if End Of Day is successful, it will delete all transactions from the
log, and it will not be possible information for the transactions to be taken anymore. In order to print
the receipt, (04: GET REPORT TAGS) command needs to be called multiple times. The first call needs
to be with parameter (01 - FIRST RECORD) and after that it needs to be called in loop with parameter
(02 - NEXT RECORDS) until the ST field in the response from the CARD READER becomes (08). If
ST field from the response has value (08), this means, that the last transaction in the log was reached.
For each transaction the transaction type and some other information needs to be taken, in order to
calculate   the   transaction   sums   and   the   card   sums   (for   transactions,   different   from   TEST
CONNECTION and END OF DAY, which are successful (TAG_DF05_TRANSACTION_RESULT
value   =   0)   and   which   are   not   reversed   transactions   (BOR_TAG_TO_TYPE   value   !=   1)).  After
performing End Of Day, it is recommended to print on the end of the Daily Report if the File was sent
successfully or not.

**NEEDED TAGS:**
none

**EXAMPLE:**

(EXT DEVICE -> CARD READER) >>
(CARD READER -> EXT DEVICE) <<

```text
3E 3D 00 00 02 01 0A 0A
3E 00 00 00 00 3E
```

**CLARIFICATION:**

(EXT DEVICE -> CARD READER):

'>':
**CMD:**
**00:**
**LH LL:**
**SUBCMD:**
[TRANS TYPE]:
<TRANS PARAMS: VAR>: none
**CSUM:**

0x3E - Start of the packet.
0x3D - Borica command.
0x00 - Fixed value '00'.
0x00 0x02 - The data length is 2 bytes.
0x01 - TRANSACTION START subcommand.
0x0A - HEX format, END OF DAY

0x0A - Xor of all bytes (3E 3D 00 00 02 01 0A).

(CARD READER -> EXT DEVICE):

'>':
**00:**
**ST:**
**LH LL:**
**CSUM:**

0x3E - Start of the packet.
0x00 - Fixed value '00'.
0x00 - No error (ERROR CODES).
0x00 0x00 - The data length is 0 bytes.
0x3E - Xor of all bytes (3E 00 00 00 00).


---

14.

0x0B: START LOYALTY BALANCE

**NEEDED TAGS:**

0x81 - needs to have value 0!

**EXAMPLE:**

(EXT DEVICE -> CARD READER) >>
(CARD READER -> EXT DEVICE) <<

```text
3E 3D 00 00 08 01 0B 81 04 00 00 00 00 84
3E 00 00 00 00 3E
```

**CLARIFICATION:**

(EXT DEVICE -> CARD READER):

'>':
**CMD:**
**00:**
**LH LL:**
**SUBCMD:**
[TRANS TYPE]:

0x3E - Start of the packet.
0x3D - Borica command.
0x00 - Fixed value '00'.
0x00 0x08 - The data length is 8 bytes.
0x01 - TRANSACTION START subcommand.
0x0B - HEX format, LOYALTY BALANCE

<TRANS PARAMS: VAR>:

'81 04 00 00 00 00' - AMOUNT (tag 0x81) = 0

**CSUM:**

0x84 - Xor of all bytes (3E 3D 00 ..... 00 00).

(CARD READER -> EXT DEVICE):

'>':
**00:**
**ST:**
**LH LL:**
**CSUM:**

0x3E - Start of the packet.
0x00 - Fixed value '00'.
0x00 - No error (ERROR CODES).
0x00 0x00 - The data length is 0 bytes.
0x3E - Xor of all bytes (3E 00 00 00 00).

15.

0x0C: START LOYALTY SPEND

**NEEDED TAGS:**
0x81

**EXAMPLE:**

(EXT DEVICE -> CARD READER) >>
(CARD READER -> EXT DEVICE) <<

```text
3E 3D 00 00 08 01 0C 81 04 00 00 00 3C BF
3E 00 00 00 00 3E
```

**CLARIFICATION:**

(EXT DEVICE -> CARD READER):

'>':
**CMD:**
**00:**
**LH LL:**
**SUBCMD:**
[TRANS TYPE]:

0x3E - Start of the packet.
0x3D - Borica command.
0x00 - Fixed value '00'.
0x00 0x08 - The data length is 8 bytes.
0x01 - TRANSACTION START subcommand.
0x0C - HEX format, LOYALTY SPEND

<TRANS PARAMS: VAR>:

'81 04 00 00 00 3C' - AMOUNT (tag 0x81) = 60 POINTS


---

**CSUM:**

0xBF - Xor of all bytes (3E 3D 00 ..... 00 3C).

(CARD READER -> EXT DEVICE):

'>':
**00:**
**ST:**
**LH LL:**
**CSUM:**

0x3E - Start of the packet.
0x00 - Fixed value '00'.
0x00 - No error (ERROR CODES).
0x00 0x00 - The data length is 0 bytes.
0x3E - Xor of all bytes (3E 00 00 00 00).

16.

0x0D: START VOID OF LOYALTY SPEND

**NEEDED TAGS:**

0x81, 0xDF01, 0xDF02

**EXAMPLE:**

(EXT DEVICE -> CARD READER) >>

(CARD READER -> EXT DEVICE) <<

**CLARIFICATION:**

(EXT DEVICE -> CARD READER):

```text
3E 3D 00 00 1B 01 0D 81 04 00 00 00 3C DF 01
07 36 39 38 30 35 36 38 DF 02 06 39 32 30 32 31
35 9E
3E 00 00 00 00 3E
```

'>':
**CMD:**
**00:**
**LH LL:**
**SUBCMD:**
[TRANS TYPE]:

0x3E - Start of the packet.
0x3D - Borica command.
0x00 - Fixed value '00'.
0x00 0x1B - The data length is 27 bytes.
0x01 - TRANSACTION START subcommand.
0x0D - HEX format, VOID OF LOYALTY SPEND

<TRANS PARAMS: VAR>:

'81 04 00 00 00 3C DF 01 07 36 39 38 30 35 36 38 DF 02
06 39 32 30 32 31 35' - AMOUNT (tag 0x81) = 60
POINTS - AMOUNT (tag 0x81) = 60 POINTS, RRN (tag
0xDF01) = "6980568", Authorization ID (tag 0xDF02) =
"920215"

**CSUM:**

0x9E - Xor of all bytes (3E 3D 00 ..... 31 35).

(CARD READER -> EXT DEVICE):

'>':
**00:**
**ST:**
**LH LL:**
**CSUM:**

0x3E - Start of the packet.
0x00 - Fixed value '00'.
0x00 - No error (ERROR CODES).
0x00 0x00 - The data length is 0 bytes.
0x3E - Xor of all bytes (3E 00 00 00 00).


---

17.

0x0E: START TEST CONNECTION

**NEEDED TAGS:**
none

**EXAMPLE:**

(EXT DEVICE -> CARD READER) >>
(CARD READER -> EXT DEVICE) <<

```text
3E 3D 00 00 02 01 0E 0E
3E 00 00 00 00 3E
```

**CLARIFICATION:**

(EXT DEVICE -> CARD READER):

'>':
**CMD:**
**00:**
**LH LL:**
**SUBCMD:**
[TRANS TYPE]:
<TRANS PARAMS: VAR>: none
**CSUM:**

0x3E - Start of the packet.
0x3D - Borica command.
0x00 - Fixed value '00'.
0x00 0x02 - The data length is 2 bytes.
0x01 - TRANSACTION START subcommand.
0x0E - HEX format, TEST CONNECTION

0x0E - Xor of all bytes (3E 3D 00 00 02 01 0E).

(CARD READER -> EXT DEVICE):

'>':
**00:**
**ST:**
**LH LL:**
**CSUM:**

0x3E - Start of the packet.
0x00 - Fixed value '00'.
0x00 - No error (ERROR CODES).
0x00 0x00 - The data length is 0 bytes.
0x3E - Xor of all bytes (3E 00 00 00 00).

18.

0x0F: START TMS UPDATE

**NEEDED TAGS:**
none

**EXAMPLE:**

(EXT DEVICE -> CARD READER) >>
(CARD READER -> EXT DEVICE) <<

```text
3E 3D 00 00 02 01 0F 0F
3E 00 00 00 00 3E
```

**CLARIFICATION:**

(EXT DEVICE -> CARD READER):

'>':
**CMD:**
**00:**
**LH LL:**
**SUBCMD:**
[TRANS TYPE]:
<TRANS PARAMS: VAR>: none
**CSUM:**

0x3E - Start of the packet.
0x3D - BORICA CMD command.
0x00 - Fixed value '00'.
0x00 0x02 - The data length is 2 bytes.
0x01 - TRANSACTION START subcommand.
0x0F - HEX format, TMS UPDATE

0x0F - Xor of all bytes (3E 3D 00 00 02 01 0F).

(CARD READER -> EXT DEVICE):


---

'>':
**00:**
**ST:**
**LH LL:**
**CSUM:**

0x3E - Start of the packet.
0x00 - Fixed value '00'.
0x00 - No error (ERROR CODES).
0x00 0x00 - The data length is 0 bytes.
0x3E - Xor of all bytes (3E 00 00 00 00).

### 3. 0x02: GET RECEIPT TAGS

**DESCRIPTION:**

At  the   end  of  the   transaction,  this  command   can  be  used  to   get  information   for  the  lastly

performed transaction. This way a receipt can be printed.

**EXT DEVICE:**

3D 00 LH LL 02 <TAGS: VAR>

<TAGS: VAR>:

Tags to be returned. (For reference see "TLV STRUCTURE" and "TAGS" sections
below).

**CARD READER:**

00 ST LH LL <DATA: VAR>

<DATA: VAR>:

Returned tags data

**EXAMPLE:**

If Purchase was performed and we want to get the amount and the transaction type, then we need to
send the following command:

(EXT DEVICE -> CARD READER) >>
(CARD READER -> EXT DEVICE) <<

```text
3E 3D 00 00 04 02 81 DF 10 4B
3E 00 08 00 00 36
```

**CLARIFICATION:**

(EXT DEVICE -> CARD READER):

'>':
**CMD:**
**00:**
**LH LL:**
**SUBCMD:**
<TAGS: VAR>:

0x3E - Start of the packet.
0x3D - BORICA CMD command.
0x00 - Fixed value '00'.
0x00 0x04 - The data length is 4 bytes.
0x02 - GET RECEIPT TAGS subcommand.
'81 DF 10' - Here we need to list all tags, which we would like to
get. In this case we need to get 2 tags - 0x81 and 0xDF10.

**CSUM:**

0x4B - Xor of all bytes (3E 3D 00 ..... DF 10).

(CARD READER -> EXT DEVICE)

'>':
**00:**

0x3E - Start of the packet.
0x00 - Fixed value '00'.


---

**ST:**

0x08 - This command needs to be called only in the end of a
transaction. In other cases it will return ST with value (08)
- There is no data. In this case no data will be returned.

**LH LL:**
<DATA: VAR>:
**CSUM:**

0x00 0x00 - The data length is 0 bytes.
none
0x36 - Xor of all bytes (3E 00 08 00 00).

### 4. 0x03: TRANSACTION END

**DESCRIPTION:**

This command is being used if the EXT DEVICE needs externally to force quit the transaction,

after it was started, or in the end of every transaction.

**EXT DEVICE:**

3D 00 LH LL 03 <CFM: 2>

<CFM: 2>:

This parameter is optional. If it is not present, then the "END OK" is used by default. If
it is present, then it should have any of the following values:

[CFM HIGH][CFM LOW]:
00 00 - END FAIL
00 01 - END OK

**CARD READER:**

00 ST 00 00

**EXAMPLE:**

(EXT DEVICE -> CARD READER) >>
(CARD READER -> EXT DEVICE) <<

```text
3E 3D 00 00 03 03 00 00 03
3E 00 00 00 00 3E
```

**CLARIFICATION:**

(EXT DEVICE -> CARD READER):

'>':
**CMD:**
**00:**
**LH LL:**
**SUBCMD:**
<CFM: 2>
**CSUM:**

0x3E - Start of the packet.
0x3D - Borica command.
0x00 - Fixed value '00'.
0x00 0x03 - The data length is 3 bytes.
0x03 - TRANSACTION END subcommand.
0x00 0x00 - END FAIL
0x03 - Xor of all bytes (3E 3D 00 00 03 03 00 00).

(CARD READER -> EXT DEVICE)

'>':
**00:**
**ST:**
**LH LL:**
**CSUM:**

0x3E - Start of the packet.
0x00 - Fixed value '00'.
0x00 - No error (ERROR CODES).
0x00 0x00 - The data length is 0 bytes.
0x3E - Xor of all bytes (3E 00 00 00 00).


---

### 5. 0x04: GET REPORT TAGS

This command is being used when we need to get some information for some specific transaction. We
can get information for the last transaction (with parameter (03 - LAST RECORD)), then we can get
information for all transactions one by one before the last (if we call the same command multiple times,
but with parameter (04 - PREVIOUS RECORD). We can also get information for the first one (01 -
FIRST RECORD) and then call the same command multiple times  to get information for all next
commands one by one (with parameter (02 - NEXT RECORDS)). It is similar to the command (02:
GET RECEIPT TAGS).

**EXT DEVICE:**

3D 00 LH LL 04 <TYPE: 2> <TAGS: VAR>

<TYPE>

[TYPE HIGH][TYPE LOW]:
00 01 - FIRST RECORD
00 02 - NEXT RECORDS
00 03 - LAST RECORD
00 04 - PREVIOUS RECORD
00 10 - GET ALL RECORDS AS EVENTS

<TAGS>

Tags to be returned. (For reference see "TLV STRUCTURE" and "TAGS"
sections below)

**CARD READER:**

00 ST LH LL <DATA: VAR>

**EXAMPLE:**

If we want to get the amount for the first transaction, then we need to send this command:

(EXT DEVICE -> CARD READER) >>
(CARD READER -> EXT DEVICE) <<

```text
3E 3D 00 00 04 04 00 01 81 83
3E 00 00 00 06 81 04 00 00 00 64 D9
```

**CLARIFICATION:**

(EXT DEVICE -> CARD READER):

'>':
**CMD:**
**00:**
**LH LL:**
**SUBCMD:**
<TYPE: 2>:
<TAGS: VAR>:

0x3E - Start of the packet.
0x3D - Borica command.
0x00 - Fixed value '00'.
0x00 0x04 - The data length is 4 bytes.
0x04 - GET REPORT TAGS subcommand.
0x00 0x01 - We want to get information for the FIRST RECORD.
0x81 - Here we need to list all tags, which we would like to get.

In this case we need to get 1 tag - 0x81.

**CSUM:**

0x83 - Xor of all bytes (3E 3D 00 ..... 01 81).

(CARD READER -> EXT DEVICE):

'>':
**00:**
**ST:**
**LH LL:**

0x3E - Start of the packet.
0x00 - Fixed value '00'.
0x00 - No error (ERROR CODES).
0x00 0x06 - The data length is 6 bytes.


---

<DATA: VAR>:

**CSUM:**

'81 04 00 00 00 64' - The first transaction in this device has
amount = 100 (1.00).
0xD9 - Xor of all bytes (3E 00 00 ..... 00 64).

### 6. 0x05: GET REPORT INFO

**EXT DEVICE:**

```text
3D 00 00 01 05
```

**CARD READER:**

00 ST 00 02 <RECCNT: 2>

<RECCNT>

[RECCNT HIGH][RECCNT LOW]: THE COUNT OF RECORDS (0..65535)

**EXAMPLE:**

(EXT DEVICE -> CARD READER) >>
(CARD READER -> EXT DEVICE) <<

```text
3E 3D 00 00 01 05 07
3E 00 00 00 02 01 6B 56
```

**CLARIFICATION:**

(EXT DEVICE -> CARD READER):

'>':
**CMD:**
**00:**
**LH LL:**
**SUBCMD:**
**CSUM:**

0x3E - Start of the packet.
0x3D - Borica command.
0x00 - Fixed value '00'.
0x00 0x01 - The data length is 1 byte.
0x05 - GET REPORT INFO subcommand.
0x07 - Xor of all bytes (3E 3D 00 00 01 05).

(CARD READER -> EXT DEVICE):

'>':
**00:**
**ST:**
**LH LL:**
<RECCNT: 2>:
**CSUM:**

0x3E - Start of the packet.
0x00 - Fixed value '00'.
0x00 - No error (ERROR CODES).
0x00 0x02 - The data length is 2 bytes.
0x01 0x6B - The count of records is 363.
0x56 - Xor of all bytes (3E 00 00 00 02 01 6B).

### 7. 0x06: GET PINPAD INFO

**EXT DEVICE:**

```text
3D 00 00 01 06
```

**CARD READER:**

00 ST 00 2B <DATA: 43 BYTES>


---

<DATA>:

<MODEL NAME: 20 BYTES>:  MODEL OF THE PINPAD
<SERIAL NUMBER: 10 BYTES>: SERIAL NUMBER OF THE PINPAD
<SOFT VER: 4 BYTES>:
<TERMINAL ID: 8 BYTES>:
[MENU TYPE]:

SOFTWARE VERSION OF THE PINPAD
TERMINAL ID OF THE PINPAD
TYPE OF THE MENU OF THE TERMINAL

BOR_MENU_TYPE_TRADING
BOR_MENU_TYPE_TRADING_REF
BOR_MENU_TYPE_TRADING_CASHBACK
BOR_MENU_TYPE_HOTEL_RENT_A_CAR
BOR_MENU_TYPE_BAR_RESTAURANT
BOR_MENU_TYPE_BANK_CHANGE
BOR_MENU_TYPE_TEST

1
2
3
4
5
6
7

**EXAMPLE:**

(EXT DEVICE -> CARD READER) >>
(CARD READER -> EXT DEVICE) <<

```text
3E 3D 00 00 01 06 04
3E 00 00 00 2B 42 6C 75 65 50 61 64 2D 35 30 00
00 00 00 00 00 00 00 00 00 30 39 30 31 39 30 30
30 30 31 01 01 17 00 39 33 38 30 30 31 33 33 07
45
```

**CLARIFICATION:**

(EXT DEVICE -> CARD READER):

'>':
**CMD:**
**00:**
**LH LL:**
**SUBCMD:**
**CSUM:**

0x3E - Start of the packet.
0x3D – Borica command.
0x00 - Fixed value '00'.
0x00 0x01 - The data length is 1 byte.
0x06 - GET PINPAD INFO subcommand.
0x04 - Xor of all bytes (3E 3D 00 00 01 06).

(CARD READER -> EXT DEVICE)

'>':
**00:**
**ST:**
**LH LL:**
<MODEL NAME: 20 BYTES>:

0x3E - Start of the packet.
0x00 - Fixed value '00'.
0x00 - No error (ERROR CODES).
0x00 0x2B - The data length is 43 bytes.

'42 6C 75 65 50 61 64 2D 35 30 00 00 00 00 00 00
00 00 00 00' - STRING format, "BluePad-50"

<SERIAL NUMBER: 10 BYTES>:  '30 39 30 31 39 30 30 30 30 31' - STRING format,
"0901900001"
'01 01 17 00'
'39 33 38 30 30 31 33 33' - STRING format,
"93800133"

<SOFT VER: 4 BYTES>:
<TERMINAL ID: 8 BYTES>:

- HEX format, version 1.1.23.0

[MENU TYPE]:
**CSUM:**

0x07 - HEX format, <BOR_MENU_TYPE_TEST>
0x45 - Xor of all bytes (3E 00 00 ..... 33 07).


---

### 8. 0x07: GET RTC

**EXT DEVICE:**

```text
3D 00 00 01 07
```

**CARD READER:**

00 ST 00 06 year[1] month[1] date[1] hour[1] min[1] sec[1]

**EXAMPLE:**

(EXT DEVICE -> CARD READER) >>
(CARD READER -> EXT DEVICE) <<

```text
3E 3D 00 00 01 07 05
3E 00 00 00 06 13 03 14 09 30 2C 29
```

**CLARIFICATION:**

(EXT DEVICE -> CARD READER):

'>':
**CMD:**
**00:**
**LH LL:**
**SUBCMD:**
**CSUM:**

0x3E - Start of the packet.
0x3D – Borica command.
0x00 - Fixed value '00'.
0x00 0x01 - The data length is 1 byte.
0x07 - GET RTC subcommand.
0x05 - Xor of all bytes (3E 3D 00 00 01 07).

(CARD READER -> EXT DEVICE)

'>':
**00:**
**ST:**
**LH LL:**
year[1]:
month[1]:
date[1]:
hour[1]:
min[1]:
sec[1]:
**CSUM:**

0x3E - Start of the packet.
0x00 - Fixed value '00'.
0x00 - No error (ERROR CODES).
0x00 0x06 - The data length is 6 bytes.
0x13 - HEX format, year 19 (2019)
0x03 - HEX format, month 03
0x14 - HEX format, day 20
0x09 - HEX format, hour 09
0x30 - HEX format, minute 48
0x2C - HEX format, second 44
0x29 - Xor of all bytes (3E 00 00 ..... 30 2C).

### 9. 0x08: SET RTC

**EXT DEVICE:**

3D 00 00 07 08 year[1] month[1] date[1] hour[1] min[1] sec[1]

**CARD READER:**

00 ST 00 00

**EXAMPLE:**

(EXT DEVICE -> CARD READER) >>
(CARD READER -> EXT DEVICE) <<

```text
3E 3D 00 00 07 08 13 03 14 09 30 2C 1D
3E 00 00 00 00 3E
```


---

**CLARIFICATION:**

(EXT DEVICE -> CARD READER)

'>':
**CMD:**
**00:**
**LH LL:**
**SUBCMD:**
year[1]:
month[1]:
date[1]:
hour[1]:
min[1]:
sec[1]:
**CSUM:**

0x3E - Start of the packet.
0x3D - Borica command.
0x00 - Fixed value '00'.
0x00 0x07 - The data length is 7 bytes.
0x08 - SET RTC subcommand.
0x13 - HEX format, year 19 (2019)
0x03 - HEX format, month 03
0x14 - HEX format, day 20
0x09 - HEX format, hour 09
0x30 - HEX format, minute 48
0x2C - HEX format, second 44
0x1D - Xor of all bytes (3E 3D 00 ..... 30 2C).

(CARD READER -> EXT DEVICE)

'>':
**00:**
**ST:**
**LH LL:**
**CSUM:**

0x3E - Start of the packet.
0x00 - Fixed value '00'.
0x00 - No error (ERROR CODES).
0x00 0x00 - The data length is 0 bytes.
0x3E - Xor of all bytes (3E 00 00 00 00).

10.

0x0B: DELETE BATCH

**DESCRIPTION:**

Use this command to delete the batch. This is emergency operation! In real conditions it should
not be performed, except in some rare and emergency cases! This is why this operation is protected
with password, which needs to be manually entered from the merchant.

**EXT DEVICE:**

3D 00 LH LL 0B <PASSWORD: VAR>

**CARD READER:**

00 ST 00 00

**EXAMPLE:**

(EXT DEVICE -> CARD READER) >>
(CARD READER -> EXT DEVICE) <<

```text
3E 3D 00 00 0A 0B 30 31 32 33 34 33 32 31 30 36
3E 00 00 00 00 3E
```

**CLARIFICATION:**

(EXT DEVICE -> CARD READER)

'>':
**CMD:**
**00:**
**LH LL:**
**SUBCMD:**
**CSUM:**

0x3E - Start of the packet.
0x3D - Borica command.
0x00 - Fixed value '00'.
0x00 0x0A - The data length is 10 bytes.
0x0B - DELETE BATCH subcommand.
0x36 - Xor of all bytes (3E 3D 00 00 ... 32 31 30).


---

(CARD READER -> EXT DEVICE)

'>':
**00:**
**ST:**
**LH LL:**
**CSUM:**

0x3E - Start of the packet.
0x00 - Fixed value '00'.
0x00 - No error (ERROR CODES).
0x00 0x00 - The is no data.
0x3E - Xor of all bytes (3E 00 00 00 00).

11.

0x0C: CLEAR REVERSAL

**DESCRIPTION:**

Use this command to delete a reversal. This is emergency operation! In real conditions it should
not be performed, except in some rare and emergency cases! This is why this operation is protected
with password, which needs to be manually entered from the merchant.

**EXT DEVICE:**

3D 00 LH LL 0C <PASSWORD: VAR>

**CARD READER:**

00 ST 00 00

**EXAMPLE:**

(EXT DEVICE -> CARD READER) >>
(CARD READER -> EXT DEVICE) <<

```text
3E 3D 00 00 0A 0C 30 31 32 33 34 33 32 31 30 31
3E 00 00 00 00 3E
```

**CLARIFICATION:**

(EXT DEVICE -> CARD READER)

'>':
**CMD:**
**00:**
**LH LL:**
**SUBCMD:**
**CSUM:**

0x3E - Start of the packet.
0x3D - Borica command.
0x00 - Fixed value '00'.
0x00 0x0A - The data length is 10 bytes.
0x0C - CLEAR REVERSAL subcommand.
0x31 - Xor of all bytes (3E 3D 00 00 ... 32 31 30).

(CARD READER -> EXT DEVICE)

'>':
**00:**
**ST:**
**LH LL:**
**CSUM:**

0x3E - Start of the packet.
0x00 - Fixed value '00'.
0x00 - No error (ERROR CODES).
0x00 0x00 - The is no data.
0x3E - Xor of all bytes (3E 00 00 00 00).

12.

0x1A: GET PINPAD STATUS

**EXT DEVICE:**

```text
3D 00 00 01 1A
```


---

**CARD READER:**

00 ST 00 02 <REVERSAL> <END DAY>

<REVERSAL>: Shows if there is any transaction, which needs to be reversed:

00: NO REVERSAL
'R': REVERSAL 'R'
'C': HANG TRANSACTION 'C'

<END DAY>: Shows if end of day needs to be performed before any other type of transaction:

00: NO END OF DAY REQUIRED
01: YOU NEED TO PERFORM END OF DAY

**EXAMPLE:**

(EXT DEVICE -> CARD READER) >>
(CARD READER -> EXT DEVICE) <<

```text
3E 3D 00 00 01 1A 18
3E 00 00 00 02 00 00 3C
```

**CLARIFICATION:**

(EXT DEVICE -> CARD READER)

'>':
**CMD:**
**00:**
**LH LL:**
**SUBCMD:**
**CSUM:**

0x3E - Start of the packet.
0x3D - Borica command.
0x00 - Fixed value '00'.
0x00 0x01 - The data length is 1 byte.
0x1A - GET PINPAD STATUS subcommand.
0x18 - Xor of all bytes (3E 3D 00 00 01 1A).

(CARD READER -> EXT DEVICE)

'>':
**00:**
**ST:**
**LH LL:**
<REVERSAL>:
<END DAY>:
**CSUM:**

0x3E - Start of the packet.
0x00 - Fixed value '00'.
0x00 - No error (ERROR CODES).
0x00 0x02 - The data length is 2 bytes.
0x00 - HEX format, No transaction needs to be reversed
0x00 - HEX format, No end of day required
0x3C - Xor of all bytes (3E 00 00 00 02 00 00).

13.

0x1D: GET MENU INFO

**EXT DEVICE:**

```text
3D 00 00 01 1D
```

**CARD READER:**

00 ST 00 7A <DATA: 122 BYTES>

<DATA>:

<SERIAL NUMBER: 10 BYTES>: SERIAL NUMBER OF THE PINPAD
<TERMINAL ID: 8 BYTES>:
TERMINAL ID OF THE PINPAD
<MERCHANT ID: 16 BYTES>: MERCHANT ID OF THE PINPAD


---

SOFTWARE VERSION OF THE PINPAD
COMPILATION DATE OF THE APPLICATION
COMPILATION TIME OF THE APPLICATION
AUTHORIZATION IP
AUTHORIZATION PORT
KEY LOAD IP

<SOFT VER: 4 BYTES>:
<COMP DATE: 16 BYTES>:
<COMP TIME: 10 BYTES>:
<AUTH IP: 16 BYTES>:
<AUTH PORT: 2 BYTES>:
<KEY LOAD IP: 16 BYTES>:
<KEY LOAD PORT: 2 BYTES>: KEY LOAD PORT
<TMS IP: 16 BYTES>:
<TMS PORT: 2 BYTES>:
<AUTH NII HOST: 2 BYTES>:
<KMC NII HOST: 2 BYTES>:
<KEYS STATE: 1 BYTE>:

TMS IP
TMS PORT
AUTH NII HOST
KMC NII HOST
SYSTEM KEYS STATE

0x00: “NO KEYS”
0x01: “SYSTEM KEK ONLY”
0x02: “KEK & MAC OK”
0x03: “MAN KEK ONLY”
0x04: “UNKNOWN KEYS”
0x05: “INTERNAL ERROR”

**EXAMPLE:**

(EXT DEVICE -> CARD READER) >>
(CARD READER -> EXT DEVICE) <<

```text
3E 3D 00 00 01 1D 1F
3E 00 00 00 7B 30 39 32 30 39 30 30 30 30 34 39
33 38 30 30 34 31 38 39 39 39 33 39 30 30 30 30
31 30 30 30 30 30 00 01 01 1C 00 4A 61 6E 20 32
37 20 32 30 32 31 00 00 00 00 00 31 31 3A 35 34
3A 35 30 00 00 31 39 33 2E 34 31 2E 31 39 30 2E
31 37 30 00 00 4E EE 31 39 33 2E 34 31 2E 31 39
30 2E 31 37 30 00 00 4E EE 31 39 33 2E 34 31 2E
31 39 30 2E 31 36 39 00 00 1F 40 03 33 06 21 02
7B
```

**CLARIFICATION:**

(EXT DEVICE -> CARD READER):

'>':
**CMD:**
**00:**
**LH LL:**
**SUBCMD:**
**CSUM:**

0x3E - Start of the packet.
0x3D – Borica command.
0x00 - Fixed value '00'.
0x00 0x01 - The data length is 1 byte.
0x1D - GET MENU INFO subcommand.
0x1F - Xor of all bytes (3E 3D 00 00 01 1D).

(CARD READER -> EXT DEVICE)

'>':
**00:**
**ST:**
**LH LL:**

0x3E - Start of the packet.
0x00 - Fixed value '00'.
0x00 - No error (ERROR CODES).
0x00 0x7B - The data length is 123 bytes.


---

<SERIAL NUMBER: 10 BYTES>:

<TERMINAL ID: 8 BYTES>:

<MERCHANT ID: 16 BYTES>:

<SOFT VER: 4 BYTES>:
<COMP DATE: 16 BYTES>:

<COMP TIME: 10 BYTES>:

<AUTH IP: 16 BYTES>:

<AUTH PORT: 2 BYTES>:
<KEY LOAD IP: 16 BYTES>:

<KEY LOAD PORT: 2 BYTES>:
<TMS IP: 16 BYTES>:

<TMS PORT: 2 BYTES>:
<AUTH NII HOST: 2 BYTES>:
<KMC NII HOST: 2 BYTES>:
<KEYS STATE: 1 BYTE>:
**CSUM:**

' 30 39 32 30 39 30 30 30 30 34' – STRING
format, “0920900004”
‘39   33  38   30  30   34  31   38’  -   STRING   format,
“93800418”
‘39 39 39 33 39 30 30 30 30 31 30 30 30 30 30 00’
- STRING format, “999390000100000”
'01 01 1C 00' – HEX format, version 1.1.28.0
'4A 61 6E 20 32 37 20 32 30 32 31 00 00 00 00 00'
– STRING format, “Jan 27 2021”
‘31 31 3A 35 34 3A 35 30 00 00’ - STRING
format, “11:54:50”
‘31 39 33 2E 34 31 2E 31 39 30 2E 31 37 30 00
00’ - STRING format, “193.41.190.170”
‘4E EE’ - HEX format, Port = 20206
‘31 39 33 2E 34 31 2E 31 39  30 2E 31 37 30 00
00’ - STRING format, “193.41.190.170”
‘4E EE’ - HEX format, Port = 20206
‘31 39 33 2E 34 31 2E 31 39 30 2E 31 36 39 00
00’ - STRING format, “193.41.190.169”.
‘1F 40’ - HEX format, Port = 8000
‘03 33’ - BCD format, ANII = 333
‘06 21’ - BCD format, KNII = 621
0x02 - “KEK & MAC OK”
0x7B - Xor of all bytes (3E 00 00 00 … 33 06 21).

14.

0x1E: GET PUBLIC KEYS LIST

**EXT DEVICE:**

```text
3D 00 00 01 1E
```

**CARD READER:**

00 ST LH LL <DATA: VAR>

<DATA: VAR>: Data in string format. Just print the string.

**EXAMPLE:**

(EXT DEVICE -> CARD READER) >>
(CARD READER -> EXT DEVICE) <<

```text
3E 3D 00 00 01 1E 1C
3E 00 00 02 52 20 31 20 41 30 30 30 30 30 30 30
30 33 20 30 37 20 31 32 32 36 0A 20 32 20 41 30
30 30 30 30 30 30 30 33 20 30 38 20 31 32 32 34
0A 20 33 20 41 30 30 30 30 30 30 30 30 33 20 30
39 20 31 32 32 36 0A 20 34 20 41 30 30 30 30 30
```

..... (too long response) .....

```text
32 37 20 41 30 30 30 30 30 30 34 36 31 20 41 32
20 31 32 32 34 0A 2A
```


---

**CLARIFICATION:**

(EXT DEVICE -> CARD READER):

'>':
**CMD:**
**00:**
**LH LL:**
**SUBCMD:**
**CSUM:**

0x3E - Start of the packet.
0x3D – Borica command.
0x00 - Fixed value '00'.
0x00 0x01 - The data length is 1 byte.
0x1E - GET PUBLIC KEYS LIST subcommand.
0x1C - Xor of all bytes (3E 3D 00 00 01 1E).

(CARD READER -> EXT DEVICE)

'>':
**00:**
**ST:**
**LH LL:**
<DATA: VAR>:
**CSUM:**

0x3E - Start of the packet.
0x00 - Fixed value '00'.
0x00 - No error (ERROR CODES).
0x02 0x52 - The data length is 594 bytes.
‘20 31 20 41 30 …  31 32 32 34 0A’ - Just print the string
0x2A - Xor of all bytes (3E 00 00 00 … 33 06 21).

15.

0x1F: GET SYMMETRIC KEYS LIST

**EXT DEVICE:**

```text
3D 00 00 01 1F
```

**CARD READER:**

00 ST LH LL <DATA: VAR>
<DATA: VAR>: Data in string format. Just print the string.

**EXAMPLE:**

(EXT DEVICE -> CARD READER) >>
(CARD READER -> EXT DEVICE) <<

```text
3E 3D 00 00 01 1F 1D
3E 00 00 00 64 53 59 53 54 45 4D 20 4B 45 4B
3A 20 20 35 37 44 35 45 37 0A 53 59 53 54 45 4D
20 4D 41 43 3A 20 20 45 33 44 42 42 43 0A 4D 41
53 54 45 52 20 50 49 4E 3A 20 20 43 43 31 35 46
34 0A 4D 41 53 54 45 52 20 4D 41 43 3A 20 20 38
33 44 36 44 39 0A 4D 41 53 54 45 52 20 44 41 54
41 3A 20 35 35 42 34 33 46 0A 75
```

**CLARIFICATION:**

(EXT DEVICE -> CARD READER):

'>':
**CMD:**
**00:**
**LH LL:**
**SUBCMD:**
**CSUM:**

0x3E - Start of the packet.
0x3D – Borica command.
0x00 - Fixed value '00'.
0x00 0x01 - The data length is 1 byte.
0x1F - GET SYMMETRIC KEYS LIST subcommand.
0x1D - Xor of all bytes (3E 3D 00 00 01 1F).

(CARD READER -> EXT DEVICE)

'>':
**00:**
**ST:**

0x3E - Start of the packet.
0x00 - Fixed value '00'.
0x00 - No error (ERROR CODES).


---

**LH LL:**
<DATA: VAR>:
**CSUM:**

0x00 0x64 - The data length is 100 bytes.
‘53 59 53 54 45 …  42 34 33 46 0A’ - Just print the string
0x75 - Xor of all bytes (3E 00 00 00 … 33 46 0A).

16.

0x20: EDIT COMMUNICATION PARAMETERS

**DESCRIPTION:**

Use this command to manually update one of the communication parameters, listed below. The

password has to be manually entered from the user! It is not hardcoded parameter of the command.

**EXT DEVICE:**

3D 00 LH LL 20 <DATA: VAR>

<DATA: VAR>: Data in TLV format.

**DF8003:**

(Mandatory tag!) This is the password, which has to be manually entered

**DF51:**
**DF52:**
**DF7B:**
**DF7C:**
**DF65:**
**DF66:**

from the user.

(Optional) Host IP
(Optional) Host port
(Optional) Key load IP
(Optional) Key load port
(Optional) TMS IP
(Optional) TMS port

**CARD READER:**

00 ST 00 00

**EXAMPLE:**

(EXT DEVICE -> CARD READER) >>

(CARD READER -> EXT DEVICE) <<

**CLARIFICATION:**

(EXT DEVICE -> CARD READER):

```text
3E 3D 00 00 3A 20 DF 80 03 09 30 31 32 33 34 33
32 31 30 DF 51 0E 31 39 33 2E 34 31 2E 31 39 30
2E 31 37 30 DF 52 02 4E EE DF 7B 0E 31 39 33
2E 34 31 2E 31 39 30 2E 31 37 30 DF 7C 02 4E
EE 7C
3E 00 00 00 00 3E
```

'>':
**CMD:**
**00:**
**LH LL:**
**SUBCMD:**
<DATA: VAR>:
**CSUM:**

0x3E - Start of the packet.
0x3D – Borica command.
0x00 - Fixed value '00'.
0x00 0x3A - The data length is 58 bytes.
0x20 - EDIT COMM PARAMETERS subcommand.
‘DF 80 03 … 02 4E EE’ - Data in TLV format.
0x7C - Xor of all bytes (3E 3D 00 00 01 1F).

(CARD READER -> EXT DEVICE)

'>':
**00:**
**ST:**

0x3E - Start of the packet.
0x00 - Fixed value '00'.
0x00 - No error (ERROR CODES).


---

**LH LL:**
**CSUM:**

0x00 0x00 - The data length is 0 bytes.
0x3E - Xor of all bytes (3E 00 00 00 00).

17.

0x21: KEYS COMMAND

**DESCRIPTION:**

This command performs few operations with the keys – either Init, Uptade or Decommission.
These  3  operations  can  be  performed  either  with  HSM, connected  via  USB cable  or with  remote
connection to the KMC.

After this command is executed successfully, the card reader will start the requested operation.
In case of 0x01 (Init keys), 0x03 (Update keys) and 0x05 (Decommission keys), the card reader will
send data directly to the HSM, so it is expected that there will be an USB connection and this data will
just be redirected through the USB. In case of 0x02 (Init keys remote), 0x04 (Update keys remote) and
0x06   (Decommission   keys   remote),   the   card   reader   will   send   the   data   to   the   remote   KMC.   The
communication in this case will be very similar to a normal transaction – first the card reader will send
event for opening a socket to the host, then it will send an event for sending data to the host and etc.

**EXT DEVICE:**

3D 00 00 02 21 <OPERATION TYPE: 1 BYTE>

<OPERATION TYPE: 1 BYTE> Specify the operation type

0x01:
0x02:
0x03:
0x04:
0x05:
0x06:

INIT KEYS
INIT KEYS REMOTE
UPDATE KEYS
UPDATE KEYS REMOTE
DECOMMISSION KEYS
DECOMMISSION KEYS REMOTE

**CARD READER:**

00 ST 00 00

**EXAMPLE:**

(EXT DEVICE -> CARD READER) >>
(CARD READER -> EXT DEVICE) <<

```text
3E 3D 00 00 02 21 01 21
3E 00 00 00 00 3E
```

**CLARIFICATION:**

(EXT DEVICE -> CARD READER):

'>':
**CMD:**
**00:**
**LH LL:**
**SUBCMD:**
<DATA: VAR>:
**CSUM:**

0x3E - Start of the packet.
0x3D – Borica command.
0x00 - Fixed value '00'.
0x00 0x02 - The data length is 2 bytes.
0x20 - KEYS COMMAND subcommand.
0x01 – Start INIT KEYS operation
0x21 - Xor of all bytes (3E 3D 00 00 02 21 01).


---

(CARD READER -> EXT DEVICE)

'>':
**00:**
**ST:**
**LH LL:**
**CSUM:**

0x3E - Start of the packet.
0x00 - Fixed value '00'.
0x00 - No error (ERROR CODES).
0x00 0x00 - The data length is 0 bytes.
0x3E - Xor of all bytes (3E 00 00 00 00).

18.

0x23: CHECK PASSWORD

**DESCRIPTION:**

Check if the password is correct.

**EXT DEVICE:**

3D 00 LH LL 23 [PASSWORD TYPE: 1 BYTE] <PASSWORD: VAR>

[PASSWORD TYPE: 1 BYTE]

0x01 – Merchant password
0x02 – Bank passwords
0x03 – Custom password 1
0x04 – Custom password 2
0x05 – Custom password 3
0x06 – Internal password

**CARD READER:**

00 ST 00 00

**EXAMPLE:**

(EXT DEVICE -> CARD READER) >>
(CARD READER -> EXT DEVICE) <<

```text
3E 3D 00 00 06 23 01 31 30 30 30 26
3E 00 15 00 00 2B
```

**CLARIFICATION:**

(EXT DEVICE -> CARD READER):

'>':
**CMD:**
**00:**
**LH LL:**
**SUBCMD:**
[PASSWORD TYPE]
<PASSWORD: VAR>
**CSUM:**

0x3E - Start of the packet.
0x3D – Borica command.
0x00 - Fixed value '00'.
0x00 0x06 - The data length is 6 bytes.
0x23 – CHECK PASSWORD subcommand.
0x01 – Check Merchant password.
‘31 30 30 30’ - String format, “1000”.
0x26 - Xor of all bytes (3E 3D 00 … 30 30 30).

(CARD READER -> EXT DEVICE)

'>':
**00:**
**ST:**
**LH LL:**
**CSUM:**

0x3E - Start of the packet.
0x00 - Fixed value '00'.
0x15 - errInvPass (ERROR CODES) – Wrong password.
0x00 0x00 - The data length is 0 bytes.
0x2B - Xor of all bytes (3E 00 15 00 00).


---

19.

0x24: GET REPORT TAGS BY STAN

This command is being used in case that it is needed a information for some specific transaction to be
taken. To specify the transaction, its STAN (transaction number) needs to be used.

**EXT DEVICE:**

3D 00 LH LL 24 <STAN: 4> <TAGS: VAR>

<STAN>

The STAN of the record as a big endian integer.

<TAGS>

Tags to be returned (For reference see "TLV STRUCTURE" and "TAGS"
sections below).

**CARD READER:**

00 ST LH LL <DATA: VAR>

**EXAMPLE:**

Let's say, for example, a transaction has been made and it has STAN (number of the transaction)
= 326. Then we would like to get the following information for this specific transaction: transaction
result, payment interface, contactless card scheme and the amount of the transaction. From the table
below (TAGS), we can see, that we need to get tags 0xDF05, 0xDF25, 0xDF60 and 0x81. So in this
case we need to send the following command:

(EXT DEVICE -> CARD READER) >>

(CARD READER -> EXT DEVICE) <<

```text
3E 3D 00 00 0C 24 00 00 01 46 DF 05 DF 25 DF
60 81 72
3E 00 00 00 19 DF 05 04 00 00 00 00 DF 25 02 00
01 DF 60 04 00 00 00 03 81 04 00 00 00 64 59
```

**CLARIFICATION:**

(EXT DEVICE -> CARD READER):

'>':
**CMD:**
**00:**
**LH LL:**
**SUBCMD:**
<STAN: 4>:

<TAGS: VAR>:

0x3E - Start of the packet.
0x3D - BORICA CMD command.
0x00 - Fixed value '00'.
0x00 0x0C - The data length is 12 bytes.
0x24 - GET REPORT TAGS BY STAN subcommand.
'00 00 01 46' - HEX format (BIG ENDIAN), STAN = 326

'DF 05 DF 25 DF 60 81' - HEX format, here we need to list all
tags, which we need to get for transaction with STAN = 326. In
this case we want to get tags 0xDF05, 0xDF25, 0xDF60 and 0x81

**CSUM:**

0x72 - Xor of all bytes (3E 3D 00 ..... 60 81).

(CARD READER -> EXT DEVICE):

'>':
**00:**
**ST:**
**LH LL:**

0x3E - Start of the packet.
0x00 - Fixed value '00'.
0x00 - No error (ERROR CODES).
0x00 0x19 - The data length is 25 bytes.


---

<DATA: VAR>:

'DF 05 04 00 00 00 00 DF 25 02 00 01 DF 60 04 00 00 00 03 81
04 00 00 00 64' - HEX format, this is the information, which is
returned   for   transaction   with   STAN   =   326.   It   contains   listed
multiple elements, composed of <TAG, LEN, VALUE>. 'DF 05
(TAG) 04 (LEN) 00 00 00 00 (VALUE)' - Transaction result tag
has value 0, which means the transaction was successful. 'DF 25
(TAG) 02 (LEN) 00 01 (VALUE)' - Payment interface has value
1. From the reference below, we can see, that this transaction was
made with contactless interface. 'DF 60 (TAG) 04 (LEN) 00 00 00
03 (VALUE)' - Contactless card cheme has value 3. From the
reference below, we can see, that this transaction was made with
Visa Contactless card. '81 (TAG) 04 (LEN) 00 00 00 64 (VALUE)
- The amount of this transaction is 100 (1.00).

**CSUM:**

0x59 - Xor of all bytes (3E 00 00 ..... 00 64).

Note: If some of the tags, listed in the command (EXT DEVICE -> CARD READER) is
missing for this transaction, it will be missing in the response. If all of the tags are
missing for this transaction, the response will contain ST field with value errNoData (8)
error.

20.

0x25: SELECT CHIP APPLICATION

**DESCRIPTION:**

This   command   needs   to   be   used   only   after   receiving   the   event   “0x3F:   SELECT   CHIP
APPLICATION”. With this command the EXT DEVICE selects a chip application, where the index is
selected by the user (indexes start from ‘00’ for the first application in the TLV format data from the
event).

**EXT DEVICE:**

3D 00 LH LL 25 [CHIP APPLICATION INDEX: 1 BYTE]

**CARD READER:**

00 ST 00 00

**EXAMPLE:**

(EXT DEVICE -> CARD READER) >>
(CARD READER -> EXT DEVICE) <<

```text
3E 3D 00 00 02 25 00 24
3E 00 00 00 00 3E
```

**CLARIFICATION:**

(EXT DEVICE -> CARD READER):

'>':
**CMD:**
**00:**
**LH LL:**
**SUBCMD:**
[PASSWORD TYPE]
**CSUM:**

0x3E - Start of the packet.
0x3D – Borica command.
0x00 - Fixed value '00'.
0x00 0x02 - The data length is 2 bytes.
0x25 – SELECT CHIP APPLICATION subcommand.
0x00 – Select chip app with index = 0 (the first one).
0x24 - Xor of all bytes (3E 3D 00 00 02 25 00).


---

(CARD READER -> EXT DEVICE)

'>':
**00:**
**ST:**
**LH LL:**
**CSUM:**

0x3E - Start of the packet.
0x00 - Fixed value '00'.
0x00 - errNoErr (ERROR CODES)
0x00 0x00 - The data length is 0 bytes.
0x3E - Xor of all bytes (3E 00 00 00 00).

21.

0x26: GET CARD READER STATE

**EXT DEVICE:**

3D 00 LH LL 26

**CARD READER:**

00 ST 00 01 [CARD READER STATE: 1 BYTE]

[CARD READER STATE: 1 BYTE]

0x01 – Idle mode
0x02 – Transaction is started
0x03 – Select application
0x04 – PIN entry
0x05 – Online authorization

**EXAMPLE:**

(EXT DEVICE -> CARD READER) >>
(CARD READER -> EXT DEVICE) <<

```text
3E 3D 00 00 01 26 24
3E 00 00 00 01 01 3E
```

**CLARIFICATION:**

(EXT DEVICE -> CARD READER):

'>':
**CMD:**
**00:**
**LH LL:**
**SUBCMD:**
**CSUM:**

0x3E - Start of the packet.
0x3D – Borica command.
0x00 - Fixed value '00'.
0x00 0x01 - The data length is 1 byte.
0x26 – GET CARD READER STATE subcommand.
0x24 - Xor of all bytes (3E 3D 00 00 01 26).

(CARD READER -> EXT DEVICE)

0x3E - Start of the packet.
'>':
0x00 - Fixed value '00'.
**00:**
0x00 - errNoErr (ERROR CODES)
**ST:**
0x00 0x01 - The data length is 1 byte.
**LH LL:**
[CARD READER STATE]: 0x01 – Card reader is in IDLE mode.
**CSUM:**

0x3E - Xor of all bytes (3E 00 00 00 01 01).


---

22.

0x27: GET TERMINAL TAGS

**DESCRIPTION:**

Usually in order to get some information using the command “0x04: GET REPORT TAGS” the
card reader needs to currently have Sale transactions in the log. If there are no transactions, no result
will be returned. For this reason we introduced command “0x27: GET TERMINAL TAGS”, which will
return   few   Terminal-related   tags   (Not   Transaction-related)   even   if   currently   there   are   no   Sale
transactions   in   the   log.   This   kind   of   important   information   are   for   example   tags   0x9F1C
(TERMINAL_ID),   0x9F1E   (TERMINAL_SERIAL_NUMBER),   0xDF32   (BATCH_NUMBER)   and
many more.

**EXT DEVICE:**

3D 00 LH LL 27 <TAGS: VAR>

<TAGS: VAR>:

Tags to be returned. (For reference see "TLV STRUCTURE" and "TAGS" sections
below).

**CARD READER:**

00 ST LH LL <DATA: VAR>

<DATA: VAR>:

Returned tags data

**EXAMPLE:**

(EXT DEVICE -> CARD READER) >>
(CARD READER -> EXT DEVICE) <<

```text
3E 3D 00 00 05 27 9F 1E DF 32 4D
3E 00 00 00 12 9F 1E 0A 31 39 30 31 39 30 30 30
31 31 DF 32 02 00 64 2C
```

**CLARIFICATION:**

(EXT DEVICE -> CARD READER):

'>':
**CMD:**
**00:**
**LH LL:**
**SUBCMD:**
<TAGS: VAR>

**CSUM:**

0x3E - Start of the packet.
0x3D – Borica command.
0x00 - Fixed value '00'.
0x00 0x05 - The data length is 5 bytes.
0x27 – GET TERMINAL TAGS subcommand.
‘9F 1E DF 32’ - Here we need to list all tags, which we
would like to get. In this case we need to get 2 tags –
0x9F1E and 0xDF32.
0x4D - Xor of all bytes (3E 3D 00 ..... DF 32).

(CARD READER -> EXT DEVICE)

'>':
**00:**
**ST:**
**LH LL:**

0x3E - Start of the packet.
0x00 - Fixed value '00'.
0x00 - No error (ERROR CODES).
0x00 0x12 - The data length is 18 bytes.


---

<DATA: VAR>:

**CSUM:**

'9F 1E 0A 31 39 30 31 39 30 30 30 31 31 DF 32 02 00 64' – Tag
0x9F1E   (Serial   number)   has   value   “1901900011”   and   DF32
(Batch number) has value 100.
0x2C - Xor of all bytes (3E 00 00 ..... 00 64).

# 3. 0x40: External internet subcommands

External   internet   command   contains   multiple   subcommands,   which   are   associated   mainly   with
handling the communication with the host. If the card reader does not use its own WIFI or GSM
capability for communicating with the host, then the card reader will use the external device for this
communication.  The  external  device  needs  to  implement  mainly  4 different  activities  –  opening  a
socket, closing a socket, sending data to the host and receiving response from the host and forwarding
the response to the card reader. In order for this functionality to be working correctly, “External internet
command” and “External internet event” need to be implemented and handled correctly.

## 1. 0x01: RECEIVE DATA

**DESCRIPTION:**

This command is being used when the external device receives some data from the host. Using

this command, the EXT DEVICE sends the received data to the CARD READER.

**EXT DEVICE:**

40 00 LH LL [SUBCMD] <DATA: VAR>

<DATA>: The data, which is received from the host.

**CARD READER:**

00 ST 00 00

**EXAMPLE:**

(EXT DEVICE -> CARD READER) >>

```text
3E 40 00 00 3C 01 14 03 01 00 01 01 16 03 01 00
30 17 D3 84 B3 F7 DF 99 20 A6 DF E2 59 6D 99
3B 5C 05 15 D7 D9 51 A6 69 79 D9 37 5C 40 92
86 67 3B 19 70 0D B3 69 24 CF B7 7F E6 E9 35
34 7A A1 E9 A0
```

(CARD READER -> EXT DEVICE) <<

```text
3E 00 00 00 00 3E
```

**CLARIFICATION:**

(EXT DEVICE -> CARD READER):

'>':
**CMD:**
**00:**
**LH LL:**
**SUBCMD:**

0x3E - Start packet.
0x40 - EXTERNAL INTERNET command.
0x00 - Fixed value '00'.
0x00 0x3C - The data length is 60 bytes.
0x01 - RECEIVE DATA subcommand.


---

<DATA: VAR>:

'14 03 01 00 ..... 34 7A A1 E9' - This is data, which was received
from the host. The  EXT DEVICE  doesn't  need to understand
these bytes, it must just send them to the CARD READER.

**CSUM:**

0xA0 - Xor of all bytes (3E 40 00 ..... A1 E9).

(CARD READER -> EXT DEVICE):

'>':
**00:**
**ST:**
**LH LL:**
**CSUM:**

0x3E - Start packet.
0x00 - Fixed value '00'.
0x00 - No error (ERROR CODES).
0x00 0x00 - The data length is 0 bytes.
0x3E - Xor of all bytes (3E 00 00 00 00).

Note: When sending the response from the host to the CARD READER, the EXT DEVICE needs to
analyze the MTU value, which is currently used. By default the MTU is 0x0400 (1024 bytes). This
means that if the length of the response from the host is bigger than the MTU, then the EXT DEVICE
needs  to   "cut"  the   response  to  a  smaller   packets  and   send  each  of  them  separately to   the  CARD
READER. So if the host returns 3000 bytes, then the EXT DEVICE needs to call the "0x01: RECEIVE
DATA" subcommand 3 times – the first 2 calls should have parameter "LH LL" with value = '04 01' (1
byte "SUBCMD" + 0x400 bytes "<DATA: VAR>") and the 3rd call should have parameter "LH LL"
with value = '03 B9' (1 byte "SUBCMD" + 0x3B8 bytes "<DATA: VAR>").

Note 2:  When   sending   the   "0x01:   RECEIVE   DATA"   subcommand,   the   EXT  DEVICE   needs   to
analyze the ST field from the response, which is returned from the CARD READER!!! If the CARD
READER returns field ST with value 0x26 (38 = errBusy), then the EXT DEVICE needs to wait 100
milliseconds and send the same data again, 2nd time! And this loop needs to continue while the CARD
READER returns field ST with value = 0x26. If the CARD READER returns field ST with value 0x00
(errNoErr), then the CARD READER successfully received the data and it is ready to receive the next
data, if there is any.

## 2. 0x02: EVENT CONFIRM

**DESCRIPTION:**

This   command   confirms   to   the   CARD   READER   whether   the   EXT   DEVICE   successfully
performed   an   action,   which   before   that   was   issued  from   the   CARD   READER   with   any   of   the
corresponding events (for example open socket).

**EXT DEVICE:**

40 00 LH LL [SUBCMD] [TYPE] [RESULT] <MTU EXT DEVICE: 2>

[TYPE]:

[01]: SOCKET OPEN EVENT –  Needs   to   be   sent   only   if   the   CARD   READER

before  that sent the “01: SOCKET OPEN” event.

[02]: SOCKET CLOSE EVENT –  Needs   to   be   sent   only   if   the   CARD   READER
before  that sent the “02: SOCKET CLOSE” event.


---

[03]: SEND DATA EVENT –

Needs   to   be   sent   only   if   the   CARD   READER
before  that sent the “03: SEND DATA” event.

[RESULT]:

[00]: CONFIRM OK
[01]: CONFIMR FAIL

<MTU EXT DEVICE>:

[MTU HIGH][MTU LOW]:  Maximum transmit unit of the external device. By default

it is 0x0400 (1024 bytes).

**CARD READER:**

00 ST LH LL

**EXAMPLE:**

(EXT DEVICE -> CARD READER) >>
(CARD READER -> EXT DEVICE) <<

```text
3E 40 00 00 03 02 02 00 7D
3E 00 00 00 00 3E
```

**CLARIFICATION:**

(EXT DEVICE -> CARD READER):

'>':
**CMD:**
**00:**
**LH LL:**
**SUBCMD:**
[TYPE]:
[RESULT]:
<MTU EXT DEVICE: 2>: Not present in this example.
**CSUM:**

0x3E - Start packet.
0x40 - EXTERNAL INTERNET command.
0x00 - Fixed value '00'.
0x00 0x03 - The data length is 3 bytes.
0x02 - EVENT CONFIRM subcommand.
0x02 - SOCKET CLOSE EVENT
0x00 - CONFIRM OK

0x7D - Xor of all bytes (3E 40 00 ..... 02 00).

(CARD READER -> EXT DEVICE):

'>':
**00:**
**ST:**
**LH LL:**
**CSUM:**

0x3E - Start packet.
0x00 - Fixed value '00'.
0x00 - No error (ERROR CODES).
0x00 0x00 - The data length is 0 bytes.
0x3E - Xor of all bytes (3E 00 00 00 00).

## 3. 0x03: GET MAX MTU

**EXT DEVICE:**

40 00 LH LL [SUBCMD]

**CARD READER:**

00 ST LH LL <MTU PINPAD: 2>

<MTU PINPAD>:

[MTU HIGH][MTU LOW]: Maximum transmit unit of the CARD READER. The card

reader only reports its max MTU (how much bytes


---

maximum can be transferred at once between EXT
DEVICE and the CARD READER using the
subcommand “0x01: RECEIVE DATA”).

**EXAMPLE:**

(EXT DEVICE -> CARD READER) >>
(CARD READER -> EXT DEVICE) <<

```text
3E 40 00 00 01 03 7C
3E 00 00 00 02 04 00 38
```

**CLARIFICATION:**

(EXT DEVICE -> CARD READER):

'>':
**CMD:**
**00:**
**LH LL:**
**SUBCMD:**
**CSUM:**

0x3E - Start packet.
0x40 - EXTERNAL INTERNET command.
0x00 - Fixed value '00'.
0x00 0x01 - The data length is 1 byte.
0x03 - GET MAX MTU subcommand.
0x7C - Xor of all bytes (3E 40 00 ..... 01 03).

(CARD READER -> EXT DEVICE):

'>':
**00:**
**ST:**
**LH LL:**
<MTU PINPAD: 2>: 0x04 0x00 - MAX MTU is 0x400 bytes.
**CSUM:**

0x3E - Start packet.
0x00 - Fixed value '00'.
0x00 - No error (ERROR CODES).
0x00 0x02 - The data length is 2 bytes.

0x38 - Xor of all bytes (3E 00 00 ..... 04 00).

# 4. 0x0E: Borica subevents

At some point different events can be received from the CARD READER. The Borica
event  has value 0x0E  and the different Borica subevents are mostly connected with
information for the transaction, which is currently performed, or a transaction, which
was already performed in the past.

## 1. 0x01: TRANSACTION COMPLETE (PAYMENT RESULT) - NO

CONFIRMATION NEEDED

**CARD READER:**

0E 00 LH LL 01 <DATA: VAR>

<DATA>:

Tags, encoded in TLV format:

BOR_TAG_PAY_RES
BOR_TAG_PAY_ERR
BOR_TAG_HOST_RRN
BOR_TAG_HOST_AUTH_ID
TAG_81_AMOUNT_AUTHORISED_BINARY

0xDF05 - [HEX BIG ENDIAN]
0xDF06 - [HEX BIG ENDIAN]
0xDF07 - [STRING]
0xDF08 - [STRING]
0x0081 - [HEX BIG ENDIAN]


---

BOR_TAG_EMV_STAN
BOR_TAG_MAX_CASHBACK_AMOUNT
BOR_TAG_CASHBACK_CURRENCY
BOR_TAG_BCARD_SCA_DECLINED

0x9F41 - [BCD]
0xDF8004 - [HEX BIG ENDIAN]
0xDF8005 - [STRING]
0xDF8006 - [HEX BIG ENDIAN]

**EXAMPLE:**

(CARD READER -> EXT DEVICE) >>

**CLARIFICATION:**

(CARD READER -> EXT DEVICE):

```text
3E 0E 00 00 1C 01 DF 05 04 00 00 00 00 DF 06
04 00 00 00 00 81 04 00 00 00 00 9F 41 04 00 00
03 67 15
```

'>':
**EVENT:**
**00:**
**LH LL:**
**SUBEVENT:**

<DATA: VAR>:

0x3E - Start of the packet.
0x0E - Borica event.
0x00 - Fixed value '00'.
0x00 0x1C - The data length is 28 bytes.
0x01 - TRANSACTION COMPLETE subevent.

'DF 05 04 00 00 00 00 DF 06 04 00 00 00 00 81 04 00 00
00 00 9F 41 04 00 00 03 67' - The Result (Tag 0xDF05) is
0 (Success), the Error (Tag 0xDF06) is 0 (No Error), The
Amount (Tag 0x81) is 0 and the transaction number (Tag
0x9F41) is 367.

**CSUM:**

0x15 - Xor of all bytes (3E 0F 00 ..... 4E EE).

## 2. 0x02: INTERMEDIATE TRANSACTION COMPLETE (PAYMENT

RESULT) - NO CONFIRMATION NEEDED

Sent if a hung transaction passed just before the transaction, which is currently being executed.

**CARD READER:**

0E 00 LH LL 02 <DATA: VAR>

<DATA>:

 Tags, encoded in TLV format:

BOR_TAG_PAY_RES
BOR_TAG_PAY_ERR
BOR_TAG_HOST_RRN
BOR_TAG_HOST_AUTH_ID
TAG_81_AMOUNT_AUTHORISED_BINARY
BOR_TAG_EMV_STAN

0xDF05 - [HEX BIG ENDIAN]
0xDF06 - [HEX BIG ENDIAN]
0xDF07 - [STRING]
0xDF08 - [STRING]

0x0081 - [HEX BIG ENDIAN]

0x9F41 – [BCD]


---

## 3. 0x03: PRINT HANG TRANSACTION RECEIPT

**DESCRIPTION:**

If this Event is received, a receipt for a Hang transaction should be force printed, containing all

required information, which is included in the Event.

**CARD READER:**

0E 00 LH LL 03 <DATA: VAR>

<DATA>:

Needed tags for constructing a receipt (See 7. TAGS).

**EXAMPLE:**

(CARD READER -> EXT DEVICE) >>

```text
3E 0E 00 01 EC 03 9F 1C 08 39 33 38 30 30 34 37
35 9F 16 0F 39 39 39 33 39 30 30 30 30 31 30 30
30 30 30 5F 2A 02 09 75 DF 26 02 0A 02 DF 27
03 42 47 4E DF 28 07 39 37 30 32 36 31 30
```

..... (too long data) .....

```text
81 04 00 00 00 05 9F 41 04 00 00 17 79 DF 07 0C
32 31 39 39 30 36 37 35 37 33 37 35 DF 08 06 30
35 31 32 39 36 3F
```

**CLARIFICATION:**

(CARD READER -> EXT DEVICE):

'>':
**EVENT:**
**00:**
**LH LL:**
**SUBEVENT:**

<DATA: VAR>:

0x3E - Start of the packet.
0x0E - Borica event.
0x00 - Fixed value '00'.
0x01 0xEC - The data length is 492 bytes.
0x03 - PRINT HANG TRANSACTION RECEIPT
subevent.

' 9F 1C 08 39 33 38 30 30 34 37 ... 31 32 39 36 35' – Data
in TLV format (See 7. TAGS). This information should be
used for constructing and printing a receipt.

**CSUM:**

0x3F - Xor of all bytes (3E 0E 00 ..... 39 36).

## 4. 0x10: SEND LOG DATA

Sent as a result of subcommand "0x04: GET REPORT TAGS" with parameter "00 10 -
GET ALL RECORDS AS EVENTS". Every record is sent as a single event.

**CARD READER:**

0E 00 LH LL 10 <DATA: VAR>


---

## 5. 0x3F: SELECT CHIP APPLICATION

**DESCRIPTION:**

This event will be sent only from BlueCash50 device! This event will be sent only if transaction
is performed with chip card, which supports more than one chip applications. This event contains the
names of the applications, which are supported from the card, they need to be displayed in a menu and
after the selection, the EXT DEVICE needs to send command "0x25: SELECT CHIP APPLICATION"
in order to confirm which is the selected application by the user.

**CARD READER:**

0E 00 LH LL 3F <DATA: VAR>

<DATA>:

The names of the applications, encoded in TLV structure

BOR_TAG_CHIP_APPLICATION_NAME

0xDFC101 - [STRING]

**EXAMPLE:**

(CARD READER -> EXT DEVICE) >>

**CLARIFICATION:**

(CARD READER -> EXT DEVICE):

```text
3E 0E 00 00 21 3F DF C1 01 0C 43 6F 6D 62 6F
30 31 20 76 31 20 31 DF C1 01 0C 43 6F 6D 62
6F 30 31 20 76 31 20 31 2E
```

'>':
**EVENT:**
**00:**
**LH LL:**
**SUBEVENT:**

<DATA: VAR>:

0x3E - Start of the packet.
0x0E - Borica event.
0x00 - Fixed value '00'.
0x00 0x21 - The data length is 33 bytes.
0x3F - SELECT CHIP APPLICATION subevent.

'DF C1 01 0C 43 6F 6D 62 6F 30 31 20 76 31 20 31 DF
C1 01 0C 43 6F 6D 62 6F 30 31 20 76 31 20 31' – TLV
format   –   Each   tag   0xDFC101   contains   the   name   of   a
specific   application.  They  need   to   be   displayed   in   the
same order and they have indexes starting from ‘00’ for
the first application.

# 5. 0x0F: External internet subevents

At some point different events can be received from the CARD READER. The External
internet event has value 0x0F and the different External internet subevents are mostly
connected with the communication with the host – opening/closing a socket or sending
data to the host.


---

## 1. 0x01: SOCKET OPEN

**DESCRIPTION:**

When the EXT DEVICE receives this subevent, it must open socket to <ADDRESS>:<PORT>
with <TIMEOUT> and if it is using APN SIM card, it needs to use the APN, Username and Password
(From the tags below) for the SIM card. Then the EXT DEVICE needs to send the subcommand
"2. 0x02: EVENT CONFIRM".

**CARD READER:**

0F   00   LH   LL  [SUBEVENT]   [ID]   [TYPE]   <ADDRESS:   4>   <PORT:   2>   <TIMEOUT:   2>

<DATA: VAR>

[ID]:

[0..255]: SOCKET ID

[TYPE]:

[01]: TCP
[02]: UDP
[03]: TCP TLS
[04]: UDP TLS

<ADDRESS>:

[0..255][0..255][0..255][0..255] : SOCKET ADDRESS

<PORT>:

[PORT HIGH][PORT LOW] : SOCKET PORT

<TIMEOUT>:

[TIMEOUT HIGH][TIMEOUT LOW] : TIMEOUT IN SECONDS

<DATA>:

TAGS ENCODED IN TLV FORMAT (For reference see "TLV STRUCTURE" section

below):

BOR_TAG_COMM_APN
BOR_TAG_COMM_GPRS_UN
BOR_TAG_COMM_GPRS_PWD
BOR_TAG_HOST_LAN_IP
BOR_TAG_HOST_LAN_PORT

0xDF50 - [STRING]
0xDF53 - [STRING]
0xDF54 - [STRING]
0xDF6C - [STRING]
0xDF6D - [HEX]

**EXAMPLE:**

(CARD READER -> EXT DEVICE) >>

**CLARIFICATION:**

( CARD READER -> EXT DEVICE):

```text
3E 0F 00 00 26 01 01 01 55 FF 80 C4 4E ED 00
1E DF 50 06 62 6F 72 69 63 61 DF 53 00 DF 54
00 DF 6C 04 58 CB EF 2E DF 6D 02 4E EE 2A
```

'>':
**EVENT:**
**00:**
**LH LL:**
**SUBEVENT:**
[ID]:
[TYPE]:
<ADDRESS: 4>:

0x3E - Start packet.
0x0F - EXTERNAL INTERNET event.
0x00 - Fixed value '00'.
0x00 0x26 - The data length is 38 bytes.
0x01 - SOCKET OPEN subevent.
0x01 - Socket ID
0x01 - TCP
0x55 0xFF 0x80 0xC4 - 85.255.128.196


---

<PORT: 2>:
<TIMEOUT: 2>:

0x4E 0xED - 20205
0x00 0x1E – 30

<DATA: VAR>:

'DF 50 06 62 6F 72 69 63 61 DF 53 00 DF 54 00 DF 6C 04 58
CB EF 2E DF 6D 02 4E EE' - The APN (Tag 0xDF50) is
"borica", the Username (Tag 0xDF53) is "" (none) and the
Password (Tag 0xDF54) is also "". The other tags don't need to be
used.

**CSUM:**

0x2A - Xor of all bytes (3E 0F 00 ..... 4E EE).

## 2. 0x02: SOCKET CLOSE

**DESCRIPTION:**

When the EXT DEVICE receives this subevent, it must close the socket with [ID], which was
opened before. Then the EXT DEVICE needs to send the subcommand "2. 0x02: EVENT CONFIRM".

**CARD READER:**

0F 00 LH LL [SUBEVENT] [ID]

[ID]:

[0..255]: SOCKET ID

**EXAMPLE:**

(CARD READER -> EXT DEVICE) >>

```text
3E 0F 00 00 02 02 01 30
```

**CLARIFICATION:**

(CARD READER -> EXT DEVICE):

'>':
**EVENT:**
**00:**
**LH LL:**
**SUBEVENT:**
[ID]:
**CSUM:**

0x3E - Start packet.
0x0F - EXTERNAL INTERNET event.
0x00 - Fixed value '00'.
0x00 0x02 - The data length is 2 bytes.
0x02 - SOCKET CLOSE subevent.
0x01 - ID of the socket = 1.
0x30 - Xor of all bytes (3E 0F 00 ..... 02 01).

## 3. 0x03: SEND DATA

**DESCRIPTION:**

When the EXT DEVICE receives this subevent, it needs to transmit the <DATA> to the host.

Then the EXT DEVICE needs to send the subcommand "2. 0x02: EVENT CONFIRM".

**CARD READER:**

0F 00 LH LL [SUBEVENT] [ID] <DATA: VAR>
[ID]:

[0..255]: SOCKET ID

<DATA>:

DATA TO SEND TO THE SOCKET


---

**EXAMPLE:**

(CARD READER -> EXT DEVICE) >>

```text
3E 0F 00 00 37 03 01 16 03 01 00 30 A9 1C C0 83
3E 74 95 D5 84 3B BE 6E D2 06 DE B2 B4 65 1E
75 CE 43 60 DC 6E 26 45 EE C7 B1 7C 2D 1E A1
E3 ED 9B A1 7F 18 BD 30 24 30 9F C1 75 72 68
```

**CLARIFICATION:**

(CARD READER -> EXT DEVICE):

'>':
**EVENT:**
**00:**
**LH LL:**
**SUBEVENT:**
[ID]:

0x3E - Start packet.
0x0F - EXTERNAL INTERNET event.
0x00 - Fixed value '00'.
0x00 0x37 - The data length is 55 bytes.
0x03 - SEND DATA subevent.
0x01 - ID of the socket is 1.

<DATA: VAR>:

'16 03 01 00 ..... C1 75 72' - The EXT DEVICE doesn't need to
understand these bytes, it must just send them to the host.

**CSUM:**

0x68 - Xor of all bytes (3E 0F 00 ..... 75 72).

# 6. ERROR CODES

errNoErr
errGeneral
errInvCmd
errInvPar
errInvAdr
errInvVal
errInvLen
errNoPermit
errNoData
errTimeOut
errKeyNum
errKeyAttr
errKeyUsage
errInvDevice
errNoSupport
errPinLimit
errFlash
errHard
errInvCRC
errCancel
errInvSign
errInvHead
errInvPass
errKeyFormat

0
1
2
3
4
5
6
7
8
9
```text
10
11
11
12
13
14
15
16
17
18
19
20
21
22
```

no error
some error
no valid command or subcommand code
invalid paremeter
address is outside limits
value is outside limits
length is outside limiuts
the action is not permit in current state
there is no data to be returned
timeout is occur
invalid key number
invalid key attributes(ussage)
invalid key attributes(ussage)
calling of non-existing device
(no used in this FW version)
Pin entering limit exceed
some error in flash commands
some hardware error
(no used in this FW version)
the button "CANCEL" is pressed
invalid signature
invalid data in header
incorrent password
invalid key format


---

errSCR
errHAL
errInvKey
errNoPinData
errInvRemainder
errNoInit
errLimit
errInvSeq
errNoPerm
errNoTMK
errInvKek
errDubKey
errKBD
errKBDNoCal
errKBDBug
errBusy
errTampered
errEmsr
errAccept
errInvPAN
errOutOfMemory
errEMV
errCrypt
errComRcv
errWrongVer
errNoPaper
errTooHot
errNoConnected
errUseChip
errEndDay

# 7. TAGS

```text
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
```

some error in smart card reader
error code is returned from HAL functions
invalid key (may be no pressent)
the PIN length is <4 or >12
Issuer or ICC key invalid remainder length
(no used in this FW version)
(no used in this FW version)
(no used in this FW version)
The action is not permited
TMK is not loaded. The action cannot be executed
Wrong kek format
Dublicated key
general keyboard error
the keyboard is no calibrated
keyboard bug detected
the device is busy, tray again
the devicete in security tampered
error in encrypted head
the button "OK" is pressed
wrong PAN
no enought memory
some EMV error
cryptographic error
something is received
wrong version. update to old firmware for example
printer is out of paper
printer is overheating
the device is not connected
use the chip reader
end the day first

[HEX] TAG_DF05_TRANSACTION_RESULT
[HEX]    TAG_DF06_TRANSACTION_ERROR_CODE
[STRING]    TAG_DF31_TERMINAL_MERCHANT_NAME_BG
[STRING]    TAG_DF30_TERMINAL_MERCHANT_CITY_BG
[STRING]    TAG_DF2F_TERMINAL_MERCHANT_ADDRESS_BG
[STRING]    TAG_DF29_TERMINAL_MERCHANT_POST_CODE
[STRING]    TAG_DF2E_TERMINAL_MERCHANT_TITLE_BG
[STRING]    TAG_DF28_TERMINAL_MERCHANT_PHONE
[STRING]    TAG_9F1C_TERMINAL_ID
[STRING]    TAG_DF00_CARD_SCHEME
[STRING]    TAG_DF0A_MASKED_PAN
[STRING]    TAG_5F20_CARDHOLDER_NAME
[HEX]    BOR_TAG_PAY_INTERFACE
[HEX]    BOR_TAG_CARD_SCHEME_CL
[HEX]    TAG_DF10_TRANS_TYPE
[HEX]    TAG_DF0B_LOYALTY_PTS
[HEX]    TAG_81_AMOUNT_AUTHORISED
[HEX]    TAG_DF04_AMOUNT_EUR

0xDF05
0xDF06
0xDF31
0xDF30
0xDF2F
0xDF29
0xDF2E
0xDF28
0x9F1C
0xDF00
0xDF0A
0x5F20
0xDF25
0xDF60
0xDF10
0xDF0B
0x81
0xDF04

REF. 1)
REF. "ERROR CODES"

REF. 2)
REF. 3)
REF. 4)


---

[HEX]    TAG_DF23_CVM_SIGNATURE
[BCD]    TAG_9F41_TRANSACTION_SEQUENCE_COUNTER
[STRING]    TAG_DF07_HOST_RRN
[STRING]    BOR_TAG_HOST_AUTH_ID
[HEX]    BOR_TAG_HOST_CODE
[HEX]    BOR_TAG_TRANS_BATCH_NUM
[STRING]    TAG_9F16_TERMINAL_MERCHANT_ID
[STRING]    BOR_TAG_INTERFACE_ID
[BCD]    TAG_9F06_TERM_AID
[HEX]    TAG_9F26_APP_CRYPTOGRAM
[BCD]    TAG_9A_TRANSACTION_DATE
[BCD]    TAG_9F21_TRANSACTION_TIME
[HEX]    BOR_TAG_ISSUER_ID
[HEX]    BOR_TAG_TO_TYPE
[STRING] BOR_TAG_TERM_CURR_NAME
[HEX] BOR_CMD_TAG_CASHBACK
[HEX] BOR_TAG_BCARD_CID_1
[HEX] BOR_TAG_BCARD_CID_2
[HEX] BOR_TAG_IS_PIN_ENTERED
[STRING] BOR_TAG_CHIP_APPLICATION_NAME
[HEX]  BOR_TAG_MAX_CASHBACK_AMOUNT
[STRING] BOR_TAG_CASHBACK_CURRENCY
[HEX]  BOR_TAG_BCARD_SCA_DECLINED
[STRING]  BOR_TAG_TERMINAL_SERIAL_NUMBER
[HEX]  BOR_TAG_BATCH_NUMBER

# 8. REFERENCES

1. TRANSACTION_RESULTS

REF. 5)

[Year:Month:Day]
[Hour:Minute:Seconds]
REF. 6)
REF. 7)

0xDF23
0x9F41
0xDF07
0xDF08
0xDF09
0xDF61
0x9F16
0xDF62
0x9F06
0x9F26
0x9A
0x9F21
0xDF79
0xDF12
0xDF27
0x9F04
0xDF7D
0xDF7E
0xDF7F
0xDFC101
0xDF8004
0xDF8005
0xDF8006
0x9F1E
0xDF32

/** @brief Transaction is approved.*/
#define PAY_TRANSACTION_APPROVED
/** @brief Transaction is declined.*/
#define PAY_TRANSACTION_DECLINED
/** @brief Transaction error.*/
#define PAY_TRANSACTION_ERROR
/** @brief Try other interface. Contactless only.*/
#define PAY_TRANSACTION_TRY_OTHER_IF
/** @brief Try again. Contactless only.*/
#define PAY_TRANSACTION_TRY_AGAIN

2. INTERFACES

/** @brief Chip interface is used.*/
#define PAY_INTERFACE_CHIP
/** @brief Contactless interface is used.*/
#define PAY_INTERFACE_CONTACTLESS
/** @brief Magnetic stripe interface is used.*/
#define PAY_INTERFACE_MAG_STRIPE
/** @brief Manual card entry is used.*/
#define PAY_INTERFACE_MANUAL_ENTRY

0

1

2

3

4

0

1

2

3


---

3. CL CARD SCHEMES

/** @brief Contactless Card Scheme IDs. */
#define PAY_CL_CARD_SCHEME_VISA_AP
#define PAY_CL_CARD_SCHEME_PAYPASS
#define PAY_CL_CARD_SCHEME_VISA
#define PAY_CL_CARD_SCHEME_AMEX
#define PAY_CL_CARD_SCHEME_JCB
#define PAY_CL_CARD_SCHEME_DISCOVER
#define PAY_CL_CARD_SCHEME_BCARD

0x01
0x02
0x03
0x04
0x05
0x06
0x0A

4. TRANSACTION TYPES

1
#define BOR_CMD_TRANS_TYPE_PURCH
2
#define BOR_CMD_TRANS_TYPE_PURCH_CASH
3
#define BOR_CMD_TRANS_TYPE_PURCH_REF
4
#define BOR_CMD_TRANS_TYPE_CASH
5
#define BOR_CMD_TRANS_TYPE_AUTH
6
#define BOR_CMD_TRANS_TYPE_PURCH_CODE
7
#define BOR_CMD_TRANS_TYPE_VOID_PURCH
8
#define BOR_CMD_TRANS_TYPE_VOID_CASH
9
#define BOR_CMD_TRANS_TYPE_VOID_AUTH
```text
10
```
#define BOR_CMD_TRANS_TYPE_END_OF_DAY
```text
11
```
#define BOR_CMD_TRANS_TYPE_LOYALTY_BALANCE
#define BOR_CMD_TRANS_TYPE_LOYALTY_SPEND
```text
12
```
#define BOR_CMD_TRANS_TYPE_VOID_LOYALTY_SPEND 13
```text
14
```
#define BOR_CMD_TRANS_TYPE_TEST_CONN
```text
15
```
#define BOR_CMD_TRANS_TYPE_TMS_UPDATE

5. SIGNATURE TYPES

#define BOR_CVM_SIGN_CARDHOLDER
#define BOR_CVM_SIGN_MERCHANT

6. CARD ISSUERS

#define BOR_ISS_ID_BORICA
#define BOR_ISS_ID_VISA
#define BOR_ISS_ID_MASTERCARD
#define BOR_ISS_ID_MAESTRO
#define BOR_ISS_ID_AMEX
#define BOR_ISS_ID_DINERS_CLUB
#define BOR_ISS_ID_JCB
#define BOR_ISS_ID_AMEX_PIN
#define BOR_ISS_ID_BCARD

1
2

1
2
3
4
5
6
7
8
9


---

7. TO TYPES

#define BOR_TO_TYPE_NONE
#define BOR_TO_TYPE_REVERSAL
#define BOR_TO_TYPE_HANG

0
1
2

# 9. TLV STRUCTURE

When a transaction is performed, some information about it is being saved in the memory of the CARD
READER. This information is array, composed of multiple elements - tags in TLV format. TLV (Tag -
Len - Value) contains the name of the tag, length of the data and the data. For example let's say
Purchase was performed. Its amount is 1.00 BGN. So when this information is saved in TLV format it
will look like this:

```text
81 04 00 00 00 64
```

81 -  This is the Tag (TAG_81_AMOUNT_AUTHORISED - 0x81)
04 -  This is the Length of the data. It means, that the next 4 bytes will be the amount of this

transaction.

00 00 00 64 -  This is the Data for tag 0x81. It is in HEX format and it means that the amount =

100 (1.00)

Now   let's   say   the   Purchase,   which   was   performed,   has   more   information,   which   is   saved   in   the
memory. It can look like this:

```text
DF 10 02 00 01 81 04 00 00 00 64 DF 04 04 00 00 00 33 DF 23 02 00 01 DF 25 02 00 00 DF 61 02 00
73 DF 00 0B 56 69 73 61 20 43 72 65 64 69 74 5F 20 1A 56 49 53 41 20 41 43 51 55 49 52 45 52 20
54 45 53 54 2F 43 41 52 44 20 31 31 DF 62 02 43 31 9F 41 04 00 00 16 39 9F 21 03 09 34 22 9A 03
18 10 19 DF 09 04 00 00 00 00 DF 07 0C 38 32 39 32 30 36 36 38 33 30 33 33 DF 08 06 30 33 30 31
30 33 DF 05 04 00 00 00 00 DF 06 04 00 00 00 00 9F 06 08 A0 00 00 00 03 10 10 02
```

Online TLV parser (For example http://paymentcardtools.com/emv-tlv-parser) can be used, so that the
array can easily be understood. When we parse the data, it has the following meanings:

```text
DF 10 02 00 01
```
DF 10 -
02 -
00 01 -

```text
81 04 00 00 00 64
```

Tag 0xDF10 (TAG_DF10_TRANS_TYPE)
Lenght of the data = 2 bytes
The value of transaction type. From "Reference 4" from above we can see, that
this means, that the transaction is "Purchase".

81 -  Tag 0x81 (TAG_81_AMOUNT_AUTHORISED)
04 -  Length of the data = 4 bytes
00 00 00 64 -  The value of "Amount" is 100 (1.00)

```text
DF 04 04 00 00 00 33
```
Tag 0xDF04 (TAG_DF04_AMOUNT_EUR)
DF 04 -
04 -
Length of the data = 4 bytes
00 00 00 33 -  The value of "Amount EUR" is 51 (0.51)


---

```text
DF 23 02 00 01
```
DF 23 -
02 -
00 01 -

```text
DF 25 02 00 00
```
DF 25 -
02 -
00 00 -

```text
DF 61 02 00 73
```
DF 61 -
02 -
00 73 -

Tag 0xDF23 (TAG_DF23_CVM_SIGNATURE)
Length of the data = 2 bytes
The value of "Signature" is 1. From "Reference 5" from above we can see, that
this means, that for this transaction Cardholder signature is needed.

Tag 0xDF25 (BOR_TAG_PAY_INTERFACE)
Length of the data = 2 bytes
The value of "Payment Interface" is 0. From "Reference 2" from above we can
see, that this transaction was performed with Chip interface.

Tag 0xDF61 (BOR_TAG_TRANS_BATCH_NUM)
Length of the data = 2 bytes
This transaction was performed in batch with number = 115

```text
DF 00 0B 56 69 73 61 20 43 72 65 64 69 74
```

DF 00 -
0B -
56 69 73 61 20 43 72 65 64 69 74 -  The card, which was used in this transaction, has card

Tag 0xDF00 (TAG_DF00_CARD_SCHEME)
Lenght of the data = 11 bytes

scheme = "Visa Credit".

```text
5F 20 1A 56 49 53 41 20 41 43 51 55 49 52 45 52 20 54 45 53 54 2F 43 41 52 44 20 31 31
```

5F 20 -
1A -
56 49 53 41 20 41 43 51 55 49 52 45 52 20 54 45 53 54 2F 43 41 52 44 20 31 31 -

Tag 0x5F20 (TAG_5F20_CARDHOLDER_NAME)
Length of the data = 26 bytes

The cardholder name is "VISA ACQUIRER TEST/CARD 11".

```text
DF 62 02 43 31
```
DF 62 -
02 -
43 31 -

Tag 0xDF62 (BOR_TAG_INTERFACE_ID)
Length of the data = 2 bytes
"C1"

```text
9F 41 04 00 00 16 39
```
9F 41 -
04 -
00 00 16 39 -  This transaction is has number 1639.

Tag 0x9F41 (TAG_9F41_TRANSACTION_SEQUENCE_COUNTER)
Length of the data = 4 bytes

```text
9F 21 03 09 34 22
```

9F 21 -
03 -
09 34 22 -

Tag 0x9F21 (TAG_9F21_TRANSACTION_TIME)
Length of the data = 3 bytes
[Hour:Minute:Seconds] The time of the transaction is 09:34:22 .

```text
9A 03 18 10 19
```

9A -
03 -
18 10 19 -

Tag 0x9A (TAG_9A_TRANSACTION_DATE)
Length of the data = 3 bytes
[Year:Month:Day] The date of the transaction is 19.10.2018.


---

```text
DF 09 04 00 00 00 00
```
DF 09 -
04 -
00 00 00 00 -  The host error code is 0, which means it is successful transaction (no error).

Tag 0xDF09 (BOR_TAG_HOST_CODE)
Length of the data = 4 bytes

```text
DF 07 0C 38 32 39 32 30 36 36 38 33 30 33 33
```

DF 07 -
0C -
38 32 39 32 30 36 36 38 33 30 33 33 -

Tag 0xDF07 (TAG_DF07_HOST_RRN)
The length of the data = 12 bytes

The unique RRN number for this  transaction is
"829206683033".

```text
DF 08 06 30 33 30 31 30 33
```

DF 08 -
06 -
30 33 30 31 30 33 -  The unique Authorization ID number for this transaction is "030103".

Tag 0xDF08 (BOR_TAG_HOST_AUTH_ID)
Length of the data = 6 bytes

```text
DF 05 04 00 00 00 00
```
DF 05 -
04 -
00 00 00 00 - The transaction result has value 0. From "Reference 1" from above we can see,

Tag 0xDF05 (TAG_DF05_TRANSACTION_RESULT)
Length of the data = 4 bytes

that this transaction is approved (PAY_TRANSACTION_APPROVED).

```text
DF 06 04 00 00 00 00
```
Tag 0xDF06 (TAG_DF06_TRANSACTION_ERROR_CODE)
DF 06 -
04 -
Length of the data = 4 bytes
00 00 00 00 -  Transaction error code is 0 (there is no error).

```text
9F 06 08 A0 00 00 00 03 10 10 02
```

9F 06 -
08 -
A0 00 00 00 03 10 10 02 -  The Application ID of the card, which was used in this transaction

Tag 0x9F06 (TAG_9F06_TERM_AID)
Length of the data = 8 bytes

is A000000003101002, which means it is VISA card.


---

10.

TRANSACTION FLOW


---

• CLARIFICATIONS

1. Check if the reader is connected

Send “PING” command and see what is the ST value in the response from the CARD READER.

2. Start a transaction

Send  “TRANSACTION START” command and see what is the ST value in the response from the
CARD READER. Different subcommands can be used for starting different types of transaction.

3. Transaction loop

Once the EXT DEVICE successfully starts a transaction (the CARD READER returns a response,
containing ST field with value ‘00’), then the EXT DEVICE needs to “enter” in a transaction loop,
where few things need to be constantly executed:

• At any moment the CARD READER can unexpectedly send an event, which is indicating
that   something   needs   to   be   performed.  The   EXT  DEVICE   needs   to   be   capable   at   any
moment to receive such an event and execute it.

If the CARD READER has its own WIFI or GSM module, it will communicate with the
host by itself and basically the only event, which will be sent, is “0x01: TRANSACTION
COMPLETE” when the transaction is completed.

If the CARD READER does NOT have its own capability for communicating with the host,
then in the Transaction loop the EXT DEVICE needs to be able to also receive all events,
which are described in the section “0x0F: External internet subevents”.

Once the EXT DEVICE receives the event “0x01: TRANSACTION COMPLETE”, then it
can “exit” from the Transaction loop and go to step 4.

Note: If chip card with multiple chip applications is used, only the BlueCash-50 device at
some   point   will   also   send   event   “0x3F:   SELECT  CHIP APPLICATION”   and   the   EXT
DEVICE should be able to execute it.

•

If there is socket, which was previously opened from the EXT DEVICE (this happens only
after the CARD READER sends the event “0x01: SOCKET OPEN” and before the CARD
READER sends the event “0x02: SOCKET CLOSE”, when the socket is being closed), then
the EXT DEVICE needs to constantly wait for data to be returned from the host at any time.
Once any kind of data is returned from the host, it needs to be sent to the CARD READER
using the subcommand “0x01: RECEIVE DATA”.


---

4. Get additional information

Once the transaction is completed (The event “0x01: TRANSACTION COMPLETE” was received
from the CARD READER), then the EXT DEVICE can get additional information for the currently
performed transaction by calling the subcommand “0x02: GET RECEIPT TAGS”.

5. Finish the transaction

At   the   end   of   the   transaction,   the   EXT   DEVICE   needs   to   send   to   the   CARD   READER   the
subcommand “0x03: TRANSACTION END”.

6. Display result message

When the transaction is completed, the CARD READER will send to the EXT DEVICE the subevent
“0x01: TRANSACTION COMPLETE”. This subevent will contain the following tags:

•

•

•

•

•

0xDF05 (Transaction result)

0xDF06 (Error code)

0xDF8004 (Maximum cashback amount) – In most cases this tag will be missing (optional).

0xDF8005 (Cashback currency) – In most cases this tag will be missing (optional).

0xDF8006 (Bcard SCA is declined) – In most cases this tag will be missing (optional).

When displaying the final result message (Approved / Declined / Error), the EXT DEVICE has to
implement the following logic:

•

If tag 0xDF05 has value ‘00’ (Approved), then the message should be “Transaction Approved”
(or similar).

• Else if both tags 0xDF8004 and 0xDF8005 are present (With example value ‘DF 80 04 04 00 00
00 64 DF 80 05 03 42 47 4E’), then the following message should be displayed “Transaction
declined! Maximum amount in cash is 100 BGN!”, where “100” is the example value of tag
0xDF8004 and “BGN” is the example value of tag 0xDF8005. These 2 tags can be sent only
from the device BlueCash-50!

• Else if tag 0xDF8006 is present (With example value ‘DF 80 06 01 01’, the value will always
be hardcoded to 01 here), the following message should be displayed “Transaction declined,
PIN required! Please try again!”. This tag can be sent only from the device BlueCash-50!

• Else   if   tag   0xDF05   has   value   ‘01’  (Declined),   then   the   message   should   be   “Transaction
Declined (<error_code>)”, or similar, where the <error code> is the value of tag 0xDF09 (Host
status code), which can additionally be taken using the subcommand “0x02: GET RECEIPT
TAGS”. Please check “13. HOST ERROR STRINGS”, if <error_code> value is defined there,
an additional error string can be added to the message “Transaction Declined (<error_code>).
<Error string>”, so for example if tag 0xDF09 has value ‘DF 09 04 00 00 00 37’, then the
message would be “Transaction Declined (55). Incorrect PIN”.

• Else if tag 0xDF05 has value ‘02’ (Error) or in all other cases (by default), the message should
be “Transaction error (<error_code>)”, or similar, where the <error_code> is the value of tag


---

0xDF06. Please check “12. CARD READER ERROR STRINGS”, if <error_code> value is
defined   there,   an   additional   error   string   can   be   added   to   the   message   “Transaction   error
(<error_code>). <Error string>”, so for example if tag 0xDF06 has value ‘DF 06 04 00 00 00
12’, then the message would be “Transaction error (18). Operation canceled”.

7. Display error message

If there is any error before even starting the transaction, the EXT DEVICE should display correct error
message.

11.

EXAMPLE TRANSACTION

This is an example of the entire process that is needed to successfully execute a transaction.

1. The EXT DEVICE sends "0x00: PING" subcommand.

>> (EXT DEVICE):

```text
3E 3D 00 00 01 00 02
```

<< (CARD READER):

```text
3E 00 00 00 00 3E
```

2. The   EXT   DEVICE   sends   "0x01:   TRANSACTION   START"   subcommand.   This   is   an
example for "Test Connection", but if you want to start a different transaction, you can see
the examples, given in the subcommand.

>> (EXT DEVICE):

```text
3E 3D 00 00 0D 01 0E 9A 03 19 03 26 9F 21 03 15 11 02 1F
```

<< (CARD READER):

```text
3E 00 00 00 00 3E
```

3. At  some   point  the  CARD   READER  will  need  to  open  a  socket. Then  it  will  send the

subevent "0x01: SOCKET OPEN".

<< (CARD READER):

```text
3E 0F 00 00 26 01 01 01 55 FF 80 C4 4E ED 00 1E DF 50 06 62 6F 72
69 63 61 DF 53 00 DF 54 00 DF 6C 04 58 CB EF 2E DF 6D 02 4E EE
2A
```

4. The EXT DEVICE must confirm if it opened the socket successfully.  It must send the

subcommand "0x02: EVENT CONFIRM".

>> (EXT DEVICE):

```text
3E 40 00 00 05 02 01 00 04 00 7C
```

<< (CARD READER):

```text
3E 00 00 00 00 3E
```

5. Then the CARD READER needs to send some data to the server. The CARD READER

sends the subevent "0x03: SEND DATA".

<< (CARD READER):

```text
3E 0F 00 00 C0 03 01 00 BC 60 03 33 00 00 08 00 20 38 00 00 00 C0 00
15 91 00 00 00 03 67 15 11 31 03 26 39 33 38 30 30 31 33 30 39 39 39
33 39 30 30 30 30 31 30 30 30 30 30 00 79 00 03 38 30 30 00 04 38 31
```


---

```text
01 22 00 12 38 32 42 6C 75 65 50 61 64 2D 35 30 00 04 39 31 00 00 00
04 39 32 00 00 00 04 39 33 00 00 00 04 39 34 00 00 00 04 39 35 00 00
00 04 39 36 00 00 00 04 39 37 00 00 00 04 39 38 00 00 00 04 39 39 00
00 00 48 94 2D 02 E3 6F 16 09 0C 6D 9F B3 C7 6C 4C 83 03 61 11 03
1D 2A F5 FF 16 A2 7F BC AB 6B 5C E8 3E 4B 68 51 FD 77 AE A4 EF
EF 8A 75 4C B3 A4 E6 DB 58 34 24 1A 00 00 00 00 36
```

6. The EXT DEVICE must confirm if it sent the data to the host successfully. It must send the

subcommand "0x02: EVENT CONFIRM".

>> (EXT DEVICE):

```text
3E 40 00 00 03 02 03 00 7C
```

<< (CARD READER):

```text
3E 00 00 00 00 3E
```

7. Then the response from the host will be received from the EXT DEVICE and it needs to
transfer the data to the CARD READER. The EXT DEVICE must call the subcommand
"0x01: RECEIVE DATA".

>> (EXT DEVICE):

```text
3E 40 00 00 70 01 00 6D 60 00 00 03 33 08 10 20 38 00 00 02 C0 00 05
91 00 00 00 03 67 15 11 52 03 26 30 30 39 33 38 30 30 31 33 30 39 39
39 33 39 30 30 30 30 31 30 30 30 30 30 00 48 94 2D 02 E3 6F 16 09 0C
6D 9F B3 C7 6C 4C 83 03 61 11 03 1D 2A F5 FF 16 A2 7F BC AB 6B
5C E8 3E 4B 68 51 FD 77 AE A4 EF EF 8A 75 4C B3 A4 E6 DB F5 7D
E1 C3 00 00 00 00 B9
```

<< (CARD READER):

```text
3E 00 00 00 00 3E
```

8. The CARD READER will send the subevent "0x02: SOCKET CLOSE".

<< (CARD READER):

```text
3E 0F 00 00 02 02 01 30
```

9. The   EXT  DEVICE   must   confirm   if   it   closed   the   socket   successfully.   It   must   send   the

subcommand "0x02: EVENT CONFIRM".

>> (EXT DEVICE):

```text
3E 40 00 00 03 02 02 00 7D
```

<< (CARD READER):

```text
3E 00 00 00 00 3E
```

10.The   CARD   READER   sends   the   subevent   "0x01:   TRANSACTION   COMPLETE

(PAYMENT RESULT)".

<< (CARD READER):

```text
3E 0E 00 00 1C 01 DF 05 04 00 00 00 00 DF 06 04 00 00 00 00 81 04 00
00 00 00 9F 41 04 00 00 03 67 15
```


---

11.The   EXT  DEVICE   sends   "0x02:   GET  RECEIPT TAGS"   command   to   get   information,
which is needed to print a receipt for this transaction. In case of "Test Connection" there is
no receipt, but the given example is from transaction "Purchase + TIP".

>> (EXT DEVICE):

<< (CARD READER):

```text
3E 3D 00 00 5B 02 81 9F 04 9A 9F 21 9F 06 9F 26 9F 1C 9F 16 5F 2A
9F 41 5F 20 DF 00 DF 01 DF 02 DF 03 DF 04 DF 05 DF 06 DF 07 DF
08 DF 09 DF 0A DF 0B DF 10 DF 12 DF 19 DF 23 DF 25 DF 24 DF 26
DF 27 DF 28 DF 29 DF 2A DF 2B DF 2C DF 2D DF 2E DF 2F DF 30
DF 31 DF 60 DF 61 DF 62 DF 63 DF 64 18
```

```text
3E 00 00 01 42 81 04 00 00 00 1E 9A 03 19 03 20 9F 21 03 18 22 22 9F
06 07 A0 00 00 00 03 20 10 9F 26 08 5D 58 40 B4 E2 51 EE 9B 9F 1C
08 39 33 38 30 30 31 33 30 9F 16 0F 39 39 39 33 39 30 30 30 30 31 30
30 30 30 30 5F 2A 02 09 75 9F 41 04 00 00 03 65 5F 20 10 58 58 58 58
58 58 58 20 20 58 58 58 58 58 58 58 DF 00 0D 56 69 73 61 20 45 6C 65
63 74 72 6F 6E DF 04 04 00 00 00 0F DF 05 04 00 00 00 00 DF 06 04
00 00 00 00 DF 07 0C 30 30 30 30 30 36 36 39 31 31 33 35 DF 08 06 39
36 39 33 36 34 DF 09 04 00 00 00 00 DF 0A 10 2A 2A 2A 2A 2A 2A 2A
2A 2A 2A 2A 2A 37 38 39 38 DF 10 01 01 DF 12 02 00 00 DF 23 02 00
00 DF 25 02 00 01 DF 26 02 0A 02 DF 27 03 42 47 4E DF 28 07 39 37
30 32 36 31 30 DF 29 04 31 30 30 30 DF 2A 04 54 45 53 54 DF 2E 06
44 41 54 45 43 53 DF 2F 19 42 55 4C 2E 54 5A 41 52 49 47 52 41 44 53
4B 4F 20 53 48 41 4F 53 53 45 45 DF 30 05 53 4F 46 49 41 DF 31 04 54
45 53 54 DF 60 04 00 00 00 03 DF 61 02 00 27 DF 62 02 43 31 DF 63
04 00 00 00 0A DF 64 04 00 00 00 05 CC
```

12.The EXT DEVICE sends "0x03: TRANSACTION END" command.

>> (EXT DEVICE):

```text
3E 3D 00 00 01 03 01
```

<< (CARD READER):

```text
3E 00 00 00 00 3E
```

Note: If the CARD READER has capability for communicating with the host by its
own, then the steps 3-9 will be missing from the transaction flow.

12.

CARD READER ERROR STRINGS

These are some of the more common error codes, which can be returned in tag 0xDF06. Please check
“6. Display result message” what should be the logic for displaying the transaction result string.

DF06 values:

1 (0x01): “General error”

2 (0x02): “Invalid command”

3 (0x03): “Invalid parameter”

5 (0x05): “Invalid length”


---

7 (0x07): “Operation is not permitted”

8 (0x08): “No data”

9 (0x09): “Timeout”

12 (0x0C): “Invalid device”

18 (0x12): “Operation canceled”

21 (0x15): “Wrong password”

31 (0x1F): “Operation is not permitted”

50 (0x32): “No connection with the host”

51 (0x33): “Please, use chip”

52 (0x34): “Please, end day”

13.

HOST ERROR STRINGS

These are some of the more common error codes, which can be returned in tag 0xDF09. Please check
“6. Display result message” what should be the logic for displaying the transaction result string.

DF09 values:

00 (0x00): “Approved transaction”

04 (0x04): “Pick up the card”

06 (0x06): “Technical problem”

07 (0x07): “Pick up the card”

12 (0x0C): “Invalid transaction”

13 (0x0D): “Invalid amount”

14 (0x0E): “Invalid card number”

15 (0x0F): “Unable to route to issuer host”

33 (0x21): “Expired card”

36 (0x24): “Restricted card. Pick up the card”

37 (0x25): “Pick up the card and call security dept.”

38 (0x26): “Allowable PIN tries exceeded”

41 (0x29): “Lost card. Pick up the card”

43 (0x2B): “Stolen card. Pick up the card”

51 (0x33): “Insufficient funds”

52 (0x34): “No checking account”

53 (0x35): “No savings account”

54 (0x36): “Expired card”


---

55 (0x37): “Incorrect PIN”

57 (0x39): “Transaction is not permitted to the cardholder”

58 (0x3A): “Transaction is not permitted to the terminal”

65 (0x41): “Exceeded withdrawal frequency limit”

66 (0x42): “Pick up the card and call security dept.”

67 (0x43): “Pick up the card and call security dept.”

75 (0x4B): “Allowable number of PIN tries exceeded”

78 (0x4E): “Account balance unavailable”

79 (0x4F): “Unacceptable PIN”

82 (0x52): “Timeout”

86 (0x56): “PIN validation not possible”

87 (0x57): “Partial approved transaction”

91 (0x5B): “Issuer is inoperative”

92 (0x5C): “Issuer is inoperative”

94 (0x5E): “Duplicated transaction”

96 (0x60): “System malfunction”

14.

0x0B: EMV subevents

## 1. 0x82: USER INTERFACE

**DESCRIPTION:**

At some point during the transaction this event can be sent from the  CARD READER. This
event will be sent only from the device BlueCash-50! In this case, if the [MESSAGE ID: 2] value is
any   of   the   described   below   ones,   then   the   EXT   DEVICE   should   display   the   message.   If   the
[MESSAGE ID: 2] is missing in the below examples, then it can be ignored.

**CARD READER:**

0B 00 LH LL [SUBEVENT] 00 C1 02 [MESSAGE ID: 2]

[MESSAGE ID: 2]:

00 10: „Remove card”
00 15: “Present card”
00 16: “Processing”
00 17: “Card read OK. Please remove card.”
00 18: “Try other interface”
00 1B: “Online authorization”
00 1C: “Try other card”
00 1D: “Insert card”
00 20: “See phone”


---

00 21: “Present card again”
00 F0: „Please use the chip reader”
00 F1: “Please insert, read or try another card”

**EXAMPLE:**

(CARD READER -> EXT DEVICE) >>

```text
3E 0B 00 00 06 82 00 C1 02 00 F0 82
```

**CLARIFICATION:**

(CARD READER -> EXT DEVICE):

'>':
**EVENT:**
**00:**
**LH LL:**
**SUBEVENT:**
**00:**
**C1:**
**02:**
[MESSAGE ID: 2]:
**CSUM:**

0x3E - Start packet.
0x0B - EMV event.
0x00 - Fixed value '00'.
0x00 0x06 - The data length is 6 bytes.
0x82 – USER INTERFACE subevent.
0x00 - Fixed value '00'.
0xC1 - Fixed value ‘C1’.
0x02 - Fixed tag length '02'.
0x00 0xF0 - „Please use the chip reader”
0x82 - Xor of all bytes (3E 0B 00 00 06 82 00 C1 02 00 F0).


---


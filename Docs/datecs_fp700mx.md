

# Page 1

FISCAL DEVICE
DATECS FMP-350X
DATECS FMP-55X
DATECS FP-700X
DATECS FP-700X E
DATECS WP-500X
DATECS WP-50X
DATECS DP-25X
DATECS DP-150X
DATECS DP-05C
DATECS WP-25X
Programmer’s Manual
The information contained in this document is subject to change without notice. No part of this document may be reproduced
or transmitted, in any form or by any means, mechanical, electrical or electronic without the prior written permission of  Date cs Ltd.
Version: 2.08, 2019


# Page 2

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
                                                                                                                                    
Description of the program interface .................................................................................................................................................................................. 3Low level protocol............................................................................................................................................................................................................... 3A) Protocol type - Master (Host) / Slave ............................................................................................................................................................................. 3B) Sequence of the messages ........................................................................................................................................................................................... 3C) Non-wrapped messages – time-out ............................................................................................................................................................................... 3D) Wrapped messages....................................................................................................................................................................................................... 4Message composition, syntax and meanings ..................................................................................................................................................................... 5Command explanations...................................................................................................................................................................................................... 6Command: 33 (21h) Clears the external display. ............................................................................................................................................................... 7Command: 35 (23h) Displaying text on second line of the external display. ..................................................................................................................... 7Command: 38 (26h) Opening a non-fiscal receipt ............................................................................................................................................................. 7Command: 39 (27h) Closing a non-fiscal receipt ............................................................................................................................................................... 7Command: 42 (2Ah) Printing of a free non-fiscal text ........................................................................................................................................................ 8Command: 43 (2Bh) Opening of storno documents ........................................................................................................................................................... 8Command: 44 (2Ch) Paper feed ........................................................................................................................................................................................ 9Command: 45 (2Dh) Check for mode connection with PC ................................................................................................................................................ 9Command: 46 (2Eh) Paper cutting ..................................................................................................................................................................................... 9Command: 47 (2Fh) Displaying text on upper line of the external display. ..................................................................................................................... 10Command: 48 (30h) Open fiscal receipt ........................................................................................................................................................................... 10Command: 49 (31h) Registration of sale .......................................................................................................................................................................... 10Command: 50 (32h) Return the active VAT rates ............................................................................................................................................................ 11Command: 51 (33h) Subtotal ........................................................................................................................................................................................... 12Command: 53 (35h) Payments and calculation of the total sum (TOTAL) ...................................................................................................................... 12Command: 54 (36h) Printing of a free fiscal text .............................................................................................................................................................. 13Command: 55 (37h) Pinpad commands ........................................................................................................................................................................... 14Command: 56 (38h) Close fiscal receipt .......................................................................................................................................................................... 17Command: 57 (39h) Enter and print invoice data ............................................................................................................................................................ 17Command: 58 (3Ah) Registering the sale of a programmed item .................................................................................................................................... 17Command: 60 (3Ch) Cancel fiscal receipt ........................................................................................................................................................................ 18Command: 61 (3Dh) Set date and time ............................................................................................................................................................................ 18Command: 62 (3Eh) Read date and time ......................................................................................................................................................................... 19Command: 63 (3Fh) Show current date and time on the external display ....................................................................................................................... 19Command: 64 (40h) Information on the last fiscal entry .................................................................................................................................................. 19Command: 65 (41h) Information on daily taxation ........................................................................................................................................................... 20Command: 66 (42h) Set invoice interval .......................................................................................................................................................................... 20Command: 68 (44h) Number of remaining entries for Z-reports in FM ............................................................................................................................ 21Command: 69 (45h) Reports ............................................................................................................................................................................................ 21Command: 70 (46h) Cash in and Cash out operations .................................................................................................................................................... 22Command: 71 (47h) General information, modem test .................................................................................................................................................... 22Command: 72 (48h) Fiscalization ..................................................................................................................................................................................... 23Command: 74 (4Ah) Reading the Status ......................................................................................................................................................................... 23Command: 76 (4Ch) Status of the fiscal transaction ........................................................................................................................................................ 24Command: 80 (50h) Play sound ....................................................................................................................................................................................... 24Command: 83 (53h) Programming of VAT rates .............................................................................................................................................................. 25Command: 84 (54h) Printing of barcode .......................................................................................................................................................................... 25Command: 86 (56h) Date of the last fiscal record ............................................................................................................................................................ 26Command: 87 (58h) Get item groups information ............................................................................................................................................................ 26Command: 88 (58h) Get department information ............................................................................................................................................................ 26Command: 89 (59h) Test of Fiscal Memory ..................................................................................................................................................................... 27Command: 90 (5Ah) Diagnostic information .................................................................................................................................................................... 27Command: 91 (5Bh) Programming of Serial number and FM number ............................................................................................................................ 28Command: 92 (5Ch) Printing of separating line ............................................................................................................................................................... 28Command: 94 (5Еh) Fiscal memory report by date ......................................................................................................................................................... 28Command: 95 (5Fh) Fiscal memory report by number of Z-report .................................................................................................................................. 29Command: 96 (60h) Set Software Password. .................................................................................................................................................................. 29Command: 98 (62h) Programming of TAX number ......................................................................................................................................................... 29Command: 99 (63h) Reading the programmed TAX number .......................................................................................................................................... 30Command: 100 (64h) Reading an error ........................................................................................................................................................................... 30Command: 101 (65h) Set operator password .................................................................................................................................................................. 30Command: 103 (67h) Information for the current receipt ................................................................................................................................................. 31Command: 105 (69h) Report operators ........................................................................................................................................................................... 31Command: 106 (6Ah) Drawer opening ............................................................................................................................................................................. 31Command: 107 (6Bh) Defining and reading items ........................................................................................................................................................... 32Command: 109 (6Dh) Print duplicate copy of receipt ...................................................................................................................................................... 34Command: 110 (6Eh) Additional daily information ........................................................................................................................................................... 35Command: 111 (65h) PLU report ..................................................................................................................................................................................... 36Command: 112 (70h) Information for operator ................................................................................................................................................................. 37Command: 116 (74h) Reading FM. .................................................................................................................................................................................. 37Command: 122 (7Ah) Printing of a free vertical fiscal text ............................................................................................................................................... 37Command: 123 (7Bh) Device information ........................................................................................................................................................................ 38Command: 124 (7Ch) Search receipt number by period ................................................................................................................................................. 39Command: 125 (7Dh) Information from EJ ...................................................................................................................................................................... 40Command: 127 (7Fh) Stamp operations .......................................................................................................................................................................... 42Command: 135 (87h) Modem information ........................................................................................................................................................................ 42Command: 140 (8Ch) Defining and reading clients ......................................................................................................................................................... 43Command: 202 (CAh) Customer graphic logo loading. ................................................................................................................................................... 45Command: 203 (CAh) Stamp image loading. ................................................................................................................................................................... 45Command: 255 (FFh) Programming ................................................................................................................................................................................ 46Status bits......................................................................................................................................................................................................................... 52
2


# Page 3

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
Description of the program interface
The fiscal device operates under the control of an application program, with which communicates 
via RS232 ( USB or LAN) serial connection. The device executes a previously set of wrapped commands, 
arranged according to the type of the operations which have to be executed. The application program does not 
have a direct access to the resources of the fiscal device although it can detect data connected with the status of 
the fiscal device and the fiscal control unit.
Low level protocol
A) Protocol type - Master (Host) / Slave
The fiscal printer performs the commands sent by the Host and returns messages, which depend on 
the result. The fiscal printer cannot instigate asynchronous communications itself. Only responses to commands 
from the Host are sent to the Host. These messages are either wrapped or single byte control codes. The fiscal 
printer maintains the communication via the RS232 serial connection at baud rates of 1200, 2400, 4800, 9600, 
19200, 38400, 57600 and 115200 b/s, 8N1. 
B) Sequence of the messages
Host sends a wrapped message, containing a command for the fiscal printer. ECR executes the 
requested operation and response with a wrapped message. Host has to wait for a response from the fiscal 
printer before to send another message. The protocol uses non-wrapped messages with a length one byte for 
processing of the necessary pauses and error conditions.
C) Non-wrapped messages – time-out
When the transmitting of messages from the Host is normal, Slave answers not later than 60 ms 
either with a wrapped message or with a 1 byte code. Host must have 500 ms of time-out for receiving a 
message from Slave. If there is no message during this period of time the Host will transmit the message again 
with the same sequence number and the same command. After several unsuccessful attempts Host must indicate
that there is either no connection to the fiscal printer or there is a hardware fault.
Non-wrapped messages consist of one byte and they are:
A) NAK 15H
This code is sent by Slave when an error in the control sum or the form of the received message is found. When 
Host receives a NAK it must again send a message with the same sequence number.
B) SYN 16H
This code is sent by Slave upon receiving a command which needs longer processing time. SYN is sent every 
60 ms until the wrapped message is not ready for transmitting.
3


# Page 4

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
D) Wrapped messages
a) Host to fiscal printer (Send)
<01><LEN><SEQ><CMD><DATA><05><BCC><03>
Example:
01 30 30 32 3F 24 30 30 32 3A 54 65 73 74 09 05 30 33 36 3F 03
b) Fiscal printer to Host (Receive)
<01><LEN><SEQ><CMD><DATA><04><STATUS><05><BCC><03>
Example:
01 30 30 33 35 24 30 30 32 3A 30 09 04 80 80 A0 80 86 9A 80 80  05 30 36 33 3A 03
Where:
<01>     Preamble.    - 1 byte long. Value: 01H.
<LEN> Number of bytes from <01> preamble (excluded) to <05> (included) plus the fixed offset of 20H.
              Length: 4 bytes. Each digit from the two bytes is sent after 30H is added to it. From example – Input 
have 15(0Fh) bytes - 30 30 32 3F 24 30 30 32 3A 54 65 73 74 09 05
Now add 20h →000F + 0020 = 002F. Sum 002F is presented as 30H, 30H, 32H, 3FH
<SEQ> Sequence number of the frame. 
             Length : 1 byte. Value: 20H – FFH. The fiscal printer saves the same <SEQ> in the return message. If 
the ECR gets a message with the same <SEQ> as the last message received it will not perform any operation, 
but will repeat the last sent message.
<CMD>  The code of the command. 
             Length: 4 byte.  The fiscal printer saves the same <CMD> in the return message. If the fiscal printer 
receives a non-existing code it returns a wrapped message with zero length in the data field and sets the 
respective status bit. Each digit from the two bytes is sent after 30H is added to it. From example, used 
command is 42 (2Ah). Command 002A is presented as 30H, 30H, 32H, 3AH
<DATA>  Data. 
             Length: 0-213 bytes for Host to fiscal printer, 0-218 bytes for Fiscal printer to Host. Value: 20H – FFH.
The format and length of the field for storing data depends on the command. If the command has no data the 
length of this field is zero. If there is a syntax error the respective status bit is established in the data and a 
wrapped message is returned with zero field length.
From example, input value Text\t is presented as 54H, 65H, 73H, 74H, 09H  (ASCII to hex convert)
<04> Separator (only for fiscal printer-to-Host massages),  - Not used in input
            Length: 1 byte. Value: 04H.
<STATUS> The field with the current status of the fiscal device. - Not used in input
            Length: 8 bytes. Value: 80H-FFH.
<05> Postamble
            Length: 1 byte. Value:05H.
<BCC> Control sum (0000H-FFFFH), 
            Length: 4 bytes. Value of each byte: 30H-3FH. The sum includes between <01> preamble (excluded) to 
<05> Each digit from the two bytes is sent after 30H is added to it. 
From example sum of 30 30 32 3F 24 30 30 32 3A 54 65 73 74 09 05 is 036F. 036F is presented as 
30H, 33H, 36H, 3FH
<03> Terminator, Length: 1 byte. Value: 03H.
4


# Page 5

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
Message composition, syntax and meanings
a) The data field depends on the command.
b) The parameters sent to the fiscal printer may be separated with a [\t] and/or may have a fixed length.
c) The separator( [\t] ) between the parameters shows that it is mandatory.
d) Some of the parameters are mandatory and others are optional. Optional parameters can be left empty, but 
after them must have separator ( [\t] ).
The symbols with ASCII codes under 32 (20H) have special meanings and their use is explained whenever 
necessary. If such a symbol has to be sent for some reason (for example in an ESCAPE-command to the 
display) it must be preceded by 16 (10H) with an added offset 40H.
Example: when we write 255,PrintColumns[\t][\t][\t]  for the data field then in that field there will be 50 72 69 
6E 74 43 6F 6C 75 6D 6E 73 09 09 09  where each hexadecimal digit is an ASCII value.
5


# Page 6

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
Command explanations 
This is example command syntax: 
{Parameter1}<SEP>{Parameter2}<SEP>{Parameter3}<SEP><DateTime><SEP>
Note:  <SEP> - this tag must be inserted after each parameter to separate different parameters. It's value is '[\
t]' (tab). It is the same for all commands.
Mandatory parameters:
Parameter1 - This parameter is mandatory, it must be filled; 
Parameter3 - This parameter is mandatory, it must be filled;
A - Possible value of Parameter3; 
Answer(1) - if Parameter3 has value 'A' see Answer(1); 
B - Possible value of Parameter3; 
Answer(2) - if Parameter3 has value 'B' see Answer(2); 
DateTime - Date and time format: DD-MM-YY hh:mm:ss DST
DD - Day 
MM - Month 
YY - Year 
hh - Hours 
mm - Minutes 
ss - Seconds 
DST - Text DST. If exist means that summer time is active. 
Optional parameters:
Parameter2 - This parameter is optional it can be left blank, but separator must exist. Default: X; 
Note
If left blank parameter will be used with value, after "Default:" in this case 'X', but in some cases 
blank parameter may change the meaning of the command, which will be explained for each 
command;
Answer(X) - This is the default answer of the command. 
Under each command there will be list with possible answers.
Answer when command fail to execute is the same for all commands, so it will not be explained after each 
command. 
Answer when command fail to execute: 
{ErrorCode}<SEP>
ErrorCode - Indicates an error code; 
6


# Page 7

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
Command: 33 (21h) Clears the external display. 
Parameters of the command: 
none
Answer: 
{ErrorStatus}<SEP>
ErrorCode - Indicates an error code;
Note: The command is not used on FMP-350X and FMP-55X; 
Command: 35 (23h) Displaying text on second line of the external display. 
Parameters of the command: 
{Text}<SEP>
Mandatory parameters:
Text - Text to be sent directly to the external display ( up to 20 symbols );
Answer: 
{ErrorStatus}<SEP>
ErrorCode - Indicates an error code;
Note: The command is not used on FMP-350X and FMP-55X; 
Command: 38 (26h) Opening a non-fiscal receipt 
Parameters of the command: 
none
Answer: 
{ErrorCode}<SEP>{SlipNumber}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
SlipNumber - Current slip number (1...9999999); 
Command: 39 (27h) Closing a non-fiscal receipt 
Parameters of the command: 
none
Answer: 
{ErrorCode}<SEP>{SlipNumber}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
SlipNumber - Current slip number (1...9999999); 
7


# Page 8

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
Command: 42 (2Ah) Printing of a free non-fiscal text 
Parameters of the command: 
{Text}<SEP>{Bold}<SEP>{Italic}<SEP>{Height}<SEP>{Underline}<SEP>{alignment}<SEP>
Mandatory parameters:
Text - text of 0...XX symbols. XX depend of opened receipt type. XX = (PrintColumns-2); 
Optional parameters:
Bold - flag 0 or 1, 1 = print bold text; empty field = normal text; 
Italic - flag 0 or 1, 1 = print italic text; empty field = normal text; 
Height  - 0, 1 or 2. 0=normal height, 1=double height, 2=half height; empty field = normal height text; 
Underline - flag 0 or 1, 1 = print underlined text; empty field = normal text; 
alignment - 0, 1 or 2. 0=left alignment, 1=center, 2=right; empty field = left alignment; 
Answer: 
{ErrorCode}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
Command: 43 (2Bh) Opening of storno documents 
Parameters of the command: 
{OpCode}<SEP>{OpPwd}<SEP>{TillNmb}<SEP>{Storno}<SEP>{DocNum}<SEP>{DateTime}<SEP>{FM
Number}<SEP>{Invoice}<SEP>{ToInvoice}<SEP>{Reason}<SEP>{NSale}<SEP>
Mandatory parameters:
OpCode - Operator number from 1...30; 
OpPwd - Operator password, ascii string of digits. Length from 1...8; 
Note: WP-500X, WP-25X, WP-50X, DP-25X, DP-150X, DP-05C:  the default password for each operator is equal to the corresponding 
number (for example, for Operator1 the password is "1") . FMP-350X, FMP-55X, FP-700X :  the default password for each operator is 
“0000”
TillNmb - Number of point of sale from 1...99999; 
Storno - Reason for storno. 
If Storno has value '0' it opens storno receipt. Reason "operator error"; 
If Storno has value '1' it opens storno receipt. Reason "refund"; 
If Storno has value '2' it opens storno receipt. Reason "tax base reduction"; 
DocNum - Number of the original document ( global 1...9999999 ); 
FMNumber - Fiscal memory number of the device the issued the original document; 
DateTime - Date and time of the original document( format "DD-MM-YY hh:mm:ss DST" ); 
Optional parameters:
Invoice - If this parameter has value 'I' it opens an invoice storno/refund receipt. 
ToInvoice - If Invoice is 'I' - Number of the invoice that this receipt is referred to; If Invoice is blank 
this parameter has to be blank too; 
Reason - If Invoice is 'I' - Reason for invoice storno/refund. If Invoice is blank this parameter has to be 
blank too; 
NSale - Unique sale number (21 chars "LLDDDDDD-CCCC-DDDDDDD", L[A-Z], C[0-9A-Za-z], 
D[0-9] ) The parameter is not required only if the original document is printed by the cashier and not by 
the PC program. 
8


# Page 9

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
Answer: 
{ErrorCode}<SEP>{SlipNumber}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
SlipNumber - Current slip number (1...9999999); 
Command: 44 (2Ch) Paper feed 
Parameters of the command: 
{Lines}<SEP>
Optional parameters:
Lines - Number of lines to feed from 1 to 99. Default: 1;
Answer: 
{ErrorCode}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0;
Command: 45 (2Dh) Check for mode connection with PC 
Parameters of the command: 
Syntax 1: none
Syntax 2: {DisablePrinting}<SEP>
Optional parameters:
DisablePrinting – Enable/disable printout. 1 – enable, 0 – disable;
◦Note: This option is possible to be used only if device is registered with FDType = 11 or 21!
Answer: 
{ErrorCode}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0;
Command: 46 (2Eh) Paper cutting 
Parameters of the command: 
none
Answer: 
{ErrorCode}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0;
Note: The command is only used on FP-700X; 
9


# Page 10

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
Command: 47 (2Fh) Displaying text on upper line of the external display. 
Parameters of the command: 
{Text}<SEP>
Mandatory parameters:
Text - Text to be sent directly to the external display ( up to 20 symbols );
Answer: 
{ErrorStatus}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0;
Note: The command is not used on FMP-350X and FMP-55X; 
Command: 48 (30h) Open fiscal receipt 
Parameters of the command: 
Syntax 1:
{OpCode}<SEP>{OpPwd}<SEP>{TillNmb}<SEP>{Invoice}<SEP>
Syntax 2:
{OpCode}<SEP>{OpPwd}<SEP>{NSale}<SEP>{TillNmb}<SEP>{Invoice}<SEP>
Mandatory parameters:
OpCode - Operator number from 1...30; 
OpPwd - Operator password, ascii string of digits. Length from 1...8; 
Note: WP-500X, WP-25X, WP-50X, DP-25X, DP-150X, DP-05C: ,  the default password for each operator is equal to the corresponding 
number (for example, for Operator1 the password is "1") . FMP-350X, FMP-55X, FP-700X :  the default password for each operator is 
“0000”
NSale - Unique sale number (21 chars "LLDDDDDD-CCCC-DDDDDDD", L[A-Z], C[0-9A-Za-z], 
D[0-9] ) 
TillNmb - Number of point of sale from 1...99999; 
Invoice - If this parameter has value 'I' it opens an invoice receipt. If left blank it opens fiscal receipt; 
Answer: 
{ErrorCode}<SEP>{SlipNumber}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
SlipNumber - Current slip number (1...9999999); 
Command: 49 (31h) Registration of sale 
Parameters of the command: 
Syntax 1:
{PluName}<SEP>{TaxCd}<SEP>{Price}<SEP>{Quantity}<SEP>{DiscountType}<SEP>{DiscountValue}<S
EP>{Department}<SEP>
Syntax 2:
{PluName}<SEP>{TaxCd}<SEP>{Price}<SEP>{Quantity}<SEP>{DiscountType}<SEP>{DiscountValue}<S
EP>{Department}<SEP>{Unit}<SEP>
Mandatory parameters: PluName, TaxCd, Price 
10


# Page 11

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
PluName - Name of product, up to 72 characters not empty string; 
TaxCd - Tax code;
'1' - vat group A; 
'2' - vat group B; 
'3' - vat group C; 
'4' - vat group D; 
'5' - vat group E; 
'6' - vat group F; 
'7' - vat group G; 
'8' - vat group H; 
Price - Product price, with sign '-' at void operations. Format: 2 decimals; up to *9999999.99 
Department - Number of the department 0..99; If '0' - Without department; 
Optional parameters: Quantity, DiscountType, DiscountValue 
Quantity - Quantity of the product ( default: 1.000 ); Format: 3 decimals; up to *999999.999 
Unit - Unit name, up to 6 characters not empty string; 
!!! Max value of Price * Quantity is *9999999.99. !!!
DiscountType - type of discount.
'0' or empty - no discount; 
'1' - surcharge by percentage; 
'2' - discount by percentage; 
'3' - surcharge by sum; 
'4' - discount by sum; If DiscountType is non zero, DiscountValue have to contain value. The 
format must be a value with two decimals. 
DiscountValue - value of discount.
a number from 0.01 to 9999999.99 for sum operations; 
a number from 0.01 to 99.99 for percentage operations; 
Note
If DiscountType is zero or empty, parameter DiscountValue must be empty.
Answer: 
{ErrorCode}<SEP>{SlipNumber}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
SlipNumber - Current slip number (1...9999999); 
Command: 50 (32h) Return the active VAT rates 
Parameters of the command: 
none
Answer: 
{ErrorCode}<SEP>{nZreport}<SEP>{TaxA}<SEP>{TaxB}<SEP>{TaxC}<SEP>{TaxD}<SEP>{TaxE}<SEP
>{TaxF}<SEP>{TaxG}<SEP>{TaxH}<SEP>{EntDate}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0;
nZreport - Number of first Z report;
TaxX - Value of Tax group X (0.00...99.99 taxable,100.00=disabled);
EntDate - Date of entry ( format DD-MM-YY );
11


# Page 12

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
Command: 51 (33h) Subtotal 
Parameters of the command: 
{Print}<SEP>{Display}<SEP>{DiscountType}<SEP>{DiscountValue}<SEP>
Optional parameters:
Print - print out;
'0' - default, no print out; 
'1' - the sum of the subtotal will be printed out; 
Display - Show the subtotal on the client display. Default: 0;
'0' - No display; 
'1' - The sum of the subtotal will appear on the display; 
Note: The option is not used on FMP-350X and FMP-55X; 
DiscountType - type of discount.
'0' or empty - no discount; 
'1' - surcharge by percentage; 
'2' - discount by percentage; 
'3' - surcharge by sum; 
'4' - discount by sum; If {DiscountType} is non zero, {DiscountValue} have to contain value. 
The format must be a value with two decimals. 
DiscountValue - value of discount.
a number from 0.01 to 21474836.47 for sum operations; 
a number from 0.01 to 99.99 for percentage operations; 
Note
If DiscountType is zero or empty, parameter DiscountValue must be empty.
Answer: 
{ErrorCode}<SEP>{SlipNumber}<SEP>{Subtotal}<SEP>{TaxA}<SEP>{TaxB}<SEP>{TaxC}<SEP>{TaxD
}<SEP>{TaxE}<SEP>{TaxF}<SEP>{TaxG}<SEP>{TaxH}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
SlipNumber - Current slip number (1...9999999); 
Subtotal - Subtotal of the receipt ( 0.00...9999999.99 or 0...999999999 depending dec point position ); 
TaxX - Recepts turnover by vat groups ( 0.00...9999999.99 or 0...999999999 depending dec point 
position ); 
Command: 53 (35h) Payments and calculation of the total sum (TOTAL) 
Parameters of the command: 
Syntax 1: 
{PaidMode}<SEP>{Amount}<SEP>{Type}<SEP>
Mandatory parameters:
PaidMode - Type of payment;
'0' - cash;
'1' - credit card;
'2' - debit card;
'3' - other pay#3
'4' - other pay#4
'5' - other pay#5
12


# Page 13

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
Amount - Amount to pay ( 0.00...9999999.99 or 0...999999999 depending dec point position );
Optional parameters (with PinPad connected):
Type - Type of card payment. Only for payment with debit card;
'1' - with money;
'12'- with points from loyal scheme;
Syntax 2: 
{PaidMode}<SEP>{Amount}<SEP>{Change}<SEP>
PaidMode - Type of payment;
'6' - Foreign currency
Amount - Amount to pay ( 0.00...9999999.99 or 0...999999999 depending dec point position );
Change - Type of change. Only if PaidMode = '6';
'0' - current currency;
'1' - foreign currency;
Answer: 1 
{ErrorCode}<SEP>{Status}<SEP>{Amount}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0;
Status - Indicates an error;
'D' - The command passed, return when the paid sum is less than the sum of the receipt. The 
residual sum due for payment is returned to Amount;
'R' - The command passed, return when the paid sum is greater than the sum of the receipt. A 
message “CHANGE” will be printed out and the change will be returned to Amount;
Amount - The sum tendered ( 0.00...9999999.99 or 0...999999999 depending dec point position );
Answer 2 - for payment with pinpad when transaction may be successful in pinpad, but unsuccessful in fiscal 
device: 
{ErrorCode}<SEP>{Sum}<SEP>{CardNum}<SEP>
ErrorCode -111560;
Sum - Sum from last transaction in cents;
CardNum - Last digits from card number;
Answer 3 - for payment with pinpad when error from pinpad occured: 
{ErrorCode}<SEP>
ErrorCode - Indicates an error code;
Command: 54 (36h) Printing of a free fiscal text 
Parameters of the command: 
{Text}<SEP>Bold<SEP>Italic<SEP>DoubleH<SEP>Underline<SEP>alignment<SEP>
Mandatory parameters:
Text - text of 0...XX symbols, XX = PrintColumns-2;
Optional parameters:
Bold - flag 0 or 1, 1 = print bold text; empty field = normal text;
Italic - flag 0 or 1, 1 = print italic text; empty field = normal text;
DoubleH - flag 0 or 1, 1 = print double height text; empty field = normal text;
Underline - flag 0 or 1, 1 = print underlined text; empty field = normal text;
13


# Page 14

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
alignment - 0, 1 or 2. 0=left alignment, 1=center, 2=right; empty field = left alignment;
Answer: 
{ErrorCode}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0;
Command: 55 (37h) Pinpad commands 
Parameters of the command: 
{Option}<SEP>{Parameters}<SEP>
Mandatory parameters:
Option - Option for execution.
'1' - Void;
If pinpad is configured for Borica:
Syntax: 
{Option}<SEP>{PayType}<SEP>{Amount}<SEP>{RRN}<SEP>{AC}<SEP>
Mandatory parameters:
PayType - Type of payment: 7 - Return with money, 13 - Return with points from loyal 
scheme;
Amount - The amount of the transaction;
RRN - RRN of the transaction(12 digits max);
AC - AC of the transaction(6 digits max);
If pinpad is configured for UBB:
Syntax: 
{Option}<SEP>{PayType}<SEP>{Amount}<SEP>{Number}<SEP>
Mandatory parameters:
PayType - Type of payment: 16 - Return with AC number, 17 - Return with receipt 
number;
Amount - The amount of the transaction;
Number - depent on PayType( 16 - AC number, 17 - receipt number )
If pinpad is configured for DSK:
Syntax: 
{Option}<SEP>{PayType}<SEP>{Amount}<SEP>
Mandatory parameters:
PayType - Type of payment: 16 - Return with money;
Amount - The amount of the transaction;
Syntax: 
{Option}<SEP>{PayType}<SEP>
Mandatory parameters:
PayType - Type of payment: 17 - Void last document;
14


# Page 15

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
'2' - Copy of last document;
Syntax: 
{Option}<SEP>
'3' - Copy of document by type;
Syntax: 
{Option}<SEP>{Type}<SEP>{Number}<SEP>
Mandatory parameters:
Type - 1 - RRN, 2 - AC, 3 - Number of the transaction;
Number - depends on Type( RRN - 12 digits max, AC - 6 digits max, Number - 6 digits 
max );
'4' - Copy of all documents;
Syntax: 
{Option}<SEP>
'5' - End of day from Pinpad;
Syntax: 
{Option}<SEP>
'6' - Report from pinpad;
Syntax: 
{Option}<SEP>
'7' - Full report from pinpad;
Syntax: 
{Option}<SEP>
'8' - Enter date and time for Pinpad;
Syntax: 
{Option}<SEP>{DateTime}<SEP>
Mandatory parameters:
DateTime - Date and time in format: "DD-MM-YY hh:mm:ss DST";
DD - Day;
MM - Month;
YY - Year;
hh - Hour;
mm - Minute;
ss - Second;
DST - Text "DST" if exist time is Summer time;
'9' - Check connection with Pinpad;
Syntax: 
{Option}<SEP>
'10' - Check connection with server;
Syntax: 
{Option}<SEP>
'11' - Loyalty balance;
Syntax: 
15


# Page 16

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
{Option}<SEP>
'12' - Get update;
Syntax: 
{Option}<SEP>
'13' - Used when command 53( paying with pinpad ) and command 55 ( option 14 ) returns error 
along with sum and last digits of card number
Syntax: 
{Option}<SEP>{Operation}<SEP>
Mandatory parameters:
Operation - Operation for execution;
'1' - Print receipt;
'2' - Void transaction from pinpad;
'14' - Make sale from pinpad, without fiscal receipt;
Syntax: 
{Option}<SEP>{Amount}<SEP>
Mandatory parameters:
Amount - Amount for sale;
'15' - Print receipt for pinpad after succesfull transaction. Must be executed after command 
53( when paying with pinpad ) and after command 56( when paying with pinpad );
Syntax: 
{Option}<SEP>
Answer 1 - for options from 1 to 13 inclusive, and option 15: 
{ErrorCode}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0;
Answer 2 - for option 14, when command passed: 
{ErrorCode}<SEP>{AC}<SEP>{CardData}<SEP>{CardNumber}<SEP>{MIDNumber}<SEP>{RRN}
<SEP>{TIDNumber}<SEP>{TransAmount}<SEP>{TransDate}<SEP>{TransTime}<SEP>{TransNum
ber}<SEP>{TransStatus}<SEP>{TransType}<SEP>{FulLResponseCode}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0;
AC - Authorization code for transaction;
CardData - Type of card payment( unknown: -1, chip: 0, contactless: 1, magnetic stripe: 2, 
manually: 3 );
CardNumber - Card number;
MIDNumber - Merchant ID;
RRN - RRN number for transaction;
TIDNumber - Terminal ID;
TransAmount - Transaction amount;
TransDate - Transaction date;
TransTime - Transaction time;
TransNumber - Transaction number;
TransStatus - Transaction status( approved: 0, declined: 1, error: 2 );
TransType - Transaction type;
FulLResponseCode  - Complete response code;
Answer 3 - for option 14 when command did not pass and the error is from pinpad: 
{ErrorCode}<SEP>
ErrorCode - Indicates an error code;
16


# Page 17

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
Answer 4 - for option 14 when transaction may be successful in pinpad, but unsuccessful in fiscal 
device: 
{ErrorCode}<SEP>{Sum}<SEP>{CardNum}<SEP>
ErrorCode -111560;
Sum - Sum from last transaction in cents;
CardNum - Last digits from card number;
Options: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14 can be executed only when receipt is closed.
Option 13 can be executed only when receipt is open.
Option 15 can be executed in both ways.
Command: 56 (38h) Close fiscal receipt 
Parameters of the command: 
none
Answer: 
{ErrorCode}<SEP>{SlipNumber}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0;
SlipNumber - Current slip number (1...9999999);
Command: 57 (39h) Enter and print invoice data 
Parameters of the command: 
{Seller}<SEP>{Receiver}<SEP>{Buyer}<SEP>{Address1}<SEP>{Address2}<SEP>{TypeTAXN}<SEP>{T
AXN}<SEP>{VATN}<SEP>
Mandatory parameters:{TypeTAXN} ,{TAXN}, {VATN}
TypeTAXN - Type of client's tax number. 0-BULSTAT; 1-EGN; 2-LNCH; 3-service number
TAXN - Client's tax number. ascii string of digits 8...13 Optional parameters:
VATN - VAT number of the client. 10...14 symbols
Seller - Name of the seller; 36 symbols max; if left blank prints empty space for hand-writing
Receiver - Name of the receiver; 36 symbols max; if left blank prints empty space for hand-writing
Buyer - Name of the buyer; 36 symbols max; if left blank prints empty space for hand-writing
Address1 - First line of the address; 36 symbols max; if left blank prints empty space for hand-writing
Address2 - Second line of the address; 36 symbols max; if left blank prints empty space for hand-
writing
Answer: 
{ErrorCode}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0;
Command: 58 (3Ah) Registering the sale of a programmed item 
Parameters of the command: 
{PluCode}<SEP>{Quantity}<SEP>{Price}<SEP>{DiscountType}<SEP>{DiscountValue}<SEP>
Mandatory parameters: PluCode 
17


# Page 18

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
PluCode: The code of the item. from 1 to MAX_PLU. MAX_PLU: ECR-100000, Printer-3000;
Optional parameters: Quanity, DiscountType, DiscountValue 
Quantity - Quantity of the product ( default: 1.000 ); Format: 3 decimals; up to *999999.999
Note
!!! Max value of Price * Quantity is *9999999.99. !!!
Price - Product price. Format: 2 decimals; up to *9999999.99 
DiscountType - type of discount.
'0' or empty - no discount; 
'1' - surcharge by percentage; 
'2' - discount by percentage; 
'3' - surcharge by sum; 
'4' - discount by sum; 
DiscountValue - value of discount.
a number from 0.01 to 9999999.99 for sum operations; 
a number from 0.01 to 100.00 for percentage operations; 
Note
If DiscountType is zero or empty, this parameter must be empty. 
Void operations are made by placing '-' before PluCode ! In order to make void operation 
the Price parameter must be the same as the price at which the item was sold.
Answer: 
{ErrorCode}<SEP>{SlipNumber}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
SlipNumber - Current slip number (1...9999999); 
Command: 60 (3Ch) Cancel fiscal receipt 
Parameters of the command: 
none
Answer: 
{ErrorCode}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0;
Command: 61 (3Dh) Set date and time 
Parameters of the command: 
{DateTime}<SEP>
Mandatory parameters:
DateTime - Date and time in format: "DD-MM-YY hh:mm:ss DST";
DD - Day;
MM - Month;
YY - Year;
hh - Hour;
mm - Minute;
18


# Page 19

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
ss - Second;
DST - Text "DST" if exist time is Summer time;
Answer: 
{ErrorCode}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0;
Command: 62 (3Eh) Read date and time 
Parameters of the command: 
none
Answer: 
{ErrorCode}<SEP>{DateTime}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0;
DateTime - Date and time in format: "DD-MM-YY hh:mm:ss DST";
DD - Day;
MM - Month;
YY - Year;
hh - Hour;
mm - Minute;
ss - Second;
DST - Text "DST" if exist time is Summer time;
Command: 63 (3Fh) Show current date and time on the external display 
Parameters of the command: 
none
Answer: 
{ErrorCode}<SEP>{DateTime}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
DateTime - Date and time in format: "DD-MM-YY hh:mm:ss DST";
DD - Day; 
MM - Month; 
YY - Year; 
hh - Hour; 
mm - Minute; 
ss - Second; 
DST - Text "DST" if exist time is Summer time; 
Note: The command is not used on FMP-350X and FMP-55X; 
Command: 64 (40h) Information on the last fiscal entry 
Parameters of the command: 
19


# Page 20

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
{Type}<SEP>
Type - Type of returned data. Default: 0;
0 - Turnover on TAX group; 
1 - Amount on TAX group; 
2 - Storno turnover on TAX group; 
3 - Storno amount on TAX group; 
Answer: 
{ErrorCode}<SEP>{nRep}<SEP>{SumA}<SEP>{SumB}<SEP>{SumC}<SEP>{SumD}<SEP>{SumE}<SE
P>{SumF}<SEP>{SumG}<SEP>{SumH}<SEP>{Date}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
nRep - Number of report 1...3650; 
SumX - Depend on Type. X is the letter of TAX group ( 0.00...9999999.99 or 0...999999999 depending 
dec point position ); 
Date - Date of fiscal record in format DD-MM-YY; 
Command: 65 (41h) Information on daily taxation 
Parameters of the command: 
{Type}<SEP>
Type - Type of returned data. Default: 0;
0 - Turnover on TAX group; 
1 - Amount on TAX group; 
2 - Storno turnover on TAX group; 
3 - Storno amount on TAX group; 
Answer: 
{ErrorCode}<SEP>{nRep}<SEP>{SumA}<SEP>{SumB}<SEP>{SumC}<SEP>{SumD}<SEP>{SumE}<SE
P>{SumF}<SEP>{SumG}<SEP>{SumH}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
nRep - Number of report (1...3650); 
SumX - Depend on Type. X is the letter of TAX group ( 0.00...9999999.99 or 0...999999999 depending 
dec point position ); 
Command: 66 (42h) Set invoice interval 
Parameters of the command: 
Syntax 1:
{End}<SEP>
If the current invoice counter didn't reached the end of the interval.
Syntax 2:
{Start}<SEP>{End}<SEP>
If the current invoice counter have reached the end of the interval.
Syntax 3:
20


# Page 21

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
       none – read current values .
Start - The starting number of the interval. Max 10 digits (1...9999999999).
End - The ending number of the interval. Max 10 digits (1...9999999999).
Answer: 
{ErrorCode}<SEP>{Start}<SEP>{End}<SEP>{Current}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0;
Start - The current starting value of the interval (1...9999999999)
End - The current ending value of the interval (1...9999999999)
Current - The current invoice receipt number (1...9999999999)
Command: 68 (44h) Number of remaining entries for Z-reports in FM 
Parameters of the command: 
none
Answer: 
{ErrorCode}<SEP>{ReportsLeft}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0;
ReportsLeft - The number of remaining entries for Z-reports in FM (1...1825 or 3650).
Command: 69 (45h) Reports 
Parameters of the command: 
{ReportType}<SEP>
Mandatory parameters:
ReportType - Report type;
'X' - X report; Answer(1) 
'Z' - Z report; Answer(1) 
'D' - Departments report; Answer(2) 
'G' - Item groups report; Answer(2) 
Answer: 
{ErrorCode}<SEP>{nRep}<SEP>{TotA}<SEP>{TotB}<SEP>{TotC}<SEP>{TotD}<SEP>{TotE}<SEP>{To
tF}<SEP>{TotG}<SEP>{TotH}<SEP>{StorA}<SEP>{StorB}<SEP>{StorC}<SEP>{StorD}<SEP>{StorE}<
SEP>{StorF}<SEP>{StorG}<SEP>{StorH}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
nRep - Number of Z-report (1...3650); 
TotX - Total sum accumulated by TAX group X - sell operations ( 0.00...9999999.99 or 0...999999999 
depending dec point position ); 
StorX - Total sum accumulated by TAX group X - storno operations ( 0.00...9999999.99 or 
0...999999999 depending dec point position ); 
Answer(2): 
{ErrorCode}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
21


# Page 22

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
Command: 70 (46h) Cash in and Cash out operations 
Parameters of the command: 
{Type}<SEP>{Amount}<SEP>
Mandatory parameters:
Type - type of operation;
'0' - cash in;
'1' - cash out;
'2' - cash in - (foreign currency);
'3' - cash out - (foreign currency); Optional parameters:
Amount - the sum ( 0.00...9999999.99 or 0...999999999 depending dec point position ); If Amount=0, 
the only Answer is returned, and receipt does not print.
Answer: 
{ErrorCode}<SEP>{CashSum}<SEP>{CashIn}<SEP>{CashOut}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0;
CashSum - cash in safe sum ( 0.00...9999999.99 or 0...999999999 depending dec point position );
CashIn - total sum of cash in operations ( 0.00...9999999.99 or 0...999999999 depending dec point 
position );
CashOut - total sum of cash out operations ( 0.00...9999999.99 or 0...999999999 depending dec point 
position );
Command: 71 (47h) General information, modem test 
Parameters of the command: 
{InfoType}<SEP>
Optional parameters:
InfoType - Type of the information printed. Default: 0;
'0' - General diagnostic information about the device; 
'1' - test of the modem; 
'2' - general information about the connection with NRA server;
Answer(2) 
'3' - print information about the connection with NRA server;
'4' - test of the LAN interface if present; 
'6' - test of the SD card performance; 
'9' - test of the Ble module ( if present ); 
'10' - test of the modem without PPP connection; 
'11' - Send all unsent documents (command execution is  accepted only once in every 5 minutes ); 
Answer(1): 
{ErrorCode}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
Answer(2):
{ErrorCode}<SEP>{LastDate}<SEP>{NextDate}<SEP>{Zrep}<SEP>{ZErrZnum}<SEP>{ZErrCnt}<SEP>{
ZErrNum}<SEP>{SellErrnDoc}<SEP>{SellErrCnt}<SEP>{SellErrStatus}<SEP>SellNumber<SEP>SellDate<
SEP>LastErr<SEP>RemMinutes<SEP>
22


# Page 23

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
LastDate - Last connection to the server; 
NextDate - Next connection to the server; 
Zrep - Last send Z report; 
ZErrZnum - Number of Z report with error; 
ZErrCnt - Sum of all errors for Z reports; 
ZErrNum - Error number from the server; 
SellErrnDoc - Number of sell document with error; 
SellErrCnt - Sum of all errors for sell documents; 
SellErrStatus - Error number from the server; 
SellNumber - Last received document number from the server; 
SellDate - The date and time of last received document from the server; 
LastErr- Last error from the server; 
RemMinutes- Remaining minutes until next GetDeviceInfo request; 
Command: 72 (48h) Fiscalization 
Parameters of the command: 
{SerialNumber}<SEP>{TAXnumber}<SEP>
Mandatory parameters:
SerialNumber - Serial Number ( Two letters and six digits: XX123456);
TAXnumber - TAX number (max 13 characters);
Answer: 
{ErrorCode}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0;
Command: 74 (4Ah) Reading the Status 
Parameters of the command: 
{Option}<SEP>
Optional parameters:
Option - Type of information to return;
'0' - current receipt status; Answer(2) 
'1' - Fiscal QRcode string - the contents of the QR code printed in the last fiscal document; 
Answer(3) 
Answer(1): 
{ErrorCode}<SEP>{StatusBytes}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
StatusBytes - Status Bytes ( See the description of the status bytes ). 
Answer(2): 
{ErrorCode}<SEP>{PrintBufferStatus}<SEP>{ReceiptStatus}<SEP>{Number}<SEP>{QRamount}<SEP>{Q
Rnumber}<SEP>{QRdatetime}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
23


# Page 24

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
PrintBufferStatus  - 0- empty buffer, no lines pending, 1-buffer is not empty; 
ReceiptStatus - Status of the current receipt.
0 - Receipt is closed; 
1 - Normal receipt is open; 
2 - Storno receipt is open. Reason "mistake by operator"; 
3 - Storno receipt is open. Reason "refund"; 
4 - Storno receipt is open. Reason "tax base reduction"; 
5 - standart non-fiscal receipt is open; 
Number - The number of the current or the last receipt (1...9999999); 
QRamount - Fiscal QRcode - the amount of the last fiscal receipt; 
QRnumber - Fiscal QRcode - the slip number of the last fiscal receipt (1...9999999); 
QRdatetime - Fiscal QRcode - the date and time of the last fiscal receipt; 
Answer(3): 
{ErrorCode}<SEP>{QRCodeString}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
QRCodeString - the Fiscal QRcode string; 
Command: 76 (4Ch) Status of the fiscal transaction 
Parameters of the command: 
none
Answer: 
{ErrorCode}<SEP>{IsOpen}<SEP>{Number}<SEP>{Items}<SEP>{Amount}<SEP>{Payed}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
IsOpen 
0 - Receipt is closed; 
1 - Normal receipt is open; 
2 - Storno receipt is open. Reason "mistake by operator"; 
3 - Storno receipt is open. Reason "refund"; 
4 - Storno receipt is open. Reason "tax base reduction"; 
5 - standard non-fiscal receipt is open; 
Number - The number of the current or the last receipt (1...9999999); 
Items - number of sales registered on the current or the last fiscal receipt (0...9999999); 
Amount - The sum from the current or the last fiscal receipt ( 0.00...9999999.99 or 0...999999999 
depending dec point position ); 
Payed - The sum payed for the current or the last receipt ( 0.00...9999999.99 or 0...999999999 
depending dec point position ); 
Command: 80 (50h) Play sound 
Parameters of the command: 
{Hz}<SEP>{mSec}<SEP>
Mandatory parameters:
Hz - Frequency (0...65535);
24


# Page 25

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
mSec - Time in milliseconds (0...65535);
Answer: 
{ErrorCode}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0;
Command: 83 (53h) Programming of VAT rates 
Parameters of the command: 
{TaxA}<SEP>{TaxB}<SEP>{TaxC}<SEP>{TaxD}<SEP>{TaxE}<SEP>{TaxF}<SEP>{TaxG}<SEP>{TaxH
}<SEP>{decimal_point}<SEP>
Mandatory parameters:
TaxX - Value of VAT rate X;
0.00...99.99 - enabled;
100.00 - disabled;
decimal_point - value: 0 or 2( if decimal_point = 0 - work with integer prices. If decimal_point = 2 - 
work with fract prices ); 
Note
When changing decimal_point is necessart to restart the printer so the correct values indicate on 
the client display 
Answer: 
{ErrorCode}<SEP>{RemainingChanges}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0;
RemainingChanges  - number of remaining changes (1...30);
Command: 84 (54h) Printing of barcode 
Parameters of the command:
Syntax 1: {Type}<SEP>{Data}<SEP>
Syntax 2: {Type}<SEP>{Data}<SEP>{QRcodeSize}<SEP>
Mandatory parameters:
Type - Type of barcode;
'1' - EAN8 barcode. Data must contain only 8 digits; Use Syntax 1;
'2' - EAN13 barcode. Data must contain only 13 digits; Use Syntax 1;
'3' - Code128 barcode. Data must contain symbols with ASCII codes between 32 and 127. Data 
length is between 3 and 31 symbols;  Use Syntax 1;
'4' - QR code. Data must contain symbols with ASCII codes between 32 and 127. Data length is 
between 3 and 279 symbols;  Use Syntax 2;
'5' - Interleave 2of5 barcode. Data must contain only digits, from 3 to 22 chars;  Use Syntax 1;
'6' - PDF417 truncated Data must contain symbols with ASCII codes between 32 and 127. Data 
length is between 3 and 400 symbols;  Use Syntax 1;
'7' - PDF417 normal Data must contain symbols with ASCII codes between 32 and 127. Data 
length is between 3 and 400 symbols;  Use Syntax 1;
Data - Data of the barcode; Length of Data depents on the type of the barcode. 
Optional parameters:
25


# Page 26

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
QRcodeSize - Dots multiplier ( 3...10 ) for QR barcodes and PDF417 barcodes. Default: 4; 
Answer: 
{ErrorCode}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0;
Command: 86 (56h) Date of the last fiscal record 
Parameters of the command: 
none
Answer: 
{ErrorCode}<SEP>{DateTime}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0;
DateTime - The date and the time of the last fiscal record in format: DD-MM-YYYY hh:mm:ss;
Command: 87 (58h) Get item groups information 
Parameters of the command: 
{ItemGroup}<SEP>
Optional parameters:
ItemGroup - Number of item group; If ItemGroup is empty - item group report;
Answer: 
{ErrorCode}<SEP>{TotSales}<SEP>{TotSum}<SEP>{Name}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0;
TotSales - Number of sales for this item group for day;
TotSum - Accumulated sum for this item group for day;
Name - Name of item group;
Command: 88 (58h) Get department information 
Parameters of the command: 
{Department}<SEP>
Optional parameters:
Department - Number of department (1...99); If Department is empty - department report; 
Answer: 
{ErrorCode}<SEP>{TaxGr}<SEP>{Price}<SEP>{TotSales}<SEP>{TotSum}<SEP>{STotSales}<SEP>{STot
Sum}<SEP>{Name}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
TaxGr - Tax group of department; 
Price - Price of department; 
26


# Page 27

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
TotSales - Number of sales for this department for day; 
TotSum - Accumulated sum for this department for day; 
STotSales - Number of storno operations for this department for day; 
STotSum - Accumulated sum from storno operations for this department for day; 
Name - Name of the department; 
Command: 89 (59h) Test of Fiscal Memory 
Parameters of the command: 
{Write}<SEP>
Optional parameters:
Write - Write test. Default: 0;
0 - Read test.
1 - Write and read test;
Answer: 
{ErrorCode}<SEP>{Records}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0;
Records - Number of records left (0...16).
Command: 90 (5Ah) Diagnostic information
Parameters of the command:   
Syntax 1: {Param}<SEP>
Optional parameters:
none - Diagnostic information without firmware checksum;
Answer(1) 
'1' - Diagnostic information with firmware checksum;
Answer(1) 
Syntax 2: {Param}
Optional parameters:
none - Diagnostic information without firmware checksum;
Answer(2) 
'1' -Diagnostic information with firmware checksum;
Answer(2) 
Answer(1):    {ErrorCode}<SEP>{Name}<SEP>{FwRev}<SEP>{FwDate}<SEP>
    {FwTime}<SEP>{Checksum}<SEP>{Sw}<SEP>{SerialNumber}<SEP>{FMNumber}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
Name - Device name ( up to 32 symbols ). 
FwRev - Firmware version. 6 symbols; 
FwDate - Firmware date DDMMMYY. 7 symbols; 
FwTime - Firmware time hhmm. 4 symbols. 
Checksum - Firmware checksum. 4 symbols; 
Sw - Switch from Sw1 to Sw8. 8 symbols (not used at this device, always 00000000); 
SerialNumber - Serial Number ( Two letters and six digits: XX123456); 
{FMNumber} –Fiscal memory number (8 digits)
Answer(2):     {Name},{FwRev}{Sp}{FwDate}{Sp}{FwTime},{Checksum},{Sw},
    {SerialNumber},{FMNumber}
27


# Page 28

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
Name - Device name ( up to 32 symbols ). 
FwRev - Firmware version. 6 symbols; 
Sp - Space. 1 symbol; 
FwDate - Firmware date DDMMMYY. 7 symbols; 
FwTime - Firmware time hhmm. 4 symbols. 
Checksum - Firmware checksum. 4 symbols; 
Sw - Switch from Sw1 to Sw8. 8 symbols; 
SerialNumber - Serial Number ( Two letters and six digits: XX123456); 
{FMNumber} –Fiscal memory number (8 digits)
Command: 91 (5Bh) Programming of Serial number and FM number 
Parameters of the command: 
{SerialNumber}<SEP>{FMnumber}<SEP>
Mandatory parameters:
SerialNumber - Serial Number ( Two letters and six digits: XX123456);
FMnumber - Fiscal Memory Number (Eight digits);
Answer: 
{ErrorCode}<SEP>{Country}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0;
Country - name of the country ( up to 32 symbols );
Command: 92 (5Ch) Printing of separating line 
Parameters of the command: 
{Type}<SEP>
Mandatory parameters:
Type - Type of the separating line.
'1' - Separating line with the symbol '-'; 
'2' - Separating line with the symbols '-' and ' '; 
'3' - Separating line with the symbol '='; 
'4' - Print fixed text "НЕ СЕ ДЪЛЖИ ПЛАЩАНЕ"; 
Answer: 
{ErrorCode}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
Command: 94 (5Еh) Fiscal memory report by date 
Parameters of the command: 
{Type}<SEP>{Start}<SEP>{End}<SEP>
Mandatory parameters:
28


# Page 29

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
Type - 0 - short; 1 - detailed;
Optional parameters:
Start - Start date. Default: Date of fiscalization ( format DD-MM-YY );
End - End date. Default: Current date ( format DD-MM-YY );
Answer: 
{ErrorCode}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0;
Command: 95 (5Fh) Fiscal memory report by number of Z-report 
Parameters of the command: 
{Type}<SEP>{First}<SEP>{Last}<SEP>
Mandatory parameters:
Type - 0 - short; 1 - detailed; 
Optional parameters:
First - First Z-report in the period. Default: 1; 
Last - Last Z-report in the period. Default: Number of last Z-report; 
Answer: 
{ErrorCode}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0;
Command: 96 (60h) Set Software Password. 
Parameters of the command: 
Syntax 1: 
{SoftPassword}<SEP>
Mandatory parameters:
SoftPassword - Software Password (max 16 characters); 
Syntax 2: 
{OldPasw}<SEP>{NewPasw}<SEP>
Mandatory parameters:
OldPasw - Value of the old password. Max 16 characters. The default password is empty string; 
NewPasw - Value of the new password. Max 16 characters. 
Answer: 
{ErrorCode}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0;
Command: 98 (62h) Programming of TAX number 
Parameters of the command: 
29


# Page 30

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
{TAXnumber}<SEP>
Mandatory parameters:
TAXnumber - TAX number (max 13 characters);
Answer: 
{ErrorCode}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0;
Command: 99 (63h) Reading the programmed TAX number 
Parameters of the command: 
none
Answer: 
{ErrorCode}<SEP>{TAXnumber}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0;
TAXnumber - TAX number (max 13 characters);
Command: 100 (64h) Reading an error 
Parameters of the command: 
{Code}<SEP>
Mandatory parameters:
Code - Code of the error(negative number);
Answer: 
{ErrorCode}<SEP>{Code}<SEP>{ErrorMessage}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0;
Code - Code of the error, to be explained;
ErrorMessage - Explanation of the error in Code;
Command: 101 (65h) Set operator password 
Parameters of the command: 
{OpCode}<SEP>{OldPwd}<SEP>{NewPwd}<SEP>
Mandatory parameters:
OpCode - Operator number from 1...30;
NewPwd - Operator password, ascii string of digits. Lenght from 1...8;
Optional parameters:
OldPwd - Operator old password or administrator (oper29 & oper30) password. Can be blank if service 
jumper is on.
Answer: 
30


# Page 31

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
{ErrorCode}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0;
Command: 103 (67h) Information for the current receipt 
Parameters of the command: 
none
Answer: 
{ErrorCode}<SEP>{SumVATA}<SEP>{SumVATB}<SEP>{SumVATC}<SEP>{SumVATD}<SEP>{SumV
ATE}<SEP>{SumVATF}<SEP>{SumVATG}<SEP>{SumVATH}<SEP>{Inv}<SEP>{InvNum}<SEP>fStor
no<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
SumVATx - The current accumulated sum on VATx ( 0.00...9999999.99 or 0...999999999 depending 
dec point position ); 
Inv - '1' if it is expanded receipt; '0' if it is simplified receipt; 
InvNmb - Number of the next invoice (up to 10 digits) 
fStorno - '1' if a storno receipt is open; '0' if it is normal receipt; 
Command: 105 (69h) Report operators 
Parameters of the command: 
{FirstOper}<SEP>{LastOper}<SEP>{Clear}<SEP>
Optional parameters:
FirstOper - First operator. Default: 1 (1...30);
LastOper - Last operator. Default: Maximum operator number (1...30);
Clear - Clear registers for operators. Default: 0;
'0' - Does not clear registers for operators.
'1' - Clear registers for operators.
Answer: 
{ErrorCode}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0;
Command: 106 (6Ah)  Drawer opening 
Parameters of the command: 
{mSec}<SEP>
Optional parameters:
mSec - The length of the impulse in milliseconds. ( 0...65535 )
Answer: 
{ErrorCode}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0;
Note: only for FP-705 
31


# Page 32

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
Command: 107 (6Bh) Defining and reading items 
Parameters of the command: 
{Option}<SEP>{Parameters}<SEP>
Mandatory parameters: Option 
'I' - Items information; 
Syntax: 
{Option}<SEP>
Answer(3) 
'P' - Item programming; 
Syntax1:
{Option}<SEP>{PLU}<SEP>{TaxGr}<SEP>{Dep}<SEP>{Group}<SEP>{PriceType}<SEP>{Price}<
SEP>{AddQty}<SEP>{Quantity}<SEP>{Bar1}<SEP>{Bar2}<SEP>{Bar3}<SEP>{Bar4}<SEP>{Na
me}<SEP>
Syntax2:
{Option}<SEP>{PLU}<SEP>{TaxGr}<SEP>{Dep}<SEP>{Group}<SEP>{PriceType}<SEP>{Price}<
SEP>{AddQty}<SEP>{Quantity}<SEP>{Bar1}<SEP>{Bar2}<SEP>{Bar3}<SEP>{Bar4}<SEP>{Na
me}<SEP>{Unit}<SEP>
Mandatory parameters: 
PLU - Item number ( For ECRs 1...100000; For FPs 1...3000 ); 
TaxGr - VAT group (letter 'A'...'H' or cyrillic 'А'...'З'); 
Dep - Department ( 0...99 ); 
Group - Stock group (1...99); 
PriceType - Price type ('0' - fixed price, '1' - free price, '2' - max price) ; 
Price - Price ( 0.00...9999999.99 or 0...999999999 depending dec point position ); 
Quantity - Stock quantity ( 0.001...99999.999 ); 
Name - Item name (up to 72 symbols); 
Unit - Measurement unit 0 - 19; 
Optional parameters: 
AddQty - A byte with value 'A', 
BarX - Barcode X ( up to 13 digits ); 
Answer(1) 
'A' - Change of the available quantity for item; 
Syntax: 
{Option}<SEP>{PLU}<SEP>{Quantity}<SEP>
Mandatory parameters: 
PLU - Item number ( For ECRs 1...100000; For FPs 1...3000 ); 
Quantity - Stock quantity ( 0.001...99999.999 ); 
Answer(1) 
'D' - Item deleting; 
Syntax: 
{Option}<SEP>{firstPLU}<SEP>{lastPLU}<SEP>
Mandatory parameters: 
firstPLU - First item to delete ( For ECRs 1...100000; For FPs 1...3000 ). If this parameter has 
value 'A', all items will be deleted ( lastPLU must be empty ); 
Optional parameters: 
lastPLU - Last item to delete ( For ECRs 1...100000; For FPs 1...3000 ). Default: firstPLU; 
32


# Page 33

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
Answer(1) 
'R' - Reading item data; 
Syntax: 
{Option}<SEP>{PLU}<SEP>
Mandatory parameters: 
PLU - Item number ( For ECRs 1...100000; For FPs 1...3000 ); 
Answer(2) 
'F' - Returns data about the first found programmed item; 
Syntax: 
{Option}<SEP>{PLU}<SEP>
Optional parameters: 
PLU - Item number ( For ECRs 1...100000; For FPs 1...3000 ). Default: 1; 
Answer(2) 
'L' - Returns data about the last found programmed item; 
Syntax: 
{Option}<SEP>{PLU}<SEP>
Optional parameters: 
PLU - Item number ( For ECRs 1...100000; For FPs 1...3000 ). Default: For ECRs 100000; For 
FPs 3000; 
Answer(2) 
'N' - Returns data for the next found programmed item;
Syntax: 
{Option}<SEP>
Note
The same command with option 'F' or 'L' must be executed first. This determines whether to get 
next('F') or previous ('L') item.
Answer(2) 
'f' - Returns data about the first found item with sales on it; 
Syntax: 
{Option}<SEP>{PLU}<SEP>
Optional parameters: 
PLU - Item number ( For ECRs 1...100000; For FPs 1...3000 ). Default: 1; 
Answer(2) 
'l' - Returns data about the last found item with sales on it; 
Syntax: 
{Option}<SEP>{PLU}<SEP>
Optional parameters: 
PLU - Item number ( For ECRs 1...100000; For FPs 1...3000 ). Default: For ECRs 100000; For 
FPs 3000; 
Answer(2) 
'n' - Returns data for the next found item with sales on it; 
Syntax: 
{Option}<SEP>
Note
The same command with option 'f' or 'l' must be executed first. This determines whether to get 
next('f') or previous ('l') item; Answer(2) 
'X' - Find the first not programmed item; 
Syntax: 
{Option}<SEP>{PLU}<SEP>
Optional parameters: 
PLU - Item number ( For ECRs 1...100000; For FPs 1...3000 ). Default: 1; 
Answer(4) 
33


# Page 34

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
'x' - Find the last not programmed item; 
Syntax: 
{Option}<SEP>{PLU}<SEP>
Optional parameters: 
PLU - Item number ( For ECRs 1...100000; For FPs 1...3000 ). Default: For ECRs 100000; For 
FPs 3000; 
Answer(4) 
Answer(1): 
{ErrorCode}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
Answer(2):
{ErrorCode}<SEP>{PLU}<SEP>{TaxGr}<SEP>{Dep}<SEP>{Group}<SEP>{PriceType}<SEP>{Price}<SE
P>{Turnover}<SEP>{SoldQty}<SEP>{StockQty}<SEP>{Bar1}<SEP>{Bar2}<SEP>{Bar3}<SEP>{Bar4}<S
EP>{Name}<SEP>{ Units}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
PLU - Item number ( For ECRs 1...100000; For FPs 1...3000 ); 
TaxGr - VAT group (letter 'A'...'H' or cyrillic 'А'...'З'); 
Dep - Department ( 0...99 ); 
Group - Stock group (1...99); 
PriceType - Price type ('0' - fixed price, '1' - free price, '2' - max price;) ; 
Price - Price ( 0.00...9999999.99 or 0...999999999 depending dec point position ); 
Turnover - Accumulated amount of the item ( 0.00...9999999.99 or 0...999999999 depending dec point 
position ); 
SoldQty - Sold out quantity ( 0.001...99999.999 ); 
StockQty - Current quantity ( 0.001...99999.999 ); 
BarX - Barcode X ( up to 13 digits ); 
Name - Item name ( up to 72 symbols ); 
Units - Measurement unit 0 - 19; 
Answer(3):
{ErrorCode}<SEP>{Total}<SEP>{Prog}<SEP>{NameLen}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
Total - Total count of the programmable items ( For ECRs: 100000; For FPs: 3000 ); 
Prog - Total count of the programmed items ( For ECRs 0...100000; For FPs 0...3000 ); 
NameLen - Maximum length of item name ( 72 ); 
Answer(4): 
{ErrorCode}<SEP>{PLU}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
PLU - Item number ( For ECRs 1...100000; For FPs 1...3000 ); 
Command: 109 (6Dh) Print duplicate copy of receipt 
Parameters of the command: 
none
Answer: 
{ErrorCode}<SEP>
34


# Page 35

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0;
Command: 110 (6Eh) Additional daily information 
Parameters of the command: 
{Type}<SEP>
Optional parameters:
Type - Type of information. Default: 0;
'0' - Payments (sell operations); 
Answer(1) 
'1' - Payments (storno operations); 
Answer(2) 
'2' - number and sum of sells; 
Answer(3) 
'3' - number and sum of discounts and surcharges; 
Answer(4) 
'4' - number and sum of corrections and annulled receipts; 
Answer(5) 
'5' - number and sum of cash in and cash out operations; 
Answer(6) 
Answer 1: 
{ErrorCode}<SEP>{Pay1}<SEP>{Pay2}<SEP>{Pay3}<SEP>{Pay4}<SEP>{Pay5}<SEP>{Pay6}<SEP>{For
eignPay}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
PayX - Value payed by payment X ( 0.00...9999999.99 or 0...999999999 depending dec point 
position );. 
ForeignPay - Value payed by foreign currency ( 0.00...9999999.99 or 0...999999999 depending dec 
point position );. 
Answer 2: 
{ErrorCode}<SEP>{Pay1}<SEP>{Pay2}<SEP>{Pay3}<SEP>{Pay4}<SEP>{Pay5}<SEP>{Pay6}<SEP>{For
eignPay}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
PayX - Value payed by payment X for return ( 0.00...9999999.99 or 0...999999999 depending dec point 
position );. 
ForeignPay - Value payed by foreign currency ( 0.00...9999999.99 or 0...999999999 depending dec 
point position );. 
Answer 3: 
{ErrorCode}<SEP>{Num}<SEP>{Sum}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
Num - number of clients ( integer number - 0,1,2, .... ); 
Sum - sum of the sells ( 0.00...9999999.99 ) 
Answer 4: 
35


# Page 36

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
{ErrorCode}<SEP>{qSur}<SEP>{sSur}<SEP>{qDis}<SEP>{sDis}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
qSur - number of surcharges;. 
sSur - sum of surcharges;. 
qDis - number of discounts;. 
sDis - sum of discounts;. 
Answer 5: 
{ErrorCode}<SEP>{qVoid}<SEP>{sVoid}<SEP>{qAnul}<SEP>{sAnul}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
qVoid - number of corrections ( integer number - 0,1,2, .... ); 
sVoid - sum of corrections ( 0.00...9999999.99 ); 
qAnul - number of annulled ( integer number - 0,1,2, .... ); 
sAnul - sum of annulled ( 0.00...9999999.99 ); 
Answer 6: 
{ErrorCode}<SEP>{qCashIn1}<SEP>{sCashIn1}<SEP>{qCashOut1}<SEP>{sCashOut1}<SEP>{qCashIn2}
<SEP>{sCashIn2}<SEP>{qCashOut2}<SEP>{sCashOut2}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
qCashIn1 - number of cash in operations ( integer number - 0,1,2, .... ); 
sCashIn1 - sum of cash in operations ( 0.00...9999999.99 ); 
qCashOut1 - number of cash out operations ( integer number - 0,1,2, .... ); 
sCashOut1 - sum of cash out operations ( 0.00...9999999.99 ); 
qCashIn2 - number of cash in operations in alternative currency ( integer number - 0,1,2, .... ); 
sCashIn2 - sum of cash in operations in alternative currency ( 0.00...9999999.99 ); 
qCashOut2 - number of cash out operations in alternative currency ( integer number - 0,1,2, .... ); 
sCashOut2 - sum of cash out operations in alternative currency ( 0.00...9999999.99 ); 
Command: 111 (65h) PLU report 
Parameters of the command: 
{Type}<SEP>{FirstPLU}<SEP>{LastPLU}<SEP>
Mandatory parameters:
Type - Type of report;
o'0' - PLU turnovers;
o'1' - PLU turnovers with clearing;
o'2' - PLU parameters;
o'3' - PLU stock;
Optional parameters:
FirstPLU - First PLU in the report (1...3000). Default: 1;
LastPLU - Last PLU in the report (1...3000). Default: Maximum PLU in the FPr;
Answer: 
{ErrorCode}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0;
36


# Page 37

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
Command: 112 (70h) Information for operator 
Parameters of the command: 
{Operator}<SEP>
Mandatory parameters:
Operator - Number of operator (1...30);
Answer: 
{ErrorCode}<SEP>{Receipts}<SEP>{Total}<SEP>{nDiscount}<SEP>{Discount}<SEP>{nSurcharge}<SEP>
{Surcharge}<SEP>{nVoid}<SEP>{Void}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0;
Receipts - Number of fiscal receipts, issued by the operator (0...65535);
Total - Total accumulated sum ( 0.00...9999999.99 or 0...999999999 depending dec point position );
nDiscount - Number of discounts (0...65535);;
Discount - Total accumulated sum of discounts with sign ( 0.00...9999999.99 or 0...999999999 
depending dec point position );
nSurcharge - Number of surcharges (0...65535);
Surcharge - Total accumulated sum of surcharges with sign( 0.00...9999999.99 or 0...999999999 
depending dec point position );
nVoid - Number of corrections (0...65535);
Void - Total accumulated sum of corrections with sign( 0.00...9999999.99 or 0...999999999 depending 
dec point position );
Command: 116 (74h) Reading FM. 
Parameters of the command: 
{Operation}<SEP>{Address}<SEP>{nBytes}<SEP>
Mandatory parameters:
Operation - type of operation = '0';
Address - Start address 0...FFFFFF ( format ascii-hex ).
nBytes - Number of bytes (1...104)
Answer: 
{ErrorCode}<SEP>{Data}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0;
Data - Data read. Number of bytes is equal to nBytes requested, multiplied by 2;
Command: 122 (7Ah) Printing of a free vertical fiscal text 
Parameters of the command: 
{Text}<SEP>
Mandatory parameters:
Text - text of 0...128 symbols; 
Double-byte control codes: 
37


# Page 38

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
(0Bh 42h ) - Bolds all symbols.
(0Bh 62h ) - Stops the bolding of the symbols.
(0Bh 55h ) - Overlines all symbols.
(0Bh 75h ) - Stops the overlining of the symbols
(0Bh 4Fh ) - Underlines all symbols.
(0Bh 6Fh ) - Stops the underlining of the symbols.
Box drawing symbols: 
(82h) - up right
(84h) - up left
(91h) - down right
(92h) - down left
(93h) - up right + down right
(94h) - up left + down left
(95h) - up left + down right
(96h) - down left + down right
(97h) - up right + down left + up left + down right
(ACh) - vertical line
Answer: 
{ErrorCode}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
Note
All information is automatically printed after XX executions of the command. XX=10 for 2 inch paper, 
XX=16 for 3 inch paper. 
Command: 123 (7Bh)  Device information 
Parameters of the command: 
{Option}[<SEP>]
Mandatory parameters: 
Option - Type of information to return;
'1' - Serial numbers, Header and Tax numbers; Answer(1) 
'2' - Battery and GSM signal status; Answer(2) 
'3' - Last fiscal receipt; Answer(3) 
'4' - Full EJ verify; Answer(4) 
'5' - Battery level; Answer(5) 
Answer(1): 
{ErrorCode}<SEP>{SerialNumber}<SEP>{FiscalNumber}<SEP>{Headerline1}<SEP>{Headerline2}<SEP>{
TAXnumber}<SEP>{Headerline3}<SEP>{Headerline4}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
SerialNumber - Serial number; 
FiscalNumber - FMemory number; 
Headerline1 - Supposed to contain Company name ( up to depending on device's maximum printing 
columns ); 
Headerline2 - Supposed to contain Company address ( up to depending on device's maximum printing 
columns ); 
38


# Page 39

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
Headerline3 - Supposed to contain name of the business premises ( up to depending on device's 
maximum printing columns ); 
Headerline4 - Supposed to contain address of the business premises ( up to depending on device's 
maximum printing columns ); 
TAXnumber 
Answer(2): 
{ErrorCode}<SEP>{MainBattery}<SEP>{RamBattery}<SEP>{Signal}<SEP>{Network}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
MainBattery - Main Battery level in mV; 
RamBattery - Ram Battery level in mV; 
Signal - GSM Signal level in percentage; 
Network - GSM network status. 1-registered, 0-unregistered;
Answer(3):
{ErrorCode}<SEP>{BonFiscal}<SEP>{DateBonFiscal}<SEP>{Znumber}<SEP>{Zdate}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
BonFiscal - Number of last sales receipt in current Z report ( 1...9999 ); 
DateBonFiscal - Date and time of last sales receipt ( format "DD-MM-YYYY hh:mm:ss" ); 
Znumber - Number of last Z-report ( 1..???? ); 
Zdate - Date of last of Z-report ( format "DD-MM-YYYY hh:mm:ss" ); 
Answer(4): 
{ErrorCode}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
Answer(5):
{ErrorCode}<SEP>{MainBattery}<SEP>{ChargeLevel}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
MainBattery - Main Battery level in mV; 
ChargeLevel - Battery charge percentage; 
Command: 124 (7Ch) Search receipt number by period 
Parameters of the command: 
{StartDate}<SEP>{EndDate}<SEP>{DocType}<SEP>
Optional parameters: 
StartDate - Start date and time for searching ( format "DD-MM-YY hh:mm:ss DST" ). Default: Date 
and time of first document; 
EndDate - End date and time for searching ( format "DD-MM-YY hh:mm:ss DST" ). Default: Date and 
time of last document; 
Note
See DateTime format described at the beginning of the document;
DocType - Type of document;
'0' - all types; 
'1' - fiscal receipts; 
'2' - daily Z reports; 
'3' - invoice receipts; 
39


# Page 40

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
'4' - non fiscal receipts; 
'5' - paidout receipts; 
'6' - fiscal receipts - storno; 
'7' - invoice receipts - storno; 
'8' - cancelled receipts ( all voided ); 
'9' - daily X reports; 
'10' - fiscal receipts, invoice receipts, fiscal receipts - storno and invoice receipts - storno; 
Answer: 
{ErrorCode}<SEP>{StartDate}<SEP>{EndDate}<SEP>{FirstDoc}<SEP>{LastDoc}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
StartDate - Start date for searching, see DateTime format described at the beginning of the document; 
EndDate - End date for searching, see DateTime format described at the beginning of the document; 
FirstDoc - First document in the period. For DocType = '2' (1...3650), else (1...99999999); 
LastDoc - Last document in the period. For DocType = '2' (1...3650), else (1...99999999); 
Command: 125 (7Dh) Information from EJ 
Parameters of the command: 
Syntax 1:
{Option}<SEP>{DocNum}<SEP>{RecType}<SEP>
Syntax 2 ( read CSV data):
{Option}<SEP>{FirstDoc}<SEP>{LastDoc}<SEP>
Syntax 3 ( read CSV data):
{Option}<SEP>
Syntax1: Mandatory parameters: 
Option - Type of information;
'0' - Set document to read; Answer(1) 
'1' - Read one line as text. Must be called multiple times to read the whole document; Answer(2) 
'2' - Read as data. Must be called multiple times to read the whole document; Answer(3) 
'3' - Print document; Answer(4) 
Syntax1: Optional parameters: 
DocNum - Number of document (1...9999999). Needed for Option = 0. 
RecType - Document type. Needed for Option = 0.
'0' - all types; 
'1' - fiscal receipts; 
'2' - daily Z reports; 
'3' - invoice receipts; 
'4' - nonfiscal receipts; 
'5' - paidout receipts; 
'6' - fiscal receipts - storno; 
'7' - invoice receipts - storno; 
'8' - cancelled receipts ( all voided ); 
'9' - daily X reports; 
'10' - fiscal receipts, invoice receipts, fiscal receipts - storno and invoice receipts - storno; 
Syntax2: Mandatory parameters: 
Option - Type of information;
'9' - Set document to read; Answer(1) 
40


# Page 41

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
FirstDoc - First document in the period (1...99999999). Number received in response to command 124; 
LastDoc - Last document in the period. (1...99999999). Number received in response to command 124; 
Syntax3: Mandatory parameters: 
Option - Type of information;
'8' - Read as data. Must be called multiple times to read the whole document; Answer(5) 
Answer(1): 
{ErrorCode}<SEP>{DocNumber}<SEP>{RecNumber}<SEP>{Date}<SEP>{Type}<SEP>{Znumber}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
DocNumber - Number of document ( global 1...9999999 ); 
RecNumber - Number of document ( depending "Type" ); 
Date - Date of document, see DateTime format described at the beginning of the document; 
Type - Type of document;
'0' - all types; 
'1' - fiscal receipts; 
'2' - daily Z reports; 
'3' - invoice receipts; 
'4' - non fiscal receipts; 
'5' - paidout receipts; 
'6' - fiscal receipts - storno; 
'7' - invoice receipts - storno; 
'8' - cancelled receipts ( all voided ); 
'9' - daily X reports; 
Znumber- number of Z report (1...3650); 
Answer(2): 
{ErrorCode}<SEP>{TextData}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
TextData - Document text (up to 64 chars); 
Answer(3): 
{ErrorCode}<SEP>{Data}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
Data - Document data, structured information in base64 format. Detailed information in other 
document; 
Answer(4): 
{ErrorCode}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
Answer(5): 
{ErrorCode}<SEP>{CSV_Col_1}<SEP> ... {CSV_Col_14}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
CSV_Col_1 - идентификационен номер на ФУ; 
CSV_Col_2 - вид на ФБ - ФБ, Разширен ФБ, Сторно ФБ или Разширен сторно ФБ; 
CSV_Col_3 - номер на ФБ; 
CSV_Col_4 - уникален номер на продажба (УНП) - в случай, че ФУ е от типа "Фискален 
принтер" или работи в такъв режим; 
CSV_Col_5 - стока/услуга - наименование; 
41


# Page 42

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
CSV_Col_6 - стока/услуга - единична цена; 
CSV_Col_7 - стока/услуга - количество; 
CSV_Col_8 - стока/услуга - стойност; 
CSV_Col_9 - обща сума на т ФБ/Сторно ФБ или Разширен ФБ/Разширен сторно ФБ; 
CSV_Col_10 - номер на фактура/кредитно известие - в случай че записът е за Разширен ФБ или 
съответно - за Разширен сторно ФБ; 
CSV_Col_11 - ЕИК на получател - в случай че записът е за разширен ФБ или Разширен сторно 
ФБ; 
CSV_Col_12 - номер на сторниран ФБ - в случай че записът се отнася за Сторно ФБ или 
Разширен сторно ФБ; 
CSV_Col_13 - номер на сторнирана фактура - в случай че записът се отнася за Разширен сторно 
ФБ; 
CSV_Col_14 - причина за издаване - в случай че записът се отнася за Сторно ФБ или Разширен 
сторно ФБ. 
Command: 127 (7Fh) Stamp operations 
Parameters of the command: 
{Type}<SEP>{Name}<SEP>
Mandatory parameters:
Type - Type of operation;
'0' - Print stamp; 
'1' - Rename loaded stamp with command 203; 
Name - Name of stamp as filename in format 8.3; 
Answer: 
{ErrorCode}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
Command: 135 (87h)  Modem information 
Parameters of the command: 
{Option}[<SEP>]
Mandatory parameters: 
Option - Type of information to return;
's' - Read the IMEI of the modem; Answer(1) 
'i' - Read the IMSI of the SIM card; Answer(2) 
'M' - Modem status. Returns the last state of the modem; Answer(3) 
Answer(1): 
{ErrorCode}<SEP>{IMEI}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
IMEI - IMEI number of the modemm; 
Answer(2): 
{ErrorCode}<SEP>{IMSI}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
42


# Page 43

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
IMSI - IMSI number of the SIM card; 
Answer(3): 
{ErrorCode}<SEP>{SignalLevel}<SEP>{IMEI}<SEP>{IMSI}<SEP>{MobileOparatorName}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
SignalLevel - GSM Signal level in percentage 0...100; 
IMEI - IMEI number of the modem; 
IMSI - IMSI number of the SIM card; 
MobileOparatorName ; 
Command: 140 (8Ch) Defining and reading clients 
Parameters of the command: 
{Option}<SEP>{Parameters}<SEP>
Mandatory parameters: {Option}
'I' - Clients information;
Syntax: 
{Option}<SEP>
Answer(3) 
'P' - Clients programming;
Syntax: 
{Option}<SEP>{FIRM}<SEP>{Name}<SEP>{TypeTAXN}<SEP>{TAXN}<SEP>{RecName}<SEP>
{VATN}<SEP>{Addr1}<SEP>{Addr2}<SEP>
Mandatory parameters:
FIRM - Client number, index of record (1...1000); 
Name - Client's name (up to 36 chars); 
TAXN - Client's tax number (9...13 chars);
TypeTAXN - Тype of TAXN: '0' - BULSTAT; '1' - EGN; '2' - LNCH; '3' - service 
number; 
RecName - Reciever's name (up to 36 chars); 
VATN - VAT number of the client (up to 14 chars); 
Addr1 - Client's address - line 1 (up to 36 chars); 
Addr2 - Client's address - line 2 (up to 36 chars); 
Answer(1) 
'D' - Client deleting;
Syntax: 
{Option}<SEP>{firstFIRM}<SEP>{lastFIRM}<SEP>
Mandatory parameters:
firstFIRM - First client to delete (1...1000); If this parameter has value 'A', all clients will be 
deleted(lastFIRM must be empty). 
Optional parameters:
lastFIRM - last client to delete (1...1000). Default: {firstFIRM}; ; 
Answer(1) 
'R' - Reading client data;
Syntax: 
{Option}<SEP>{FIRM}<SEP>
Mandatory parameters:
FIRM - Client number (1...1000); 
Answer(2) 
43


# Page 44

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
'F' - Returns data about the first found programmed client;
Syntax: 
{Option}<SEP>{FIRM}<SEP>
Optional parameters:
FIRM - Client number (0...1000). Default: 0; 
Answer(2) 
'L' - Returns data about the last found programmed client;
Syntax: 
{Option}<SEP>{FIRM}<SEP>
Optional parameters:
FIRM - Client number (1...1000). Default: 1000; 
Answer(2) 
'N' - Returns data for the next found programmed client;
Syntax: 
{Option}<SEP>
Note
The same command with option 'F' or 'L' must be executed first. This determines whether to get 
next('F') or previous ('L') client. Answer(2) 
'T' - Find a client by tax number;
Syntax: 
{Option}<SEP>{TAXN}<SEP>
- \b TAXN - Client's tax number (9...13 chars);
Answer(2) 
'X' - Find the first not programmed client;
Syntax: 
{Option}<SEP>{FIRM}<SEP>
Optional parameters:
FIRM - Client number (0...1000). Default: 0; 
Answer(4) 
'x' - Find the last not programmed client;
Syntax: 
{Option}<SEP>{FIRM}<SEP>
Optional parameters:
FIRM - Client number (1...1000). Default: 1000; 
Answer(4) 
Answer(1):
{ErrorCode}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
Answer(2):
{ErrorCode}<SEP>{FIRM}<SEP>{TAXN}<SEP>{TypeTAXN}<SEP>{VATN}<SEP>{Name}<SEP>{Rec
Name}<SEP>{Addr1}<SEP>{Addr2}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
FIRM - Client number, index of record (1...1000); 
Name - Client's name (up to 36 chars); 
TAXN - Client's tax number (9...13 chars); 
TypeTAXN - Тype of TAXN: '0' - BULSTAT; '1' - EGN; '2' - LNCH; '3' - service number; 
RecName - Reciever's name (up to 36 chars); 
VATN - VAT number of the client (up to 14 chars); 
Addr1 - Client's address - line 1 (up to 36 chars); 
Addr2 - Client's address - line 2 (up to 36 chars); 
44


# Page 45

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
Answer(3):
{ErrorCode}<SEP>{Total}<SEP>{Prog}<SEP>{NameLen}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
Total - Total count of the programmable clients (1000); 
Prog - Total count of the programmed clients (0...1000); 
NameLen - Maximum length of client name (36); 
Answer(4):
{ErrorCode}<SEP>{FIRM}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
FIRM - Client number (1...1000); 
Command: 202 (CAh) Customer graphic logo loading. 
Parameters of the command: Syntax 1: 
{Parameter}<SEP>
Mandatory parameters:
Parameter - type of operation;
START - Praparation for data loading; Answer(1) 
STOP - End of data; Answer(2) 
YmFzZTY0ZGF0YQ==  - base64 coded data of the grahpic logo; Answer(2) 
POWEROFF - Shutting down the device; Answer(1) 
RESTART - Device restarting; Answer(1) 
Answer(1):
{ErrorCode}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
Answer(2):
{ErrorCode}<SEP>{Chechsum}
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
Chechsum - Sum of decoded base64 data;
Command: 203 (CAh)  Stamp image loading. 
Parameters of the command: Syntax 1: 
{Parameter}<SEP>
Mandatory parameters:
Parameter - type of operation;
START - Praparation for data loading; Answer(1) 
STOP - End of data; Answer(2) 
YmFzZTY0ZGF0YQ==  - base64 coded data of the grahpic logo; Answer(2) 
Answer(1):
{ErrorCode}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
45


# Page 46

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
Answer(2):
{ErrorCode}<SEP>{Chechsum}
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
Chechsum - Sum of decoded base64 data;
Command: 255 (FFh) Programming
Parameters of the command: 
{Name}<SEP>{Index}<SEP>{Value}<SEP>
Mandatory parameters: 
Name - Variable name;
Device settings;
FpComBaudRate - Baud rate of COM port for communication with PC ( from 0 to 9 ) 
AutoPaperCutting  - Permission/rejection of the automatic cutting of paper after each 
receipt. ( 1 - permitted, 0 - rejected ) (FP-700X only); 
PaperCuttingType  - Partial=0/Full=1 cutting of paper (FP-700X only); 
BarCodeHeight - Barcode height from '1' (7mm) to '10' (70mm); 
BarcodeName - Enable/Disable printing of the barcode data; 
ComPortBaudRate  - Baud rate of COM port that has peripheral device assigned.( from 0
to 999999 ) Number of COM port is determined by "Index". 
ComPortProtocol  - Protocol for communication with peripheral device assigned COM 
port. ( from 0 to 9 ), if device is scale; Number of COM port is determined by "Index". 
MainInterfaceType  - PC interface type. 0-auto select, 1-RS232, 2-BLUETOOTH, 3-
USB, 4-LAN; 
TimeOutBeforePrintFlush-  Time out between fiscal printer commands before start auto 
print( in milliseconds ). value 1...999999999; 
WorkBatteryIncluded  - FPr works with battery on main supply ( 1 - enable; 0 - disable);
Dec2xLineSpacing  - 0...5 - Default 0; Decrease the space between text lines. Greater 
values = less line spacing. 
PrintFontType - Printer font type. 0: default, coarser with a small line spacing, 1: 
smaller, with greater spacing between rows.; 
FooterEmptyLines  - number of blank lines for proper paper cutting; 
HeaderMinLines - Minimum number of lines from the header after printing the footer; 
LogoPrintAfterFooter  - Print the logo after rows to push the paper. 1: yes, 0: no. default:
0; 
EnableNearPaperEnd  - handling of near paper end. 0: No handling, 1: handling 
(default); 
DateFromNAPServDisable  - Synchronize date/time from the NRA server ( 0 - sync, 1 - 
does not sync ); 
AutoPowerOff - Minutes to automatically turn off ECR if it is idle. ( 0 - disable; from 1 
minute to 240 minutes );
BkLight_AutoOff  - Minutes to automatically turn off Backlight of the display if FPr is 
idle. ( 0 - disable; from 1 minute to 5 minutes ); 
PinPad 
PinpadComPort - Number of COM port for communication with pinpad( 1-COM1, 2-
COM2, 4-Bluetooth ); 
PinpadComBaudRate  - Baud rate of COM port that has pinpad device assigned.( from 0
to 9 ); 
PinpadType - Type of pinpad( 1 - BORICA; 2 - UBB; 3 - DSK ); 
46


# Page 47

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
PinpadConnectionType  - Type of connection between cash register and bank server( 0-
GPRS, 1-LAN ); 
PinpadReceiptCopies  - Copies of the receipt from pinpad( 0 - 3 ); 
PinpadReceiptInfo  - Where to print pinpad receipt( 1 - in fiscal receipt; 0 - separate from
fiscal receipt ); 
PinpadPaymentMenu  - Function of PY2 key in registration( 1 - menu for payment with 
pinpad( card and loyalty scheme ); 0 - payment with card with pinpad ). Works only with 
configuration with BORICA. 
PinpadLoyaltyPayment  - Function of PY4 key( 1 - payment with pinpad with loyalty 
scheme; 0 - payment PY4 ). Works only with configuration with BORICA.
PinpadShortRec - Short receipt( 1 ) or normal receipt from pinpad( 0 ); 
Bluetooth parameters (only for bluetooth enabled devices and not for FMP-55X)
BthEnable - turn on / off bluetooth module; 
BthDiscoverability  - turn on / off bluetooth device discoverability; ( 1 - discoverable; 0 - 
non-discoverable); 
BthPairing - 0-unsecure, 1-reset and save, 2-reset; 
BthPinCode - pin code for bluetooth pairing ( default: 0000 ); 
BthVersion - firmware version of bluetooth module; 
BthAddress - bluetooth device address; 
ECR parameters;
EcrLogNumber - Logical number in the workplace ( from 1 to 9999 ); 
EcrExtendedReceipt  - Type of the receipt( 1 - extended, 0 - simplified ); 
EcrDoveriteli - Work with constituents: 1-enable( in one receipt only one constituent ), 0 
- disable; 
EcrWithoutPasswords  - Work without passwords ( 1 - enable; 0 - disable); 
EcrAskForPassword  - Require password after each receipt ( 1 - enable; 0 - disable); 
EcrAskForVoidPassword  - Require password for void operations ( 1 - enable; 0 - 
disable);; 
EcrConnectedOperReport  - When making Z-report, automatically make "Operator 
report" ( 1 - enable; 0 - disable); 
EcrConnectedDeptReport  - When making Z-report, automatically make "Report by 
Departments" ( 1 - enable; 0 - disable); 
EcrConnectedPluSalesReport  - When making Z-report, automatically make "Report by 
PLU with turnovers" ( 1 - enable; 0 - disable); 
EcrConnectedGroupsReport  - When making Z-report, automatically make "Group 
report" ( 1 - enable; 0 - disable);; 
EcrConnectedCashReport  - When making Z-report, automatically make "Ecr report" ( 1
- enable; 0 - disable); 
EcrUserPeriodReports  - Periodic reports ( 1 - enable; 0 - disable) ; 
EcrPluDailyClearing  - When making Z-report, automatically clear PLU turnover ( 1 - 
enable; 0 - disable); 
EcrSafeOpening - Open drawer on every total ( 1 - enable; 0 - disable); 
EcrScaleBarMask  - Text up to 10 symbols. If second number of the weight barcode 
match any of the symbols in this string, barcode will be interpreted as normal barcode. 
EcrNumberBarcode  - Count of used barcodes for each programmed article ( 1...4 ); 
RegModeOnIdle - Time to clear display after last receipt in miliseconds( 1 - 2 147 483 
647 ); 
FlushAtEndOnly - For ECR's only. The receipt is printed after last payment; 
EcrMidnightWarning  - For ECR's only. Minutes before midnight, when ECR starts 
showing warning for Z report. 
EcrMandatorySubtotal  - For ECR's only. The operator must press STL key before 
payment. 1: yes, 0: no. default: 0; 
47


# Page 48

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
Seller - For ECR's only; Name of the seller; 36 symbols max; 
AutoMonthReport  - For ECR's only; Flag for a monthly report suggesting; 1: yes, 0: no. 
default: 1; 
AutoMonthReportDubl  - For ECR's only; Flag for a monthly report dublicate 
suggesting; 1: yes, 0: no. default: 1; 
EcrUnsentWarning  - For ECR's only; Warning for unsent documents from XX hours. 
The value must be set in hours before device will be blocked; 0: no. default: 0; 
Currencies 
CurrNameLocal - Local currency name( up to 3 chars ); 
CurrNameForeign  - Foreign currency name( up to 3 chars ); 
ExchangeRate - Exchange rate( from 1 to 999999999, decimal point is before last five 
digits ); 
Unit names;
Unit_name - Text up to 6 chars. The line is determined by "Index". Index 0 is for line 
1...Index 19 is for line 20; 
Header of the receipt 
Header - Text up to XX symbols. Header line is determined by "Index",
for FP-700X XX= 42, 48 or 64 columns; 
for FMP-350X XX= 42, 48 or 64 columns; 
for FMP-55X XX= 32 columns; 
for DP-25X, DP-150X, WP-500X, WP-25X, WP-50X XX= 42 columns; Index 0 
is for line 1, Index 9 is for line 10; 
Footer of the receipt 
Footer - Text up to XX symbols. Footer line is determined by "Index".
for FP-700X XX= 42, 48 or 64 columns; 
for FMP-350X XX= 42, 48 or 64 columns; 
for FMP-55X XX= 32 columns; 
for DP-25X, DP-150X, WP-500X, WP-25X, WP-50X XX= 42 columns; Index 0 
is for line 1, Index 9 is for line 10; 
Operators;
OperName - Name of operator. Text up to 32 symbols. Number of operator is determined
by "Index"; 
OperPasw - Password of operator. Text up to 8 symbols. ( Require Service jumper ) 
Number of operator is determined by "Index"; 
Note: WP-500X, WP-50X, WP-25X, DP-25X, DP-150X, DP-05C:  the default password for each operator is
equal to the corresponding number (for example, for Operator1 the password is "1") . FMP-350X, FMP-55X, 
FP-700X:  the default password for each operator is “0000”
Payments 
PayName - Name of payment. Text up to 16 symbols. Number of payment is determined 
by "Index"; 
Payment_forbidden  - Forbid the payment ( 1- forbidden, 0 - not forbidden ). Number of 
payment is determined by "Index"; 
Shortcut keys (Only for ECRs)
DPxx_PluCode - Number of PLU assigned to shortcut key. ( 0 - Key is disabled; from 1 
to 99999 for assigning PLU ). Number of key is determined by "Index"; 
Keys discount and surcharge (Only for ECRs)
KeyNDB_value - Value for value surcharge; Value is in cents. ( from 0 to 999999999 ); 
KeyNDB_percentage  - Percentage for percentage surcharge; Value is in hundredths 
(0.01) of a percent. ( from 0 to 9999 ); 
KeyOTS_value - Value for value discount; Value is in cents. ( from 0 to 999999999 ); 
KeyOTS_percentage  - Percentage for percentage discount; Value is in hundredths (0.01)
of a percent. ( from 0 to 9999 ); 
KeyNDB_forbidden  - Forbid the surcharge key ( 1- forbidden, 0 - not forbidden ); 
48


# Page 49

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
KeyOTS_forbidden  - Forbid the discount key ( 1- forbidden, 0 - not forbidden ); 
Service 
ServPasw - Password of the Service man. Text up to 8 symbols;( Require Service 
jumper ) 
ServMessage - Message that will be printed when "ServDate" is reached, up to 64 
symbols. Message line is determined by "Index"; 
ServiceDate - Service date( Format: DD-MM-YY HH:MM:SS ); 
Receipt parameters;
PrnQuality - Contrast of Printing ( from 0 to 20 ); 
PrintColumns - Number of printer columns:
for FP-700X = 42, 48 or 64 columns; 
for FMP-350X = 42, 48 or 64 columns; 
for FMP-55X = 32 columns; 
for DP-25X, DP-150X, WP-500X, WP-50X, WP-25X = 42 columns; 
EmptyLineAfterTotal  - Print empty line after TOTAL line in fiscal receipts 
( 1 - enable, 0 -disable ); 
DblHeigh_totalinreg  - Print TOTAL line in fiscal receipts with double height
( 1 - enable, 0 -disable ); 
Bold_payments – Bold print of the payment names in fiscal receipt 
( 1 - enable, 0 -disable ); 
DublReceipts - Print receipt dublicate ( 1 - enable, 0 -disable ); 
IntUseReceipts - Number of internal receipts ( from 0 to 9 ); 
BarcodePrint - Print PLU barcode in the receipt ( 1 - enable, 0 -disable ); 
LogoPrint - Print the logo in the receipt ( 1 - enable, 0 -disable ); 
DoveritelPrint - Print the department name at the beginning of the receipt ( 1 - enable, 0 -
disable ); 
ForeignPrint - Print total sum in foreign currency 
( 1 - enable, 0 -disable, 2 - print exchange rate ); 
VatPrintEnable - Print VAT rates in the receipt ( 1 - enable, 0 -disable ); 
EnableNearPaperEnd  - handling of near paper end. 0: No handling, 1: handling 
(default); 
Menu functions to enable or disable from the keyboard for fiscal printers only;
DsblKeyZreport - Disable Z report generating from the keyboard; ( 1 - disabled, 0 - 
enabled ); 
DsblKeyXreport - Disable X report generating from the keyboard; ( 1 - disabled, 0 - 
enabled ); 
DsblKeyDiagnostics  - Disable diagnostic info; ( 1 - disabled, 0 - enabled ); 
DsblKeyFmReports  - Disable fiscal memory reports; ( 1 - disabled, 0 - enabled ); 
DsblKeyJournal - Disable electronic journal menu; ( 1 - disabled, 0 - enabled ); 
DsblKeyDateTime  - Disable changing the date and time; ( 1 - disabled, 0 - enabled ); 
DsblKeyCloseReceipt  - Disable manualy closing of the receipt; ( 1 - disabled, 0 - 
enabled ); 
DsblKeyCancelReceipt  - Disable manualy cancellation of the receipt; ( 1 - disabled, 0 - 
enabled ); 
Modem and network 
ModemModel - Model of the modem ( 0 - Quectel M72, 1 - Quectel UC20, 2 - Quectel 
M66, 3- Quectel UG96  ); 
SimPin - PIN code of SIM card. Text up to 16 symbols; 
APN - Access Point Name. Text up to 64 symbols. Number of APN is determined by 
"Index"; 
APN_User - APN Username. Text up to 32 symbols. Number of APN is determined by 
"Index"; 
49


# Page 50

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
APN_Pass - APN Password. Text up to 32 symbols. Number of APN is determined by 
"Index"; 
SimICCID - ICC number of the SIM card. Text up to 31 symbols ( readonly ); 
SimIMSI - IMSI number of the SIM card. Text up to 16 symbols ( readonly ); 
SimTelNumber - MSISDN number of the SIM card. Text up to 16 symbols ( readonly ); 
IMEI - IMEI of the modem( read only ); 
LanMAC - MAC address of the LAN controller( up to 12 chars ); 
DHCPenable Enable use of DHCP ( 1 - enable, 0 -disable ); 
LAN_IP - IP address when DHCP is disabled( up to 15 chars ); 
LAN_NetMask - Net mask when DHCP is disabled( up to 15 chars ); 
LAN_Gateway - Default gateway when DHCP is disabled( up to 15 chars ); 
LAN_PriDNS - Primary DNS when DHCP is disabled( up to 15 chars ); 
LAN_SecDNS - Second DNS when DHCP is disabled( up to 15 chars ); 
LANport_fpCommands  - The number of listening port for PC connection. default: 4999 
(only for devices with LAN); 
WLAN_Enable - Enable/disable wlan interface. 1 – enable, 0 – disable ( only for devices
with WLAN );
WLAN_DHCPenable  - Flag "Use DHCP during WLAN connection" ( 1 - enable, 0 - 
disable ) (only for devices with WLAN); 
WLAN_IP - IP address (only for devices with WLAN); 
WLAN_NetMask - Net mask (only for devices with WLAN); 
WLAN_Gateway - Default gateway (only for devices with WLAN); 
WLAN_PriDNS - Primary DNS (only for devices with WLAN); 
WLAN_SecDNS - Secondary DNS (only for devices with WLAN); 
WLAN_AP_SSID  - SSID of WLAN Access point. Text up to 32 symbols. Number of 
WLAN APN is determined by "Index"; (only for devices with WLAN) 
WLAN_AP_Password  - Password of WLAN Access point. Text up to 32 symbols. Number
of WLAN APN is determined by "Index" (only for devices with WLAN); 
NRA data -( Read Only )
Nap1RType - Registration type(1 char); 
Nap2FDType - FD type(1 char); 
Nap3EIK - EIK(up to 16 chars); 
Nap4EIKType - EIK type(1 char); 
Nap5FDIN - ID of the FD(up to 16 chars); 
Nap6FMIN - ID of the fiscal memory of the FD (up to 16 chars); 
Nap7FDRID - FD registration number(up to 16 chars); 
Nap8RCFD - Reason for deregistration(up to 2 chars); 
Nap9FDCert - Certificate number(up to 16 chars); 
Nap10IMSI - IMSI(up to 32 chars); 
Nap11MSISDN - Telephone number(up to 16 chars); 
Nap12OPID - Operator ID(1 char); 
Nap13OrgName - Name of the organisation(up to 200 chars); 
Nap14PSNum - PS number(up to 16 chars); 
Nap15PSType - PS type(up to 3 chars); 
Nap16SEKATTE - EKATTE code(up to 16 chars); 
Nap17Settl - Settlement name(up to 64 chars); 
Nap18AEktte - Area code(up to 16 chars); 
Nap19Area - Area(up to 100 chars); 
Nap20StreetCode  - Street code(up to 16 chars); 
Nap21Street - Street(up to 100 chars); 
Nap22StrNo - Street number(up to 16 chars); 
50


# Page 51

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
Nap23Block - Block(up to 16 chars); 
Nap24En - Entrance(up to 16 chars); 
Nap25Fl - Floor(up to 16 chars); 
Nap26Ap - Apartment(up to 16 chars); 
Nap27PSName - PS name(up to 200 chars); 
Nap28SOD - Exploitation start date(up to 19 chars); 
Nap29ServiceEIK  - Service organization EIK(up to 16 chars); 
Nap30ServiceEIKType  - Service organization EIK type(1 char); 
Nap31ServiceCo - Date of expiration of service contract(up to 19 chars); 
Nap32APN - APN(up to 100 chars); 
Nap33IP - IP(up to 200 chars); 
Nap34Port - Port(up to 5 chars); 
Nap35APNUser - APN name(up to 32 chars); 
Nap36APNPassword  - APN password(up to 32 chars); 
NapBlockDateTime  - The date and time after which the device will be blocked due to a 
lack of connection with the NRA server; 
Note: "Index" = 0 for current values, "Index" = 1 for saved values after successful registration/change on the NRA server;
Variables for FM ( Read Only )
nZreport - Number of current Z-report; 
nReset - Number of current memory failure; 
nVatChanges - Number of current VAT change; 
nIDnumberChanges  - Number of current SN changes ( 0 - not programmed; 1 - 
programmed ); 
nFMnumberChanges  - Number of current FM number changes ( 0 - not programmed; 1 
- programmed ); 
nTAXnumberChanges  - Number of current TAX number changes ( 0 - not 
programmed; 1 - programmed ); 
valVat - Current value of VAT. Number of VAT is determined by "Index"; 
FMDeviceID - ID of the fiscal memory; 
IDnumber - Serial number of the ECR; 
FMnumber - Number of FM; 
TAXnumber - TAX number; 
FmWriteDateTime  - Date and time for writting block in FM; 
LastValiddate - Last valid date ( written on FM or EJ ); 
Variables for FM ( Read and Write )
TAXlabel - TAX number label( up to 10 chars ); 
Internal variables ( Read Only )
UNP - Last printed unique sale number (21 chars "LLDDDDDD-CCCC-DDDDDDD", 
L[A-Z], C[0-9A-Za-z], D[0-9] ); 
StornoUNP - Last printed unique sale number in strono document (21 chars 
"LLDDDDDD-CCCC-DDDDDDD", L[A-Z], C[0-9A-Za-z], D[0-9] ); 
Fiscalized - flag that shows if FPr is fiscalized. ( 1 - fiscalized; 0 - not fiscalized ); 
DFR_needed - Shows if fiscal receipt is issued after last Z-report. ( 1 - Z-report is 
needed; 0 - Z-report is not needed ); 
DecimalPoint - number of symbols after decimal point; 
nBon - global number of receipts; 
nFBon - Global number of fiscal receipts; 
nInvoice - Number of invoices; 
InvoiceRangeBeg - Start of the invoice range( from 0 to 9999999999 ); 
InvoiceRangeEnd  - End of the invoice range( from 0 to 9999999999 ); 
nFBonDailyCount  - Number of fiscal receipts for the day;
51


# Page 52

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
nLastFiscalDoc - Last number of fiscal receipt;
CurrClerk - number of current operator;
EJNewJurnal - New EJ;
EJNumber - Number of current EJ;
DateLastSucceededSent  - Date/time of last connection to the server; 
NapRegistered - ECR is registered on the NRA server (1 - registered; 0 -not registered); 
DeregOnSever - ECR is deregistered on the NRA server (1 - deregistered; 0 - not 
deregistered); 
Item Groups 
ItemGroups_name  - Name of item group. Text up to 32 symbols. Number of item group 
is determined by "Index"; 
Department registers 
Dept_name - Name of department. Text up to 72 symbols. Number of department is 
determined by "Index"; 
Dept_price - Programmed price of department( from 0 to 999999999 ). Number of 
department is determined by "Index"; 
Dept_vat - VAT group of department( from 1 to 8 ). Number of department is determined
by "Index"; 
ECR variables only in DP-05C
DHL_Algo - flag that tells if the entered tovaritelnica has to be checked with DHL's 
algorithm; 
EIK_validation - flag that tells if the entered EIK number has to be valid; 
EGN_validation - flag that tells if the entered EGN number has to be valid; 
Bonuses - Description of the bonus. Text up to 40 symbols. Number of bonus is 
determined by "Index"; 
TextReducedVAT  - Free text lines describing reason for reduced VAT. Text up to 42 
symbols. Number of line is determined by "Index"; 
Optional parameters: 
Index - Used for index if variable is array. For variable that is not array can be left blank. Default: 0; 
Note
For example: Header[], Index 0 refer to line 1. Index 9 refer to line 10.
Value - If this parameter is blank ECR will return current value ( Answer(2) ). If the value is set, then 
ECR will program this value ( Answer(1) ); 
Answer(1):
{ErrorCode}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
Answer(2):
{ErrorCode}<SEP>{VarValue}<SEP>
ErrorCode - Indicates an error code. If command passed, ErrorCode is 0; 
VarValue - Curent value of the variable; 
Status bits
The current status of the device is coded in field 8 bytes long which is sent within each message of the fiscal 
printer. Description of each byte in this field:
Byte 0: General purpose 
0.7 = 1 Always 1. 
0.6 = 1 Cover is open. 
52


# Page 53

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
0.5 = 1 General error - this is OR of all errors marked with #. 
0.4 = 1# Failure in printing mechanism. 
0.3 = 0 Always 0.
0.2 = 1 The real time clock is not synchronized. 
0.1 = 1# Command code is invalid. 
0.0 = 1# Syntax error.
Byte 1: General purpose 
1.7 = 1 Always 1. 
1.6 = 0 Always 0. 
1.5 = 0 Always 0. 
1.4 = 0 Always 0. 
1.3 = 0 Always 0. 
1.2 = 0 Always 0. 
1.1 = 1# Command is not permitted. 
1.0 = 1# Overflow during command execution.
Byte 2: General purpose 
2.7 = 1 Always 1. 
2.6 = 0 Always 0. 
2.5 = 1 Nonfiscal receipt is open. 
2.4 = 1 EJ nearly full. 
2.3 = 1 Fiscal receipt is open. 
2.2 = 1 EJ is full. 
2.1 = 1 Near paper end. 
2.0 = 1# End of paper.
Byte 3: Not used 
3.7 = 1 Always 1. 
3.6 = 0 Always 0. 
3.5 = 0 Always 0. 
3.4 = 0 Always 0. 
3.3 = 0 Always 0. 
3.2 = 0 Always 0. 
3.1 = 0 Always 0. 
3.0 = 0 Always 0.
Byte 4: Fiscal memory 
4.7 = 1 Always 1. 
4.6 = 1 Fiscal memory is not found or damaged. 
4.5 = 1 OR of all errors marked with ‘*’ from Bytes 4 и 5. 
4.4 = 1* Fiscal memory is full. 
4.3 = 1 There is space for less then 60 reports in Fiscal memory. 
4.2 = 1 Serial number and number of FM are set. 
4.1 = 1 Tax number is set. 
4.0 = 1* Error when trying to access data stored in the FM.
Byte 5: Fiscal memory 
5.7 = 1 Always 1. 
5.6 = 0 Always 0. 
5.5 = 0 Always 0. 
5.4 = 1 VAT are set at least once. 
53


# Page 54

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
5.3 = 1 Device is fiscalized. 
5.2 = 0 Always 0. 
5.1 = 1 FM is formatted. 
5.0 = 0 Always 0.
Byte 6: Not used 
6.7 = 1 Always 1. 
6.6 = 0 Always 0. 
6.5 = 0 Always 0. 
6.4 = 0 Always 0. 
6.3 = 0 Always 0. 
6.2 = 0 Always 0. 
6.1 = 0 Always 0. 
6.0 = 0 Always 0.
Byte 7: Not used 
7.7 = 1 Always 1. 
7.6 = 0 Always 0. 
7.5 = 0 Always 0. 
7.4 = 0 Always 0. 
7.3 = 0 Always 0. 
7.2 = 0 Always 0. 
7.1 = 0 Always 0. 
7.0 = 0 Always 0. 
Error codes
Error code Error name Description
(100000 - 100100) GENERIC ERRORS - FISCAL DEVICES
-100001ERR_IO General error in fiscal device: In - out error( cannot 
read or write )
-100002ERR_CHECKSUM General error in fiscal device: Wrong checksum
-100003ERR_END_OF_DATA General error in fiscal device: No more data
-100004ERR_NOTFOUND General error in fiscal device: The element is not 
found
-100005ERR_NO_RECORDS General error in fiscal device: There are no records 
found
-100006ERR_ABORTED General error in fiscal device: The operation is aborted
-100007ERR_WRONG_MODE Wrong mode( standart, training...)  is selected.
-100008ERR_NOT_READY General error in fiscal device: Device is not ready
-100009ERR_NOTHING_TO_PRINT General error in fiscal device: Nothing to print
(100100 - 100254) FISCAL MEMORIES
-100100ERR_FM_BUSY Fiscal memory error: Fiscal memory is busy
-100101ERR_FM_FAILURE Fiscal memory error: Fiscal memory failure. Could not 
read or write
-100102ERR_FM_WRITE_PROTECTED Fiscal memory error: Forbidden write in fiscal memory
-100103ERR_FM_WRONG_ADDRESS Fiscal memory error: Wrong address in fiscal memory
54


# Page 55

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
-100104ERR_FM_WRONG_SIZE Fiscal memory error: Wrong size in fiscal memory
-100105ERR_FM_NOT_CONNECTED Fiscal memory error: Fiscal memory is not connected
-100106ERR_FM_WRONG_CHECK_SUM Fiscal memory error: Wrong checksum in fiscal 
memory( invalid data )
-100107ERR_FM_BLOCK_IS_EMPTY Fiscal memory error: Empty block in fiscal memory
-100108ERR_FM_MAX_NUMBER Fiscal memory error: Maximum number of block  in 
fiscal memory
-100109ERR_FM_WRONG_RANGE Fiscal memory error: Wrong range in fiscal memory
-100110ERR_FM_EMPTY_RANGE Fiscal memory error: Empty range in fiscal memory
-100111ERR_FM_NEW_MODULE Fiscal memory error: New module in fiscal memory
-100112ERR_FM_NOT_EMPTY Fiscal memory error: Fiscal memory is not empty
-100113ERR_FM_NOT_EQUAL Fiscal memory error: Fiscal memory is not equal
-100114ERR_FM_FULL Fiscal memory error: Fiscal memory is full
-100115ERR_FM_NEED_UPDATE Fiscal memory error: Fiscal memory needs update
-100116ERR_FM_BLOCKED Fiscal memory error: Fiscal memory is blocked
(100400 - 100499) PRINTER DRIVER ERRORS
-100400ERR_LTP_VCCERR Line thermal printer mechanism error: Power supply 
error (3,3 V)
-100401ERR_LTP_SVPERR Line thermal printer mechanism error: Power supply 
error (24V or 8V)
-100402ERR_LTP_STHERR Line thermal printer mechanism error: Head 
overheating
-100403ERR_LTP_PESENS Line thermal printer mechanism error: Paper end
-100404ERR_LTP_HDSENS Line thermal printer mechanism error: Cover is open
-100405ERR_LTP_NESENS Line thermal printer mechanism error: Near paper end
-100406ERR_LTP_MKSENS Line thermal printer mechanism error: Mark sensor - 
not used
-100407ERR_LTP_CUTERR Line thermal printer mechanism error: Cutter error
-100408ERR_LTP_PR_ERR Line thermal printer mechanism error: Not used
-100409ERR_LTP_PR_BUSY Line thermal printer mechanism error: Not used
-100410ERR_LTP_BZLPDEC Line thermal printer mechanism error: Not used
-100411ERR_LTP_BZLCLMP Line thermal printer mechanism error: Not used
-100412ERR_LTP_CHARGE_MODE Line thermal printer mechanism error: Not used
-100413ERR_LTP_INZERR_MODE Line thermal printer mechanism error: Not used
-100414ERR_LTP_MOTOR_OVERRUN Printer on time is overrun.
(100500 - 100999) SYSTEM ERRORS
-100500ERR_PROGRAM_SELF_CHECK_ERROR System error: Memory structure error
-100501ERR_SRAM_ERROR System error: Error in RAM
-100502ERR_FLASH_ERROR System error: Flash memory error
-100503ERR_SDCARD_ERROR System error: SD card error
-100504ERR_INVALID_MSG_FILE System error: Invalid message file
-100505ERR_FM_ERROR System error: Fiscal memory error( could not write or 
read )
55


# Page 56

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
-100506ERR_NO_RAM_BATTERY System error: No RAM battery
-100507ERR_SAM_ERROR System error: SAM module error
-100508ERR_RTC_ERROR System error: Real time clock error
-100509ERR_PROGRAM_EXRAM_CHECK_ERROR System error: Memory error
-100510ERR_SDCARD_WRONG_SIZE System error: The size of SD card is wrong.
-100511ERR_TPM_ERROR System error: TPM module error
(101000 - 101499) COMMON LOGICAL ERRORS
-101000ERR_NO_HEAP_MEMORY Common logical error: No heap memory( cannot 
allocate memory for operation )
-101001ERR_FILE_MANIPULATE Common logical error: File manipulate error
-101003ERR_REJECTED Common logical error: Operation is rejected
-101004ERR_BAD_INPUT Common logical error: Bad input. Some of the data or 
parameters are incorrect
-101005ERR_IAP Common logical error: In Application Programming 
error
-101006ERR_NOT_POSSIBLE Common logical error: The execution of the operation 
is not possible
-101007ERR_TMOUT Common logical error: Timeout. The time for waiting 
execution is out
-101007ERR_TIMEOUT Common logical error: Timeout. The time for waiting 
execution is out
-101008ERR_INVALID_TIME Common logical error: Invalid time
-101009ERR_CANCELLED Common logical error: The operation is cancelled
-101010ERR_INVALID_FORMAT Common logical error: Invalid format
-101011ERR_INVALID_DATA Common logical error: Invalid data
-101012ERR_PARSE_ERROR Common logical error: Data parsing error
-101013ERR_HARDWARE_CONFIGURATION Common logical error: Hardware configuration error
-101014ERR_ACCESS_DENIED ERR_ACCESS_DENIED
-101015ERR_BAD_DATA_LENGTH Wrong data length
-101016ERR_VERIFY_Z Error during verification of Z reports
-101017ERR_NO_PERMISSION Common logical error:  No permission
(101500 - 101999) UPDATE ERRORS
-101500ERR_NO_UPDATE Update error: No update. The device is up to date
-101501ERR_UPDATE_IN_PROGRESS Update error: Update is already in progress
(102000 - 102999) GENERAL ERRORS
-102000ERR_LOW_BATTERY Battery error: Low battery
-102001ERR_LOW_BATTERY_WARNING Battery error: Low battery warning
-102002ERR_OPER_WRONG_PASSWORD Operator error: Wrong operator password
-102003ERR_IDNUMBER_IS_EMPTY ECR error: ID number is empty
-102004ERR_NOT_FOUND_BLUETOOTH Bluetooth error: Bluetooth is not found
-102005ERR_DISPLAY_DISCONNECTED Display error: Display is not connected
-102006ERR_PRINTER_DISCONNECTED Printer error: Printer is not connected
56


# Page 57

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
-102007ERR_SD_NOT_PRESENT SD card error: SD card not present
-102008ERR_SD2_NOT_PRESENT SD card error: SD2 card not present
-102009ERR_VAT_RATES_ARE_EMPTY ECR error: VAT rates is not set.
-102010ERR_HEADER_IS_EMPTY ECR error: Header lines are empty.
-102011ERR_ZDDS_NUM_IS_EMPTY User is registered by VAT, but number of the user is 
not entered.
-102012ERR_FMNUMBER_IS_EMPTY ECR error: FM number is empty
-102013ERR_SERVICEMAN_NAME_IS_EMPTY ECR error: Serviceman name is empty
-102014ERR_SERVICEMAN_ID_IS_EMPTY ECR error: Serviceman ID is empty
-102015ERR_TAXOFFICE_ID_IS_EMPTY ECR error: Tax office ID is empty!
-102016ERR_WRONG_FORMAT ECR error: Wrong format
-102017ERR_TAXNUMBER_IS_EMPTY ECR error: TAX number is empty
-102018ERR_WRONG_IDNUMBER ECR error: ID number is wrong
-102019ERR_DATETIME_EARLIER_THAN_PREV_Z ECR error: Date and time are earlier than date and 
time of previous Z report.
-102020ERR_NEED_SOFTWARE_PASSWORD ECR error: The software password is not entered
(103000 - 103999) PLU DATABASE 
-103000ERR_PLUDB_NOT_FOUND PLU database error: PLU database is not found
-103001ERR_PLUDB_PLUCODE_EXISTS PLU database error: PLU code already exists
-103002ERR_PLUDB_BARCODE_EXISTS PLU database error: Barcode already exists
-103003ERR_PLUDB_FULL PLU database error: PLU database is full
-103004ERR_P_HAVE_TURNOVER PLU database error: PLU has turnover
-103005ERR_PLUDB_NAME_EXISTS PLU database error: In the PLU base has an article 
with same name.
-103006ERR_PLUDB_NAMES_NOT_UNIQUE PLU database error: PLU name is not unique.
-103007ERR_PLUDB_FORMAT_INCOMPATIBLE PLU database error: Database format is not 
compatible.
-103008ERR_PLUDB_CAN_NOT_OPEN Can't open the PLU database file
(104000 - 104999) SERVICE OPERATIONS
-104000ERR_NEED_Z_REPORT Service operation error: Z report is needed for this 
operation
-104001ERR_NEED_SERVICE_JUMPER Service operation error: Service jumper is needed for 
this operation
-104002ERR_NEED_SERVICE_PASSWORD Service operation error: Service password is needed 
for this operation
-104003ERR_FORBIDEN Service operation error: The operation is forbidden
-104004ERR_NEED_SERVICE_INTERVENTION Service operation error: Service intervention is needed
-104005ERR_NEED_ALL_CLEARING_REPORTS Service operation error: All clearing report is needed.
-104006ERR_Z_REPORT_CLOSED Service operation error: Z report closed.
-104007ERR_NEED_MONTH_REPORT Service operation error: Montly report needed.
-104008ERR_NEED_YEAR_REPORT Service operation error: Year report needed.
-104009ERR_NEED_BACKUP Service operation error: Backup needed.
-104010ERR_NEED_ALL_PAIDOUT ERR_NEED_ALL_PAIDOUT
57


# Page 58

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
-104011ERR_NEED_OPERATOR_Z_REPORT Clearing report for operator is needed.
-104012ERR_NEED_GROUP_Z_REPORT Clearing report for item group is needed.
-104013ERR_NEED_VAT_CHANGES VAT changes is needed.
(105000 - 105999) EJ - ERRORS
-105000ERR_EJ_NO_RECORDS EJ error: No records in EJ
-105001ERR_CANNOT_ADD_TO_EJ EJ error: Cannot add to EJ
-105002ERR_EJ_WRONG_MAC_RECORD EJ error: SAM module signature error
-105003ERR_EJ_IMMPOSSIBLE_TO_CHK_MAC_RE
CORDEJ error: Signature key version is changed -> 
impossible check
-105004ERR_EJ_BAD_RECORDS EJ error: Bad record in EJ
-105005ERR_EJ_CAN_NOT_GENERATE_MAC EJ error: Generate signature error( cannoct generate 
signature )
-105006ERR_EJ_WRONG_TYPE_TO_SIGN EJ error: Wrong type of document to sign
-105007ERR_EJ_ALREADY_SIGNED EJ error: Document is already signed
-105008ERR_EJ_NOT_FROM_THIS_DEVICE EJ error: EJ is not from this device
-105009ERR_EJ_NEAR_FULL EJ error: EJ is almost full
-105010ERR_EJ_FULL EJ error: EJ is full
-105011ERR_EJ_WRONG_FORMAT EJ error: Wrong format of EJ
-105012ERR_EJ_NOT_READY The electronic journal is not ready.
-105013ERR_EJ_NEED_NEW Error in EJ structure. Create new one.
(106000 - 106999) CLIENTS DATABASE ERRORS
-106000ERR_R_FIRM_NOTEXIST Client database error: Firm does not exist
-106001ERR_FIRMDB_FIRMCODE_EXISTS Client database error: Firmcode already exists
-106002ERR_FIRMDB_EIK_EXISTS Client database error: EIK already exists
-106003ERR_FIRMDB_FULL Client database error: Firm database is full
-106004ERR_FIRMDB_NOT_FOUND Client database error: Firm database is not found
(107000 - 107499) CERTIFICATE STORE
-107001ERR_INVALID_CERTIFICATE Invalid certificate.
-107002ERR_VALID_CERT_EXISTS Certificate exist.
-107003ERR_CERT_UNPACKING_FAILED Certificate unpack failed.
-107004ERR_CERT_WRONG_PASSWORD Wrong certificate password.
-107005ERR_CERT_FILE_WRITE File write error.
-107006ERR_CERT_FILE_READ File read error.
-107007ERR_CERT_NOT_FOUND Certificate not found.
(108000 - 108999) DISCOUNT CARDS DATABASE ERRORS
-108000ERR_R_DISC_NOTEXIST Discount card database error: Discount card does not 
exist
-108001ERR_DISCDB_DISCCODE_EXISTS Discount card database error: Discount card already 
exists
-108002ERR_DISCDB_BARCODE_EXISTS Discount card database error: Barcode already exists
58


# Page 59

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
-108003ERR_DISCDB_FULL Discount card database error: Discount card database 
is full
-108004ERR_DISCDB_NOT_FOUND Discount card database error: Discount card not found
(109000 - 109999) SMARTCARD ERRORS
-109981ERR_SMARTCARD_NOT_PRESENT Smartcard error: No card in the holder.
-109982ERR_SMARTCARD_CONFIG Smartcard error: Configuration failed
-109983ERR_SMARTCARD_COMMUNICATION Smartcard error: SmartCard communication error.
-109984ERR_SMARTCARD_CARD_FAULT Smartcard error: Supply voltage drop, a VCC over-
current detection or overheating.
-109985ERR_SMARTCARD_MODULE_ERROR Smartcard error: Unexpected response from the 
applet.
-109986ERR_SMARTCARD_WRONG_ID The ID of the smart card does not match the ID stored 
in the fiscal memory.
(110100 - 110199) EXT FISCAL DEVICE ERRORS
-110100ERR_DEVICE_COMM_ERROR Device error: Communication error
-110101ERR_DEVICE_WRONG_STRUCT Device error: Wrong struct format
-110102ERR_DEVICE_STFLAG_ACTIVE Device error: ST flag is active
-110103ERR_DEVICE_INVALID_DATA Device error: Invalid data
-110104ERR_DEVICE_NOT_FISCALIZED Device error: Device is not fiscalized
-110105ERR_DEVICE_ALREADY_FISCALIZED Device error: Device is already fiscalized
-110106ERR_DEVICE_IN_SERVICE_MODE Device error: Device is in service mode
-110107ERR_DEVICE_PASSED_SERVICE_DATE Device error: Service date is passed
-110108ERR_DEVICE_DAY_IS_OPEN Device error: Day( shift ) is open
-110109ERR_DEVICE_DAY_IS_CLOSED Device error: Day( shift ) is closed
-110110ERR_DEVICE_WRONG_NUMBERS Device error: Z-report number and shift number are 
not equal
-110111ERR_DEVICE_ADMIN_ONLY Device error: Only admin has permition
-110112ERR_DEVICE_UNFISCALIZED Device error: Fiscal memory is closed
(110200 - 110299) NAP SERVER ERRORS
-110200ERR_NAP_OPEN_SESSION NAP server error: Error open session
-110201ERR_NAP_PREPARE_DATA NAP server error: Error preparing data for server
-110202ERR_NAP_SEND_DATA NAP server error: There is unsent data
-110203ERR_NAP_RECV_DATA NAP server error: Receiving data error
-110204ERR_NAP_EMPTY_DATA NAP server error: Empty data
-110205ERR_NAP_NEGATIVE_ANSWER NAP server error: Server negative answer
-110206ERR_NAP_WRONG_ANSWER_FORMAT NAP server error: Wrong answer format
-110207ERR_NAP_HOSTDI_ZERRO NAP server error: Server HOSTDI is zerro
-110208ERR_NAP_EXCEPTION NAP server error: Server exception
-110209ERR_NAP_NOTPERSONALIZED NAP server error: Not registered on server
-110209ERR_NAP_NOTREGISTERED NAP server error: Not registered on server
-110210ERR_NAP_BLOCKED_72H NAP server error: Communication with NAP server is 
blocked
59


# Page 60

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
-110211ERR_NAP_BLOCKED_NO_MODEM_LAN NAP server error: Modem error
-110212ERR_NAP_BUSY NAP server error: NAP is busy
-110213ERR_NAP_REGISTERED NAP server error: Already registered
-110214ERR_NAP_WRONG_PSTYPE NAP server error: Wrong PS type
-110215ERR_NAP_DEREG_ON_SERVER NAP server error: Deregistered in NAP
-110216ERR_NAP_WRONG_IMSI NAP server error: Wrong IMSI number
-110217ERR_NAP_BLOCKED_MAX_ZERRORS NAP server error: Device is blocked( maximum Z-
reports )
-110218ERR_NAP_WRONG_FDTYPE NAP server error: Wrong FD( Fiscal device ) type
-110219ERR_NAP_BLOCKED_BY_SERVER NAP server error: The ECR is blocked by server
-110220ERR_NAP_BLOCKED_ERROR_FROM_SERV
ERNAP server error: The ECR is blocked - server error
-110221ERR_NAP_NO_SERVER_ADDRESS NAP server error: No server address
-110222ERR_NAP_NO_REGISTRATIONS_POSSIBLE NAP server error: Max. registrations reached.
-110223ERR_NAP_INVALID_OPERATOR_INN Invalid INN of the cashier
-110224ERR_NAP_INVALID_SERVER_INN Invalid INN of the server
-110225ERR_NAP_BLOCKED_MAX_SELLERRORS NAP server error: Device is blocked( unsent sales 
documents )
-110226ERR_NAP_BLOCKED_24H NAP server error: Communication with NAP server is 
blocked. More than 24 hours from last sent receipt.
(110300 - 110399) WORK_INVALID
-110300ERR_WORK_INVALID_FILE Working error: Invalid file
-110301ERR_WORK_INVALID_PARAM Working error: Invalid parameters
(110500 - 110599) MODEM ERRORS
-110500ERR_MODEM_CTRL Modem error: error in communication between device 
and modem
-110501ERR_MODEM_NO_SIM Modem error: No SIM card
-110502ERR_MODEM_PIN Modem error: Wrong PIN of SIM
-110503ERR_MODEM_ATTACH Modem error: Cannot register to mobile network
-110504ERR_MODEM_PPP Modem error: No PPP connection( cannot connect )
-110505ERR_MODEM_CONFIG Modem error: Wrong modem configuration( for 
example - no programmed apn )
-110506ERR_MODEM_WAIT_INIT Modem error: Modem initializing
-110507ERR_MODEM_NOTREADY Modem error: Modem is not ready
-110508ERR_MODEM_REMOVE_SIM Modem error: Remove SIM card
-110509ERR_MODEM_CELL_FOUND Modem error: Modem found a cell
-110510ERR_MODEM_CELL_NOTFOUND Modem error: Modem does not find a cell
-110511ERR_MODEM_LOT_DAYS_FAIL Modem error: Failed lot days
(110600 - 110699) WIFI ERRORS
-110601ERR_MODEM_CONNECT_AP Modem error: Device is not connected to AP( access 
point )
60


# Page 61

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
(110700 - 110799) NETWORK ERRORS
-110700ERR_NET_DNS_RESOLVE Network error: Cannot resolve address
-110701ERR_NET_SOCKET Network error: Cannot open socket for communication 
with server
-110702ERR_NET_CONNECTION Network error: Connection error( cannot connect to a 
server )
-110703ERR_NET_CONFIG Network error: Config error( for example: no server 
address )
-110704ERR_NET_SOCKET_CONNECTED Network error: Connection socket is already opened
-110705ERR_NET_SSL_ERROR Network error: SSL communication error( something 
went wrong in cryptographic protocol )
-110706ERR_NET_HTTP_ERROR Network error: HTTP communication error( something 
went wrong in http protocol )
(110800 - 110899) TAX_TERMINAL_ERRORS
-110800ERR_DT_OK Tax terminal error: No error
-110801ERR_DT_UNKNOWN_ID Tax terminal error: Unknown ID
-110802ERR_DT_INVALID_TOKEN Tax terminal error: Invalid token( key from the server )
-110803ERR_DT_PROTOCOL_ERROR Tax terminal error: Protocol error
-110804ERR_DT_UNKNOWN_COMMAND Tax terminal error: The command is unknown
-110805ERR_DT_UNSUPPORTED_COMMAND Tax terminal error: The command is not supported
-110806ERR_DT_INVALID_CONFIGURATION Tax terminal error: Invalid configuration
-110807ERR_DT_SSL_IS_NOT_ALLOWED Tax terminal error: SSL is not allowed
-110808ERR_DT_INVALID_REQUEST_NUMBER Tax terminal error: Invalid request number
-110809ERR_DT_INVALID_RETRY_REQUEST Tax terminal error: Invalid retry request
-110810ERR_DT_CANT_CANCEL_TICKET Tax terminal error: Cannot cancel ticket
-110811ERR_DT_OPEN_SHIFT_TIMEOUT_EXPIRED Tax terminal error: More than 24 hours from shift 
opening
-110812ERR_DT_INVALID_LOGIN_PASSWORD Tax terminal error: Invalid login name or password
-110813ERR_DT_INCORRECT_REQUEST_DATA Tax terminal error: Incorrect request data
-110814ERR_DT_NOT_ENOUGH_CASH Tax terminal error: Not enough cash
-110815ERR_DT_BLOCKED Tax terminal error: Blocked from server
-110854ERR_DT_SERVICE_TEMPORARILY_UNAVAI
LABLETax terminal error: Service temporarily unavailable
-110855ERR_DT_UNKNOWN_ERROR Tax terminal error: Unknown error
(111000 - 111499) REGMODE ERRORS
-111000ERR_R_CLEAR Registration mode error: Common error, followed by 
deliting all data for the command
-111001ERR_R_NOCLEAR Registration mode error: Common error, followed by 
partly deliting data for the command
-111002ERR_R_SYNTAX Registration mode error: Syntax error. Check the 
parameters of the command
-111003ERR_R_NPOSSIBLE Registration mode error: Cannot do operation
-111004ERR_R_PLU_NOTEXIST Registration mode error: PLU code was not found
-111005ERR_R_PLU_VAT_DISABLE Registration mode error: Forbidden VAT
61


# Page 62

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
-111006ERR_R_PLU_QTY_PRC Registration mode error: Overflow in multiplication of 
quantity and price
-111007ERR_R_PLU_NO_PRC Registration mode error: PLU has no price
-111008ERR_R_PLU_GRP_RANGE Registration mode error: Group is not in range
-111009ERR_R_PLU_DEP_RANGE Registration mode error: Department is not in range
-111010ERR_R_BAR_NOTEXIST Registration mode error: BAR code does not exist
-111011ERR_R_OVF_TOTAL Registration mode error: Overflow of the PLU turnover
-111012ERR_R_OVF_QTY Registration mode error: Overflow of the PLU quantity
-111013ERR_R_ECR_OVR Registration mode error: ECR daily registers overflow
-111014ERR_R_BILL_TL_OVR Registration mode error: Bill total register overflow
-111015ERR_R_OPEN_BON Registration mode error: Receipt is opened
-111016ERR_R_CLOSED_BON Registration mode error: Receipt is closed
-111017ERR_R_PAY_NOCASH Registration mode error: No cash in ECR
-111018ERR_R_PAY_STARTED Registration mode error: Payment is initiated
-111019ERR_R_OVF_TRZ_BUFF Registration mode error: Maximum number of sales in 
receipt
-111020ERR_R_NO_TRANSACTIONS Registration mode error: No transactions
-111021ERR_R_NEGATIVE_SUMVAT Registration mode error: Possible negative turnover
-111022ERR_R_PYFOREIGN_HAVERESTO Registration mode error: Foreign payment has change
-111023ERR_R_TRZ_NOT_EXIST Registration mode error: Transaction is not found in 
the receipt
-111024ERR_R_END_OF_24_HOUR_PERIOD Registration mode error: End of 24 hour blocking
-111025ERR_R_NO_VALID_INVOICE Registration mode error: Invalid invoice range
-111026ERR_R_POS_TERM_CANCELED Registration mode error: Operation is cancelled by 
operator
-111027ERR_R_POS_TERM_APPROVED Registration mode error: Operation approved by POS
-111028ERR_R_POS_TERM_NOT_APPROVED Registration mode error: Operation is not approved by 
POS
-111029ERR_R_POS_TERM_CONN_ERR Registration mode error: POS terminal communication
error
-111030ERR_R_PLU_QTY_PRC_TOO_LOW Registration mode error: Multiplication of quantity and 
price is 0
-111031ERR_R_VALUE_TOO_BIG Registration mode error: Value is too big
-111032ERR_R_VALUE_BAD Registration mode error: Value is bad
-111033ERR_R_PRICE_TOO_BIG Registration mode error: Price is too big
-111034ERR_R_PRICE_BAD Registration mode error: Price is bad
-111035ERR_R_ALL_VOID_SELECTED Registration mode error: Operation all void is selected 
to be executed
-111036ERR_R_ONLY_ALL_VOID_IS_POSSIBLE Registration mode error: Only all void operation is 
permitted
-111040ERR_R_REST_NOFREESPC_SELLS Registration mode error: Restaurant: There is no free 
space for other purchases
-111041ERR_R_REST_NOFREESPCFORNEWACNT Registration mode error: Restaurant: There is no free 
space for new acount
-111042ERR_R_REST_ACCOUNT_IS_OPENED Registration mode error: Restaurant: Account is 
already opened
-111043ERR_R_REST_WRONG_INDEX Registration mode error: Restaurant: Wrong index
62


# Page 63

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
-111044ERR_R_REST_ACNT_IS_NOTFOUND Registration mode error: Restaurant: Account is not 
found
-111045ERR_R_REST_NOT_PERMITTED Registration mode error: Restaurant: Not 
permitted( only for admins )
-111046ERR_R_OPEN_NONFISCALBON Registration mode error: non-fiscal receipt is opened
-111047ERR_R_OPEN_FISCALBON Registration mode error: fiscal receipt is opened
-111048ERR_R_BUYERS_TIN_IS_ENTERED Registration mode error: Buyers TIN is already 
entered
-111049ERR_R_BUYERS_TIN_IS_NOT_ENTERED Registration mode error: Buyers TIN is not entered
-111050ERR_R_PAY_NOT_STARTED Registration mode error: Payment is not initiated
-111051ERR_R_BON_TYPE_MISMATCH Registration mode error: Reeipt type mismatch
-111052ERR_R_REACH_BON_TL_LIMIT Registration mode error: Receipt total limit is reached
-111053ERR_R_CASH_NO_MULT_MIN_COIN Registration mode error: Sum cannot be divided by the
minimum coin
-111054ERR_R_PAY_BIG_AMOUNT Registration mode error: Sum must be <= payment 
amount
-111055ERR_R_PAY_VOUCHER_NEED_INPUT_SU
MRegistration mode error: Sum of voucher must be 
entered when paying with voucher
-111056ERR_R_PAY_VOUCHER_NEED_SURCHAR
GERegistration mode error: Value surcharge of the 
difference between voucher sum and total must be 
done when paying with voucher and sum > total
-111057ERR_R_PAY_FOREIGN_DISABLED Registration mode error: Payment with foreign 
currency is disabled
-111058ERR_R_PAY_FOREIGN_IMPOSSIBLE Registration mode error: Payment with foreign 
currency is impossible
-111059ERR_R_PAY_FOREIGN_SMALL_AMOUNT Registration mode error: Sum must be bigger or equal 
to payment amount
-111060ERR_R_SAFE_OPEN_DISABLED Registration mode error: Safe opening is disabled
-111061ERR_R_PAY_FORBIDDEN Registration mode error: Forbidden payment
-111062ERR_R_PERC_KEY_FORBIDDEN Registration mode error: Forbidden key for surcharge/
discount
-111063ERR_R_AMOUNT_BIGGER_BILLAMOUNT Registration mode error: Entered sum is bigger than 
receipt sum
-111064ERR_R_AMOUNT_SMALLER_BILLAMOUNT Registration mode error: Entered sum is smaller than 
receipt sum
-111065ERR_R_ZERO_BILLAMOUNT Registration mode error: Fiscal printer: Sum of receipt 
is 0. Operation 'void' is needed
-111066ERR_R_ALL_VOID_EXECUTED Registration mode error: Fiscal printer: Operation 'void'
is executed. Close receipt is needed
-111067ERR_R_OPEN_STORNOBON Registration mode error: Storno receipt is opened
-111068ERR_R_PAY_ZERO_AMOUNT Registration mode error: Sum is not entered
-111069ERR_R_PLU_PRICETYPE_RANGE Registration mode error: Price type is invalid
-111070ERR_R_PLU_PRICETYPE_LINKED Registration mode error: Linked surcharge is forbidden
-111071ERR_R_PLU_PRICETYPE_NEGATIVE Registration mode error: Negative price is forbidden
-111072ERR_R_MORE_THAN_ONE_VAT Registration mode error: More than 1 VAT in one 
receipt is not allowed
-111073ERR_R_PINPAD Registration mode error: Pinpad error
-111074ERR_R_WRONG_BUYERS_DATA Registration mode error: Buyer data is wrong
-111075ERR_R_VAT_SYSTEM_DISABLE Registration mode error: Vat system disable.
63


# Page 64

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
-111076ERR_R_OPER_NOT_LOGGED_IN Operator not logged in.
-111077ERR_R_WRONG_DATE_FM The receipt date is early on last date in fiscal memory.
-111078ERR_R_CORR_DATA_NOT_ENTERED Correction receipt data is not entered!
-111079ERR_R_FRACTIONAL_QTY Fractional quantity!
-111080ERR_R_OUT_OF_STOCK Registration mode error: Registration mode error: Out 
of stock
-111081ERR_R_STL_NEEDED Registration mode error: Must pushing of the STL 
before TL.
-111082ERR_R_PACK_NOTEXIST Package does not exist
-111083ERR_R_PLU_UNIT_NOTEXIST Measuring unit not found
-111084ERR_R_PLU_CATEGORY_NOTEXIST Category not found in the data base
-111085ERR_R_DEP_WRONG_NAME Invalid department name
-111086ERR_R_BANK_TERM_NOT_CONFIGURED Bank terminal not configured
-111087ERR_R_SIGN_PAY_INCORECT Disallowed 'признак расчета' (Russia)
-111088ERR_R_SIGN_INCORRECT Forbidden признак товара
-111089ERR_R_PLU_OVER_MAX_PRC Entered price is bigger than the programmed
-111090ERR_R_PLU_FIX_PRC Fix PLU's price
-111091ERR_R_SIGN_AGENT_INCORECT Incorect sign agent.
-111092ERR_R_PAY_VOUCHER_RESTO Voucher payment cannot have change
-111093ERR_R_PAY_ADVANCE_BIG Sum for advance payment is bigger than the sum of 
article
-111094ERR_R_PAY_STORNO_RESTO Payment in storno can not have change
-111095ERR_R_NOT_EXCISE_PLU_WITH_EXCISE_
STAMPInvalid parameter - PLU is not defined as excise PLU
-111096ERR_R_EXCISE_PLU_WITHOUT_EXCISE_S
TAMPExcise stamp of an excise PLU is not entered
-111097ERR_R_EXCISE_PLU_FORBIDDEN SALE FORBIDDEN (excise stamp is not valid)
(111500 - 111799) PINPAD ERRORS
-111500ERR_PINPAD_NONE Pinpad error: No error from pinpad
-111501ERR_PINPAD_GENERAL Pinpad error: General unicreditbulbank icon error
-111502ERR_PINPAD_INVALID_COMMAND Pinpad error: Not valid command or sub command 
code
-111503ERR_PINPAD_INVALID_PARAM Pinpad error: Invalid parameter
-111504ERR_PINPAD_INVALID_ADDRESS Pinpad error: The address is outside limits
-111505ERR_PINPAD_INVALID_VALUE Pinpad error: The value is outside limits
-111506ERR_PINPAD_INVALID_LENGTH Pinpad error: The length is outside limits
-111507ERR_PINPAD_NOT_PERMIT Pinpad error: The action is not permited in current 
state
-111508ERR_PINPAD_NO_DATA Pinpad error: There is no data to be returned
-111509ERR_PINPAD_TIMEOUT Pinpad error: Timeout occurs
-111510ERR_PINPAD_INVALID_KEY_NUMBER Pinpad error: Invalid key number
-111511ERR_PINPAD_INVALID_KEY_ATTRIBUTES Pinpad error: Invalid key attributes(usage)
-111512ERR_PINPAD_INVALID_DEVICE Pinpad error: Calling of non-existing device
-111513ERR_PINPAD_NOT_SUPPORT Pinpad error: (Not used in this FW version)
64


# Page 65

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
-111514ERR_PINPAD_PIN_LIMIT Pinpad error: Pin entering limit exceed
-111515ERR_PINPAD_FLASH Pinpad error: General error in flash commands
-111516ERR_PINPAD_HARDWARE Pinpad error: General hardware unicreditbulbank error
-111517ERR_PINPAD_INVALID_CRC Pinpad error: Invalid code check (Not used in this FW 
version)
-111518ERR_PINPAD_CANCEL Pinpad error: The button 'CANCEL' is pressed
-111519ERR_PINPAD_INVALID_SIGNATURE Pinpad error: Invalid signature
-111520ERR_PINPAD_INVALID_HEADER Pinpad error: Invalid data in header
-111521ERR_PINPAD_INVALID_PASSWORD Pinpad error: Incorrect password
-111522ERR_PINPAD_INVALID_KEY_FORMAT Pinpad error: Invalid key format
-111523ERR_PINPAD_SCR Pinpad error: General unicreditbulbank error in smart 
card reader
-111524ERR_PINPAD_HAL Pinpad error: Error code returned from HAL functions
-111525ERR_PINPAD_INVALID_KEY Pinpad error: Invalid key (may not be present)
-111526ERR_PINPAD_NO_PIN_DATA Pinpad error: The PIN length is less than 4 or bigger 
than 12
-111527ERR_PINPAD_INVALID_REMINDER Pinpad error: Issuer or ICC key invalid remainder 
length
-111528ERR_PINPAD_NOT_INIT Pinpad error: Not initialized (Not used in this FW 
version)
-111529ERR_PINPAD_LIMIT Pinpad error: Limit is reached (Not used in this FW 
version)
-111530ERR_PINPAD_INVALID_SEQUENCE Pinpad error: Invalid sequence (Not used in this FW 
version)
-111531ERR_PINPAD_NO_PERMITION Pinpad error: The action is not permitted
-111532ERR_PINPAD_NO_TMK Pinpad error: TMK is not loaded. The action cannot be
executed
-111533ERR_PINPAD_INVALID_KEK Pinpad error: Wrong key format
-111534ERR_PINPAD_DUPLICATE_KEY Pinpad error: Duplicated key
-111535ERR_PINPAD_KEYBOARD Pinpad error: General keyboard error
-111536ERR_PINPAD_KEYBOARD_NOT_CALIBRAT
EDPinpad error: The keyboard is no calibrated.
-111537ERR_PINPAD_KEYBOARD_FAILED Pinpad error: Keyboard bug detected.
-111538ERR_PINPAD_DEVICE_BUSY Pinpad error: The device is busy, try again
-111539ERR_PINPAD_TAMPERED Pinpad error: Device is tampered
-111540ERR_PINPAD_EMSR Pinpad error: Error in encrypted head
-111541ERR_PINPAD_ACCEPT Pinpad error: The button 'OK' is pressed
-111542ERR_PINPAD_INVALID_PAN Pinpad error: Wrong PAN
-111543ERR_PINPAD_NOT_ENOUGH_MEMORY Pinpad error: Out of memory
-111544ERR_PINPAD_EMV Pinpad error: EMV error
-111545ERR_PINPAD_CRYPTOGRAPHY Pinpad error: Cryptographic error
-111546ERR_PINPAD_COMMUNICATION Pinpad error: Communication error
-111547ERR_PINPAD_INVALID_VERSION Pinpad error: Invalid firmware version
-111548ERR_PINPAD_NOPAPER Pinpad error: Printer is out of paper
-111549ERR_PINPAD_OVERHEATED Pinpad error: Printer is overheated
-111550ERR_PINPAD_NOT_CONNECTED Pinpad error: Device is not connected
65


# Page 66

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
-111551ERR_PINPAD_USE_CHIP Pinpad error: Use the chip reader
-111552ERR_PINPAD_END_DAY Pinpad error: End the day first
-111554ERR_PINPAD_BOR_ERR Pinpad error: Error from Borica
-111555ERR_PINPAD_NO_CONN Pinpad error: No connection with pinpad
-111556ERR_PINPAD_ECR Pinpad error: Success in pinpad, unsuccess in ECR
-111557ERR_PINPAD_NOT_CONF Pinpad error: Not configured connection between 
fiscal device and PinPad
-111558ERR_PINPAD_SAME_TRANS Pinpad error: The last transactions are equals or 
connection is interrupted - try again.
-111559ERR_PINPAD_RECEIPT Pinpad error: Payment type: debit/credit card via 
PinPad. In the fiscal receipt is allowed only one 
payment with such type.
-111560ERR_PINPAD_FP_TRANS Pinpad error: Unknown result of the transaction 
between fiscal device and PinPad
-111561ERR_PINPAD_NOT_CONF_TYPE Pinpad error: Pinpad type not configured
-111700ERR_PINPAD_INV_AMOUNT Pinpad error: Invalid ammount.
-111701ERR_PINPAD_TRN_NOT_FOUND Pinpad error: Transaction not found.
-111702ERR_PINPAD_FILE_EMPTY Pinpad error: The file is empty.
-111703ERR_PINPAD_MAX_CASHBACK Entered cashback is bigger than cashback limit.
(111800 - 111899) SCALE REMOTE CONTROL
-111800ERR_SCALE_NOT_RESPOND ERR_SCALE_NOT_RESPOND
-111801ERR_SCALE_NOT_CALCULATED ERR_SCALE_NOT_CALCULATED
-111802ERR_SCALE_WRONG_RESPONSE ERR_SCALE_WRONG_RESPONSE
-111803ERR_SCALE_ZERO_WEIGHT ERR_SCALE_ZERO_WEIGHT
-111804ERR_SCALE_NEGATIVE_WEIGHT ERR_SCALE_NEGATIVE_WEIGHT
-111805ERR_SCALE_T_WRONG_INTF ERR_SCALE_T_WRONG_INTF
-111806ERR_SCALE_T_CONNECT ERR_SCALE_T_CONNECT
-111807ERR_SCALE_SEND ERR_SCALE_SEND
-111808ERR_SCALE_RECEIVE ERR_SCALE_RECEIVE
-111809ERR_SCALE_FILE_GENERATE ERR_SCALE_FILE_GENERATE
-111810ERR_SCALE_NOT_CONFIG ERR_SCALE_NOT_CONFIG
(111900 - 111999) NTP SERVER ERRORS
-111900ERR_NTP_NO_COMM Communication error wtih NTP server: Cannot make 
communication
-111901ERR_NTP_EARLIER_DATETIME Communication error wtih NTP server: The date and 
time is earlier than the last saved in the fiscal memory
-111902ERR_NTP_WRONG_IP Communication error wtih NTP server: Wrong IP 
address
(112000 - 112099) FP_MODE ERRORS
-112000ERR_FP_INVALID_COMMAND Fiscal printer error: Fiscal printer invalid command
-112001ERR_FP_INVALID_SYNTAX Fiscal printer error: Fiscal printer command invalid 
syntax
-112002ERR_FP_COMMAND_NOT_PERMITTED Fiscal printer error: Command is not permitted
66


# Page 67

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
-112003ERR_FP_OVERFLOW Fiscal printer error: Register overflow
-112004ERR_FP_WRONG_DATE_TIME Fiscal printer error: Wrong date/time
-112005ERR_FP_NEEDED_MODE_PC Fiscal printer error: PC mode is needed
-112006ERR_FP_NO_PAPER Fiscal printer error: No paper
-112007ERR_FP_COVER_IS_OPEN Fiscal printer error: Cover is open
-112008ERR_FP_PRINTER_FAILURE Fiscal printer error: Printing mechanism error
(112100 - 112199) FP_MODE ERRORS BY SYNTAX
-112100_ERR_FP_SYNTAX_PARAM_BEGIN _ERR_FP_SYNTAX_PARAM_BEGIN
-112101ERR_FP_SYNTAX_PARAM_1 Invalid syntax of parameter 1.
-112102ERR_FP_SYNTAX_PARAM_2 Invalid syntax of parameter 2.
-112103ERR_FP_SYNTAX_PARAM_3 Invalid syntax of parameter 3.
-112104ERR_FP_SYNTAX_PARAM_4 Invalid syntax of parameter 4.
-112105ERR_FP_SYNTAX_PARAM_5 Invalid syntax of parameter 5.
-112106ERR_FP_SYNTAX_PARAM_6 Invalid syntax of parameter 6.
-112107ERR_FP_SYNTAX_PARAM_7 Invalid syntax of parameter 7.
-112108ERR_FP_SYNTAX_PARAM_8 Invalid syntax of parameter 8.
-112109ERR_FP_SYNTAX_PARAM_9 Invalid syntax of parameter 9.
-112110ERR_FP_SYNTAX_PARAM_10 Invalid syntax of parameter 10.
-112111ERR_FP_SYNTAX_PARAM_11 Invalid syntax of parameter 11.
-112112ERR_FP_SYNTAX_PARAM_12 Invalid syntax of parameter 12.
-112113ERR_FP_SYNTAX_PARAM_13 Invalid syntax of parameter 13.
-112114ERR_FP_SYNTAX_PARAM_14 Invalid syntax of parameter 14.
-112115ERR_FP_SYNTAX_PARAM_15 Invalid syntax of parameter 15.
-112116ERR_FP_SYNTAX_PARAM_16 Invalid syntax of parameter 16.
-112199_ERR_FP_SYNTAX_PARAM_END _ERR_FP_SYNTAX_PARAM_END
(112200 - 112299) FP_MODE ERRORS BY VALUE
-112200_ERR_FP_BAD_PARAM_BEGIN _ERR_FP_BAD_PARAM_BEGIN
-112201ERR_FP_BAD_PARAM_1 Bad value of parameter 1.
-112202ERR_FP_BAD_PARAM_2 Bad value of parameter 2.
-112203ERR_FP_BAD_PARAM_3 Bad value of parameter 3.
-112204ERR_FP_BAD_PARAM_4 Bad value of parameter 4.
-112205ERR_FP_BAD_PARAM_5 Bad value of parameter 5.
-112206ERR_FP_BAD_PARAM_6 Bad value of parameter 6.
-112207ERR_FP_BAD_PARAM_7 Bad value of parameter 7.
-112208ERR_FP_BAD_PARAM_8 Bad value of parameter 8.
-112209ERR_FP_BAD_PARAM_9 Bad value of parameter 9.
-112210ERR_FP_BAD_PARAM_10 Bad value of parameter 10.
-112211ERR_FP_BAD_PARAM_11 Bad value of parameter 11.
-112212ERR_FP_BAD_PARAM_12 Bad value of parameter 12.
-112213ERR_FP_BAD_PARAM_13 Bad value of parameter 13.
-112214ERR_FP_BAD_PARAM_14 Bad value of parameter 14.
67


# Page 68

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
-112215ERR_FP_BAD_PARAM_15 Bad value of parameter 15.
-112216ERR_FP_BAD_PARAM_16 Bad value of parameter 16.
-112299_ERR_FP_BAD_PARAM_END _ERR_FP_BAD_PARAM_END
(112900 - 112999) EGAIS Module
-112900_ERR_RANGE_EM_BEGIN _ERR_RANGE_EM_BEGIN
-112999_ERR_RANGE_EM_END _ERR_RANGE_EM_END
(113000 - 113999) FLASH_MEMORY ERRORS
-113000ERR_FLASH_WRONG_ID Flash memory error: Reading ID error
-113001ERR_FLASH_WRONG_SIZE Flash memory error: Sector size error
(114000 - 114997) POS TERMINAL ERRORS
-114000ERR_POS_TERM_CHAN_CLOSED POS- terminal error: Communication channel is closed
(118000 - 118999) ONLINE ERRORS
-118000ERR_ECRSRV_NO_SOCKET_OPENED ECR server error: The connection socket is not open
-118001ERR_ECRSRV_SET_IS_NOT_TAKEN ECR server error: The set for this command is not 
opened
-118002ERR_ECRSRV_WRONG_PARAM ECR server error: Wrong parameter
-118003ERR_ECRSRV_NOT_SEND ECR server error: Socket send error. Could not send 
data to server
-118004ERR_ECRSRV_RECV_TMOUT ECR server error: Receiving timeout. No data is 
receivec on time
-118005ERR_ECRSRV_SOCKET_CLOSED ECR server error: Socket is closed
-118006ERR_ECRSRV_UNKNOWN ECR server error: Unknown state
-118007ERR_ECRSRV_FORBIDEN ECR server error: Forbidden operation
(120000 - 120999) PROGRAMMING ERROR
-120000ERR_PGM_NAME_NOT_UNIQUE Programming: Name is not unique!
-120001ERR_PGM_OPER_PASS_NOT_UNIQUE Programming: Operator password is not unique!
-120002ERR_PGM_DATETIME_OUT_OF_RANGE_MI
NProgramming: Date and time is under the range.
-120003ERR_PGM_DATETIME_OUT_OF_RANGE_M
AXProgramming: Date and time is under the range.
(121000 - 121099) COURIER ERRORS
-121000ERR_SCANNER_GENERAL Barcode scanner reading error!
-121001ERR_COURIER_EIK_INVALID Invalid EIK/EGN number!
(170000 - 170999) PENDRIVE ERRORS
-170000ERR_USB_HOST_INIT USB error: Host init error
-170001ERR_USB_NO_DEVICE USB error: No device
-170002ERR_USB_NO_FILESYSTEM USB error: No filesystem
-170003ERR_USB_FILE_OPEN USB error: File open error
68


# Page 69

       Datecs    FMP-350X, FMP-55X, FP-700X  , FP-700XE                                          Programmer’s Manual
                                        WP-500X, WP-50X, DP-25X, WP-25X, DP-150X, DP-05C
-170004ERR_USB_FILE_COPY USB error: File copy error
-170005ERR_FILE_UNPACK USB error: File unpack error
(171000 - 171999) RENTAL SERVICES
-171000ERR_RENTAL_NOT_FOUND Rental database: Not found
-171001ERR_RENTAL_FULL Rental database: Full
-171002ERR_RENTAL_POSITION_OCCUPIED Rental database: Position is occupied
-171003ERR_RENTAL_POSITION_FREE Rental database: Position is free
-171004ERR_RENTAL_SUBSCRIPTION_ACTIVE Rental database: Subscription is active
69
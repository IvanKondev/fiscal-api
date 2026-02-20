import sqlite3, json, re
conn = sqlite3.connect(r"data\print_gateway.sqlite")

# Find the latest correlation_id from PINPAD logs
cur = conn.execute("""
    SELECT context_json FROM logs 
    WHERE message LIKE 'PINPAD_TXLOOP_START%'
    ORDER BY id DESC LIMIT 1
""")
row = cur.fetchone()
if row:
    cid = json.loads(row[0]).get("correlation_id","")
else:
    cid = ""
print(f"Latest correlation_id: {cid}\n")

# Get ALL logs for this correlation_id
def show_flow(cid):
    cur = conn.execute("""
        SELECT id, level, message, context_json, created_at FROM logs 
        WHERE context_json LIKE ?
        ORDER BY id ASC
    """, (f"%{cid}%",))
    for r in cur.fetchall():
        ctx = json.loads(r[3]) if r[3] else {}
        msg = r[2]
        ts = r[4][11:19] if r[4] else ""
        lvl = r[1]
        
        if "SOCKET_OPEN" in msg and "FAIL" not in msg:
            print(f"  {r[0]} {ts} >> SOCKET_OPEN: {ctx.get('addr','')}:{ctx.get('port','')} type={ctx.get('type','')}")
        elif "SOCKET_CLOSE" in msg:
            print(f"  {r[0]} {ts} >> SOCKET_CLOSE: id={ctx.get('id','')}")
        elif "SOCKET_RECV" in msg:
            print(f"  {r[0]} {ts} << HOST_RECV: {ctx.get('len','')} bytes")
        elif "SOCKET_SEND" in msg and "FAIL" not in msg:
            print(f"  {r[0]} {ts} >> HOST_SEND: {ctx.get('len','')} bytes")
        elif "HOST_DATA_TOTAL" in msg:
            print(f"  {r[0]} {ts} ** HOST_DATA_TOTAL: {ctx.get('total_bytes','')} bytes")
        elif msg == "PINPAD_EXT_INTERNET_EVENT":
            sub = ctx.get("subevent","?")
            names = {"0x01": "SOCKET_OPEN", "0x02": "SOCKET_CLOSE", "0x03": "SEND_DATA"}
            print(f"  {r[0]} {ts} <- DEV_EVENT: {names.get(sub,sub)} data_len={ctx.get('data_len',0)}")
        elif msg == "PINPAD_SEND":
            cmd = ctx.get("cmd","?")
            plen = ctx.get("packet_len",0)
            dhex = ctx.get("data_hex","")[:30]
            print(f"  {r[0]} {ts} -> DEV_SEND: cmd={cmd} len={plen} [{dhex}]")
        elif msg == "PINPAD_RECV":
            st = ctx.get("status_name","?")
            dlen = ctx.get("data_len",0)
            if st != "errNoErr":
                print(f"  {r[0]} {ts} <- DEV_RECV: *** {st} *** data_len={dlen}")
            # skip errNoErr to reduce noise
        elif "TXLOOP_START" in msg:
            print(f"  {r[0]} {ts} == TXLOOP START (timeout={ctx.get('timeout_s','')}s) ==")
        elif "TXLOOP_END" in msg:
            print(f"  {r[0]} {ts} == TXLOOP END ==")
        elif "TXLOOP_PKT" in msg:
            ptype = ctx.get("pkt_type","?")
            rlen = ctx.get("raw_len",0)
            if ptype != "?":
                names = {"0x0E": "BORICA_EVT", "0x0F": "EXT_INET_EVT", "0x0B": "EMV_EVT"}
                print(f"  {r[0]} {ts} <- DEV_PKT: {names.get(ptype, ptype)} len={rlen}")
        elif msg == "PINPAD_EMV_EVENT":
            print(f"  {r[0]} {ts} <- EMV: \"{ctx.get('message','?')}\"")
        elif msg == "PINPAD_BORICA_EVENT":
            sn = ctx.get("subevent_name","?")
            print(f"  {r[0]} {ts} <- BORICA: {sn}")
        elif "TIMEOUT" in msg or "FAIL" in msg:
            print(f"  {r[0]} {ts} *** [{lvl}] {msg}: {json.dumps(ctx)[:120]}")
        elif "PRE_CHECK" in msg:
            print(f"  {r[0]} {ts} PRE_CHECK: reversal={ctx.get('has_reversal')}, eod={ctx.get('end_day_required')}, hang={ctx.get('has_hang_transaction')}")
        elif "PURCHASE_START" in msg or "EOD" in msg or "TEST" in msg:
            print(f"  {r[0]} {ts} ** {msg}: {json.dumps(ctx)[:120]}")
        elif "EVENT_DURING" in msg:
            print(f"  {r[0]} {ts} !! EVENT_DURING_CMD: got {ctx.get('got','?')}")

if cid:
    show_flow(cid)
else:
    print("No TXLOOP_START found")

# Also show last 5 error/warning logs
print("\n=== RECENT ERRORS ===")
cur = conn.execute("""
    SELECT id, message, context_json, created_at FROM logs 
    WHERE level IN ('error','warning') AND message LIKE 'PINPAD%'
    ORDER BY id DESC LIMIT 5
""")
for r in cur.fetchall():
    ctx = r[2][:150] if r[2] else ""
    print(f"  {r[0]} {r[3][11:19] if r[3] else ''} {r[1]}  {ctx}")

conn.close()

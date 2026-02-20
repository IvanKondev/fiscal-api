import sqlite3, json

conn = sqlite3.connect(r'd:\UnrealSoft\FiscalAPI\data\print_gateway.sqlite')
conn.row_factory = sqlite3.Row
c = conn.cursor()

# Last 3 jobs
print("=== LAST 3 JOBS ===")
c.execute("SELECT id,printer_id,payload_type,status,error,payload_json FROM jobs ORDER BY id DESC LIMIT 3")
for r in c.fetchall():
    d = dict(r)
    pj = d.pop('payload_json', '{}')
    print(d)
    payload = json.loads(pj or '{}')
    # Show UNP if present
    if payload.get('unp'):
        print(f"  UNP: {payload['unp']}")
    print()

# All logs for the last job (by correlation_id)
print("=== LAST JOB FULL LOG TRACE ===")
c.execute("SELECT id,level,message,context_json FROM logs ORDER BY id DESC LIMIT 40")
rows = list(c.fetchall())
rows.reverse()
for r in rows:
    d = dict(r)
    ctx_raw = d.get('context_json', '') or ''
    msg = d['message']
    if msg in ('DATECS_SEND', 'DATECS_PROTOCOL_RECV', 'JOB_SUCCESS', 'JOB_FAILED', 'JOB_PRINTING',
               'DATECS_FISCAL_JOB_START', 'DATECS_FISCAL_JOB_FAILED', 'DATECS_CLOSE_RESPONSE',
               'DATECS_STATUS_SUCCESS', 'DATECS_TRANSACTION_STATUS', 'DATECS_NRA_DATA_RESPONSE',
               'DATECS_OPEN_RECEIPT_DATA', 'DATECS_PAYMENT_INCOMPLETE', 'PRINT_SENT',
               'DATECS_SET_OPERATOR_NAME', 'DATECS_OPERATOR_INFO_SUCCESS'):
        try:
            ctx = json.loads(ctx_raw)
            # Trim long values
            for k, v in list(ctx.items()):
                if isinstance(v, str) and len(v) > 80:
                    ctx[k] = v[:60] + "..."
            print(f"#{d['id']} [{d['level']}] {msg}")
            print(f"  {ctx}")
        except:
            print(f"#{d['id']} [{d['level']}] {msg}: {ctx_raw[:200]}")

conn.close()

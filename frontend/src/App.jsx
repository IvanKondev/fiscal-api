import { useEffect, useMemo, useState } from "react";

const API_BASE = "/api";

const defaultForm = {
  name: "",
  model: "datecs_fp700mx",
  transport: "serial",
  port: "",
  baudrate: "115200",
  ip_address: "",
  tcp_port: "4999",
  operator_id: "2",
  operator_password: "0000",
  operator_till: "2",
  enabled: true,
  dry_run: false,
  serial_number: "",
  firmware: "",
};

const taxOptions = [
  { value: "А", label: "А - 20%" },
  { value: "Б", label: "Б - 20%" },
  { value: "В", label: "В - 9%" },
  { value: "Г", label: "Г - 0%" },
];

const createFiscalItem = (overrides = {}) => ({
  name: "",
  tax: "Б",
  price: "",
  qty: "1",
  unit: "",
  discount: "",
  ...overrides,
});

const createPayment = (overrides = {}) => ({ type: "P", amount: "", ...overrides });

const toNumber = (value) => {
  const num = Number.parseFloat(String(value).replace(",", "."));
  return Number.isFinite(num) ? num : 0;
};

const parseDiscount = (discount, lineTotal) => {
  if (discount === null || discount === undefined || discount === "") return 0;
  let raw = String(discount).trim();
  if (!raw) return 0;
  let sign = 1;
  if (raw.startsWith("-")) {
    sign = -1;
    raw = raw.slice(1);
  } else if (raw.startsWith("+")) {
    raw = raw.slice(1);
  }
  if (!raw) return 0;
  if (raw.endsWith("%")) {
    const percent = toNumber(raw.slice(0, -1));
    return (lineTotal * percent) / 100 * sign;
  }
  return toNumber(raw) * sign;
};

const formatDeltaSeconds = (deltaSeconds) => {
  if (deltaSeconds === null || deltaSeconds === undefined) return "—";
  const sign = deltaSeconds >= 0 ? "+" : "-";
  const abs = Math.abs(deltaSeconds);
  const hours = Math.floor(abs / 3600);
  const minutes = Math.floor((abs % 3600) / 60);
  const seconds = Math.floor(abs % 60);
  if (hours > 0) {
    return `${sign}${String(hours).padStart(2, "0")}:${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
  }
  if (minutes > 0) {
    return `${sign}${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
  }
  return `${sign}${seconds}s`;
};

const calculateFiscalTotal = (items) =>
  items.reduce((sum, item) => {
    const price = toNumber(item.price);
    const qty = toNumber(item.qty || 1);
    if (!price || !qty) return sum;
    const lineTotal = price * qty;
    return sum + lineTotal + parseDiscount(item.discount, lineTotal);
  }, 0);

const paymentOptions = [
  { value: "P", label: "P - Cash" },
  { value: "N", label: "N - Card" },
  { value: "C", label: "C - Cheque" },
  { value: "D", label: "D - Coupon" },
  { value: "I", label: "I - Add. 1" },
  { value: "J", label: "J - Add. 2" },
  { value: "K", label: "K - Add. 3" },
  { value: "L", label: "L - Add. 4" },
];

const modelLabel = (model) => {
  const labels = {
    datecs_fp700mx: "Datecs FP700MX",
    datecs_fp2000: "Datecs FP2000",
    datecs_fp700x: "Datecs FP700X",
    datecs_fp700xe: "Datecs FP700XE",
    datecs_fmp350x: "Datecs FMP350X",
    datecs_fmp55x: "Datecs FMP55X",
    datecs_wp500x: "Datecs WP500X",
    datecs_wp50x: "Datecs WP50X",
    datecs_dp25x: "Datecs DP25X",
    datecs_wp25x: "Datecs WP25X",
    datecs_dp150x: "Datecs DP150X",
    datecs_dp05c: "Datecs DP05C",
    datecs_fp800: "Datecs FP800",
    datecs_fp650: "Datecs FP650",
    datecs_sk1_21f: "Datecs SK1-21F",
    datecs_sk1_31f: "Datecs SK1-31F",
    datecs_fmp10: "Datecs FMP10",
    datecs_fp700: "Datecs FP700",
    datecspay_bluepad: "DatecsPay BluePad",
  };
  return labels[model] || model;
};
const printerLabel = (printer) => {
  if (!printer) return "";
  const conn = printer.transport === "lan"
    ? `${printer.ip_address || "?"}:${printer.tcp_port || 4999}`
    : printer.port || "-";
  return `${printer.name} (${conn})`;
};

function parseError(message) {
  if (!message) return "Unexpected error";
  try {
    const parsed = JSON.parse(message);
    if (parsed?.detail) return parsed.detail;
  } catch {
    // ignore
  }
  return message;
}

async function apiRequest(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });
  if (response.ok) {
    if (response.status === 204) return null;
    return response.json();
  }
  const text = await response.text();
  throw new Error(parseError(text));
}

const RECEIPT_WIDTH = 42;
const receiptLine = (char = "-") => char.repeat(RECEIPT_WIDTH);
const receiptCenter = (text) => {
  const pad = Math.max(0, RECEIPT_WIDTH - text.length);
  const left = Math.floor(pad / 2);
  return " ".repeat(left) + text;
};
const receiptRow = (left, right) => {
  const gap = RECEIPT_WIDTH - left.length - right.length;
  if (gap < 1) return left + " " + right;
  return left + " ".repeat(gap) + right;
};
const fmtAmount = (v) => {
  const n = Number.parseFloat(String(v).replace(",", "."));
  return Number.isFinite(n) ? n.toFixed(2) : String(v);
};
const paymentLabel = (type) => {
  const map = { P: "В БРОЙ", N: "КАРТА", C: "ЧЕК", D: "КУПОН", I: "ДОП.1", J: "ДОП.2", K: "ДОП.3", L: "ДОП.4" };
  return map[String(type).toUpperCase()] || type;
};
const taxLabel = (tax) => {
  const raw = String(tax || "Б").trim().toUpperCase();
  const map = { "А": "А", "Б": "Б", "В": "В", "Г": "Г", A: "А", B: "Б", C: "В", D: "Г", "1": "А", "2": "Б", "3": "В", "4": "Г" };
  return map[raw] || raw;
};

function ReceiptPreview({ job, printerName, onClose }) {
  if (!job) return null;
  const { payload_type, payload, result, created_at } = job;
  const lines = [];
  const dateStr = new Date(created_at).toLocaleString("bg-BG", { dateStyle: "short", timeStyle: "medium" });

  if (payload_type === "fiscal_receipt") {
    const op = payload.operator || {};
    lines.push(receiptCenter("ФИСКАЛЕН БОН"));
    lines.push(receiptLine("="));
    if (printerName) lines.push(receiptCenter(printerName));
    lines.push(receiptCenter(dateStr));
    if (op.id) lines.push(`Оператор: ${op.id}`);
    lines.push(receiptLine("-"));
    const items = payload.items || [];
    let total = 0;
    for (const item of items) {
      const price = toNumber(item.price);
      const qty = toNumber(item.qty || 1);
      const lineTotal = price * qty;
      const disc = parseDiscount(item.discount, lineTotal);
      const finalTotal = lineTotal + disc;
      total += finalTotal;
      const name = String(item.name || "").substring(0, 28);
      const tax = taxLabel(item.tax);
      lines.push(name);
      const qtyStr = `  ${qty.toFixed(3)} x ${price.toFixed(2)}`;
      lines.push(receiptRow(qtyStr, `${tax} ${finalTotal.toFixed(2)}`));
      if (disc !== 0) {
        lines.push(receiptRow("    отстъпка", disc.toFixed(2)));
      }
    }
    lines.push(receiptLine("-"));
    lines.push(receiptRow("СУМА", `${total.toFixed(2)} лв`));
    lines.push(receiptLine("="));
    const payments = payload.payments || [];
    for (const pay of payments) {
      lines.push(receiptRow(paymentLabel(pay.type), `${fmtAmount(pay.amount)} лв`));
    }
    const paidTotal = payments.reduce((s, p) => s + toNumber(p.amount), 0);
    const change = paidTotal - total;
    if (change > 0.005) {
      lines.push(receiptRow("РЕСТО", `${change.toFixed(2)} лв`));
    }
    lines.push(receiptLine("-"));
    if (payload.nsale) lines.push(`УНП: ${payload.nsale}`);
    if (payload.invoice) lines.push("ФАКТУРА");
    if (result?.receipt_number) lines.push(`Бон №: ${result.receipt_number}`);
    lines.push(receiptCenter("* ФИСКАЛЕН БОН *"));
  } else if (payload_type === "storno") {
    const op = payload.operator || {};
    lines.push(receiptCenter("СТОРНО БОН"));
    lines.push(receiptLine("="));
    if (printerName) lines.push(receiptCenter(printerName));
    lines.push(receiptCenter(dateStr));
    if (op.id) lines.push(`Оператор: ${op.id}`);
    const orig = payload.original || {};
    if (orig.doc_no) lines.push(`Ориг. док: ${orig.doc_no}`);
    if (orig.date) lines.push(`Ориг. дата: ${orig.date}`);
    if (orig.unp) lines.push(`Ориг. УНП: ${orig.unp}`);
    lines.push(receiptLine("-"));
    const items = payload.items || [];
    let total = 0;
    for (const item of items) {
      const price = toNumber(item.price);
      const qty = toNumber(item.qty || 1);
      const lineTotal = price * qty;
      total += lineTotal;
      lines.push(String(item.name || "").substring(0, 28));
      lines.push(receiptRow(`  ${qty.toFixed(3)} x ${price.toFixed(2)}`, `${taxLabel(item.tax)} ${lineTotal.toFixed(2)}`));
    }
    lines.push(receiptLine("-"));
    lines.push(receiptRow("СУМА СТОРНО", `${total.toFixed(2)} лв`));
    lines.push(receiptLine("="));
    const payments = payload.payments || [];
    for (const pay of payments) {
      lines.push(receiptRow(paymentLabel(pay.type), `${fmtAmount(pay.amount)} лв`));
    }
    lines.push(receiptLine("-"));
    lines.push(receiptCenter("* СТОРНО *"));
  } else if (payload_type === "text") {
    lines.push(receiptCenter("СЛУЖЕБЕН БОН"));
    lines.push(receiptLine("="));
    if (printerName) lines.push(receiptCenter(printerName));
    lines.push(receiptCenter(dateStr));
    lines.push(receiptLine("-"));
    for (const line of (payload.lines || [])) {
      lines.push(String(line));
    }
    lines.push(receiptLine("-"));
    lines.push(receiptCenter("* НЕФИСКАЛЕН *"));
  } else if (payload_type === "receipt") {
    lines.push(receiptCenter("БОН"));
    lines.push(receiptLine("="));
    for (const h of (payload.header || [])) {
      lines.push(receiptCenter(String(h)));
    }
    lines.push(receiptLine("-"));
    for (const item of (payload.items || [])) {
      const name = String(item.name || "");
      const qty = item.qty != null ? `${item.qty}x` : "";
      const price = item.price != null ? fmtAmount(item.price) : "";
      const total = item.total != null ? fmtAmount(item.total) : "";
      if (qty && price) {
        lines.push(name);
        lines.push(receiptRow(`  ${qty} ${price}`, total));
      } else {
        lines.push(receiptRow(name, total || price));
      }
    }
    lines.push(receiptLine("-"));
    for (const t of (payload.totals || [])) {
      lines.push(receiptRow(String(t.label || ""), String(t.value || "")));
    }
    lines.push(receiptLine("="));
    for (const f of (payload.footer || [])) {
      lines.push(receiptCenter(String(f)));
    }
  } else if (payload_type === "report") {
    const rType = String(payload.type || payload.option || "X").toUpperCase();
    const reportName = rType === "Z" ? "Z-ОТЧЕТ (Дневен финансов)" : "X-ОТЧЕТ (Текущ)";
    lines.push(receiptCenter(reportName));
    lines.push(receiptLine("="));
    if (printerName) lines.push(receiptCenter(printerName));
    lines.push(receiptCenter(dateStr));
    lines.push(receiptLine("-"));
    lines.push(receiptCenter(`Тип: ${rType}`));
    if (rType === "Z") {
      lines.push("");
      lines.push(receiptCenter("Нулиране на регистрите"));
    }
    lines.push(receiptLine("-"));
    lines.push(receiptCenter(`* ${reportName} *`));
  } else if (payload_type === "cash") {
    const dir = String(payload.direction || "in").toLowerCase();
    const isIn = dir === "in" || dir === "deposit";
    const title = isIn ? "СЛУЖЕБЕН ВНОС" : "СЛУЖЕБЕН ИЗНОС";
    lines.push(receiptCenter(title));
    lines.push(receiptLine("="));
    if (printerName) lines.push(receiptCenter(printerName));
    lines.push(receiptCenter(dateStr));
    lines.push(receiptLine("-"));
    lines.push(receiptRow(isIn ? "Внос:" : "Износ:", `${fmtAmount(payload.amount)} лв`));
    lines.push(receiptLine("-"));
    lines.push(receiptCenter(`* ${title} *`));
  } else {
    lines.push(receiptCenter("НЕИЗВЕСТЕН ТИП"));
    lines.push(receiptLine("-"));
    lines.push(JSON.stringify(payload, null, 2));
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="receipt-modal" onClick={(e) => e.stopPropagation()}>
        <div className="receipt-paper">
          <div className="receipt-tear-top" />
          <pre className="receipt-content">
            {lines.join("\n")}
          </pre>
          <div className="receipt-tear-bottom" />
        </div>
        <div className="receipt-modal-actions">
          <button className="small" onClick={onClose}>Затвори</button>
        </div>
      </div>
    </div>
  );
}

function App() {
  const [activeTab, setActiveTab] = useState("Printers");
  const [printers, setPrinters] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [logs, setLogs] = useState([]);
  const [form, setForm] = useState(defaultForm);
  const [editingId, setEditingId] = useState(null);
  const [status, setStatus] = useState({ type: "info", message: "" });
  const [loading, setLoading] = useState(false);
  const [fiscalLoading, setFiscalLoading] = useState(false);
  const [reportLoading, setReportLoading] = useState(false);
  const [fiscalSale, setFiscalSale] = useState({
    printerId: "",
    operator: { id: "", password: "", till: "", name: "" },
    items: [createFiscalItem()],
    payments: [createPayment()],
  });
  const [reportForm, setReportForm] = useState({
    printerId: "",
    reportType: "Z",
    startDate: "",
    endDate: "",
    cashAmount: "",
    cashType: "in",
  });
  const [stornoForm, setStornoForm] = useState({
    printerId: "",
    operator: { id: "", password: "", till: "" },
    stornoType: "0",
    original: { doc_no: "", date: "", fm: "", unp: "" },
    items: [createFiscalItem()],
    payments: [createPayment()],
  });
  const [stornoLoading, setStornoLoading] = useState(false);
  const [printerStatuses, setPrinterStatuses] = useState({});
  const [printerTimes, setPrinterTimes] = useState({});
  const [modal, setModal] = useState({ show: false, title: "", message: "", onConfirm: null });
  const [availablePorts, setAvailablePorts] = useState([]);
  const [previewJob, setPreviewJob] = useState(null);
  const [detectingPorts, setDetectingPorts] = useState({});
  const [renamingPrinter, setRenamingPrinter] = useState({ id: null, name: "" });
  const [lanDetectState, setLanDetectState] = useState({ status: "idle", result: null });
  const [mqttStatus, setMqttStatus] = useState({ enabled: false, connected: false });
  const [mqttMessages, setMqttMessages] = useState([]);
  const [mqttPublishTopic, setMqttPublishTopic] = useState("restaurant/1/bills/closed");
  const [mqttPublishPayload, setMqttPublishPayload] = useState('{"bill_id": 1, "waiter_id": 1}');
  const [mqttPublishing, setMqttPublishing] = useState(false);
  const [pinpadForm, setPinpadForm] = useState({ printerId: "", amount: "", tip: "", rrn: "", auth_id: "" });
  const [pinpadInfo, setPinpadInfo] = useState(null);
  const [pinpadStatus, setPinpadStatus] = useState(null);
  const [pinpadLoading, setPinpadLoading] = useState(false);
  const [pinpadResult, setPinpadResult] = useState(null);
  const [supportedModels, setSupportedModels] = useState(["datecs_fp700mx"]);
  const [lanForm, setLanForm] = useState({ ip_address: "", tcp_port: "4999", name: "", model: "", operator_id: "1", operator_password: "0000", operator_till: "1" });
  const [lanDetecting, setLanDetecting] = useState(false);
  const [lanDetectResult, setLanDetectResult] = useState(null);
  const [lanAdding, setLanAdding] = useState(false);

  const statusClass = status.type ? `status ${status.type}` : "status";
  const fiscalTotal = useMemo(
    () => calculateFiscalTotal(fiscalSale.items),
    [fiscalSale.items]
  );
  const fiscalPaymentTotal = useMemo(
    () =>
      fiscalSale.payments.reduce(
        (sum, payment) => sum + toNumber(payment.amount),
        0
      ),
    [fiscalSale.payments]
  );
  const fiscalRemaining = Math.max(0, fiscalTotal - fiscalPaymentTotal);
  const stornoTotal = useMemo(
    () => calculateFiscalTotal(stornoForm.items),
    [stornoForm.items]
  );
  const stornoPaymentTotal = useMemo(
    () =>
      stornoForm.payments.reduce(
        (sum, payment) => sum + toNumber(payment.amount),
        0
      ),
    [stornoForm.payments]
  );
  const stornoRemaining = Math.max(0, stornoTotal - stornoPaymentTotal);

  const refreshPrinters = async () => {
    const data = await apiRequest("/printers");
    setPrinters(data);
  };

  const refreshJobs = async () => {
    const data = await apiRequest("/jobs?limit=100");
    setJobs(data);
  };

  const refreshLogs = async () => {
    const data = await apiRequest("/logs?limit=200");
    setLogs(data);
  };

  const refreshMqtt = async () => {
    try {
      const [st, msgs] = await Promise.all([
        apiRequest("/mqtt/status"),
        apiRequest("/mqtt/messages?limit=50"),
      ]);
      setMqttStatus(st);
      setMqttMessages(msgs);
    } catch { /* ignore */ }
  };

  const getPrinterOperator = (printerId) => {
    const printer = printers.find((entry) => entry.id === Number(printerId));
    return printer?.config?.operator;
  };

  const buildPrinterOperator = (printerId) => {
    const operator = getPrinterOperator(printerId);
    if (!operator) return null;
    return {
      id: operator.id?.toString() || "",
      password: operator.password?.toString() || "",
      till: operator.till?.toString() || "",
      name: operator.name?.toString() || "",
    };
  };

  const ensureOperator = (printerId, operator) => {
    if (operator) return;
    if (!getPrinterOperator(printerId)) {
      throw new Error("Операторът е задължителен за фискални операции.");
    }
  };

  const updateFiscalSaleOperator = (field, value) => {
    setFiscalSale((current) => ({
      ...current,
      operator: { ...current.operator, [field]: value },
    }));
  };

  const updateFiscalSaleItem = (index, field, value) => {
    setFiscalSale((current) => {
      const items = current.items.map((item, idx) =>
        idx === index ? { ...item, [field]: value } : item
      );
      return { ...current, items };
    });
  };

  const addFiscalSaleItem = () => {
    setFiscalSale((current) => ({
      ...current,
      items: [...current.items, createFiscalItem()],
    }));
  };

  const removeFiscalSaleItem = (index) => {
    setFiscalSale((current) => ({
      ...current,
      items: current.items.filter((_, idx) => idx !== index),
    }));
  };

  const updateFiscalSalePayment = (index, field, value) => {
    setFiscalSale((current) => {
      const payments = current.payments.map((payment, idx) =>
        idx === index ? { ...payment, [field]: value } : payment
      );
      return { ...current, payments };
    });
  };

  const addFiscalSalePayment = () => {
    setFiscalSale((current) => ({
      ...current,
      payments: [...current.payments, createPayment()],
    }));
  };

  const removeFiscalSalePayment = (index) => {
    setFiscalSale((current) => ({
      ...current,
      payments: current.payments.filter((_, idx) => idx !== index),
    }));
  };

  const applyFiscalTotal = () => {
    const remaining = fiscalRemaining;
    if (remaining <= 0) return;
    setFiscalSale((current) => {
      const payments = [...current.payments];
      if (payments.length === 0) {
        payments.push({ type: "P", amount: remaining.toFixed(2) });
      } else {
        const lastPayment = payments[payments.length - 1];
        lastPayment.amount = (toNumber(lastPayment.amount) + remaining).toFixed(2);
      }
      return { ...current, payments };
    });
  };

  const collectOperator = (operator, { requireTill = true } = {}) => {
    const trimmed = {
      id: operator.id?.trim() || "",
      password: operator.password?.trim() || "",
      till: operator.till?.trim() || "",
    };
    if (!trimmed.id && !trimmed.password && !trimmed.till) {
      return { value: null, error: null };
    }
    if (!trimmed.id || !trimmed.password || (requireTill && !trimmed.till)) {
      return {
        value: null,
        error: requireTill
          ? "Операторът изисква ID, парола и каса."
          : "Операторът изисква ID и парола.",
      };
    }
    return { value: trimmed, error: null };
  };

  const computeFiscalValidation = () => {
    const errors = {};
    if (!fiscalSale.printerId) {
      errors.printerId = "Избери принтер.";
    }
    
    const operatorCheck = collectOperator(fiscalSale.operator, { requireTill: true });
    const operator = operatorCheck.value;
    
    if (!operator) {
      errors.operator = "Попълни оператор ID, парола и каса.";
    }
    const itemErrors = fiscalSale.items.map((item) =>
      !item.name?.trim() || item.price === "" || item.price === null
    );
    const items = fiscalSale.items
      .filter((item) => item.name && item.price !== "" && item.price !== null)
      .map((item) => ({
        name: item.name,
        vat_group: item.tax,
        price: item.price,
        quantity: item.qty,
        unit: item.unit,
        discount: item.discount,
      }));
    if (items.length === 0) {
      errors.items = "Добави поне един артикул с цена.";
    }
    const paymentErrors = fiscalSale.payments.map(
      (payment) => !payment.type || payment.amount === "" || payment.amount === null
    );
    const payments = fiscalSale.payments
      .filter((payment) => payment.type && payment.amount !== "" && payment.amount !== null)
      .map((payment) => ({
        type: payment.type,
        amount: payment.amount,
      }));
    if (payments.length === 0) {
      errors.payments = "Добави поне един тип плащане.";
    }
    if (!errors.payments) {
      const total = calculateFiscalTotal(items);
      const paid = payments.reduce((sum, payment) => sum + toNumber(payment.amount), 0);
      if (total > 0 && paid < total) {
        errors.payments = `Плащането е по-малко от тотала (${total.toFixed(2)}).`;
      }
    }
    const payload = {
      operator_id: operator?.id,
      operator_password: operator?.password,
      operator_till: operator?.till,
      operator_name: fiscalSale.operator.name?.trim() || undefined,
      nsale: fiscalSale.nsale?.trim() || undefined,
      items,
      payments,
    };
    return {
      errors,
      itemErrors,
      paymentErrors,
      payload,
    };
  };

  const submitFiscalSale = async (event) => {
    event.preventDefault();
    const validation = computeFiscalValidation();
    if (Object.keys(validation.errors).length > 0) {
      setStatus({
        type: "error",
        message: "Поправи маркираните полета преди изпращане.",
      });
      return;
    }
    setFiscalLoading(true);
    setStatus({ type: "info", message: "Изпращам фискален бон..." });
    try {
      const payload = validation.payload;
      ensureOperator(fiscalSale.printerId, payload.operator);

      const job = await apiRequest("/jobs", {
        method: "POST",
        body: JSON.stringify({
          printer_id: Number(fiscalSale.printerId),
          payload_type: "fiscal_receipt",
          payload,
        }),
      });
      setStatus({
        type: "success",
        message: `Фискален бон е изпратен (Job #${job.id}).`,
      });
    } catch (error) {
      setStatus({ type: "error", message: error.message });
    } finally {
      setFiscalLoading(false);
    }
  };

  const submitReport = async (event) => {
    event.preventDefault();
    if (!reportForm.printerId) {
      setStatus({ type: "error", message: "Избери принтер." });
      return;
    }
    setReportLoading(true);
    setStatus({ type: "info", message: "Изпращам отчет..." });
    try {
      const payload = {
        type: reportForm.reportType,
      };
      if (reportForm.startDate) payload.start_date = reportForm.startDate;
      if (reportForm.endDate) payload.end_date = reportForm.endDate;
      
      const job = await apiRequest("/jobs", {
        method: "POST",
        body: JSON.stringify({
          printer_id: Number(reportForm.printerId),
          payload_type: "report",
          payload,
        }),
      });
      setStatus({ type: "success", message: `Отчет изпратен (Job #${job.id}).` });
    } catch (error) {
      setStatus({ type: "error", message: error.message });
    } finally {
      setReportLoading(false);
    }
  };

  const submitStorno = async (event) => {
    event.preventDefault();
    if (!stornoForm.printerId) {
      setStatus({ type: "error", message: "Избери принтер." });
      return;
    }
    const operatorCheck = collectOperator(stornoForm.operator, { requireTill: true });
    const operator = operatorCheck.value;
    if (!operator) {
      setStatus({ type: "error", message: "Попълни оператор ID, парола и каса." });
      return;
    }
    const items = stornoForm.items
      .filter((item) => item.name && item.price !== "" && item.price !== null)
      .map((item) => ({
        name: item.name,
        vat_group: item.tax,
        price: item.price,
        quantity: item.qty,
        unit: item.unit,
        discount: item.discount,
      }));
    if (items.length === 0) {
      setStatus({ type: "error", message: "Добави поне един артикул." });
      return;
    }
    const payments = stornoForm.payments
      .filter((payment) => payment.type && payment.amount !== "" && payment.amount !== null)
      .map((payment) => ({
        type: payment.type,
        amount: payment.amount,
      }));
    if (payments.length === 0) {
      setStatus({ type: "error", message: "Добави поне едно плащане." });
      return;
    }
    setStornoLoading(true);
    setStatus({ type: "info", message: "Изпращам сторно бележка..." });
    try {
      const payload = {
        operator_id: operator.id,
        operator_password: operator.password,
        operator_till: operator.till,
        storno_type: stornoForm.stornoType,
        original: stornoForm.original,
        items,
        payments,
      };
      const job = await apiRequest("/jobs", {
        method: "POST",
        body: JSON.stringify({
          printer_id: Number(stornoForm.printerId),
          payload_type: "storno",
          payload,
        }),
      });
      setStatus({ type: "success", message: `Сторно бележка изпратена (Job #${job.id}).` });
    } catch (error) {
      setStatus({ type: "error", message: error.message });
    } finally {
      setStornoLoading(false);
    }
  };

  const retryJob = async (jobId) => {
    try {
      await apiRequest(`/jobs/${jobId}/retry`, { method: "POST" });
      setStatus({ type: "success", message: `Job #${jobId} опашката за повторно изпълнение.` });
      await refreshJobs();
    } catch (error) {
      setStatus({ type: "error", message: error.message });
    }
  };

  const cancelJob = async (jobId) => {
    if (!window.confirm("Сигурен ли си, че искаш да откажеш този job?")) {
      return;
    }
    try {
      await apiRequest(`/jobs/${jobId}/cancel`, { method: "POST" });
      setStatus({ type: "success", message: `Job #${jobId} беше отказан.` });
      await refreshJobs();
    } catch (error) {
      setStatus({ type: "error", message: error.message });
    }
  };

  const submitCashOperation = async (event) => {
    event.preventDefault();
    if (!reportForm.printerId) {
      setStatus({ type: "error", message: "Избери принтер." });
      return;
    }
    if (!reportForm.cashAmount || Number(reportForm.cashAmount) <= 0) {
      setStatus({ type: "error", message: "Въведи валидна сума." });
      return;
    }
    setReportLoading(true);
    setStatus({ type: "info", message: "Изпращам служебна операция..." });
    try {
      const job = await apiRequest("/jobs", {
        method: "POST",
        body: JSON.stringify({
          printer_id: Number(reportForm.printerId),
          payload_type: "cash",
          payload: {
            type: reportForm.cashType,
            amount: Number(reportForm.cashAmount),
          },
        }),
      });
      setStatus({ type: "success", message: `Служебна операция изпратена (Job #${job.id}).` });
      setReportForm((current) => ({ ...current, cashAmount: "" }));
    } catch (error) {
      setStatus({ type: "error", message: error.message });
    } finally {
      setReportLoading(false);
    }
  };

  const refreshModels = async () => {
    try {
      const data = await apiRequest("/tools/models");
      if (data.models && data.models.length > 0) setSupportedModels(data.models);
    } catch { /* keep fallback */ }
  };

  const refreshAll = async () => {
    await Promise.all([refreshPrinters(), refreshLogs()]);
  };

  const pinpadAction = async (action, body = {}) => {
    if (!pinpadForm.printerId) {
      setStatus({ type: "error", message: "Избери устройство." });
      return;
    }
    setPinpadLoading(true);
    setPinpadResult(null);
    const labels = {
      ping: "Ping...", info: "Зареждам инфо...", status: "Зареждам статус...",
      purchase: "Плащане с карта...", void: "Анулиране...",
      "end-of-day": "Край на деня...", "test-connection": "Тест връзка...",
    };
    setStatus({ type: "info", message: labels[action] || action });
    try {
      const isPost = ["ping", "purchase", "void", "end-of-day", "test-connection"].includes(action);
      const opts = isPost ? { method: "POST", body: JSON.stringify(body) } : {};
      const result = await apiRequest(`/printers/${pinpadForm.printerId}/pinpad/${action}`, opts);
      if (action === "info") setPinpadInfo(result);
      else if (action === "status") setPinpadStatus(result);
      else setPinpadResult(result);
      const ok = result?.alive !== false && result?.approved !== false;
      const msg = result?.result_message || (result?.alive ? "Pinpad OK" : JSON.stringify(result, null, 2).substring(0, 200));
      setStatus({ type: ok ? "success" : "warning", message: msg });
    } catch (error) {
      setStatus({ type: "error", message: error.message });
    } finally {
      setPinpadLoading(false);
    }
  };

  const detectPrinterOnPort = async (portDevice) => {
    setDetectingPorts((prev) => ({ ...prev, [portDevice]: "detecting" }));
    try {
      const result = await apiRequest("/tools/detect-printer", {
        method: "POST",
        body: JSON.stringify({ port: portDevice }),
      });
      if (result.detected) {
        setDetectingPorts((prev) => ({ ...prev, [portDevice]: result }));
        return result;
      } else {
        setDetectingPorts((prev) => ({ ...prev, [portDevice]: "not_found" }));
        return null;
      }
    } catch {
      setDetectingPorts((prev) => ({ ...prev, [portDevice]: "error" }));
      return null;
    }
  };

  const detectSerialPorts = async () => {
    try {
      setLoading(true);
      setDetectingPorts({});
      const data = await apiRequest("/tools/serial-ports");
      const ports = data.ports || [];
      setAvailablePorts(ports);
      if (ports.length === 0) {
        setStatus({ type: "warning", message: "Не са намерени COM портове" });
        return;
      }
      setStatus({ type: "info", message: `Намерени ${ports.length} порта, разпознаване...` });

      const usedPorts = new Set(printers.map((p) => p.port));
      const freePorts = ports.filter((p) => !usedPorts.has(p.device));

      const results = await Promise.allSettled(
        freePorts.map((p) => detectPrinterOnPort(p.device))
      );
      const detected = results.filter(
        (r) => r.status === "fulfilled" && r.value
      ).length;
      if (detected > 0) {
        setStatus({
          type: "success",
          message: `Разпознати ${detected} принтер${detected > 1 ? "а" : ""}`,
        });
      } else {
        setStatus({
          type: "success",
          message: `Намерени ${ports.length} порта (няма разпознати Datecs принтери)`,
        });
      }
    } catch (error) {
      setStatus({ type: "error", message: `Грешка при откриване: ${error.message}` });
      setAvailablePorts([]);
    } finally {
      setLoading(false);
    }
  };

  const detectPrinterOnLan = async () => {
    const ip = form.ip_address?.trim();
    const port = Number(form.tcp_port) || 4999;
    if (!ip) {
      setStatus({ type: "error", message: "Въведете IP адрес за откриване." });
      return;
    }
    setLanDetectState({ status: "detecting", result: null });
    try {
      const result = await apiRequest("/tools/detect-printer-lan", {
        method: "POST",
        body: JSON.stringify({ ip_address: ip, tcp_port: port }),
      });
      if (result.detected) {
        setLanDetectState({ status: "found", result });
        setForm((prev) => ({
          ...prev,
          name: prev.name || `${result.name} LAN`,
          model: result.model || prev.model,
          serial_number: result.serial_number || prev.serial_number || "",
          firmware: result.firmware || prev.firmware || "",
        }));
        setStatus({ type: "success", message: `Разпознат ${result.name} на ${ip}:${port}` });
      } else {
        setLanDetectState({ status: "not_found", result: null });
        setStatus({ type: "warning", message: result.error || "Не е открит принтер на този адрес." });
      }
    } catch (error) {
      setLanDetectState({ status: "error", result: null });
      setStatus({ type: "error", message: `Грешка при LAN откриване: ${error.message}` });
    }
  };

  const checkPrinterStatus = async (printerId) => {
    try {
      const status = await apiRequest(`/printers/${printerId}/status`);
      setPrinterStatuses((prev) => ({ ...prev, [printerId]: status }));
    } catch (error) {
      setPrinterStatuses((prev) => ({
        ...prev,
        [printerId]: {
          status: "error",
          message: error.message,
          issues: ["connection_error"],
        },
      }));
    }
  };

  const updatePrinterTimeState = (printerId, updates) => {
    setPrinterTimes((prev) => ({
      ...prev,
      [printerId]: { ...(prev[printerId] || {}), ...updates },
    }));
  };

  const readPrinterTime = async (printerId, { silent = false } = {}) => {
    updatePrinterTimeState(printerId, { loading: true, error: null });
    try {
      const data = await apiRequest(`/printers/${printerId}/datetime`);
      updatePrinterTimeState(printerId, {
        ...data,
        loading: false,
        error: null,
        fetchedAt: new Date().toISOString(),
      });
      if (!silent) {
        setStatus({ type: "success", message: "Прочетен час от принтера." });
      }
    } catch (error) {
      updatePrinterTimeState(printerId, { loading: false, error: error.message });
      if (!silent) {
        setStatus({ type: "error", message: error.message });
      }
    }
  };

  const syncPrinterTime = async (printerId) => {
    updatePrinterTimeState(printerId, { loading: true, error: null });
    setStatus({ type: "info", message: "Сверявам часа с компютъра..." });
    try {
      await apiRequest(`/printers/${printerId}/datetime/sync`, {
        method: "POST",
        body: JSON.stringify({}),
      });
      await readPrinterTime(printerId, { silent: true });
      setStatus({ type: "success", message: "Часът е синхронизиран." });
    } catch (error) {
      updatePrinterTimeState(printerId, { loading: false, error: error.message });
      setStatus({ type: "error", message: error.message });
    }
  };

  const checkAllPrinterStatuses = async () => {
    for (const printer of printers) {
      await checkPrinterStatus(printer.id);
    }
  };

  useEffect(() => {
    if (printers.length > 0) {
      checkAllPrinterStatuses();
      const first = printers[0];
      const op = first.config?.operator || {};
      const opData = {
        id: op.id?.toString() || "1",
        password: op.password?.toString() || "0000",
        till: op.till?.toString() || "1",
        name: "UnrealSoft Waiter",
      };
      setFiscalSale((prev) => {
        if (prev.printerId) return prev;
        return {
          printerId: String(first.id),
          operator: opData,
          items: [createFiscalItem({ name: "Ънриъл бургер", price: "1.29", qty: "1", tax: "Б" })],
          payments: [
            createPayment({ type: "P", amount: "1" }),
            createPayment({ type: "N", amount: "0.29" }),
          ],
        };
      });
      setStornoForm((prev) => {
        if (prev.printerId) return prev;
        return { ...prev, printerId: String(first.id), operator: { id: opData.id, password: opData.password, till: opData.till } };
      });
      setReportForm((prev) => {
        if (prev.printerId) return prev;
        return { ...prev, printerId: String(first.id) };
      });
    }
  }, [printers]);

  useEffect(() => {
    refreshPrinters();
    refreshJobs();
    refreshLogs();
    refreshMqtt();
    refreshModels();
    const interval = setInterval(() => {
      refreshJobs();
      refreshLogs();
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (activeTab === "MQTT") {
      refreshMqtt();
      const interval = setInterval(refreshMqtt, 2000);
      return () => clearInterval(interval);
    }
  }, [activeTab]);

  const updateField = (field, value) => {
    setForm((current) => ({ ...current, [field]: value }));
  };

  const resetForm = () => {
    setEditingId(null);
    setForm(defaultForm);
  };

  const submitForm = async (event) => {
    event.preventDefault();
    setLoading(true);
    setStatus({ type: "info", message: "" });
    try {
      const transportType = form.transport || "serial";
      const payload = {
        name: form.name.trim(),
        model: form.model,
        transport: transportType,
        enabled: Boolean(form.enabled),
        dry_run: Boolean(form.dry_run),
        config: {
          protocol: "raw",
        },
      };
      if (transportType === "serial") {
        payload.port = form.port.trim() || null;
        payload.baudrate = Number(form.baudrate) || 115200;
      } else if (transportType === "lan") {
        payload.ip_address = form.ip_address.trim() || null;
        payload.tcp_port = Number(form.tcp_port) || 4999;
      }
      if (form.serial_number?.trim()) payload.serial_number = form.serial_number.trim();
      if (form.firmware?.trim()) payload.firmware = form.firmware.trim();
      const operatorDefaults = {
        id: form.operator_id?.trim() || "",
        password: form.operator_password?.trim() || "",
        till: form.operator_till?.trim() || "",
      };
      const hasOperatorDefaults = Object.values(operatorDefaults).some(Boolean);
      if (hasOperatorDefaults) {
        if (!operatorDefaults.id || !operatorDefaults.password || !operatorDefaults.till) {
          throw new Error("Операторът изисква ID, парола и каса.");
        }
        payload.config.operator = operatorDefaults;
      }
      if (!payload.name) {
        throw new Error("Името на принтера е задължително.");
      }
      if (transportType === "lan" && !payload.ip_address) {
        throw new Error("IP адресът е задължителен за LAN принтер.");
      }
      if (transportType === "serial" && !payload.port) {
        throw new Error("COM портът е задължителен за Serial принтер.");
      }
      if (editingId) {
        await apiRequest(`/printers/${editingId}`, {
          method: "PUT",
          body: JSON.stringify(payload),
        });
        setStatus({ type: "success", message: "Принтерът е обновен." });
      } else {
        await apiRequest("/printers", {
          method: "POST",
          body: JSON.stringify(payload),
        });
        setStatus({ type: "success", message: "Принтерът е добавен." });
      }
      await refreshPrinters();
      resetForm();
    } catch (error) {
      setStatus({ type: "error", message: error.message });
    } finally {
      setLoading(false);
    }
  };

  const refreshPrinterInfo = async (printerId) => {
    setStatus({ type: "info", message: "Обновяване на информация за принтера..." });
    try {
      await apiRequest(`/printers/${printerId}/refresh-info`, { method: "POST" });
      await refreshPrinters();
      setStatus({ type: "success", message: "Информацията за принтера е обновена." });
    } catch (error) {
      setStatus({ type: "error", message: `Грешка: ${error.message}` });
    }
  };

  const handleEdit = (printer) => {
    const operatorDefaults = printer.config?.operator || {};
    setEditingId(printer.id);
    setForm({
      name: printer.name || "",
      model: printer.model || "datecs_fp700mx",
      transport: printer.transport || "serial",
      port: printer.port || "",
      baudrate: String(printer.baudrate ?? "115200"),
      ip_address: printer.ip_address || "",
      tcp_port: String(printer.tcp_port ?? "4999"),
      enabled: Boolean(printer.enabled),
      dry_run: Boolean(printer.dry_run),
      operator_id: operatorDefaults.id?.toString() || "",
      operator_password: operatorDefaults.password?.toString() || "",
      operator_till: operatorDefaults.till?.toString() || "",
      serial_number: printer.serial_number || "",
      firmware: printer.firmware || "",
    });
  };

  const handleDelete = async (printerId) => {
    if (!window.confirm("Сигурни ли сте, че искате да изтриете този принтер?")) {
      return;
    }
    setLoading(true);
    try {
      await apiRequest(`/printers/${printerId}`, { method: "DELETE" });
      setStatus({ type: "success", message: "Принтерът е изтрит." });
      await refreshPrinters();
    } catch (error) {
      setStatus({ type: "error", message: error.message });
    } finally {
      setLoading(false);
    }
  };

  const fiscalValidation = useMemo(() => computeFiscalValidation(), [
    fiscalSale,
    printers,
  ]);

  return (
    <div className="app">
      <header className="hero">
        <div>
          <p className="eyebrow">Local Print Gateway</p>
          <h1>Управление на Datecs принтери</h1>
          <p className="subtitle">
            Изпращай, управлявай и следи всички задачи за печат в реално
            време.
          </p>
          {Object.entries(printerStatuses).some(([_, s]) => s.status === "error" || s.status === "warning") && (
            <div style={{ marginTop: "16px", padding: "12px", background: "#fef1f1", border: "1px solid #b42318", borderRadius: "12px" }}>
              <strong style={{ color: "#b42318" }}>⚠️ Проблем с принтер:</strong>
              {Object.entries(printerStatuses).filter(([_, s]) => s.status === "error" || s.status === "warning").map(([printerId, status]) => {
                const printer = printers.find(p => p.id === parseInt(printerId));
                const color = status.status === "warning" ? "#f59e0b" : "#b42318";
                return (
                  <div key={printerId} style={{ marginTop: "8px", fontSize: "14px", color }}>
                    <strong>{printer?.name || `Принтер #${printerId}`}:</strong> {status.message}
                  </div>
                );
              })}
            </div>
          )}
        </div>
        <div className="hero-card">
          <p>Статус</p>
          <h3>{printers.length} принтера</h3>
          {Object.keys(printerStatuses).length > 0 && (
            <p style={{ fontSize: "12px", marginTop: "8px", color: "var(--muted)" }}>
              {Object.values(printerStatuses).filter(s => s.status === "ok").length} ✅ готови
              {Object.values(printerStatuses).filter(s => s.status === "warning").length > 0 && (
                <>, {Object.values(printerStatuses).filter(s => s.status === "warning").length} ⚠️ предупреждение</>
              )}
              {Object.values(printerStatuses).filter(s => s.status === "error").length > 0 && (
                <>, {Object.values(printerStatuses).filter(s => s.status === "error").length} ❌ грешка</>
              )}
            </p>
          )}
        </div>
      </header>

      <nav className="tabs">
        {["Printers", "Fiscal", "Storno", "Reports", "Pinpad", "Jobs", "Logs", "MQTT"].map((tab) => (
          <button
            key={tab}
            className={tab === activeTab ? "tab active" : "tab"}
            onClick={() => setActiveTab(tab)}
          >
            {tab}
          </button>
        ))}
      </nav>

      {status.message ? <div className={statusClass}>{status.message}</div> : null}

      {activeTab === "Printers" && (
        <section className="printers-section">

          {printers.length > 0 && (
          <div className="card">
            <div className="card-header">
              <div>
                <h2>🖨️ Свързани принтери</h2>
                <p className="muted">{printers.length} {printers.length === 1 ? "принтер" : "принтера"} в системата</p>
              </div>
              <button onClick={refreshPrinters} disabled={loading}>
                Refresh
              </button>
            </div>
            <div className="printer-list">
              {printers.map((printer) => {
                const timeInfo = printerTimes[printer.id] || {};
                const timeLoading = Boolean(timeInfo.loading);
                const printerTimeLabel = timeLoading ? "Чета..." : timeInfo.printer_time || "—";
                const hostTimeLabel = timeInfo.host_time || "—";
                const deltaLabel = formatDeltaSeconds(timeInfo.delta_seconds);
                const statusInfo = printerStatuses[printer.id];
                const statusIcon = statusInfo?.status === "ok" ? "🟢" : statusInfo?.status === "warning" ? "🟡" : statusInfo?.status === "error" ? "🔴" : "⚪";

                return (
                  <div key={printer.id} className="printer-card">
                    <div className="printer-details">
                      <h3>{statusIcon} {printer.name}</h3>
                      <p className="muted">
                        {printer.model} · {printer.transport === "lan"
                          ? `🌐 ${printer.ip_address || "?"}:${printer.tcp_port || 4999}`
                          : `🔌 ${printer.port || "-"}`}
                      </p>
                      <div style={{ display: "flex", gap: "16px", flexWrap: "wrap", marginTop: "4px" }}>
                        {printer.serial_number && (
                          <span className="small" style={{ background: "var(--bg)", padding: "2px 8px", borderRadius: "6px", border: "1px solid var(--border)" }}>
                            <strong>S/N:</strong> {printer.serial_number}
                          </span>
                        )}
                        {printer.firmware && (
                          <span className="small" style={{ background: "var(--bg)", padding: "2px 8px", borderRadius: "6px", border: "1px solid var(--border)" }}>
                            <strong>FW:</strong> {printer.firmware}
                          </span>
                        )}
                        {printer.fiscal_memory_number && (
                          <span className="small" style={{ background: "var(--bg)", padding: "2px 8px", borderRadius: "6px", border: "1px solid var(--border)" }}>
                            <strong>ФП:</strong> {printer.fiscal_memory_number}
                          </span>
                        )}
                      </div>
                      <p className="small" style={{ marginTop: "4px" }}>
                        {printer.transport === "lan"
                          ? `TCP порт: ${printer.tcp_port || 4999}`
                          : `Baudrate: ${printer.baudrate}`}
                      </p>
                    </div>
                    <div className="printer-time">
                      <div>
                        <p className="muted small">Час на принтера</p>
                        <strong>{printerTimeLabel}</strong>
                        <p className="small muted">PC: {hostTimeLabel}</p>
                        <p className="small">Δ {deltaLabel}</p>
                        {timeInfo.error && (
                          <p className="small error-text">⚠️ {timeInfo.error}</p>
                        )}
                      </div>
                      <div className="printer-time-actions">
                        <button onClick={() => readPrinterTime(printer.id)} disabled={timeLoading}>
                          ⏱ Прочети
                        </button>
                        <button
                          className="primary"
                          onClick={() => syncPrinterTime(printer.id)}
                          disabled={timeLoading}
                        >
                          🔄 Свери
                        </button>
                      </div>
                    </div>
                    {renamingPrinter.id === printer.id ? (
                      <div className="printer-actions" style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
                        <input
                          autoFocus
                          value={renamingPrinter.name}
                          onChange={(e) => setRenamingPrinter({ ...renamingPrinter, name: e.target.value })}
                          onKeyDown={(e) => {
                            if (e.key === "Escape") setRenamingPrinter({ id: null, name: "" });
                            if (e.key === "Enter") {
                              e.preventDefault();
                              const btn = e.target.parentElement.querySelector(".primary");
                              if (btn) btn.click();
                            }
                          }}
                          style={{ flex: 1, minWidth: 150 }}
                        />
                        <button
                          className="primary"
                          disabled={loading}
                          onClick={async () => {
                            const newName = renamingPrinter.name.trim();
                            if (newName && newName !== printer.name) {
                              try {
                                await apiRequest(`/printers/${printer.id}`, {
                                  method: "PUT",
                                  body: JSON.stringify({ name: newName }),
                                });
                                setStatus({ type: "success", message: "Името е обновено." });
                                await refreshPrinters();
                              } catch (error) {
                                setStatus({ type: "error", message: error.message });
                              }
                            }
                            setRenamingPrinter({ id: null, name: "" });
                          }}
                        >
                          💾 Запази
                        </button>
                        <button onClick={() => setRenamingPrinter({ id: null, name: "" })}>
                          ✕ Откажи
                        </button>
                      </div>
                    ) : (
                      <div className="printer-actions">
                        <button onClick={() => refreshPrinterInfo(printer.id)} disabled={loading}>
                          🔄 Обнови инфо
                        </button>
                        <button onClick={() => handleEdit(printer)}>
                          ⚙️ Редактирай
                        </button>
                        <button onClick={() => setRenamingPrinter({ id: printer.id, name: printer.name })}>
                          ✏️ Преименувай
                        </button>
                        <button
                          className="danger"
                          onClick={() => handleDelete(printer.id)}
                        >
                          Delete
                        </button>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
          )}

          {editingId && (
          <div className="card" style={{ border: "2px solid var(--primary, #2563eb)" }}>
            <div className="card-header">
              <div>
                <h2>⚙️ Редактиране на принтер #{editingId}</h2>
                <p className="muted">Промени настройките и натисни "Запази".</p>
              </div>
              <button onClick={resetForm}>✕ Откажи</button>
            </div>
            <form onSubmit={submitForm} className="form" style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              <div className="row">
                <label style={{ flex: 2 }}>
                  Име *
                  <input value={form.name} onChange={(e) => updateField("name", e.target.value)} placeholder="Име на принтера" />
                </label>
                <label style={{ flex: 1 }}>
                  Модел
                  <select value={form.model} onChange={(e) => updateField("model", e.target.value)}>
                    {(supportedModels.includes(form.model) ? supportedModels : [form.model, ...supportedModels]).map((m) => (
                      <option key={m} value={m}>{modelLabel(m)}</option>
                    ))}
                  </select>
                </label>
                <label style={{ flex: 1 }}>
                  Транспорт
                  <select value={form.transport} onChange={(e) => updateField("transport", e.target.value)}>
                    <option value="serial">Serial (COM)</option>
                    <option value="lan">LAN (TCP/IP)</option>
                  </select>
                </label>
              </div>

              {form.transport === "serial" && (
                <div className="row">
                  <label style={{ flex: 2 }}>
                    COM порт
                    <input value={form.port} onChange={(e) => updateField("port", e.target.value)} placeholder="COM3" />
                  </label>
                  <label style={{ flex: 1 }}>
                    Baudrate
                    <select value={form.baudrate} onChange={(e) => updateField("baudrate", e.target.value)}>
                      {[9600, 19200, 38400, 57600, 115200].map((b) => (
                        <option key={b} value={String(b)}>{b}</option>
                      ))}
                    </select>
                  </label>
                </div>
              )}

              {form.transport === "lan" && (
                <div className="row">
                  <label style={{ flex: 2 }}>
                    IP адрес *
                    <input value={form.ip_address} onChange={(e) => updateField("ip_address", e.target.value)} placeholder="192.168.1.100" />
                  </label>
                  <label style={{ flex: 1 }}>
                    TCP порт
                    <input type="number" min="1" max="65535" value={form.tcp_port} onChange={(e) => updateField("tcp_port", e.target.value)} placeholder="4999" />
                  </label>
                  <label style={{ flex: 0, alignSelf: "flex-end" }}>
                    <button
                      type="button"
                      disabled={lanDetectState.status === "detecting" || !form.ip_address?.trim()}
                      onClick={detectPrinterOnLan}
                    >
                      {lanDetectState.status === "detecting" ? "🔍..." : "🔍 Открий"}
                    </button>
                  </label>
                </div>
              )}

              <div className="row">
                <label>
                  Оператор ID
                  <input value={form.operator_id} onChange={(e) => updateField("operator_id", e.target.value)} placeholder="1" />
                </label>
                <label>
                  Парола
                  <input value={form.operator_password} onChange={(e) => updateField("operator_password", e.target.value)} placeholder="0000" />
                </label>
                <label>
                  Каса
                  <input value={form.operator_till} onChange={(e) => updateField("operator_till", e.target.value)} placeholder="1" />
                </label>
              </div>

              <div className="row">
                <label>
                  <input type="checkbox" checked={form.enabled} onChange={(e) => updateField("enabled", e.target.checked)} />
                  {" "}Активен
                </label>
                <label>
                  <input type="checkbox" checked={form.dry_run} onChange={(e) => updateField("dry_run", e.target.checked)} />
                  {" "}Dry Run (тест без печат)
                </label>
              </div>

              <div style={{ display: "flex", gap: 8 }}>
                <button className="primary" type="submit" disabled={loading}>
                  {loading ? "Запазване..." : "💾 Запази промените"}
                </button>
                <button type="button" onClick={resetForm}>Откажи</button>
              </div>
            </form>
          </div>
          )}

          <div className="card">
            <div className="card-header">
              <div>
                <h2>🔍 Автоматично откриване</h2>
                <p className="muted">Намери свързани Datecs принтери автоматично</p>
              </div>
              <button onClick={detectSerialPorts} disabled={loading} className="primary">
                {loading ? "Търсене..." : "🔄 Търси принтери"}
              </button>
            </div>
            {availablePorts.length > 0 && (
              <div className="detected-ports">
                <h3>Открити портове: {availablePorts.length}</h3>
                <div className="ports-grid">
                  {availablePorts.map((port) => {
                    const existingPrinter = printers.find(p => p.port === port.device);
                    const detection = detectingPorts[port.device];
                    const isDetecting = detection === "detecting";
                    const detected = detection && typeof detection === "object" && detection.detected;
                    const notFound = detection === "not_found" || detection === "error";
                    return (
                      <div key={port.device} className={`port-card ${existingPrinter ? 'port-used' : ''} ${detected ? 'port-detected' : ''}`}>
                        <div className="port-info">
                          <strong>{port.device}</strong>
                          <p className="muted small">{port.description || "Непознато устройство"}</p>
                          {isDetecting && (
                            <p className="muted small">🔍 Разпознаване...</p>
                          )}
                          {detected && (
                            <>
                              <p className="success small" style={{ fontWeight: 600 }}>
                                {detection.device_type === "pinpad" ? "💳" : "✅"} {detection.name}
                              </p>
                              {detection.device_type === "pinpad" && (
                                <span className="badge info" style={{ fontSize: 10, padding: "2px 6px" }}>Картов терминал</span>
                              )}
                              {detection.firmware && (
                                <p className="muted small">FW: {detection.firmware}</p>
                              )}
                              {detection.serial_number && (
                                <p className="muted small">S/N: {detection.serial_number}</p>
                              )}
                              {detection.terminal_id && (
                                <p className="muted small">TID: {detection.terminal_id}</p>
                              )}
                              <p className="muted small">Baudrate: {detection.baudrate}</p>
                            </>
                          )}
                          {notFound && !existingPrinter && (
                            <p className="muted small">— Не е разпознат Datecs принтер</p>
                          )}
                          {existingPrinter && (
                            <p className="success small">✅ Добавен: {existingPrinter.name}</p>
                          )}
                        </div>
                        {existingPrinter ? (
                          <button
                            className="secondary"
                            disabled
                            style={{ opacity: 0.5, cursor: "not-allowed" }}
                          >
                            ✓ Добавен
                          </button>
                        ) : detected ? (
                          <button
                            className="primary"
                            onClick={async () => {
                              try {
                                const isPinpad = detection.device_type === "pinpad";
                                await apiRequest("/printers", {
                                  method: "POST",
                                  body: JSON.stringify({
                                    name: `${detection.name} ${port.device}`,
                                    model: detection.model || "datecs_fp700mx",
                                    transport: "serial",
                                    port: port.device,
                                    baudrate: detection.baudrate || 115200,
                                    enabled: true,
                                    serial_number: detection.serial_number || undefined,
                                    firmware: detection.firmware || undefined,
                                    fiscal_memory_number: detection.fiscal_memory_number || undefined,
                                    config: isPinpad ? {} : { operator: { id: "1", password: "0000", till: "1" } },
                                  }),
                                });
                                setStatus({ type: "success", message: `✅ ${detection.name} добавен автоматично` });
                                await refreshPrinters();
                              } catch (error) {
                                setStatus({ type: "error", message: error.message });
                              }
                            }}
                          >
                            ➕ Добави
                          </button>
                        ) : (
                          <button
                            className="secondary"
                            disabled={isDetecting}
                            onClick={() => {
                              if (!isDetecting) {
                                detectPrinterOnPort(port.device);
                              }
                            }}
                          >
                            {isDetecting ? "🔍..." : "🔍 Разпознай"}
                          </button>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>

          <div className="card">
            <div className="card-header">
              <div>
                <h2>🌐 Добави LAN принтер</h2>
                <p className="muted">Свържи Datecs принтер по мрежа (TCP/IP)</p>
              </div>
            </div>
            <div className="form" style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              <div className="row">
                <label style={{ flex: 2 }}>
                  IP адрес *
                  <input
                    value={lanForm.ip_address}
                    onChange={(e) => { setLanForm({ ...lanForm, ip_address: e.target.value }); setLanDetectResult(null); }}
                    placeholder="192.168.1.100"
                  />
                </label>
                <label style={{ flex: 1 }}>
                  TCP порт
                  <input
                    type="number"
                    min="1"
                    max="65535"
                    value={lanForm.tcp_port}
                    onChange={(e) => { setLanForm({ ...lanForm, tcp_port: e.target.value }); setLanDetectResult(null); }}
                    placeholder="4999"
                  />
                </label>
                <label style={{ flex: 0, alignSelf: "flex-end" }}>
                  <button
                    className="primary"
                    disabled={lanDetecting || !lanForm.ip_address.trim()}
                    onClick={async () => {
                      const ip = lanForm.ip_address.trim();
                      const port = Number(lanForm.tcp_port) || 4999;
                      if (!ip) { setStatus({ type: "error", message: "Въведи IP адрес." }); return; }
                      if (!/^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/.test(ip)) {
                        setStatus({ type: "error", message: "Невалиден IP адрес (очаква се формат x.x.x.x)." }); return;
                      }
                      if (port < 1 || port > 65535) {
                        setStatus({ type: "error", message: "Невалиден порт (1-65535)." }); return;
                      }
                      const duplicate = printers.find(p => p.transport === "lan" && p.ip_address === ip && (p.tcp_port || 4999) === port);
                      if (duplicate) {
                        setStatus({ type: "warning", message: `Принтер на ${ip}:${port} вече е добавен (${duplicate.name}).` }); return;
                      }
                      setLanDetecting(true);
                      setLanDetectResult(null);
                      setStatus({ type: "info", message: `Търсене на принтер на ${ip}:${port}...` });
                      try {
                        const result = await apiRequest("/tools/detect-printer-lan", {
                          method: "POST",
                          body: JSON.stringify({ ip_address: ip, tcp_port: port }),
                        });
                        if (result.detected) {
                          setLanDetectResult(result);
                          setLanForm(prev => ({
                            ...prev,
                            name: prev.name || `${result.name} LAN`,
                            model: result.model || prev.model || supportedModels[0] || "datecs_fp700mx",
                          }));
                          setStatus({ type: "success", message: `Разпознат: ${result.name} (${result.model || "unknown"})` });
                        } else {
                          setLanDetectResult({ detected: false });
                          setStatus({ type: "warning", message: result.error || "Не е открит принтер на този адрес." });
                        }
                      } catch (error) {
                        setLanDetectResult({ detected: false });
                        setStatus({ type: "error", message: `Грешка: ${error.message}` });
                      } finally {
                        setLanDetecting(false);
                      }
                    }}
                  >
                    {lanDetecting ? "🔍 Търсене..." : "🔍 Открий"}
                  </button>
                </label>
              </div>

              {lanDetectResult && lanDetectResult.detected && (
                <div style={{ background: "var(--success-bg, #e6f9e6)", border: "1px solid #4caf50", borderRadius: 8, padding: 12 }}>
                  <strong style={{ color: "#2e7d32" }}>✅ Разпознат: {lanDetectResult.name}</strong>
                  <div style={{ display: "flex", gap: 16, flexWrap: "wrap", marginTop: 8 }}>
                    {lanDetectResult.model && <span className="small"><strong>Модел:</strong> {modelLabel(lanDetectResult.model)}</span>}
                    {lanDetectResult.serial_number && <span className="small"><strong>S/N:</strong> {lanDetectResult.serial_number}</span>}
                    {lanDetectResult.firmware && <span className="small"><strong>FW:</strong> {lanDetectResult.firmware}</span>}
                    {lanDetectResult.fiscal_memory_number && <span className="small"><strong>ФП:</strong> {lanDetectResult.fiscal_memory_number}</span>}
                    {lanDetectResult.protocol && <span className="small"><strong>Протокол:</strong> {lanDetectResult.protocol}</span>}
                  </div>
                </div>
              )}

              {lanDetectResult && !lanDetectResult.detected && (
                <div style={{ background: "var(--error-bg, #fde8e8)", border: "1px solid #e53935", borderRadius: 8, padding: 12 }}>
                  <strong style={{ color: "#c62828" }}>❌ Не е открит принтер</strong>
                  <p className="small muted" style={{ marginTop: 4 }}>Провери: 1) Принтерът е включен, 2) IP адресът е правилен, 3) TCP портът е правилен (обикновено 4999), 4) Мрежовата връзка е наред.</p>
                </div>
              )}

              <div className="row">
                <label style={{ flex: 2 }}>
                  Име на принтера *
                  <input
                    value={lanForm.name}
                    onChange={(e) => setLanForm({ ...lanForm, name: e.target.value })}
                    placeholder="Datecs FP700MX LAN"
                  />
                </label>
                <label style={{ flex: 1 }}>
                  Модел *
                  <select
                    value={lanForm.model || (lanDetectResult?.model || supportedModels[0] || "datecs_fp700mx")}
                    onChange={(e) => setLanForm({ ...lanForm, model: e.target.value })}
                  >
                    {supportedModels.map((m) => (
                      <option key={m} value={m}>{modelLabel(m)}</option>
                    ))}
                  </select>
                </label>
              </div>

              <div className="row">
                <label>
                  Оператор ID
                  <input
                    value={lanForm.operator_id}
                    onChange={(e) => setLanForm({ ...lanForm, operator_id: e.target.value })}
                    placeholder="1"
                  />
                </label>
                <label>
                  Парола
                  <input
                    value={lanForm.operator_password}
                    onChange={(e) => setLanForm({ ...lanForm, operator_password: e.target.value })}
                    placeholder="0000"
                  />
                </label>
                <label>
                  Каса
                  <input
                    value={lanForm.operator_till}
                    onChange={(e) => setLanForm({ ...lanForm, operator_till: e.target.value })}
                    placeholder="1"
                  />
                </label>
              </div>

              <button
                className="primary"
                disabled={lanAdding || !lanForm.name.trim() || !lanForm.ip_address.trim()}
                onClick={async () => {
                  const ip = lanForm.ip_address.trim();
                  const port = Number(lanForm.tcp_port) || 4999;
                  const name = lanForm.name.trim();
                  if (!name) { setStatus({ type: "error", message: "Въведи име на принтера." }); return; }
                  if (!ip) { setStatus({ type: "error", message: "Въведи IP адрес." }); return; }
                  if (!/^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/.test(ip)) {
                    setStatus({ type: "error", message: "Невалиден IP адрес." }); return;
                  }
                  const duplicate = printers.find(p => p.transport === "lan" && p.ip_address === ip && (p.tcp_port || 4999) === port);
                  if (duplicate) {
                    setStatus({ type: "warning", message: `Принтер на ${ip}:${port} вече е добавен (${duplicate.name}).` }); return;
                  }
                  setLanAdding(true);
                  setStatus({ type: "info", message: "Добавяне на LAN принтер..." });
                  try {
                    const model = lanForm.model || lanDetectResult?.model || supportedModels[0] || "datecs_fp700mx";
                    const payload = {
                      name,
                      model,
                      transport: "lan",
                      ip_address: ip,
                      tcp_port: port,
                      enabled: true,
                      config: {},
                    };
                    if (lanDetectResult?.serial_number) payload.serial_number = lanDetectResult.serial_number;
                    if (lanDetectResult?.firmware) payload.firmware = lanDetectResult.firmware;
                    if (lanDetectResult?.fiscal_memory_number) payload.fiscal_memory_number = lanDetectResult.fiscal_memory_number;
                    const opId = lanForm.operator_id?.trim();
                    const opPass = lanForm.operator_password?.trim();
                    const opTill = lanForm.operator_till?.trim();
                    if (opId && opPass && opTill) {
                      payload.config.operator = { id: opId, password: opPass, till: opTill };
                    }
                    await apiRequest("/printers", {
                      method: "POST",
                      body: JSON.stringify(payload),
                    });
                    setStatus({ type: "success", message: `✅ LAN принтер "${name}" добавен успешно!` });
                    setLanForm({ ip_address: "", tcp_port: "4999", name: "", model: "", operator_id: "1", operator_password: "0000", operator_till: "1" });
                    setLanDetectResult(null);
                    await refreshPrinters();
                  } catch (error) {
                    setStatus({ type: "error", message: error.message });
                  } finally {
                    setLanAdding(false);
                  }
                }}
              >
                {lanAdding ? "Добавяне..." : "➕ Добави LAN принтер"}
              </button>
            </div>
          </div>

        </section>
      )}

      {activeTab === "Fiscal" && (
        <section className="fiscal-stack">
          <div className="card form-card fiscal-section fiscal-main">
            <div className="card-header">
              <div>
                <h2>Фискален бон</h2>
                <p className="muted">Open → Sell items → Payment → Close.</p>
              </div>
              <button
                type="button"
                className="danger"
                onClick={() => {
                  if (!fiscalSale.printerId) {
                    setStatus({ type: "error", message: "Избери принтер първо" });
                    return;
                  }
                  setModal({
                    show: true,
                    title: "⚠️ Отказ на бон",
                    message: "Сигурен ли си, че искаш да откажеш отворения бон? Това действие не може да бъде отменено.",
                    onConfirm: async () => {
                      try {
                        await apiRequest(`/printers/${fiscalSale.printerId}/cancel_receipt`, {
                          method: "POST",
                        });
                        setStatus({ type: "success", message: "✅ Бонът е отказан успешно" });
                        await refreshJobs();
                      } catch (error) {
                        setStatus({ type: "error", message: `Грешка при отказ: ${error.message}` });
                      }
                    },
                  });
                }}
              >
                ⚠️ Отказ на бон
              </button>
            </div>
            <form onSubmit={submitFiscalSale} className="form">
              <label>
                Принтер
                <select
                  value={fiscalSale.printerId}
                  onChange={(event) => {
                    const printerId = event.target.value;
                    const operatorDefaults = buildPrinterOperator(printerId);
                    setFiscalSale((current) => ({
                      ...current,
                      printerId,
                      operator: operatorDefaults || current.operator,
                    }));
                  }}
                  className={fiscalValidation.errors.printerId ? "field-error" : ""}
                >
                  <option value="">Избери принтер</option>
                  {printers.map((printer) => (
                    <option key={printer.id} value={printer.id}>
                      {printerLabel(printer)}
                    </option>
                  ))}
                </select>
                {fiscalValidation.errors.printerId && (
                  <span className="inline-error">{fiscalValidation.errors.printerId}</span>
                )}
              </label>
              <div className="row">
                <label>
                  Оператор ID
                  <input
                    value={fiscalSale.operator.id}
                    onChange={(event) => updateFiscalSaleOperator("id", event.target.value)}
                    placeholder="1"
                    className={fiscalValidation.errors.operator ? "field-error" : ""}
                  />
                </label>
                <label>
                  Парола
                  <input
                    value={fiscalSale.operator.password}
                    onChange={(event) =>
                      updateFiscalSaleOperator("password", event.target.value)
                    }
                    placeholder="0000"
                    className={fiscalValidation.errors.operator ? "field-error" : ""}
                  />
                </label>
                <label>
                  Каса (задължително)
                  <input
                    value={fiscalSale.operator.till}
                    onChange={(event) => updateFiscalSaleOperator("till", event.target.value)}
                    placeholder="1"
                    className={fiscalValidation.errors.operator ? "field-error" : ""}
                  />
                </label>
                <label>
                  Име (сервитьор)
                  <input
                    value={fiscalSale.operator.name}
                    onChange={(event) => updateFiscalSaleOperator("name", event.target.value)}
                    placeholder="Иван Иванов"
                  />
                </label>
              </div>
              {fiscalValidation.errors.operator && (
                <span className="inline-error">{fiscalValidation.errors.operator}</span>
              )}
              <div className="row">
                <label>
                  УНП (опционално)
                  <input
                    value={fiscalSale.nsale || ""}
                    onChange={(event) => setFiscalSale((c) => ({ ...c, nsale: event.target.value }))}
                    placeholder="DT998016-0001-0000001"
                  />
                </label>
              </div>
              <div className="items">
                <div className="card-header">
                  <h3>Артикули</h3>
                  <button type="button" onClick={addFiscalSaleItem}>
                    + Добави
                  </button>
                </div>
                {fiscalSale.items.map((item, index) => (
                  <div
                    key={`sale-item-${index}`}
                    className={`items-row ${
                      fiscalValidation.itemErrors[index] ? "row-error" : ""
                    }`}
                  >
                    <input
                      placeholder="Артикул"
                      value={item.name}
                      onChange={(event) =>
                        updateFiscalSaleItem(index, "name", event.target.value)
                      }
                    />
                    <select
                      value={item.tax}
                      onChange={(event) =>
                        updateFiscalSaleItem(index, "tax", event.target.value)
                      }
                    >
                      {taxOptions.map((tax) => (
                        <option key={tax.value} value={tax.value}>
                          {tax.label}
                        </option>
                      ))}
                    </select>
                    <input
                      type="number"
                      min="0"
                      step="0.01"
                      placeholder="Price"
                      value={item.price}
                      onChange={(event) =>
                        updateFiscalSaleItem(index, "price", event.target.value)
                      }
                    />
                    <input
                      type="number"
                      min="0"
                      step="0.001"
                      placeholder="Qty"
                      value={item.qty}
                      onChange={(event) =>
                        updateFiscalSaleItem(index, "qty", event.target.value)
                      }
                    />
                    <input
                      placeholder="Unit"
                      value={item.unit}
                      onChange={(event) =>
                        updateFiscalSaleItem(index, "unit", event.target.value)
                      }
                    />
                    <input
                      placeholder="Discount"
                      value={item.discount}
                      onChange={(event) =>
                        updateFiscalSaleItem(index, "discount", event.target.value)
                      }
                    />
                    <button type="button" onClick={() => removeFiscalSaleItem(index)}>
                      Remove
                    </button>
                    {fiscalValidation.itemErrors[index] && (
                      <span className="inline-error">Име + цена са задължителни.</span>
                    )}
                  </div>
                ))}
                {fiscalValidation.errors.items && (
                  <span className="inline-error">{fiscalValidation.errors.items}</span>
                )}
              </div>
              <div className="items">
                <div className="card-header">
                  <div>
                    <h3>Плащания</h3>
                    <p className="muted small">
                      Тотал: {fiscalTotal.toFixed(2)} EUR · Платено: {fiscalPaymentTotal.toFixed(2)} EUR
                    </p>
                  </div>
                  <div className="actions-inline">
                    <span className={`pill ${fiscalRemaining > 0 ? "warning" : "success"}`}>
                      Остатък: {fiscalRemaining.toFixed(2)}
                    </span>
                    <button type="button" onClick={applyFiscalTotal}>
                      Попълни тотал
                    </button>
                    <button type="button" onClick={addFiscalSalePayment}>
                      + Добави
                    </button>
                  </div>
                </div>
                {fiscalSale.payments.map((payment, index) => (
                  <div key={`sale-pay-${index}`} className="items-row">
                    <select
                      value={payment.type}
                      onChange={(event) =>
                        updateFiscalSalePayment(index, "type", event.target.value)
                      }
                      className={
                        fiscalValidation.paymentErrors[index] ? "field-error" : ""
                      }
                    >
                      {paymentOptions.map((option) => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                    <input
                      type="number"
                      min="0"
                      step="0.01"
                      placeholder="Amount"
                      value={payment.amount}
                      onChange={(event) =>
                        updateFiscalSalePayment(index, "amount", event.target.value)
                      }
                    />
                    <button type="button" onClick={() => removeFiscalSalePayment(index)}>
                      Remove
                    </button>
                    {fiscalValidation.paymentErrors[index] && (
                      <span className="inline-error">Избери тип и сума.</span>
                    )}
                  </div>
                ))}
                {fiscalValidation.errors.payments && (
                  <span className="inline-error">{fiscalValidation.errors.payments}</span>
                )}
              </div>
              <button className="primary" type="submit" disabled={fiscalLoading}>
                Изпрати фискален бон
              </button>
            </form>
          </div>
        </section>
      )}

      {activeTab === "Storno" && (
        <section className="fiscal-stack">
          <div className="card form-card fiscal-section fiscal-main">
            <div className="card-header">
              <div>
                <h2>Сторно на цяла бележка</h2>
                <p className="muted">Избери успешен фискален бон от списъка или въведи номер на документ ръчно.</p>
              </div>
            </div>
            <form onSubmit={submitStorno} className="form">
              <div className="form-section">
                <h3>📄 Избери бележка за сторниране</h3>
                <label>
                  Последни фискални бонове
                  <select
                    value=""
                    onChange={(e) => {
                      const job = jobs.find((j) => j.id === Number(e.target.value));
                      if (!job) return;
                      const p = job.payload || {};
                      const created = new Date(job.created_at);
                      const dd = String(created.getDate()).padStart(2, "0");
                      const mm = String(created.getMonth() + 1).padStart(2, "0");
                      const yy = String(created.getFullYear()).slice(-2);
                      const items = (p.items || []).map((it) => ({
                        name: it.name || "",
                        tax: it.vat_group || it.tax || "Б",
                        price: String(it.price || ""),
                        qty: String(it.quantity || it.qty || "1"),
                        unit: it.unit || "",
                        discount: it.discount || "",
                      }));
                      const payments = (p.payments || []).map((pm) => ({
                        type: pm.type || "P",
                        amount: String(pm.amount || ""),
                      }));
                      setStornoForm((prev) => ({
                        ...prev,
                        printerId: String(job.printer_id),
                        original: {
                          doc_no: job.result?.receipt_number || "",
                          date: `${dd}${mm}${yy}`,
                          fm: "",
                          unp: p.nsale || "",
                        },
                        items: items.length ? items : [createFiscalItem()],
                        payments: payments.length ? payments : [createPayment()],
                      }));
                      setStatus({ type: "info", message: `Заредена бележка #${job.result?.receipt_number || job.id} за сторно` });
                    }}
                  >
                    <option value="">— Избери от последните бонове —</option>
                    {jobs
                      .filter((j) => j.payload_type === "fiscal_receipt" && j.status === "success" && j.result?.receipt_number)
                      .slice(0, 20)
                      .map((j) => (
                        <option key={j.id} value={j.id}>
                          Бон №{j.result.receipt_number} — {new Date(j.created_at).toLocaleString("bg-BG", { dateStyle: "short", timeStyle: "short" })} — {(j.payload?.items || []).map(i => i.name).join(", ").substring(0, 40)}
                        </option>
                      ))}
                  </select>
                </label>
              </div>
              <div className="form-section">
                <h3>📋 Данни за сторно</h3>
                <div className="row">
                  <label>
                    Тип сторно
                    <select
                      value={stornoForm.stornoType}
                      onChange={(e) => setStornoForm({...stornoForm, stornoType: e.target.value})}
                    >
                      <option value="0">0 - Оператор грешка</option>
                      <option value="1">1 - Връщане/рекламация</option>
                      <option value="2">2 - Данъчна редукция</option>
                    </select>
                  </label>
                  <label>
                    Номер на документ *
                    <input
                      value={stornoForm.original.doc_no}
                      onChange={(e) => setStornoForm({...stornoForm, original: {...stornoForm.original, doc_no: e.target.value}})}
                      placeholder="0001234"
                      required
                    />
                  </label>
                  <label>
                    Дата и час (DDMMYYhhmmss) *
                    <input
                      value={stornoForm.original.date}
                      onChange={(e) => setStornoForm({...stornoForm, original: {...stornoForm.original, date: e.target.value}})}
                      placeholder="100226153000"
                      required
                    />
                  </label>
                </div>
              </div>
              {stornoForm.items.length > 0 && stornoForm.items[0].name && (
                <div className="form-section">
                  <h3>🛒 Артикули ({stornoForm.items.length})</h3>
                  <div style={{ background: "var(--bg)", borderRadius: 8, padding: 12 }}>
                    {stornoForm.items.map((item, i) => (
                      <div key={i} className="small" style={{ display: "flex", justifyContent: "space-between", padding: "4px 0", borderBottom: i < stornoForm.items.length - 1 ? "1px solid var(--border)" : "none" }}>
                        <span>{item.name}</span>
                        <span>{item.qty} x {item.price} лв ({taxLabel(item.tax)})</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              {stornoForm.payments.length > 0 && stornoForm.payments[0].amount && (
                <div className="form-section">
                  <h3>💳 Плащания</h3>
                  <div style={{ background: "var(--bg)", borderRadius: 8, padding: 12 }}>
                    {stornoForm.payments.map((pm, i) => (
                      <div key={i} className="small" style={{ display: "flex", justifyContent: "space-between", padding: "4px 0" }}>
                        <span>{paymentLabel(pm.type)}</span>
                        <span>{pm.amount} лв</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              <div className="summary">
                <p><strong>Тотал за сторно:</strong> {stornoTotal.toFixed(2)} лв</p>
              </div>
              <button className="primary" type="submit" disabled={stornoLoading || !stornoForm.original.doc_no}>
                {stornoLoading ? "Изпращам..." : "🔄 Сторнирай цялата бележка"}
              </button>
            </form>
          </div>
        </section>
      )}

      {activeTab === "Reports" && (
        <section className="grid">
          <div className="card form-card">
            <div className="card-header">
              <h2>Дневни отчети (Z/X)</h2>
              <p className="muted">Печат на фискални отчети.</p>
            </div>
            <form onSubmit={submitReport} className="form">
              <label>
                Принтер
                <select
                  value={reportForm.printerId}
                  onChange={(e) => setReportForm({ ...reportForm, printerId: e.target.value })}
                  required
                >
                  <option value="">Избери принтер</option>
                  {printers.map((printer) => (
                    <option key={printer.id} value={printer.id}>
                      {printerLabel(printer)}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Тип отчет
                <select
                  value={reportForm.reportType}
                  onChange={(e) => setReportForm({ ...reportForm, reportType: e.target.value })}
                >
                  <option value="Z">Z - Дневен отчет с нулиране</option>
                  <option value="X">X - Междинен отчет (без нулиране)</option>
                </select>
              </label>
              <div className="row">
                <label>
                  От дата (опционално)
                  <input
                    type="date"
                    value={reportForm.startDate}
                    onChange={(e) => setReportForm({ ...reportForm, startDate: e.target.value })}
                  />
                </label>
                <label>
                  До дата (опционално)
                  <input
                    type="date"
                    value={reportForm.endDate}
                    onChange={(e) => setReportForm({ ...reportForm, endDate: e.target.value })}
                  />
                </label>
              </div>
              <button className="primary" type="submit" disabled={reportLoading}>
                Печат на отчет
              </button>
            </form>
          </div>

          <div className="card form-card">
            <div className="card-header">
              <h2>Служебно въвеждане/извеждане</h2>
              <p className="muted">Операции с каса.</p>
            </div>
            <form onSubmit={submitCashOperation} className="form">
              <label>
                Принтер
                <select
                  value={reportForm.printerId}
                  onChange={(e) => setReportForm({ ...reportForm, printerId: e.target.value })}
                  required
                >
                  <option value="">Избери принтер</option>
                  {printers.map((printer) => (
                    <option key={printer.id} value={printer.id}>
                      {printerLabel(printer)}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Операция
                <select
                  value={reportForm.cashType}
                  onChange={(e) => setReportForm({ ...reportForm, cashType: e.target.value })}
                >
                  <option value="in">Въвеждане (вноска)</option>
                  <option value="out">Извеждане (изплащане)</option>
                </select>
              </label>
              <label>
                Сума
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  value={reportForm.cashAmount}
                  onChange={(e) => setReportForm({ ...reportForm, cashAmount: e.target.value })}
                  placeholder="0.00"
                  required
                />
              </label>
              <button className="primary" type="submit" disabled={reportLoading}>
                Изпълни операция
              </button>
            </form>
          </div>
        </section>
      )}

      {activeTab === "Pinpad" && (
        <section className="grid">
          <div className="card form-card">
            <div className="card-header">
              <div>
                <h2>💳 Картов терминал (PinPad)</h2>
                <p className="muted">DatecsPay BluePad — плащане с банкова карта.</p>
              </div>
            </div>
            <div className="form">
              <label>
                Устройство
                <select
                  value={pinpadForm.printerId}
                  onChange={(e) => setPinpadForm({ ...pinpadForm, printerId: e.target.value })}
                >
                  <option value="">Избери устройство</option>
                  {printers.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.name} ({p.port || p.ip_address || "-"})
                    </option>
                  ))}
                </select>
              </label>

              <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                <button onClick={() => pinpadAction("ping")} disabled={pinpadLoading}>
                  📡 Ping
                </button>
                <button onClick={() => pinpadAction("info")} disabled={pinpadLoading}>
                  ℹ️ Инфо
                </button>
                <button onClick={() => pinpadAction("status")} disabled={pinpadLoading}>
                  📊 Статус
                </button>
                <button onClick={() => pinpadAction("test-connection")} disabled={pinpadLoading} className="secondary">
                  🔌 Тест връзка
                </button>
                <button onClick={() => pinpadAction("end-of-day")} disabled={pinpadLoading} className="danger">
                  📋 Край на деня
                </button>
              </div>

              {pinpadInfo && (
                <div style={{ background: "var(--bg)", borderRadius: 8, padding: 12, marginTop: 8 }}>
                  <h3 style={{ marginBottom: 8 }}>ℹ️ Информация за устройството</h3>
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "4px 16px" }}>
                    <span className="muted small">Модел:</span><strong>{pinpadInfo.model}</strong>
                    <span className="muted small">Сериен №:</span><strong>{pinpadInfo.serial_number}</strong>
                    <span className="muted small">Софтуер:</span><strong>{pinpadInfo.software_version}</strong>
                    <span className="muted small">Терминал ID:</span><strong>{pinpadInfo.terminal_id}</strong>
                    <span className="muted small">Меню тип:</span><strong>{pinpadInfo.menu_type}</strong>
                  </div>
                </div>
              )}

              {pinpadStatus && (
                <div style={{ background: "var(--bg)", borderRadius: 8, padding: 12, marginTop: 8 }}>
                  <h3 style={{ marginBottom: 8 }}>📊 Статус</h3>
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "4px 16px" }}>
                    <span className="muted small">Четец:</span>
                    <strong>{pinpadStatus.reader_state}</strong>
                    <span className="muted small">Реверсал:</span>
                    <strong style={{ color: pinpadStatus.has_reversal ? "#e53935" : "#4caf50" }}>
                      {pinpadStatus.has_reversal ? "⚠️ Да" : "✅ Няма"}
                    </strong>
                    <span className="muted small">Край на деня:</span>
                    <strong style={{ color: pinpadStatus.end_day_required ? "#f59e0b" : "#4caf50" }}>
                      {pinpadStatus.end_day_required ? "⚠️ Необходим" : "✅ Не"}
                    </strong>
                    <span className="muted small">Записи в лога:</span>
                    <strong>{pinpadStatus.report_count}</strong>
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="card form-card">
            <div className="card-header">
              <div>
                <h2>💰 Плащане с карта</h2>
                <p className="muted">Сумата е в лева (напр. 1.50 = 1.50 лв).</p>
              </div>
            </div>
            <div className="form">
              <label>
                Сума (лв) *
                <input
                  type="number"
                  min="0.01"
                  step="0.01"
                  value={pinpadForm.amount}
                  onChange={(e) => setPinpadForm({ ...pinpadForm, amount: e.target.value })}
                  placeholder="0.00"
                />
              </label>
              <label>
                Бакшиш (лв)
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  value={pinpadForm.tip}
                  onChange={(e) => setPinpadForm({ ...pinpadForm, tip: e.target.value })}
                  placeholder="0.00"
                />
              </label>
              <button
                className="primary"
                disabled={pinpadLoading || !pinpadForm.amount}
                onClick={() => pinpadAction("purchase", {
                  amount: Number(pinpadForm.amount),
                  tip: Number(pinpadForm.tip) || 0,
                })}
              >
                {pinpadLoading ? "Обработка..." : "💳 Плати с карта"}
              </button>

              <div style={{ marginTop: 16, borderTop: "1px solid var(--border)", paddingTop: 16 }}>
                <h3>🔄 Анулиране (Void)</h3>
                <p className="muted small" style={{ marginBottom: 8 }}>За анулиране е необходим RRN и Auth ID от оригиналната транзакция.</p>
                <div className="row">
                  <label>
                    RRN
                    <input
                      value={pinpadForm.rrn}
                      onChange={(e) => setPinpadForm({ ...pinpadForm, rrn: e.target.value })}
                      placeholder="Номер от бележка"
                    />
                  </label>
                  <label>
                    Auth ID
                    <input
                      value={pinpadForm.auth_id}
                      onChange={(e) => setPinpadForm({ ...pinpadForm, auth_id: e.target.value })}
                      placeholder="Код за оторизация"
                    />
                  </label>
                </div>
                <button
                  className="danger"
                  disabled={pinpadLoading || !pinpadForm.amount || !pinpadForm.rrn || !pinpadForm.auth_id}
                  onClick={() => pinpadAction("void", {
                    amount: Number(pinpadForm.amount),
                    rrn: pinpadForm.rrn,
                    auth_id: pinpadForm.auth_id,
                  })}
                >
                  {pinpadLoading ? "Обработка..." : "🔄 Анулирай"}
                </button>
              </div>

              {pinpadResult && (
                <div style={{
                  background: pinpadResult.approved ? "var(--success-bg, #e6f9e6)" : pinpadResult.alive !== undefined ? "var(--bg)" : "var(--error-bg, #fde8e8)",
                  borderRadius: 8, padding: 12, marginTop: 12,
                  border: `1px solid ${pinpadResult.approved ? "#4caf50" : pinpadResult.alive !== undefined ? "var(--border)" : "#e53935"}`,
                }}>
                  <h3 style={{ marginBottom: 8 }}>
                    {pinpadResult.approved ? "✅ Одобрена" : pinpadResult.alive ? "📡 Alive" : pinpadResult.alive === false ? "❌ Няма връзка" : "❌ Отказана"}
                  </h3>
                  {pinpadResult.result_message && !pinpadResult.approved && (
                    <p style={{ color: "#e53935", fontWeight: 600, marginBottom: 8 }}>{pinpadResult.result_message}</p>
                  )}
                  {pinpadResult.approved !== undefined && (
                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "4px 16px" }}>
                      {pinpadResult.amount_display && pinpadResult.amount_display !== "0.00" && <><span className="muted small">Сума:</span><strong>{pinpadResult.amount_display} лв</strong></>}
                      {pinpadResult.card_scheme && <><span className="muted small">Карта:</span><strong>{pinpadResult.card_scheme}</strong></>}
                      {pinpadResult.masked_pan && <><span className="muted small">PAN:</span><strong>{pinpadResult.masked_pan}</strong></>}
                      {pinpadResult.rrn && <><span className="muted small">RRN:</span><strong>{pinpadResult.rrn}</strong></>}
                      {pinpadResult.auth_id && <><span className="muted small">Auth ID:</span><strong>{pinpadResult.auth_id}</strong></>}
                      {pinpadResult.terminal_id && <><span className="muted small">Terminal:</span><strong>{pinpadResult.terminal_id}</strong></>}
                      {pinpadResult.merchant_name && <><span className="muted small">Търговец:</span><strong>{pinpadResult.merchant_name}</strong></>}
                      {pinpadResult.interface_name && <><span className="muted small">Интерфейс:</span><strong>{pinpadResult.interface_name}</strong></>}
                      {pinpadResult.trans_date && <><span className="muted small">Дата:</span><strong>{pinpadResult.trans_date} {pinpadResult.trans_time}</strong></>}
                      {pinpadResult.stan > 0 && <><span className="muted small">STAN:</span><strong>{pinpadResult.stan}</strong></>}
                      {pinpadResult.currency && <><span className="muted small">Валута:</span><strong>{pinpadResult.currency}</strong></>}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </section>
      )}

      {activeTab === "Jobs" && (
        <section className="card">
          <div className="card-header">
            <div>
              <h2>Job Queue (Опашка)</h2>
              <p className="muted">Всички задачи за печат - активни, чакащи и неуспешни.</p>
            </div>
            <button onClick={refreshJobs} disabled={loading}>
              Refresh
            </button>
          </div>
          <div className="table-wrapper">
            {jobs.length === 0 && <p className="muted">Няма jobs.</p>}
            {jobs.length > 0 && (
              <table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Принтер</th>
                    <th>Тип</th>
                    <th>Статус</th>
                    <th>Опити</th>
                    <th>Информация</th>
                    <th>Създаден</th>
                    <th>Действия</th>
                  </tr>
                </thead>
                <tbody>
                  {jobs.map((job) => {
                    const printer = printers.find((p) => p.id === job.printer_id);
                    const printerName = printer ? printer.name : `#${job.printer_id}`;
                    const statusClass = {
                      queued: "warning",
                      printing: "info",
                      success: "success",
                      failed: "error",
                    }[job.status] || "";
                    const statusText = {
                      queued: "Чака",
                      printing: "Печата",
                      success: "Успех",
                      failed: "Грешка",
                    }[job.status] || job.status;
                    
                    return (
                      <tr key={job.id}>
                        <td><strong>#{job.id}</strong></td>
                        <td>{printerName}</td>
                        <td>
                          <span className="badge">
                            {job.payload_type === "fiscal_receipt" && "Фискален бон"}
                            {job.payload_type === "storno" && "Сторно"}
                            {job.payload_type === "report" && "Отчет"}
                            {job.payload_type === "cash" && "Каса"}
                            {job.payload_type === "text" && "Текст"}
                            {job.payload_type === "receipt" && "Бон"}
                          </span>
                        </td>
                        <td>
                          <span className={`badge ${statusClass}`}>{statusText}</span>
                        </td>
                        <td>{job.retries > 0 ? `${job.retries}x` : "-"}</td>
                        <td>
                          {job.status === "success" && job.result && (
                            <div className="success-info">
                              {job.result.receipt_number && (
                                <div><strong>Бон №:</strong> {job.result.receipt_number}</div>
                              )}
                              {job.result.total_amount !== undefined && (
                                <div><strong>Сума:</strong> {job.result.total_amount.toFixed(2)} EUR</div>
                              )}
                              {job.result.payment_methods && job.result.payment_methods.length > 0 && (
                                <div>
                                  <strong>Плащане:</strong>{" "}
                                  {job.result.payment_methods.map((pm, idx) => (
                                    <span key={idx}>
                                      {pm.type} ({pm.amount.toFixed(2)} EUR)
                                      {idx < job.result.payment_methods.length - 1 ? ", " : ""}
                                    </span>
                                  ))}
                                </div>
                              )}
                              {job.result.report_type && (
                                <div><strong>Отчет:</strong> {job.result.report_type}</div>
                              )}
                              {job.result.cash_type && (
                                <div>
                                  <strong>{job.result.cash_type === "in" ? "Въвеждане" : "Извеждане"}:</strong> {job.result.amount} EUR
                                </div>
                              )}
                            </div>
                          )}
                          {job.error && (
                            <span className="error-text" title={job.error}>
                              {job.error.length > 80 ? job.error.substring(0, 80) + "..." : job.error}
                            </span>
                          )}
                          {job.status === "queued" && !job.error && (
                            <span className="muted small">Чака ред...</span>
                          )}
                        </td>
                        <td className="small muted">
                          {new Date(job.created_at).toLocaleString("bg-BG", {
                            dateStyle: "short",
                            timeStyle: "short",
                          })}
                        </td>
                        <td className="actions-inline">
                          <button
                            className="small"
                            onClick={() => setPreviewJob(job)}
                            title="Преглед на бележката"
                          >
                            🧾
                          </button>
                          {job.status === "failed" && (
                            <button
                              className="small"
                              onClick={() => retryJob(job.id)}
                              title="Повторно изпълнение"
                            >
                              🔄 Retry
                            </button>
                          )}
                          {job.status === "queued" && (
                            <button
                              className="small error"
                              onClick={() => cancelJob(job.id)}
                              title="Откажи job"
                            >
                              ✕ Cancel
                            </button>
                          )}
                          {job.status === "printing" && (
                            <span className="muted small">В момента се обработва...</span>
                          )}
                          {job.status === "success" && (
                            <span className="muted small">✓</span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            )}
          </div>
        </section>
      )}

      {activeTab === "Logs" && (
        <section className="card">
          <div className="card-header">
            <div>
              <h2>Системни логове</h2>
              <p className="muted">Последните 200 събития.</p>
            </div>
            <button onClick={refreshLogs} disabled={loading}>
              Refresh
            </button>
          </div>
          <div className="logs">
            {logs.length === 0 && <p className="muted">Няма логове.</p>}
            {logs.map((log) => (
              <div key={log.id} className="log-item">
                <span className={`badge ${log.level}`}>{log.level}</span>
                <div>
                  <strong>{log.message}</strong>
                  <p className="muted small">
                    {new Date(log.created_at).toLocaleString("bg-BG")}
                  </p>
                  {log.context && (
                    <pre className="log-context">
                      {JSON.stringify(log.context, null, 2)}
                    </pre>
                  )}
                </div>
              </div>
            ))}
          </div>
        </section>
      )}
      {activeTab === "MQTT" && (
        <section className="card">
          <div className="card-header">
            <div>
              <h2>📡 MQTT Bridge</h2>
              <p className="muted">Връзка с EMQX брокер — входящи съобщения в реално време.</p>
            </div>
            <button onClick={refreshMqtt} disabled={loading}>
              Refresh
            </button>
          </div>

          <div style={{ display: "flex", gap: 16, flexWrap: "wrap", marginBottom: 16 }}>
            <div style={{ flex: "1 1 200px", padding: 12, borderRadius: 8, background: mqttStatus.connected ? "var(--success-bg, #e6f9e6)" : "var(--error-bg, #fde8e8)", border: `1px solid ${mqttStatus.connected ? "#4caf50" : "#e53935"}` }}>
              <strong style={{ fontSize: 18 }}>{mqttStatus.connected ? "🟢 Свързан" : mqttStatus.enabled ? "🔴 Прекъснат" : "⚪ Изключен"}</strong>
              <p className="small muted" style={{ marginTop: 4 }}>
                {mqttStatus.broker || "Не е конфигуриран"}
              </p>
            </div>
            <div style={{ flex: "1 1 200px", padding: 12, borderRadius: 8, background: "var(--card-bg, #f5f5f5)", border: "1px solid var(--border, #ddd)" }}>
              <p className="small muted">Client ID</p>
              <strong>{mqttStatus.client_id || "—"}</strong>
              <p className="small muted" style={{ marginTop: 4 }}>Transport: {mqttStatus.transport || "—"}</p>
            </div>
            <div style={{ flex: "1 1 200px", padding: 12, borderRadius: 8, background: "var(--card-bg, #f5f5f5)", border: "1px solid var(--border, #ddd)" }}>
              <p className="small muted">Topic</p>
              <strong>{mqttStatus.topic || "—"}</strong>
              <p className="small muted" style={{ marginTop: 4 }}>Получени: {mqttStatus.message_count || 0}</p>
            </div>
          </div>

          <h3>📤 Изпрати съобщение</h3>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 16, alignItems: "flex-end" }}>
            <label style={{ flex: "1 1 250px" }}>
              Topic
              <input
                value={mqttPublishTopic}
                onChange={(e) => setMqttPublishTopic(e.target.value)}
                placeholder="restaurant/1/bills/closed"
              />
            </label>
            <label style={{ flex: "2 1 300px" }}>
              Payload (JSON)
              <input
                value={mqttPublishPayload}
                onChange={(e) => setMqttPublishPayload(e.target.value)}
                placeholder='{"bill_id": 1, "waiter_id": 1}'
              />
            </label>
            <button
              className="primary"
              disabled={!mqttStatus.connected || mqttPublishing}
              onClick={async () => {
                setMqttPublishing(true);
                try {
                  let parsed;
                  try { parsed = JSON.parse(mqttPublishPayload); } catch { parsed = mqttPublishPayload; }
                  await apiRequest("/mqtt/publish", {
                    method: "POST",
                    body: JSON.stringify({ topic: mqttPublishTopic, payload: parsed, qos: 1 }),
                  });
                  setStatus({ type: "success", message: `Изпратено на ${mqttPublishTopic}` });
                } catch (err) {
                  setStatus({ type: "error", message: `Грешка: ${err.message}` });
                } finally {
                  setMqttPublishing(false);
                }
              }}
              style={{ whiteSpace: "nowrap" }}
            >
              {mqttPublishing ? "Изпращане..." : "📤 Publish"}
            </button>
          </div>

          <h3>📥 Входящи съобщения</h3>
          <div className="logs" style={{ maxHeight: 500, overflowY: "auto" }}>
            {mqttMessages.length === 0 && (
              <p className="muted">Няма получени съобщения. Чакаме...</p>
            )}
            {mqttMessages.map((msg) => (
              <div key={msg.id} className="log-item" style={{ borderLeft: "3px solid #4caf50" }}>
                <span className="badge info" style={{ minWidth: 50 }}>#{msg.id}</span>
                <div style={{ flex: 1 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <strong>{msg.topic}</strong>
                    <span className="small muted">{msg.time} · QoS {msg.qos}</span>
                  </div>
                  <pre className="log-context" style={{ marginTop: 4, maxHeight: 200, overflow: "auto" }}>
                    {typeof msg.payload === "object" ? JSON.stringify(msg.payload, null, 2) : String(msg.payload)}
                  </pre>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {previewJob && (
        <ReceiptPreview
          job={previewJob}
          printerName={
            (printers.find((p) => p.id === previewJob.printer_id) || {}).name ||
            `#${previewJob.printer_id}`
          }
          onClose={() => setPreviewJob(null)}
        />
      )}

      {modal.show && (
        <div className="modal-overlay" onClick={() => setModal({ show: false, title: "", message: "", onConfirm: null })}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>{modal.title}</h2>
            <p>{modal.message}</p>
            <div className="modal-actions">
              <button
                className="secondary"
                onClick={() => setModal({ show: false, title: "", message: "", onConfirm: null })}
              >
                Отказ
              </button>
              <button
                className="danger"
                onClick={() => {
                  const fn = modal.onConfirm;
                  setModal({ show: false, title: "", message: "", onConfirm: null });
                  if (fn) fn();
                }}
              >
                Потвърди
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;

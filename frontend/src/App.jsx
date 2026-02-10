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

const createFiscalItem = () => ({
  name: "",
  tax: "Б",
  price: "",
  qty: "1",
  unit: "",
  discount: "",
});

const createPayment = () => ({ type: "P", amount: "" });

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

const modelOptions = ["datecs_fp700mx"];
const modelLabels = {
  datecs_fp700mx: "Datecs FP700MX",
};
const modelLabel = (model) => modelLabels[model] || model;

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
  const [lanDetectState, setLanDetectState] = useState({ status: "idle", result: null });
  const [mqttStatus, setMqttStatus] = useState({ enabled: false, connected: false });
  const [mqttMessages, setMqttMessages] = useState([]);
  const [mqttPublishTopic, setMqttPublishTopic] = useState("restaurant/1/bills/closed");
  const [mqttPublishPayload, setMqttPublishPayload] = useState('{"bill_id": 1, "waiter_id": 1}');
  const [mqttPublishing, setMqttPublishing] = useState(false);

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

  const refreshAll = async () => {
    await Promise.all([refreshPrinters(), refreshLogs()]);
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
    }
  }, [printers]);

  useEffect(() => {
    refreshPrinters();
    refreshJobs();
    refreshLogs();
    refreshMqtt();
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
        {["Printers", "Fiscal", "Storno", "Reports", "Jobs", "Logs", "MQTT"].map((tab) => (
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
                                ✅ {detection.name}
                              </p>
                              {detection.firmware && (
                                <p className="muted small">FW: {detection.firmware}</p>
                              )}
                              {detection.serial_number && (
                                <p className="muted small">S/N: {detection.serial_number}</p>
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
                            onClick={() => {
                              setForm({
                                ...defaultForm,
                                name: `${detection.name} ${port.device}`,
                                port: port.device,
                                baudrate: String(detection.baudrate || "115200"),
                                model: detection.model || "datecs_fp700mx",
                                serial_number: detection.serial_number || "",
                                firmware: detection.firmware || "",
                              });
                              setStatus({ type: "info", message: `Разпознат ${detection.name} на ${port.device} — форма попълнена` });
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

          <div className="card form-card">
            <div className="card-header">
              <h2>{editingId ? "✏️ Редакция" : "➕ Нов принтер"}</h2>
            </div>
            <form onSubmit={submitForm} className="form">
              <label>
                Име на принтера
                <input
                  value={form.name}
                  onChange={(event) => updateField("name", event.target.value)}
                  placeholder="Datecs COM4 - Каса 1"
                  required
                />
              </label>
              <div className="row">
                <label>
                  Връзка
                  <select
                    value={form.transport}
                    onChange={(event) => updateField("transport", event.target.value)}
                  >
                    <option value="serial">🔌 Сериен (COM)</option>
                    <option value="lan">🌐 LAN (TCP/IP)</option>
                  </select>
                </label>
              </div>
              {form.transport === "serial" ? (
                <div className="row">
                  <label>
                    COM порт *
                    <select
                      value={form.port}
                      onChange={(event) => updateField("port", event.target.value)}
                      required
                    >
                      <option value="">Избери порт...</option>
                      {availablePorts.map((port) => (
                        <option key={port.device} value={port.device}>
                          {port.device} - {port.description || "Неизвестен"}
                        </option>
                      ))}
                      <option disabled>──────────</option>
                      <option value="COM3">COM3 (ръчно)</option>
                      <option value="COM4">COM4 (ръчно)</option>
                      <option value="COM5">COM5 (ръчно)</option>
                    </select>
                  </label>
                  <label>
                    Baudrate
                    <select
                      value={form.baudrate}
                      onChange={(event) => updateField("baudrate", event.target.value)}
                    >
                      <option value="115200">115200 (препоръчано)</option>
                      <option value="57600">57600</option>
                      <option value="38400">38400</option>
                      <option value="19200">19200</option>
                      <option value="9600">9600</option>
                    </select>
                  </label>
                </div>
              ) : (
                <>
                  <div className="row">
                    <label>
                      IP адрес *
                      <input
                        value={form.ip_address}
                        onChange={(event) => updateField("ip_address", event.target.value)}
                        placeholder="192.168.1.100"
                        required
                      />
                    </label>
                    <label>
                      TCP порт
                      <input
                        value={form.tcp_port}
                        onChange={(event) => updateField("tcp_port", event.target.value)}
                        placeholder="4999"
                      />
                    </label>
                    <label style={{ display: "flex", alignItems: "flex-end" }}>
                      <button
                        type="button"
                        className="secondary"
                        onClick={detectPrinterOnLan}
                        disabled={lanDetectState.status === "detecting"}
                        style={{ whiteSpace: "nowrap" }}
                      >
                        {lanDetectState.status === "detecting" ? "🔍..." : "🔍 Разпознай"}
                      </button>
                    </label>
                  </div>
                  {lanDetectState.status === "found" && lanDetectState.result && (
                    <p className="small" style={{ color: "var(--success)", marginTop: 4 }}>
                      ✓ {lanDetectState.result.name} — {lanDetectState.result.firmware || ""} (S/N: {lanDetectState.result.serial_number || "?"})
                    </p>
                  )}
                  {lanDetectState.status === "not_found" && (
                    <p className="small" style={{ color: "var(--warning)", marginTop: 4 }}>
                      Не е открит принтер на този адрес.
                    </p>
                  )}
                </>
              )}
              <div className="row">
                <label>
                  Модел
                  <select
                    value={form.model}
                    onChange={(event) => updateField("model", event.target.value)}
                  >
                    <optgroup label="FP-700 Series (Protocol 2.08)">
                      <option value="datecs_fp700mx">Datecs FP-700MX</option>
                      <option value="datecs_fp700x">Datecs FP-700X</option>
                      <option value="datecs_fp700xe">Datecs FP-700XE</option>
                      <option value="datecs_fmp350x">Datecs FMP-350X</option>
                      <option value="datecs_fmp55x">Datecs FMP-55X</option>
                      <option value="datecs_wp500x">Datecs WP-500X</option>
                      <option value="datecs_wp50x">Datecs WP-50X</option>
                      <option value="datecs_wp25x">Datecs WP-25X</option>
                      <option value="datecs_dp25x">Datecs DP-25X</option>
                      <option value="datecs_dp150x">Datecs DP-150X</option>
                      <option value="datecs_dp05c">Datecs DP-05C</option>
                    </optgroup>
                    <optgroup label="FP-2000 Series (Protocol 2.00BG)">
                      <option value="datecs_fp2000">Datecs FP-2000</option>
                      <option value="datecs_fp800">Datecs FP-800</option>
                      <option value="datecs_fp650">Datecs FP-650</option>
                      <option value="datecs_sk1_21f">Datecs SK1-21F</option>
                      <option value="datecs_sk1_31f">Datecs SK1-31F</option>
                      <option value="datecs_fmp10">Datecs FMP-10</option>
                      <option value="datecs_fp700">Datecs FP-700 (v2.00BG)</option>
                    </optgroup>
                  </select>
                </label>
              </div>
              <div className="form-section">
                <h3>👤 Оператор по подразбиране</h3>
                <div className="row">
                  <label>
                    ID
                    <input
                      value={form.operator_id}
                      onChange={(event) => updateField("operator_id", event.target.value)}
                      placeholder="2"
                    />
                  </label>
                  <label>
                    Парола
                    <input
                      value={form.operator_password}
                      onChange={(event) => updateField("operator_password", event.target.value)}
                      placeholder="0000"
                    />
                  </label>
                  <label>
                    Каса
                    <input
                      value={form.operator_till}
                      onChange={(event) => updateField("operator_till", event.target.value)}
                      placeholder="2"
                    />
                  </label>
                </div>
              </div>
              <div className="toggle-row">
                <label className="toggle">
                  <input
                    type="checkbox"
                    checked={form.enabled}
                    onChange={(event) => updateField("enabled", event.target.checked)}
                  />
                  ✅ Активен
                </label>
              </div>
              <div className="actions">
                <button className="primary" type="submit" disabled={loading}>
                  {editingId ? "💾 Запази" : "➕ Добави"}
                </button>
                {editingId && (
                  <button type="button" onClick={resetForm} disabled={loading}>
                    ❌ Откажи
                  </button>
                )}
              </div>
            </form>
          </div>

          <div className="card">
            <div className="card-header">
              <div>
                <h2>Налични принтери</h2>
                <p className="muted">Последно обновяване в реално време.</p>
              </div>
              <button onClick={refreshPrinters} disabled={loading}>
                Refresh
              </button>
            </div>
            <div className="printer-list">
              {printers.length === 0 && (
                <p className="muted">Няма конфигурирани принтери.</p>
              )}
              {printers.map((printer) => {
                const timeInfo = printerTimes[printer.id] || {};
                const timeLoading = Boolean(timeInfo.loading);
                const printerTimeLabel = timeLoading ? "Чета..." : timeInfo.printer_time || "—";
                const hostTimeLabel = timeInfo.host_time || "—";
                const deltaLabel = formatDeltaSeconds(timeInfo.delta_seconds);

                return (
                  <div key={printer.id} className="printer-card">
                    <div className="printer-details">
                      <h3>{printer.name}</h3>
                      <p className="muted">
                        {printer.model} · {printer.transport === "lan"
                          ? `🌐 ${printer.ip_address || "?"}:${printer.tcp_port || 4999}`
                          : `🔌 ${printer.port || "-"}`}
                      </p>
                      <p className="small">
                        {printer.transport === "lan"
                          ? `TCP порт: ${printer.tcp_port || 4999}`
                          : `Baudrate: ${printer.baudrate}`} · Dry-run: {printer.dry_run ? "on" : "off"}
                      </p>
                      {(printer.serial_number || printer.firmware || printer.fiscal_memory_number) && (
                        <p className="muted small">
                          {printer.serial_number && `S/N: ${printer.serial_number}`}
                          {printer.serial_number && printer.firmware && " · "}
                          {printer.firmware && `FW: ${printer.firmware}`}
                          {(printer.serial_number || printer.firmware) && printer.fiscal_memory_number && " · "}
                          {printer.fiscal_memory_number && `ФП: ${printer.fiscal_memory_number}`}
                        </p>
                      )}
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
                    <div className="printer-actions">
                      <button onClick={() => handleEdit(printer)}>Edit</button>
                      <button
                        className="danger"
                        onClick={() => handleDelete(printer.id)}
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                );
              })}
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
                        const response = await fetch(`${API_BASE}/printers/${fiscalSale.printerId}/cancel_receipt`, {
                          method: "POST",
                        });
                        if (!response.ok) throw new Error("Failed to cancel receipt");
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
                      {printer.name} ({printer.port || "-"})
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
                <h2>Сторно бележка</h2>
                <p className="muted">Корекция/анулиране на фискален бон.</p>
              </div>
            </div>
            <form onSubmit={submitStorno} className="form">
              <label>
                Принтер
                <select
                  value={stornoForm.printerId}
                  onChange={(e) => {
                    const printerId = e.target.value;
                    const operatorDefaults = buildPrinterOperator(printerId);
                    setStornoForm((current) => ({
                      ...current,
                      printerId,
                      operator: operatorDefaults || current.operator,
                    }));
                  }}
                >
                  <option value="">Избери принтер</option>
                  {printers.map((printer) => (
                    <option key={printer.id} value={printer.id}>
                      {printer.name} ({printer.port || "-"})
                    </option>
                  ))}
                </select>
              </label>
              <div className="row">
                <label>
                  Оператор ID
                  <input
                    value={stornoForm.operator.id}
                    onChange={(e) => setStornoForm({...stornoForm, operator: {...stornoForm.operator, id: e.target.value}})}
                    placeholder="1"
                  />
                </label>
                <label>
                  Парола
                  <input
                    value={stornoForm.operator.password}
                    onChange={(e) => setStornoForm({...stornoForm, operator: {...stornoForm.operator, password: e.target.value}})}
                    placeholder="0000"
                  />
                </label>
                <label>
                  Каса
                  <input
                    value={stornoForm.operator.till}
                    onChange={(e) => setStornoForm({...stornoForm, operator: {...stornoForm.operator, till: e.target.value}})}
                    placeholder="1"
                  />
                </label>
              </div>
              <div className="form-section">
                <div className="card-header">
                  <h3>Оригинален документ</h3>
                </div>
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
                <div className="row">
                  <label>
                    Номер на документ
                    <input
                      value={stornoForm.original.doc_no}
                      onChange={(e) => setStornoForm({...stornoForm, original: {...stornoForm.original, doc_no: e.target.value}})}
                      placeholder="0001234"
                    />
                  </label>
                  <label>
                    Дата (DDMMYY)
                    <input
                      value={stornoForm.original.date}
                      onChange={(e) => setStornoForm({...stornoForm, original: {...stornoForm.original, date: e.target.value}})}
                      placeholder="030226"
                    />
                  </label>
                </div>
                <div className="row">
                  <label>
                    FM номер (опция)
                    <input
                      value={stornoForm.original.fm}
                      onChange={(e) => setStornoForm({...stornoForm, original: {...stornoForm.original, fm: e.target.value}})}
                      placeholder=""
                    />
                  </label>
                  <label>
                    УНП (опция)
                    <input
                      value={stornoForm.original.unp}
                      onChange={(e) => setStornoForm({...stornoForm, original: {...stornoForm.original, unp: e.target.value}})}
                      placeholder=""
                    />
                  </label>
                </div>
              </div>
              <div className="items">
                <div className="card-header">
                  <h3>Артикули</h3>
                  <button type="button" onClick={() => setStornoForm({...stornoForm, items: [...stornoForm.items, createFiscalItem()]})}>
                    + Добави
                  </button>
                </div>
                {stornoForm.items.map((item, index) => (
                  <div key={`storno-item-${index}`} className="items-row">
                    <input
                      placeholder="Артикул"
                      value={item.name}
                      onChange={(e) => {
                        const updated = [...stornoForm.items];
                        updated[index] = {...item, name: e.target.value};
                        setStornoForm({...stornoForm, items: updated});
                      }}
                    />
                    <select
                      value={item.tax}
                      onChange={(e) => {
                        const updated = [...stornoForm.items];
                        updated[index] = {...item, tax: e.target.value};
                        setStornoForm({...stornoForm, items: updated});
                      }}
                    >
                      {taxOptions.map((opt) => (
                        <option key={opt.value} value={opt.value}>{opt.label}</option>
                      ))}
                    </select>
                    <input
                      placeholder="Цена"
                      type="number"
                      step="0.01"
                      value={item.price}
                      onChange={(e) => {
                        const updated = [...stornoForm.items];
                        updated[index] = {...item, price: e.target.value};
                        setStornoForm({...stornoForm, items: updated});
                      }}
                    />
                    <input
                      placeholder="Кол."
                      type="number"
                      step="0.001"
                      value={item.qty}
                      onChange={(e) => {
                        const updated = [...stornoForm.items];
                        updated[index] = {...item, qty: e.target.value};
                        setStornoForm({...stornoForm, items: updated});
                      }}
                    />
                    <button
                      type="button"
                      onClick={() => {
                        const updated = stornoForm.items.filter((_, i) => i !== index);
                        setStornoForm({...stornoForm, items: updated.length ? updated : [createFiscalItem()]});
                      }}
                    >
                      ✕
                    </button>
                  </div>
                ))}
              </div>
              <div className="items">
                <div className="card-header">
                  <h3>Плащания</h3>
                  <button type="button" onClick={() => setStornoForm({...stornoForm, payments: [...stornoForm.payments, createPayment()]})}>
                    + Добави
                  </button>
                </div>
                {stornoForm.payments.map((payment, index) => (
                  <div key={`storno-payment-${index}`} className="items-row">
                    <select
                      value={payment.type}
                      onChange={(e) => {
                        const updated = [...stornoForm.payments];
                        updated[index] = {...payment, type: e.target.value};
                        setStornoForm({...stornoForm, payments: updated});
                      }}
                    >
                      <option value="P">В брой (P)</option>
                      <option value="C">С карта (C)</option>
                      <option value="D">Ваучер (D)</option>
                      <option value="I">Банка (I)</option>
                    </select>
                    <input
                      placeholder="Сума"
                      type="number"
                      step="0.01"
                      value={payment.amount}
                      onChange={(e) => {
                        const updated = [...stornoForm.payments];
                        updated[index] = {...payment, amount: e.target.value};
                        setStornoForm({...stornoForm, payments: updated});
                      }}
                    />
                    <button
                      type="button"
                      onClick={() => {
                        const updated = stornoForm.payments.filter((_, i) => i !== index);
                        setStornoForm({...stornoForm, payments: updated.length ? updated : [createPayment()]});
                      }}
                    >
                      ✕
                    </button>
                  </div>
                ))}
              </div>
              <div className="summary">
                <p><strong>Тотал:</strong> {stornoTotal.toFixed(2)} EUR</p>
                <p><strong>Платено:</strong> {stornoPaymentTotal.toFixed(2)} EUR</p>
                {stornoRemaining > 0 && (
                  <p className="warning"><strong>Остава:</strong> {stornoRemaining.toFixed(2)} EUR</p>
                )}
              </div>
              <button className="primary" type="submit" disabled={stornoLoading}>
                {stornoLoading ? "Изпращам..." : "Печат на сторно бележка"}
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
                      {printer.name} ({printer.port || "-"})
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
                      {printer.name} ({printer.port || "-"})
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
                  setModal({ show: false, title: "", message: "", onConfirm: null });
                  if (modal.onConfirm) modal.onConfirm();
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

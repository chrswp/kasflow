import { useEffect, useMemo, useState } from "react";
import axios from "axios";
import * as XLSX from "xlsx";
import { ArrowDownLeft, ArrowUpRight, BarChart3, CalendarDays, Download, FileUp, MoreHorizontal, Plus, ReceiptText, Trash2, WalletCards } from "lucide-react";
import { toast, Toaster } from "sonner";
import "@/App.css";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;
const formatMoney = (amount) => new Intl.NumberFormat("id-ID", { style: "currency", currency: "IDR", maximumFractionDigits: 0 }).format(amount);
const today = new Date().toISOString().slice(0, 10);

function Stat({ label, value, tone, icon: Icon }) {
  return <section className={`stat-card ${tone}`} data-testid={`stat-${label.toLowerCase().replaceAll(" ", "-")}`}><div className="stat-icon"><Icon size={19} /></div><span>{label}</span><strong>{formatMoney(value)}</strong></section>;
}

function App() {
  const [transactions, setTransactions] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [filter, setFilter] = useState("all");
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState({ transaction_type: "cash_out", amount: "", purpose: "", note: "", transaction_date: today, evidence_url: null });

  const loadTransactions = async () => { try { const { data } = await axios.get(`${API}/transactions`); setTransactions(data); } catch { toast.error("Data belum bisa dimuat"); } finally { setLoading(false); } };
  useEffect(() => { loadTransactions(); }, []);
  const summary = useMemo(() => transactions.reduce((acc, item) => { acc[item.transaction_type] += Number(item.amount); return acc; }, { cash_in: 0, cash_out: 0 }), [transactions]);
  const visible = transactions.filter((item) => filter === "all" || item.transaction_type === filter);
  const update = (key, value) => setForm((current) => ({ ...current, [key]: value }));

  const submit = async (event) => {
    event.preventDefault();
    if (!form.amount || !form.purpose) return toast.error("Nominal dan purpose wajib diisi");
    try { await axios.post(`${API}/transactions`, { ...form, amount: Number(form.amount) }); toast.success("Transaksi tersimpan"); setForm({ transaction_type: "cash_out", amount: "", purpose: "", note: "", transaction_date: today, evidence_url: null }); setShowForm(false); loadTransactions(); } catch { toast.error("Transaksi gagal disimpan"); }
  };
  const upload = async (event) => { const file = event.target.files?.[0]; if (!file) return; const body = new FormData(); body.append("file", file); try { const { data } = await axios.post(`${API}/evidence`, body); update("evidence_url", data.url); toast.success("Bukti siap dilampirkan"); } catch { toast.error("Upload bukti gagal"); } };
  const remove = async (id) => { if (!window.confirm("Hapus transaksi ini?")) return; try { await axios.delete(`${API}/transactions/${id}`); setTransactions((items) => items.filter((item) => item.id !== id)); toast.success("Transaksi dihapus"); } catch { toast.error("Transaksi gagal dihapus"); } };
  const exportExcel = () => { const rows = transactions.map((item) => ({ Tanggal: item.transaction_date, Tipe: item.transaction_type === "cash_in" ? "Cash in" : "Cash out", Purpose: item.purpose, Catatan: item.note, Nominal: item.amount })); const sheet = XLSX.utils.json_to_sheet(rows); const workbook = XLSX.utils.book_new(); XLSX.utils.book_append_sheet(workbook, sheet, "Transaksi"); XLSX.writeFile(workbook, `kasflow-${today}.xlsx`); toast.success("Report Excel berhasil dibuat"); };

  return <div className="app-shell"><Toaster position="top-center" richColors />
    <header className="topbar"><div className="brand"><div className="brand-mark"><WalletCards size={21} /></div><div><strong>KasFlow</strong><small>personal cash tracker</small></div></div><button className="icon-button" data-testid="header-menu-button" aria-label="Menu" onClick={() => toast("KasFlow siap mencatat transaksi") }><MoreHorizontal size={22} /></button></header>
    <main className="content"><div className="welcome-row"><div><p className="eyebrow">OVERVIEW · HARI INI</p><h1>Keuanganmu,<br /><em>terkendali.</em></h1></div><div className="date-chip" data-testid="current-date"><CalendarDays size={15} /> {new Intl.DateTimeFormat("id-ID", { day: "numeric", month: "short" }).format(new Date())}</div></div>
      <section className="balance-panel" data-testid="balance-summary"><div><span>Saldo saat ini</span><strong>{formatMoney(summary.cash_in - summary.cash_out)}</strong></div><div className="balance-decoration"><BarChart3 size={52} strokeWidth={1.2} /></div></section>
      <div className="stats-grid"><Stat label="Cash in" value={summary.cash_in} tone="income" icon={ArrowDownLeft} /><Stat label="Cash out" value={summary.cash_out} tone="expense" icon={ArrowUpRight} /></div>
      <div className="section-heading"><div><p className="eyebrow">ACTIVITY</p><h2>Transaksi terbaru</h2></div><button className="export-button" data-testid="export-excel-button" onClick={exportExcel}><Download size={16} /> Export Excel</button></div>
      <div className="filter-tabs" role="tablist"><button className={filter === "all" ? "active" : ""} data-testid="filter-all-button" onClick={() => setFilter("all")}>Semua <b>{transactions.length}</b></button><button className={filter === "cash_in" ? "active" : ""} data-testid="filter-cash-in-button" onClick={() => setFilter("cash_in")}>Masuk</button><button className={filter === "cash_out" ? "active" : ""} data-testid="filter-cash-out-button" onClick={() => setFilter("cash_out")}>Keluar</button></div>
      <section className="transaction-list" data-testid="transaction-list">{loading ? <p className="empty-state" data-testid="transactions-loading">Memuat transaksi...</p> : visible.length === 0 ? <div className="empty-state" data-testid="empty-transactions"><ReceiptText size={30} /><strong>Belum ada transaksi</strong><span>Catat pemasukan atau pengeluaran pertamamu.</span></div> : visible.map((item) => <article className="transaction-item" key={item.id} data-testid={`transaction-item-${item.id}`}><div className={`transaction-icon ${item.transaction_type}`}><ArrowDownLeft size={18} /></div><div className="transaction-info"><strong>{item.purpose}</strong><span>{new Date(item.transaction_date).toLocaleDateString("id-ID", { day: "numeric", month: "short", year: "numeric" })}{item.note ? ` · ${item.note}` : ""}</span></div><div className={`transaction-amount ${item.transaction_type}`}><strong>{item.transaction_type === "cash_in" ? "+" : "−"}{formatMoney(item.amount)}</strong><button data-testid={`delete-transaction-${item.id}`} aria-label="Hapus transaksi" onClick={() => remove(item.id)}><Trash2 size={14} /></button></div></article>)}</section>
    </main>
    <button className="add-fab" data-testid="open-transaction-form-button" onClick={() => setShowForm(true)}><Plus size={22} /> Catat transaksi</button>
    {showForm && <div className="modal-backdrop" data-testid="transaction-modal"><form className="transaction-form" onSubmit={submit}><div className="form-heading"><div><p className="eyebrow">NEW ENTRY</p><h2>Catat transaksi</h2></div><button type="button" className="close-button" data-testid="close-transaction-form-button" onClick={() => setShowForm(false)}>×</button></div><div className="type-switch"><button type="button" className={form.transaction_type === "cash_in" ? "selected in" : ""} data-testid="cash-in-type-button" onClick={() => update("transaction_type", "cash_in")}>Cash in</button><button type="button" className={form.transaction_type === "cash_out" ? "selected out" : ""} data-testid="cash-out-type-button" onClick={() => update("transaction_type", "cash_out")}>Cash out</button></div><label>Nominal<input data-testid="transaction-amount-input" type="number" min="1" placeholder="0" value={form.amount} onChange={(e) => update("amount", e.target.value)} /></label><label>Purpose<input data-testid="transaction-purpose-input" placeholder="Contoh: makan siang" value={form.purpose} onChange={(e) => update("purpose", e.target.value)} /></label><label>Tanggal<input data-testid="transaction-date-input" type="date" value={form.transaction_date} onChange={(e) => update("transaction_date", e.target.value)} /></label><label>Catatan <span className="optional">(opsional)</span><textarea data-testid="transaction-note-input" placeholder="Tambahkan detail kecil..." value={form.note} onChange={(e) => update("note", e.target.value)} /></label><label className="upload-label"><FileUp size={18} /> {form.evidence_url ? "Bukti terlampir" : "Lampirkan bukti (opsional)"}<input data-testid="evidence-upload-input" type="file" accept="image/*,.pdf" onChange={upload} /></label><button className="save-button" data-testid="save-transaction-button" type="submit">Simpan transaksi <ArrowUpRight size={17} /></button></form></div>}
  </div>;
}
export default App;
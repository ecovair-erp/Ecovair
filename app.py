# -*- coding: utf-8 -*-
"""
Ecovair ERP — نظام إدارة موارد المنشأة (محاسبة + مبيعات + مشتريات + مخزون + أصول + خزينة + صلاحيات)
التشغيل:  streamlit run ecovair_erp.py
"""
import streamlit as st
import pandas as pd
import datetime as dt
import json, io, os, re, html, sqlite3, hashlib, hmac, secrets
from contextlib import contextmanager, closing
import plotly.graph_objects as go

try:
    from fpdf import FPDF
    import arabic_reshaper
    from bidi.algorithm import get_display
    PDF_OK = True
except Exception:  # المكتبات غير مثبتة
    PDF_OK = False
try:
    import xlsxwriter  # noqa
    XL_ENGINE = "xlsxwriter"
except Exception:
    XL_ENGINE = "openpyxl"

BASE_DIR = os.path.dirname(os.path.abspath(globals().get("__file__", "ecovair_erp.py")))
DB_PATH = os.environ.get("ECOVAIR_DB_PATH", os.path.join(BASE_DIR, "ecovair_data.sqlite3"))
FONT_DIR = os.path.join(BASE_DIR, "fonts")

st.set_page_config(page_title="Ecovair ERP", page_icon="❄️", layout="wide", initial_sidebar_state="expanded")

# ============================================================
# التصميم
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"], [data-testid="stAppViewContainer"] * { font-family: 'Cairo','Segoe UI',Tahoma,sans-serif !important; }
[data-testid="stAppViewContainer"] { background-color:#eef2f7 !important; }
[data-testid="stHeader"] { background:transparent !important; }
.block-container { padding-top:1rem !important; padding-bottom:2rem !important; max-width:1480px !important; }
[data-testid="stAppViewContainer"] .main p, [data-testid="stAppViewContainer"] .main span,
[data-testid="stAppViewContainer"] .main label, [data-testid="stAppViewContainer"] .main h1,
[data-testid="stAppViewContainer"] .main h2, [data-testid="stAppViewContainer"] .main h3,
[data-testid="stAppViewContainer"] .main div { color:#0f172a; }
h1 { font-size:1.5rem !important; font-weight:800 !important; margin:0 0 .8rem 0 !important; }
h2 { font-size:1.05rem !important; font-weight:700 !important; } h3 { font-size:.95rem !important; font-weight:700 !important; }
[data-testid="stVerticalBlock"] { gap:.8rem !important; }
[data-testid="stVerticalBlockBorderWrapper"] { background:#fff !important; border-radius:14px !important; border:1px solid #e9edf3 !important; box-shadow:0 2px 10px rgba(15,23,42,.05) !important; padding:2px 4px !important; }
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlock"] { gap:.45rem !important; }
.section-title { font-size:.9rem; font-weight:700; color:#0f172a !important; padding:8px 4px 2px 4px; display:flex; gap:6px; align-items:center; }
[data-testid="stDataFrame"] { background:#fff !important; border-radius:12px; overflow:hidden; }
.stSelectbox div[data-baseweb="select"] > div, .stTextInput input, .stNumberInput input, .stDateInput input, .stTextArea textarea { background:#fff !important; color:#0f172a !important; border-radius:10px !important; border:1px solid #e2e8f0 !important; }
.stTabs [data-baseweb="tab-list"] { gap:6px; } .stTabs [data-baseweb="tab"] { border-radius:10px 10px 0 0 !important; }
[data-testid="stSidebar"] { background:linear-gradient(180deg,#0b1120 0%,#101827 55%,#0f172a 100%) !important; border-left:1px solid #1e293b; }
[data-testid="stSidebar"] * { color:#cbd5e1 !important; }
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap:.12rem !important; }
.sb-brand { display:flex; align-items:center; gap:10px; padding:4px 6px 14px 6px; border-bottom:1px solid rgba(148,163,184,.15); margin-bottom:8px; }
.sb-brand .icon { width:40px; height:40px; border-radius:12px; background:linear-gradient(135deg,#0ea5e9,#38bdf8); display:flex; align-items:center; justify-content:center; font-size:1.2rem; box-shadow:0 4px 14px rgba(14,165,233,.4); flex-shrink:0; }
.sb-brand .txt b { font-size:1rem; color:#f8fafc !important; display:block; line-height:1.2; } .sb-brand .txt span { font-size:.66rem; color:#64748b !important; }
.sb-user { background:rgba(56,189,248,.08); border:1px solid rgba(56,189,248,.18); border-radius:10px; padding:8px 10px; margin-bottom:6px; font-size:.75rem; }
.sb-user b { color:#f1f5f9 !important; font-size:.82rem; }
.sb-section-label { font-size:.65rem; color:#3f5169 !important; font-weight:700; letter-spacing:.4px; margin:12px 8px 3px 8px; }
[data-testid="stSidebar"] .stButton > button { width:100%; background:transparent !important; border:1px solid transparent !important; text-align:right !important; justify-content:flex-start !important; font-size:.8rem !important; font-weight:500 !important; padding:6px 12px !important; border-radius:9px !important; box-shadow:none !important; }
[data-testid="stSidebar"] .stButton > button:hover { background:rgba(56,189,248,.10) !important; border-color:rgba(56,189,248,.25) !important; }
[data-testid="stSidebar"] .stButton > button[kind="primary"] { background:linear-gradient(90deg,#0ea5e9,#0284c7) !important; font-weight:700 !important; box-shadow:0 4px 14px rgba(14,165,233,.35) !important; }
[data-testid="stSidebar"] .stButton > button[kind="primary"] * { color:#fff !important; }
.kpi-card { height:92px; background:linear-gradient(135deg,#0f172a 0%,#16324f 100%); border-radius:14px; padding:10px 14px; display:flex; flex-direction:column; justify-content:center; box-shadow:0 4px 14px rgba(15,23,42,.18); }
.kpi-card .kpi-icon { font-size:1.05rem; } .kpi-card .kpi-value { font-size:1.22rem; font-weight:800; color:#38bdf8 !important; } .kpi-card .kpi-label { font-size:.7rem; color:#94a3b8 !important; }
.alert-card { border-radius:10px; padding:9px 12px; margin-bottom:6px; font-size:.8rem; font-weight:500; }
.alert-warn { background:#fef3c7; border-right:4px solid #f59e0b; } .alert-warn * { color:#92400e !important; }
.alert-info { background:#dbeafe; border-right:4px solid #3b82f6; } .alert-info * { color:#1e40af !important; }
.alert-ok { background:#dcfce7; border-right:4px solid #22c55e; } .alert-ok * { color:#166534 !important; }
.alert-bad { background:#fee2e2; border-right:4px solid #ef4444; } .alert-bad * { color:#991b1b !important; }
.stmt { direction:rtl; background:#fff; border-radius:12px; padding:14px 18px; }
.stmt-t { text-align:center; font-weight:800; font-size:1.05rem; } .stmt-s { text-align:center; color:#64748b !important; font-size:.78rem; margin-bottom:10px; }
.stmt table { width:100%; border-collapse:collapse; font-size:.86rem; }
.stmt td { padding:5px 8px; border-bottom:1px solid #f1f5f9; } .stmt td.n { text-align:left; direction:ltr; font-variant-numeric:tabular-nums; width:170px; }
.stmt tr.h td { background:#0f172a; color:#fff !important; font-weight:700; } .stmt tr.h td * { color:#fff !important; }
.stmt tr.s td { font-weight:700; background:#f1f5f9; } .stmt tr.t td { font-weight:800; background:#dbeafe; border-top:2px solid #0f172a; }
.stmt td.i { padding-right:26px; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# ثوابت ومخططات الجداول
# ============================================================
SCHEMA_VER = 3
JOURNAL_COLS = ["التاريخ", "رقم القيد", "نوع العملية", "كود الحساب", "اسم الحساب", "مدين", "دائن", "الطرف", "المرجع", "البيان", "المصدر", "المستخدم"]
INVOICE_COLS = ["رقم الفاتورة", "النوع", "التاريخ", "كود الطرف", "اسم الطرف", "الصافي", "الضريبة", "الإجمالي", "البنود", "ملاحظات", "المستخدم"]
STOCK_COLS = ["التاريخ", "المرجع", "نوع الحركة", "كود الصنف", "الكمية", "تكلفة الوحدة", "البيان"]
CUSTOMER_COLS = ["كود العميل", "اسم العميل", "الهاتف", "العنوان", "السجل التجاري", "الرقم الضريبي", "جهة الاتصال", "حد الائتمان", "مدة السداد (يوم)", "الحالة", "ملاحظات"]
SUPPLIER_COLS = ["كود المورد", "اسم المورد", "الهاتف", "العنوان", "السجل التجاري", "الرقم الضريبي", "جهة الاتصال", "نوع التوريد", "مدة السداد (يوم)", "الحالة", "ملاحظات"]
ITEM_COLS = ["كود الصنف", "اسم الصنف", "الوحدة", "النوع", "سعر البيع", "حد إعادة الطلب", "الحالة"]
ASSET_COLS = ["كود الأصل", "اسم الأصل", "التصنيف", "تاريخ الشراء", "التكلفة", "القيمة التخريدية", "العمر (سنوات)", "كود حساب الأصل", "كود مجمع الإهلاك", "كود مصروف الإهلاك", "رقم قيد الاقتناء", "الحالة", "تاريخ الاستبعاد", "رقم قيد الاستبعاد", "ملاحظات"]
DEP_COLS = ["التاريخ", "رقم القيد", "كود الأصل", "اسم الأصل", "مبلغ الإهلاك"]
TREASURY_COLS = ["كود الحساب", "اسم الحساب", "النوع", "رقم الحساب البنكي", "الحالة"]
CUSTODY_COLS = ["كود العهدة", "الموظف", "تاريخ الصرف", "مبلغ العهدة", "الغرض", "رقم قيد الصرف"]
USER_COLS = ["اسم المستخدم", "الاسم الكامل", "الدور", "الحالة", "كلمة المرور", "آخر دخول"]
AUDIT_COLS = ["الوقت", "المستخدم", "الإجراء", "التفاصيل"]
SCHEMAS = {"journal": JOURNAL_COLS, "invoices": INVOICE_COLS, "stock_moves": STOCK_COLS, "customers": CUSTOMER_COLS,
           "suppliers": SUPPLIER_COLS, "inventory": ITEM_COLS, "fixed_assets": ASSET_COLS, "depreciation_log": DEP_COLS,
           "treasury": TREASURY_COLS, "custody": CUSTODY_COLS, "users": USER_COLS, "audit_log": AUDIT_COLS}
INT_COLS = {"كود الحساب", "كود حساب الأصل", "كود مجمع الإهلاك", "كود مصروف الإهلاك"}
NUM_COLS = {"مدين", "دائن", "الصافي", "الضريبة", "الإجمالي", "الكمية", "تكلفة الوحدة", "سعر البيع", "حد إعادة الطلب", "حد الائتمان",
            "مدة السداد (يوم)", "التكلفة", "القيمة التخريدية", "العمر (سنوات)", "مبلغ الإهلاك", "مبلغ العهدة"}
PERSIST_KEYS = list(SCHEMAS) + ["custom_chart", "role_permissions", "settings"]

AR_CODE, AP_CODE, CASH_CODE, BANK_CODE = 1210, 2110, 1110, 1120
VAT_IN, CUSTODY_ACC, INV_ACC = 1220, 1230, 1310
VAT_OUT, OPEN_EQ, CAPITAL = 2320, 3120, 3110
SALES_ACC, SALES_RET, OTHER_INC, ASSET_GAIN = 4110, 4120, 4210, 4230
COGS_ACC, PURCH_ACC, STOCK_ADJ, DEP_EXP, ASSET_LOSS = 5110, 5120, 5250, 5280, 5290
ACCUM_DEP = 1420
ASSET_CLASSES = {"معدات وآلات": 1410, "سيارات ووسائل نقل": 1430, "أثاث وتجهيزات": 1440, "أجهزة حاسب وإلكترونيات": 1450, "مباني وإنشاءات": 1460}
SYSTEM_CODES = {1110, 1120, 1210, 1220, 1230, 1310, 1410, 1420, 1430, 1440, 1450, 1460, 2110, 2320, 3110, 3120, 4110, 4120, 4210, 4230,
                5110, 5120, 5210, 5220, 5230, 5250, 5280, 5290}
TYPE_DIGIT = {"أصل": "1", "التزام": "2", "ملكية": "3", "إيراد": "4", "مصروف": "5"}


class AccountingError(Exception):
    pass


def default_chart():
    R = [(1000, "الأصول", "أصل", "رئيسي"), (1100, "النقدية والبنوك", "أصل", "فرعي"), (1110, "الصندوق (الخزنة الرئيسية)", "أصل", "تفصيلي"),
         (1120, "الحساب البنكي", "أصل", "تفصيلي"), (1200, "الذمم المدينة والأرصدة المدينة", "أصل", "فرعي"), (1210, "عملاء محليون", "أصل", "تفصيلي"),
         (1220, "ضريبة القيمة المضافة - مدخلات", "أصل", "تفصيلي"), (1230, "عهد وسلف الموظفين", "أصل", "تفصيلي"), (1300, "المخزون", "أصل", "فرعي"),
         (1310, "مخزون البضاعة والمواد", "أصل", "تفصيلي"), (1400, "الأصول الثابتة", "أصل", "فرعي"), (1410, "معدات وآلات", "أصل", "تفصيلي"),
         (1420, "مجمع إهلاك الأصول الثابتة", "أصل", "تفصيلي"), (1430, "سيارات ووسائل نقل", "أصل", "تفصيلي"), (1440, "أثاث وتجهيزات", "أصل", "تفصيلي"),
         (1450, "أجهزة حاسب وإلكترونيات", "أصل", "تفصيلي"), (1460, "مباني وإنشاءات", "أصل", "تفصيلي"),
         (2000, "الالتزامات", "التزام", "رئيسي"), (2100, "الذمم الدائنة", "التزام", "فرعي"), (2110, "موردون محليون", "التزام", "تفصيلي"),
         (2300, "الضرائب المستحقة", "التزام", "فرعي"), (2310, "ضرائب أخرى مستحقة", "التزام", "تفصيلي"),
         (2320, "ضريبة القيمة المضافة - مخرجات", "التزام", "تفصيلي"), (2400, "أرصدة دائنة أخرى", "التزام", "فرعي"), (2410, "مصروفات مستحقة", "التزام", "تفصيلي"),
         (3000, "حقوق الملكية", "ملكية", "رئيسي"), (3110, "رأس المال المدفوع", "ملكية", "تفصيلي"), (3120, "أرصدة افتتاحية (حساب تسوية)", "ملكية", "تفصيلي"),
         (4000, "الإيرادات", "إيراد", "رئيسي"), (4110, "مبيعات محلية (توريد وتركيب)", "إيراد", "تفصيلي"), (4120, "مردودات ومسموحات المبيعات", "إيراد", "تفصيلي"),
         (4210, "إيرادات أخرى", "إيراد", "تفصيلي"), (4230, "أرباح بيع أصول ثابتة", "إيراد", "تفصيلي"),
         (5000, "المصروفات", "مصروف", "رئيسي"), (5110, "تكلفة البضاعة المباعة", "مصروف", "تفصيلي"), (5120, "مشتريات مواد وخامات ومقاولين", "مصروف", "تفصيلي"),
         (5210, "الرواتب والأجور", "مصروف", "تفصيلي"), (5220, "الإيجار", "مصروف", "تفصيلي"), (5230, "مصروفات عمومية وإدارية", "مصروف", "تفصيلي"),
         (5240, "مصروفات نقل وانتقالات", "مصروف", "تفصيلي"), (5250, "عجز وزيادة جرد المخزون", "مصروف", "تفصيلي"), (5270, "الصيانة والإصلاحات", "مصروف", "تفصيلي"),
         (5280, "مصروف إهلاك الأصول الثابتة", "مصروف", "تفصيلي"), (5290, "خسائر بيع أصول ثابتة", "مصروف", "تفصيلي"), (5310, "مصروفات بنكية", "مصروف", "تفصيلي")]
    return pd.DataFrame(R, columns=["الكود", "اسم الحساب", "النوع", "التصنيف"])


# ============================================================
# الصلاحيات
# ============================================================
LEVELS = {"لا وصول": 0, "عرض فقط": 1, "إدخال": 2, "تعديل وحذف": 3}
MODULES = {"dashboard": "لوحة التحكم", "sales": "المبيعات", "purchases": "المشتريات", "customers": "العملاء", "suppliers": "الموردون",
           "inventory": "المخزون", "treasury": "الخزينة والبنوك", "custody": "العهد", "journal": "القيود اليومية", "ledger": "دفتر الأستاذ",
           "reports": "القوائم والتقارير", "assets": "الأصول الثابتة", "coa": "شجرة الحسابات", "data": "الاستيراد والتصدير",
           "users": "المستخدمون والصلاحيات", "settings": "الإعدادات"}
ADMIN_ROLE = "مدير النظام"


def default_role_perms():
    none = {m: "لا وصول" for m in MODULES}
    roles = {ADMIN_ROLE: {m: "تعديل وحذف" for m in MODULES},
             "مراجع": {m: "عرض فقط" for m in MODULES},
             "محاسب": {**none, **{m: "تعديل وحذف" for m in ["dashboard", "sales", "purchases", "customers", "suppliers", "treasury", "custody", "journal", "ledger", "reports", "assets", "data"]}, "inventory": "عرض فقط", "coa": "إدخال"},
             "أمين مخزن": {**none, "inventory": "تعديل وحذف"},
             "مسؤول مبيعات": {**none, "dashboard": "عرض فقط", "sales": "تعديل وحذف", "customers": "تعديل وحذف", "inventory": "عرض فقط"},
             "مسؤول مشتريات": {**none, "dashboard": "عرض فقط", "purchases": "تعديل وحذف", "suppliers": "تعديل وحذف", "inventory": "عرض فقط"}}
    return pd.DataFrame([{"الدور": r, **{MODULES[m]: v[m] for m in MODULES}} for r, v in roles.items()])


def hash_pw(pw, salt=None):
    salt = salt or secrets.token_hex(8)
    return f"{salt}${hashlib.pbkdf2_hmac('sha256', pw.encode(), salt.encode(), 120_000).hex()}"


def check_pw(pw, stored):
    try:
        salt, h = str(stored).split("$")
        return hmac.compare_digest(hash_pw(pw, salt).split("$")[1], h)
    except Exception:
        return False


def default_users():
    return pd.DataFrame([{"اسم المستخدم": "admin", "الاسم الكامل": "مدير النظام", "الدور": ADMIN_ROLE, "الحالة": "نشط", "كلمة المرور": hash_pw("admin123"), "آخر دخول": ""}], columns=USER_COLS)


def cur_role():
    a = st.session_state.get("auth")
    return a["role"] if a else None


def user_level(module):
    role = cur_role()
    if not role:
        return 0
    if role == ADMIN_ROLE:
        return 3
    rp = st.session_state.role_permissions
    row = rp[rp["الدور"] == role]
    if row.empty:
        return 0
    return LEVELS.get(str(row.iloc[0].get(MODULES.get(module, module), "لا وصول")), 0)


def can(module, lvl=1):
    return user_level(module) >= lvl


# ============================================================
# أدوات عامة
# ============================================================
def to_date(x):
    if isinstance(x, pd.Timestamp):
        return x.date()
    if isinstance(x, dt.datetime):
        return x.date()
    if isinstance(x, dt.date):
        return x
    return pd.to_datetime(str(x)).date()


def ts(x):
    return pd.Timestamp(to_date(x))


def today():
    return dt.date.today()


def cents(x):
    return int(round(float(x or 0) * 100))


def fromc(n):
    return round(n / 100.0, 2)


def r2(x):
    return round(float(x or 0) + 0.0, 2)


def fmt(x, d=2):
    x = float(x or 0)
    s = f"{abs(x):,.{d}f}"
    return f"({s})" if x < -0.004 else s


def ensure_schema(df, cols):
    if not isinstance(df, pd.DataFrame):
        df = pd.DataFrame(columns=cols)
    df = df.copy()
    for c in cols:
        if c not in df.columns:
            df[c] = 0 if c in INT_COLS else (0.0 if c in NUM_COLS else "")
    df = df[cols]
    for c in cols:
        if c in INT_COLS:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)
        elif c in NUM_COLS:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0).astype(float)
        else:
            df[c] = df[c].where(df[c].notna(), "").astype(str)
    return df.reset_index(drop=True)


def opt_code(s):
    return str(s).split(" — ")[0].strip() if s is not None and str(s) not in ("nan", "None") else ""


def append_rows(key, rows):
    if not rows:
        return
    new = ensure_schema(pd.DataFrame(rows), SCHEMAS[key])
    cur = st.session_state[key]
    st.session_state[key] = new if cur.empty else pd.concat([cur, new], ignore_index=True)


# ============================================================
# التخزين الدائم (SQLite)
# ============================================================
def _db_init():
    with closing(sqlite3.connect(DB_PATH, timeout=30)) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS app_state (state_key TEXT PRIMARY KEY, payload TEXT NOT NULL)")
        conn.commit()


def _db_read(key):
    try:
        with closing(sqlite3.connect(DB_PATH, timeout=30)) as conn:
            row = conn.execute("SELECT payload FROM app_state WHERE state_key=?", (key,)).fetchone()
        return row[0] if row else None
    except Exception:
        return None


def _db_write(key, payload):
    with closing(sqlite3.connect(DB_PATH, timeout=30)) as conn:
        conn.execute("INSERT INTO app_state(state_key,payload) VALUES(?,?) ON CONFLICT(state_key) DO UPDATE SET payload=excluded.payload", (key, payload))
        conn.commit()


def _json_default(o):
    return o.item() if hasattr(o, "item") else str(o)


def _pack(v):
    if isinstance(v, pd.DataFrame):
        return json.dumps({"kind": "df", "columns": list(v.columns), "data": v.astype(object).where(pd.notna(v), None).to_dict(orient="records")}, ensure_ascii=False, default=_json_default)
    return json.dumps({"kind": "json", "data": v}, ensure_ascii=False, default=_json_default)


def _unpack(raw):
    o = json.loads(raw)
    if o.get("kind") == "df":
        return pd.DataFrame(o.get("data", []), columns=o.get("columns"))
    return o.get("data")


def persist():
    h = st.session_state.setdefault("_h", {})
    for k in PERSIST_KEYS:
        v = st.session_state.get(k)
        if v is None:
            continue
        payload = _pack(v)
        d = hashlib.md5(payload.encode()).hexdigest()
        if h.get(k) != d:
            _db_write(k, payload)
            h[k] = d


def load_all():
    h = st.session_state.setdefault("_h", {})
    for k in PERSIST_KEYS:
        raw = _db_read(k)
        if raw is None:
            continue
        try:
            st.session_state[k] = _unpack(raw)
            h[k] = hashlib.md5(raw.encode()).hexdigest()
        except Exception:
            pass


@contextmanager
def atomic(keep=True):
    """تنفيذ عملية كاملة أو لا شيء. keep=False للفحص التجريبي (يتراجع دائمًا)."""
    s = st.session_state
    keys = list(SCHEMAS) + ["custom_chart"]
    snap = {k: s[k].copy() for k in keys}
    try:
        yield
        if not keep:
            for k, v in snap.items():
                s[k] = v
    except Exception:
        for k, v in snap.items():
            s[k] = v
        raise


def log_action(action, detail=""):
    a = st.session_state.get("auth")
    append_rows("audit_log", [{"الوقت": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "المستخدم": a["user"] if a else "النظام", "الإجراء": action, "التفاصيل": detail}])
    if len(st.session_state.audit_log) > 5000:
        st.session_state.audit_log = st.session_state.audit_log.tail(5000).reset_index(drop=True)


def cur_user():
    a = st.session_state.get("auth")
    return a["user"] if a else "النظام"


# ============================================================
# شجرة الحسابات
# ============================================================
def chart():
    return st.session_state.custom_chart


def acct_row(code):
    r = chart()[chart()["الكود"] == int(code)]
    return None if r.empty else r.iloc[0]


def acct_name(code):
    r = acct_row(code)
    return "" if r is None else str(r["اسم الحساب"])


def postable():
    ch = chart()
    return ch[ch["التصنيف"] == "تفصيلي"]


def account_options(types=None):
    p = postable()
    if types:
        p = p[p["النوع"].isin(types)]
    return [f"{r['الكود']} — {r['اسم الحساب']}" for _, r in p.sort_values("الكود").iterrows()]


def ensure_chart():
    base = default_chart()
    ch = st.session_state.get("custom_chart")
    if not isinstance(ch, pd.DataFrame) or "الكود" not in ch.columns:
        st.session_state.custom_chart = base
        return
    ch = ch[["الكود", "اسم الحساب", "النوع", "التصنيف"]].copy()
    ch["الكود"] = pd.to_numeric(ch["الكود"], errors="coerce").fillna(0).astype(int)
    missing = base[~base["الكود"].isin(ch["الكود"])]
    if not missing.empty:
        ch = pd.concat([ch, missing], ignore_index=True)
    st.session_state.custom_chart = ch.sort_values("الكود").reset_index(drop=True)


# ============================================================
# الأطراف (عملاء / موردون)
# ============================================================
PK = {"customer": dict(key="customers", code="كود العميل", name="اسم العميل", prefix="C", control=AR_CODE, label="العميل", plural="العملاء"),
      "supplier": dict(key="suppliers", code="كود المورد", name="اسم المورد", prefix="S", control=AP_CODE, label="المورد", plural="الموردون")}


def ptable(kind):
    return st.session_state[PK[kind]["key"]]


def party_row(kind, code):
    t = ptable(kind)
    r = t[t[PK[kind]["code"]] == str(code)]
    return None if r.empty else r.iloc[0]


def party_options(kind, active_only=True):
    t = ptable(kind)
    if active_only:
        t = t[t["الحالة"] == "نشط"]
    return [f"{r[PK[kind]['code']]} — {r[PK[kind]['name']]}" for _, r in t.iterrows()]


def party_name(code):
    code = str(code)
    for k in PK:
        r = party_row(k, code)
        if r is not None:
            return str(r[PK[k]["name"]])
    return ""


def next_party_code(kind):
    t = ptable(kind)
    p = PK[kind]["prefix"]
    nums = [int(m.group(1)) for x in t[PK[kind]["code"]] if (m := re.match(rf"^{p}(\d+)$", str(x)))]
    return f"{p}{(max(nums) + 1 if nums else 1):04d}"


def next_no(prefix):
    s = st.session_state
    used = list(s.journal["رقم القيد"].unique()) + list(s.invoices["رقم الفاتورة"])
    nums = [int(m.group(1)) for x in used if (m := re.match(rf"^{prefix}-(\d+)$", str(x)))]
    return f"{prefix}-{(max(nums) + 1 if nums else 1):05d}"


# ============================================================
# دفتر الأستاذ العام: محرك الترحيل
# ============================================================
def fiscal_start(d):
    d = to_date(d)
    try:
        m, dd = [int(x) for x in str(st.session_state.settings.get("بداية السنة المالية", "01-01")).split("-")]
        fs = dt.date(d.year, m, dd)
    except Exception:
        fs = dt.date(d.year, 1, 1)
    return fs if fs <= d else dt.date(d.year - 1, fs.month, fs.day)


def check_lock(d):
    lock = str(st.session_state.settings.get("تاريخ الإقفال", "") or "")
    if lock and to_date(d) <= to_date(lock):
        raise AccountingError(f"الفترة مقفلة حتى {lock}؛ لا يمكن الترحيل أو التعديل أو الحذف بتاريخ {to_date(d)}.")


def post_entry(date, lines, op_type, source="يدوي", entry_no=None, prefix="J", note="", user=None):
    """يرحّل قيدًا متعدد السطور بعد التحقق الكامل (توازن، حسابات، أطراف، إقفال الفترة)."""
    date = to_date(date)
    check_lock(date)
    clean = []
    for i, l in enumerate(lines, 1):
        d, c = cents(l.get("debit", 0)), cents(l.get("credit", 0))
        if d == 0 and c == 0:
            continue
        if d < 0 or c < 0:
            raise AccountingError(f"السطر {i}: لا يجوز إدخال مبلغ سالب.")
        if d > 0 and c > 0:
            raise AccountingError(f"السطر {i}: لا يجوز أن يحتوي السطر على مدين ودائن معًا.")
        code = int(l["code"])
        a = acct_row(code)
        if a is None:
            raise AccountingError(f"السطر {i}: الحساب {code} غير موجود.")
        if a["التصنيف"] != "تفصيلي":
            raise AccountingError(f"السطر {i}: الحساب {code} حساب تجميعي ولا يقبل الترحيل المباشر.")
        party = str(l.get("party") or "")
        if code == AR_CODE and party_row("customer", party) is None:
            raise AccountingError(f"السطر {i}: يجب تحديد العميل عند الترحيل على حساب العملاء.")
        if code == AP_CODE and party_row("supplier", party) is None:
            raise AccountingError(f"السطر {i}: يجب تحديد المورد عند الترحيل على حساب الموردين.")
        if code not in (AR_CODE, AP_CODE):
            party = ""
        if code == CUSTODY_ACC and not str(l.get("ref") or ""):
            raise AccountingError(f"السطر {i}: يجب تحديد رقم العهدة (المرجع) عند الترحيل على حساب العهد.")
        clean.append((code, str(a["اسم الحساب"]), d, c, party, str(l.get("ref") or ""), str(l.get("note") or note or "")))
    if len(clean) < 2:
        raise AccountingError("القيد يجب أن يحتوي على طرفين على الأقل بمبالغ غير صفرية.")
    td, tc = sum(x[2] for x in clean), sum(x[3] for x in clean)
    if td != tc:
        raise AccountingError(f"القيد غير متوازن: إجمالي المدين {fromc(td):,.2f} ≠ إجمالي الدائن {fromc(tc):,.2f}.")
    entry_no = entry_no or next_no(prefix)
    if (st.session_state.journal["رقم القيد"] == entry_no).any():
        raise AccountingError(f"رقم القيد {entry_no} مستخدم بالفعل.")
    user = user or cur_user()
    append_rows("journal", [{"التاريخ": str(date), "رقم القيد": entry_no, "نوع العملية": op_type, "كود الحساب": code, "اسم الحساب": nm, "مدين": fromc(d), "دائن": fromc(c),
                             "الطرف": p, "المرجع": rf, "البيان": nt, "المصدر": source, "المستخدم": user} for code, nm, d, c, p, rf, nt in clean])
    return entry_no


def delete_entries(nos):
    s = st.session_state
    nos = list(dict.fromkeys(nos))
    for n in nos:
        d = s.journal.loc[s.journal["رقم القيد"] == n, "التاريخ"]
        if len(d):
            check_lock(d.iloc[0])
        if (s.fixed_assets["رقم قيد الاقتناء"] == n).any():
            raise AccountingError(f"القيد {n} هو قيد اقتناء أصل ثابت؛ احذف الأصل من صفحة الأصول الثابتة.")
        if (s.custody["رقم قيد الصرف"] == n).any():
            raise AccountingError(f"القيد {n} هو قيد صرف عهدة؛ احذف العهدة من صفحة العهد.")
    s.journal = s.journal[~s.journal["رقم القيد"].isin(nos)].reset_index(drop=True)
    s.invoices = s.invoices[~s.invoices["رقم الفاتورة"].isin(nos)].reset_index(drop=True)
    s.stock_moves = s.stock_moves[~s.stock_moves["المرجع"].isin(nos)].reset_index(drop=True)
    s.depreciation_log = s.depreciation_log[~s.depreciation_log["رقم القيد"].isin(nos)].reset_index(drop=True)
    fa = s.fixed_assets
    m = fa["رقم قيد الاستبعاد"].isin(nos)
    if m.any():
        fa.loc[m, ["الحالة", "تاريخ الاستبعاد", "رقم قيد الاستبعاد"]] = ["نشط", "", ""]
    log_action("حذف قيود", ", ".join(nos)[:300])


def reverse_entry(no, date=None):
    s = st.session_state
    rows = s.journal[s.journal["رقم القيد"] == no]
    if rows.empty:
        raise AccountingError("القيد غير موجود.")
    lines = [dict(code=r["كود الحساب"], debit=r["دائن"], credit=r["مدين"], party=r["الطرف"], ref=r["المرجع"], note=f"عكس القيد {no}") for _, r in rows.iterrows()]
    new = post_entry(date or today(), lines, "قيد عكسي", "عكس", prefix="RV")
    log_action("عكس قيد", f"{no} → {new}")
    return new


def jdf():
    j = st.session_state.journal.copy()
    j["_d"] = pd.to_datetime(j["التاريخ"], errors="coerce")
    return j


def net_by_account(frm=None, to=None):
    """صافي (مدين - دائن) لكل حساب ضمن الفترة."""
    j = jdf()
    if frm is not None:
        j = j[j["_d"] >= ts(frm)]
    if to is not None:
        j = j[j["_d"] <= ts(to)]
    g = j.groupby("كود الحساب")[["مدين", "دائن"]].sum()
    return (g["مدين"] - g["دائن"]).to_dict()


def code_sum(net, lo, hi):
    return sum(v for k, v in net.items() if lo <= k <= hi)


def entries_summary(j=None):
    j = st.session_state.journal if j is None else j
    cols = ["رقم القيد", "التاريخ", "نوع العملية", "المصدر", "الإجمالي", "البيان", "عدد السطور", "المستخدم"]
    if j.empty:
        return pd.DataFrame(columns=cols)
    first = lambda s: next((x for x in s if str(x).strip()), "")
    out = j.groupby("رقم القيد", sort=False).agg(**{"التاريخ": ("التاريخ", "first"), "نوع العملية": ("نوع العملية", "first"), "المصدر": ("المصدر", "first"),
                                                    "الإجمالي": ("مدين", "sum"), "البيان": ("البيان", first), "عدد السطور": ("مدين", "size"), "المستخدم": ("المستخدم", "first")}).reset_index()
    return out.sort_values(["التاريخ", "رقم القيد"], ascending=False).reset_index(drop=True)[cols]


# ---------------- أرصدة الأطراف ----------------
def party_balance(kind, code, upto=None):
    j = jdf()
    m = (j["كود الحساب"] == PK[kind]["control"]) & (j["الطرف"] == str(code))
    if upto is not None:
        m &= j["_d"] <= ts(upto)
    return float(j.loc[m, "مدين"].sum() - j.loc[m, "دائن"].sum())


def party_balances(kind, upto=None):
    j = jdf()
    m = j["كود الحساب"] == PK[kind]["control"]
    if upto is not None:
        m &= j["_d"] <= ts(upto)
    g = j[m].groupby("الطرف")[["مدين", "دائن"]].sum()
    t = ptable(kind).copy()
    p = PK[kind]
    t["مدين"] = t[p["code"]].map(g["مدين"]).fillna(0.0)
    t["دائن"] = t[p["code"]].map(g["دائن"]).fillna(0.0)
    t["net"] = t["مدين"] - t["دائن"]
    return t


def side_label(net):
    return "مدين (عليه)" if net > 0.004 else ("دائن (له)" if net < -0.004 else "متزن")


# ---------------- الخزينة والبنوك ----------------
def treasury_codes(active=True):
    t = st.session_state.treasury
    if active:
        t = t[t["الحالة"] == "نشط"]
    return [int(x) for x in t["كود الحساب"]]


def treasury_options(active=True):
    t = st.session_state.treasury
    if active:
        t = t[t["الحالة"] == "نشط"]
    return [f"{r['كود الحساب']} — {r['اسم الحساب']}" for _, r in t.iterrows()]


def cash_balance(code, upto=None):
    return fromc(cents(net_by_account(None, upto).get(int(code), 0.0)))


def check_cash(code, amount_c, date):
    if st.session_state.settings.get("السماح برصيد نقدية سالب", False):
        return
    bal = cents(cash_balance(code, date))
    if bal < amount_c:
        raise AccountingError(f"رصيد الحساب «{acct_name(code)}» غير كافٍ: المتاح {fromc(bal):,.2f} والمطلوب {fromc(amount_c):,.2f}.")


def alloc_code(lo, hi):
    used = set(chart()["الكود"])
    for c in range(lo, hi + 1):
        if c not in used:
            return c
    raise AccountingError("لا توجد أكواد متاحة في هذا النطاق.")


def add_treasury(name, kind, iban="", opening=0.0, open_date=None):
    if not name.strip():
        raise AccountingError("اسم الحساب مطلوب.")
    code = alloc_code(1121, 1199) if kind == "بنك" else alloc_code(1111, 1119)
    st.session_state.custom_chart = pd.concat([chart(), pd.DataFrame([{"الكود": code, "اسم الحساب": name.strip(), "النوع": "أصل", "التصنيف": "تفصيلي"}])], ignore_index=True).sort_values("الكود").reset_index(drop=True)
    append_rows("treasury", [{"كود الحساب": code, "اسم الحساب": name.strip(), "النوع": kind, "رقم الحساب البنكي": iban, "الحالة": "نشط"}])
    if abs(opening) > 0.004:
        d = open_date or fiscal_start(today())
        amt = abs(opening)
        lines = [dict(code=code, debit=amt), dict(code=OPEN_EQ, credit=amt)] if opening > 0 else [dict(code=OPEN_EQ, debit=amt), dict(code=code, credit=amt)]
        post_entry(d, lines, "رصيد افتتاحي", "رصيد افتتاحي", prefix="OP", note=f"رصيد افتتاحي - {name}")
    log_action("إضافة حساب خزينة", f"{code} {name}")
    return code


# ---------------- الأطراف: إضافة ----------------
def add_party(kind, data, opening=0.0, side="عليه", open_date=None):
    p = PK[kind]
    name = str(data.get(p["name"], "")).strip()
    if not name:
        raise AccountingError(f"اسم {p['label']} مطلوب.")
    t = ptable(kind)
    if (t[p["name"]].str.strip() == name).any():
        raise AccountingError(f"يوجد {p['label']} بنفس الاسم.")
    code = str(data.get(p["code"]) or "").strip() or next_party_code(kind)
    if (t[p["code"]] == code).any():
        raise AccountingError(f"الكود {code} مستخدم بالفعل.")
    row = {c: data.get(c, "") for c in SCHEMAS[p["key"]]}
    row[p["code"]] = code
    row["الحالة"] = row.get("الحالة") or "نشط"
    append_rows(p["key"], [row])
    if abs(opening) > 0.004:
        d = open_date or fiscal_start(today())
        amt = abs(opening)
        ctrl = p["control"]
        debit_party = side == "عليه"  # الرصيد المدين (عليه) => مدين على حساب الطرف، والدائن (له) => دائن
        lines = [dict(code=ctrl, debit=amt, party=code), dict(code=OPEN_EQ, credit=amt)] if debit_party else [dict(code=OPEN_EQ, debit=amt), dict(code=ctrl, credit=amt, party=code)]
        post_entry(d, lines, "رصيد افتتاحي", "رصيد افتتاحي", prefix="OP", note=f"رصيد افتتاحي - {name}")
    log_action(f"إضافة {p['label']}", f"{code} {name}")
    return code


# ---------------- المخزون ----------------
def stock_state(item, upto=None):
    m = st.session_state.stock_moves
    m = m[m["كود الصنف"] == item]
    if upto is not None:
        m = m[pd.to_datetime(m["التاريخ"]) <= ts(upto)]
    if m.empty:
        return 0.0, 0.0, 0.0
    m = m.assign(_d=pd.to_datetime(m["التاريخ"])).sort_values("_d", kind="stable")
    qty = val = last = 0.0
    for q, c in zip(m["الكمية"], m["تكلفة الوحدة"]):
        if q > 0:
            val += q * c
            qty += q
            last = c
        else:
            avg = val / qty if qty > 1e-9 else (last or c)
            val += q * avg
            qty += q
            if abs(qty) < 1e-9:
                val = 0.0
    avg = val / qty if qty > 1e-9 else last
    return qty, val, avg


def stock_position(upto=None):
    rows = []
    for _, it in st.session_state.inventory.iterrows():
        q, v, a = stock_state(it["كود الصنف"], upto)
        rows.append({"كود الصنف": it["كود الصنف"], "اسم الصنف": it["اسم الصنف"], "الوحدة": it["الوحدة"], "النوع": it["النوع"], "الكمية": round(q, 3), "متوسط التكلفة": round(a, 4), "القيمة": round(v, 2),
                     "سعر البيع": it["سعر البيع"], "حد إعادة الطلب": it["حد إعادة الطلب"], "الحالة": it["الحالة"]})
    return pd.DataFrame(rows, columns=["كود الصنف", "اسم الصنف", "الوحدة", "النوع", "الكمية", "متوسط التكلفة", "القيمة", "سعر البيع", "حد إعادة الطلب", "الحالة"])


def add_move(date, ref, mtype, item, qty, cost, note=""):
    append_rows("stock_moves", [{"التاريخ": str(to_date(date)), "المرجع": ref, "نوع الحركة": mtype, "كود الصنف": item, "الكمية": qty, "تكلفة الوحدة": cost, "البيان": note}])


def add_item(data, opening_qty=0.0, opening_cost=0.0, open_date=None):
    code = str(data.get("كود الصنف", "")).strip()
    name = str(data.get("اسم الصنف", "")).strip()
    if not code or not name:
        raise AccountingError("كود الصنف واسمه مطلوبان.")
    if (st.session_state.inventory["كود الصنف"] == code).any():
        raise AccountingError(f"كود الصنف {code} مستخدم بالفعل.")
    row = {c: data.get(c, "") for c in ITEM_COLS}
    row["النوع"] = row.get("النوع") or "مخزني"
    row["الحالة"] = row.get("الحالة") or "نشط"
    row["الوحدة"] = row.get("الوحدة") or "قطعة"
    append_rows("inventory", [row])
    if opening_qty > 0 and row["النوع"] == "مخزني":
        if opening_cost < 0:
            raise AccountingError("تكلفة الوحدة لا يمكن أن تكون سالبة.")
        d = open_date or fiscal_start(today())
        val = fromc(cents(opening_qty * opening_cost))
        if val > 0:
            no = post_entry(d, [dict(code=INV_ACC, debit=val), dict(code=OPEN_EQ, credit=val)], "رصيد افتتاحي مخزون", "رصيد افتتاحي", prefix="OP", note=f"رصيد افتتاحي - {name}")
        else:
            no = next_no("OP")
        add_move(d, no, "رصيد افتتاحي", code, opening_qty, opening_cost, f"رصيد افتتاحي - {name}")
    log_action("إضافة صنف", f"{code} {name}")


def stock_adjust(date, item, counted, unit_cost=None, note=""):
    it = st.session_state.inventory[st.session_state.inventory["كود الصنف"] == item]
    if it.empty or it.iloc[0]["النوع"] != "مخزني":
        raise AccountingError("الصنف غير موجود أو غير مخزني.")
    q, v, avg = stock_state(item, date)
    diff = round(counted - q, 3)
    if abs(diff) < 1e-9:
        raise AccountingError("لا يوجد فرق بين الجرد الفعلي والرصيد الدفتري.")
    cost = avg if (avg > 0 and diff < 0) or (unit_cost is None) else unit_cost
    if diff > 0 and avg > 0 and unit_cost is None:
        cost = avg
    val = fromc(cents(abs(diff) * cost))
    lines = ([dict(code=STOCK_ADJ, debit=val), dict(code=INV_ACC, credit=val)] if diff < 0 else [dict(code=INV_ACC, debit=val), dict(code=STOCK_ADJ, credit=val)])
    no = post_entry(date, lines, "تسوية جرد مخزون", "تسوية مخزون", prefix="ADJ", note=note or f"تسوية جرد {item}")
    add_move(date, no, "تسوية جرد", item, diff, cost, note)
    log_action("تسوية جرد", f"{item} فرق {diff}")
    return no


# ---------------- الفواتير ----------------
INV_KINDS = {"sales": dict(label="فاتورة مبيعات", prefix="SI", party="customer"), "sales_return": dict(label="مرتجع مبيعات", prefix="SR", party="customer"),
             "purchase": dict(label="فاتورة مشتريات", prefix="PI", party="supplier"), "purchase_return": dict(label="مرتجع مشتريات", prefix="PR", party="supplier")}
INV_LABEL2KIND = {v["label"]: k for k, v in INV_KINDS.items()}


def post_invoice(kind, date, party_code, lines, vat_rate=0.0, notes="", inv_no=None, allow_over_credit=False):
    K = INV_KINDS[kind]
    date = to_date(date)
    check_lock(date)
    pk = K["party"]
    P = party_row(pk, party_code)
    if P is None:
        raise AccountingError(f"{PK[pk]['label']} غير موجود.")
    if P["الحالة"] != "نشط":
        raise AccountingError(f"{PK[pk]['label']} «{P[PK[pk]['name']]}» موقوف ولا يمكن التعامل معه.")
    if not lines:
        raise AccountingError("الفاتورة لا تحتوي على بنود.")
    if vat_rate < 0 or vat_rate > 100:
        raise AccountingError("نسبة الضريبة غير صحيحة.")
    items = {r["كود الصنف"]: r for _, r in st.session_state.inventory.iterrows()}
    net_c = 0
    rows = []
    for i, l in enumerate(lines, 1):
        qty, price = float(l["qty"]), float(l["price"])
        if qty <= 0 or price < 0:
            raise AccountingError(f"البند {i}: الكمية يجب أن تكون أكبر من صفر والسعر غير سالب.")
        it = items.get(l.get("item") or "")
        if l.get("item") and it is None:
            raise AccountingError(f"البند {i}: الصنف {l['item']} غير موجود.")
        if it is not None and it["الحالة"] != "نشط":
            raise AccountingError(f"البند {i}: الصنف {l['item']} موقوف.")
        stock = it is not None and it["النوع"] == "مخزني"
        acct = int(l.get("acct") or 0) or (SALES_ACC if kind == "sales" else PURCH_ACC)
        amt_c = cents(qty * price)
        net_c += amt_c
        rows.append(dict(item=l.get("item") or "", desc=str(l.get("desc") or (it["اسم الصنف"] if it is not None else "")), qty=qty, price=price, amt_c=amt_c, stock=stock, acct=acct))
    vat_c = int(round(net_c * vat_rate / 100.0))
    total_c = net_c + vat_c
    jl, moves, need = [], [], {}
    tot = fromc(total_c)
    if kind == "sales":
        limit = float(P["حد الائتمان"] or 0)
        if limit > 0 and not allow_over_credit:
            exist = party_balance("customer", party_code)
            if inv_no:
                exist -= float(st.session_state.invoices.loc[st.session_state.invoices["رقم الفاتورة"] == inv_no, "الإجمالي"].sum())
            if exist + tot > limit + 0.004:
                raise AccountingError(f"تجاوز حد الائتمان للعميل: الرصيد بعد الفاتورة {exist + tot:,.2f} > الحد {limit:,.2f}.")

    def qty_avail(code):
        return stock_state(code, date)[0]
    if kind == "sales":
        jl.append(dict(code=AR_CODE, debit=tot, party=party_code))
        rev = {}
        for r in rows:
            rev[r["acct"]] = rev.get(r["acct"], 0) + r["amt_c"]
        for a, v in rev.items():
            jl.append(dict(code=a, credit=fromc(v)))
        if vat_c:
            jl.append(dict(code=VAT_OUT, credit=fromc(vat_c)))
        cogs_c = 0
        for r in rows:
            if r["stock"]:
                need[r["item"]] = need.get(r["item"], 0) + r["qty"]
        for it_code, q in need.items():
            if qty_avail(it_code) + 1e-9 < q and not st.session_state.settings.get("السماح بمخزون سالب", False):
                raise AccountingError(f"الكمية المتاحة من {it_code} ({qty_avail(it_code):g}) أقل من المطلوب ({q:g}).")
        for r in rows:
            if r["stock"]:
                avg = stock_state(r["item"], date)[2]
                cogs_c += cents(r["qty"] * avg)
                moves.append((r["item"], -r["qty"], avg, r["desc"]))
        if cogs_c:
            jl += [dict(code=COGS_ACC, debit=fromc(cogs_c)), dict(code=INV_ACC, credit=fromc(cogs_c))]
    elif kind == "sales_return":
        jl.append(dict(code=AR_CODE, credit=tot, party=party_code))
        jl.append(dict(code=SALES_RET, debit=fromc(net_c)))
        if vat_c:
            jl.append(dict(code=VAT_OUT, debit=fromc(vat_c)))
        cogs_c = 0
        for r in rows:
            if r["stock"]:
                avg = stock_state(r["item"], date)[2]
                cogs_c += cents(r["qty"] * avg)
                moves.append((r["item"], r["qty"], avg, r["desc"]))
        if cogs_c:
            jl += [dict(code=INV_ACC, debit=fromc(cogs_c)), dict(code=COGS_ACC, credit=fromc(cogs_c))]
    elif kind == "purchase":
        jl.append(dict(code=AP_CODE, credit=tot, party=party_code))
        exp = {}
        for r in rows:
            a = INV_ACC if r["stock"] else r["acct"]
            exp[a] = exp.get(a, 0) + r["amt_c"]
            if r["stock"]:
                moves.append((r["item"], r["qty"], r["amt_c"] / 100.0 / r["qty"], r["desc"]))
        for a, v in exp.items():
            jl.append(dict(code=a, debit=fromc(v)))
        if vat_c:
            jl.append(dict(code=VAT_IN, debit=fromc(vat_c)))
    else:  # purchase_return
        jl.append(dict(code=AP_CODE, debit=tot, party=party_code))
        stock_amt_c = stock_val_c = 0
        oth = {}
        for r in rows:
            if r["stock"]:
                need[r["item"]] = need.get(r["item"], 0) + r["qty"]
            else:
                oth[r["acct"]] = oth.get(r["acct"], 0) + r["amt_c"]
        for it_code, q in need.items():
            if qty_avail(it_code) + 1e-9 < q and not st.session_state.settings.get("السماح بمخزون سالب", False):
                raise AccountingError(f"الكمية المتاحة من {it_code} ({qty_avail(it_code):g}) أقل من كمية المرتجع ({q:g}).")
        for r in rows:
            if r["stock"]:
                avg = stock_state(r["item"], date)[2]
                stock_amt_c += r["amt_c"]
                stock_val_c += cents(r["qty"] * avg)
                moves.append((r["item"], -r["qty"], avg, r["desc"]))
        if stock_val_c:
            jl.append(dict(code=INV_ACC, credit=fromc(stock_val_c)))
        for a, v in oth.items():
            jl.append(dict(code=a, credit=fromc(v)))
        if vat_c:
            jl.append(dict(code=VAT_IN, credit=fromc(vat_c)))
        diff = stock_amt_c - stock_val_c
        if diff > 0:
            jl.append(dict(code=COGS_ACC, credit=fromc(diff)))
        elif diff < 0:
            jl.append(dict(code=COGS_ACC, debit=fromc(-diff)))
    no = inv_no or next_no(K["prefix"])
    post_entry(date, jl, K["label"], K["label"], entry_no=no, note=notes or K["label"])
    for it_code, q, cost, desc in moves:
        add_move(date, no, K["label"], it_code, q, cost, desc)
    append_rows("invoices", [{"رقم الفاتورة": no, "النوع": K["label"], "التاريخ": str(date), "كود الطرف": party_code, "اسم الطرف": str(P[PK[pk]["name"]]), "الصافي": fromc(net_c), "الضريبة": fromc(vat_c),
                              "الإجمالي": tot, "البنود": json.dumps([{k: v for k, v in r.items() if k in ("item", "desc", "qty", "price", "acct")} for r in rows], ensure_ascii=False),
                              "ملاحظات": notes, "المستخدم": cur_user()}])
    log_action(f"ترحيل {K['label']}", f"{no} - {P[PK[pk]['name']]} - {tot:,.2f}")
    return no


def replace_invoice(inv_no, kind, date, party_code, lines, vat_rate, notes, allow_over_credit=False):
    delete_entries([inv_no])
    return post_invoice(kind, date, party_code, lines, vat_rate, notes, inv_no=inv_no, allow_over_credit=allow_over_credit)


# ---------------- السندات النقدية ----------------
VOUCHERS = {"قبض من عميل": dict(prefix="RC", party="customer", dir="in"), "دفع لمورد": dict(prefix="PY", party="supplier", dir="out"),
            "رد مبلغ لعميل": dict(prefix="PY", party="customer", dir="out"), "استرداد من مورد": dict(prefix="RC", party="supplier", dir="in"),
            "مصروف": dict(prefix="EX", party=None, dir="out"), "إيراد آخر": dict(prefix="IN", party=None, dir="in")}


def post_voucher(vtype, date, treasury_code, amount, party="", acct=0, vat_rate=0.0, note=""):
    V = VOUCHERS[vtype]
    date = to_date(date)
    total_c = cents(amount)
    if total_c <= 0:
        raise AccountingError("المبلغ يجب أن يكون أكبر من صفر.")
    if int(treasury_code) not in treasury_codes():
        raise AccountingError("حساب الخزينة/البنك غير صالح أو موقوف.")
    tr = int(treasury_code)
    if V["dir"] == "out":
        check_cash(tr, total_c, date)
    amt = fromc(total_c)
    if V["party"]:
        p = party_row(V["party"], party)
        if p is None:
            raise AccountingError("يجب اختيار الطرف.")
        ctrl = PK[V["party"]]["control"]
        lines = [dict(code=tr, debit=amt), dict(code=ctrl, credit=amt, party=party)] if V["dir"] == "in" else [dict(code=ctrl, debit=amt, party=party), dict(code=tr, credit=amt)]
    else:
        a = acct_row(acct)
        if a is None or a["التصنيف"] != "تفصيلي":
            raise AccountingError("اختر حساب المصروف/الإيراد.")
        if vtype == "مصروف":
            if a["النوع"] != "مصروف":
                raise AccountingError("الحساب المختار ليس حساب مصروف.")
            vat_c = int(round(total_c * vat_rate / (100.0 + vat_rate))) if vat_rate else 0
            lines = [dict(code=acct, debit=fromc(total_c - vat_c)), dict(code=tr, credit=amt)]
            if vat_c:
                lines.append(dict(code=VAT_IN, debit=fromc(vat_c)))
        else:
            if a["النوع"] != "إيراد":
                raise AccountingError("الحساب المختار ليس حساب إيراد.")
            lines = [dict(code=tr, debit=amt), dict(code=acct, credit=amt)]
    no = post_entry(date, lines, vtype, "سند نقدي", prefix=V["prefix"], note=note or vtype)
    log_action(f"سند {vtype}", f"{no} - {amt:,.2f}")
    return no


def post_transfer(date, from_code, to_code, amount, note=""):
    if int(from_code) == int(to_code):
        raise AccountingError("لا يمكن التحويل إلى نفس الحساب.")
    total_c = cents(amount)
    if total_c <= 0:
        raise AccountingError("المبلغ يجب أن يكون أكبر من صفر.")
    check_cash(from_code, total_c, date)
    no = post_entry(date, [dict(code=int(to_code), debit=fromc(total_c)), dict(code=int(from_code), credit=fromc(total_c))], "تحويل بين حسابات", "تحويل", prefix="TR", note=note or "تحويل بين حسابات")
    log_action("تحويل", f"{no} - {fromc(total_c):,.2f}")
    return no


# ---------------- العهد ----------------
def custody_balance(code):
    j = st.session_state.journal
    m = (j["كود الحساب"] == CUSTODY_ACC) & (j["المرجع"] == code)
    return fromc(cents(j.loc[m, "مدين"].sum()) - cents(j.loc[m, "دائن"].sum()))


def issue_custody(employee, date, amount, treasury_code, purpose=""):
    if not employee.strip():
        raise AccountingError("اسم الموظف مطلوب.")
    total_c = cents(amount)
    if total_c <= 0:
        raise AccountingError("مبلغ العهدة يجب أن يكون أكبر من صفر.")
    if int(treasury_code) not in treasury_codes():
        raise AccountingError("حساب الصرف غير صالح.")
    check_cash(treasury_code, total_c, date)
    t = st.session_state.custody
    nums = [int(m.group(1)) for x in t["كود العهدة"] if (m := re.match(r"^CU(\d+)$", str(x)))]
    code = f"CU{(max(nums) + 1 if nums else 1):04d}"
    no = post_entry(date, [dict(code=CUSTODY_ACC, debit=fromc(total_c), ref=code), dict(code=int(treasury_code), credit=fromc(total_c))], "صرف عهدة", "عهدة", prefix="CU", note=f"عهدة {employee} - {purpose}")
    append_rows("custody", [{"كود العهدة": code, "الموظف": employee.strip(), "تاريخ الصرف": str(to_date(date)), "مبلغ العهدة": fromc(total_c), "الغرض": purpose, "رقم قيد الصرف": no}])
    log_action("صرف عهدة", f"{code} {employee} {fromc(total_c):,.2f}")
    return code


def settle_custody(code, date, expenses, refund=0.0, refund_treasury=None, note=""):
    """expenses: [(acct, amount, note)] ; refund: مبلغ نقدي يعاد للخزينة."""
    row = st.session_state.custody[st.session_state.custody["كود العهدة"] == code]
    if row.empty:
        raise AccountingError("العهدة غير موجودة.")
    bal_c = cents(custody_balance(code))
    lines, tot = [], 0
    for a, amt, n in expenses:
        if not amt or cents(amt) == 0:
            continue
        ar_ = acct_row(a)
        if ar_ is None or ar_["النوع"] != "مصروف":
            raise AccountingError("بنود التسوية يجب أن تكون على حسابات مصروفات.")
        lines.append(dict(code=int(a), debit=fromc(cents(amt)), note=n or note))
        tot += cents(amt)
    if cents(refund) > 0:
        if not refund_treasury or int(refund_treasury) not in treasury_codes():
            raise AccountingError("اختر حساب الخزينة لاستلام المبلغ المردود.")
        lines.append(dict(code=int(refund_treasury), debit=fromc(cents(refund)), note="رد رصيد عهدة"))
        tot += cents(refund)
    if tot <= 0:
        raise AccountingError("أدخل مصروفات أو مبلغًا مردودًا.")
    if tot > bal_c:
        raise AccountingError(f"إجمالي التسوية {fromc(tot):,.2f} يتجاوز رصيد العهدة {fromc(bal_c):,.2f}.")
    lines.append(dict(code=CUSTODY_ACC, credit=fromc(tot), ref=code))
    no = post_entry(date, lines, "تسوية عهدة", "عهدة", prefix="CS", note=note or f"تسوية عهدة {code}")
    log_action("تسوية عهدة", f"{code} {fromc(tot):,.2f}")
    return no


def delete_custody(code):
    s = st.session_state
    row = s.custody[s.custody["كود العهدة"] == code]
    if row.empty:
        raise AccountingError("العهدة غير موجودة.")
    j = s.journal
    others = j[(j["المرجع"] == code) & (j["رقم القيد"] != row.iloc[0]["رقم قيد الصرف"])]
    if not others.empty:
        raise AccountingError("عليها تسويات مسجلة؛ احذف قيود التسوية أولًا من القيود اليومية.")
    check_lock(row.iloc[0]["تاريخ الصرف"])
    s.journal = j[j["رقم القيد"] != row.iloc[0]["رقم قيد الصرف"]].reset_index(drop=True)
    s.custody = s.custody[s.custody["كود العهدة"] != code].reset_index(drop=True)
    log_action("حذف عهدة", code)


# ---------------- الأصول الثابتة ----------------
def dep_months(asset, upto):
    start, upto = to_date(asset["تاريخ الشراء"]), to_date(upto)
    return 0 if upto < start else (upto.year - start.year) * 12 + upto.month - start.month + 1


def dep_should(asset, upto):
    life, cost, salv = float(asset["العمر (سنوات)"]), float(asset["التكلفة"]), float(asset["القيمة التخريدية"])
    if life <= 0:
        return 0.0
    base = max(cost - salv, 0.0)
    total_m = int(round(life * 12))
    m = min(dep_months(asset, upto), total_m)
    return round(base, 2) if m >= total_m else round(base * m / total_m, 2)


def dep_posted(code):
    d = st.session_state.depreciation_log
    return fromc(cents(d.loc[d["كود الأصل"] == code, "مبلغ الإهلاك"].sum()))


def register_asset(data, method, treasury_code=None, supplier=None, vat_rate=0.0):
    s = st.session_state
    code = str(data.get("كود الأصل", "")).strip()
    name = str(data.get("اسم الأصل", "")).strip()
    if not code or not name:
        raise AccountingError("كود الأصل واسمه مطلوبان.")
    if (s.fixed_assets["كود الأصل"] == code).any():
        raise AccountingError(f"كود الأصل {code} مستخدم بالفعل.")
    cost, salv, life = float(data["التكلفة"]), float(data.get("القيمة التخريدية", 0) or 0), float(data["العمر (سنوات)"])
    if cost <= 0 or life <= 0:
        raise AccountingError("التكلفة والعمر الإنتاجي يجب أن يكونا أكبر من صفر.")
    if salv < 0 or salv >= cost:
        raise AccountingError("القيمة التخريدية يجب أن تكون أقل من التكلفة وغير سالبة.")
    acct = int(data.get("كود حساب الأصل") or ASSET_CLASSES.get(data.get("التصنيف"), 1410))
    accum = int(data.get("كود مجمع الإهلاك") or ACCUM_DEP)
    exp = int(data.get("كود مصروف الإهلاك") or DEP_EXP)
    for c_, t_ in ((acct, "أصل"), (accum, "أصل"), (exp, "مصروف")):
        a = acct_row(c_)
        if a is None or a["النوع"] != t_ or a["التصنيف"] != "تفصيلي":
            raise AccountingError(f"الحساب {c_} غير صالح لهذا الغرض.")
    d = to_date(data["تاريخ الشراء"])
    cost_c = cents(cost)
    vat_c = int(round(cost_c * vat_rate / 100.0)) if method != "رصيد افتتاحي" else 0
    tot_c = cost_c + vat_c
    lines = [dict(code=acct, debit=fromc(cost_c), ref=code)]
    if vat_c:
        lines.append(dict(code=VAT_IN, debit=fromc(vat_c), ref=code))
    if method == "نقدًا / بنك":
        if not treasury_code or int(treasury_code) not in treasury_codes():
            raise AccountingError("اختر حساب الخزينة/البنك.")
        check_cash(treasury_code, tot_c, d)
        lines.append(dict(code=int(treasury_code), credit=fromc(tot_c), ref=code))
    elif method == "آجل من مورد":
        if party_row("supplier", supplier) is None:
            raise AccountingError("اختر المورد.")
        lines.append(dict(code=AP_CODE, credit=fromc(tot_c), party=supplier, ref=code))
    else:
        lines.append(dict(code=OPEN_EQ, credit=fromc(tot_c), ref=code))
    no = post_entry(d, lines, "اقتناء أصل ثابت", "أصول ثابتة", prefix="FA", note=f"اقتناء أصل {code} - {name}")
    row = {c_: data.get(c_, "") for c_ in ASSET_COLS}
    row.update({"كود الأصل": code, "اسم الأصل": name, "كود حساب الأصل": acct, "كود مجمع الإهلاك": accum, "كود مصروف الإهلاك": exp, "رقم قيد الاقتناء": no, "الحالة": "نشط",
                "تاريخ الشراء": str(d), "التكلفة": cost, "القيمة التخريدية": salv, "العمر (سنوات)": life})
    append_rows("fixed_assets", [row])
    log_action("تسجيل أصل ثابت", f"{code} {name} {cost:,.2f}")
    return no


def run_depreciation(upto, only=None):
    s = st.session_state
    lines, logs = [], []
    for _, a in s.fixed_assets.iterrows():
        if a["الحالة"] != "نشط" or (only and a["كود الأصل"] != only):
            continue
        amt = fromc(cents(dep_should(a, upto)) - cents(dep_posted(a["كود الأصل"])))
        if amt <= 0.004:
            continue
        lines += [dict(code=int(a["كود مصروف الإهلاك"]), debit=amt, ref=a["كود الأصل"], note=f"إهلاك {a['اسم الأصل']}"), dict(code=int(a["كود مجمع الإهلاك"]), credit=amt, ref=a["كود الأصل"], note=f"إهلاك {a['اسم الأصل']}")]
        logs.append((a["كود الأصل"], a["اسم الأصل"], amt))
    if not lines:
        return None
    no = post_entry(upto, lines, "قيد إهلاك", "إهلاك", prefix="DEP", note=f"إهلاك الأصول الثابتة حتى {to_date(upto)}")
    append_rows("depreciation_log", [{"التاريخ": str(to_date(upto)), "رقم القيد": no, "كود الأصل": c_, "اسم الأصل": n, "مبلغ الإهلاك": v} for c_, n, v in logs])
    log_action("احتساب إهلاك", f"{no} حتى {to_date(upto)}")
    return no


def dispose_asset(code, date, proceeds, treasury_code=None, note=""):
    s = st.session_state
    r = s.fixed_assets[s.fixed_assets["كود الأصل"] == code]
    if r.empty:
        raise AccountingError("الأصل غير موجود.")
    a = r.iloc[0]
    if a["الحالة"] != "نشط":
        raise AccountingError("الأصل مستبعد بالفعل.")
    date = to_date(date)
    if date < to_date(a["تاريخ الشراء"]):
        raise AccountingError("تاريخ الاستبعاد قبل تاريخ الشراء.")
    run_depreciation(date, only=code)
    accum_c = cents(dep_posted(code))
    cost_c = cents(a["التكلفة"])
    nbv_c = cost_c - accum_c
    pro_c = cents(proceeds)
    if pro_c < 0:
        raise AccountingError("قيمة البيع لا يمكن أن تكون سالبة.")
    lines = []
    if pro_c > 0:
        if not treasury_code or int(treasury_code) not in treasury_codes():
            raise AccountingError("اختر حساب الخزينة/البنك لاستلام قيمة البيع.")
        lines.append(dict(code=int(treasury_code), debit=fromc(pro_c), ref=code))
    if accum_c > 0:
        lines.append(dict(code=int(a["كود مجمع الإهلاك"]), debit=fromc(accum_c), ref=code))
    if pro_c < nbv_c:
        lines.append(dict(code=ASSET_LOSS, debit=fromc(nbv_c - pro_c), ref=code))
    lines.append(dict(code=int(a["كود حساب الأصل"]), credit=fromc(cost_c), ref=code))
    if pro_c > nbv_c:
        lines.append(dict(code=ASSET_GAIN, credit=fromc(pro_c - nbv_c), ref=code))
    no = post_entry(date, lines, "استبعاد / بيع أصل ثابت", "أصول ثابتة", prefix="FD", note=note or f"استبعاد الأصل {code} - {a['اسم الأصل']}")
    s.fixed_assets.loc[s.fixed_assets["كود الأصل"] == code, ["الحالة", "تاريخ الاستبعاد", "رقم قيد الاستبعاد"]] = ["مستبعد", str(date), no]
    log_action("استبعاد أصل", f"{code} بقيمة {fromc(pro_c):,.2f}")
    return no


def delete_asset(code):
    s = st.session_state
    r = s.fixed_assets[s.fixed_assets["كود الأصل"] == code]
    if r.empty:
        raise AccountingError("الأصل غير موجود.")
    a = r.iloc[0]
    if a["الحالة"] != "نشط":
        raise AccountingError("الأصل مستبعد؛ احذف قيد الاستبعاد أولًا.")
    if (s.depreciation_log["كود الأصل"] == code).any():
        raise AccountingError("عليه قيود إهلاك؛ احذف قيود الإهلاك أولًا.")
    check_lock(a["تاريخ الشراء"])
    s.journal = s.journal[s.journal["رقم القيد"] != a["رقم قيد الاقتناء"]].reset_index(drop=True)
    s.fixed_assets = s.fixed_assets[s.fixed_assets["كود الأصل"] != code].reset_index(drop=True)
    log_action("حذف أصل", code)


def assets_report(asof):
    rows = []
    for _, a in st.session_state.fixed_assets.iterrows():
        if to_date(a["تاريخ الشراء"]) > to_date(asof):
            continue
        disposed = a["الحالة"] == "مستبعد" and a["تاريخ الاستبعاد"] and to_date(a["تاريخ الاستبعاد"]) <= to_date(asof)
        d = st.session_state.depreciation_log
        acc = d[(d["كود الأصل"] == a["كود الأصل"]) & (pd.to_datetime(d["التاريخ"]) <= ts(asof))]["مبلغ الإهلاك"].sum()
        cost = float(a["التكلفة"])
        rows.append({"كود الأصل": a["كود الأصل"], "الأصل": a["اسم الأصل"], "التصنيف": a["التصنيف"], "تاريخ الشراء": a["تاريخ الشراء"], "التكلفة": cost,
                     "مجمع الإهلاك": 0.0 if disposed else round(acc, 2), "صافي القيمة الدفترية": 0.0 if disposed else round(cost - acc, 2), "الإهلاك السنوي": round((cost - float(a["القيمة التخريدية"])) / float(a["العمر (سنوات)"]), 2) if float(a["العمر (سنوات)"]) else 0,
                     "الحالة": "مستبعد" if disposed else "نشط"})
    return pd.DataFrame(rows, columns=["كود الأصل", "الأصل", "التصنيف", "تاريخ الشراء", "التكلفة", "مجمع الإهلاك", "صافي القيمة الدفترية", "الإهلاك السنوي", "الحالة"])


# ============================================================
# القوائم المالية
# ============================================================
def trial_balance(frm, to):
    j = jdf()
    before = j[j["_d"] < ts(frm)].groupby("كود الحساب")[["مدين", "دائن"]].sum()
    within = j[(j["_d"] >= ts(frm)) & (j["_d"] <= ts(to))].groupby("كود الحساب")[["مدين", "دائن"]].sum()
    rows = []
    for _, a in postable().sort_values("الكود").iterrows():
        k = int(a["الكود"])
        bd, bc = (before.loc[k, "مدين"], before.loc[k, "دائن"]) if k in before.index else (0.0, 0.0)
        md, mc = (within.loc[k, "مدين"], within.loc[k, "دائن"]) if k in within.index else (0.0, 0.0)
        ob, cl = bd - bc, bd - bc + md - mc
        if abs(bd) + abs(bc) + abs(md) + abs(mc) < 0.004:
            continue
        rows.append({"الكود": k, "الحساب": a["اسم الحساب"], "افتتاحي مدين": max(ob, 0), "افتتاحي دائن": max(-ob, 0), "حركة مدين": md, "حركة دائن": mc, "ختامي مدين": max(cl, 0), "ختامي دائن": max(-cl, 0)})
    df = pd.DataFrame(rows, columns=["الكود", "الحساب", "افتتاحي مدين", "افتتاحي دائن", "حركة مدين", "حركة دائن", "ختامي مدين", "ختامي دائن"])
    num = [c for c in df.columns if c not in ("الكود", "الحساب")]
    df[num] = df[num].round(2)
    return df


def _lines_for(net, lo, hi, sign, skip=()):
    out = []
    for _, a in postable().sort_values("الكود").iterrows():
        k = int(a["الكود"])
        if lo <= k <= hi and k not in skip:
            v = sign * net.get(k, 0.0)
            if abs(v) > 0.004:
                out.append((("(-) " if v < 0 and k == ACCUM_DEP else "") + f"{a['اسم الحساب']}", round(v, 2)))
    return out


def income_statement(frm, to):
    net = net_by_account(frm, to)
    rows = []
    rev_lines = _lines_for(net, 4100, 4199, -1)
    rows.append(("h", "الإيرادات", None))
    for l, v in rev_lines:
        rows.append(("i", l, v))
    net_sales = sum(v for _, v in rev_lines)
    rows.append(("s", "صافي المبيعات", net_sales))
    cogs = _lines_for(net, 5100, 5199, 1)
    rows.append(("h", "تكلفة المبيعات والمشتريات المباشرة", None))
    for l, v in cogs:
        rows.append(("i", l, v))
    tot_cogs = sum(v for _, v in cogs)
    rows.append(("s", "إجمالي تكلفة المبيعات", tot_cogs))
    gross = net_sales - tot_cogs
    rows.append(("t", "مجمل الربح", gross))
    opex = _lines_for(net, 5200, 5299, 1, skip=(DEP_EXP, ASSET_LOSS))
    rows.append(("h", "المصروفات التشغيلية", None))
    for l, v in opex:
        rows.append(("i", l, v))
    dep = round(net.get(DEP_EXP, 0.0), 2)
    if abs(dep) > 0.004:
        rows.append(("i", acct_name(DEP_EXP), dep))
    tot_opex = sum(v for _, v in opex) + dep
    rows.append(("s", "إجمالي المصروفات التشغيلية", tot_opex))
    other_inc = _lines_for(net, 4200, 4299, -1)
    other_exp = _lines_for(net, 5300, 5399, 1) + ([(acct_name(ASSET_LOSS), round(net.get(ASSET_LOSS, 0.0), 2)) ] if abs(net.get(ASSET_LOSS, 0.0)) > 0.004 else [])
    rows.append(("h", "إيرادات ومصروفات أخرى", None))
    for l, v in other_inc:
        rows.append(("i", l, v))
    for l, v in other_exp:
        rows.append(("i", l + " (مصروف)", -v))
    other_net = sum(v for _, v in other_inc) - sum(v for _, v in other_exp)
    rows.append(("s", "صافي الإيرادات (المصروفات) الأخرى", other_net))
    profit = gross - tot_opex + other_net
    rows.append(("t", "صافي الربح / (الخسارة) للفترة", profit))
    return rows, round(profit, 2)


def balance_sheet(asof):
    asof = to_date(asof)
    net = net_by_account(None, asof)
    fs = fiscal_start(asof)
    prior_net = net_by_account(None, fs - dt.timedelta(days=1))
    ni_prior = -code_sum(prior_net, 4000, 5999)
    ni_curr = -code_sum(net, 4000, 5999) - ni_prior
    rows = []
    rows.append(("h", "الأصول المتداولة", None))
    ca = _lines_for(net, 1100, 1399, 1)
    [rows.append(("i", l, v)) for l, v in ca]
    tca = sum(v for _, v in ca)
    rows.append(("s", "إجمالي الأصول المتداولة", tca))
    rows.append(("h", "الأصول غير المتداولة", None))
    nca = _lines_for(net, 1400, 1999, 1)
    [rows.append(("i", l, v)) for l, v in nca]
    tnca = sum(v for _, v in nca)
    rows.append(("s", "إجمالي الأصول غير المتداولة (بالصافي)", tnca))
    ta = tca + tnca
    rows.append(("t", "إجمالي الأصول", ta))
    rows.append(("h", "الالتزامات المتداولة", None))
    cl = _lines_for(net, 2000, 2499, -1)
    [rows.append(("i", l, v)) for l, v in cl]
    tcl = sum(v for _, v in cl)
    rows.append(("s", "إجمالي الالتزامات المتداولة", tcl))
    ltl = _lines_for(net, 2500, 2999, -1)
    if ltl:
        rows.append(("h", "الالتزامات طويلة الأجل", None))
        [rows.append(("i", l, v)) for l, v in ltl]
    tl = tcl + sum(v for _, v in ltl)
    rows.append(("t", "إجمالي الالتزامات", tl))
    rows.append(("h", "حقوق الملكية", None))
    eq = _lines_for(net, 3000, 3999, -1)
    [rows.append(("i", l, v)) for l, v in eq]
    if abs(ni_prior) > 0.004:
        rows.append(("i", "أرباح (خسائر) السنوات السابقة", round(ni_prior, 2)))
    rows.append(("i", "صافي ربح (خسارة) السنة المالية الحالية", round(ni_curr, 2)))
    te = sum(v for _, v in eq) + ni_prior + ni_curr
    rows.append(("s", "إجمالي حقوق الملكية", te))
    rows.append(("t", "إجمالي الالتزامات وحقوق الملكية", tl + te))
    diff = round(ta - (tl + te), 2)
    return rows, diff, round(ta, 2)


def vat_summary(frm, to):
    net = net_by_account(frm, to)
    out_v, in_v = round(-net.get(VAT_OUT, 0.0), 2), round(net.get(VAT_IN, 0.0), 2)
    return pd.DataFrame([{"البند": "ضريبة المخرجات (مبيعات)", "المبلغ": out_v}, {"البند": "ضريبة المدخلات (مشتريات ومصروفات)", "المبلغ": in_v},
                         {"البند": "صافي الضريبة المستحقة / (القابلة للاسترداد)", "المبلغ": round(out_v - in_v, 2)}])


def stmt_df(rows):
    return pd.DataFrame([{"البند": l, "المبلغ": ("" if v is None else round(v, 2)), "_k": k} for k, l, v in rows])


def stmt_html(rows, title, subtitle=""):
    tr = ""
    for k, l, v in rows:
        e = html.escape(str(l))
        if k == "h":
            tr += f'<tr class="h"><td colspan="2">{e}</td></tr>'
        else:
            cls = {"i": "", "s": "s", "t": "t"}[k]
            tr += f'<tr class="{cls}"><td class="{"i" if k == "i" else ""}">{e}</td><td class="n">{fmt(v)}</td></tr>'
    return f'<div class="stmt"><div class="stmt-t">{html.escape(title)}</div><div class="stmt-s">{html.escape(subtitle)}</div><table>{tr}</table></div>'


# ============================================================
# التصدير (Excel / PDF / CSV)
# ============================================================
def excel_bytes(sheets):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine=XL_ENGINE) as w:
        for name, d in sheets.items():
            nm = re.sub(r"[\[\]\*\?/\\:]", "-", name)[:31]
            d = d.drop(columns=[c for c in d.columns if c.startswith("_")], errors="ignore")
            d.to_excel(w, sheet_name=nm, index=False)
            if XL_ENGINE == "xlsxwriter":
                ws = w.sheets[nm]
                ws.right_to_left()
                hf = w.book.add_format({"bold": True, "bg_color": "#0F172A", "font_color": "#FFFFFF", "border": 1, "align": "center"})
                for i, col in enumerate(d.columns):
                    ws.write(0, i, col, hf)
                    ln = int(d[col].astype(str).str.len().max()) if len(d) else 0
                    ws.set_column(i, i, min(45, max(12, ln + 2, len(str(col)) + 4)))
    return buf.getvalue()


def _ar(t):
    return get_display(arabic_reshaper.reshape(str(t)))


def pdf_bytes(title, df, subtitle=""):
    reg, bold = os.path.join(FONT_DIR, "Amiri-Regular.ttf"), os.path.join(FONT_DIR, "Amiri-Bold.ttf")
    if not (PDF_OK and os.path.exists(reg)):
        return None
    kcol = df["_k"].tolist() if "_k" in df.columns else None
    d = df.drop(columns=[c for c in df.columns if c.startswith("_")], errors="ignore").copy()
    cols = list(d.columns)[::-1]

    class RPDF(FPDF):
        def footer(self):
            self.set_y(-12)
            self.set_font("Amiri", "", 8)
            self.cell(0, 8, f"{self.page_no()}/{{nb}}", align="C")

    pdf = RPDF(orientation="L" if len(cols) > 5 else "P", unit="mm", format="A4")
    pdf.add_font("Amiri", "", reg)
    pdf.add_font("Amiri", "B", bold if os.path.exists(bold) else reg)
    pdf.alias_nb_pages()
    pdf.set_margins(10, 12, 10)
    pdf.set_auto_page_break(True, 16)
    pdf.add_page()
    pdf.set_font("Amiri", "B", 15)
    pdf.cell(0, 9, _ar(st.session_state.settings.get("اسم الشركة", "")), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Amiri", "B", 12)
    pdf.cell(0, 8, _ar(title), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Amiri", "", 9)
    pdf.cell(0, 6, _ar(f"{subtitle}   |   تاريخ الطباعة: {today()}"), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    weights = []
    for c in cols:
        ml = max([len(str(c))] + [len(str(x)) for x in d[c].head(200)])
        weights.append(min(max(ml, 7), 34))
    W = [pdf.epw * w / sum(weights) for w in weights]

    def head():
        pdf.set_font("Amiri", "B", 9)
        pdf.set_fill_color(15, 23, 42)
        pdf.set_text_color(255, 255, 255)
        for c, w in zip(cols, W):
            pdf.cell(w, 8, _ar(c), border=1, align="C", fill=True)
        pdf.ln()
        pdf.set_text_color(0, 0, 0)

    head()
    for idx in range(len(d)):
        if pdf.get_y() > pdf.h - 24:
            pdf.add_page()
            head()
        k = kcol[idx] if kcol else ""
        pdf.set_font("Amiri", "B" if k in ("h", "s", "t") else "", 9)
        pdf.set_fill_color(*((219, 234, 254) if k == "t" else (241, 245, 249) if k in ("h", "s") else (255, 255, 255)))
        for c, w in zip(cols, W):
            v = d.iloc[idx][c]
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                txt = f"{v:,.2f}" if (c not in ("الكود",) and not str(c).startswith("كود")) else f"{v:g}"
            else:
                mx = max(int(w / 1.55), 4)
                txt = _ar(str(v)[:mx]) if str(v) else ""
            pdf.cell(w, 7, txt, border=1, align="C", fill=True)
        pdf.ln()
    return bytes(pdf.output())


def download_bar(df, title, base, subtitle="", key="dl", extra_sheets=None):
    """أزرار تنزيل Excel / PDF / CSV."""
    c1, c2, c3 = st.columns(3)
    sheets = {title: df, **(extra_sheets or {})}
    c1.download_button("⬇️ Excel", excel_bytes(sheets), f"{base}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True, key=f"{key}_x")
    p = pdf_bytes(title, df, subtitle) if PDF_OK else None
    if p:
        c2.download_button("⬇️ PDF", p, f"{base}.pdf", "application/pdf", use_container_width=True, key=f"{key}_p")
    else:
        c2.button("PDF غير متاح (ثبّت fpdf2 وضع مجلد fonts)", disabled=True, use_container_width=True, key=f"{key}_pn")
    c3.download_button("⬇️ CSV", df.drop(columns=[c for c in df.columns if c.startswith("_")], errors="ignore").to_csv(index=False).encode("utf-8-sig"), f"{base}.csv", "text/csv", use_container_width=True, key=f"{key}_c")


# ============================================================
# التهيئة، الترحيل من النسخ القديمة، والبيانات التجريبية
# ============================================================
def default_settings():
    return {"اسم الشركة": "Ecovair للتكييف والتوريدات", "الرقم الضريبي": "300-123-456", "العملة": "جنيه مصري (EGP)", "بداية السنة المالية": "01-01", "الرمز": "❄️",
            "نسبة الضريبة الافتراضية": 14.0, "السماح بمخزون سالب": False, "السماح برصيد نقدية سالب": False, "تاريخ الإقفال": "", "_schema": 0}


def init_state():
    s = st.session_state
    for k, cols in SCHEMAS.items():
        s[k] = ensure_schema(s.get(k), cols)
    ensure_chart()
    st_ = default_settings()
    st_.update(s.get("settings") or {})
    s.settings = st_
    rp = s.get("role_permissions")
    if not isinstance(rp, pd.DataFrame) or "الدور" not in rp.columns:
        s.role_permissions = default_role_perms()
    else:
        for m in MODULES.values():
            if m not in rp.columns:
                rp[m] = "لا وصول"
        s.role_permissions = rp
    if s.users.empty or (s.users["كلمة المرور"] == "").all():
        s.users = default_users()


def migrate_legacy(old):
    """تحويل بيانات النسخ القديمة (قيد بمدين/دائن في سطر واحد) إلى النظام الجديد."""
    s = st.session_state
    if not (isinstance(old, pd.DataFrame) and "كود المدين" in old.columns):
        return False
    # أطراف افتراضية للسطور القديمة التي لا تحمل طرفًا
    if s.customers.empty:
        s.customers = ensure_schema(pd.DataFrame([{"كود العميل": "C0001", "اسم العميل": "عميل (ترحيل من النسخة القديمة)", "الحالة": "نشط"}]), CUSTOMER_COLS)
    if s.suppliers.empty:
        s.suppliers = ensure_schema(pd.DataFrame([{"كود المورد": "S0001", "اسم المورد": "مورد (ترحيل من النسخة القديمة)", "الحالة": "نشط"}]), SUPPLIER_COLS)
    for kind in PK:
        t = ptable(kind)
        p = PK[kind]
        for i in t.index[t[p["code"]] == ""]:
            t.at[i, p["code"]] = next_party_code(kind)
        t["الحالة"] = t["الحالة"].replace("", "نشط")
    c0, s0 = str(s.customers.iloc[0]["كود العميل"]), str(s.suppliers.iloc[0]["كود المورد"])
    rows = []
    for _, r in old.iterrows():
        amt = float(r.get("المبلغ", 0) or 0)
        if amt <= 0:
            continue
        common = dict(التاريخ=str(r["التاريخ"])[:10], رقم_القيد=str(r["رقم القيد"]))
        for side, codecol, namecol in (("d", "كود المدين", "الحساب المدين"), ("c", "كود الدائن", "الحساب الدائن")):
            code = int(r[codecol])
            party = c0 if code == AR_CODE else (s0 if code == AP_CODE else "")
            rows.append({"التاريخ": common["التاريخ"], "رقم القيد": common["رقم_القيد"], "نوع العملية": str(r.get("نوع العملية", "")), "كود الحساب": code, "اسم الحساب": str(r[namecol]),
                         "مدين": amt if side == "d" else 0.0, "دائن": amt if side == "c" else 0.0, "الطرف": party, "المرجع": "", "البيان": str(r.get("الملاحظات", "")), "المصدر": "ترحيل قديم", "المستخدم": "ترحيل"})
    s.journal = ensure_schema(pd.DataFrame(rows), JOURNAL_COLS)
    # الجداول التي تغيّر هيكلها: نبدأ بها من جديد (كانت بيانات إدخال فقط دون قيود)
    s.treasury = ensure_schema(None, TREASURY_COLS)
    s.custody = ensure_schema(None, CUSTODY_COLS)
    s.users = default_users()
    s.role_permissions = default_role_perms()
    s.fixed_assets = ensure_schema(None, ASSET_COLS)
    s.depreciation_log = ensure_schema(None, DEP_COLS)
    return True


def bootstrap_treasury():
    s = st.session_state
    if s.treasury.empty:
        append_rows("treasury", [{"كود الحساب": CASH_CODE, "اسم الحساب": acct_name(CASH_CODE), "النوع": "خزنة نقدية", "رقم الحساب البنكي": "", "الحالة": "نشط"},
                                 {"كود الحساب": BANK_CODE, "اسم الحساب": acct_name(BANK_CODE), "النوع": "بنك", "رقم الحساب البنكي": "", "الحالة": "نشط"}])


def migrate_inventory_legacy(old_inv):
    """أصناف النسخة القديمة (بكمية وسعر) -> أصناف جديدة برصيد افتتاحي مُرحَّل محاسبيًا."""
    for _, r in old_inv.iterrows():
        try:
            add_item({"كود الصنف": r["كود الصنف"], "اسم الصنف": r["اسم الصنف"], "الوحدة": r.get("الوحدة", "قطعة"), "سعر البيع": float(r.get("سعر الوحدة", 0) or 0), "حد إعادة الطلب": float(r.get("حد إعادة الطلب", 0) or 0)},
                     opening_qty=float(r.get("الكمية المتاحة", 0) or 0), opening_cost=float(r.get("سعر الوحدة", 0) or 0))
        except Exception:
            pass


def seed_demo():
    """بيانات تجريبية سليمة محاسبيًا لأول تشغيل (يمكن مسحها من الإعدادات)."""
    fs = fiscal_start(today())
    D = lambda n: fs + dt.timedelta(days=n)
    add_party("customer", {"اسم العميل": "شركة النيل للمقاولات", "الهاتف": "01001234567", "العنوان": "القاهرة - مدينة نصر", "السجل التجاري": "123456", "الرقم الضريبي": "300-111-222", "حد الائتمان": 500000, "مدة السداد (يوم)": 30})
    add_party("supplier", {"اسم المورد": "مصنع الدلتا للتكييفات", "الهاتف": "01112345678", "العنوان": "الإسكندرية - برج العرب", "السجل التجاري": "654321", "الرقم الضريبي": "300-333-444", "نوع التوريد": "معدات تكييف", "مدة السداد (يوم)": 45})
    append_rows("treasury", [])
    bootstrap_treasury()
    post_entry(D(0), [dict(code=BANK_CODE, debit=1000000), dict(code=CAPITAL, credit=1000000)], "قيد افتتاحي", "يدوي", note="إيداع رأس المال")
    add_item({"كود الصنف": "AC-001", "اسم الصنف": "وحدة تكييف اسبليت 1.5 حصان", "الوحدة": "قطعة", "سعر البيع": 9500, "حد إعادة الطلب": 5}, opening_qty=5, opening_cost=7400, open_date=D(0))
    add_item({"كود الصنف": "DC-010", "اسم الصنف": "دكت ألوميتال (متر)", "الوحدة": "متر", "سعر البيع": 220, "حد إعادة الطلب": 30}, opening_qty=0)
    add_item({"كود الصنف": "SRV-01", "اسم الصنف": "خدمة تركيب وتشغيل", "الوحدة": "خدمة", "النوع": "خدمة", "سعر البيع": 1500, "حد إعادة الطلب": 0})
    post_invoice("purchase", D(4), "S0001", [dict(item="AC-001", qty=20, price=7500), dict(item="DC-010", qty=200, price=150)], 14.0, "توريد وحدات تكييف ودكت")
    post_voucher("دفع لمورد", D(20), BANK_CODE, 100000, party="S0001", note="دفعة تحت الحساب")
    post_invoice("sales", D(14), "C0001", [dict(item="AC-001", qty=10, price=9500), dict(item="SRV-01", qty=10, price=1500)], 14.0, "مستخلص توريد وتركيب مشروع تكييف")
    post_voucher("قبض من عميل", D(19), BANK_CODE, 60000, party="C0001", note="تحصيل دفعة")
    post_voucher("مصروف", D(30), BANK_CODE, 60000, acct=5210, note="رواتب مهندسي وفنيي الشركة")
    register_asset({"كود الأصل": "FA-001", "اسم الأصل": "سيارة نقل توريدات", "التصنيف": "سيارات ووسائل نقل", "تاريخ الشراء": str(D(1)), "التكلفة": 350000, "القيمة التخريدية": 50000, "العمر (سنوات)": 5}, "نقدًا / بنك", treasury_code=BANK_CODE)
    prev_m_end = today().replace(day=1) - dt.timedelta(days=1)
    run_depreciation(prev_m_end)


def bootstrap():
    _db_init()
    load_all()
    s = st.session_state
    fresh = (_db_read("journal") is None) and (_db_read("settings") is None)
    legacy_inv = s.get("inventory") if isinstance(s.get("inventory"), pd.DataFrame) and "الكمية المتاحة" in s.get("inventory", pd.DataFrame()).columns else None
    legacy_j = s.get("journal") if isinstance(s.get("journal"), pd.DataFrame) and "كود المدين" in s.get("journal", pd.DataFrame()).columns else None
    init_state()
    if s.settings.get("_schema") != SCHEMA_VER:
        was_legacy = migrate_legacy(legacy_j)
        if was_legacy:
            s.inventory = ensure_schema(None, ITEM_COLS)
            s.stock_moves = ensure_schema(None, STOCK_COLS)
        bootstrap_treasury()
        s.settings["_schema"] = SCHEMA_VER
        try:
            if fresh:
                seed_demo()
            elif was_legacy and legacy_inv is not None:
                migrate_inventory_legacy(legacy_inv)
        except Exception as e:  # لا نوقف التشغيل بسبب البيانات التجريبية
            st.session_state["_seed_error"] = str(e)
        persist()
    bootstrap_treasury()


bootstrap()

# ============================================================
# أدوات الواجهة
# ============================================================
def flash(msg, kind="success"):
    st.session_state["_flash"] = (kind, msg)


def show_flash():
    f = st.session_state.pop("_flash", None)
    if f:
        getattr(st, f[0])(f[1])


def bump(key):
    st.session_state[f"_v_{key}"] = st.session_state.get(f"_v_{key}", 0) + 1


def do(fn, *a, ok=None, **kw):
    """ينفّذ عملية محاسبية داخل معاملة (كاملة أو لا شيء) ويحفظ النتيجة."""
    try:
        with atomic():
            r = fn(*a, **kw)
        persist()
        if ok:
            flash(ok.replace("{}", str(r)))
        return True, r
    except AccountingError as e:
        st.error(f"❌ {e}")
    except Exception as e:  # noqa
        st.error(f"⚠️ خطأ غير متوقع: {e}")
    return False, None


def kpi(col, icon, value, label):
    col.markdown(f'<div class="kpi-card"><span class="kpi-icon">{icon}</span><div class="kpi-value">{value}</div><div class="kpi-label">{label}</div></div>', unsafe_allow_html=True)


def alert(kind, text):
    st.markdown(f'<div class="alert-card alert-{kind}">{text}</div>', unsafe_allow_html=True)


def show_table(df, key, date_col=None, height=None, selectable=True, cfg=None, search=True):
    """جدول بحث + فلتر تاريخ + تحديد متعدد. يرجع (الجدول المعروض، فهارس الصفوف المحددة)."""
    v = st.session_state.get(f"_v_{key}", 0)
    view = df.copy()
    if search or date_col:
        cols = st.columns([3, 1.2, 1.2] if date_col else [3])
        q = cols[0].text_input("🔎 بحث", key=f"q_{key}", placeholder="ابحث بأي جزء من الاسم أو الرقم أو المبلغ أو البيان...", label_visibility="collapsed") if search else ""
        if date_col:
            d1 = cols[1].date_input("من تاريخ", value=None, key=f"d1_{key}")
            d2 = cols[2].date_input("إلى تاريخ", value=None, key=f"d2_{key}")
            dd = pd.to_datetime(view[date_col], errors="coerce")
            if d1:
                view = view[dd >= pd.Timestamp(d1)]
                dd = dd[view.index]
            if d2:
                view = view[dd <= pd.Timestamp(d2)]
        if q:
            mask = view.astype(str).apply(lambda s: s.str.contains(q, case=False, na=False, regex=False)).any(axis=1)
            view = view[mask]
    st.caption(f"عدد السجلات: {len(view)} من {len(df)}")
    kw = dict(use_container_width=True, hide_index=True, column_config=cfg)
    if height:
        kw["height"] = height
    if selectable and len(view):
        ev = st.dataframe(view, on_select="rerun", selection_mode="multi-row", key=f"tbl_{key}_{v}", **kw)
        rows = [i for i in ev.selection.rows if i < len(view)]
        return view, [view.index[i] for i in rows]
    st.dataframe(view, **kw)
    return view, []


def date_range(key, default_from=None, default_to=None, cols=None):
    c = cols or st.columns([1, 1, 3])
    a = c[0].date_input("من", default_from or fiscal_start(today()), key=f"{key}_a")
    b = c[1].date_input("إلى", default_to or today(), key=f"{key}_b")
    return a, b


def natural_sign(code):
    a = acct_row(code)
    if a is None:
        return 1
    s = 1 if a["النوع"] in ("أصل", "مصروف") else -1
    return -s if code in (ACCUM_DEP, SALES_RET) else s


def entry_lines_editor(key, init=None, rows=4):
    opts = account_options()
    popts = party_options("customer", False) + party_options("supplier", False)
    base = init if init is not None else pd.DataFrame({"الحساب": [None] * rows, "مدين": [0.0] * rows, "دائن": [0.0] * rows, "الطرف": [None] * rows, "المرجع": [""] * rows, "بيان السطر": [""] * rows})
    ed = st.data_editor(base, num_rows="dynamic", use_container_width=True, hide_index=True, key=key, column_config={
        "الحساب": st.column_config.SelectboxColumn("الحساب", options=opts, width="large"),
        "مدين": st.column_config.NumberColumn("مدين", min_value=0.0, format="%.2f", default=0.0),
        "دائن": st.column_config.NumberColumn("دائن", min_value=0.0, format="%.2f", default=0.0),
        "الطرف": st.column_config.SelectboxColumn("العميل / المورد", options=popts, width="medium"),
        "المرجع": st.column_config.TextColumn("المرجع"), "بيان السطر": st.column_config.TextColumn("بيان السطر")})
    lines = []
    for _, r in ed.iterrows():
        if r.get("الحساب") in (None, "") or pd.isna(r.get("الحساب")):
            continue
        d, c = float(r.get("مدين") or 0), float(r.get("دائن") or 0)
        if d == 0 and c == 0:
            continue
        lines.append(dict(code=int(opt_code(r["الحساب"])), debit=d, credit=c, party=opt_code(r.get("الطرف")), ref=str(r.get("المرجع") or ""), note=str(r.get("بيان السطر") or "")))
    td, tc = sum(cents(l["debit"]) for l in lines), sum(cents(l["credit"]) for l in lines)
    a, b, c3 = st.columns(3)
    a.metric("إجمالي المدين", f"{fromc(td):,.2f}")
    b.metric("إجمالي الدائن", f"{fromc(tc):,.2f}")
    c3.metric("الفرق", f"{fromc(td - tc):,.2f}", delta="متوازن ✓" if td == tc and td > 0 else "غير متوازن", delta_color="normal" if td == tc and td > 0 else "inverse")
    return lines


def update_manual_entry(no, date, lines, op_type, source, note):
    delete_entries([no])
    return post_entry(date, lines, op_type, source, entry_no=no, note=note)


# ============================================================
# لوحة التحكم
# ============================================================
def page_dashboard():
    s = st.session_state
    st.title(f"{s.settings['الرمز']} لوحة التحكم")
    c1, c2, _ = st.columns([1, 1, 3])
    frm = c1.date_input("من", fiscal_start(today()), key="dash_a")
    to = c2.date_input("إلى", today(), key="dash_b")
    if frm > to:
        st.error("تاريخ البداية بعد تاريخ النهاية.")
        return
    net, asof = net_by_account(frm, to), net_by_account(None, to)
    rev, exp = -code_sum(net, 4000, 4999), code_sum(net, 5000, 5999)
    cash = sum(asof.get(c, 0) for c in treasury_codes(False))
    ar, ap = asof.get(AR_CODE, 0), -asof.get(AP_CODE, 0)
    stock, fa = asof.get(INV_ACC, 0), code_sum(asof, 1400, 1999)
    vat = -asof.get(VAT_OUT, 0) - asof.get(VAT_IN, 0)
    r1 = st.columns(4)
    kpi(r1[0], "💰", f"{rev:,.0f}", "صافي الإيرادات (الفترة)")
    kpi(r1[1], "🧾", f"{exp:,.0f}", "إجمالي المصروفات (الفترة)")
    kpi(r1[2], "📈", f"{rev - exp:,.0f}", "صافي الربح / (الخسارة)")
    kpi(r1[3], "🏦", f"{cash:,.0f}", "النقدية والبنوك")
    r2 = st.columns(4)
    kpi(r2[0], "🧑‍💼", f"{ar:,.0f}", "مديونية العملاء")
    kpi(r2[1], "🚚", f"{ap:,.0f}", "مستحق للموردين")
    kpi(r2[2], "📦", f"{stock:,.0f}", "قيمة المخزون")
    kpi(r2[3], "🏢", f"{fa:,.0f}", "صافي الأصول الثابتة")
    j = jdf()
    j = j[(j["_d"] >= ts(frm)) & (j["_d"] <= ts(to))].copy()
    j["m"] = j["_d"].dt.strftime("%Y-%m")
    code = j["كود الحساب"]
    j["rev"] = (j["دائن"] - j["مدين"]).where((code >= 4000) & (code <= 4999), 0.0)
    j["exp"] = (j["مدين"] - j["دائن"]).where((code >= 5000) & (code <= 5999), 0.0)
    agg = j.groupby("m")[["rev", "exp"]].sum()
    g1, g2 = st.columns([2, 1])
    with g1:
        with st.container(border=True):
            st.markdown('<div class="section-title">📊 الإيرادات والمصروفات شهريًا</div>', unsafe_allow_html=True)
            fig = go.Figure()
            fig.add_bar(x=list(agg.index), y=list(agg["rev"]), name="إيرادات", marker_color="#0ea5e9")
            fig.add_bar(x=list(agg.index), y=list(agg["exp"]), name="مصروفات", marker_color="#94a3b8")
            fig.update_layout(height=260, barmode="group", margin=dict(l=6, r=6, t=6, b=4), paper_bgcolor="white", plot_bgcolor="white", legend=dict(orientation="h", y=1.1), yaxis=dict(gridcolor="#f1f5f9"))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    with g2:
        with st.container(border=True):
            st.markdown('<div class="section-title">🍩 تركيب المصروفات</div>', unsafe_allow_html=True)
            lab, val = [], []
            for k, v in net.items():
                if 5000 <= k <= 5999 and v > 0.004:
                    lab.append(acct_name(k))
                    val.append(round(v, 2))
            if val:
                f2 = go.Figure(go.Pie(labels=lab, values=val, hole=0.6, textinfo="percent"))
                f2.update_layout(height=260, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="white", legend=dict(font=dict(size=10)))
                st.plotly_chart(f2, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("لا توجد مصروفات في الفترة.")
    a1, a2 = st.columns(2)
    with a1:
        with st.container(border=True):
            st.markdown('<div class="section-title">🔔 تنبيهات وضوابط النظام</div>', unsafe_allow_html=True)
            tot_d, tot_c = cents(s.journal["مدين"].sum()), cents(s.journal["دائن"].sum())
            alert("ok", "✅ ميزان المراجعة متوازن: إجمالي المدين = إجمالي الدائن") if tot_d == tot_c else alert("bad", f"⛔ اختلال في الدفاتر: فرق {fromc(tot_d - tot_c):,.2f}")
            ar_sub = sum(party_balance("customer", c) for c in s.customers["كود العميل"])
            ap_sub = sum(party_balance("supplier", c) for c in s.suppliers["كود المورد"])
            gl_ar, gl_ap = net_by_account().get(AR_CODE, 0.0), net_by_account().get(AP_CODE, 0.0)
            if abs(ar_sub - gl_ar) < 0.01 and abs(ap_sub + gl_ap) < 0.01 + 0:
                alert("ok", "✅ أرصدة العملاء والموردين مطابقة لحسابات الأستاذ العام")
            else:
                alert("bad", "⛔ أرصدة العملاء/الموردين لا تطابق حسابات الأستاذ العام (راجع القيود اليدوية)")
            sp = stock_position()
            low = sp[(sp["النوع"] == "مخزني") & (sp["الحالة"] == "نشط") & (sp["الكمية"] <= sp["حد إعادة الطلب"])]
            alert("warn", f"⚠️ {len(low)} صنف وصل لحد إعادة الطلب: " + "، ".join(low["اسم الصنف"].head(4))) if len(low) else alert("ok", "✅ لا توجد أصناف تحت حد إعادة الطلب")
            openc = sum(1 for c in s.custody["كود العهدة"] if custody_balance(c) > 0.004)
            alert("info", f"💼 عهد مفتوحة تحتاج تسوية: {openc}") if openc else None
            alert("info", f"🧮 ضريبة القيمة المضافة المستحقة/(القابلة للاسترداد): {vat:,.2f}")
            lock = s.settings.get("تاريخ الإقفال", "")
            alert("info", f"🔒 الفترة مقفلة حتى {lock}") if lock else None
    with a2:
        with st.container(border=True):
            st.markdown('<div class="section-title">🏦 أرصدة الخزائن والبنوك</div>', unsafe_allow_html=True)
            rows = [{"الحساب": r["اسم الحساب"], "الرصيد": round(asof.get(int(r["كود الحساب"]), 0.0), 2)} for _, r in s.treasury.iterrows()]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            top = party_balances("customer", to).sort_values("net", ascending=False).head(5)
            st.markdown('<div class="section-title">🧑‍💼 أعلى العملاء مديونية</div>', unsafe_allow_html=True)
            st.dataframe(top[["اسم العميل", "net"]].rename(columns={"net": "الرصيد"}).round(2), use_container_width=True, hide_index=True)


# ============================================================
# القيود اليومية
# ============================================================
def page_journal():
    s = st.session_state
    lvl = user_level("journal")
    st.title("📒 القيود اليومية")
    tabs = st.tabs(["📚 سجل القيود", "➕ قيد جديد"] if lvl >= 2 else ["📚 سجل القيود"])
    with tabs[0]:
        ed_no = s.get("edit_entry")
        if ed_no and lvl >= 3:
            rows = s.journal[s.journal["رقم القيد"] == ed_no]
            if rows.empty:
                s.pop("edit_entry", None)
            else:
                with st.container(border=True):
                    st.markdown(f'<div class="section-title">✏️ تعديل القيد {ed_no}</div>', unsafe_allow_html=True)
                    r0 = rows.iloc[0]
                    d = st.date_input("التاريخ", to_date(r0["التاريخ"]), key="ee_date")
                    nt = st.text_input("البيان", r0["البيان"], key="ee_note")
                    init = pd.DataFrame({"الحساب": [f"{r['كود الحساب']} — {r['اسم الحساب']}" for _, r in rows.iterrows()], "مدين": rows["مدين"].tolist(), "دائن": rows["دائن"].tolist(),
                                         "الطرف": [(f"{r['الطرف']} — {party_name(r['الطرف'])}" if r["الطرف"] else None) for _, r in rows.iterrows()], "المرجع": rows["المرجع"].tolist(), "بيان السطر": rows["البيان"].tolist()})
                    lines = entry_lines_editor(f"ee_lines_{ed_no}", init)
                    c1, c2 = st.columns(2)
                    if c1.button("💾 حفظ التعديل", type="primary", use_container_width=True, key="ee_save"):
                        ok, _ = do(update_manual_entry, ed_no, d, lines, r0["نوع العملية"], r0["المصدر"], nt, ok="تم تعديل القيد بنجاح")
                        if ok:
                            s.pop("edit_entry", None)
                            bump("j_entries")
                            st.rerun()
                    if c2.button("إلغاء", use_container_width=True, key="ee_cancel"):
                        s.pop("edit_entry", None)
                        st.rerun()
        es = entries_summary()
        view, sel = show_table(es, "j_entries", date_col="التاريخ", height=330)
        if sel:
            nos = view.loc[sel, "رقم القيد"].tolist()
            st.info(f"تم تحديد {len(nos)} قيد")
            for n in nos[:6]:
                with st.expander(f"سطور القيد {n}", expanded=len(nos) == 1):
                    st.dataframe(s.journal[s.journal["رقم القيد"] == n][["التاريخ", "كود الحساب", "اسم الحساب", "مدين", "دائن", "الطرف", "المرجع", "البيان", "المصدر", "المستخدم"]], use_container_width=True, hide_index=True)
            b = st.columns(4)
            if lvl >= 3 and len(nos) == 1:
                src = view.loc[sel[0], "المصدر"]
                if src in ("يدوي", "استيراد", "رصيد افتتاحي") and b[0].button("✏️ تعديل القيد", use_container_width=True):
                    s["edit_entry"] = nos[0]
                    st.rerun()
                elif src not in ("يدوي", "استيراد", "رصيد افتتاحي"):
                    b[0].caption("القيود الآلية تُعدَّل من شاشة مستندها الأصلي")
            if lvl >= 2 and len(nos) == 1 and b[1].button("↩️ عكس القيد", use_container_width=True):
                ok, r = do(reverse_entry, nos[0], ok="تم إنشاء القيد العكسي {}")
                if ok:
                    bump("j_entries")
                    st.rerun()
            if lvl >= 3:
                conf = b[2].checkbox(f"أؤكد حذف {len(nos)} قيد", key="j_del_ok")
                if b[3].button("🗑️ حذف المحدد", disabled=not conf, type="primary", use_container_width=True):
                    ok, _ = do(delete_entries, nos, ok=f"تم حذف {len(nos)} قيد")
                    if ok:
                        bump("j_entries")
                        st.rerun()
        elif lvl >= 3:
            st.caption("حدّد قيدًا أو أكثر من الجدول (مربع الاختيار على يمين الصف) لعرض السطور أو التعديل أو الحذف أو العكس.")
        if len(es):
            download_bar(s.journal.drop(columns=[c for c in s.journal.columns if c.startswith("_")]), "دفتر اليومية", "journal", key="dl_j")
    if lvl >= 2:
        with tabs[1]:
            with st.container(border=True):
                c1, c2, c3 = st.columns([1, 1, 2])
                d = c1.date_input("تاريخ القيد", today(), key="ne_date")
                tp = c2.selectbox("نوع القيد", ["قيد يومية", "قيد تسوية", "قيد افتتاحي", "قيد تصحيح"], key="ne_type")
                nt = c3.text_input("البيان العام", key="ne_note")
                v = s.get("_v_ne", 0)
                lines = entry_lines_editor(f"ne_lines_{v}")
                st.caption("ملاحظة: عند اختيار «عملاء محليون» أو «موردون محليون» يجب تحديد الطرف. لا يُقبل القيد إلا متوازنًا.")
                if st.button("💾 ترحيل القيد", type="primary", use_container_width=True, key="ne_post"):
                    ok, no = do(post_entry, d, lines, tp, "يدوي", note=nt, ok="تم ترحيل القيد {}")
                    if ok:
                        log_action("قيد يدوي", str(no))
                        persist()
                        bump("ne")
                        bump("j_entries")
                        st.rerun()


# ============================================================
# دفتر الأستاذ
# ============================================================
def page_ledger():
    st.title("📖 دفتر الأستاذ (كشف حساب)")
    opts = account_options()
    c = st.columns([2, 1.3, 1, 1])
    pick = c[0].selectbox("الحساب", opts, key="lg_acc")
    code = int(opt_code(pick))
    frm, to = date_range("lg", cols=c[2:])
    party = ""
    if code in (AR_CODE, AP_CODE):
        kind = "customer" if code == AR_CODE else "supplier"
        po = ["الكل"] + party_options(kind, False)
        pp = c[1].selectbox("الطرف", po, key="lg_party")
        party = "" if pp == "الكل" else opt_code(pp)
    j = jdf()
    m = j["كود الحساب"] == code
    if party:
        m &= j["الطرف"] == party
    sg = natural_sign(code)
    before = j[m & (j["_d"] < ts(frm))]
    opening = sg * (before["مدين"].sum() - before["دائن"].sum())
    per = j[m & (j["_d"] >= ts(frm)) & (j["_d"] <= ts(to))].sort_values(["_d", "رقم القيد"])
    rows = [{"التاريخ": str(frm), "رقم القيد": "", "البيان": "رصيد افتتاحي", "الطرف": party, "مدين": 0.0, "دائن": 0.0, "الرصيد": round(opening, 2)}]
    run = opening
    for _, r in per.iterrows():
        run += sg * (r["مدين"] - r["دائن"])
        rows.append({"التاريخ": r["التاريخ"], "رقم القيد": r["رقم القيد"], "البيان": r["البيان"] or r["نوع العملية"], "الطرف": r["الطرف"], "مدين": r["مدين"], "دائن": r["دائن"], "الرصيد": round(run, 2)})
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)
    a, b, d = st.columns(3)
    a.metric("رصيد أول الفترة", f"{opening:,.2f}")
    b.metric("حركة الفترة (مدين / دائن)", f"{per['مدين'].sum():,.2f} / {per['دائن'].sum():,.2f}")
    d.metric("رصيد آخر الفترة", f"{run:,.2f}")
    download_bar(df, f"كشف حساب {acct_name(code)}", f"ledger_{code}", f"الفترة من {frm} إلى {to}", key="dl_lg")


# ============================================================
# القوائم والتقارير المالية
# ============================================================
def page_reports():
    st.title("📊 القوائم والتقارير المالية")
    rep = st.radio("التقرير", ["قائمة المركز المالي", "قائمة الدخل", "ميزان المراجعة", "ضريبة القيمة المضافة", "تقييم المخزون", "أعمار وأرصدة العملاء والموردين"], horizontal=True, key="rep_pick")
    st.caption("جميع القوائم تُحتسب تلقائيًا من القيود المرحّلة. حدّد الفترة ثم نزّل التقرير بصيغة Excel أو PDF.")
    if rep == "قائمة المركز المالي":
        c = st.columns([1, 3])
        asof = c[0].date_input("كما في تاريخ", today(), key="bs_asof")
        rows, diff, ta = balance_sheet(asof)
        st.markdown(stmt_html(rows, "قائمة المركز المالي", f"كما في {asof}   |   {st.session_state.settings['اسم الشركة']}"), unsafe_allow_html=True)
        alert("ok", "✅ المعادلة المحاسبية متزنة: الأصول = الالتزامات + حقوق الملكية") if abs(diff) < 0.01 else alert("bad", f"⛔ عدم اتزان قدره {diff:,.2f} — راجع القيود")
        download_bar(stmt_df(rows), "قائمة المركز المالي", f"balance_sheet_{asof}", f"كما في {asof}", key="dl_bs")
    elif rep == "قائمة الدخل":
        frm, to = date_range("is")
        rows, profit = income_statement(frm, to)
        st.markdown(stmt_html(rows, "قائمة الدخل", f"عن الفترة من {frm} إلى {to}   |   {st.session_state.settings['اسم الشركة']}"), unsafe_allow_html=True)
        download_bar(stmt_df(rows), "قائمة الدخل", f"income_{frm}_{to}", f"من {frm} إلى {to}", key="dl_is")
    elif rep == "ميزان المراجعة":
        frm, to = date_range("tb")
        tb = trial_balance(frm, to)
        tot = tb.drop(columns=["الكود", "الحساب"]).sum()
        st.dataframe(tb, use_container_width=True, hide_index=True)
        ok = abs(tot["ختامي مدين"] - tot["ختامي دائن"]) < 0.01 and abs(tot["حركة مدين"] - tot["حركة دائن"]) < 0.01
        alert("ok", "✅ الميزان متوازن") if ok else alert("bad", "⛔ الميزان غير متوازن")
        c = st.columns(4)
        c[0].metric("حركة مدين", f"{tot['حركة مدين']:,.2f}")
        c[1].metric("حركة دائن", f"{tot['حركة دائن']:,.2f}")
        c[2].metric("ختامي مدين", f"{tot['ختامي مدين']:,.2f}")
        c[3].metric("ختامي دائن", f"{tot['ختامي دائن']:,.2f}")
        totrow = pd.DataFrame([{"الكود": "", "الحساب": "الإجمالي", **{k: round(v, 2) for k, v in tot.items()}}])
        download_bar(pd.concat([tb, totrow], ignore_index=True), "ميزان المراجعة", f"trial_balance_{frm}_{to}", f"من {frm} إلى {to}", key="dl_tb")
    elif rep == "ضريبة القيمة المضافة":
        frm, to = date_range("vat")
        v = vat_summary(frm, to)
        st.dataframe(v, use_container_width=True, hide_index=True)
        download_bar(v, "ملخص ضريبة القيمة المضافة", f"vat_{frm}_{to}", f"من {frm} إلى {to}", key="dl_vat")
    elif rep == "تقييم المخزون":
        asof = st.date_input("كما في تاريخ", today(), key="sv_asof")
        sp = stock_position(asof)
        sp = sp[sp["النوع"] == "مخزني"]
        st.dataframe(sp, use_container_width=True, hide_index=True)
        gl = net_by_account(None, asof).get(INV_ACC, 0.0)
        c = st.columns(2)
        c[0].metric("إجمالي قيمة المخزون (سجل الأصناف)", f"{sp['القيمة'].sum():,.2f}")
        c[1].metric("رصيد حساب المخزون بالأستاذ", f"{gl:,.2f}")
        download_bar(sp, "تقييم المخزون", f"stock_valuation_{asof}", f"كما في {asof}", key="dl_sv")
    else:
        asof = st.date_input("كما في تاريخ", today(), key="ag_asof")
        for kind in PK:
            p = PK[kind]
            t = party_balances(kind, asof)
            t = t[t["net"].abs() > 0.004]
            df = pd.DataFrame({"الكود": t[p["code"]], "الاسم": t[p["name"]], "مدين": t["مدين"].round(2), "دائن": t["دائن"].round(2), "الرصيد": t["net"].round(2).abs(), "الطبيعة": t["net"].map(side_label)})
            st.markdown(f"**{p['plural']}**")
            st.dataframe(df, use_container_width=True, hide_index=True)
            download_bar(df, f"أرصدة {p['plural']}", f"balances_{kind}_{asof}", f"كما في {asof}", key=f"dl_ag_{kind}")


# ============================================================
# شجرة الحسابات
# ============================================================
def page_coa():
    s = st.session_state
    lvl = user_level("coa")
    st.title("🌳 شجرة الحسابات")
    ch = chart().copy()
    net = net_by_account()
    ch["الرصيد الحالي"] = ch["الكود"].map(lambda k: round(natural_sign(k) * net.get(k, 0.0), 2) if acct_row(k)["التصنيف"] == "تفصيلي" else 0.0)
    ch["حساب نظام"] = ch["الكود"].isin(SYSTEM_CODES).map({True: "نعم", False: ""})
    view, sel = show_table(ch, "coa", height=360)
    if lvl >= 2:
        with st.expander("➕ إضافة حساب جديد"):
            c = st.columns(4)
            code = c[0].number_input("الكود", min_value=1000, max_value=9999, step=1, value=1500, key="coa_code")
            name = c[1].text_input("اسم الحساب", key="coa_name")
            typ = c[2].selectbox("النوع", list(TYPE_DIGIT), key="coa_type")
            cls = c[3].selectbox("التصنيف", ["تفصيلي", "فرعي", "رئيسي"], key="coa_cls")
            if st.button("إضافة الحساب", type="primary", key="coa_add"):
                def _add():
                    if not name.strip():
                        raise AccountingError("اسم الحساب مطلوب.")
                    if int(code) in set(chart()["الكود"]):
                        raise AccountingError("الكود مستخدم بالفعل.")
                    if str(int(code))[0] != TYPE_DIGIT[typ]:
                        raise AccountingError(f"كود حساب من نوع «{typ}» يجب أن يبدأ بالرقم {TYPE_DIGIT[typ]}.")
                    s.custom_chart = pd.concat([chart(), pd.DataFrame([{"الكود": int(code), "اسم الحساب": name.strip(), "النوع": typ, "التصنيف": cls}])], ignore_index=True).sort_values("الكود").reset_index(drop=True)
                    log_action("إضافة حساب", f"{code} {name}")
                ok, _ = do(_add, ok="تمت إضافة الحساب")
                if ok:
                    st.rerun()
    if sel and lvl >= 3 and len(sel) == 1:
        code = int(view.loc[sel[0], "الكود"])
        r = acct_row(code)
        with st.container(border=True):
            st.markdown(f'<div class="section-title">✏️ الحساب {code}</div>', unsafe_allow_html=True)
            nn = st.text_input("الاسم", r["اسم الحساب"], key=f"coa_en_{code}")
            b = st.columns(3)
            if b[0].button("💾 حفظ الاسم", use_container_width=True):
                s.custom_chart.loc[s.custom_chart["الكود"] == code, "اسم الحساب"] = nn.strip()
                s.journal.loc[s.journal["كود الحساب"] == code, "اسم الحساب"] = nn.strip()
                persist()
                bump("coa")
                st.rerun()
            used = (s.journal["كود الحساب"] == code).any()
            conf = b[1].checkbox("أؤكد الحذف", key=f"coa_dc_{code}")
            if b[2].button("🗑️ حذف الحساب", disabled=not conf, use_container_width=True):
                if code in SYSTEM_CODES:
                    st.error("حساب أساسي في النظام لا يمكن حذفه.")
                elif used:
                    st.error("عليه حركات مسجلة ولا يمكن حذفه.")
                elif code in treasury_codes(False):
                    st.error("مرتبط بحساب خزينة/بنك.")
                else:
                    s.custom_chart = chart()[chart()["الكود"] != code].reset_index(drop=True)
                    persist()
                    bump("coa")
                    st.rerun()
    download_bar(ch, "شجرة الحسابات", "chart_of_accounts", key="dl_coa")

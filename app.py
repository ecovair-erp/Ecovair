import streamlit as st
import pandas as pd
import datetime
import plotly.graph_objects as go
import json
import io
import sqlite3
import os

# ============================================================
# تخزين دائم محلي (SQLite) مع إبقاء بيانات الجلسة الحالية
# ============================================================
DB_PATH = os.environ.get("ECOVAIR_DB_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "ecovair_data.sqlite3"))

def _db_init():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS app_state (state_key TEXT PRIMARY KEY, payload TEXT NOT NULL)")

def _db_load(key):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            row = conn.execute("SELECT payload FROM app_state WHERE state_key=?", (key,)).fetchone()
        return json.loads(row[0]) if row else None
    except Exception:
        return None

def _db_save(key, value):
    try:
        if isinstance(value, pd.DataFrame):
            payload = {"kind":"dataframe", "data":value.where(pd.notna(value), None).to_dict(orient="records"), "columns":list(value.columns)}
        else:
            payload = {"kind":"json", "data":value}
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("INSERT INTO app_state(state_key,payload) VALUES(?,?) ON CONFLICT(state_key) DO UPDATE SET payload=excluded.payload", (key, json.dumps(payload, ensure_ascii=False, default=str)))
    except Exception as exc:
        st.warning(f"تعذر حفظ البيانات محليًا ({key}): {exc}")

_db_init()

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Ecovair ERP - نظام إيكوفير للتكييف والتوريدات",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# GLOBAL THEME
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], [data-testid="stAppViewContainer"] * {
    font-family: 'Cairo', 'Segoe UI', Tahoma, sans-serif !important;
}

[data-testid="stAppViewContainer"] { background-color: #eef2f7 !important; }
[data-testid="stHeader"] { background: transparent !important; }
.block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; max-width: 1440px !important; }

[data-testid="stAppViewContainer"] .main p,
[data-testid="stAppViewContainer"] .main span,
[data-testid="stAppViewContainer"] .main label,
[data-testid="stAppViewContainer"] .main h1,
[data-testid="stAppViewContainer"] .main h2,
[data-testid="stAppViewContainer"] .main h3,
[data-testid="stAppViewContainer"] .main div { color: #0f172a; }

h1 { font-size: 1.5rem !important; font-weight: 800 !important; margin: 0 0 0.9rem 0 !important; }
h2 { font-size: 1.05rem !important; font-weight: 700 !important; }
h3 { font-size: 0.95rem !important; font-weight: 700 !important; }

/* مسافات أهدأ بين الكتل */
[data-testid="stVerticalBlock"] { gap: 0.85rem !important; }
hr { margin: 0.5rem 0 !important; opacity: 0.12; }

/* ---------- الكروت الحقيقية (st.container(border=True)) ---------- */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff !important;
    border-radius: 14px !important;
    border: 1px solid #e9edf3 !important;
    box-shadow: 0 2px 10px rgba(15,23,42,0.05) !important;
    padding: 2px 4px !important;
}
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlock"] { gap: 0.4rem !important; }

.section-title {
    font-size: 0.86rem; font-weight: 700; color:#0f172a !important;
    padding: 8px 4px 2px 4px; display:flex; align-items:center; gap:6px;
}

/* dataframes / inputs */
[data-testid="stDataFrame"] { background:#ffffff !important; border-radius: 12px; overflow:hidden; }
.stSelectbox div[data-baseweb="select"] > div,
.stTextInput input, .stNumberInput input, .stDateInput input {
    background:#ffffff !important; color:#0f172a !important;
    border-radius: 10px !important; border: 1px solid #e2e8f0 !important;
}
.stTabs [data-baseweb="tab-list"] { gap: 6px; }
.stTabs [data-baseweb="tab"] { border-radius: 10px 10px 0 0 !important; }

/* ---------- SIDEBAR ---------- */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0b1120 0%, #101827 55%, #0f172a 100%) !important;
    border-left: 1px solid #1e293b;
}
[data-testid="stSidebar"] * { color: #cbd5e1 !important; }
[data-testid="stSidebar"] .block-container { padding-top: 1.1rem !important; padding-bottom: 1rem !important; }
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: 0.15rem !important; }

.sb-brand {
    display:flex; align-items:center; gap:10px;
    padding: 4px 6px 16px 6px;
    border-bottom: 1px solid rgba(148,163,184,0.15);
    margin-bottom: 10px;
}
.sb-brand .icon {
    width:40px; height:40px; border-radius:12px;
    background: linear-gradient(135deg,#0ea5e9,#38bdf8);
    display:flex; align-items:center; justify-content:center;
    font-size:1.2rem; box-shadow:0 4px 14px rgba(14,165,233,0.4);
    flex-shrink:0;
}
.sb-brand .txt b { font-size:1rem; color:#f8fafc !important; display:block; line-height:1.2;}
.sb-brand .txt span { font-size:0.66rem; color:#64748b !important; }

.sb-section-label {
    font-size: 0.65rem; color:#3f5169 !important; font-weight:700;
    letter-spacing:0.4px; margin: 14px 8px 4px 8px; text-transform:uppercase;
}

[data-testid="stSidebar"] .stButton { margin-bottom: 2px; }
[data-testid="stSidebar"] .stButton > button {
    width: 100%; background: transparent !important; border: 1px solid transparent !important;
    text-align: right !important; justify-content: flex-start !important;
    font-size: 0.82rem !important; font-weight: 500 !important;
    padding: 8px 12px !important; border-radius: 9px !important;
    box-shadow: none !important; transition: all .15s ease;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(56,189,248,0.10) !important; border-color: rgba(56,189,248,0.25) !important; color:#38bdf8 !important;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: linear-gradient(90deg,#0ea5e9,#0284c7) !important; color:#fff !important;
    font-weight:700 !important; box-shadow: 0 4px 14px rgba(14,165,233,0.35) !important;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"] * { color:#ffffff !important; }

.sb-footer { margin-top: 18px; padding-top: 12px; border-top: 1px solid rgba(148,163,184,0.15);
             font-size: 0.66rem; color:#475569 !important; text-align:center; }

/* ---------- KPI CARDS ---------- */
.kpi-card {
    height: 96px; background: linear-gradient(135deg, #0f172a 0%, #16324f 100%);
    border-radius: 14px; padding: 12px 14px; display:flex; flex-direction:column; justify-content:center;
    box-shadow: 0 4px 14px rgba(15,23,42,0.18);
}
.kpi-card .kpi-icon { font-size: 1.1rem; }
.kpi-card .kpi-value { font-size: 1.28rem; font-weight: 800; color: #38bdf8 !important; margin-top:2px; }
.kpi-card .kpi-label { font-size: 0.7rem; color: #94a3b8 !important; }
.kpi-card .kpi-delta { font-size: 0.68rem; color: #4ade80 !important; }

.alert-card { border-radius: 10px; padding: 10px 12px; margin-bottom: 8px; font-size: 0.8rem; font-weight: 500; }
.alert-warn { background:#fef3c7; color:#92400e !important; border-right:4px solid #f59e0b; }
.alert-warn * { color:#92400e !important; }
.alert-info { background:#dbeafe; color:#1e40af !important; border-right:4px solid #3b82f6; }
.alert-info * { color:#1e40af !important; }
.alert-ok   { background:#dcfce7; color:#166534 !important; border-right:4px solid #22c55e; }
.alert-ok * { color:#166534 !important; }

.progress-label { display:flex; justify-content:space-between; font-size:0.72rem; color:#64748b !important; margin-bottom:3px; }
.progress-bg { background:#e2e8f0; border-radius:6px; height:6px; margin-bottom:8px; }
.progress-fill { height:6px; border-radius:6px; }

.badge { display:inline-block; padding:2px 9px; border-radius:20px; font-size:0.7rem; font-weight:700; }
.badge-green { background:#dcfce7; color:#166534; }
.badge-yellow{ background:#fef3c7; color:#92400e; }
.badge-red   { background:#fee2e2; color:#991b1b; }
.badge-blue  { background:#dbeafe; color:#1e40af; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# البيانات الأساسية
# ============================================================
@st.cache_data
def get_ecovair_chart():
    return pd.DataFrame([
        {"الكود": 1000, "اسم الحساب": "الأصول", "النوع": "أصل", "التصنيف": "رئيسي"},
        {"الكود": 1100, "اسم الحساب": "النقدية والبنوك", "النوع": "أصل", "التصنيف": "فرعي"},
        {"الكود": 1110, "اسم الحساب": "الصندوق", "النوع": "أصل", "التصنيف": "تفصيلي"},
        {"الكود": 1120, "اسم الحساب": "الحساب البنكي", "النوع": "أصل", "التصنيف": "تفصيلي"},
        {"الكود": 1200, "اسم الحساب": "الذمم المدينة", "النوع": "أصل", "التصنيف": "فرعي"},
        {"الكود": 1210, "اسم الحساب": "عملاء محليون", "النوع": "أصل", "التصنيف": "تفصيلي"},
        {"الكود": 1300, "اسم الحساب": "مخزون السلع", "النوع": "أصل", "التصنيف": "فرعي"},
        {"الكود": 1310, "اسم الحساب": "بضاعة آخر الفترة", "النوع": "أصل", "التصنيف": "تفصيلي"},
        {"الكود": 1400, "اسم الحساب": "الأصول الثابتة", "النوع": "أصل", "التصنيف": "فرعي"},
        {"الكود": 1410, "اسم الحساب": "الممتلكات والآلات", "النوع": "أصل", "التصنيف": "تفصيلي"},
        {"الكود": 2000, "اسم الحساب": "الالتزامات", "النوع": "التزام", "التصنيف": "رئيسي"},
        {"الكود": 2100, "اسم الحساب": "الذمم الدائنة", "النوع": "التزام", "التصنيف": "فرعي"},
        {"الكود": 2110, "اسم الحساب": "موردون محليون", "النوع": "التزام", "التصنيف": "تفصيلي"},
        {"الكود": 2300, "اسم الحساب": "الضرائب المستحقة", "النوع": "التزام", "التصنيف": "فرعي"},
        {"الكود": 2310, "اسم الحساب": "ضريبة الدخل / القيمة المضافة", "النوع": "التزام", "التصنيف": "تفصيلي"},
        {"الكود": 3000, "اسم الحساب": "حقوق الملكية", "النوع": "ملكية", "التصنيف": "رئيسي"},
        {"الكود": 3110, "اسم الحساب": "رأس المال المدفوع", "النوع": "ملكية", "التصنيف": "تفصيلي"},
        {"الكود": 4000, "اسم الحساب": "الإيرادات", "النوع": "إيراد", "التصنيف": "رئيسي"},
        {"الكود": 4110, "اسم الحساب": "مبيعات محلية (توريد وتركيب)", "النوع": "إيراد", "التصنيف": "تفصيلي"},
        {"الكود": 5000, "اسم الحساب": "المصروفات", "النوع": "مصروف", "التصنيف": "رئيسي"},
        {"الكود": 5120, "اسم الحساب": "المشتريات (معدات وخامات)", "النوع": "مصروف", "التصنيف": "تفصيلي"},
        {"الكود": 5210, "اسم الحساب": "الرواتب و الأجور", "النوع": "مصروف", "التصنيف": "تفصيلي"},
        {"الكود": 5220, "اسم الحساب": "الأيجار", "النوع": "مصروف", "التصنيف": "تفصيلي"},
        {"الكود": 5270, "اسم الحساب": "الصيانة والإصلاحات", "النوع": "مصروف", "التصنيف": "تفصيلي"}
    ])

chart_df = st.session_state.get("custom_chart", get_ecovair_chart())

if "journal" not in st.session_state:
    st.session_state.journal = pd.DataFrame([
        {"التاريخ": "2026-01-01", "رقم القيد": "J001", "نوع العملية": "قيد افتتاحي", "كود المدين": 1120, "الحساب المدين": "الحساب البنكي", "كود الدائن": 3110, "الحساب الدائن": "رأس المال المدفوع", "المبلغ": 1000000.0, "الملاحظات": "إيداع رأس مال شركة Ecovair"},
        {"التاريخ": "2026-01-05", "رقم القيد": "J002", "نوع العملية": "فاتورة شراء", "كود المدين": 5120, "الحساب المدين": "المشتريات (معدات وخامات)", "كود الدائن": 2110, "الحساب الدائن": "موردون محليون", "المبلغ": 400000.0, "الملاحظات": "شراء وحدات تكييف وتوريدات دكت"},
        {"التاريخ": "2026-01-15", "رقم القيد": "J003", "نوع العملية": "فاتورة بيع", "كود المدين": 1210, "الحساب المدين": "عملاء محليون", "كود الدائن": 4110, "الحساب الدائن": "مبيعات محلية (توريد وتركيب)", "المبلغ": 650000.0, "الملاحظات": "مستخلص توريد وتركيب مشروع تكييف"},
        {"التاريخ": "2026-01-20", "رقم القيد": "J004", "نوع العملية": "سداد فاتورة", "كود المدين": 1120, "الحساب المدين": "الحساب البنكي", "كود الدائن": 1210, "الحساب الدائن": "عملاء محليون", "المبلغ": 500000.0, "الملاحظات": "تحصيل دفعة من العميل"},
        {"التاريخ": "2026-01-31", "رقم القيد": "J005", "نوع العملية": "اذن صرف", "كود المدين": 5210, "الحساب المدين": "الرواتب و الأجور", "كود الدائن": 1120, "الحساب الدائن": "الحساب البنكي", "المبلغ": 60000.0, "الملاحظات": "صرف رواتب مهندسي وفنيي Ecovair"}
    ])

DEFAULTS = {
    "customers": [
        {"اسم العميل": "شركة النيل للمقاولات", "الهاتف": "01001234567", "الرصيد الافتتاحي": 0.0, "ملاحظات": "عميل مشاريع توريد وتركيب"},
    ],
    "suppliers": [
        {"اسم المورد": "مصنع الدلتا للتكييفات", "الهاتف": "01112345678", "نوع التوريد": "معدات تكييف", "الرصيد الافتتاحي": 0.0},
    ],
    "inventory": [
        {"كود الصنف": "AC-001", "اسم الصنف": "وحدة تكييف اسبليت 1.5 حصان", "الوحدة": "قطعة", "الكمية المتاحة": 25.0, "سعر الوحدة": 9500.0, "حد إعادة الطلب": 5.0},
        {"كود الصنف": "DC-010", "اسم الصنف": "دكت ألوميتال (متر)", "الوحدة": "متر", "الكمية المتاحة": 180.0, "سعر الوحدة": 220.0, "حد إعادة الطلب": 30.0},
    ],
    "treasury": [
        {"اسم الحساب": "الخزنة الرئيسية", "النوع": "خزنة نقدية", "رقم الحساب": "-", "الرصيد الحالي": 0.0},
        {"اسم الحساب": "البنك الأهلي - حساب جاري", "النوع": "بنك", "رقم الحساب": "EG12-4455-9981", "الرصيد الحالي": 0.0},
    ],
    "custody": [
        {"اسم الموظف": "م. أحمد سامي", "المبلغ": 15000.0, "تاريخ الصرف": "2026-01-10", "الغرض": "مصاريف تركيب مشروع", "الحالة": "مفتوحة"},
    ],
    "users": [
        {"اسم المستخدم": "Admin", "البريد الإلكتروني": "admin@ecovair.com", "الدور": "مدير عام", "الحالة": "نشط"},
        {"اسم المستخدم": "محاسب1", "البريد الإلكتروني": "acc@ecovair.com", "الدور": "محاسب", "الحالة": "نشط"},
    ],
}
for key, rows in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = pd.DataFrame(rows)

# سجلات إضافية قابلة للتوسع
if "fixed_assets" not in st.session_state:
    st.session_state.fixed_assets = pd.DataFrame(columns=["كود الأصل", "اسم الأصل", "التصنيف", "تاريخ الشراء", "تكلفة الأصل", "القيمة التخريدية", "العمر الإنتاجي (سنوات)", "طريقة الإهلاك", "حساب الأصل", "مجمع الإهلاك", "مصروف الإهلاك"])
if "depreciation_log" not in st.session_state:
    st.session_state.depreciation_log = pd.DataFrame(columns=["التاريخ", "كود الأصل", "اسم الأصل", "مصروف الإهلاك", "مجمع الإهلاك", "صافي القيمة الدفترية"])

if "settings" not in st.session_state:
    st.session_state.settings = {
        "اسم الشركة": "Ecovair للتكييف والتوريدات",
        "الرقم الضريبي": "300-123-456",
        "العملة": "جنيه مصري (EGP)",
        "بداية السنة المالية": "01-01",
        "الرمز": "❄️",
    }

# استعادة آخر بيانات محفوظة من قاعدة البيانات المحلية
_PERSIST_KEYS = ["journal", "customers", "suppliers", "inventory", "treasury", "custody", "users", "fixed_assets", "depreciation_log", "custom_chart", "settings"]
for _key in _PERSIST_KEYS:
    _saved = _db_load(_key)
    if _saved:
        try:
            if _saved.get("kind") == "dataframe":
                st.session_state[_key] = pd.DataFrame(_saved.get("data", []), columns=_saved.get("columns"))
            else:
                st.session_state[_key] = _saved.get("data", {})
        except Exception:
            pass
chart_df = st.session_state.get("custom_chart", get_ecovair_chart())

# ============================================================
# دالة مساعدة عامة: قائمة + إضافة (زي موديولات Odoo)
# ============================================================
def crud_module(title, icon, state_key, fields, key_prefix=None):
    st.title(f"{icon} {title}")
    tab_list, tab_add, tab_manage = st.tabs(["📋 القائمة والبحث", "➕ إضافة جديد", "✏️ تعديل / حذف"])
    with tab_list:
        df = st.session_state[state_key].copy()
        if df.empty:
            st.info("لا توجد بيانات مسجلة بعد.")
        else:
            query = st.text_input("🔎 بحث في السجلات", key=f"search_{key_prefix or state_key}")
            if query:
                mask = df.astype(str).apply(lambda col: col.str.contains(query, case=False, na=False)).any(axis=1)
                df = df[mask]
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.caption(f"عدد السجلات المعروضة: {len(df)}")
    with tab_add:
        with st.container(border=True):
            with st.form(f"form_{key_prefix or state_key}", clear_on_submit=True):
                values = {}
                cols = st.columns(2)
                for i, f in enumerate(fields):
                    col = cols[i % 2]
                    if f["type"] == "text": values[f["key"]] = col.text_input(f["label"])
                    elif f["type"] == "number": values[f["key"]] = col.number_input(f["label"], min_value=f.get("min", 0.0), step=f.get("step", 1.0))
                    elif f["type"] == "select": values[f["key"]] = col.selectbox(f["label"], f["options"])
                    elif f["type"] == "date": values[f["key"]] = str(col.date_input(f["label"], datetime.date.today()))
                submitted = st.form_submit_button("💾 حفظ", use_container_width=True, type="primary")
                if submitted:
                    if not values.get(fields[0]["key"]): st.error("من فضلك أدخل الاسم / الحقل الأساسي.")
                    else:
                        st.session_state[state_key] = pd.concat([st.session_state[state_key], pd.DataFrame([values])], ignore_index=True)
                        st.success("✅ تم الحفظ بنجاح")
                        st.rerun()
    with tab_manage:
        df = st.session_state[state_key]
        if df.empty:
            st.info("لا توجد سجلات لإدارتها.")
        else:
            idx = st.selectbox("اختر السجل", list(range(len(df))), format_func=lambda i: str(df.iloc[i].get(fields[0]["key"], f"سجل {i+1}")), key=f"manage_select_{key_prefix or state_key}")
            row = df.iloc[idx].to_dict()
            with st.form(f"manage_form_{key_prefix or state_key}"):
                updated = {}
                cols = st.columns(2)
                for i, f in enumerate(fields):
                    col = cols[i % 2]; old = row.get(f["key"], "")
                    if f["type"] == "text": updated[f["key"]] = col.text_input(f["label"], str(old), key=f"edit_{state_key}_{idx}_{f['key']}")
                    elif f["type"] == "number": updated[f["key"]] = col.number_input(f["label"], min_value=f.get("min", 0.0), value=float(old or 0), step=f.get("step", 1.0), key=f"edit_{state_key}_{idx}_{f['key']}")
                    elif f["type"] == "select":
                        opts=f["options"]; updated[f["key"]] = col.selectbox(f["label"], opts, index=opts.index(old) if old in opts else 0, key=f"edit_{state_key}_{idx}_{f['key']}")
                    elif f["type"] == "date":
                        try: old_date=datetime.date.fromisoformat(str(old)[:10])
                        except Exception: old_date=datetime.date.today()
                        updated[f["key"]] = str(col.date_input(f["label"], old_date, key=f"edit_{state_key}_{idx}_{f['key']}"))
                a,b=st.columns(2)
                save = a.form_submit_button("💾 حفظ التعديل", use_container_width=True, type="primary")
                delete = b.form_submit_button("🗑️ حذف السجل", use_container_width=True)
                if save:
                    if not updated.get(fields[0]["key"]): st.error("الحقل الأساسي مطلوب.")
                    else:
                        for key,value in updated.items(): st.session_state[state_key].at[idx,key]=value
                        st.success("تم تعديل السجل."); st.rerun()
                if delete:
                    st.session_state[state_key] = st.session_state[state_key].drop(index=idx).reset_index(drop=True)
                    st.success("تم حذف السجل."); st.rerun()

def kpi(col, icon, value, label, delta=None):
    delta_html = f'<div class="kpi-delta">▲ {delta}</div>' if delta else '<div class="kpi-delta">&nbsp;</div>'
    col.markdown(f"""
    <div class="kpi-card">
        <span class="kpi-icon">{icon}</span>
        <div class="kpi-value">{value}</div>
        <div class="kpi-label">{label}</div>
        {delta_html}
    </div>""", unsafe_allow_html=True)

# ============================================================
# SIDEBAR — تنقل عصري مقسم لمجموعات
# ============================================================
if "current_page" not in st.session_state:
    st.session_state.current_page = "dashboard"

NAV_GROUPS = [
    {"label": "الرئيسية", "items": [
        {"key": "dashboard", "icon": "📊", "label": "لوحة التحكم"},
    ]},
    {"label": "المحاسبة", "items": [
        {"key": "new_entry", "icon": "📝", "label": "تسجيل قيد جديد"},
        {"key": "ledger", "icon": "📖", "label": "اليومية والأستاذ"},
        {"key": "trial_balance", "icon": "⚖️", "label": "ميزان المراجعة"},
        {"key": "financials", "icon": "📈", "label": "القوائم المالية"},
        {"key": "chart_of_accounts", "icon": "🌳", "label": "شجرة الحسابات"},
        {"key": "fixed_assets", "icon": "🏢", "label": "الأصول الثابتة والإهلاك"},
        {"key": "reports", "icon": "📤", "label": "التقارير والتصدير"},
    ]},
    {"label": "العلاقات", "items": [
        {"key": "customers", "icon": "🧑‍💼", "label": "العملاء"},
        {"key": "suppliers", "icon": "🚚", "label": "الموردين"},
    ]},
    {"label": "المخزون", "items": [
        {"key": "inventory", "icon": "📦", "label": "الأصناف والمخزون"},
    ]},
    {"label": "الخزينة", "items": [
        {"key": "treasury", "icon": "🏦", "label": "البنوك والخزنة الرئيسية"},
        {"key": "custody", "icon": "💼", "label": "العهد"},
    ]},
    {"label": "الإدارة", "items": [
        {"key": "users", "icon": "👥", "label": "المستخدمين والصلاحيات"},
        {"key": "settings", "icon": "⚙️", "label": "الإعدادات"},
    ]},
]

with st.sidebar:
    st.markdown(f"""
    <div class="sb-brand">
        <div class="icon">{st.session_state.settings['الرمز']}</div>
        <div class="txt"><b>ECOVAIR ERP</b><span>نظام الحسابات والتوريدات</span></div>
    </div>
    """, unsafe_allow_html=True)

    for group in NAV_GROUPS:
        st.markdown(f'<div class="sb-section-label">{group["label"]}</div>', unsafe_allow_html=True)
        for item in group["items"]:
            is_active = st.session_state.current_page == item["key"]
            if st.button(f"{item['icon']}  {item['label']}", key=f"nav_{item['key']}",
                         use_container_width=True, type="primary" if is_active else "secondary"):
                st.session_state.current_page = item["key"]
                st.rerun()

    st.markdown(f"""
    <div class="sb-footer">{datetime.date.today().strftime('%Y-%m-%d')}<br>Ecovair © 2026</div>
    """, unsafe_allow_html=True)

menu = st.session_state.current_page

# ============================================================
# 1. DASHBOARD
# ============================================================
if menu == "dashboard":
    top_l, top_r = st.columns([3, 1])
    with top_l:
        st.title(f"{st.session_state.settings['الرمز']} لوحة التحكم المالية")
    with top_r:
        df_tmp = st.session_state.journal.copy()
        df_tmp['التاريخ'] = pd.to_datetime(df_tmp['التاريخ'])
        df_tmp['شهر_رقم'] = df_tmp['التاريخ'].dt.to_period('M').astype(str)
        month_options = ["كل الشهور"] + sorted(df_tmp['شهر_رقم'].unique().tolist())
        selected_month = st.selectbox("🗓️ فلتر الشهر", month_options, label_visibility="collapsed")

    df_all = st.session_state.journal.copy()
    df_all['التاريخ'] = pd.to_datetime(df_all['التاريخ'])
    df_all['شهر_رقم'] = df_all['التاريخ'].dt.to_period('M').astype(str)
    df_j = df_all if selected_month == "كل الشهور" else df_all[df_all['شهر_رقم'] == selected_month]
    today_str = str(datetime.date.today())

    tot_sales     = df_j[df_j["كود الدائن"] == 4110]["المبلغ"].sum()
    tot_purchases = df_j[df_j["كود المدين"] == 5120]["المبلغ"].sum()
    tot_salaries  = df_j[df_j["كود المدين"] == 5210]["المبلغ"].sum()
    tot_rent      = df_j[df_j["كود المدين"] == 5220]["المبلغ"].sum() if 5220 in df_j["كود المدين"].values else 0
    tot_expenses  = tot_purchases + tot_salaries + tot_rent
    net_profit    = tot_sales - tot_expenses

    bank_bal = (df_j[df_j["كود المدين"]==1120]["المبلغ"].sum() - df_j[df_j["كود الدائن"]==1120]["المبلغ"].sum())
    cash_bal = (df_j[df_j["كود المدين"]==1110]["المبلغ"].sum() - df_j[df_j["كود الدائن"]==1110]["المبلغ"].sum())
    today_count = len(df_j[df_j["التاريخ"].astype(str).str[:10] == today_str])

    rec_due = df_j[df_j["كود المدين"]==1210]["المبلغ"].sum() - df_j[df_j["كود الدائن"]==1210]["المبلغ"].sum()
    pay_due = df_j[df_j["كود الدائن"]==2110]["المبلغ"].sum() - df_j[df_j["كود المدين"]==2110]["المبلغ"].sum()

    c1, c2, c3, c4, c5 = st.columns(5)
    kpi(c1, "💰", f"{tot_sales/1000:,.0f}K", "إجمالي المبيعات")
    kpi(c2, "🛒", f"{tot_purchases/1000:,.0f}K", "إجمالي المشتريات")
    kpi(c3, "📈", f"{net_profit/1000:,.0f}K", "صافي الربح", delta=f"{net_profit/1000:,.0f}K" if net_profit>=0 else None)
    kpi(c4, "🏦", f"{(bank_bal+cash_bal)/1000:,.0f}K", "رصيد البنك والنقدية")
    kpi(c5, "📄", f"{today_count}", "فواتير اليوم")

    col_bar, col_budget, col_costs = st.columns([2.1, 1.5, 1.4])

    month_order = ['01','02','03','04','05','06','07','08','09','10','11','12']
    month_names = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']
    df_all['شهر_م'] = df_all['التاريخ'].dt.strftime('%m')
    monthly_s = df_all[df_all["كود الدائن"]==4110].groupby('شهر_م')['المبلغ'].sum().reindex(month_order, fill_value=0)

    bar_colors = ['#1e3a5f'] * 12
    nonzero = monthly_s[monthly_s > 0]
    if len(nonzero) > 0:
        bar_colors[month_order.index(nonzero.index[-1])] = '#38bdf8'

    with col_bar:
        with st.container(border=True):
            st.markdown('<div class="section-title">📊 التدفقات الشهرية</div>', unsafe_allow_html=True)
            fig_bar = go.Figure(go.Bar(x=month_names, y=monthly_s.values, marker_color=bar_colors, width=0.55))
            fig_bar.update_layout(height=240, paper_bgcolor='white', plot_bgcolor='white',
                                   margin=dict(l=6, r=6, t=4, b=4), showlegend=False,
                                   xaxis=dict(showgrid=False, tickfont=dict(size=10, color='#64748b')),
                                   yaxis=dict(showgrid=True, gridcolor='#f1f5f9', tickfont=dict(size=10, color='#64748b')))
            st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})

    with col_budget:
        with st.container(border=True):
            st.markdown('<div class="section-title">💳 توزيع الميزانية</div>', unsafe_allow_html=True)
            values = [tot_purchases, tot_salaries, tot_rent]
            fig_d1 = go.Figure(go.Pie(labels=['مشتريات','رواتب','إيجار'], values=values, hole=0.65,
                                       marker_colors=['#0ea5e9','#1e3a5f','#94a3b8'],
                                       textinfo='none', hoverinfo='label+percent'))
            fig_d1.update_layout(height=135, paper_bgcolor='white', margin=dict(l=0,r=0,t=0,b=0), showlegend=False,
                                 annotations=[dict(text=f"<b>{sum(values)/1000:,.1f}K</b>", x=0.5, y=0.5,
                                                    font_size=13, showarrow=False, font_color='#0f172a')])
            st.plotly_chart(fig_d1, use_container_width=True, config={'displayModeBar': False})
            inflow_pct = min(int(tot_sales/(tot_sales+tot_expenses+1)*100), 100)
            outflow_pct = 100 - inflow_pct
            st.markdown(f"""
            <div class="progress-label"><span>تدفق داخل</span><b>{inflow_pct}%</b></div>
            <div class="progress-bg"><div class="progress-fill" style="width:{inflow_pct}%;background:#0ea5e9;"></div></div>
            <div class="progress-label"><span>تدفق خارج</span><b>{outflow_pct}%</b></div>
            <div class="progress-bg"><div class="progress-fill" style="width:{outflow_pct}%;background:#94a3b8;"></div></div>
            """, unsafe_allow_html=True)

    with col_costs:
        with st.container(border=True):
            st.markdown('<div class="section-title">📦 التكاليف</div>', unsafe_allow_html=True)
            cost_labels = ['مشتريات','رواتب','إيجار']
            cost_vals = [tot_purchases, tot_salaries, tot_rent]
            cost_colors = ['#0f172a','#0ea5e9','#38bdf8']
            fig_c = go.Figure(go.Pie(labels=cost_labels, values=cost_vals, hole=0.62,
                                      marker_colors=cost_colors, textinfo='none', hoverinfo='label+percent'))
            fig_c.update_layout(height=125, paper_bgcolor='white', margin=dict(l=0,r=0,t=0,b=0), showlegend=False,
                                annotations=[dict(text=f"<b>{tot_expenses/1000:,.1f}K</b>", x=0.5, y=0.5,
                                                   font_size=12, showarrow=False, font_color='#0f172a')])
            st.plotly_chart(fig_c, use_container_width=True, config={'displayModeBar': False})
            for lbl, val, clr in zip(cost_labels, cost_vals, cost_colors):
                pct = int(val/(tot_expenses+1)*100)
                st.markdown(f"""<div style="display:flex;justify-content:space-between;font-size:0.72rem;color:#475569;margin-bottom:3px;">
                    <span><span style="color:{clr};">●</span> {lbl}</span><span>{pct}% &nbsp;<b>{val/1000:,.0f}K</b></span></div>""",
                    unsafe_allow_html=True)

    col_line, col_alerts = st.columns([2.4, 1.6])

    with col_line:
        with st.container(border=True):
            st.markdown('<div class="section-title">📈 مقارنة الإيرادات والمصروفات</div>', unsafe_allow_html=True)
            df_sorted = df_all.sort_values('التاريخ').copy()
            df_sorted['ايراد_تراكمي'] = df_sorted['المبلغ'].where(df_sorted['كود الدائن']==4110, 0).cumsum()
            df_sorted['مصروف_تراكمي'] = df_sorted['المبلغ'].where(df_sorted['كود المدين'].isin([5120,5210,5220]), 0).cumsum()
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(x=df_sorted['التاريخ'], y=df_sorted['ايراد_تراكمي'], name='إيرادات',
                                           mode='lines', fill='tozeroy', line=dict(color='#0ea5e9', width=2.5),
                                           fillcolor='rgba(14,165,233,0.08)'))
            fig_line.add_trace(go.Scatter(x=df_sorted['التاريخ'], y=df_sorted['مصروف_تراكمي'], name='مصروفات',
                                           mode='lines', fill='tozeroy', line=dict(color='#94a3b8', width=2, dash='dot'),
                                           fillcolor='rgba(148,163,184,0.06)'))
            fig_line.update_layout(height=205, paper_bgcolor='white', plot_bgcolor='white',
                                    margin=dict(l=6, r=6, t=6, b=4),
                                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10)),
                                    xaxis=dict(showgrid=False, tickfont=dict(size=9)),
                                    yaxis=dict(showgrid=True, gridcolor='#f1f5f9', tickfont=dict(size=9)))
            st.plotly_chart(fig_line, use_container_width=True, config={'displayModeBar': False})

    with col_alerts:
        with st.container(border=True):
            st.markdown('<div class="section-title">🔔 التنبيهات</div>', unsafe_allow_html=True)
            if rec_due > 0:
                st.markdown(f'<div class="alert-card alert-warn">⚠️ مستحقات عملاء غير محصلة<br><b>{rec_due:,.0f} ج.م</b></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="alert-card alert-ok">✅ جميع مستحقات العملاء محصلة</div>', unsafe_allow_html=True)
            if pay_due > 0:
                st.markdown(f'<div class="alert-card alert-info">📌 التزامات موردين مستحقة<br><b>{pay_due:,.0f} ج.م</b></div>', unsafe_allow_html=True)
            if net_profit >= 0:
                st.markdown(f'<div class="alert-card alert-ok">📈 الشركة رابحة<br><b>+{net_profit:,.0f} ج.م</b></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="alert-card alert-warn">📉 خسارة صافية<br><b>{net_profit:,.0f} ج.م</b></div>', unsafe_allow_html=True)

# ============================================================
# 2. تسجيل قيد جديد
# ============================================================
elif menu == "new_entry":
    st.title("📝 تسجيل قيد محاسبي جديد")
    detailed_accounts = chart_df[chart_df["التصنيف"] == "تفصيلي"]
    with st.container(border=True):
        with st.form("new_entry_form"):
            col1, col2 = st.columns(2)
            with col1:
                entry_date = st.date_input("تاريخ العملية", datetime.date.today())
                op_type = st.selectbox("نوع العملية", ["فاتورة بيع", "فاتورة شراء", "اذن صرف", "تحصيل من عميل", "سداد لمورد", "قيد افتتاحي"])
                amount = st.number_input("المبلغ (EGP)", min_value=1.0, step=100.0)
            with col2:
                entry_num = st.text_input("رقم القيد", f"J{len(st.session_state.journal)+1:03d}")
                debit_acc = st.selectbox("الحساب المدين (من حساب)", detailed_accounts["اسم الحساب"])
                credit_acc = st.selectbox("الحساب الدائن (إلى حساب)", detailed_accounts["اسم الحساب"])
            notes = st.text_input("البيان / تفاصيل العملية")
            btn = st.form_submit_button("💾 حفظ القيد المحاسبي", use_container_width=True, type="primary")

            if btn:
                if debit_acc == credit_acc:
                    st.error("لا يمكن أن يكون الحساب المدين والدائن نفس الحساب!")
                else:
                    d_code = detailed_accounts[detailed_accounts["اسم الحساب"] == debit_acc]["الكود"].values[0]
                    c_code = detailed_accounts[detailed_accounts["اسم الحساب"] == credit_acc]["الكود"].values[0]
                    new_row = {
                        "التاريخ": str(entry_date), "رقم القيد": entry_num, "نوع العملية": op_type,
                        "كود المدين": d_code, "الحساب المدين": debit_acc,
                        "كود الدائن": c_code, "الحساب الدائن": credit_acc,
                        "المبلغ": float(amount), "الملاحظات": notes
                    }
                    st.session_state.journal = pd.concat([st.session_state.journal, pd.DataFrame([new_row])], ignore_index=True)
                    st.success(f"✅ تم حفظ القيد {entry_num} بنجاح!")

# ============================================================
# 3. اليومية والأستاذ
# ============================================================
elif menu == "ledger":
    st.title("📖 دفتر اليومية العامة وحسابات الأستاذ")
    tab1, tab2 = st.tabs(["اليومية العامة", "كشف حساب أستاذ تفصيلي"])
    with tab1:
        with st.container(border=True):
            st.dataframe(st.session_state.journal, use_container_width=True, hide_index=True)
    with tab2:
        with st.container(border=True):
            acc_choice = st.selectbox("اختر الحساب:", chart_df[chart_df["التصنيف"]=="تفصيلي"]["اسم الحساب"])
            df_j = st.session_state.journal
            d_df = df_j[df_j["الحساب المدين"] == acc_choice][["التاريخ", "رقم القيد", "المبلغ", "الملاحظات"]].copy()
            d_df["مدين"] = d_df["المبلغ"]; d_df["دائن"] = 0.0
            c_df = df_j[df_j["الحساب الدائن"] == acc_choice][["التاريخ", "رقم القيد", "المبلغ", "الملاحظات"]].copy()
            c_df["مدين"] = 0.0; c_df["دائن"] = c_df["المبلغ"]
            ledger = pd.concat([d_df, c_df]).sort_values(by="التاريخ")
            if not ledger.empty:
                ledger["الرصيد التراكمي"] = (ledger["مدين"] - ledger["دائن"]).cumsum()
                st.dataframe(ledger[["التاريخ", "رقم القيد", "مدين", "دائن", "الرصيد التراكمي", "الملاحظات"]], use_container_width=True, hide_index=True)
            else:
                st.info("لا توجد حركات مسجلة على هذا الحساب حتى الآن.")

# ============================================================
# 4. ميزان المراجعة
# ============================================================
elif menu == "trial_balance":
    st.title("⚖️ ميزان المراجعة بالإجماليات والأرصدة")
    df_j = st.session_state.journal
    tb_data, tot_d, tot_c = [], 0, 0
    for _, row in chart_df[chart_df["التصنيف"] == "تفصيلي"].iterrows():
        code, name, acc_type = row["الكود"], row["اسم الحساب"], row["النوع"]
        debits = df_j[df_j["كود المدين"] == code]["المبلغ"].sum()
        credits = df_j[df_j["كود الدائن"] == code]["المبلغ"].sum()
        if debits > 0 or credits > 0:
            tb_data.append({"الكود": code, "اسم الحساب": name, "النوع": acc_type,
                             "إجمالي المدين": debits, "إجمالي الدائن": credits, "الرصيد الصافي": debits - credits})
            tot_d += debits; tot_c += credits
    with st.container(border=True):
        st.dataframe(pd.DataFrame(tb_data), use_container_width=True, hide_index=True)
    st.success(f"⚖️ إجمالي الحركة المدينة: {tot_d:,.2f} EGP | إجمالي الحركة الدائنة: {tot_c:,.2f} EGP")

# ============================================================
# 5. القوائم المالية
# ============================================================
elif menu == "financials":
    st.title("📈 القوائم المالية")
    df_j = st.session_state.journal.copy()
    accounts = st.session_state.get("custom_chart", get_ecovair_chart()).copy()
    if df_j.empty:
        st.info("لا توجد قيود كافية لإعداد القوائم المالية.")
    else:
        # أرصدة الحسابات محسوبة من جانبي المدين والدائن
        rows=[]
        for _, acc in accounts.iterrows():
            code=acc["الكود"]; name=acc["اسم الحساب"]; typ=acc["النوع"]
            debit=float(df_j.loc[df_j["كود المدين"]==code,"المبلغ"].sum())
            credit=float(df_j.loc[df_j["كود الدائن"]==code,"المبلغ"].sum())
            # الأصول والمصروفات طبيعتها مدينة، والباقي دائن
            balance=(debit-credit) if typ in ["أصل","مصروف"] else (credit-debit)
            rows.append({"الكود":code,"الحساب":name,"النوع":typ,"مدين":debit,"دائن":credit,"الرصيد":balance})
        balances=pd.DataFrame(rows)
        rev=float(balances.loc[balances["النوع"]=="إيراد","الرصيد"].sum())
        exp=float(balances.loc[balances["النوع"]=="مصروف","الرصيد"].sum())
        profit=rev-exp
        st.subheader("📄 قائمة الدخل")
        income=balances[balances["النوع"].isin(["إيراد","مصروف"])][["الكود","الحساب","النوع","الرصيد"]].copy()
        st.dataframe(income,use_container_width=True,hide_index=True)
        a,b,c=st.columns(3); a.metric("إجمالي الإيرادات",f"{rev:,.2f} {st.session_state.settings.get('العملة','EGP')}"); b.metric("إجمالي المصروفات",f"{exp:,.2f}"); c.metric("صافي الربح / الخسارة",f"{profit:,.2f}")
        st.divider(); st.subheader("🏛️ الميزانية العمومية")
        assets=balances[balances["النوع"]=="أصل"][ ["الكود","الحساب","الرصيد"] ].copy()
        liabilities=balances[balances["النوع"]=="التزام"][ ["الكود","الحساب","الرصيد"] ].copy()
        equity=balances[balances["النوع"]=="ملكية"][ ["الكود","الحساب","الرصيد"] ].copy()
        # نتيجة الفترة تظهر ضمن حقوق الملكية لأغراض العرض
        if abs(profit)>0.0001:
            equity=pd.concat([equity,pd.DataFrame([{"الكود":"—","الحساب":"صافي نتيجة الفترة","الرصيد":profit}])],ignore_index=True)
        x,y=st.columns(2)
        with x:
            st.markdown("**الأصول**"); st.dataframe(assets,use_container_width=True,hide_index=True); st.metric("إجمالي الأصول",f"{assets['الرصيد'].sum():,.2f}")
        with y:
            st.markdown("**الالتزامات وحقوق الملكية**")
            st.dataframe(pd.concat([liabilities.assign(القسم="التزامات"),equity.assign(القسم="حقوق الملكية")],ignore_index=True),use_container_width=True,hide_index=True)
            st.metric("إجمالي الالتزامات وحقوق الملكية",f"{liabilities['الرصيد'].sum()+equity['الرصيد'].sum():,.2f}")
        st.caption("تنبيه: القوائم مبنية على دليل الحسابات والقيود المسجلة حاليًا. راجع التصنيف المحاسبي واكتمال القيود قبل اعتمادها رسميًا.")
        st.subheader("⚖️ ميزان المراجعة")
        st.dataframe(balances,use_container_width=True,hide_index=True)

# ============================================================
# 6. شجرة الحسابات
# ============================================================
elif menu == "chart_of_accounts":
    st.title("🌳 شجرة الحسابات")
    with st.container(border=True):
        st.dataframe(chart_df, use_container_width=True, hide_index=True)
    st.subheader("إضافة حساب تفصيلي")
    with st.form("chart_add_form", clear_on_submit=True):
        a,b,c=st.columns(3)
        new_code=a.number_input("كود الحساب",min_value=1,step=1)
        new_name=b.text_input("اسم الحساب")
        new_type=c.selectbox("نوع الحساب",["أصل","التزام","ملكية","إيراد","مصروف"])
        if st.form_submit_button("إضافة الحساب",type="primary"):
            if not new_name.strip(): st.error("اسم الحساب مطلوب.")
            elif int(new_code) in chart_df["الكود"].astype(int).tolist(): st.error("كود الحساب موجود بالفعل.")
            else:
                chart_df=pd.concat([chart_df,pd.DataFrame([{"الكود":int(new_code),"اسم الحساب":new_name,"النوع":new_type,"التصنيف":"تفصيلي"}])],ignore_index=True)
                st.session_state.custom_chart=chart_df
                st.success("تمت إضافة الحساب لهذه الجلسة."); st.rerun()
    if "custom_chart" in st.session_state:
        chart_df=st.session_state.custom_chart
        st.subheader("تعديل / حذف حساب")
        editable=chart_df[chart_df["التصنيف"]=="تفصيلي"]
        if not editable.empty:
            chosen=st.selectbox("اختر الحساب",editable["الكود"].tolist(),format_func=lambda code: f"{code} — {editable[editable['الكود']==code]['اسم الحساب'].iloc[0]}")
            acc_row=chart_df.index[chart_df["الكود"]==chosen][0]
            x,y=st.columns(2)
            edited_name=x.text_input("اسم الحساب المعدل",str(chart_df.at[acc_row,"اسم الحساب"]))
            edited_type=y.selectbox("نوع الحساب المعدل",["أصل","التزام","ملكية","إيراد","مصروف"],index=["أصل","التزام","ملكية","إيراد","مصروف"].index(chart_df.at[acc_row,"النوع"]) if chart_df.at[acc_row,"النوع"] in ["أصل","التزام","ملكية","إيراد","مصروف"] else 0)
            u,v=st.columns(2)
            if u.button("حفظ تعديل الحساب"):
                chart_df.at[acc_row,"اسم الحساب"]=edited_name; chart_df.at[acc_row,"النوع"]=edited_type
                st.session_state.custom_chart=chart_df; st.success("تم تعديل الحساب."); st.rerun()
            if v.button("حذف الحساب"):
                used=(st.session_state.journal["كود المدين"].eq(chosen)|st.session_state.journal["كود الدائن"].eq(chosen)).any()
                if used: st.error("لا يمكن حذف حساب عليه حركات مسجلة.")
                else:
                    st.session_state.custom_chart=chart_df.drop(index=acc_row).reset_index(drop=True); st.success("تم حذف الحساب."); st.rerun()

# ============================================================
# 7. العملاء
# ============================================================
elif menu == "customers":
    crud_module("العملاء", "🧑‍💼", "customers", [
        {"key": "اسم العميل", "label": "اسم العميل", "type": "text"},
        {"key": "الهاتف", "label": "رقم الهاتف", "type": "text"},
        {"key": "الرصيد الافتتاحي", "label": "الرصيد الافتتاحي", "type": "number"},
        {"key": "ملاحظات", "label": "ملاحظات", "type": "text"},
    ])

# ============================================================
# 8. الموردين
# ============================================================
elif menu == "suppliers":
    crud_module("الموردين", "🚚", "suppliers", [
        {"key": "اسم المورد", "label": "اسم المورد", "type": "text"},
        {"key": "الهاتف", "label": "رقم الهاتف", "type": "text"},
        {"key": "نوع التوريد", "label": "نوع التوريد", "type": "text"},
        {"key": "الرصيد الافتتاحي", "label": "الرصيد الافتتاحي", "type": "number"},
    ])

# ============================================================
# 9. المخزون
# ============================================================
elif menu == "inventory":
    st.title("📦 الأصناف والمخزون")
    tab_list, tab_add = st.tabs(["📋 القائمة", "➕ إضافة صنف"])
    with tab_list:
        with st.container(border=True):
            df = st.session_state.inventory.copy()
            if df.empty:
                st.info("لا توجد أصناف مسجلة بعد.")
            else:
                df["قيمة المخزون"] = df["الكمية المتاحة"] * df["سعر الوحدة"]
                st.dataframe(df, use_container_width=True, hide_index=True)
                low_stock = df[df["الكمية المتاحة"] <= df["حد إعادة الطلب"]]
                m1, m2 = st.columns(2)
                m1.metric("💰 إجمالي قيمة المخزون", f"{df['قيمة المخزون'].sum():,.0f} ج.م")
                m2.metric("⚠️ أصناف تحتاج إعادة طلب", f"{len(low_stock)}")
    with tab_add:
        with st.container(border=True):
            with st.form("form_inventory", clear_on_submit=True):
                col1, col2 = st.columns(2)
                item_code = col1.text_input("كود الصنف")
                item_name = col2.text_input("اسم الصنف")
                unit = col1.text_input("الوحدة", "قطعة")
                qty = col2.number_input("الكمية المتاحة", min_value=0.0, step=1.0)
                price = col1.number_input("سعر الوحدة", min_value=0.0, step=10.0)
                reorder = col2.number_input("حد إعادة الطلب", min_value=0.0, step=1.0)
                if st.form_submit_button("💾 حفظ الصنف", use_container_width=True, type="primary"):
                    if not item_name:
                        st.error("من فضلك أدخل اسم الصنف.")
                    else:
                        new_row = {"كود الصنف": item_code, "اسم الصنف": item_name, "الوحدة": unit,
                                   "الكمية المتاحة": qty, "سعر الوحدة": price, "حد إعادة الطلب": reorder}
                        st.session_state.inventory = pd.concat([st.session_state.inventory, pd.DataFrame([new_row])], ignore_index=True)
                        st.success("✅ تم حفظ الصنف بنجاح")
                        st.rerun()

# ============================================================
# 10. البنوك والخزنة الرئيسية
# ============================================================
elif menu == "treasury":
    st.title("🏦 البنوك والخزنة الرئيسية")
    df_j = st.session_state.journal
    bank_bal = df_j[df_j["كود المدين"]==1120]["المبلغ"].sum() - df_j[df_j["كود الدائن"]==1120]["المبلغ"].sum()
    cash_bal = df_j[df_j["كود المدين"]==1110]["المبلغ"].sum() - df_j[df_j["كود الدائن"]==1110]["المبلغ"].sum()

    m1, m2, m3 = st.columns(3)
    kpi(m1, "🏦", f"{bank_bal:,.0f}", "رصيد الحساب البنكي (من دفتر اليومية)")
    kpi(m2, "💵", f"{cash_bal:,.0f}", "رصيد الصندوق (من دفتر اليومية)")
    kpi(m3, "📊", f"{(bank_bal+cash_bal):,.0f}", "إجمالي السيولة")

    crud_module("حسابات البنوك والخزنة المسجلة", "📒", "treasury", [
        {"key": "اسم الحساب", "label": "اسم الحساب / الخزنة", "type": "text"},
        {"key": "النوع", "label": "النوع", "type": "select", "options": ["بنك", "خزنة نقدية"]},
        {"key": "رقم الحساب", "label": "رقم الحساب", "type": "text"},
        {"key": "الرصيد الحالي", "label": "الرصيد الحالي (تسجيل يدوي)", "type": "number"},
    ], key_prefix="treasury")

# ============================================================
# 11. العهد
# ============================================================
elif menu == "custody":
    crud_module("العهد المالية للموظفين", "💼", "custody", [
        {"key": "اسم الموظف", "label": "اسم الموظف", "type": "text"},
        {"key": "المبلغ", "label": "مبلغ العهدة", "type": "number"},
        {"key": "تاريخ الصرف", "label": "تاريخ الصرف", "type": "date"},
        {"key": "الغرض", "label": "الغرض من العهدة", "type": "text"},
        {"key": "الحالة", "label": "الحالة", "type": "select", "options": ["مفتوحة", "تحت التسوية", "مغلقة"]},
    ], key_prefix="custody")

# ============================================================
# 12. المستخدمين والصلاحيات
# ============================================================
elif menu == "users":
    crud_module("المستخدمين والصلاحيات", "👥", "users", [
        {"key": "اسم المستخدم", "label": "اسم المستخدم", "type": "text"},
        {"key": "البريد الإلكتروني", "label": "البريد الإلكتروني", "type": "text"},
        {"key": "الدور", "label": "الدور / الصلاحية", "type": "select",
         "options": ["مدير عام", "محاسب", "مدير مبيعات", "مدير مخزون", "اطلاع فقط"]},
        {"key": "الحالة", "label": "الحالة", "type": "select", "options": ["نشط", "موقوف"]},
    ], key_prefix="users")

# ============================================================
# 13. الإعدادات
# ============================================================
elif menu == "settings":
    st.title("⚙️ إعدادات النظام")
    with st.container(border=True):
        st.markdown('<div class="section-title">🏢 بيانات الشركة</div>', unsafe_allow_html=True)
        with st.form("settings_form"):
            col1, col2 = st.columns(2)
            company_name = col1.text_input("اسم الشركة", st.session_state.settings["اسم الشركة"])
            tax_id = col2.text_input("الرقم الضريبي", st.session_state.settings["الرقم الضريبي"])
            currency = col1.selectbox("العملة", ["جنيه مصري (EGP)", "دولار أمريكي (USD)", "ريال سعودي (SAR)"], index=0)
            fiscal_start = col2.text_input("بداية السنة المالية (يوم-شهر)", st.session_state.settings["بداية السنة المالية"])
            if st.form_submit_button("💾 حفظ الإعدادات", use_container_width=True, type="primary"):
                st.session_state.settings.update({
                    "اسم الشركة": company_name, "الرقم الضريبي": tax_id,
                    "العملة": currency, "بداية السنة المالية": fiscal_start,
                })
                st.success("✅ تم حفظ الإعدادات بنجاح")
                st.rerun()

    with st.container(border=True):
        st.markdown('<div class="section-title">ℹ️ الإعدادات الحالية</div>', unsafe_allow_html=True)
        for k, v in st.session_state.settings.items():
            st.markdown(f"**{k}:** {v}")

    st.subheader("استيراد إعدادات / نسخة JSON")
    uploaded_backup=st.file_uploader("اختر ملف JSON تم تصديره من النظام",type=["json"],key="settings_json_upload")
    if uploaded_backup is not None and st.button("استيراد الإعدادات من الملف"):
        try:
            imported=json.loads(uploaded_backup.getvalue().decode("utf-8"))
            if isinstance(imported.get("الإعدادات"),dict):
                st.session_state.settings.update(imported["الإعدادات"])
                st.success("تم استيراد إعدادات الشركة.")
                st.rerun()
            else: st.error("الملف لا يحتوي على قسم الإعدادات المتوقع.")
        except Exception as exc: st.error(f"تعذر قراءة الملف: {exc}")


# ============================================================
# إضافات المرحلة الأولى: الأصول الثابتة، التصدير، إدارة الحسابات
# ============================================================
if menu == "fixed_assets":
    st.title("🏢 الأصول الثابتة والإهلاك")
    st.caption("حساب الإهلاك هنا بطريقة القسط الثابت، مع حفظ سجل الإهلاك. راجع السياسة المحاسبية قبل اعتماد القيود الفعلية.")
    assets = st.session_state.fixed_assets.copy()
    with st.expander("➕ تسجيل أصل ثابت", expanded=True):
        with st.form("asset_add_form", clear_on_submit=True):
            c1,c2,c3=st.columns(3)
            code=c1.text_input("كود الأصل"); name=c2.text_input("اسم الأصل"); category=c3.selectbox("التصنيف",["أجهزة ومعدات","سيارات","أثاث وتجهيزات","أجهزة كمبيوتر","أخرى"])
            c4,c5,c6=st.columns(3)
            purchase_date=c4.date_input("تاريخ الشراء", datetime.date.today()); cost=c5.number_input("تكلفة الأصل",min_value=0.0,step=1000.0); residual=c6.number_input("القيمة التخريدية",min_value=0.0,step=100.0)
            c7,c8,c9=st.columns(3)
            life=c7.number_input("العمر الإنتاجي (سنوات)",min_value=1,step=1,value=5); asset_account=c8.selectbox("حساب الأصل",["الممتلكات والآلات","الأصول الثابتة"]); accum_account=c9.text_input("حساب مجمع الإهلاك","مجمع إهلاك الأصول")
            expense_account=st.text_input("حساب مصروف الإهلاك","مصروف الإهلاك")
            if st.form_submit_button("حفظ الأصل",type="primary",use_container_width=True):
                if not code.strip() or not name.strip(): st.error("أدخل كود الأصل واسمه.")
                elif residual>cost: st.error("القيمة التخريدية لا يمكن أن تتجاوز تكلفة الأصل.")
                elif code in assets.get("كود الأصل",pd.Series(dtype=str)).astype(str).tolist(): st.error("كود الأصل مسجل بالفعل.")
                else:
                    new={"كود الأصل":code,"اسم الأصل":name,"التصنيف":category,"تاريخ الشراء":str(purchase_date),"تكلفة الأصل":cost,"القيمة التخريدية":residual,"العمر الإنتاجي (سنوات)":life,"طريقة الإهلاك":"القسط الثابت","حساب الأصل":asset_account,"مجمع الإهلاك":accum_account,"مصروف الإهلاك":expense_account}
                    st.session_state.fixed_assets=pd.concat([assets,pd.DataFrame([new])],ignore_index=True); st.success("تم تسجيل الأصل."); st.rerun()
    assets=st.session_state.fixed_assets.copy()
    if not assets.empty:
        assets["الإهلاك السنوي"]=(assets["تكلفة الأصل"]-assets["القيمة التخريدية"])/assets["العمر الإنتاجي (سنوات)"].replace(0,1)
        st.subheader("سجل الأصول")
        st.dataframe(assets,use_container_width=True,hide_index=True)
        selected=st.selectbox("الأصل المطلوب احتساب إهلاكه",assets["كود الأصل"].astype(str),key="dep_asset_select")
        dep_date=st.date_input("تاريخ احتساب الإهلاك",datetime.date.today(),key="dep_date")
        if st.button("احتساب إهلاك سنة واحدة",type="primary"):
            ar=assets[assets["كود الأصل"].astype(str)==selected].iloc[0]
            annual=float(ar["الإهلاك السنوي"]); prev=st.session_state.depreciation_log
            already=float(prev[prev["كود الأصل"].astype(str)==selected]["مصروف الإهلاك"].sum()) if not prev.empty else 0.0
            max_dep=max(0.0,float(ar["تكلفة الأصل"])-float(ar["القيمة التخريدية"])-already)
            amount=min(annual,max_dep)
            if amount<=0: st.warning("تم استنفاد القيمة القابلة للإهلاك لهذا الأصل.")
            else:
                total=already+amount; book=float(ar["تكلفة الأصل"])-total
                rec={"التاريخ":str(dep_date),"كود الأصل":selected,"اسم الأصل":ar["اسم الأصل"],"مصروف الإهلاك":amount,"مجمع الإهلاك":total,"صافي القيمة الدفترية":book}
                st.session_state.depreciation_log=pd.concat([prev,pd.DataFrame([rec])],ignore_index=True)
                # إنشاء قيد إهلاك متوازن تلقائيًا إذا كانت الحسابات المقابلة موجودة بدليل الحسابات
                chart_now=st.session_state.get("custom_chart",get_ecovair_chart())
                exp_name=str(ar.get("مصروف الإهلاك","مصروف الإهلاك")); accum_name=str(ar.get("مجمع الإهلاك","مجمع إهلاك الأصول"))
                exp_acc=chart_now[chart_now["اسم الحساب"].astype(str)==exp_name]
                accum_acc=chart_now[chart_now["اسم الحساب"].astype(str)==accum_name]
                if exp_acc.empty or accum_acc.empty:
                    st.warning("تم حفظ سجل الإهلاك، لكن لم يُنشأ قيد يومية: أضف حساب مصروف الإهلاك وحساب مجمع الإهلاك إلى دليل الحسابات أولًا.")
                else:
                    en=int(exp_acc.iloc[0]["الكود"]); an=int(accum_acc.iloc[0]["الكود"])
                    jnum=f"DEP-{selected}-{str(dep_date).replace('-','')}"
                    if not st.session_state.journal["رقم القيد"].astype(str).eq(jnum).any():
                        jrow={"التاريخ":str(dep_date),"رقم القيد":jnum,"نوع العملية":"قيد إهلاك أصل ثابت","كود المدين":en,"الحساب المدين":exp_name,"كود الدائن":an,"الحساب الدائن":accum_name,"المبلغ":float(amount),"الملاحظات":f"إهلاك الأصل {selected} — {ar['اسم الأصل']}"}
                        st.session_state.journal=pd.concat([st.session_state.journal,pd.DataFrame([jrow])],ignore_index=True)
                        st.success(f"تم تسجيل الإهلاك وإنشاء قيد اليومية {jnum} بقيمة {amount:,.2f}.")
                    else: st.warning("يوجد قيد إهلاك بنفس الرقم؛ لم يتم تكرار القيد.")
                st.rerun()
        st.subheader("سجل الإهلاك")
        st.dataframe(st.session_state.depreciation_log,use_container_width=True,hide_index=True)
    else: st.info("ابدأ بإضافة أول أصل ثابت.")

elif menu == "reports":
    st.title("📤 التقارير والتصدير")
    tables={"دفتر اليومية":st.session_state.journal,"دليل الحسابات":chart_df,"العملاء":st.session_state.customers,"الموردون":st.session_state.suppliers,"المخزون":st.session_state.inventory,"الخزينة":st.session_state.treasury,"الأصول الثابتة":st.session_state.fixed_assets,"سجل الإهلاك":st.session_state.depreciation_log}
    st.write("اختر نوع الملف لتصدير البيانات الحالية.")
    excel_buffer=io.BytesIO()
    with pd.ExcelWriter(excel_buffer,engine="openpyxl") as writer:
        for sheet,df in tables.items(): df.to_excel(writer,sheet_name=sheet[:31],index=False)
    st.download_button("⬇️ تنزيل جميع الجداول Excel",data=excel_buffer.getvalue(),file_name="Ecovair_ERP_Export.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",use_container_width=True)
    payload={name:df.where(pd.notna(df),None).to_dict(orient="records") for name,df in tables.items()}
    payload["الإعدادات"]=st.session_state.settings
    st.download_button("⬇️ تنزيل نسخة JSON للبيانات والإعدادات",data=json.dumps(payload,ensure_ascii=False,indent=2,default=str),file_name="Ecovair_ERP_Backup.json",mime="application/json",use_container_width=True)
    st.divider(); st.subheader("تصدير تقرير محدد")
    report_name=st.selectbox("اختر التقرير",list(tables.keys()))
    report_df=tables[report_name]
    csv_data=report_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button("تنزيل التقرير المحدد CSV",data=csv_data,file_name=f"{report_name}.csv",mime="text/csv",use_container_width=True)
    st.warning("التصدير الحالي يشمل البيانات الموجودة في جلسة التشغيل. النسخ الاحتياطي الدائم وقاعدة البيانات متعددة المستخدمين مرحلة لازمة قبل الاستخدام الفعلي.")


# ============================================================
# حفظ الحالة بعد كل تشغيل/إعادة تشغيل Streamlit
# ============================================================
for _key in _PERSIST_KEYS:
    if _key in st.session_state:
        _db_save(_key, st.session_state[_key])

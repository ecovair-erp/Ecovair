import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import plotly.graph_objects as go

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
# GLOBAL THEME - ثابت بغض النظر عن دارك/لايت مود المتصفح
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], [data-testid="stAppViewContainer"] * {
    font-family: 'Cairo', 'Segoe UI', Tahoma, sans-serif !important;
}

/* ---------- خلفية المحتوى الرئيسي ثابتة دائمًا ---------- */
[data-testid="stAppViewContainer"] {
    background-color: #eef2f7 !important;
}
[data-testid="stHeader"] {
    background: transparent !important;
}
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 1rem !important;
    max-width: 1420px !important;
}

/* ---------- إجبار كل نص داخل المحتوى الرئيسي على لون داكن ثابت ---------- */
[data-testid="stAppViewContainer"] .main p,
[data-testid="stAppViewContainer"] .main span,
[data-testid="stAppViewContainer"] .main label,
[data-testid="stAppViewContainer"] .main h1,
[data-testid="stAppViewContainer"] .main h2,
[data-testid="stAppViewContainer"] .main h3,
[data-testid="stAppViewContainer"] .main div {
    color: #0f172a;
}

h1 { font-size: 1.55rem !important; font-weight: 800 !important; margin-bottom: 0.2rem !important; }
h2 { font-size: 1.2rem !important;  font-weight: 700 !important; }
h3 { font-size: 1.0rem !important;  font-weight: 700 !important; }

/* تقليل المسافات بين العناصر الافتراضية */
[data-testid="stVerticalBlock"] { gap: 0.6rem !important; }
hr { margin: 0.6rem 0 !important; opacity: 0.15; }

/* dataframes / inputs تبقى واضحة في أي وضع */
[data-testid="stDataFrame"] { background:#ffffff !important; border-radius: 12px; overflow:hidden; }
.stSelectbox div[data-baseweb="select"] > div,
.stTextInput input, .stNumberInput input, .stDateInput input {
    background:#ffffff !important; color:#0f172a !important;
    border-radius: 10px !important; border: 1px solid #e2e8f0 !important;
}

/* ---------- SIDEBAR - داكنة ديناميكية دائمًا ---------- */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0b1120 0%, #101827 55%, #0f172a 100%) !important;
    border-left: 1px solid #1e293b;
}
[data-testid="stSidebar"] * { color: #cbd5e1 !important; }
[data-testid="stSidebar"] .block-container { padding-top: 1.2rem !important; }

.sb-brand {
    display:flex; align-items:center; gap:10px;
    padding: 4px 6px 18px 6px;
    border-bottom: 1px solid rgba(148,163,184,0.15);
    margin-bottom: 14px;
}
.sb-brand .icon {
    width:42px; height:42px; border-radius:12px;
    background: linear-gradient(135deg,#0ea5e9,#38bdf8);
    display:flex; align-items:center; justify-content:center;
    font-size:1.3rem; box-shadow:0 4px 14px rgba(14,165,233,0.4);
}
.sb-brand .txt b { font-size:1.02rem; color:#f8fafc !important; display:block; }
.sb-brand .txt span { font-size:0.7rem; color:#64748b !important; }

.sb-section-label {
    font-size: 0.68rem; color:#475569 !important; font-weight:700;
    letter-spacing:0.5px; margin: 14px 6px 6px 6px;
}

/* أزرار التنقل الجانبي */
[data-testid="stSidebar"] .stButton { margin-bottom: 3px; }
[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    background: transparent !important;
    border: 1px solid transparent !important;
    text-align: right !important;
    justify-content: flex-start !important;
    font-size: 0.86rem !important;
    font-weight: 500 !important;
    padding: 9px 14px !important;
    border-radius: 10px !important;
    box-shadow: none !important;
    transition: all .15s ease;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(56,189,248,0.10) !important;
    border-color: rgba(56,189,248,0.25) !important;
    color:#38bdf8 !important;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: linear-gradient(90deg,#0ea5e9,#0284c7) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 14px rgba(14,165,233,0.35) !important;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"] * { color:#ffffff !important; }

.sb-footer {
    margin-top: 26px; padding-top: 14px;
    border-top: 1px solid rgba(148,163,184,0.15);
    font-size: 0.68rem; color:#475569 !important; text-align:center;
}

/* ---------- KPI CARDS ---------- */
.kpi-card {
    height: 96px;
    background: linear-gradient(135deg, #0f172a 0%, #16324f 100%);
    border-radius: 14px;
    padding: 12px 14px;
    display:flex; flex-direction:column; justify-content:center;
    box-shadow: 0 4px 14px rgba(15,23,42,0.18);
}
.kpi-card .row-top { display:flex; align-items:center; justify-content:space-between; }
.kpi-card .kpi-icon { font-size: 1.1rem; }
.kpi-card .kpi-value { font-size: 1.28rem; font-weight: 800; color: #38bdf8 !important; margin-top:2px; }
.kpi-card .kpi-label { font-size: 0.7rem; color: #94a3b8 !important; }
.kpi-card .kpi-delta { font-size: 0.68rem; color: #4ade80 !important; }

/* ---------- SECTION CARDS ---------- */
.section-card {
    background: #ffffff;
    border-radius: 14px;
    padding: 14px 16px;
    box-shadow: 0 2px 8px rgba(15,23,42,0.06);
    height: 100%;
}
.section-title {
    font-size: 0.85rem; font-weight: 700; color:#0f172a !important;
    margin-bottom: 8px; display:flex; align-items:center; gap:6px;
}

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
</style>
""", unsafe_allow_html=True)

# ============================================================
# 1. شجرة الحسابات
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

chart_df = get_ecovair_chart()

if "journal" not in st.session_state:
    st.session_state.journal = pd.DataFrame([
        {"التاريخ": "2026-01-01", "رقم القيد": "J001", "نوع العملية": "قيد افتتاحي", "كود المدين": 1120, "الحساب المدين": "الحساب البنكي", "كود الدائن": 3110, "الحساب الدائن": "رأس المال المدفوع", "المبلغ": 1000000.0, "الملاحظات": "إيداع رأس مال شركة Ecovair"},
        {"التاريخ": "2026-01-05", "رقم القيد": "J002", "نوع العملية": "فاتورة شراء", "كود المدين": 5120, "الحساب المدين": "المشتريات (معدات وخامات)", "كود الدائن": 2110, "الحساب الدائن": "موردون محليون", "المبلغ": 400000.0, "الملاحظات": "شراء وحدات تكييف وتوريدات دكت"},
        {"التاريخ": "2026-01-15", "رقم القيد": "J003", "نوع العملية": "فاتورة بيع", "كود المدين": 1210, "الحساب المدين": "عملاء محليون", "كود الدائن": 4110, "الحساب الدائن": "مبيعات محلية (توريد وتركيب)", "المبلغ": 650000.0, "الملاحظات": "مستخلص توريد وتركيب مشروع تكييف"},
        {"التاريخ": "2026-01-20", "رقم القيد": "J004", "نوع العملية": "سداد فاتورة", "كود المدين": 1120, "الحساب المدين": "الحساب البنكي", "كود الدائن": 1210, "الحساب الدائن": "عملاء محليون", "المبلغ": 500000.0, "الملاحظات": "تحصيل دفعة من العميل"},
        {"التاريخ": "2026-01-31", "رقم القيد": "J005", "نوع العملية": "اذن صرف", "كود المدين": 5210, "الحساب المدين": "الرواتب و الأجور", "كود الدائن": 1120, "الحساب الدائن": "الحساب البنكي", "المبلغ": 60000.0, "الملاحظات": "صرف رواتب مهندسي وفنيي Ecovair"}
    ])

# ============================================================
# SIDEBAR - تنقل عصري ديناميكي
# ============================================================
if "current_page" not in st.session_state:
    st.session_state.current_page = "dashboard"

NAV_ITEMS = [
    {"key": "dashboard",         "icon": "📊", "label": "لوحة التحكم"},
    {"key": "new_entry",         "icon": "📝", "label": "تسجيل قيد جديد"},
    {"key": "ledger",            "icon": "📖", "label": "اليومية والأستاذ"},
    {"key": "trial_balance",     "icon": "⚖️", "label": "ميزان المراجعة"},
    {"key": "financials",        "icon": "📈", "label": "القوائم المالية"},
    {"key": "chart_of_accounts", "icon": "🌳", "label": "شجرة الحسابات"},
]

with st.sidebar:
    st.markdown("""
    <div class="sb-brand">
        <div class="icon">❄️</div>
        <div class="txt"><b>ECOVAIR ERP</b><span>نظام الحسابات والتوريدات</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sb-section-label">القوائم الرئيسية</div>', unsafe_allow_html=True)
    for item in NAV_ITEMS:
        is_active = st.session_state.current_page == item["key"]
        if st.button(f"{item['icon']}  {item['label']}", key=f"nav_{item['key']}",
                     use_container_width=True,
                     type="primary" if is_active else "secondary"):
            st.session_state.current_page = item["key"]
            st.rerun()

    st.markdown(f"""
    <div class="sb-footer">
        {datetime.date.today().strftime('%Y-%m-%d')}<br>Ecovair © 2026
    </div>
    """, unsafe_allow_html=True)

menu = st.session_state.current_page

# ============================================================
# صغيرة: دالة كارت KPI
# ============================================================
def kpi(col, icon, value, label, delta=None):
    delta_html = f'<div class="kpi-delta">▲ {delta}</div>' if delta else '<div class="kpi-delta">&nbsp;</div>'
    col.markdown(f"""
    <div class="kpi-card">
        <div class="row-top"><span class="kpi-icon">{icon}</span></div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-label">{label}</div>
        {delta_html}
    </div>""", unsafe_allow_html=True)

# ============================================================
# 1. DASHBOARD
# ============================================================
if menu == "dashboard":
    top_l, top_r = st.columns([3, 1])
    with top_l:
        st.title("❄️ لوحة التحكم المالية")
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

    # ---- Row 1: KPIs ----
    c1, c2, c3, c4, c5 = st.columns(5)
    kpi(c1, "💰", f"{tot_sales/1000:,.0f}K", "إجمالي المبيعات")
    kpi(c2, "🛒", f"{tot_purchases/1000:,.0f}K", "إجمالي المشتريات")
    kpi(c3, "📈", f"{net_profit/1000:,.0f}K", "صافي الربح", delta=f"{net_profit/1000:,.0f}K" if net_profit>=0 else None)
    kpi(c4, "🏦", f"{(bank_bal+cash_bal)/1000:,.0f}K", "رصيد البنك والنقدية")
    kpi(c5, "📄", f"{today_count}", "فواتير اليوم")

    st.write("")

    # ---- Row 2: Charts ----
    col_bar, col_budget, col_costs = st.columns([2.1, 1.5, 1.4])

    month_order = ['01','02','03','04','05','06','07','08','09','10','11','12']
    month_names = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']
    df_all['شهر_م'] = df_all['التاريخ'].dt.strftime('%m')

    monthly_s = df_all[df_all["كود الدائن"]==4110].groupby('شهر_م')['المبلغ'].sum().reindex(month_order, fill_value=0)
    monthly_e = df_all[df_all["كود المدين"].isin([5120,5210,5220])].groupby('شهر_م')['المبلغ'].sum().reindex(month_order, fill_value=0)

    bar_colors = ['#1e3a5f'] * 12
    nonzero = monthly_s[monthly_s > 0]
    if len(nonzero) > 0:
        bar_colors[month_order.index(nonzero.index[-1])] = '#38bdf8'

    with col_bar:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📊 التدفقات الشهرية</div>', unsafe_allow_html=True)
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(x=month_names, y=monthly_s.values, name='مبيعات', marker_color=bar_colors, width=0.55))
        fig_bar.update_layout(
            height=250, paper_bgcolor='white', plot_bgcolor='white',
            margin=dict(l=6, r=6, t=6, b=6), showlegend=False,
            xaxis=dict(showgrid=False, tickfont=dict(size=10, color='#64748b')),
            yaxis=dict(showgrid=True, gridcolor='#f1f5f9', tickfont=dict(size=10, color='#64748b'))
        )
        st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    with col_budget:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">💳 توزيع الميزانية</div>', unsafe_allow_html=True)
        labels = ['مشتريات','رواتب','إيجار']
        values = [tot_purchases, tot_salaries, tot_rent]
        fig_d1 = go.Figure(go.Pie(labels=labels, values=values, hole=0.65,
                                   marker_colors=['#0ea5e9','#1e3a5f','#94a3b8'],
                                   textinfo='none', hoverinfo='label+percent'))
        fig_d1.update_layout(height=140, paper_bgcolor='white', margin=dict(l=0,r=0,t=0,b=0), showlegend=False,
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
        st.markdown('</div>', unsafe_allow_html=True)

    with col_costs:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📦 التكاليف</div>', unsafe_allow_html=True)
        cost_labels = ['مشتريات','رواتب','إيجار']
        cost_vals = [tot_purchases, tot_salaries, tot_rent]
        cost_colors = ['#0f172a','#0ea5e9','#38bdf8']
        fig_c = go.Figure(go.Pie(labels=cost_labels, values=cost_vals, hole=0.62,
                                  marker_colors=cost_colors, textinfo='none', hoverinfo='label+percent'))
        fig_c.update_layout(height=130, paper_bgcolor='white', margin=dict(l=0,r=0,t=0,b=0), showlegend=False,
                            annotations=[dict(text=f"<b>{tot_expenses/1000:,.1f}K</b>", x=0.5, y=0.5,
                                               font_size=12, showarrow=False, font_color='#0f172a')])
        st.plotly_chart(fig_c, use_container_width=True, config={'displayModeBar': False})
        for lbl, val, clr in zip(cost_labels, cost_vals, cost_colors):
            pct = int(val/(tot_expenses+1)*100)
            st.markdown(f"""<div style="display:flex;justify-content:space-between;font-size:0.72rem;color:#475569;margin-bottom:3px;">
                <span><span style="color:{clr};">●</span> {lbl}</span><span>{pct}% &nbsp;<b>{val/1000:,.0f}K</b></span></div>""",
                unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.write("")

    # ---- Row 3: Line chart + Alerts ----
    col_line, col_alerts = st.columns([2.4, 1.6])

    with col_line:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
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
        fig_line.update_layout(height=210, paper_bgcolor='white', plot_bgcolor='white',
                                margin=dict(l=6, r=6, t=6, b=6),
                                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10)),
                                xaxis=dict(showgrid=False, tickfont=dict(size=9)),
                                yaxis=dict(showgrid=True, gridcolor='#f1f5f9', tickfont=dict(size=9)))
        st.plotly_chart(fig_line, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    with col_alerts:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
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
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# 2. تسجيل قيد جديد
# ============================================================
elif menu == "new_entry":
    st.title("📝 تسجيل قيد محاسبي جديد")
    detailed_accounts = chart_df[chart_df["التصنيف"] == "تفصيلي"]

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
        st.dataframe(st.session_state.journal, use_container_width=True)

    with tab2:
        acc_choice = st.selectbox("اختر الحساب:", chart_df[chart_df["التصنيف"]=="تفصيلي"]["اسم الحساب"])
        df_j = st.session_state.journal
        d_df = df_j[df_j["الحساب المدين"] == acc_choice][["التاريخ", "رقم القيد", "المبلغ", "الملاحظات"]].copy()
        d_df["مدين"] = d_df["المبلغ"]; d_df["دائن"] = 0.0
        c_df = df_j[df_j["الحساب الدائن"] == acc_choice][["التاريخ", "رقم القيد", "المبلغ", "الملاحظات"]].copy()
        c_df["مدين"] = 0.0; c_df["دائن"] = c_df["المبلغ"]
        ledger = pd.concat([d_df, c_df]).sort_values(by="التاريخ")
        if not ledger.empty:
            ledger["الرصيد التراكمي"] = (ledger["مدين"] - ledger["دائن"]).cumsum()
            st.dataframe(ledger[["التاريخ", "رقم القيد", "مدين", "دائن", "الرصيد التراكمي", "الملاحظات"]], use_container_width=True)
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
    st.dataframe(pd.DataFrame(tb_data), use_container_width=True)
    st.success(f"⚖️ إجمالي الحركة المدينة: {tot_d:,.2f} EGP | إجمالي الحركة الدائنة: {tot_c:,.2f} EGP")

# ============================================================
# 5. القوائم المالية
# ============================================================
elif menu == "financials":
    st.title("📈 القوائم المالية الختامية")
    df_j = st.session_state.journal
    col_inc, col_bal = st.columns(2)
    with col_inc:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📄 قائمة الدخل</div>', unsafe_allow_html=True)
        rev = df_j[df_j["كود الدائن"] == 4110]["المبلغ"].sum()
        exp = df_j[df_j["كود المدين"].isin([5120, 5210, 5220, 5270])]["المبلغ"].sum()
        st.metric("صافي الربح / الخسارة", f"{(rev - exp):,.2f} EGP")
        st.markdown('</div>', unsafe_allow_html=True)
    with col_bal:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🏛️ الميزانية العمومية</div>', unsafe_allow_html=True)
        bank = df_j[df_j["كود المدين"] == 1120]["المبلغ"].sum() - df_j[df_j["كود الدائن"] == 1120]["المبلغ"].sum()
        receivables = df_j[df_j["كود المدين"] == 1210]["المبلغ"].sum() - df_j[df_j["كود الدائن"] == 1210]["المبلغ"].sum()
        st.metric("إجمالي الأصول المتداولة", f"{(bank + receivables):,.2f} EGP")
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# 6. شجرة الحسابات
# ============================================================
elif menu == "chart_of_accounts":
    st.title("🌳 شجرة الحسابات المعتمدة")
    st.dataframe(chart_df, use_container_width=True)

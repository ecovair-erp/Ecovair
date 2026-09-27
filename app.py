import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import plotly.graph_objects as go

# ضبط إعدادات الصفحة
st.set_page_config(
    page_title="Ecovair ERP - نظام إيكوفير للتكييف والتوريدات",
    page_icon="❄️",
    layout="wide"
)

# تصميم وتنسيق الهوية البصرية لشركة Ecovair
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .stApp header { background-color: #0f172a; }
    h1, h2, h3 { color: #0f172a; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    </style>
""", unsafe_allow_html=True)

# 1. شجرة الحسابات الكاملة لشركة Ecovair
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

# تهيئة قاعدة البيانات المؤقتة بالذاكرة
if "journal" not in st.session_state:
    st.session_state.journal = pd.DataFrame([
        {"التاريخ": "2026-01-01", "رقم القيد": "J001", "نوع العملية": "قيد افتتاحي", "كود المدين": 1120, "الحساب المدين": "الحساب البنكي", "كود الدائن": 3110, "الحساب الدائن": "رأس المال المدفوع", "المبلغ": 1000000.0, "الملاحظات": "إيداع رأس مال شركة Ecovair"},
        {"التاريخ": "2026-01-05", "رقم القيد": "J002", "نوع العملية": "فاتورة شراء", "كود المدين": 5120, "الحساب المدين": "المشتريات (معدات وخامات)", "كود الدائن": 2110, "الحساب الدائن": "موردون محليون", "المبلغ": 400000.0, "الملاحظات": "شراء وحدات تكييف وتوريدات دكت"},
        {"التاريخ": "2026-01-15", "رقم القيد": "J003", "نوع العملية": "فاتورة بيع", "كود المدين": 1210, "الحساب المدين": "عملاء محليون", "كود الدائن": 4110, "الحساب الدائن": "مبيعات محلية (توريد وتركيب)", "المبلغ": 650000.0, "الملاحظات": "مستخلص توريد وتركيب مشروع تكييف"},
        {"التاريخ": "2026-01-20", "رقم القيد": "J004", "نوع العملية": "سداد فاتورة", "كود المدين": 1120, "الحساب المدين": "الحساب البنكي", "كود الدائن": 1210, "الحساب الدائن": "عملاء محليون", "المبلغ": 500000.0, "الملاحظات": "تحصيل دفعة من العميل"},
        {"التاريخ": "2026-01-31", "رقم القيد": "J005", "نوع العملية": "اذن صرف", "كود المدين": 5210, "الحساب المدين": "الرواتب و الأجور", "كود الدائن": 1120, "الحساب الدائن": "الحساب البنكي", "المبلغ": 60000.0, "الملاحظات": "صرف رواتب مهندسي وفنيي Ecovair"}
    ])

# القائمة الجانبية
st.sidebar.image("https://img.icons8.com/color/96/air-conditioner.png", width=70)
st.sidebar.title("❄️ ECOVAIR ERP")
st.sidebar.caption("نظام الحسابات والتوريدات لشركة Ecovair")

menu = st.sidebar.radio("القائمة الرئيسية:", [
    "📊 لوحة التحكم (Dashboard)",
    "📝 تسجيل قيد يومية جديد",
    "📖 دفتر اليومية والأستاذ",
    "⚖️ ميزان المراجعة",
    "📈 القوائم المالية (Income & Balance Sheet)",
    "🌳 شجرة الحسابات"
])

# ----------------- 1. DASHBOARD -----------------
# ----------------- 1. DASHBOARD -----------------
if menu == "📊 لوحة التحكم (Dashboard)":
    st.title("❄️ لوحة التحكم المالية - شركة Ecovair")

    df_j = st.session_state.journal.copy()
    df_j['التاريخ'] = pd.to_datetime(df_j['التاريخ'])

    # ===================== فلتر الشهور =====================
    df_j['الشهر_رقم'] = df_j['التاريخ'].dt.to_period('M')
    available_months = sorted(df_j['الشهر_رقم'].unique().astype(str).tolist())
    month_options = ["كل الشهور"] + available_months

    col_filter1, col_filter2 = st.columns([1, 3])
    with col_filter1:
        selected_month = st.selectbox("🗓️ فلتر بالشهر:", month_options)

    if selected_month != "كل الشهور":
        df_j = df_j[df_j['الشهر_رقم'].astype(str) == selected_month]

    today_str = str(datetime.date.today())

    # ===================== KPIs =====================
    tot_sales      = df_j[df_j["كود الدائن"] == 4110]["المبلغ"].sum()
    tot_purchases  = df_j[df_j["كود المدين"] == 5120]["المبلغ"].sum()
    tot_salaries   = df_j[df_j["كود المدين"] == 5210]["المبلغ"].sum()
    tot_rent       = df_j[df_j["كود المدين"] == 5220]["المبلغ"].sum() if 5220 in df_j["كود المدين"].values else 0
    tot_expenses   = tot_purchases + tot_salaries + tot_rent
    net_profit     = tot_sales - tot_expenses

    bank_in        = df_j[df_j["كود المدين"] == 1120]["المبلغ"].sum()
    bank_out       = df_j[df_j["كود الدائن"] == 1120]["المبلغ"].sum()
    current_bank   = bank_in - bank_out

    cash_in        = df_j[df_j["كود المدين"] == 1110]["المبلغ"].sum()
    cash_out       = df_j[df_j["كود الدائن"] == 1110]["المبلغ"].sum()
    current_cash   = cash_in - cash_out

    today_invoices = df_j[df_j["التاريخ"].astype(str).str[:10] == today_str]
    today_count    = len(today_invoices)

    rec_due = (df_j[df_j["كود المدين"] == 1210]["المبلغ"].sum()
             - df_j[df_j["كود الدائن"] == 1210]["المبلغ"].sum())
    pay_due = (df_j[df_j["كود الدائن"] == 2110]["المبلغ"].sum()
             - df_j[df_j["كود المدين"] == 2110]["المبلغ"].sum())

    # ===================== CSS للكروت =====================
    st.markdown("""
    <style>
    .kpi-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%);
        border-radius: 16px;
        padding: 20px 16px;
        text-align: center;
        color: white;
        margin-bottom: 8px;
        box-shadow: 0 4px 15px rgba(15,23,42,0.25);
    }
    .kpi-card .kpi-icon  { font-size: 1.6rem; margin-bottom: 4px; }
    .kpi-card .kpi-value { font-size: 1.45rem; font-weight: 700; color: #38bdf8; }
    .kpi-card .kpi-label { font-size: 0.78rem; color: #94a3b8; margin-top: 3px; }
    .kpi-card .kpi-delta { font-size: 0.75rem; color: #4ade80; margin-top: 4px; }

    .section-card {
        background: white;
        border-radius: 16px;
        padding: 18px 16px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.07);
        margin-bottom: 12px;
    }
    .section-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 12px;
    }

    .alert-card {
        border-radius: 12px;
        padding: 12px 14px;
        margin-bottom: 8px;
        font-size: 0.85rem;
        font-weight: 500;
    }
    .alert-warn  { background: #fef3c7; color: #92400e; border-left: 4px solid #f59e0b; }
    .alert-info  { background: #dbeafe; color: #1e40af; border-left: 4px solid #3b82f6; }
    .alert-ok    { background: #dcfce7; color: #166534; border-left: 4px solid #22c55e; }

    .progress-bar-bg {
        background: #e2e8f0;
        border-radius: 6px;
        height: 8px;
        margin: 4px 0 10px 0;
    }
    .progress-bar-fill {
        height: 8px;
        border-radius: 6px;
        background: linear-gradient(90deg, #38bdf8, #0ea5e9);
    }
    </style>
    """, unsafe_allow_html=True)

    # ===================== ROW 1: KPI Cards =====================
    c1, c2, c3, c4, c5 = st.columns(5)

    def kpi(col, icon, value, label, delta=None):
        delta_html = f'<div class="kpi-delta">▲ {delta}</div>' if delta else ""
        col.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">{icon}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-label">{label}</div>
            {delta_html}
        </div>""", unsafe_allow_html=True)

    kpi(c1, "💰", f"{tot_sales/1000:.0f}K ج.م",  "إجمالي المبيعات")
    kpi(c2, "🛒", f"{tot_purchases/1000:.0f}K ج.م","إجمالي المشتريات")
    kpi(c3, "📈", f"{net_profit/1000:.0f}K ج.م",  "صافي الربح",
        delta=f"+{net_profit/1000:.0f}K" if net_profit > 0 else None)
    kpi(c4, "🏦", f"{(current_bank+current_cash)/1000:.0f}K ج.م","رصيد البنك والنقدية")
    kpi(c5, "📄", f"{today_count}", "فواتير اليوم")

    st.markdown("<br>", unsafe_allow_html=True)

    # ===================== ROW 2: Charts =====================
    col_left, col_mid, col_right = st.columns([2.2, 1.6, 1.4])

    # --- Inflow Bar Chart (زي الصورة) ---
    with col_left:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📊 التدفقات الشهرية (مبيعات / مصروفات)</div>', unsafe_allow_html=True)

        df_all = st.session_state.journal.copy()
        df_all['التاريخ'] = pd.to_datetime(df_all['التاريخ'])
        df_all['الشهر'] = df_all['التاريخ'].dt.strftime('%b')
        month_order = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        df_all['الشهر'] = pd.Categorical(df_all['الشهر'], categories=month_order, ordered=True)

        monthly_s = df_all[df_all["كود الدائن"]==4110].groupby('الشهر',observed=True)['المبلغ'].sum().reindex(month_order, fill_value=0)
        monthly_e = df_all[df_all["كود المدين"].isin([5120,5210,5220])].groupby('الشهر',observed=True)['المبلغ'].sum().reindex(month_order, fill_value=0)

        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            x=month_order, y=monthly_s.values, name='مبيعات',
            marker_color=['#38bdf8' if m == (df_all['الشهر'].max() if len(df_all)>0 else 'Jan') else '#1e3a5f' for m in month_order],
            width=0.4
        ))
        fig_bar.add_trace(go.Bar(
            x=month_order, y=monthly_e.values, name='مصروفات',
            marker_color='#94a3b8', width=0.4, opacity=0.6
        ))
        fig_bar.update_layout(
            barmode='group', height=240, paper_bgcolor='white', plot_bgcolor='white',
            margin=dict(l=10, r=10, t=10, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="right", x=1, font=dict(size=11)),
            xaxis=dict(showgrid=False, tickfont=dict(size=10)),
            yaxis=dict(showgrid=True, gridcolor='#f1f5f9', tickfont=dict(size=10))
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- Budget Donut (زي الصورة) ---
    with col_mid:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">💳 الميزانية والتوزيع</div>', unsafe_allow_html=True)

        labels  = ['مشتريات', 'رواتب', 'إيجار', 'رصيد']
        values  = [tot_purchases, tot_salaries, tot_rent, max(current_bank+current_cash, 0)]
        colors  = ['#0ea5e9', '#1e3a5f', '#38bdf8', '#94a3b8']

        fig_donut = go.Figure(go.Pie(
            labels=labels, values=values,
            hole=0.62, marker_colors=colors,
            textinfo='percent', textfont_size=11,
            hoverinfo='label+value'
        ))
        fig_donut.update_layout(
            height=200, paper_bgcolor='white',
            margin=dict(l=0, r=0, t=10, b=0),
            showlegend=False,
            annotations=[dict(text=f"<b>{(current_bank+current_cash)/1000:.1f}K</b><br>رصيد",
                              x=0.5, y=0.5, font_size=13, showarrow=False, font_color='#0f172a')]
        )
        st.plotly_chart(fig_donut, use_container_width=True)

        # Progress bars
        inflow_pct  = min(int(tot_sales/(tot_sales+tot_expenses+1)*100), 100)
        outflow_pct = 100 - inflow_pct
        st.markdown(f"""
        <div style="font-size:0.78rem; color:#64748b; margin-bottom:2px;">
            تدفق داخل <span style="float:left;font-weight:700;color:#0ea5e9;">{inflow_pct}%</span>
        </div>
        <div class="progress-bar-bg"><div class="progress-bar-fill" style="width:{inflow_pct}%"></div></div>
        <div style="font-size:0.78rem; color:#64748b; margin-bottom:2px;">
            تدفق خارج <span style="float:left;font-weight:700;color:#94a3b8;">{outflow_pct}%</span>
        </div>
        <div class="progress-bar-bg"><div class="progress-bar-fill" style="width:{outflow_pct}%;background:linear-gradient(90deg,#94a3b8,#64748b);"></div></div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- Costs Donut (زي الصورة) ---
    with col_right:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📦 التكاليف</div>', unsafe_allow_html=True)

        cost_labels = ['مشتريات', 'رواتب', 'إيجار']
        cost_vals   = [tot_purchases, tot_salaries, tot_rent]
        cost_colors = ['#0f172a', '#0ea5e9', '#38bdf8']

        fig_cost = go.Figure(go.Pie(
            labels=cost_labels, values=cost_vals,
            hole=0.6, marker_colors=cost_colors,
            textinfo='none', hoverinfo='label+percent'
        ))
        fig_cost.update_layout(
            height=160, paper_bgcolor='white',
            margin=dict(l=0, r=0, t=10, b=0),
            showlegend=False,
            annotations=[dict(text=f"<b>{tot_expenses/1000:.1f}K</b>",
                              x=0.5, y=0.5, font_size=13, showarrow=False, font_color='#0f172a')]
        )
        st.plotly_chart(fig_cost, use_container_width=True)

        for lbl, val, clr in zip(cost_labels, cost_vals, cost_colors):
            pct = int(val / (tot_expenses+1) * 100)
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;font-size:0.75rem;margin-bottom:4px;">
                <span><span style="color:{clr};font-size:0.9rem;">●</span> {lbl}</span>
                <span style="color:#64748b;">{pct}% &nbsp; <b>{val/1000:.0f}K</b></span>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ===================== ROW 3: Line Chart + Alerts =====================
    col_line, col_alerts = st.columns([2.5, 1.5])

    with col_line:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📈 منحنى مقارنة التكاليف والإيرادات</div>', unsafe_allow_html=True)

        df_all2 = st.session_state.journal.copy()
        df_all2['التاريخ'] = pd.to_datetime(df_all2['التاريخ'])
        df_all2_sorted = df_all2.sort_values('التاريخ').copy()
        df_all2_sorted['مبيعات_تراكمي']   = df_all2_sorted['المبلغ'].where(df_all2_sorted['كود الدائن']==4110, 0).cumsum()
        df_all2_sorted['مصروفات_تراكمي'] = df_all2_sorted['المبلغ'].where(df_all2_sorted['كود المدين'].isin([5120,5210,5220]), 0).cumsum()

        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=df_all2_sorted['التاريخ'], y=df_all2_sorted['مبيعات_تراكمي'],
            name='إيرادات', mode='lines', fill='tozeroy',
            line=dict(color='#0ea5e9', width=2.5),
            fillcolor='rgba(14,165,233,0.08)'
        ))
        fig_line.add_trace(go.Scatter(
            x=df_all2_sorted['التاريخ'], y=df_all2_sorted['مصروفات_تراكمي'],
            name='مصروفات', mode='lines', fill='tozeroy',
            line=dict(color='#94a3b8', width=2, dash='dot'),
            fillcolor='rgba(148,163,184,0.06)'
        ))
        fig_line.update_layout(
            height=220, paper_bgcolor='white', plot_bgcolor='white',
            margin=dict(l=10, r=10, t=10, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="right", x=1, font=dict(size=11)),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='#f1f5f9')
        )
        st.plotly_chart(fig_line, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_alerts:
        st.markdown('<div class="section-card" style="height:100%">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🔔 التنبيهات</div>', unsafe_allow_html=True)

        if rec_due > 0:
            st.markdown(f'<div class="alert-card alert-warn">⚠️ مستحقات عملاء غير محصلة<br><b>{rec_due:,.0f} ج.م</b></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-card alert-ok">✅ جميع مستحقات العملاء محصلة</div>', unsafe_allow_html=True)

        if pay_due > 0:
            st.markdown(f'<div class="alert-card alert-info">📌 التزامات موردين مستحقة<br><b>{pay_due:,.0f} ج.م</b></div>', unsafe_allow_html=True)

        if net_profit > 0:
            st.markdown(f'<div class="alert-card alert-ok">📈 الشركة رابحة<br><b>+{net_profit:,.0f} ج.م</b></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="alert-card alert-warn">📉 خسارة صافية<br><b>{net_profit:,.0f} ج.م</b></div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
# ----------------- 2. RECORD ENTRY -----------------
elif menu == "📝 تسجيل قيد يومية جديد":
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
        
        notes = st.text_input("البيان / تفاصيل العملية (اسم المشروع / العميل / المورد)")
        btn = st.form_submit_button("💾 حفظ القيد المحاسبي")

        if btn:
            if debit_acc == credit_acc:
                st.error("لا يمكن أن يكون الحساب المدين والدائن نفس الحساب!")
            else:
                d_code = detailed_accounts[detailed_accounts["اسم الحساب"] == debit_acc]["الكود"].values[0]
                c_code = detailed_accounts[detailed_accounts["اسم الحساب"] == credit_acc]["الكود"].values[0]
                
                new_row = {
                    "التاريخ": str(entry_date),
                    "رقم القيد": entry_num,
                    "نوع العملية": op_type,
                    "كود المدين": d_code,
                    "الحساب المدين": debit_acc,
                    "كود الدائن": c_code,
                    "الحساب الدائن": credit_acc,
                    "المبلغ": float(amount),
                    "الملاحظات": notes
                }
                st.session_state.journal = pd.concat([st.session_state.journal, pd.DataFrame([new_row])], ignore_index=True)
                st.success(f"✅ تم حفظ القيد {entry_num} بنجاح!")

# ----------------- 3. JOURNAL & LEDGER -----------------
elif menu == "📖 دفتر اليومية والأستاذ":
    st.title("📖 دفتر اليومية العامة وحسابات الأستاذ")
    tab1, tab2 = st.tabs(["اليومية العامة", "كشف حساب أستاذ تفصيلي"])
    
    with tab1:
        st.dataframe(st.session_state.journal, use_container_width=True)
        
    with tab2:
        acc_choice = st.selectbox("اختر الحساب لعرض حركة كشف الحساب:", chart_df[chart_df["التصنيف"]=="تفصيلي"]["اسم الحساب"])
        df_j = st.session_state.journal
        
        d_df = df_j[df_j["الحساب المدين"] == acc_choice][["التاريخ", "رقم القيد", "المبلغ", "الملاحظات"]].copy()
        d_df["مدين"] = d_df["المبلغ"]
        d_df["دائن"] = 0.0
        
        c_df = df_j[df_j["الحساب الدائن"] == acc_choice][["التاريخ", "رقم القيد", "المبلغ", "الملاحظات"]].copy()
        c_df["مدين"] = 0.0
        c_df["دائن"] = c_df["المبلغ"]
        
        ledger = pd.concat([d_df, c_df]).sort_values(by="التاريخ")
        if not ledger.empty:
            ledger["الرصيد التراكمي"] = (ledger["مدين"] - ledger["دائن"]).cumsum()
            st.dataframe(ledger[["التاريخ", "رقم القيد", "مدين", "دائن", "الرصيد التراكمي", "الملاحظات"]], use_container_width=True)
        else:
            st.info("لا توجد حرّكات مسجلة على هذا الحساب حتى الآن.")

# ----------------- 4. TRIAL BALANCE -----------------
elif menu == "⚖️ ميزان المراجعة":
    st.title("⚖️ ميزان المراجعة بالإجماليات والأرصدة")
    df_j = st.session_state.journal
    tb_data = []
    tot_d, tot_c = 0, 0
    
    for _, row in chart_df[chart_df["التصنيف"] == "تفصيلي"].iterrows():
        code = row["الكود"]
        name = row["اسم الحساب"]
        acc_type = row["النوع"]
        
        debits = df_j[df_j["كود المدين"] == code]["المبلغ"].sum()
        credits = df_j[df_j["كود الدائن"] == code]["المبلغ"].sum()
        balance = debits - credits
        
        if debits > 0 or credits > 0:
            tb_data.append({
                "الكود": code, "اسم الحساب": name, "النوع": acc_type,
                "إجمالي المدين": debits, "إجمالي الدائن": credits, "الرصيد الصافي": balance
            })
            tot_d += debits
            tot_c += credits
            
    st.dataframe(pd.DataFrame(tb_data), use_container_width=True)
    st.success(f"⚖️ إجمالي الحركة المدينة: {tot_d:,.2f} EGP | إجمالي الحركة الدائنة: {tot_c:,.2f} EGP")

# ----------------- 5. FINANCIAL STATEMENTS -----------------
elif menu == "📈 القوائم المالية (Income & Balance Sheet)":
    st.title("📈 القوائم المالية الختامية لشركة Ecovair")
    df_j = st.session_state.journal
    col_inc, col_bal = st.columns(2)
    
    with col_inc:
        st.subheader("📄 قائمة الدخل")
        rev = df_j[df_j["كود الدائن"] == 4110]["المبلغ"].sum()
        exp = df_j[df_j["كود المدين"].isin([5120, 5210, 5220, 5270])]["المبلغ"].sum()
        st.metric("صافي الربح / الخسارة", f"{(rev - exp):,.2f} EGP")

    with col_bal:
        st.subheader("🏛️ الميزانية العمومية")
        bank = df_j[df_j["كود المدين"] == 1120]["المبلغ"].sum() - df_j[df_j["كود الدائن"] == 1120]["المبلغ"].sum()
        receivables = df_j[df_j["كود المدين"] == 1210]["المبلغ"].sum() - df_j[df_j["كود الدائن"] == 1210]["المبلغ"].sum()
        st.metric("إجمالي الأصول المتداولة", f"{(bank + receivables):,.2f} EGP")

# ----------------- 6. CHART OF ACCOUNTS -----------------
elif menu == "🌳 شجرة الحسابات":
    st.title("🌳 شجرة الحسابات المعتمدة - Ecovair")
    st.dataframe(chart_df, use_container_width=True)

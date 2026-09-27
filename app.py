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
if menu == "📊 لوحة التحكم (Dashboard)":
    st.title("❄️ لوحة التحكم المالية - شركة Ecovair")
    st.caption("متابعة حية للتدفقات المالية، المبيعات، الحسابات والإشعارات")

    df_j = st.session_state.journal.copy()
    df_j['التاريخ'] = pd.to_datetime(df_j['التاريخ'])
    today_str = str(datetime.date.today())

    # حساب المؤشرات الرئيسية (KPIs)
    tot_sales = df_j[df_j["كود الدائن"] == 4110]["المبلغ"].sum()
    tot_purchases = df_j[df_j["كود المدين"] == 5120]["المبلغ"].sum()
    tot_salaries = df_j[df_j["كود المدين"] == 5210]["المبلغ"].sum()
    tot_rent = df_j[df_j["كود المدين"] == 5220]["المبلغ"].sum() if 5220 in df_j["كود المدين"].values else 0
    
    tot_expenses = tot_purchases + tot_salaries + tot_rent
    net_profit = tot_sales - tot_expenses
    
    bank_in = df_j[df_j["كود المدين"] == 1120]["المبلغ"].sum()
    bank_out = df_j[df_j["كود الدائن"] == 1120]["المبلغ"].sum()
    current_bank = bank_in - bank_out

    cash_in = df_j[df_j["كود المدين"] == 1110]["المبلغ"].sum()
    cash_out = df_j[df_j["كود الدائن"] == 1110]["المبلغ"].sum()
    current_cash = cash_in - cash_out
    
    today_invoices = df_j[df_j["التاريخ"].astype(str) == today_str]
    today_count = len(today_invoices)

    # الصف الأول: البطاقات
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("💰 إجمالي المبيعات", f"{tot_sales:,.0f} ج.م")
    m2.metric("🛒 إجمالي المشتريات", f"{tot_purchases:,.0f} ج.م")
    m3.metric("📈 صافي الربح", f"{net_profit:,.0f} ج.م", delta=f"{net_profit:,.0f}")
    m4.metric("🏦 رصيد البنك والنقدية", f"{(current_bank + current_cash):,.0f} ج.م")
    m5.metric("📄 فواتير اليوم", f"{today_count} فاتورة")

    st.markdown("---")

    # الصف الثاني: الرسوم البيانية
    col_chart1, col_chart2 = st.columns([2, 1])

    with col_chart1:
        st.subheader("📊 التدفقات المالية (المبيعات مقابل المصروفات)")
        df_j['الشهر'] = df_j['التاريخ'].dt.strftime('%Y-%m')
        monthly_sales = df_j[df_j["كود الدائن"] == 4110].groupby('الشهر')['المبلغ'].sum().reset_index(name='المبيعات')
        monthly_exp = df_j[df_j["كود المدين"].isin([5120, 5210, 5220])].groupby('الشهر')['المبلغ'].sum().reset_index(name='المصروفات')
        merged_monthly = pd.merge(monthly_sales, monthly_exp, on='الشهر', how='outer').fillna(0)
        
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(x=merged_monthly['الشهر'], y=merged_monthly['المبيعات'], name='المبيعات', marker_color='#10b981'))
        fig_bar.add_trace(go.Bar(x=merged_monthly['الشهر'], y=merged_monthly['المصروفات'], name='المصروفات والمشتريات', marker_color='#ef4444'))
        fig_bar.update_layout(barmode='group', height=320, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_chart2:
        st.subheader("🍩 توزيع الهيكل المالي والتكاليف")
        expense_labels = ['مشتريات خامات ومعدات', 'رواتب وأجور', 'إيجار وتشغيل']
        expense_values = [tot_purchases, tot_salaries, tot_rent]
        fig_donut = px.pie(names=expense_labels, values=expense_values, hole=0.6, color_discrete_sequence=['#3b82f6', '#8b5cf6', '#f59e0b'])
        fig_donut.update_layout(height=320, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig_donut, use_container_width=True)

    st.markdown("---")

    # الصف الثالث: منحنى النمو والتنبيهات
    col_bottom1, col_bottom2 = st.columns([2, 1])

    with col_bottom1:
        st.subheader("📈 منحنى نمو الأرباح التراكمي")
        df_j_sorted = df_j.sort_values('التاريخ').copy()
        df_j_sorted['ربح_العملية'] = 0.0
        df_j_sorted.loc[df_j_sorted['كود الدائن'] == 4110, 'ربح_العملية'] = df_j_sorted['المبلغ']
        df_j_sorted.loc[df_j_sorted['كود المدين'].isin([5120, 5210, 5220]), 'ربح_العملية'] = -df_j_sorted['المبلغ']
        df_j_sorted['الربح_التراكمي'] = df_j_sorted['ربح_العملية'].cumsum()
        
        fig_line = px.line(df_j_sorted, x='التاريخ', y='الربح_التراكمي', markers=True)
        fig_line.update_traces(line_color='#2563eb', line_width=3)
        fig_line.update_layout(height=260, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_line, use_container_width=True)

    with col_bottom2:
        st.subheader("🔔 مركز الإشعارات والتنبيهات")
        rec_due = df_j[df_j["كود المدين"] == 1210]["المبلغ"].sum() - df_j[df_j["كود الدائن"] == 1210]["المبلغ"].sum()
        pay_due = df_j[df_j["كود الدائن"] == 2110]["المبلغ"].sum() - df_j[df_j["كود المدين"] == 2110]["المبلغ"].sum()

        if rec_due > 0:
            st.warning(f"⚠️ **مستحقات عملاء:** يوجد مبلغ **{rec_due:,.0f} ج.م** آجل لدى العملاء لم يتم تحصيله.")
        else:
            st.success("✅ جميع مستحقات العملاء محصلة بالكامل.")

        if pay_due > 0:
            st.info(f"📌 **التزامات موردين:** عليك سداد **{pay_due:,.0f} ج.م** للموردين.")

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

import streamlit as st
import pandas as pd
import datetime

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
    .metric-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
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
    st.title("❄️ شركة Ecovair للتكييف والتوريدات العمومية")
    st.subheader("الملخص المالي والتحليلي للشركة")
    
    df_j = st.session_state.journal
    revenues = df_j[df_j["كود الدائن"] == 4110]["المبلغ"].sum()
    purchases = df_j[df_j["كود المدين"] == 5120]["المبلغ"].sum()
    salaries = df_j[df_j["كود المدين"] == 5210]["المبلغ"].sum()
    total_expenses = purchases + salaries
    net_profit = revenues - total_expenses

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("إجمالي الإيرادات (المبيعات)", f"{revenues:,.2f} EGP")
    c2.metric("إجمالي المشتريات والمصروفات", f"{total_expenses:,.2f} EGP")
    c3.metric("صافي الربح الحالي", f"{net_profit:,.2f} EGP", delta=f"{net_profit:,.0f}")
    c4.metric("عدد العمليات المسجلة", len(df_j))

    st.markdown("---")
    st.subheader("📋 أحدث العمليات المالية المسجلة")
    st.dataframe(df_j.tail(5), use_container_width=True)

# ----------------- 2. RECORD ENTRY -----------------
elif menu == "📝 تسجيل قيد يومية جديد":
    st.title("📝 تسجيل قيد محاسبي جديد")
    st.info("نظام القيد المزدوج التلقائي لشركة Ecovair")

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
                st.success(f"✅ تم حفظ القيد {entry_num} بنجاح وتحديث كافة القوائم المالية!")

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
                "الكود": code,
                "اسم الحساب": name,
                "النوع": acc_type,
                "إجمالي المدين": debits,
                "إجمالي الدائن": credits,
                "الرصيد الصافي": balance
            })
            tot_d += debits
            tot_c += credits
            
    tb_df = pd.DataFrame(tb_data)
    st.dataframe(tb_df, use_container_width=True)
    st.success(f"⚖️ إجمالي الحركة المدينة: {tot_d:,.2f} EGP | إجمالي الحركة الدائنة: {tot_c:,.2f} EGP (الميزان متزن تلقائياً)")

# ----------------- 5. FINANCIAL STATEMENTS -----------------
elif menu == "📈 القوائم المالية (Income & Balance Sheet)":
    st.title("📈 القوائم المالية الختامية لشركة Ecovair")
    
    df_j = st.session_state.journal
    
    col_inc, col_bal = st.columns(2)
    
    with col_inc:
        st.subheader("📄 قائمة الدخل (Income Statement)")
        rev = df_j[df_j["كود الدائن"] == 4110]["المبلغ"].sum()
        exp = df_j[df_j["كود المدين"].isin([5120, 5210, 5220, 5270])]["المبلغ"].sum()
        net = rev - exp
        
        st.write(f"**إجمالي الإيرادات والمبيعات:** {rev:,.2f} EGP")
        st.write(f"**تكلفة المشتريات والمصروفات:** {exp:,.2f} EGP")
        st.markdown("---")
        st.metric("صافي الربح / الخسارة", f"{net:,.2f} EGP")

    with col_bal:
        st.subheader("🏛️ الميزانية العمومية (Balance Sheet)")
        
        bank = df_j[df_j["كود المدين"] == 1120]["المبلغ"].sum() - df_j[df_j["كود الدائن"] == 1120]["المبلغ"].sum()
        receivables = df_j[df_j["كود المدين"] == 1210]["المبلغ"].sum() - df_j[df_j["كود الدائن"] == 1210]["المبلغ"].sum()
        total_assets = bank + receivables
        
        payables = df_j[df_j["كود الدائن"] == 2110]["المبلغ"].sum() - df_j[df_j["كود المدين"] == 2110]["المبلغ"].sum()
        capital = df_j[df_j["كود الدائن"] == 3110]["المبلغ"].sum()
        total_liab_equity = payables + capital + net
        
        st.write(f"**الأصول المتداولة (البنك والعملاء):** {total_assets:,.2f} EGP")
        st.write(f"**الالتزامات (الموردون):** {payables:,.2f} EGP")
        st.write(f"**حقوق الملكية (رأس المال + أرباح الفترة):** {capital + net:,.2f} EGP")
        st.markdown("---")
        st.write(f"**إجمالي الأصول:** {total_assets:,.2f} EGP")
        st.write(f"**إجمالي الالتزامات وحقوق الملكية:** {total_liab_equity:,.2f} EGP")
        
        if abs(total_assets - total_liab_equity) < 0.01:
            st.success("✅ الميزانية متزنة تماماً (الأصول = الالتزامات + حقوق الملكية)")

# ----------------- 6. CHART OF ACCOUNTS -----------------
elif menu == "🌳 شجرة الحسابات":
    st.title("🌳 شجرة الحسابات المعتمدة - Ecovair")
    st.dataframe(chart_df, use_container_width=True)

import streamlit as st
import pandas as pd
import sqlite3
import os

# ─── إعداد الصفحة ───────────────────────────────────────────────
st.set_page_config(
    page_title="النظام المحاسبي",
    page_icon="📒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CSS مخصص ────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');

* { font-family: 'Cairo', sans-serif !important; direction: rtl; }

.stApp { background: #f0f4f8; }

/* Header */
.main-header {
    background: linear-gradient(135deg, #1a3a5c 0%, #2d6a9f 100%);
    color: white;
    padding: 1.5rem 2rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
    text-align: center;
    box-shadow: 0 4px 20px rgba(26,58,92,0.3);
}
.main-header h1 { font-size: 2rem; font-weight: 900; margin: 0; }
.main-header p { opacity: 0.85; margin: 0.3rem 0 0; font-size: 1rem; }

/* Cards */
.stat-card {
    background: white;
    border-radius: 10px;
    padding: 1.2rem 1.5rem;
    text-align: center;
    box-shadow: 0 2px 10px rgba(0,0,0,0.07);
    border-right: 4px solid #2d6a9f;
}
.stat-card .num { font-size: 2rem; font-weight: 900; color: #1a3a5c; }
.stat-card .lbl { color: #666; font-size: 0.9rem; }

/* Table */
.dataframe thead th {
    background: #1a3a5c !important;
    color: white !important;
    text-align: right !important;
}
.dataframe tbody tr:hover { background: #e8f0fe !important; }

/* Buttons */
.stButton > button {
    background: #2d6a9f;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1.5rem;
    font-family: 'Cairo', sans-serif;
    font-weight: 600;
    transition: all 0.2s;
}
.stButton > button:hover { background: #1a3a5c; transform: translateY(-1px); }

/* Level badges */
.level-1 { background:#1a3a5c; color:white; padding:2px 10px; border-radius:12px; font-size:0.8rem; }
.level-2 { background:#2d6a9f; color:white; padding:2px 10px; border-radius:12px; font-size:0.8rem; }
.level-3 { background:#3d8bcd; color:white; padding:2px 10px; border-radius:12px; font-size:0.8rem; }
.level-4 { background:#6aabde; color:white; padding:2px 10px; border-radius:12px; font-size:0.8rem; }

/* Sidebar */
[data-testid="stSidebar"] { background: #1a3a5c !important; }
[data-testid="stSidebar"] * { color: white !important; }
[data-testid="stSidebar"] .stSelectbox label { color: #adc8e6 !important; }

/* Success/Error */
.stSuccess { border-right: 4px solid #28a745; }
.stError   { border-right: 4px solid #dc3545; }
</style>
""", unsafe_allow_html=True)


# ─── قاعدة البيانات ───────────────────────────────────────────────
DB_PATH = "accounting.db"

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    """إنشاء الجدول إذا لم يكن موجوداً"""
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chart_of_accounts (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            level1   TEXT,
            level2   TEXT,
            level3   TEXT,
            level4   TEXT,
            level5   TEXT,
            level6   TEXT,
            code     TEXT UNIQUE NOT NULL,
            name     TEXT NOT NULL,
            acc_level INTEGER  -- المستوى الفعلي للحساب (1-6)
        )
    """)
    conn.commit()
    conn.close()

def import_from_excel(path: str):
    """استيراد شجرة الحسابات من Excel إلى SQLite"""
    conn = get_conn()
    count = conn.execute("SELECT COUNT(*) FROM chart_of_accounts").fetchone()[0]
    if count > 0:
        conn.close()
        return  # تم الاستيراد من قبل

    df = pd.read_excel(path, engine="openpyxl")
    df.columns = ["level1","level2","level3","level4","level5","level6","code"]

    rows = []
    for _, r in df.iterrows():
        levels = [str(r[f"level{i}"]).strip() if pd.notna(r[f"level{i}"]) and str(r[f"level{i}"]).strip() else ""
                  for i in range(1,7)]
        # الاسم = آخر مستوى غير فارغ
        name = next((levels[i] for i in range(5,-1,-1) if levels[i]), "")
        # المستوى الفعلي
        acc_level = sum(1 for l in levels if l)
        code = str(r["code"]).strip() if pd.notna(r["code"]) else ""
        if not code or not name:
            continue
        rows.append((*levels, code, name, acc_level))

    conn.executemany(
        "INSERT OR IGNORE INTO chart_of_accounts (level1,level2,level3,level4,level5,level6,code,name,acc_level) VALUES (?,?,?,?,?,?,?,?,?)",
        rows
    )
    conn.commit()
    conn.close()

def load_accounts(search="", level1_filter="الكل", acc_level_filter=0):
    conn = get_conn()
    q = "SELECT * FROM chart_of_accounts WHERE 1=1"
    params = []
    if search:
        q += " AND (name LIKE ? OR code LIKE ?)"
        params += [f"%{search}%", f"%{search}%"]
    if level1_filter != "الكل":
        q += " AND level1 = ?"
        params.append(level1_filter)
    if acc_level_filter > 0:
        q += " AND acc_level = ?"
        params.append(acc_level_filter)
    q += " ORDER BY code"
    df = pd.read_sql(q, conn, params=params)
    conn.close()
    return df

def add_account(level1, level2, level3, level4, level5, level6, code, name, acc_level):
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO chart_of_accounts (level1,level2,level3,level4,level5,level6,code,name,acc_level) VALUES (?,?,?,?,?,?,?,?,?)",
            (level1, level2, level3, level4, level5, level6, code, name, acc_level)
        )
        conn.commit()
        return True, "✅ تم إضافة الحساب بنجاح"
    except sqlite3.IntegrityError:
        return False, "❌ الكود موجود بالفعل"
    finally:
        conn.close()

def update_account(acc_id, level1, level2, level3, level4, level5, level6, code, name, acc_level):
    conn = get_conn()
    try:
        conn.execute(
            "UPDATE chart_of_accounts SET level1=?,level2=?,level3=?,level4=?,level5=?,level6=?,code=?,name=?,acc_level=? WHERE id=?",
            (level1, level2, level3, level4, level5, level6, code, name, acc_level, acc_id)
        )
        conn.commit()
        return True, "✅ تم التعديل بنجاح"
    except sqlite3.IntegrityError:
        return False, "❌ الكود مستخدم بالفعل"
    finally:
        conn.close()

def delete_account(acc_id):
    conn = get_conn()
    conn.execute("DELETE FROM chart_of_accounts WHERE id=?", (acc_id,))
    conn.commit()
    conn.close()

def get_level1_options():
    conn = get_conn()
    opts = pd.read_sql("SELECT DISTINCT level1 FROM chart_of_accounts WHERE level1 != '' ORDER BY level1", conn)
    conn.close()
    return ["الكل"] + opts["level1"].tolist()

def get_stats():
    conn = get_conn()
    total = conn.execute("SELECT COUNT(*) FROM chart_of_accounts").fetchone()[0]
    by_level1 = pd.read_sql(
        "SELECT level1, COUNT(*) as cnt FROM chart_of_accounts WHERE level1!='' GROUP BY level1",
        conn
    )
    conn.close()
    return total, by_level1


# ─── تهيئة ────────────────────────────────────────────────────────
init_db()
excel_path = "شجرة_الحسابات_كاملة.xlsx"
if os.path.exists(excel_path):
    import_from_excel(excel_path)


# ─── الشريط الجانبي ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📒 النظام المحاسبي")
    st.markdown("---")
    page = st.radio(
        "القائمة",
        ["🏠 الرئيسية", "📋 شجرة الحسابات", "➕ إضافة حساب", "✏️ تعديل / حذف"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    total, _ = get_stats()
    st.markdown(f"**إجمالي الحسابات:** {total:,}")


# ─── الصفحات ──────────────────────────────────────────────────────

# ════ الرئيسية ════
if page == "🏠 الرئيسية":
    st.markdown("""
    <div class="main-header">
        <h1>📒 النظام المحاسبي</h1>
        <p>إدارة شجرة الحسابات ودفتر الأستاذ</p>
    </div>
    """, unsafe_allow_html=True)

    total, by_level1 = get_stats()

    cols = st.columns(len(by_level1) + 1)
    with cols[0]:
        st.markdown(f"""
        <div class="stat-card">
            <div class="num">{total:,}</div>
            <div class="lbl">إجمالي الحسابات</div>
        </div>""", unsafe_allow_html=True)

    for i, row in by_level1.iterrows():
        if i+1 < len(cols):
            with cols[i+1]:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="num">{row['cnt']:,}</div>
                    <div class="lbl">{row['level1']}</div>
                </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.info("📌 استخدم القائمة الجانبية للتنقل بين الأقسام")


# ════ شجرة الحسابات ════
elif page == "📋 شجرة الحسابات":
    st.markdown("## 📋 شجرة الحسابات")

    col1, col2, col3 = st.columns([3, 2, 1])
    with col1:
        search = st.text_input("🔍 بحث بالاسم أو الكود", placeholder="اكتب هنا...")
    with col2:
        level1_opts = get_level1_options()
        level1_filter = st.selectbox("تصفية بالقسم الرئيسي", level1_opts)
    with col3:
        acc_level_filter = st.selectbox("المستوى", [0,1,2,3,4,5,6],
                                         format_func=lambda x: "الكل" if x==0 else f"مستوى {x}")

    df = load_accounts(search, level1_filter, acc_level_filter)

    st.markdown(f"**النتائج: {len(df):,} حساب**")

    if df.empty:
        st.warning("لا توجد نتائج")
    else:
        display = df[["code","name","level1","level2","level3","acc_level"]].copy()
        display.columns = ["الكود","اسم الحساب","المستوى 1","المستوى 2","المستوى 3","المستوى"]
        display["المستوى"] = display["المستوى"].apply(lambda x: f"مستوى {x}")
        st.dataframe(
            display,
            use_container_width=True,
            hide_index=True,
            height=500
        )

        csv = df.to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            "⬇️ تحميل Excel",
            data=csv,
            file_name="شجرة_الحسابات.csv",
            mime="text/csv"
        )


# ════ إضافة حساب ════
elif page == "➕ إضافة حساب":
    st.markdown("## ➕ إضافة حساب جديد")

    with st.form("add_form"):
        col1, col2 = st.columns(2)
        with col1:
            code = st.text_input("كود الحساب *", placeholder="مثال: 1202010")
            name = st.text_input("اسم الحساب *", placeholder="مثال: بنك القاهرة")
            acc_level = st.selectbox("مستوى الحساب *", [1,2,3,4,5,6],
                                      format_func=lambda x: f"مستوى {x}")
        with col2:
            level1 = st.text_input("المستوى 1", placeholder="مثال: الأصول")
            level2 = st.text_input("المستوى 2", placeholder="مثال: الأصول المتداولة")
            level3 = st.text_input("المستوى 3", placeholder="مثال: البنك")

        col3, col4 = st.columns(2)
        with col3:
            level4 = st.text_input("المستوى 4")
            level5 = st.text_input("المستوى 5")
        with col4:
            level6 = st.text_input("المستوى 6")

        submitted = st.form_submit_button("💾 حفظ الحساب", use_container_width=True)
        if submitted:
            if not code or not name:
                st.error("الكود والاسم مطلوبان")
            else:
                ok, msg = add_account(level1, level2, level3, level4, level5, level6,
                                       code, name, acc_level)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)


# ════ تعديل / حذف ════
elif page == "✏️ تعديل / حذف":
    st.markdown("## ✏️ تعديل أو حذف حساب")

    search = st.text_input("🔍 ابحث عن الحساب بالاسم أو الكود")
    df = load_accounts(search) if search else pd.DataFrame()

    if not df.empty:
        options = {f"{r['code']} — {r['name']}": r for _, r in df.iterrows()}
        selected_label = st.selectbox("اختر الحساب", list(options.keys()))
        r = options[selected_label]

        tab1, tab2 = st.tabs(["✏️ تعديل", "🗑️ حذف"])

        with tab1:
            with st.form("edit_form"):
                col1, col2 = st.columns(2)
                with col1:
                    new_code = st.text_input("الكود", value=r["code"])
                    new_name = st.text_input("الاسم", value=r["name"])
                    new_level = st.selectbox("المستوى", [1,2,3,4,5,6],
                                              index=int(r["acc_level"])-1,
                                              format_func=lambda x: f"مستوى {x}")
                with col2:
                    new_l1 = st.text_input("المستوى 1", value=r["level1"] or "")
                    new_l2 = st.text_input("المستوى 2", value=r["level2"] or "")
                    new_l3 = st.text_input("المستوى 3", value=r["level3"] or "")

                col3, col4 = st.columns(2)
                with col3:
                    new_l4 = st.text_input("المستوى 4", value=r["level4"] or "")
                    new_l5 = st.text_input("المستوى 5", value=r["level5"] or "")
                with col4:
                    new_l6 = st.text_input("المستوى 6", value=r["level6"] or "")

                if st.form_submit_button("💾 حفظ التعديلات", use_container_width=True):
                    ok, msg = update_account(r["id"], new_l1, new_l2, new_l3, new_l4,
                                              new_l5, new_l6, new_code, new_name, new_level)
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)

        with tab2:
            st.warning(f"⚠️ هتحذف الحساب: **{r['name']}** (كود: {r['code']})")
            if st.button("🗑️ تأكيد الحذف", type="primary"):
                delete_account(r["id"])
                st.success("✅ تم حذف الحساب")
                st.rerun()
    elif search:
        st.info("لا توجد نتائج — جرب بحثاً مختلفاً")

import streamlit as st
import pandas as pd
import sqlite3
import os

st.set_page_config(page_title="النظام المحاسبي", page_icon="📒", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');
*, *::before, *::after { font-family: 'Cairo', sans-serif !important; box-sizing: border-box; }
body, .stApp { direction: rtl; background: #f4f6f9; color: #1a1a2e; }

/* ── إخفاء زر طي الـ sidebar ── */
[data-testid="collapsedControl"] { display: none !important; }
button[kind="headerNoPadding"] { display: none !important; }
section[data-testid="stSidebar"] > div:first-child > div:first-child button { display: none !important; }

[data-testid="stSidebar"] { background: #1e2a4a !important; min-width: 220px !important; max-width: 220px !important; }
[data-testid="stSidebar"] * { color: #c8d6f0 !important; }
[data-testid="stSidebar"] .sidebar-logo { text-align:center; padding:1.2rem 0 0.5rem; font-size:1.4rem; font-weight:900; color:white !important; border-bottom:1px solid #2d3f6e; margin-bottom:0.5rem; }
[data-testid="stSidebar"] .sidebar-section { font-size:0.7rem; font-weight:700; color:#7a8fc0 !important; letter-spacing:1px; padding:1rem 1rem 0.3rem; margin:0; }

input, textarea, select { color:#1a1a2e !important; background:white !important; border:1px solid #dde3f0 !important; border-radius:8px !important; direction:rtl !important; }
input::placeholder { color:#a0aec0 !important; }
label { color:#2d3f6e !important; font-weight:600 !important; font-size:0.88rem !important; }

.page-header { background:white; padding:1rem 1.5rem; border-radius:12px; margin-bottom:1.2rem; box-shadow:0 1px 8px rgba(0,0,0,0.06); border-right:5px solid #3b5bdb; }
.page-header .ph-title { font-size:1.3rem; font-weight:900; color:#1e2a4a; margin:0; }
.page-header .ph-sub { font-size:0.8rem; color:#7a8fc0; margin:0; }

.stat-card { background:white; border-radius:12px; padding:1rem 1.5rem; box-shadow:0 1px 8px rgba(0,0,0,0.06); border-top:4px solid #3b5bdb; text-align:center; }
.stat-card.green { border-top-color:#2f9e44; }
.stat-card.orange { border-top-color:#e67700; }
.stat-card .s-num { font-size:1.7rem; font-weight:900; color:#1e2a4a; line-height:1; }
.stat-card .s-lbl { font-size:0.8rem; color:#7a8fc0; margin-top:4px; }

.acc-detail-card { background:white; border-radius:12px; padding:1.2rem 1.5rem; margin-bottom:1rem; box-shadow:0 1px 8px rgba(0,0,0,0.06); border-right:5px solid #3b5bdb; }
.adc-name { font-size:1.2rem; font-weight:900; color:#1e2a4a; }
.adc-meta { color:#7a8fc0; font-size:0.82rem; margin:4px 0 6px; }
.adc-balance { font-size:1.5rem; font-weight:900; margin-top:6px; }
.adc-balance.debit { color:#c92a2a; }
.adc-balance.credit { color:#2f9e44; }

.breadcrumb { display:flex; flex-wrap:wrap; gap:4px; direction:rtl; margin-bottom:0.8rem; align-items:center; }
.bc-item { background:#e8f0fe; color:#2d3f6e; padding:3px 10px; border-radius:20px; font-size:0.78rem; font-weight:600; }
.bc-sep { color:#a0aec0; font-size:0.78rem; }

.nav-bar { display:flex; align-items:center; gap:6px; direction:rtl; margin-bottom:0.8rem; flex-wrap:wrap; background:white; padding:0.6rem 1rem; border-radius:10px; box-shadow:0 1px 6px rgba(0,0,0,0.05); }
.nav-active { color:#3b5bdb; font-weight:900; font-size:0.85rem; }
.nav-sep { color:#a0aec0; font-size:0.85rem; }

.stButton > button { background:#3b5bdb !important; color:white !important; border:none !important; border-radius:8px !important; font-weight:700 !important; }
.stButton > button:hover { background:#2f4ac7 !important; }
.stDownloadButton > button { background:#2f9e44 !important; color:white !important; border:none !important; border-radius:8px !important; font-weight:700 !important; }

.upload-box { background:white; border-radius:12px; padding:1.5rem; border:2px dashed #3b5bdb; margin-bottom:1rem; text-align:center; }
.upload-box h4 { color:#1e2a4a; margin-bottom:.3rem; font-size:1rem; }
.upload-box p { color:#7a8fc0; font-size:.82rem; margin:0; }
.sec-title { font-size:1rem; font-weight:900; color:#1e2a4a; margin-bottom:0.8rem; padding-bottom:0.4rem; border-bottom:2px solid #e8ecf8; }
.warning-box { background:#fff9db; border:1px solid #f59f00; border-radius:8px; padding:0.8rem 1rem; margin-bottom:1rem; color:#7d5a00; font-size:0.88rem; }
.info-box { background:#e8f4fd; border:1px solid #3b5bdb; border-radius:8px; padding:0.8rem 1rem; margin-bottom:1rem; color:#1e2a4a; font-size:0.88rem; }
.danger-box { background:#fff0f0; border:1px solid #c92a2a; border-radius:8px; padding:0.8rem 1rem; margin-bottom:1rem; color:#c92a2a; font-size:0.88rem; }
.add-form-box { background:white; border-radius:12px; padding:1.5rem; box-shadow:0 2px 12px rgba(0,0,0,0.08); border:1px solid #e8ecf8; margin-top:1rem; }

/* ── جدول ميزان المراجعة ── */
.tb-table { width:100%; border-collapse:collapse; background:white; border-radius:12px; overflow:hidden; box-shadow:0 1px 8px rgba(0,0,0,0.06); }
.tb-table th { background:#1e2a4a; color:white; padding:10px 14px; text-align:right; font-size:0.88rem; }
.tb-table td { padding:8px 14px; border-bottom:1px solid #f0f3fa; font-size:0.85rem; color:#1a1a2e; }
.tb-table tr:hover td { background:#f0f4ff; }
.tb-table tr.total-row td { background:#1e2a4a; color:white; font-weight:900; }
.tb-table .debit { color:#c92a2a; font-weight:700; }
.tb-table .credit { color:#2f9e44; font-weight:700; }
.tb-table .balanced { color:#2f9e44; font-weight:900; text-align:center; }
.tb-table .unbalanced { color:#c92a2a; font-weight:900; text-align:center; }

/* ── دفتر الأستاذ ── */
.ledger-header { background:white; border-radius:12px; padding:1rem 1.5rem; margin-bottom:1rem; box-shadow:0 1px 8px rgba(0,0,0,0.06); border-right:5px solid #2f9e44; }
.ledger-balance { font-size:1.8rem; font-weight:900; }
</style>
""", unsafe_allow_html=True)

DB_PATH = "accounting.db"

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_conn()
    conn.execute("""CREATE TABLE IF NOT EXISTS chart_of_accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        level1 TEXT DEFAULT '', level2 TEXT DEFAULT '', level3 TEXT DEFAULT '',
        level4 TEXT DEFAULT '', level5 TEXT DEFAULT '', level6 TEXT DEFAULT '',
        code TEXT UNIQUE NOT NULL, name TEXT NOT NULL, acc_level INTEGER,
        is_leaf INTEGER DEFAULT 1, parent_code TEXT DEFAULT '')""")
    conn.execute("""CREATE TABLE IF NOT EXISTS journal_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entry_date TEXT, entry_no TEXT, account_code TEXT, account_name TEXT,
        description TEXT, debit REAL DEFAULT 0, credit REAL DEFAULT 0,
        source TEXT DEFAULT 'manual')""")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_code ON chart_of_accounts(code)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_parent ON chart_of_accounts(parent_code)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_lvl ON chart_of_accounts(acc_level)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_jcode ON journal_entries(account_code)")
    conn.commit(); conn.close()

def get_path(row):
    return [str(row.get(f"level{i}","") or "").strip() for i in range(1,7)
            if str(row.get(f"level{i}","") or "").strip()]

def get_parent_name(row):
    p = get_path(row); return p[-2] if len(p)>=2 else ""

def breadcrumb_html(path):
    if not path: return ""
    items = []
    for i,p in enumerate(path):
        items.append(f'<span class="bc-item">{p}</span>')
        if i < len(path)-1: items.append('<span class="bc-sep">←</span>')
    return f'<div class="breadcrumb">{"".join(items)}</div>'

@st.cache_data(ttl=300)
def load_all_accounts():
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM chart_of_accounts ORDER BY code", conn)
    conn.close(); return df

def load_accounts(search="", l1="الكل"):
    conn = get_conn()
    q = "SELECT * FROM chart_of_accounts WHERE 1=1"; p = []
    if search:
        q += " AND (name LIKE ? OR code LIKE ?)"; p += [f"%{search}%",f"%{search}%"]
    if l1 != "الكل":
        q += " AND level1=?"; p.append(l1)
    q += " ORDER BY code"
    df = pd.read_sql(q, conn, params=p); conn.close(); return df

def get_account_by_code(code):
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM chart_of_accounts WHERE code=?", conn, params=(str(code),))
    conn.close()
    return df.iloc[0] if not df.empty else None

def get_children_by_parent(parent_code):
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM chart_of_accounts WHERE parent_code=? ORDER BY CAST(code AS INTEGER)", conn, params=(str(parent_code),))
    conn.close(); return df

def get_l1_opts():
    conn = get_conn()
    df = pd.read_sql("SELECT DISTINCT level1 FROM chart_of_accounts WHERE level1!='' ORDER BY level1", conn)
    conn.close(); return ["الكل"] + df["level1"].tolist()

def has_transactions(code):
    conn = get_conn()
    count = conn.execute("SELECT COUNT(*) FROM journal_entries WHERE account_code=?", (str(code),)).fetchone()[0]
    conn.close(); return count > 0

@st.cache_data(ttl=300)
def get_cumulative_balances_all():
    conn = get_conn()
    direct_df = pd.read_sql(
        "SELECT account_code, COALESCE(SUM(debit),0) d, COALESCE(SUM(credit),0) c FROM journal_entries GROUP BY account_code", conn)
    acc_df = pd.read_sql(
        "SELECT code, parent_code FROM chart_of_accounts ORDER BY acc_level DESC, code DESC", conn)
    conn.close()
    balances = {}
    for _, r in direct_df.iterrows():
        balances[str(r["account_code"])] = [float(r["d"]), float(r["c"])]
    for _, r in acc_df.iterrows():
        if str(r["code"]) not in balances:
            balances[str(r["code"])] = [0.0, 0.0]
    for _, r in acc_df.iterrows():
        code = str(r["code"]); parent = str(r["parent_code"] or "").strip()
        if parent:
            if parent not in balances: balances[parent] = [0.0, 0.0]
            balances[parent][0] += balances[code][0]
            balances[parent][1] += balances[code][1]
    return {k: (v[0], v[1]) for k, v in balances.items()}

def get_stats():
    conn = get_conn()
    total   = conn.execute("SELECT COUNT(*) FROM chart_of_accounts").fetchone()[0]
    leaves  = conn.execute("SELECT COUNT(*) FROM chart_of_accounts WHERE is_leaf=1").fetchone()[0]
    by_l1   = pd.read_sql("SELECT level1, COUNT(*) cnt FROM chart_of_accounts WHERE acc_level=1 GROUP BY level1", conn)
    j_total = conn.execute("SELECT COUNT(*) FROM journal_entries").fetchone()[0]
    conn.close(); return total, leaves, by_l1, j_total

def add_account(parent_row, code, name, acc_type):
    conn = get_conn()
    try:
        parent_path = get_path(parent_row)
        new_level   = len(parent_path)+1
        levels      = [""]*6
        for i,p in enumerate(parent_path): levels[i] = p
        if new_level <= 6: levels[new_level-1] = name
        parent_code = str(parent_row["code"])
        is_leaf     = 1 if acc_type == "leaf" else 0
        conn.execute("""INSERT INTO chart_of_accounts
            (level1,level2,level3,level4,level5,level6,code,name,acc_level,is_leaf,parent_code)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (*levels, code, name, new_level, is_leaf, parent_code))
        conn.execute("UPDATE chart_of_accounts SET is_leaf=0 WHERE code=?", (parent_code,))
        conn.commit()
        load_all_accounts.clear(); get_cumulative_balances_all.clear()
        return True, "✅ تم إضافة الحساب بنجاح"
    except sqlite3.IntegrityError:
        return False, "❌ الكود موجود بالفعل"
    finally:
        conn.close()

def delete_account_db(acc_id, code, parent_code):
    conn = get_conn()
    conn.execute("DELETE FROM chart_of_accounts WHERE id=?", (acc_id,))
    if parent_code:
        siblings = conn.execute("SELECT COUNT(*) FROM chart_of_accounts WHERE parent_code=?", (str(parent_code),)).fetchone()[0]
        if siblings == 0:
            conn.execute("UPDATE chart_of_accounts SET is_leaf=1 WHERE code=?", (str(parent_code),))
    conn.commit()
    load_all_accounts.clear(); get_cumulative_balances_all.clear()
    conn.close()

def import_accounts_df(df, mode="add"):
    conn = get_conn()
    if mode=="replace":
        conn.execute("DELETE FROM chart_of_accounts"); conn.commit()
    df.columns = [str(c).strip() for c in df.columns]
    col_map = {}
    for c in df.columns:
        for i in range(1,7):
            if f"level{i}" in c.lower() or f"مستوى {i}" in c or f"مستوي {i}" in c:
                col_map[f"level{i}"] = c
        if "كود" in c or "code" in c.lower(): col_map["code"] = c
    parsed = []
    for _, r in df.iterrows():
        levels = []
        for k in [f"level{i}" for i in range(1,7)]:
            col = col_map.get(k)
            v = str(r[col]).strip() if col and pd.notna(r.get(col)) and str(r.get(col)).strip() not in ("","nan") else ""
            levels.append(v)
        name = next((levels[i] for i in range(5,-1,-1) if levels[i]), "")
        lvl  = sum(1 for l in levels if l)
        code_col = col_map.get("code")
        code = str(r[code_col]).strip() if code_col and pd.notna(r.get(code_col)) else ""
        try: code = str(int(float(code)))
        except: pass
        if not code or not name or code=="nan": continue
        parsed.append((levels, code, name, lvl))
    ins = skp = 0
    for levels, code, name, lvl in parsed:
        try:
            conn.execute("INSERT OR IGNORE INTO chart_of_accounts (level1,level2,level3,level4,level5,level6,code,name,acc_level,is_leaf,parent_code) VALUES (?,?,?,?,?,?,?,?,?,1,'')",
                         (*levels, code, name, lvl))
            if conn.execute("SELECT changes()").fetchone()[0]: ins+=1
            else: skp+=1
        except: skp+=1
    conn.commit()
    all_rows = conn.execute("SELECT code,level1,level2,level3,level4,level5,level6,acc_level FROM chart_of_accounts").fetchall()
    levels_to_code = {}
    for row in all_rows:
        lvls = tuple(str(row[i+1] or "").strip() for i in range(6))
        levels_to_code[lvls] = row[0]
    for row in all_rows:
        code = row[0]; lvls = [str(row[i+1] or "").strip() for i in range(6)]; lvl = row[7]
        if lvl <= 1:
            parent_code = ""
        else:
            parent_lvls = lvls[:]
            for j in range(5,-1,-1):
                if parent_lvls[j]: parent_lvls[j] = ""; break
            parent_code = levels_to_code.get(tuple(parent_lvls), "")
        conn.execute("UPDATE chart_of_accounts SET parent_code=? WHERE code=?", (parent_code, code))
    parent_codes = set(r[0] for r in conn.execute("SELECT DISTINCT parent_code FROM chart_of_accounts WHERE parent_code!=''").fetchall())
    conn.execute("UPDATE chart_of_accounts SET is_leaf=1")
    for pc in parent_codes:
        conn.execute("UPDATE chart_of_accounts SET is_leaf=0 WHERE code=?", (pc,))
    conn.commit(); conn.close()
    load_all_accounts.clear(); get_cumulative_balances_all.clear()
    return ins, skp

def import_journal_df(df, mode="add"):
    conn = get_conn()
    if mode=="replace": conn.execute("DELETE FROM journal_entries"); conn.commit()
    df.columns = [str(c).strip() for c in df.columns]
    col_map = {}
    for c in df.columns:
        cl = c.lower()
        if "تاريخ" in c or "date" in cl: col_map["date"]=c
        elif "رقم القيد" in c or "entry" in cl: col_map["entry_no"]=c
        elif "كود" in c or "account_code" in cl: col_map["code"]=c
        elif "اسم الحساب" in c or "account_name" in cl: col_map["name"]=c
        elif "وصف" in c or "desc" in cl: col_map["desc"]=c
        elif "مدين" in c or "debit" in cl: col_map["debit"]=c
        elif "دائن" in c or "credit" in cl: col_map["credit"]=c
    rows = []
    for _, r in df.iterrows():
        def g(k): col=col_map.get(k); return str(r[col]).strip() if col and pd.notna(r.get(col)) else ""
        def gn(k):
            col=col_map.get(k)
            try: return float(r[col]) if col and pd.notna(r.get(col)) else 0.0
            except: return 0.0
        rows.append((g("date"),g("entry_no"),g("code"),g("name"),g("desc"),gn("debit"),gn("credit"),"excel"))
    conn.executemany("INSERT INTO journal_entries (entry_date,entry_no,account_code,account_name,description,debit,credit,source) VALUES (?,?,?,?,?,?,?,?)", rows)
    conn.commit(); get_cumulative_balances_all.clear(); conn.close(); return len(rows)

# ══════════════════ Init ══════════════════
init_db()
excel_path = "شجرة_الحسابات_كاملة.xlsx"
if os.path.exists(excel_path):
    conn = get_conn()
    count = conn.execute("SELECT COUNT(*) FROM chart_of_accounts").fetchone()[0]
    conn.close()
    if count == 0:
        with st.spinner("جاري استيراد شجرة الحسابات..."):
            df_init = pd.read_excel(excel_path, engine="openpyxl")
            import_accounts_df(df_init, mode="replace")

if "drill_path" not in st.session_state: st.session_state.drill_path = []
if "adding_to" not in st.session_state: st.session_state.adding_to = None
if "editing_code" not in st.session_state: st.session_state.editing_code = None

# ══════════════════ Sidebar ══════════════════
with st.sidebar:
    st.markdown('<div class="sidebar-logo">📒 المحاسبي</div>', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-section">الحسابات العامة</p>', unsafe_allow_html=True)
    page = st.radio("nav", [
        "🏠  الرئيسية",
        "📋  دليل الحسابات",
        "⚖️  ميزان المراجعة",
        "📒  دفتر الأستاذ",
        "✏️  تعديل / حذف",
        "📤  استيراد البيانات",
    ], label_visibility="collapsed")
    st.markdown("---")
    total,leaves,_,j_total = get_stats()
    st.markdown(f'<div style="color:#7a8fc0;font-size:.8rem;padding:.2rem 1rem;">الحسابات: <b style="color:white">{total:,}</b></div>', unsafe_allow_html=True)
    st.markdown(f'<div style="color:#7a8fc0;font-size:.8rem;padding:.2rem 1rem;">الرئيسية: <b style="color:white">{total-leaves:,}</b></div>', unsafe_allow_html=True)
    st.markdown(f'<div style="color:#7a8fc0;font-size:.8rem;padding:.2rem 1rem;">النهائية: <b style="color:white">{leaves:,}</b></div>', unsafe_allow_html=True)
    st.markdown(f'<div style="color:#7a8fc0;font-size:.8rem;padding:.2rem 1rem;">الحركات: <b style="color:white">{j_total:,}</b></div>', unsafe_allow_html=True)

# ══════════════════ Add Form ══════════════════
def render_add_form(parent_row):
    path = get_path(parent_row)
    current_level = len(path)
    st.markdown('<div class="add-form-box">', unsafe_allow_html=True)
    st.markdown(f'**➕ إضافة حساب تحت:** {parent_row["name"]}')
    st.markdown(breadcrumb_html(path+["◀ الحساب الجديد"]), unsafe_allow_html=True)
    with st.form(f"add_inline_{parent_row['code']}"):
        col1,col2 = st.columns(2)
        with col1:
            new_code = st.text_input("كود الحساب *", placeholder="مثال: 1204301")
            new_name = st.text_input("اسم الحساب *", placeholder="اسم الحساب")
        with col2:
            if current_level >= 5:
                st.info("📄 سيكون حساباً نهائياً (المستوى 6 لا يقبل أولاداً)")
                acc_type = "leaf"
            else:
                acc_type_label = st.radio("نوع الحساب", [
                    "📄 نهائي (تُسجَّل عليه الحركات)",
                    "📁 رئيسي (سيكون له حسابات فرعية)"
                ], key=f"type_{parent_row['code']}")
                acc_type = "leaf" if "نهائي" in acc_type_label else "parent"
        col_s,col_c = st.columns(2)
        with col_s: save = st.form_submit_button("💾 حفظ", use_container_width=True)
        with col_c: cancel = st.form_submit_button("❌ إلغاء", use_container_width=True)
        if save:
            if not new_code or not new_name: st.error("الكود والاسم مطلوبان")
            else:
                ok,msg = add_account(parent_row, new_code, new_name, acc_type)
                if ok:
                    st.success(msg); st.session_state.adding_to = None; st.rerun()
                else: st.error(msg)
        if cancel:
            st.session_state.adding_to = None; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════ Edit/Delete inline ══════════════════
def render_edit_delete_inline(code):
    r = get_account_by_code(code)
    if r is None: st.session_state.editing_code = None; return
    path = get_path(r); is_leaf = int(r.get("is_leaf",1))==1
    has_tx = has_transactions(code)
    cumulative = get_cumulative_balances_all()
    d,c = cumulative.get(code,(0,0)); bal = d-c
    bal_cls = "debit" if bal>=0 else "credit"; bal_lbl = "مدين" if bal>=0 else "دائن"
    st.markdown("---")
    st.markdown(f"""
    <div class="acc-detail-card">
        <div class="adc-name">{'📄' if is_leaf else '📁'} {r['name']}</div>
        <div class="adc-meta">كود: {code} &nbsp;|&nbsp; {'✅ نهائي' if is_leaf else '📁 رئيسي'} &nbsp;|&nbsp; الحساب الرئيسي: {get_parent_name(r) or '—'}</div>
        {breadcrumb_html(path)}
        {'<div class="adc-balance '+bal_cls+'">'+f"{abs(bal):,.2f} {bal_lbl}"+'</div>' if (d+c)>0 else ''}
    </div>""", unsafe_allow_html=True)
    if has_tx:
        st.markdown('<div class="danger-box">🔒 هذا الحساب عليه معاملات مالية — لا يمكن تعديله أو حذفه</div>', unsafe_allow_html=True)
        if st.button("✖️ إغلاق"): st.session_state.editing_code = None; st.rerun()
        return
    tab1,tab2 = st.tabs(["✏️ تعديل","🗑️ حذف"])
    with tab1:
        with st.form(f"edit_inline_{code}"):
            col1,col2 = st.columns(2)
            with col1: new_code = st.text_input("الكود", value=code)
            with col2: new_name = st.text_input("الاسم", value=str(r["name"]))
            col_s,col_c = st.columns(2)
            with col_s:
                if st.form_submit_button("💾 حفظ", use_container_width=True):
                    conn = get_conn()
                    try:
                        lvl = int(r["acc_level"])
                        levels = [str(r.get(f"level{i}") or "") for i in range(1,7)]
                        levels[lvl-1] = new_name
                        conn.execute("UPDATE chart_of_accounts SET level1=?,level2=?,level3=?,level4=?,level5=?,level6=?,code=?,name=? WHERE id=?",
                            (*levels,new_code,new_name,r["id"]))
                        conn.commit(); load_all_accounts.clear(); get_cumulative_balances_all.clear()
                        st.session_state.editing_code = None; st.success("✅ تم التعديل"); st.rerun()
                    except sqlite3.IntegrityError: st.error("❌ الكود مستخدم بالفعل")
                    finally: conn.close()
            with col_c:
                if st.form_submit_button("❌ إلغاء", use_container_width=True):
                    st.session_state.editing_code = None; st.rerun()
    with tab2:
        if not is_leaf:
            st.error("❌ لا يمكن حذف حساب رئيسي — احذف الحسابات الفرعية أولاً")
        else:
            st.warning(f"⚠️ هتحذف: **{r['name']}** (كود: {code})")
            confirm = st.text_input("اكتب اسم الحساب للتأكيد", key=f"conf_{code}")
            col_d,col_c2 = st.columns(2)
            with col_d:
                if st.button("🗑️ تأكيد الحذف", type="primary", use_container_width=True):
                    if confirm.strip() == str(r["name"]).strip():
                        delete_account_db(r["id"],code,str(r.get("parent_code","")))
                        st.session_state.editing_code = None; st.success("✅ تم الحذف"); st.rerun()
                    else: st.error("الاسم غلط")
            with col_c2:
                if st.button("❌ إلغاء", use_container_width=True, key=f"cancel_del_{code}"):
                    st.session_state.editing_code = None; st.rerun()

# ══════════════════ Drill-down ══════════════════
def render_drill_down(parent_code=None):
    cumulative = get_cumulative_balances_all()
    if st.session_state.drill_path:
        nav_html = '<div class="nav-bar">🏠 الكل'
        for code,name in st.session_state.drill_path:
            nav_html += f' <span class="nav-sep">←</span> <span class="nav-active">{name}</span>'
        nav_html += '</div>'
        st.markdown(nav_html, unsafe_allow_html=True)
        if st.button("⬅️ رجوع"):
            st.session_state.drill_path.pop(); st.session_state.adding_to = None; st.rerun()
    if parent_code is None:
        conn = get_conn()
        current_df = pd.read_sql("SELECT * FROM chart_of_accounts WHERE (parent_code='' OR parent_code IS NULL) ORDER BY CAST(code AS INTEGER)", conn)
        conn.close(); current_level = 0
    else:
        current_df = get_children_by_parent(parent_code)
        pr = get_account_by_code(parent_code)
        current_level = int(pr["acc_level"]) if pr is not None else 0
    if current_df.empty and parent_code is not None:
        st.markdown('<div class="info-box">📄 حساب نهائي — الحركات المالية تُسجَّل عليه مباشرةً</div>', unsafe_allow_html=True)
    else:
        for _,r in current_df.iterrows():
            code = str(r["code"]); name = str(r["name"])
            is_leaf = int(r.get("is_leaf",1))==1
            icon = "📄" if is_leaf else "📁"
            d,c = cumulative.get(code,(0,0)); bal = d-c
            has_bal = (d+c)>0; color = "#c92a2a" if bal>=0 else "#2f9e44"; lbl = "مدين" if bal>=0 else "دائن"
            col1,col2,col3 = st.columns([5,2,1])
            with col1:
                label = f"{icon}  {name}" + ("  ◀" if not is_leaf else "")
                if st.button(label, key=f"d_{code}", use_container_width=True):
                    if not is_leaf:
                        st.session_state.drill_path.append((code,name)); st.session_state.adding_to = None; st.rerun()
            with col2:
                if has_bal:
                    st.markdown(f'<div style="text-align:left;padding-top:6px"><b style="color:{color}">{abs(bal):,.2f}</b><br><span style="font-size:.72rem;color:{color}">{lbl}</span></div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div style="text-align:left;padding-top:10px;color:#ccc">—</div>', unsafe_allow_html=True)
            with col3:
                if st.button("⚙️", key=f"edit_{code}", help="تعديل أو حذف"):
                    st.session_state.editing_code = code; st.rerun()
    if parent_code is not None and current_level < 5:
        st.markdown("---")
        parent_row_for_add = get_account_by_code(parent_code)
        if parent_row_for_add is not None:
            if st.session_state.adding_to == parent_code:
                render_add_form(parent_row_for_add)
            else:
                if st.button(f"➕ إضافة حساب تحت: {parent_row_for_add['name']}", use_container_width=True):
                    st.session_state.adding_to = parent_code; st.rerun()
    elif parent_code is not None and current_level >= 5:
        st.markdown('<div class="danger-box">🚫 لا يمكن إضافة حسابات — وصلت للمستوى الأقصى (6)</div>', unsafe_allow_html=True)
    if st.session_state.editing_code:
        render_edit_delete_inline(st.session_state.editing_code)

# ══════════════════ Pages ══════════════════

if page == "🏠  الرئيسية":
    st.markdown('<div class="page-header"><p class="ph-title">🏠 لوحة التحكم</p><p class="ph-sub">نظرة عامة على النظام المحاسبي</p></div>', unsafe_allow_html=True)
    total,leaves,by_l1,j_total = get_stats()
    cols = st.columns(max(len(by_l1)+2,3))
    with cols[0]: st.markdown(f'<div class="stat-card"><div class="s-num">{total:,}</div><div class="s-lbl">إجمالي الحسابات</div></div>', unsafe_allow_html=True)
    with cols[1]: st.markdown(f'<div class="stat-card green"><div class="s-num">{j_total:,}</div><div class="s-lbl">الحركات المسجلة</div></div>', unsafe_allow_html=True)
    for i,row in by_l1.iterrows():
        if i+2 < len(cols):
            with cols[i+2]: st.markdown(f'<div class="stat-card orange"><div class="s-num">{row["cnt"]:,}</div><div class="s-lbl">{row["level1"]}</div></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="sec-title">📁 دليل الحسابات</div>', unsafe_allow_html=True)
    current_code = st.session_state.drill_path[-1][0] if st.session_state.drill_path else None
    render_drill_down(current_code)

elif page == "📋  دليل الحسابات":
    st.markdown('<div class="page-header"><p class="ph-title">📋 دليل الحسابات</p><p class="ph-sub">تصفح وبحث في شجرة الحسابات</p></div>', unsafe_allow_html=True)
    col1,col2 = st.columns([3,2])
    with col1: search = st.text_input("🔍 بحث بالاسم أو الكود", placeholder="اكتب هنا...")
    with col2: l1_filter = st.selectbox("القسم الرئيسي", get_l1_opts())
    if search or l1_filter != "الكل":
        df = load_accounts(search, l1_filter)
        cumulative = get_cumulative_balances_all()
        st.markdown(f'<div style="color:#7a8fc0;font-size:.85rem;margin-bottom:.5rem;">{len(df):,} حساب</div>', unsafe_allow_html=True)
        rows_display = []
        for _,r in df.iterrows():
            code = str(r["code"]); d,c = cumulative.get(code,(0,0)); bal = d-c
            is_leaf = int(r.get("is_leaf",1))==1
            rows_display.append({
                "الكود": code, "اسم الحساب": ("📄 " if is_leaf else "📁 ")+r["name"],
                "الحساب الرئيسي": get_parent_name(r),
                "الرصيد": f"{abs(bal):,.2f}" if (d+c)>0 else "—",
                "النوع": ("مدين" if bal>=0 else "دائن") if (d+c)>0 else "—",
            })
        st.dataframe(pd.DataFrame(rows_display), use_container_width=True, hide_index=True, height=500)
        csv = df.to_csv(index=False, encoding="utf-8-sig")
        st.download_button("⬇️ تحميل CSV", data=csv, file_name="شجرة_الحسابات.csv", mime="text/csv")
    else:
        current_code = st.session_state.drill_path[-1][0] if st.session_state.drill_path else None
        render_drill_down(current_code)

# ══════════════════ ميزان المراجعة ══════════════════
elif page == "⚖️  ميزان المراجعة":
    st.markdown('<div class="page-header"><p class="ph-title">⚖️ ميزان المراجعة</p><p class="ph-sub">إجمالي المدين والدائن لكل حساب</p></div>', unsafe_allow_html=True)

    col1,col2,col3 = st.columns([2,2,2])
    with col1:
        lvl_filter = st.selectbox("المستوى", [0,1,2,3,4,5,6],
                                   format_func=lambda x: "كل المستويات" if x==0 else f"مستوى {x}")
    with col2:
        l1_tb = st.selectbox("القسم الرئيسي", get_l1_opts(), key="tb_l1")
    with col3:
        show_zero = st.checkbox("إظهار الحسابات ذات الرصيد صفر", value=False)

    conn = get_conn()
    q = """
        SELECT c.code, c.name, c.acc_level, c.level1,
               COALESCE(SUM(j.debit),0) as total_debit,
               COALESCE(SUM(j.credit),0) as total_credit
        FROM chart_of_accounts c
        LEFT JOIN journal_entries j ON c.code = j.account_code
        WHERE c.is_leaf = 1
    """
    params = []
    if lvl_filter > 0:
        q += " AND c.acc_level=?"; params.append(lvl_filter)
    if l1_tb != "الكل":
        q += " AND c.level1=?"; params.append(l1_tb)
    q += " GROUP BY c.code, c.name, c.acc_level, c.level1 ORDER BY c.code"
    tb_df = pd.read_sql(q, conn, params=params)
    conn.close()

    if not show_zero:
        tb_df = tb_df[(tb_df["total_debit"] > 0) | (tb_df["total_credit"] > 0)]

    if tb_df.empty:
        st.info("لا توجد بيانات")
    else:
        tb_df["الرصيد"] = tb_df["total_debit"] - tb_df["total_credit"]
        tb_df["نوع الرصيد"] = tb_df["الرصيد"].apply(lambda x: "مدين" if x>=0 else "دائن")
        tb_df["الرصيد"] = tb_df["الرصيد"].abs()

        total_d = tb_df["total_debit"].sum()
        total_c = tb_df["total_credit"].sum()
        is_balanced = abs(total_d - total_c) < 0.01

        # إحصائيات
        col1,col2,col3 = st.columns(3)
        with col1: st.markdown(f'<div class="stat-card"><div class="s-num" style="color:#c92a2a">{total_d:,.2f}</div><div class="s-lbl">إجمالي المدين</div></div>', unsafe_allow_html=True)
        with col2: st.markdown(f'<div class="stat-card"><div class="s-num" style="color:#2f9e44">{total_c:,.2f}</div><div class="s-lbl">إجمالي الدائن</div></div>', unsafe_allow_html=True)
        with col3:
            status = "✅ ميزان متوازن" if is_balanced else f"❌ فرق: {abs(total_d-total_c):,.2f}"
            color  = "#2f9e44" if is_balanced else "#c92a2a"
            st.markdown(f'<div class="stat-card"><div class="s-num" style="color:{color};font-size:1.2rem">{status}</div><div class="s-lbl">حالة الميزان</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # جدول
        display = pd.DataFrame({
            "الكود":        tb_df["code"],
            "اسم الحساب":  tb_df["name"],
            "القسم":        tb_df["level1"],
            "المستوى":      tb_df["acc_level"].apply(lambda x: f"مستوى {x}"),
            "مدين":         tb_df["total_debit"].apply(lambda x: f"{x:,.2f}" if x>0 else "—"),
            "دائن":         tb_df["total_credit"].apply(lambda x: f"{x:,.2f}" if x>0 else "—"),
            "الرصيد":       tb_df["الرصيد"].apply(lambda x: f"{x:,.2f}"),
            "النوع":        tb_df["نوع الرصيد"],
        })
        st.dataframe(display, use_container_width=True, hide_index=True, height=500)

        # تحميل
        csv = display.to_csv(index=False, encoding="utf-8-sig")
        st.download_button("⬇️ تحميل ميزان المراجعة", data=csv, file_name="ميزان_المراجعة.csv", mime="text/csv")

# ══════════════════ دفتر الأستاذ ══════════════════
elif page == "📒  دفتر الأستاذ":
    st.markdown('<div class="page-header"><p class="ph-title">📒 دفتر الأستاذ</p><p class="ph-sub">حركات كل حساب مدين ودائن</p></div>', unsafe_allow_html=True)

    col1,col2 = st.columns([3,1])
    with col1: acc_search = st.text_input("🔍 ابحث عن الحساب", placeholder="اكتب اسم أو كود الحساب...")
    with col2: show_all = st.checkbox("كل الحركات", value=False)

    acc_df = load_accounts(acc_search) if acc_search else pd.DataFrame()
    selected_acc = None

    if not acc_df.empty:
        # فلتر الحسابات النهائية فقط
        leaf_df = acc_df[acc_df["is_leaf"]==1]
        if leaf_df.empty:
            st.info("ابحث عن حساب نهائي (📄) لعرض حركاته")
        else:
            opts = {f"{r['code']} — {r['name']}": r for _,r in leaf_df.iterrows()}
            sel  = st.selectbox("اختر الحساب", list(opts.keys()))
            selected_acc = opts[sel]

    if selected_acc is not None:
        code = str(selected_acc["code"])
        name = str(selected_acc["name"])
        path = get_path(selected_acc)

        # جيب الحركات
        conn = get_conn()
        q = "SELECT * FROM journal_entries WHERE account_code=?"
        params = [code]
        if not show_all:
            q += " ORDER BY entry_date, id"
        else:
            q += " ORDER BY entry_date, id"
        entries = pd.read_sql(q, conn, params=params)
        conn.close()

        total_d = entries["debit"].sum()
        total_c = entries["credit"].sum()
        bal     = total_d - total_c
        bal_cls = "debit" if bal >= 0 else "credit"
        bal_lbl = "مدين" if bal >= 0 else "دائن"

        # header الحساب
        st.markdown(f"""
        <div class="ledger-header">
            <div style="font-size:1.1rem;font-weight:900;color:#1e2a4a">📄 {name}</div>
            <div style="color:#7a8fc0;font-size:0.8rem;margin:4px 0">{breadcrumb_html(path)}</div>
            <div style="display:flex;gap:2rem;margin-top:0.5rem">
                <div><span style="color:#c92a2a;font-weight:900;font-size:1.1rem">{total_d:,.2f}</span><br><span style="font-size:.75rem;color:#666">إجمالي المدين</span></div>
                <div><span style="color:#2f9e44;font-weight:900;font-size:1.1rem">{total_c:,.2f}</span><br><span style="font-size:.75rem;color:#666">إجمالي الدائن</span></div>
                <div><span style="color:{'#c92a2a' if bal>=0 else '#2f9e44'};font-weight:900;font-size:1.3rem">{abs(bal):,.2f} {bal_lbl}</span><br><span style="font-size:.75rem;color:#666">الرصيد</span></div>
            </div>
        </div>""", unsafe_allow_html=True)

        if entries.empty:
            st.info("لا توجد حركات على هذا الحساب")
        else:
            # حساب الرصيد التراكمي
            entries = entries.copy()
            entries["الرصيد التراكمي"] = (entries["debit"] - entries["credit"]).cumsum()

            display = pd.DataFrame({
                "التاريخ":          entries["entry_date"],
                "رقم القيد":        entries["entry_no"],
                "الوصف":            entries["description"],
                "مدين":             entries["debit"].apply(lambda x: f"{x:,.2f}" if x>0 else "—"),
                "دائن":             entries["credit"].apply(lambda x: f"{x:,.2f}" if x>0 else "—"),
                "الرصيد التراكمي":  entries["الرصيد التراكمي"].apply(lambda x: f"{abs(x):,.2f} {'مدين' if x>=0 else 'دائن'}"),
            })
            st.dataframe(display, use_container_width=True, hide_index=True, height=500)

            csv = display.to_csv(index=False, encoding="utf-8-sig")
            st.download_button(f"⬇️ تحميل دفتر {name}", data=csv, file_name=f"دفتر_الاستاذ_{code}.csv", mime="text/csv")
    elif acc_search:
        st.info("لا توجد نتائج")

elif page == "✏️  تعديل / حذف":
    st.markdown('<div class="page-header"><p class="ph-title">✏️ تعديل أو حذف حساب</p><p class="ph-sub">ابحث عن الحساب وعدّله أو احذفه</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">💡 يمكنك أيضاً التعديل والحذف من داخل شجرة الحسابات بالضغط على ⚙️</div>', unsafe_allow_html=True)
    search = st.text_input("🔍 ابحث عن الحساب بالاسم أو الكود", placeholder="اكتب هنا...")
    df = load_accounts(search) if search else pd.DataFrame()
    if not df.empty:
        opts = {}
        for _,r in df.iterrows():
            is_leaf = int(r.get("is_leaf",1))==1
            opts[f"{'📄' if is_leaf else '📁'} {r['code']} — {r['name']}"] = r
        sel = st.selectbox("اختر الحساب", list(opts.keys()))
        r   = opts[sel]
        render_edit_delete_inline(str(r["code"]))
    elif search:
        st.info("لا توجد نتائج")

elif page == "📤  استيراد البيانات":
    st.markdown('<div class="page-header"><p class="ph-title">📤 استيراد البيانات</p><p class="ph-sub">رفع شجرة الحسابات وحركات دفتر الأستاذ</p></div>', unsafe_allow_html=True)
    tab1,tab2 = st.tabs(["🌳 شجرة الحسابات","📒 حركات دفتر الأستاذ"])
    with tab1:
        st.markdown('<div class="upload-box"><h4>🌳 رفع شجرة الحسابات</h4><p>ملف Excel فيه أعمدة: المستوى 1 ... المستوى 6، الكود</p></div>', unsafe_allow_html=True)
        uploaded = st.file_uploader("اختر ملف Excel", type=["xlsx","xls"], key="acc_up")
        if uploaded:
            try:
                df_up = pd.read_excel(uploaded, engine="openpyxl")
                st.success(f"✅ تم قراءة الملف — {len(df_up):,} سطر")
                st.dataframe(df_up.head(5), use_container_width=True)
                total_now,_,_,_ = get_stats()
                st.info(f"📊 الحسابات الموجودة: {total_now:,}")
                mode = st.radio("طريقة الاستيراد",["➕ أضف للموجود","🔄 امسح وابدأ من أول"], key="acc_mode")
                if st.button("🚀 استيراد شجرة الحسابات", use_container_width=True):
                    with st.spinner("جاري الاستيراد..."):
                        ins,skp = import_accounts_df(df_up, "add" if "أضف" in mode else "replace")
                    st.success(f"✅ أضيف: {ins:,} | تخطى: {skp:,}"); st.rerun()
            except Exception as e: st.error(f"❌ خطأ: {e}")
    with tab2:
        st.markdown('<div class="upload-box"><h4>📒 رفع حركات دفتر الأستاذ</h4><p>ملف Excel فيه: التاريخ، رقم القيد، كود الحساب، اسم الحساب، الوصف، مدين، دائن</p></div>', unsafe_allow_html=True)
        uploaded_j = st.file_uploader("اختر ملف Excel", type=["xlsx","xls"], key="j_up")
        if uploaded_j:
            try:
                df_j = pd.read_excel(uploaded_j, engine="openpyxl")
                st.success(f"✅ تم قراءة الملف — {len(df_j):,} سطر")
                st.dataframe(df_j.head(5), use_container_width=True)
                _,_,_,j_total = get_stats()
                st.info(f"📊 الحركات الموجودة: {j_total:,}")
                mode_j = st.radio("طريقة الاستيراد",["➕ أضف للموجود","🔄 امسح وابدأ من أول"], key="j_mode")
                if st.button("🚀 استيراد الحركات", use_container_width=True):
                    with st.spinner("جاري الاستيراد..."):
                        ins_j = import_journal_df(df_j, "add" if "أضف" in mode_j else "replace")
                    st.success(f"✅ تم استيراد {ins_j:,} حركة!"); st.rerun()
            except Exception as e: st.error(f"❌ خطأ: {e}")

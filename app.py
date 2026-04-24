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

def get_children_by_parent(parent_code):
    conn = get_conn()
    df = pd.read_sql(
        "SELECT * FROM chart_of_accounts WHERE parent_code=? ORDER BY code",
        conn, params=(str(parent_code),))
    conn.close(); return df

def get_l1_opts():
    conn = get_conn()
    df = pd.read_sql("SELECT DISTINCT level1 FROM chart_of_accounts WHERE level1!='' ORDER BY level1", conn)
    conn.close(); return ["الكل"] + df["level1"].tolist()

@st.cache_data(ttl=300)
def get_cumulative_balances_all():
    """حساب الأرصدة التراكمية - iterative من الأعمق للأعلى"""
    conn = get_conn()
    direct_df = pd.read_sql(
        "SELECT account_code, COALESCE(SUM(debit),0) d, COALESCE(SUM(credit),0) c FROM journal_entries GROUP BY account_code",
        conn)
    # نجيب الحسابات مرتبة من الأعمق للأعلى
    acc_df = pd.read_sql(
        "SELECT code, parent_code FROM chart_of_accounts ORDER BY acc_level DESC, code DESC",
        conn)
    conn.close()

    # dict الأرصدة
    balances = {}
    for _, r in direct_df.iterrows():
        balances[str(r["account_code"])] = [float(r["d"]), float(r["c"])]

    # نضيف الحسابات اللي مفيهاش حركات
    for _, r in acc_df.iterrows():
        code = str(r["code"])
        if code not in balances:
            balances[code] = [0.0, 0.0]

    # نتجمع من الأعمق للأعلى
    for _, r in acc_df.iterrows():
        code   = str(r["code"])
        parent = str(r["parent_code"] or "").strip()
        if parent:
            if parent not in balances:
                balances[parent] = [0.0, 0.0]
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

def add_account(parent_row, code, name):
    conn = get_conn()
    try:
        parent_path = get_path(parent_row)
        new_level   = len(parent_path)+1
        levels      = [""]*6
        for i,p in enumerate(parent_path): levels[i] = p
        if new_level <= 6: levels[new_level-1] = name
        parent_code = str(parent_row["code"])
        conn.execute("""INSERT INTO chart_of_accounts
            (level1,level2,level3,level4,level5,level6,code,name,acc_level,is_leaf,parent_code)
            VALUES (?,?,?,?,?,?,?,?,?,1,?)""",
            (*levels, code, name, new_level, parent_code))
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
        siblings = conn.execute(
            "SELECT COUNT(*) FROM chart_of_accounts WHERE parent_code=?", (str(parent_code),)
        ).fetchone()[0]
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

    # ── الخطوة 1: استيراد كل الحسابات ──
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

    # ── الخطوة 2: تحديد parent_code بطريقة صحيحة ──
    # بنبني dict: (level1,level2,...levelN) → code لكل حساب
    all_rows = conn.execute(
        "SELECT code,level1,level2,level3,level4,level5,level6,acc_level FROM chart_of_accounts"
    ).fetchall()

    # نبني lookup: tuple المستويات → code
    levels_to_code = {}
    for row in all_rows:
        code   = row[0]
        lvls   = tuple(str(row[i+1] or "").strip() for i in range(6))
        levels_to_code[lvls] = code

    # لكل حساب نحدد الأب = نفس المستويات بس بدون آخر مستوى
    for row in all_rows:
        code  = row[0]
        lvls  = [str(row[i+1] or "").strip() for i in range(6)]
        lvl   = row[7]

        if lvl <= 1:
            parent_code = ""
        else:
            # مستويات الأب = نفس المستويات مع تفريغ آخر مستوى مليان
            parent_lvls = lvls[:]
            # نشوف آخر مستوى مليان ونفرغه
            for j in range(5,-1,-1):
                if parent_lvls[j]:
                    parent_lvls[j] = ""
                    break
            parent_code = levels_to_code.get(tuple(parent_lvls), "")

        conn.execute("UPDATE chart_of_accounts SET parent_code=? WHERE code=?", (parent_code, code))

    # ── الخطوة 3: تحديد is_leaf ──
    parent_codes = set(r[0] for r in conn.execute(
        "SELECT DISTINCT parent_code FROM chart_of_accounts WHERE parent_code!=''").fetchall())
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

if "drill_path" not in st.session_state:
    st.session_state.drill_path = []

# ══════════════════ Sidebar ══════════════════
with st.sidebar:
    st.markdown('<div class="sidebar-logo">📒 المحاسبي</div>', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-section">الحسابات العامة</p>', unsafe_allow_html=True)
    page = st.radio("nav", [
        "🏠  الرئيسية",
        "📋  دليل الحسابات",
        "➕  إضافة حساب",
        "✏️  تعديل / حذف",
        "📤  استيراد البيانات",
    ], label_visibility="collapsed")
    st.markdown('<p class="sidebar-section">قريباً</p>', unsafe_allow_html=True)
    st.markdown('<div style="color:#4a5f8a;font-size:.85rem;padding:.2rem 1rem;">📝 القيود اليومية</div>', unsafe_allow_html=True)
    st.markdown('<div style="color:#4a5f8a;font-size:.85rem;padding:.2rem 1rem;">📒 دفتر الأستاذ</div>', unsafe_allow_html=True)
    st.markdown('<div style="color:#4a5f8a;font-size:.85rem;padding:.2rem 1rem;">⚖️ ميزان المراجعة</div>', unsafe_allow_html=True)
    st.markdown("---")
    total,leaves,_,j_total = get_stats()
    st.markdown(f'<div style="color:#7a8fc0;font-size:.8rem;padding:.2rem 1rem;">الحسابات: <b style="color:white">{total:,}</b></div>', unsafe_allow_html=True)
    st.markdown(f'<div style="color:#7a8fc0;font-size:.8rem;padding:.2rem 1rem;">الرئيسية: <b style="color:white">{total-leaves:,}</b></div>', unsafe_allow_html=True)
    st.markdown(f'<div style="color:#7a8fc0;font-size:.8rem;padding:.2rem 1rem;">النهائية: <b style="color:white">{leaves:,}</b></div>', unsafe_allow_html=True)
    st.markdown(f'<div style="color:#7a8fc0;font-size:.8rem;padding:.2rem 1rem;">الحركات: <b style="color:white">{j_total:,}</b></div>', unsafe_allow_html=True)

# ══════════════════ Drill-down ══════════════════
def render_drill_down(parent_code=None):
    cumulative = get_cumulative_balances_all()

    if st.session_state.drill_path:
        nav_html = '<div class="nav-bar">🏠 الكل'
        for code, name in st.session_state.drill_path:
            nav_html += f' <span class="nav-sep">←</span> <span class="nav-active">{name}</span>'
        nav_html += '</div>'
        st.markdown(nav_html, unsafe_allow_html=True)
        if st.button("⬅️ رجوع"):
            st.session_state.drill_path.pop(); st.rerun()

    if parent_code is None:
        conn = get_conn()
        current_df = pd.read_sql("SELECT * FROM chart_of_accounts WHERE (parent_code='' OR parent_code IS NULL) AND acc_level=(SELECT MIN(acc_level) FROM chart_of_accounts) ORDER BY CAST(code AS INTEGER)", conn)
        conn.close()
    else:
        current_df = get_children_by_parent(parent_code)

    if current_df.empty:
        st.markdown('<div class="info-box">📄 حساب نهائي — الحركات المالية تُسجَّل عليه مباشرةً</div>', unsafe_allow_html=True)
        return

    for _, r in current_df.iterrows():
        code    = str(r["code"])
        name    = str(r["name"])
        is_leaf = int(r.get("is_leaf", 1)) == 1
        icon    = "📄" if is_leaf else "📁"
        d, c    = cumulative.get(code, (0,0))
        bal     = d - c
        has_bal = (d+c) > 0
        color   = "#c92a2a" if bal >= 0 else "#2f9e44"
        lbl     = "مدين" if bal >= 0 else "دائن"

        col1, col2 = st.columns([5,2])
        with col1:
            label = f"{icon}  {name}" + ("  ◀" if not is_leaf else "")
            if st.button(label, key=f"d_{code}", use_container_width=True):
                if not is_leaf:
                    st.session_state.drill_path.append((code, name)); st.rerun()
        with col2:
            if has_bal:
                st.markdown(f'<div style="text-align:left;padding-top:6px"><b style="color:{color}">{abs(bal):,.2f}</b><br><span style="font-size:.72rem;color:{color}">{lbl}</span></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="text-align:left;padding-top:10px;color:#ccc">—</div>', unsafe_allow_html=True)

# ══════════════════ Pages ══════════════════

if page == "🏠  الرئيسية":
    st.markdown('<div class="page-header"><p class="ph-title">🏠 لوحة التحكم</p><p class="ph-sub">نظرة عامة على النظام المحاسبي</p></div>', unsafe_allow_html=True)
    total,leaves,by_l1,j_total = get_stats()
    cols = st.columns(max(len(by_l1)+2, 3))
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
            code = str(r["code"])
            d,c  = cumulative.get(code,(0,0)); bal = d-c
            is_leaf = int(r.get("is_leaf",1))==1
            rows_display.append({
                "الكود": code,
                "اسم الحساب": ("📄 " if is_leaf else "📁 ")+r["name"],
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

elif page == "➕  إضافة حساب":
    st.markdown('<div class="page-header"><p class="ph-title">➕ إضافة حساب جديد</p><p class="ph-sub">الحساب الجديد يُضاف دائماً تحت حساب رئيسي</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">💡 يمكنك الإضافة تحت أي حساب — الحساب النهائي سيتحول لرئيسي تلقائياً</div>', unsafe_allow_html=True)
    parent_search = st.text_input("🔍 ابحث عن الحساب الرئيسي", placeholder="مثال: المدينون")
    parent_df = load_accounts(parent_search) if parent_search else pd.DataFrame()
    parent_row = None
    if not parent_df.empty:
        opts = {}
        for _,r in parent_df.iterrows():
            is_leaf = int(r.get("is_leaf",1))==1
            opts[f"{r['code']} — {r['name']} ({'📄 نهائي' if is_leaf else '📁 رئيسي'})"] = r
        sel = st.selectbox("اختر الحساب الرئيسي", list(opts.keys()))
        parent_row = opts[sel]
        path = get_path(parent_row)
        is_leaf = int(parent_row.get("is_leaf",1))==1
        st.markdown(breadcrumb_html(path+["◀ الحساب الجديد"]), unsafe_allow_html=True)
        if is_leaf:
            st.markdown('<div class="warning-box">⚠️ هذا حساب نهائي — سيتحول لرئيسي بعد الإضافة</div>', unsafe_allow_html=True)
        if len(path) >= 6:
            st.error("❌ وصلت للمستوى الأقصى (6 مستويات)"); parent_row = None
    with st.form("add_form"):
        col1,col2 = st.columns(2)
        with col1: code = st.text_input("كود الحساب *", placeholder="مثال: 1204301")
        with col2: name = st.text_input("اسم الحساب *", placeholder="مثال: سلفة أحمد محمد")
        if st.form_submit_button("💾 حفظ الحساب", use_container_width=True):
            if not code or not name: st.error("الكود والاسم مطلوبان")
            elif parent_row is None: st.error("اختر الحساب الرئيسي أولاً")
            else:
                ok,msg = add_account(parent_row, code, name)
                if ok: st.success(msg); st.balloons()
                else: st.error(msg)

elif page == "✏️  تعديل / حذف":
    st.markdown('<div class="page-header"><p class="ph-title">✏️ تعديل أو حذف حساب</p><p class="ph-sub">ابحث عن الحساب وعدّله أو احذفه</p></div>', unsafe_allow_html=True)
    search = st.text_input("🔍 ابحث عن الحساب بالاسم أو الكود", placeholder="اكتب هنا...")
    df = load_accounts(search) if search else pd.DataFrame()
    if not df.empty:
        opts = {}
        for _,r in df.iterrows():
            is_leaf = int(r.get("is_leaf",1))==1
            opts[f"{'📄' if is_leaf else '📁'} {r['code']} — {r['name']}"] = r
        sel  = st.selectbox("اختر الحساب", list(opts.keys()))
        r    = opts[sel]
        code = str(r["code"])
        path = get_path(r); parent = get_parent_name(r)
        is_leaf = int(r.get("is_leaf",1))==1
        cumulative = get_cumulative_balances_all()
        d,c = cumulative.get(code,(0,0)); bal = d-c
        bal_cls = "debit" if bal>=0 else "credit"
        bal_lbl = "مدين" if bal>=0 else "دائن"
        st.markdown(f"""
        <div class="acc-detail-card">
            <div class="adc-name">{'📄' if is_leaf else '📁'} {r['name']}</div>
            <div class="adc-meta">كود: {code} &nbsp;|&nbsp; الحساب الرئيسي: {parent or '—'} &nbsp;|&nbsp; {'✅ نهائي' if is_leaf else '📁 رئيسي'}</div>
            {breadcrumb_html(path)}
            {'<div class="adc-balance '+bal_cls+'">'+f"{abs(bal):,.2f} {bal_lbl}"+'</div>' if (d+c)>0 else ''}
        </div>""", unsafe_allow_html=True)
        tab1,tab2 = st.tabs(["✏️ تعديل الاسم والكود","🗑️ حذف"])
        with tab1:
            with st.form("edit_form"):
                col1,col2 = st.columns(2)
                with col1: new_code = st.text_input("الكود", value=code)
                with col2: new_name = st.text_input("الاسم", value=str(r["name"]))
                if st.form_submit_button("💾 حفظ التعديلات", use_container_width=True):
                    conn = get_conn()
                    try:
                        lvl = int(r["acc_level"])
                        levels = [str(r.get(f"level{i}") or "") for i in range(1,7)]
                        levels[lvl-1] = new_name
                        conn.execute("UPDATE chart_of_accounts SET level1=?,level2=?,level3=?,level4=?,level5=?,level6=?,code=?,name=? WHERE id=?",
                            (*levels, new_code, new_name, r["id"]))
                        conn.commit()
                        load_all_accounts.clear(); get_cumulative_balances_all.clear()
                        st.success("✅ تم التعديل"); st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("❌ الكود مستخدم بالفعل")
                    finally:
                        conn.close()
        with tab2:
            if not is_leaf:
                st.error("❌ لا يمكن حذف حساب رئيسي — احذف الحسابات الفرعية أولاً")
            else:
                st.warning(f"⚠️ هتحذف: **{r['name']}** (كود: {code})")
                confirm = st.text_input("اكتب اسم الحساب للتأكيد")
                if st.button("🗑️ تأكيد الحذف", type="primary"):
                    if confirm.strip() == str(r["name"]).strip():
                        delete_account_db(r["id"], code, str(r.get("parent_code","")))
                        st.success("✅ تم الحذف"); st.rerun()
                    else:
                        st.error("الاسم غلط")
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

import streamlit as st
import pandas as pd
import mysql.connector
import os
import re


# ══ MySQL Config — Aiven Cloud ══
import os as _os

def _get_mysql_config():
    # لو على Streamlit Cloud → يقرأ من Secrets
    # لو على جهازك المحلي → localhost
    try:
        return {
            "host":     st.secrets["mysql"]["host"],
            "port":     int(st.secrets["mysql"]["port"]),
            "user":     st.secrets["mysql"]["user"],
            "password": st.secrets["mysql"]["password"],
            "database": st.secrets["mysql"]["database"],
            "charset":  "utf8mb4",
            "ssl_ca":   st.secrets["mysql"].get("ssl_ca", None),
            "ssl_verify_cert": True,
            "ssl_verify_identity": False,
        }
    except:
        return {
            "host":     "localhost",
            "user":     "root",
            "password": "",
            "database": "accounting_cuc",
            "charset":  "utf8mb4",
        }

MYSQL_CONFIG = _get_mysql_config()
st.set_page_config(page_title="النظام المحاسبي", page_icon="📒", layout="wide", initial_sidebar_state="expanded")

# ══════════════════ نظام تسجيل الدخول ══════════════════
ALLOWED_USERS = {
    "waleed@gmail.com":     {"name": "أستاذ وليد",      "role": "Admin",    "password": "admin123"},
    "assistant@gmail.com":  {"name": "المساعد الخبير",   "role": "User",     "password": "user123"},
    "new_staff@gmail.com":  {"name": "الموظف الجديد",    "role": "User",     "password": "user123"},
}

def login_screen():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2%sfamily=Cairo:wght@400;600;700;900&display=swap');

    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"],
    .main, .block-container, section.main > div {
        font-family: 'Cairo', sans-serif !important;
        background: #1a2744 !important;
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
    }
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stSidebar"],
    footer { display: none !important; }

    /* تمركز الكارت */
    section.main > div { display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; }
    [data-testid="stForm"] { width: 100%; max-width: 360px; }

    /* الكارت نفسه */
    .login-card {
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.13);
        border-radius: 16px 16px 0 0;
        padding: 1.5rem 1.8rem 1rem;
        width: 100%;
        max-width: 100%;
        margin: 0 0 0 0;
        text-align: center;
    }
    .stForm > div {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255,255,255,0.13) !important;
        border-top: none !important;
        border-radius: 0 0 16px 16px !important;
        padding: 1rem 1.2rem 1.2rem !important;
    }
    .login-icon { font-size: 2.4rem; display: block; margin-bottom: 0.4rem; }
    .login-title { font-size: 1.4rem; font-weight: 900; color: #fff; margin: 0 0 0.2rem; }
    .login-sub   { font-size: 0.8rem; color: #8ba3d4; margin-bottom: 1.2rem; }
    .login-divider { height: 1px; background: rgba(255,255,255,0.1); margin-bottom: 1rem; }

    /* الـ labels */
    [data-testid="stTextInput"] label {
        color: #8ba3d4 !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        direction: rtl !important;
        text-align: right !important;
        display: block !important;
    }

    /* الـ input boxes */
    [data-testid="stTextInput"] input {
        background: rgba(255,255,255,0.07) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 8px !important;
        color: white !important;
        caret-color: white !important;
        font-size: 0.9rem !important;
        font-family: 'Cairo', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
        padding: 0.5rem 0.8rem !important;
    }
    [data-testid="stTextInput"] input:focus {
        border-color: #4d7cfe !important;
        box-shadow: 0 0 0 2px rgba(77,124,254,0.25) !important;
        outline: none !important;
    }
    [data-testid="stTextInput"] input::placeholder {
        color: rgba(255,255,255,0.25) !important;
        direction: rtl !important;
        text-align: right !important;
    }

    /* زرار الدخول */
    [data-testid="stFormSubmitButton"] > button {
        background: #3b5bdb !important;
        background-image: none !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        font-family: 'Cairo', sans-serif !important;
        padding: 0.55rem 1rem !important;
        width: 100% !important;
        cursor: pointer !important;
        margin-top: 0.4rem !important;
    }
    [data-testid="stFormSubmitButton"] > button:hover {
        background: #2f4ac7 !important;
        background-image: none !important;
    }
    [data-testid="stFormSubmitButton"] > button:focus {
        background: #3b5bdb !important;
        background-image: none !important;
        box-shadow: 0 0 0 2px rgba(77,124,254,0.4) !important;
    }

    /* إخفاء border الفورم */
    .stForm { border: none !important; padding: 0 !important; background: transparent !important; }
    [data-testid="stAlert"] { border-radius: 8px !important; max-width: 360px; margin: 0 auto; }
    </style>

    <div class="login-card">
        <span class="login-icon">📒</span>
        <div class="login-title">النظام المحاسبي</div>
        <div class="login-sub">أدخل بياناتك للمتابعة</div>
        <div class="login-divider"></div>
    </div>
    <style>
    /* تمركز الفورم تحت الكارت مباشرة */
    [data-testid="stForm"] { width:360px !important; margin: -0.5rem auto 0 !important; }
    </style>
    """, unsafe_allow_html=True)

    _, col_m, _ = st.columns([1, 1.2, 1])
    with col_m:
      with st.form("login_form"):
        email    = st.text_input("البريد الإلكتروني", placeholder="example@email.com", label_visibility="visible")
        password = st.text_input("كلمة المرور", type="password", placeholder="••••••••")
        submit   = st.form_submit_button("دخول ←", use_container_width=True)
        if submit:
            user = ALLOWED_USERS.get(email.strip())
            if user and password == user["password"]:
                st.session_state["authenticated"] = True
                st.session_state["user_info"]     = user
                st.rerun()
            else:
                st.error("❌ البريد الإلكتروني أو كلمة المرور غلط")

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# if not st.session_state["authenticated"]:
#     login_screen()
#     st.stop()
st.session_state["authenticated"] = True
st.session_state["user_info"] = {"name": "أستاذ وليد", "role": "Admin"}

user_info = st.session_state["user_info"]
is_admin  = user_info["role"] == "Admin"

# ══════════════════ CSS ══════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2%sfamily=Cairo:wght@400;600;700;900&display=swap');
*, *::before, *::after { font-family: 'Cairo', sans-serif !important; box-sizing: border-box; }
body, .stApp { direction: rtl; background: #f4f6f9; color: #1a1a2e; }

[data-testid="collapsedControl"] { display:none !important; }
[data-testid="stSidebarCollapseButton"] { display:none !important; }
button[data-testid="baseButton-headerNoPadding"] { display:none !important; }

[data-testid="stSidebar"] {
    background: #111827 !important;
    min-width: 280px !important;
    max-width: 280px !important;
}
[data-testid="stSidebar"] > div { overflow-x: hidden !important; }
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }

/* اللوجو */
[data-testid="stSidebar"] .sidebar-logo {
    text-align: center;
    padding: 1.2rem 1rem 1rem;
    font-size: 1.15rem;
    font-weight: 900;
    color: white !important;
    letter-spacing: .5px;
}

/* معلومات المستخدم */
[data-testid="stSidebar"] .user-info {
    padding: .6rem 1rem;
    background: rgba(255,255,255,.06);
    border-radius: 10px;
    margin: 0 .8rem .8rem;
    font-size: .82rem;
    border: 1px solid rgba(255,255,255,.08);
}

/* عنوان القسم */
[data-testid="stSidebar"] .sidebar-section {
    font-size: .68rem;
    font-weight: 700;
    color: #64748b !important;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding: 1.2rem 1rem .4rem;
    margin: 0;
}

/* اختيار الشركة */
[data-testid="stSidebar"] [data-baseweb="select"],
[data-testid="stSidebar"] [data-baseweb="select"] > div,
[data-testid="stSidebar"] [data-baseweb="select"] > div > div {
    background: rgba(255,255,255,.08) !important;
    border: 1px solid rgba(255,255,255,.2) !important;
    border-radius: 8px !important;
    color: white !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] *,
[data-testid="stSidebar"] [data-baseweb="select"] span,
[data-testid="stSidebar"] [data-baseweb="select"] div,
[data-testid="stSidebar"] [data-baseweb="select"] p { color: white !important; }
[data-testid="stSidebar"] [data-baseweb="select"] svg { fill: white !important; }



/* الإحصائيات السفلية */
[data-testid="stSidebar"] .stats-row {
    display: flex;
    justify-content: space-between;
    padding: .4rem 1rem;
    font-size: .78rem;
    color: #64748b !important;
}
[data-testid="stSidebar"] .stats-row b { color: #94a3b8 !important; }

/* إخفاء أزرار الناف — كل أزرار الـ sidebar مخفية ما عدا الخروج */
[data-testid="stSidebar"] .nav-btn-hidden button {
    position: absolute !important;
    width: 1px !important; height: 1px !important;
    opacity: 0 !important; pointer-events: none !important;
    overflow: hidden !important;
}

/* زرار الخروج */
[data-testid="stSidebar"] .logout-btn button {
    background: rgba(201,42,42,.2) !important;
    color: #fca5a5 !important;
    border: 1px solid rgba(201,42,42,.3) !important;
    border-radius: 8px !important;
    font-size: .84rem !important;
    width: 100% !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}
[data-testid="stSidebar"] .logout-btn button p,
[data-testid="stSidebar"] .logout-btn button span {
    color: #fca5a5 !important;
}
[data-testid="stSidebar"] .logout-btn button:hover {
    background: rgba(201,42,42,.4) !important;
}

/* ══ إصلاح شامل للنصوص والألوان ══ */
/* inputs */
input, textarea, select {
    color: #1a1a2e !important;
    background: white !important;
    border: 1px solid #dde3f0 !important;
    border-radius: 8px !important;
    direction: rtl !important;
}
input::placeholder { color: #a0aec0 !important; }

/* labels خارج الـ sidebar */
.main label,
section.main label,
[data-testid="stMain"] label {
    color: #2d3f6e !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
}

/* Tabs — نص داكن على خلفية فاتحة */
[data-baseweb="tab-list"] {
    background: transparent !important;
}
[data-baseweb="tab"] {
    background: transparent !important;
    color: #4a5568 !important;
}
[data-baseweb="tab"] button,
[data-baseweb="tab"] [role="tab"] {
    color: #4a5568 !important;
    background: transparent !important;
    font-weight: 500 !important;
}
[data-baseweb="tab"] button[aria-selected="true"],
[data-baseweb="tab"] [role="tab"][aria-selected="true"] {
    color: #3b5bdb !important;
    font-weight: 700 !important;
    background: transparent !important;
}
[data-testid="stTabs"] [role="tab"] p,
[data-testid="stTabs"] [role="tab"] span {
    color: inherit !important;
}

/* Expander */
[data-testid="stExpander"] summary {
    color: #1e2a4a !important;
    background: white !important;
}
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary span {
    color: #1e2a4a !important;
}

/* Radio خارج الـ sidebar */
section.main [data-testid="stRadio"] label,
section.main [data-baseweb="radio"] label {
    color: #1e2a4a !important;
    background: transparent !important;
}

/* Selectbox خارج الـ sidebar */
section.main [data-baseweb="select"] div,
section.main [data-baseweb="select"] span,
section.main [data-baseweb="select"] input {
    color: #1e2a4a !important;
    background: white !important;
}
section.main [data-baseweb="select"] > div {
    background: white !important;
    border: 1px solid #dde3f0 !important;
}

/* Checkbox */
[data-baseweb="checkbox"] label,
[data-baseweb="checkbox"] span {
    color: #1e2a4a !important;
}

/* Popover / dropdown options */
[data-baseweb="popover"] {
    background: white !important;
}
[data-baseweb="popover"] li,
[data-baseweb="popover"] [role="option"] {
    color: #1e2a4a !important;
    background: white !important;
}
[data-baseweb="popover"] li:hover,
[data-baseweb="popover"] [role="option"]:hover {
    background: #e8f0fe !important;
}
[data-baseweb="menu"] { background: white !important; }
[data-baseweb="menu"] li { color: #1e2a4a !important; background: white !important; }
[data-baseweb="menu"] li:hover { background: #e8f0fe !important; }

/* DataFrames */
[data-testid="stDataFrame"] { color: #1e2a4a !important; }
[data-testid="stDataFrame"] * { color: #1e2a4a !important; }

/* Metric */
[data-testid="stMetric"] label { color: #7a8fc0 !important; }
[data-testid="stMetric"] [data-testid="stMetricValue"] { color: #1e2a4a !important; }

/* ══ Radio في الـ main content ══ */
section.main [data-testid="stRadio"] label {
    color: #1e2a4a !important;
    background: white !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 8px !important;
    padding: .4rem .9rem !important;
    font-size: .88rem !important;
    cursor: pointer !important;
    transition: all .15s !important;
}
section.main [data-testid="stRadio"] label:hover {
    background: #f0f4ff !important;
    border-color: #3b5bdb !important;
    color: #1e2a4a !important;
}
section.main [data-testid="stRadio"] label[data-checked="true"],
section.main [data-testid="stRadio"] label:has(input:checked) {
    background: #e8f0fe !important;
    border-color: #3b5bdb !important;
    color: #1e2a4a !important;
    font-weight: 700 !important;
}
section.main [data-testid="stRadio"] label p,
section.main [data-testid="stRadio"] label span {
    color: #1e2a4a !important;
}
section.main [data-testid="stRadio"] input[type="radio"] {
    display: none !important;
}
section.main [data-testid="stRadio"] [data-testid="stMarkdownContainer"] {
    display: none !important;
}
section.main [data-testid="stRadio"] > label {
    color: #2d3f6e !important;
    font-weight: 600 !important;
    font-size: .88rem !important;
}
section.main [data-testid="stRadio"] > div {
    display: flex !important;
    flex-wrap: wrap !important;
    gap: 6px !important;
    background: transparent !important;
}

/* Alerts */
[data-testid="stAlert"] * { color: inherit !important; }

/* كل النصوص في الـ main تكون داكنة */
section.main p,
section.main span:not([data-testid="stSidebar"] span),
section.main div:not([data-testid="stSidebar"] div) {
    color: inherit;
}

/* ══ Selectbox كـ tab bar ══ */
section.main [data-testid="stSelectbox"] > div > div {
    background: white !important;
    border: 1.5px solid #3b5bdb !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    color: #1e2a4a !important;
}
section.main [data-testid="stSelectbox"] [data-baseweb="select"] span,
section.main [data-testid="stSelectbox"] [data-baseweb="select"] div {
    color: #1e2a4a !important;
}

/* ══ Scrollbar شامل ══ */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #f1f5f9; border-radius: 3px; }
::-webkit-scrollbar-thumb { background: #94a3b8; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #64748b; }

/* Streamlit dataframe scrollbar */
[data-testid="stDataFrame"] > div { overflow: auto !important; }
[data-testid="stDataFrame"] iframe { overflow: auto !important; }

/* الصفحة الرئيسية تأخذ كل الارتفاع المتاح */
section.main > div.block-container {
    padding-top: 1rem !important;
    padding-bottom: 2rem !important;
    max-width: 100% !important;
    overflow-y: auto !important;
}

/* Sidebar scrollbar */
[data-testid="stSidebar"] > div:first-child {
    overflow-y: auto !important;
    overflow-x: hidden !important;
    height: 100vh !important;
}

/* إخفاء عناصر Streamlit غير المطلوبة */
[data-testid="stHeader"] { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
footer { display: none !important; }
#MainMenu { display: none !important; }
.reportview-container .main footer { display: none !important; }

/* File uploader */
[data-testid="stFileUploader"] { background: white !important; }
[data-testid="stFileUploader"] section,
[data-testid="stFileUploader"] > div {
    background: white !important;
    border: 2px dashed #3b5bdb !important;
    border-radius: 10px !important;
}
[data-testid="stFileUploader"] * { color: #2d3f6e !important; }
[data-testid="stFileUploaderDropzone"],
[data-testid="stFileUploaderDropzone"] > div { background: white !important; }

/* زرار Browse files */
[data-testid="stFileUploader"] button,
[data-testid="stFileUploader"] [data-testid="baseButton-secondary"],
[data-testid="stFileUploaderDropzone"] button {
    background: #3b5bdb !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
}
[data-testid="stFileUploader"] button *,
[data-testid="stFileUploader"] button span,
[data-testid="stFileUploader"] button p,
[data-testid="stFileUploaderDropzone"] button span,
[data-testid="stFileUploaderDropzone"] button p {
    color: white !important;
    font-weight: 700 !important;
}
[data-testid="stFileUploaderDropzoneInstructions"],
[data-testid="stFileUploaderDropzoneInstructions"] * { color: #7a8fc0 !important; }

/* X زرار حذف الملف */
[data-testid="stFileUploader"] [data-testid="stFileUploaderDeleteBtn"] button {
    background: transparent !important;
    color: #c92a2a !important;
    border: 1px solid #c92a2a !important;
}

.page-header { background:white; padding:1rem 1.5rem; border-radius:12px; margin-bottom:1.2rem; box-shadow:0 1px 8px rgba(0,0,0,0.06); border-right:5px solid #3b5bdb; }
.page-header .ph-title { font-size:1.3rem; font-weight:900; color:#1e2a4a; margin:0; }
.page-header .ph-sub { font-size:0.8rem; color:#7a8fc0; margin:0; }

.stat-card { background:white; border-radius:12px; padding:1rem 1.5rem; box-shadow:0 1px 8px rgba(0,0,0,0.06); border-top:4px solid #3b5bdb; text-align:center; }
.stat-card.green { border-top-color:#2f9e44; }
.stat-card.orange { border-top-color:#e67700; }
.stat-card.red { border-top-color:#c92a2a; }
.stat-card .s-num { font-size:1.7rem; font-weight:900; color:#1e2a4a !important; line-height:1; }
.stat-card .s-lbl { font-size:0.8rem; color:#7a8fc0 !important; margin-top:4px; }



.check-card { background:white; border-radius:12px; padding:1.2rem 1.5rem; box-shadow:0 1px 8px rgba(0,0,0,0.06); border:2px solid #e8ecf8; text-align:center; }
.check-card.blue  { border-color:#3b5bdb; }
.check-card.green { border-color:#2f9e44; }
.check-card.red   { border-color:#c92a2a; }
.check-card.orange{ border-color:#e67700; }
.check-card .cn   { font-size:1.8rem; font-weight:900; }
.check-card .cl   { font-size:0.78rem; color:#7a8fc0; margin-top:4px; }

.acc-detail-card { background:white; border-radius:12px; padding:1.2rem 1.5rem; margin-bottom:1rem; box-shadow:0 1px 8px rgba(0,0,0,0.06); border-right:5px solid #3b5bdb; }
.adc-name { font-size:1.2rem; font-weight:900; color:#1e2a4a; }
.adc-meta { color:#7a8fc0; font-size:0.82rem; margin:4px 0 6px; }
.adc-balance { font-size:1.5rem; font-weight:900; margin-top:6px; }
.adc-balance.debit { color:#c92a2a; }
.adc-balance.credit { color:#2f9e44; }

.breadcrumb { display:flex; flex-wrap:wrap; gap:4px; direction:rtl; margin-bottom:0.8rem; align-items:center; }
.bc-item { background:#e8f0fe; color:#2d3f6e; padding:3px 10px; border-radius:20px; font-size:0.78rem; font-weight:600; }
.bc-sep { color:#a0aec0; font-size:0.78rem; }


/* أزرار الشجرة والهرمي — نص داكن على خلفية فاتحة */
[data-testid="stButton"] button[kind="secondary"] {
    background: white !important;
    color: #1e2a4a !important;
    border: 1px solid #e8ecf8 !important;
    border-right: 3px solid #3b5bdb !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
    padding: 0.35rem 0.8rem !important;
    text-align: right !important;
    box-shadow: none !important;
}
[data-testid="stButton"] button[kind="secondary"]:hover {
    background: #f0f4ff !important;
    color: #1e2a4a !important;
    border-color: #3b5bdb !important;
}
/* أزرار الحسابات الهرمية */
[data-testid="stButton"] button[data-testid*="led_ch_"] {
    background: white !important;
    color: #1e2a4a !important;
    border: 1px solid #e8ecf8 !important;
    border-radius: 10px !important;
    font-size: 0.85rem !important;
    white-space: pre-line !important;
    height: auto !important;
    min-height: 60px !important;
    padding: 0.5rem !important;
}
[data-testid="stButton"] button[data-testid*="led_ch_"]:hover {
    background: #f0f4ff !important;
    color: #1e2a4a !important;
    border-color: #3b5bdb !important;
}
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
.success-box { background:#ebfbee; border:1px solid #2f9e44; border-radius:8px; padding:0.8rem 1rem; margin-bottom:1rem; color:#1a6e2e; font-size:0.88rem; }
.add-form-box { background:white; border-radius:12px; padding:1.5rem; box-shadow:0 2px 12px rgba(0,0,0,0.08); border:1px solid #e8ecf8; margin-top:1rem; }
.ledger-header { background:white; border-radius:12px; padding:1rem 1.5rem; margin-bottom:1rem; box-shadow:0 1px 8px rgba(0,0,0,0.06); border-right:5px solid #2f9e44; }

[data-testid="stFileUploader"] section { background:white !important; border:2px dashed #3b5bdb !important; border-radius:10px !important; }
[data-testid="stFileUploader"] section * { color:#2d3f6e !important; }
[data-testid="stFileUploaderDropzone"] { background:white !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════ DB ══════════════════

class _ConnWrap:
    def __init__(self, conn):
        self._c = conn
        self._cur = conn.cursor(buffered=True)
    def execute(self, sql, p=None):
        if p: self._cur.execute(sql, p)
        else: self._cur.execute(sql)
        return self._cur
    def executemany(self, sql, p):
        self._cur.executemany(sql, p)
        return self._cur
    def fetchall(self): return self._cur.fetchall()
    def fetchone(self): return self._cur.fetchone()
    def commit(self): self._c.commit()
    def close(self):
        try: self._cur.close()
        except: pass
        try: self._c.close()
        except: pass
    def cursor(self): return self._c.cursor(buffered=True)
    def __enter__(self): return self
    def __exit__(self, *a): self.close()

def get_conn():
    return _ConnWrap(mysql.connector.connect(**MYSQL_CONFIG))


def init_db():
    try:
        conn = get_conn()
        conn.execute("INSERT IGNORE INTO companies (id, name, color) VALUES (1, 'الشركة الرئيسية', '#3b5bdb')")
        conn.commit()
        conn.close()
    except Exception:
        pass

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

# ══════════ دوال الشركات ══════════
def get_companies():
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM companies ORDER BY id", conn)
    conn.close(); return df

def add_company(name, color="#3b5bdb"):
    conn = get_conn()
    count = conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
    if count >= 5: return False, "❌ الحد الأقصى 5 شركات"
    try:
        conn.execute("INSERT INTO companies (name, color) VALUES (%s,%s)", (name, color))
        conn.commit(); return True, "✅ تمت إضافة الشركة"
    except mysql.connector.errors.IntegrityError: return False, "❌ الاسم موجود بالفعل"
    finally: conn.close()

def delete_company(company_id):
    conn = get_conn()
    conn.execute("DELETE FROM chart_of_accounts WHERE company_id=%s", (company_id,))
    conn.execute("DELETE FROM journal_entries WHERE company_id=%s", (company_id,))
    conn.execute("DELETE FROM companies WHERE id=%s", (company_id,))
    conn.commit(); conn.close()
    load_all_accounts.clear(); get_cumulative_balances_all.clear(); get_all_leaf_accounts.clear()

def get_active_company_id():
    if "active_company" not in st.session_state:
        conn = get_conn()
        first = conn.execute("SELECT id FROM companies ORDER BY id LIMIT 1").fetchone()
        conn.close()
        st.session_state.active_company = first[0] if first else 1
    return st.session_state.active_company

# ══════════ دوال البيانات (مع company_id) ══════════
@st.cache_data(ttl=600)
def load_all_accounts(company_id=1):
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM chart_of_accounts WHERE company_id=%s ORDER BY code", conn, params=(company_id,))
    conn.close(); return df

def load_accounts(search="", l1="الكل", company_id=1):
    conn = get_conn()
    q = "SELECT * FROM chart_of_accounts WHERE company_id=%s"; p = [company_id]
    if search:
        q += " AND (name LIKE %s OR code LIKE %s)"; p += [f"%{search}%",f"%{search}%"]
    if l1 != "الكل":
        q += " AND level1=%s"; p.append(l1)
    q += " ORDER BY name COLLATE utf8mb4_general_ci"
    df = pd.read_sql(q, conn, params=p); conn.close(); return df

@st.cache_data(ttl=600)
def get_all_leaf_accounts(company_id=1):
    conn = get_conn()
    df = pd.read_sql(
        "SELECT code, name, level1, acc_level FROM chart_of_accounts WHERE is_leaf=1 AND company_id=%s ORDER BY name COLLATE utf8mb4_general_ci",
        conn, params=(company_id,))
    conn.close(); return df

def get_account_by_code(code, company_id=1):
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM chart_of_accounts WHERE code=%s AND company_id=%s", conn, params=(str(code), company_id))
    conn.close()
    return df.iloc[0] if not df.empty else None

def get_children_by_parent(parent_code, company_id=1):
    conn = get_conn()
    df = pd.read_sql(
        "SELECT * FROM chart_of_accounts WHERE parent_code=%s AND company_id=%s ORDER BY CAST(code AS UNSIGNED)",
        conn, params=(str(parent_code), company_id))
    conn.close(); return df

def get_l1_opts(company_id=1):
    conn = get_conn()
    df = pd.read_sql("SELECT DISTINCT level1 FROM chart_of_accounts WHERE level1!='' AND company_id=%s ORDER BY level1", conn, params=(company_id,))
    conn.close(); return ["الكل"] + df["level1"].tolist()

def has_transactions(code, company_id=1):
    conn = get_conn()
    count = conn.execute("SELECT COUNT(*) FROM journal_lines WHERE account_code=%s AND company_id=%s", (str(code), company_id)).fetchone()[0]
    conn.close(); return count > 0

@st.cache_data(ttl=600)
def get_cumulative_balances_all(company_id=1):
    conn = get_conn()
    direct_df = pd.read_sql(
        "SELECT account_code, COALESCE(SUM(debit),0) d, COALESCE(SUM(credit),0) c FROM journal_lines WHERE company_id=%s GROUP BY account_code",
        conn, params=(company_id,))
    acc_df = pd.read_sql(
        "SELECT code, parent_code FROM chart_of_accounts WHERE company_id=%s ORDER BY acc_level DESC, code DESC",
        conn, params=(company_id,))
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

def get_stats(company_id=1):
    conn = get_conn()
    total   = conn.execute("SELECT COUNT(*) FROM chart_of_accounts WHERE company_id=%s", (company_id,)).fetchone()[0]
    leaves  = conn.execute("SELECT COUNT(*) FROM chart_of_accounts WHERE is_leaf=1 AND company_id=%s", (company_id,)).fetchone()[0]
    by_l1   = pd.read_sql("SELECT level1, COUNT(*) cnt FROM chart_of_accounts WHERE acc_level=1 AND company_id=%s GROUP BY level1", conn, params=(company_id,))
    j_total = conn.execute("SELECT COUNT(*) FROM journal_lines WHERE company_id=%s", (company_id,)).fetchone()[0]
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
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (*levels, code, name, new_level, is_leaf, parent_code))
        conn.execute("UPDATE chart_of_accounts SET is_leaf=0 WHERE code=%s", (parent_code,))
        conn.commit()
        load_all_accounts.clear(); get_cumulative_balances_all.clear(); get_all_leaf_accounts.clear()
        return True, "✅ تم إضافة الحساب بنجاح"
    except mysql.connector.errors.IntegrityError:
        return False, "❌ الكود موجود بالفعل"
    finally:
        conn.close()

def delete_account_db(code, parent_code):
    conn = get_conn()
    conn.execute("DELETE FROM chart_of_accounts WHERE code=%s AND company_id=%s", (str(code), co_id))
    if parent_code:
        siblings = conn.execute("SELECT COUNT(*) FROM chart_of_accounts WHERE parent_code=%s AND company_id=%s", (str(parent_code), co_id)).fetchone()[0]
        if siblings == 0:
            conn.execute("UPDATE chart_of_accounts SET is_leaf=1 WHERE code=%s", (str(parent_code),))
    conn.commit()
    load_all_accounts.clear(); get_cumulative_balances_all.clear(); get_all_leaf_accounts.clear()
    conn.close()

def import_accounts_df(df, mode="add", company_id=1):
    conn = get_conn()
    if mode=="replace":
        conn.execute("DELETE FROM chart_of_accounts WHERE company_id=%s", (company_id,)); conn.commit()
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
        # تنظيف الكود بدون float (يضيع الدقة في الأرقام الكبيرة)
        code = str(code).strip()
        if 'e+' in code.lower() or 'e-' in code.lower():
            try: code = str(int(float(code)))  # scientific notation فقط
            except: code = ''
        else:
            code = code.split('.')[0]  # إزالة .0 فقط
        if not code.lstrip('-').isdigit(): code = ""
        if not code or not name or code=="nan": continue
        parsed.append((levels, code, name, lvl))
    ins = skp = 0
    for levels, code, name, lvl in parsed:
        try:
            conn.execute("INSERT IGNORE INTO chart_of_accounts (company_id,level1,level2,level3,level4,level5,level6,code,name,acc_level,is_leaf,parent_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,1,'')",
                         (company_id, *levels, code, name, lvl))
            if conn.execute("SELECT changes()").fetchone()[0]: ins+=1  # noqa
            else: skp+=1
        except: skp+=1
    conn.commit()
    all_rows = conn.execute("SELECT code,level1,level2,level3,level4,level5,level6,acc_level FROM chart_of_accounts WHERE company_id=%s", (company_id,)).fetchall()
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
        conn.execute("UPDATE chart_of_accounts SET parent_code=%s WHERE code=%s AND company_id=%s", (parent_code, code, company_id))
    parent_codes = set(r[0] for r in conn.execute("SELECT DISTINCT parent_code FROM chart_of_accounts WHERE parent_code!='' AND company_id=%s", (company_id,)).fetchall())
    conn.execute("UPDATE chart_of_accounts SET is_leaf=1 WHERE company_id=%s", (company_id,))
    for pc in parent_codes:
        conn.execute("UPDATE chart_of_accounts SET is_leaf=0 WHERE code=%s AND company_id=%s", (pc, company_id))
    conn.commit(); conn.close()
    load_all_accounts.clear(); get_cumulative_balances_all.clear(); get_all_leaf_accounts.clear()
    return ins, skp

# ══════════ دوال Mapping (دمج البيانات) ══════════
def apply_mappings(df, company_id=1, product_col="product_name", code_col="product_code", cat_col="category", center_col="cost_center"):
    """
    يطبق كل الـ mappings على DataFrame —
    يستبدل أسماء المنتجات والتصنيفات ومراكز التكلفة بالنسخة الموحدة
    """
    conn = get_conn()
    pmaps = pd.read_sql("SELECT original_name, original_code, mapped_name, mapped_category FROM product_mapping WHERE company_id=%s", conn, params=(company_id,))
    cmaps = pd.read_sql("SELECT original_category, mapped_category FROM category_mapping WHERE company_id=%s", conn, params=(company_id,))
    ccmaps = pd.read_sql("SELECT original_name, mapped_name FROM cost_center_mapping WHERE company_id=%s", conn, params=(company_id,))
    conn.close()

    df = df.copy()

    # تطبيق product mapping
    if not pmaps.empty and product_col in df.columns:
        p_name_map = dict(zip(pmaps["original_name"], pmaps["mapped_name"]))
        p_cat_map  = dict(zip(pmaps["original_name"], pmaps["mapped_category"]))
        p_code_map = {}
        for _, r in pmaps.iterrows():
            if pd.notna(r["original_code"]) and r["original_code"]:
                p_code_map[str(r["original_code"])] = r["mapped_name"]
        if code_col in df.columns:
            df[product_col] = df.apply(lambda r: p_code_map.get(str(r[code_col]), p_name_map.get(r[product_col], r[product_col])), axis=1)
        else:
            df[product_col] = df[product_col].map(lambda x: p_name_map.get(x, x))
        if cat_col in df.columns:
            df[cat_col] = df.apply(lambda r: p_cat_map.get(r[product_col], r[cat_col]) if pd.notna(p_cat_map.get(r[product_col])) else r[cat_col], axis=1)

    # تطبيق category mapping
    if not cmaps.empty and cat_col in df.columns:
        cat_map_d = dict(zip(cmaps["original_category"], cmaps["mapped_category"]))
        df[cat_col] = df[cat_col].map(lambda x: cat_map_d.get(x, x))

    # تطبيق cost center mapping
    if not ccmaps.empty and center_col in df.columns:
        cc_map_d = dict(zip(ccmaps["original_name"], ccmaps["mapped_name"]))
        df[center_col] = df[center_col].map(lambda x: cc_map_d.get(x, x) if pd.notna(x) else x)

    return df


def tab_bar(options, key, default=0):
    """بديل للـ radio — selectbox واضح"""
    if f"tab_{key}" not in st.session_state:
        st.session_state[f"tab_{key}"] = options[default] if default < len(options) else options[0]
    # لو القيمة المحفوظة مش في الـ options — reset
    if st.session_state[f"tab_{key}"] not in options:
        st.session_state[f"tab_{key}"] = options[0]
    chosen = st.selectbox("", options,
                          index=options.index(st.session_state[f"tab_{key}"]),
                          key=f"tabsel_{key}",
                          label_visibility="collapsed")
    st.session_state[f"tab_{key}"] = chosen
    return chosen


def parse_stock_ledger(df_raw):
    """
    يقرأ ملف أستاذ المخزن من دفترة — كل منتج header ثم حركاته
    يُرجع DataFrame موحد مع عمود product_name
    """
    df_raw = df_raw.copy()
    df_raw.columns = [c.strip() for c in df_raw.columns]

    # تحديد صفوف الهيدر (المنتج) — المستودع فاضي والاسم فيه #
    mask_product = df_raw.iloc[:,2].isna() & df_raw.iloc[:,0].astype(str).str.contains("#", na=False)
    mask_data    = df_raw.iloc[:,2].notna()

    # تحديد المنتج لكل حركة
    current_prod = None
    product_col  = []
    for idx in df_raw.index:
        if mask_product[idx]:
            raw_name = str(df_raw.iloc[idx, 0]).strip()
            # فصل الاسم عن الكود
            parts = raw_name.rsplit("#", 1)
            current_prod = parts[0].strip() if len(parts) > 1 else raw_name
        product_col.append(current_prod)
    df_raw["product_name"] = product_col

    # الحركات فقط
    df_data = df_raw[mask_data].copy()

    # تحويل الأعمدة الرقمية
    num_cols = ["الكمية", "سعر الوحدة (EGP)", "المخزون بعد",
                "متوسط سعر التكلفة", "إجمالي قيمة الحركة",
                "السعر الكلي", "قيمة المخزون بعد"]
    for c in num_cols:
        if c in df_data.columns:
            df_data[c] = pd.to_numeric(df_data[c].astype(str).str.replace(",",""), errors="coerce").fillna(0)

    # تحديد نوع الحركة من الكمية
    qty_col = "الكمية"
    if qty_col in df_data.columns:
        df_data["movement_type"] = df_data[qty_col].apply(
            lambda x: "اضافة" if float(x) > 0 else "صرف" if float(x) < 0 else "تسوية")
        df_data["qty_abs"] = df_data[qty_col].abs()

    # رصيد نهائي لكل منتج/مستودع
    warehouse_col = df_data.columns[2] if len(df_data.columns) > 2 else "المستودع"
    last_bal = df_data.groupby(["product_name", warehouse_col]).last().reset_index()

    return df_data, last_bal, warehouse_col


def _normalize_code(val):
    """تحويل الكود لنص رقمي موحد — بدون float عشان ما يخسرش الدقة"""
    s = str(val).strip()
    if 'e+' in s.lower() or 'e-' in s.lower():
        try: return str(int(float(s)))
        except: return s
    s = s.split('.')[0]
    return s if s.lstrip('-').isdigit() else str(val).strip()

def _map_journal_cols(df):
    """استخراج خريطة الأعمدة من ملف الحركات — يدعم أي تسمية"""
    col_map = {}
    for c in df.columns:
        cl = c.lower().strip()
        if any(k in cl for k in ["تاريخ", "date"]):          col_map["date"]     = c
        elif any(k in cl for k in ["رقم القيد", "entry_no", "entry no", "entryno"]): col_map["entry_no"] = c
        elif any(k in cl for k in ["account_code", "كود الحساب", "كود"]): col_map["code"]     = c
        elif any(k in cl for k in ["account_name", "اسم الحساب"]):         col_map["name"]     = c
        elif any(k in cl for k in ["وصف", "desc", "description", "بيان"]): col_map["desc"]     = c
        elif any(k in cl for k in ["مدين", "debit"]):         col_map["debit"]    = c
        elif any(k in cl for k in ["دائن", "credit"]):        col_map["credit"]   = c
    return col_map

def _is_person_name(name):
    """يحاول يكتشف لو الاسم اسم شخص"""
    import re
    arabic_words = len(re.findall(r'[؀-ۿ]+', name))
    has_title = any(t in name for t in ["م.", "م .", "ا.", "أ.", "د.", "أ/", "ا/", "عم ", "Mr", "Ms"])
    long_enough = len(name.split()) >= 2
    return (arabic_words >= 2 and long_enough) or has_title

def _classify_account(code, name, total_d, total_c, tree_rows):
    """
    يحاول يصنف الحساب الجديد ويقترح الحساب الرئيسي الأنسب.
    يعتمد على: prefix الكود + نسبة مدين/دائن + اسم الحساب
    """
    import re
    name = str(name or "").strip()

    # 1. prefix matching أولاً
    best_code = None; best_name = ""; best_path = []; best_len = 0
    for row in tree_rows:
        rc = str(row[0]).strip()
        if code.startswith(rc) and len(rc) > best_len and len(rc) < len(code):
            best_len = len(rc); best_code = rc
            best_name = str(row[1]).strip()
            best_path = [str(row[i+2] or "").strip() for i in range(6) if str(row[i+2] or "").strip()]

    # 2. لو prefix مش كافي — نحاول classify بالسياق
    reason = ""
    if best_len >= 4:
        conf = "high"
        reason = f"prefix مطابق ({best_len} أرقام)"
    else:
        # نحاول تصنيف ذكي
        is_person = _is_person_name(name)
        net = total_d - total_c  # موجب = مدين = عميل، سالب = دائن = مورد

        # ابحث عن حسابات مناسبة في الشجرة
        candidate = None
        # كلمات دالة في الاسم
        name_lower = name.lower()
        if any(k in name for k in ["عميل","مدين","مشتر"]):
            key = "عملاء"
        elif any(k in name for k in ["مورد","مورّد","موّرد","بائع"]):
            key = "موردين"
        elif any(k in name for k in ["شريك","شركاء","جاري"]):
            key = "شركاء"
        elif is_person and net > 0:
            key = "عملاء"   # شخص + مدين = عميل غالباً
        elif is_person and net < 0:
            key = "موردين"  # شخص + دائن = مورد غالباً
        elif is_person:
            key = "عملاء"   # default للأشخاص
        else:
            key = None

        if key:
            for row in tree_rows:
                rn = str(row[1] or "").strip()
                if key in rn:
                    candidate = row
                    break

        if candidate:
            best_code = str(candidate[0]).strip()
            best_name = str(candidate[1]).strip()
            best_path = [str(candidate[i+2] or "").strip() for i in range(6) if str(candidate[i+2] or "").strip()]
            conf = "high" if is_person else "medium"
            reason = f"{'اسم شخص' if is_person else 'تصنيف تلقائي'} → {key} ({'مدين' if net>=0 else 'دائن'})"
        else:
            conf = "low" if best_code else "none"
            reason = "لم يتم التعرف"

    return best_code, best_name, best_path, conf, reason


def find_parent_by_prefix(new_code, tree_rows, name="", total_d=0, total_c=0):
    """Wrapper للتوافق مع الكود القديم"""
    code, n, path, conf, reason = _classify_account(new_code, name, total_d, total_c, tree_rows)
    return code, n, path, conf


def preview_journal_df(df, company_id=1):
    """فحص الملف قبل الاستيراد مع اقتراح parent لكل كود جديد"""
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    col_map = _map_journal_cols(df)

    conn = get_conn()
    tree_codes = set(_normalize_code(r[0]) for r in conn.execute("SELECT code FROM chart_of_accounts WHERE company_id=%s", (company_id,)).fetchall())
    tree_rows  = conn.execute("SELECT code, name, level1, level2, level3, level4, level5, level6, acc_level FROM chart_of_accounts WHERE company_id=%s", (company_id,)).fetchall()
    j_total_now = conn.execute("SELECT COUNT(*) FROM journal_lines WHERE company_id=%s", (company_id,)).fetchone()[0]
    conn.close()

    total = 0
    in_tree_count = 0
    not_in_tree_count = 0
    total_d = total_c = 0.0
    missing_codes = {}

    for _, r in df.iterrows():
        code_col = col_map.get("code")
        code = _normalize_code(r[code_col]) if code_col and pd.notna(r.get(code_col)) else ""
        d = float(r[col_map["debit"]])  if col_map.get("debit")  and pd.notna(r.get(col_map["debit"]))  else 0.0
        c = float(r[col_map["credit"]]) if col_map.get("credit") and pd.notna(r.get(col_map["credit"])) else 0.0
        total_d += d; total_c += c; total += 1

        if code in tree_codes:
            in_tree_count += 1
        else:
            not_in_tree_count += 1
            name_col = col_map.get("name")
            name = str(r[name_col]).strip() if name_col and pd.notna(r.get(name_col)) else code
            if code not in missing_codes:
                missing_codes[code] = {
                    "name": name, "count": 0, "d": 0.0, "c": 0.0,
                    "suggested_parent": None, "suggested_parent_name": "",
                    "suggested_path": [], "confidence": "none", "reason": "",
                }
            missing_codes[code]["count"] += 1
            missing_codes[code]["d"] += d
            missing_codes[code]["c"] += c

    # الآن نعمل التصنيف الذكي بعد ما عرفنا الأرصدة الكاملة
    for code, info in missing_codes.items():
        pc, pn, pp, conf, reason = _classify_account(
            code, info["name"], info["d"], info["c"], tree_rows)
        info["suggested_parent"] = pc
        info["suggested_parent_name"] = pn
        info["suggested_path"] = pp
        info["confidence"] = conf
        info["reason"] = reason

    return {
        "total": total,
        "in_tree": in_tree_count,
        "not_in_tree": not_in_tree_count,
        "missing_codes": missing_codes,
        "total_d": total_d,
        "total_c": total_c,
        "j_total_now": j_total_now,
        "col_map": col_map,
    }


def add_new_codes_to_tree(confirmed_codes, co_id=1):
    """
    confirmed_codes: dict {new_code: {"name": ..., "parent_code": ...}}
    يضيف الكودات الجديدة للشجرة في مكانها الصح
    """
    conn = get_conn()
    added = []
    for code, info in confirmed_codes.items():
        parent_code = info.get("parent_code", "")
        if parent_code == "__skip__": continue  # تجاهل
        name = info.get("name", code)
        # جلب بيانات الـ parent
        parent_row = conn.execute(
            "SELECT level1,level2,level3,level4,level5,level6,acc_level FROM chart_of_accounts WHERE code=%s AND company_id=%s",
            (str(parent_code), co_id)).fetchone()
        if not parent_row:
            continue
        levels = [str(parent_row[i] or "").strip() for i in range(6)]
        parent_lvl = int(parent_row[6])
        new_lvl = parent_lvl + 1
        if new_lvl > 6:
            continue
        levels[new_lvl - 1] = name
        try:
            conn.execute(
                "INSERT IGNORE INTO chart_of_accounts "
                "(company_id,level1,level2,level3,level4,level5,level6,code,name,acc_level,is_leaf,parent_code) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,1,%s)",
                (co_id, *levels, code, name, new_lvl, parent_code))
            conn.execute("UPDATE chart_of_accounts SET is_leaf=0 WHERE code=%s AND company_id=%s", (parent_code, co_id))
            added.append(code)
        except Exception:
            pass
    conn.commit()
    conn.close()
    load_all_accounts.clear(); get_cumulative_balances_all.clear(); get_all_leaf_accounts.clear()
    return added


def import_journal_df(df, mode="add", company_id=1):
    """استيراد الحركات — يستورد كل الحركات اللي كودها موجود في الشجرة"""
    conn = get_conn()
    if mode == "replace":
        conn.execute("DELETE FROM journal_entries WHERE company_id=%s", (company_id,)); conn.commit()

    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    col_map = _map_journal_cols(df)

    tree_codes = set(_normalize_code(r[0]) for r in conn.execute("SELECT code FROM chart_of_accounts WHERE company_id=%s", (company_id,)).fetchall())

    rows = []
    skipped = {}

    for _, r in df.iterrows():
        def g(k):
            col = col_map.get(k)
            return str(r[col]).strip() if col and pd.notna(r.get(col)) else ""
        def gn(k):
            col = col_map.get(k)
            try: return float(r[col]) if col and pd.notna(r.get(col)) else 0.0
            except: return 0.0

        code = _normalize_code(g("code")) if g("code") else ""
        acc_name = g("name")

        if not code or code not in tree_codes:
            key = code or "(فاضي)"
            if key not in skipped: skipped[key] = {"name": acc_name, "count": 0}
            skipped[key]["count"] += 1
            continue

        rows.append((g("date"), g("entry_no"), code, acc_name, g("desc"), gn("debit"), gn("credit"), "excel"))

    # INSERT في journal_entries ثم journal_lines
    rows_with_co = [(company_id, *r) for r in rows]
    seen = set()
    entry_rows = []
    for r in rows_with_co:
        co_id2, date, entry_no, code2, acc_name, desc, debit, credit, source = r
        if entry_no not in seen:
            seen.add(entry_no)
            entry_rows.append((entry_no, date, desc, source, "posted", co_id2, "excel"))
    conn.executemany(
        "INSERT IGNORE INTO journal_entries (entry_no,entry_date,description,source,company_id) "
        "VALUES (%s,%s,%s,%s,%s)", [(r[0],r[1],r[2],r[3],r[5]) for r in entry_rows])
    conn.commit()
    cur2 = conn.cursor()
    cur2.execute("SELECT id, entry_no FROM journal_entries WHERE company_id=%s", (company_id,))
    id_map2 = {r[1]: r[0] for r in cur2.fetchall()}
    line_rows2 = []
    for r in rows_with_co:
        co_id2, date, entry_no, code2, acc_name, desc, debit, credit, source = r
        eid = id_map2.get(entry_no)
        if eid:
            line_rows2.append((eid, entry_no, code2, acc_name, debit, credit, desc, co_id2))
    conn.executemany(
        "INSERT INTO journal_lines (entry_id,entry_no,account_code,account_name,debit,credit,notes,company_id) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", line_rows2)
    conn.commit()
    get_cumulative_balances_all.clear(); get_all_leaf_accounts.clear(); load_all_accounts.clear()
    conn.close()
    return len(rows), skipped

# ══════════════════ Init ══════════════════
init_db()

if "drill_path"    not in st.session_state: st.session_state.drill_path    = []
if "adding_to"     not in st.session_state: st.session_state.adding_to     = None
if "editing_code"  not in st.session_state: st.session_state.editing_code  = None
if "expanded"      not in st.session_state: st.session_state.expanded       = {}

# ══════════════════ Sidebar ══════════════════
with st.sidebar:
    st.markdown('<div class="sidebar-logo">📒 المحاسبي</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="user-info">👤 {user_info["name"]}<br><span style="color:#94a3b8;font-size:.75rem">{user_info["role"]}</span></div>', unsafe_allow_html=True)

    # ── اختيار الشركة ──
    companies_df = get_companies()
    if not companies_df.empty:
        co_names = companies_df["name"].tolist()
        co_ids   = companies_df["id"].tolist()
        active_co_id = get_active_company_id()
        active_idx = co_ids.index(active_co_id) if active_co_id in co_ids else 0
        st.markdown('<p class="sidebar-section">الشركة النشطة</p>', unsafe_allow_html=True)
        selected_co = st.selectbox("", co_names, index=active_idx,
                                   key="co_select", label_visibility="collapsed")
        new_co_id = co_ids[co_names.index(selected_co)]
        if new_co_id != st.session_state.get("active_company"):
            st.session_state.active_company = new_co_id
            load_all_accounts.clear(); get_cumulative_balances_all.clear(); get_all_leaf_accounts.clear()
            st.rerun()
        co_id = new_co_id
    else:
        co_id = 1

    st.markdown('<p class="sidebar-section">القائمة الرئيسية</p>', unsafe_allow_html=True)
    pages = [
        "🏠  الرئيسية",
        "📋  دليل الحسابات",
        "⚖️  ميزان المراجعة",
        "📒  دفتر الأستاذ",
        "📑  القيود اليومية",
        "📊  مراكز التكلفة",
        "🔬  تقرير التكلفة المدمج",
        "📦  المخزن والمستندات",
        "🔗  إدارة التطابق",
        "🔀  ربط الاذونات بالقيود",
        "💸  المصروفات",
        "💰  سندات القبض",
    ]
    if is_admin:
        pages += ["🏢  إدارة الشركات"]
    page = st.radio("nav", pages, label_visibility="collapsed")

    # ── إحصائيات ──
    st.markdown("<div style='height:1px;background:rgba(255,255,255,.08);margin:.8rem .8rem'></div>", unsafe_allow_html=True)
    total, leaves, _, j_total = get_stats(co_id)
    st.markdown(f"""
    <div style="padding:.2rem 1rem .8rem">
        <div style="display:flex;justify-content:space-between;padding:.3rem 0;border-bottom:1px solid rgba(255,255,255,.06)">
            <span style="color:#64748b;font-size:.78rem">الحسابات</span>
            <b style="color:#94a3b8;font-size:.78rem">{total:,}</b>
        </div>
        <div style="display:flex;justify-content:space-between;padding:.3rem 0;border-bottom:1px solid rgba(255,255,255,.06)">
            <span style="color:#64748b;font-size:.78rem">النهائية</span>
            <b style="color:#94a3b8;font-size:.78rem">{leaves:,}</b>
        </div>
        <div style="display:flex;justify-content:space-between;padding:.3rem 0">
            <span style="color:#64748b;font-size:.78rem">الحركات</span>
            <b style="color:#94a3b8;font-size:.78rem">{j_total:,}</b>
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
    if st.button("🚪 تسجيل الخروج", use_container_width=True):
        st.session_state["authenticated"] = False
        st.session_state["user_info"] = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

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
        with col_s: save   = st.form_submit_button("💾 حفظ",   use_container_width=True)
        with col_c: cancel = st.form_submit_button("❌ إلغاء", use_container_width=True)
        if save:
            if not new_code or not new_name: st.error("الكود والاسم مطلوبان")
            else:
                ok,msg = add_account(parent_row, new_code, new_name, acc_type)
                if ok: st.success(msg); st.session_state.adding_to = None; st.rerun()
                else: st.error(msg)
        if cancel:
            st.session_state.adding_to = None; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════ Edit/Delete ══════════════════
def render_edit_delete_inline(code):
    conn = get_conn()
    df_r = pd.read_sql("SELECT * FROM chart_of_accounts WHERE code=%s AND company_id=%s", conn, params=(str(code), co_id))
    conn.close()
    if df_r.empty: st.session_state.editing_code = None; return
    r = df_r.iloc[0]
    path = get_path(r)
    conn2 = get_conn()
    is_leaf = conn2.execute("SELECT is_leaf FROM chart_of_accounts WHERE code=%s AND company_id=%s", (str(code), co_id)).fetchone()
    is_leaf = int(is_leaf[0]) == 1 if is_leaf else True
    conn2.close()
    has_tx = has_transactions(code, co_id)
    cumulative = get_cumulative_balances_all(co_id)
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
        if st.button("✖️ إغلاق", key=f"close_{code}"): st.session_state.editing_code = None; st.rerun()
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
                        conn.execute("UPDATE chart_of_accounts SET level1=%s,level2=%s,level3=%s,level4=%s,level5=%s,level6=%s,code=%s,name=%s WHERE id=%s",
                            (*levels,new_code,new_name,r["id"]))
                        conn.commit()
                        load_all_accounts.clear(); get_cumulative_balances_all.clear(); get_all_leaf_accounts.clear()
                        st.session_state.editing_code = None; st.success("✅ تم التعديل"); st.rerun()
                    except mysql.connector.errors.IntegrityError: st.error("❌ الكود مستخدم بالفعل")
                    finally: conn.close()
            with col_c:
                if st.form_submit_button("❌ إلغاء", use_container_width=True):
                    st.session_state.editing_code = None; st.rerun()
    with tab2:
        if not is_leaf:
            st.error("❌ لا يمكن حذف حساب رئيسي — احذف الحسابات الفرعية أولاً")
        else:
            st.markdown(f'<div style="background:#fff3cd;border:1px solid #f59f00;border-radius:8px;padding:0.8rem 1.2rem;color:#7d4e00;font-weight:700;font-size:1rem;direction:rtl">⚠️ هتحذف الحساب: {r["name"]}</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            col_d,col_c2 = st.columns(2)
            with col_d:
                if st.button("🗑️ تأكيد الحذف", type="primary", use_container_width=True):
                    delete_account_db(code, str(r.get("parent_code","")))
                    st.session_state.editing_code = None; st.success("✅ تم الحذف"); st.rerun()
            with col_c2:
                if st.button("❌ إلغاء", use_container_width=True, key=f"cancel_del_{code}"):
                    st.session_state.editing_code = None; st.rerun()

# ══════════════════ Expandable Tree ══════════════════
def render_tree(parent_code=None, depth=0):
    cumulative = get_cumulative_balances_all(co_id)

    if parent_code is None:
        conn = get_conn()
        current_df = pd.read_sql(
            "SELECT * FROM chart_of_accounts WHERE acc_level=1 AND company_id=%s ORDER BY CAST(code AS UNSIGNED)",
            conn, params=(co_id,))
        conn.close()
    else:
        current_df = get_children_by_parent(parent_code, co_id)

    if current_df.empty:
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
        is_expanded = st.session_state.expanded.get(code, False)

        col1, col2, col3 = st.columns([5, 2, 1])
        with col1:
            if is_leaf:
                st.markdown(
                    f'<div style="padding:0.5rem 0.8rem;margin:{depth*8}px 0 2px {depth*20}px;background:white;border-radius:8px;border-right:3px solid #e8ecf8;color:#374151;font-size:0.9rem">📄 &nbsp;{name}</div>',
                    unsafe_allow_html=True)
            else:
                arrow = "▼" if is_expanded else "◀"
                label = f"{arrow} {icon}  {name}"
                if st.button(label, key=f"tree_{code}", use_container_width=True):
                    st.session_state.expanded[code] = not is_expanded
                    st.session_state.adding_to = None
                    st.rerun()
        with col2:
            if has_bal:
                st.markdown(
                    f'<div style="text-align:left;padding-top:6px"><b style="color:{color}">{abs(bal):,.2f}</b><br><span style="font-size:.72rem;color:{color}">{lbl}</span></div>',
                    unsafe_allow_html=True)
            else:
                st.markdown('<div style="text-align:left;padding-top:10px;color:#ccc">—</div>', unsafe_allow_html=True)
        with col3:
            if is_admin:
                if st.button("⚙️", key=f"edit_{code}", help="تعديل أو حذف"):
                    st.session_state.editing_code = code
                    st.rerun()

        if not is_leaf and is_expanded:
            render_tree(code, depth+1)
            if is_admin and int(r.get("acc_level",1)) < 5:
                if st.session_state.adding_to == code:
                    parent_row = get_account_by_code(code, co_id)
                    if parent_row is not None:
                        render_add_form(parent_row)
                else:
                    cols_add = st.columns([1, 5])
                    with cols_add[1]:
                        if st.button(f"➕ إضافة تحت: {name}", key=f"add_{code}", use_container_width=True):
                            st.session_state.adding_to = code
                            st.rerun()

    if st.session_state.editing_code:
        render_edit_delete_inline(st.session_state.editing_code)

def render_drill_down(parent_code=None):
    render_tree(parent_code, depth=0)

# ══════════════════ Pages ══════════════════

if page == "🏠  الرئيسية":
    st.markdown('<div class="page-header"><p class="ph-title">🏠 لوحة التحكم</p><p class="ph-sub">نظرة عامة على النظام المحاسبي</p></div>', unsafe_allow_html=True)
    total,leaves,by_l1,j_total = get_stats(co_id)
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
    with col2: l1_filter = st.selectbox("القسم الرئيسي", get_l1_opts(co_id))
    if search or l1_filter != "الكل":
        df = load_accounts(search, l1_filter, co_id)
        cumulative = get_cumulative_balances_all(co_id)
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
        st.dataframe(pd.DataFrame(rows_display), use_container_width=True, hide_index=True, height=600)
        csv = df.to_csv(index=False, encoding="utf-8-sig")
        st.download_button("⬇️ تحميل CSV", data=csv, file_name="شجرة_الحسابات.csv", mime="text/csv")
    else:
        current_code = st.session_state.drill_path[-1][0] if st.session_state.drill_path else None
        render_drill_down(current_code)

elif page == "⚖️  ميزان المراجعة":
    st.markdown('<div class="page-header"><p class="ph-title">⚖️ ميزان المراجعة</p><p class="ph-sub">إجمالي المدين والدائن لكل حساب</p></div>', unsafe_allow_html=True)

    # ── أزرار المستويات ──
    if "tb_max_level" not in st.session_state: st.session_state.tb_max_level = 6
    btn_cols = st.columns([1,1,1,1,1,1,2,1,1])
    if btn_cols[0].button("مستوى 1", key="lvl1", use_container_width=True): st.session_state.tb_max_level = 1
    if btn_cols[1].button("مستوى 2", key="lvl2", use_container_width=True): st.session_state.tb_max_level = 2
    if btn_cols[2].button("مستوى 3", key="lvl3", use_container_width=True): st.session_state.tb_max_level = 3
    if btn_cols[3].button("مستوى 4", key="lvl4", use_container_width=True): st.session_state.tb_max_level = 4
    if btn_cols[4].button("مستوى 5", key="lvl5", use_container_width=True): st.session_state.tb_max_level = 5
    if btn_cols[5].button("مستوى 6", key="lvl6", use_container_width=True): st.session_state.tb_max_level = 6
    show_zero = False
    with btn_cols[7]: l1_tb = st.selectbox("", get_l1_opts(co_id), key="tb_l1", label_visibility="collapsed")
    max_level = st.session_state.tb_max_level
    view_mode = "كل الحسابات"

    # ── جلب البيانات ──
    conn = get_conn()
    all_accs = pd.read_sql("""
        SELECT c.code, c.name, c.acc_level, c.is_leaf,
               c.level1, c.level2, c.level3, c.level4, c.level5, c.level6,
               c.parent_code,
               COALESCE(SUM(j.debit),0)  AS direct_d,
               COALESCE(SUM(j.credit),0) AS direct_c
        FROM chart_of_accounts c
        LEFT JOIN journal_lines j ON c.code = j.account_code
        GROUP BY c.code, c.name, c.acc_level, c.is_leaf,
               c.level1, c.level2, c.level3, c.level4, c.level5, c.level6,
               c.parent_code
        ORDER BY c.code
    """, conn)
    orphan_df = pd.read_sql("""
        SELECT account_code, account_name,
               COALESCE(SUM(debit),0) orphan_d, COALESCE(SUM(credit),0) orphan_c
        FROM journal_lines
        WHERE account_code NOT IN (SELECT code FROM chart_of_accounts)
        GROUP BY account_code, account_name
    """, conn)
    conn.close()

    # ── حساب الأرصدة التراكمية (leaf → parent) ──
    balances = {}
    for _, r in all_accs.iterrows():
        balances[str(r["code"])] = [float(r["direct_d"]), float(r["direct_c"])]

    for _, r in all_accs.sort_values("acc_level", ascending=False).iterrows():
        code   = str(r["code"])
        parent = str(r["parent_code"] or "").strip()
        if parent and parent in balances:
            balances[parent][0] += balances[code][0]
            balances[parent][1] += balances[code][1]

    all_accs["total_debit"]  = all_accs["code"].apply(lambda c: balances.get(str(c),[0,0])[0])
    all_accs["total_credit"] = all_accs["code"].apply(lambda c: balances.get(str(c),[0,0])[1])
    all_accs["bal"]          = all_accs["total_debit"] - all_accs["total_credit"]

    # ── فلترة ──
    if l1_tb != "الكل":
        all_accs = all_accs[all_accs["level1"] == l1_tb]
    tb_show = all_accs[all_accs["acc_level"] <= max_level].copy()
    if not show_zero:
        tb_show = tb_show[(tb_show["total_debit"] > 0) | (tb_show["total_credit"] > 0)]

    # ── إجماليات ──
    # الإجمالي من كل الحركات المباشرة (direct) بغض النظر عن leaf/parent
    total_d = all_accs["direct_d"].sum()
    total_c = all_accs["direct_c"].sum()
    diff    = abs(total_d - total_c)
    is_bal  = diff < 0.01

    # ── بطاقات الإجماليات ──
    col1, col2, col3 = st.columns(3)
    with col1: st.markdown(f'<div class="stat-card red"><div class="s-num" style="color:#c92a2a">{total_d:,.2f}</div><div class="s-lbl">إجمالي المدين</div></div>', unsafe_allow_html=True)
    with col2: st.markdown(f'<div class="stat-card green"><div class="s-num" style="color:#2f9e44">{total_c:,.2f}</div><div class="s-lbl">إجمالي الدائن</div></div>', unsafe_allow_html=True)
    with col3:
        status = "✅ متوازن" if is_bal else f"❌ فرق: {diff:,.2f}"
        color  = "#2f9e44" if is_bal else "#c92a2a"
        st.markdown(f'<div class="stat-card"><div class="s-num" style="color:{color};font-size:1.1rem">{status}</div><div class="s-lbl">حالة الميزان</div></div>', unsafe_allow_html=True)

    if not orphan_df.empty:
        codes_list = ", ".join(orphan_df["account_code"].astype(str).tolist())
        st.markdown(f'<div class="warning-box" style="margin-top:.8rem">⚠️ {len(orphan_df)} حساب خارج الشجرة ({codes_list})</div>', unsafe_allow_html=True)

    if tb_show.empty:
        st.info("لا توجد بيانات")
    else:
        st.markdown("<br>", unsafe_allow_html=True)

        # ── جدول الميزان بتصميم دفترة ──
        rows_html = ""
        for _, r in tb_show.iterrows():
            lvl    = int(r["acc_level"])
            indent = (lvl - 1) * 20
            is_lf  = int(r["is_leaf"]) == 1
            d_val  = f"{r['total_debit']:,.2f}"  if r["total_debit"]  > 0 else "—"
            c_val  = f"{r['total_credit']:,.2f}" if r["total_credit"] > 0 else "—"
            bal    = r["bal"]
            bal_color = "#c92a2a" if bal >= 0 else "#2f9e44"
            bal_type  = "مدين" if bal >= 0 else "دائن"
            bal_val   = f"{abs(bal):,.2f}" if (r['total_debit']+r['total_credit']) > 0 else "—"
            fw        = "700" if not is_lf else "400"
            bg        = "#f8faff" if not is_lf else "white"
            icon      = "📄" if is_lf else "📁"

            rows_html += f"""
            <tr style="background:{bg};border-bottom:1px solid #f0f2f8">
                <td style="padding:.55rem .8rem;font-weight:{fw};color:#1e2a4a;direction:rtl">
                    <span style="display:inline-block;width:{indent}px"></span>
                    <span style="font-size:.75rem;margin-left:4px">{icon}</span>
                    {r['name']}
                </td>
                <td style="padding:.55rem .8rem;color:#5a6a8a;font-size:.82rem;text-align:center">{r['code']}</td>
                <td style="padding:.55rem .8rem;color:#c92a2a;text-align:left;font-family:monospace">{d_val}</td>
                <td style="padding:.55rem .8rem;color:#2f9e44;text-align:left;font-family:monospace">{c_val}</td>
                <td style="padding:.55rem .8rem;color:{bal_color};text-align:left;font-family:monospace;font-weight:600">{bal_val}</td>
                <td style="padding:.55rem .8rem;color:{bal_color};text-align:center;font-size:.78rem">{bal_type if bal_val!="—" else "—"}</td>
            </tr>"""

        st.markdown(f"""
        <div style="background:white;border-radius:12px;overflow:hidden;box-shadow:0 1px 8px rgba(0,0,0,.06)">
        <table style="width:100%;border-collapse:collapse;direction:rtl">
            <thead>
                <tr style="background:#1e2a4a;color:white">
                    <th style="padding:.7rem 1rem;text-align:right;font-weight:700;font-size:.85rem">الاسم</th>
                    <th style="padding:.7rem .8rem;text-align:center;font-weight:700;font-size:.85rem">الكود</th>
                    <th style="padding:.7rem .8rem;text-align:left;font-weight:700;font-size:.85rem">مدين (EGP)</th>
                    <th style="padding:.7rem .8rem;text-align:left;font-weight:700;font-size:.85rem">دائن (EGP)</th>
                    <th style="padding:.7rem .8rem;text-align:left;font-weight:700;font-size:.85rem">الرصيد (EGP)</th>
                    <th style="padding:.7rem .8rem;text-align:center;font-weight:700;font-size:.85rem">النوع</th>
                </tr>
            </thead>
            <tbody>{rows_html}</tbody>
        </table>
        </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        csv_data = tb_show[["code","name","acc_level","total_debit","total_credit","bal"]].copy()
        csv_data.columns = ["الكود","الاسم","المستوى","مدين","دائن","الرصيد"]
        st.download_button("⬇️ تحميل ميزان المراجعة", data=csv_data.to_csv(index=False, encoding="utf-8-sig"),
                           file_name="ميزان_المراجعة.csv", mime="text/csv")

elif page == "📒  دفتر الأستاذ":
    st.markdown('<div class="page-header"><p class="ph-title">📒 دفتر الأستاذ</p><p class="ph-sub">حركات كل حساب مدين ودائن</p></div>', unsafe_allow_html=True)

    # ── بحث واختيار الحساب من جدول ──
    if "led_selected" not in st.session_state: st.session_state.led_selected = None

    conn_led = get_conn()
    all_accs_led = pd.read_sql(
        "SELECT code, name, acc_level, is_leaf, level1, level2 FROM chart_of_accounts WHERE company_id=%s AND is_leaf=1 ORDER BY CAST(code AS UNSIGNED)",
        conn_led, params=(co_id,))
    conn_led.close()

    if all_accs_led.empty:
        st.info("لا توجد حسابات"); selected_code = None
    else:
        # ── فلاتر ──
        f1, f2, f3, f4, f5 = st.columns([2, 2, 3, 1, 1])

        # فلتر الحساب الرئيسي (level1)
        with f1:
            l1_opts = ["كل الأقسام"] + sorted(all_accs_led["level1"].dropna().unique().tolist())
            sel_l1 = st.selectbox("القسم الرئيسي", l1_opts, key="led_l1", label_visibility="visible")

        # فلتر الحساب الفرعي (level2) — يتغير حسب l1
        with f2:
            if sel_l1 != "كل الأقسام":
                l2_opts = ["كل الفروع"] + sorted(all_accs_led[all_accs_led["level1"]==sel_l1]["level2"].dropna().unique().tolist())
            else:
                l2_opts = ["كل الفروع"] + sorted(all_accs_led["level2"].dropna().unique().tolist())
            sel_l2 = st.selectbox("الفرع", l2_opts, key="led_l2", label_visibility="visible")

        # فلتر التاريخ
        with f3:
            date_range_led = st.date_input("الفترة", value=[], key="led_dates",
                                           label_visibility="visible")

        with f4:
            search_q = st.text_input("", key="led_search",
                                     placeholder="🔍 بحث...", label_visibility="collapsed")
        with f5:
            if st.button("✖️ مسح", key="led_clear_sel", use_container_width=True):
                st.session_state.led_selected = None
                st.rerun()

        # تطبيق فلتر الحساب الرئيسي والفرعي
        filtered_led = all_accs_led.copy()
        if sel_l1 != "كل الأقسام":
            filtered_led = filtered_led[filtered_led["level1"] == sel_l1]
        if sel_l2 != "كل الفروع":
            filtered_led = filtered_led[filtered_led["level2"] == sel_l2]
        if search_q:
            mask = (filtered_led["name"].str.contains(search_q, case=False, na=False) |
                    filtered_led["code"].str.contains(search_q, case=False, na=False))
            filtered_led = filtered_led[mask]

        # تطبيق فلتر التاريخ على الحركات
        date_from_led = str(date_range_led[0]) if len(date_range_led) >= 1 else None
        date_to_led   = str(date_range_led[1]) if len(date_range_led) >= 2 else None

        # الحساب المحدد حالياً
        selected_code = st.session_state.led_selected
        if selected_code:
            sel_row = all_accs_led[all_accs_led["code"] == selected_code]
            sel_name = sel_row.iloc[0]["name"] if not sel_row.empty else selected_code
            st.markdown(f'<div style="background:#e8f0fe;border-radius:8px;padding:.5rem 1rem;margin-bottom:.5rem;font-weight:700;color:#1e2a4a;direction:rtl">📄 محدد: {sel_name} ({selected_code})</div>', unsafe_allow_html=True)

        # جدول الحسابات
        if not filtered_led.empty and (search_q or not selected_code):
            cumulative = get_cumulative_balances_all(co_id)
            rows_led = ""
            for _, ac in filtered_led.head(50).iterrows():
                ac_code = str(ac["code"]); ac_name = str(ac["name"])
                d, c = cumulative.get(ac_code, (0, 0)); bal = d - c
                is_sel = ac_code == selected_code
                bg = "#e8f0fe" if is_sel else ("white" if _ % 2 == 0 else "#f8faff")
                bal_clr = "#c92a2a" if bal >= 0 else "#2f9e44"
                bal_str = f"{abs(bal):,.2f}" if (d+c) > 0 else "—"
                bal_lbl = ("مدين" if bal >= 0 else "دائن") if (d+c) > 0 else ""
                rows_led += f'''<tr style="background:{bg};border-bottom:1px solid #f0f2f8;cursor:pointer"
                    onclick="">
                    <td style="padding:.45rem .8rem;color:#3b5bdb;font-weight:700;font-size:.85rem">{ac_code}</td>
                    <td style="padding:.45rem .8rem;color:#1e2a4a;font-size:.88rem">{ac_name}</td>
                    <td style="padding:.45rem .8rem;color:#7a8fc0;font-size:.78rem">{ac.get("level1","")}</td>
                    <td style="padding:.45rem .8rem;color:{bal_clr};text-align:left;font-family:monospace;font-size:.85rem">{bal_str}</td>
                    <td style="padding:.45rem .8rem;color:{bal_clr};font-size:.78rem">{bal_lbl}</td>
                </tr>'''

            st.markdown(f"""
            <div style="background:white;border-radius:10px;overflow:hidden;box-shadow:0 1px 6px rgba(0,0,0,.06);max-height:320px;overflow-y:auto;margin-bottom:.5rem">
            <table style="width:100%;border-collapse:collapse;direction:rtl">
                <thead><tr style="background:#1e2a4a;color:white;position:sticky;top:0">
                    <th style="padding:.5rem .8rem;text-align:right;font-size:.8rem">الكود</th>
                    <th style="padding:.5rem .8rem;text-align:right;font-size:.8rem">الحساب</th>
                    <th style="padding:.5rem .8rem;text-align:right;font-size:.8rem">القسم</th>
                    <th style="padding:.5rem .8rem;text-align:left;font-size:.8rem">الرصيد</th>
                    <th style="padding:.5rem .8rem;font-size:.8rem"></th>
                </tr></thead>
                <tbody>{rows_led}</tbody>
            </table></div>""", unsafe_allow_html=True)

            # أزرار الاختيار (مخفية مرئياً تعمل كـ selector)
            btn_cols = st.columns(min(len(filtered_led.head(50)), 6))
            for i, (_, ac) in enumerate(filtered_led.head(50).iterrows()):
                ac_code = str(ac["code"])
                with btn_cols[i % len(btn_cols)]:
                    if st.button(f"{ac_code}", key=f"sel_ac_{ac_code}_{co_id}", use_container_width=True):
                        st.session_state.led_selected = ac_code
                        st.rerun()

    if selected_code:
            r    = get_account_by_code(selected_code, co_id)
            code = str(r["code"]); name = str(r["name"])
            path = get_path(r)

            conn = get_conn()
            j_query = """SELECT jl.id, jl.entry_no, jl.account_code, jl.account_name,
                jl.debit, jl.credit, jl.notes,
                je.entry_date, je.description
                FROM journal_lines jl
                LEFT JOIN journal_entries je ON jl.entry_id = je.id
                WHERE jl.account_code=%s AND jl.company_id=%s"""
            j_params = [code, co_id]
            if date_from_led:
                j_query += " AND je.entry_date >= %s"; j_params.append(date_from_led)
            if date_to_led:
                j_query += " AND je.entry_date <= %s"; j_params.append(date_to_led)
            j_query += " ORDER BY jl.id"
            entries = pd.read_sql(j_query, conn, params=j_params)
            # لو مفيش فلتر تاريخ → آخر 10 حركات افتراضي
            if not date_from_led and not date_to_led and len(entries) > 10:
                entries = entries.tail(10).reset_index(drop=True)
            conn.close()

            total_d = entries["debit"].sum()
            total_c = entries["credit"].sum()
            bal     = total_d - total_c
            bal_lbl   = "مدين" if bal >= 0 else "دائن"
            bal_color = "#c92a2a" if bal >= 0 else "#2f9e44"

            # ── رأس الحساب بشكل دفترة ──
            path_html = " ← ".join(f'<span style="background:#e8f0fe;color:#2d3f6e;padding:2px 10px;border-radius:20px;font-size:.78rem">{p}</span>' for p in path)
            st.markdown(f"""
            <div style="background:white;border-radius:12px;padding:1.2rem 1.5rem;margin-bottom:1rem;
                        box-shadow:0 1px 8px rgba(0,0,0,.06);border-right:5px solid #3b5bdb">
                <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:1rem">
                    <div>
                        <div style="font-size:1.15rem;font-weight:900;color:#1e2a4a">📄 {name}</div>
                        <div style="margin-top:.4rem;direction:rtl">{path_html}</div>
                    </div>
                    <div style="display:flex;gap:2rem;flex-wrap:wrap;direction:rtl">
                        <div style="text-align:center">
                            <div style="font-size:1.2rem;font-weight:900;color:#c92a2a">{total_d:,.2f}</div>
                            <div style="font-size:.75rem;color:#7a8fc0">إجمالي المدين</div>
                        </div>
                        <div style="text-align:center">
                            <div style="font-size:1.2rem;font-weight:900;color:#2f9e44">{total_c:,.2f}</div>
                            <div style="font-size:.75rem;color:#7a8fc0">إجمالي الدائن</div>
                        </div>
                        <div style="text-align:center">
                            <div style="font-size:1.4rem;font-weight:900;color:{bal_color}">{abs(bal):,.2f}</div>
                            <div style="font-size:.75rem;color:{bal_color};font-weight:700">{bal_lbl}</div>
                        </div>
                        <div style="text-align:center">
                            <div style="font-size:1.2rem;font-weight:900;color:#1e2a4a">{len(entries):,}</div>
                            <div style="font-size:.75rem;color:#7a8fc0">عدد الحركات</div>
                        </div>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

            if entries.empty:
                st.markdown('<div class="info-box" style="text-align:center">لا توجد حركات على هذا الحساب</div>', unsafe_allow_html=True)
            else:
                entries = entries.copy()
                entries["running"] = (entries["debit"] - entries["credit"]).cumsum()

                # ── Popup القيد ──
                if "popup_entry_no" not in st.session_state:
                    st.session_state.popup_entry_no = None

                if st.session_state.popup_entry_no:
                    eno = st.session_state.popup_entry_no
                    conn_p = get_conn()
                    qeid_rows = pd.read_sql(
                        "SELECT account_code, account_name, description, debit, credit FROM journal_lines WHERE entry_no=%s AND company_id=%s ORDER BY id",
                        conn_p, params=(str(eno), co_id))
                    conn_p.close()
                    with st.expander(f"📋 تفاصيل القيد رقم {eno}", expanded=True):
                        qrows_html = ""
                        tot_d = tot_c = 0
                        for _, qr in qeid_rows.iterrows():
                            tot_d += qr["debit"]; tot_c += qr["credit"]
                            dv = f"{qr['debit']:,.2f}"  if qr["debit"]  > 0 else "—"
                            cv = f"{qr['credit']:,.2f}" if qr["credit"] > 0 else "—"
                            qrows_html += f"""
                            <tr style="border-bottom:1px solid #f0f2f8">
                                <td style="padding:.5rem .8rem;color:#1e2a4a;font-weight:600">{qr['account_name'] or qr['account_code']}</td>
                                <td style="padding:.5rem .8rem;color:#5a6a8a;font-size:.82rem">{qr['account_code']}</td>
                                <td style="padding:.5rem .8rem;color:#374151;font-size:.82rem">{str(qr['description'] or '')[:50]}</td>
                                <td style="padding:.5rem .8rem;color:#c92a2a;text-align:left;font-family:monospace">{dv}</td>
                                <td style="padding:.5rem .8rem;color:#2f9e44;text-align:left;font-family:monospace">{cv}</td>
                            </tr>"""
                        diff = abs(tot_d - tot_c)
                        bal_status = "✅ متوازن" if diff < 0.01 else f"❌ فرق: {diff:,.2f}"
                        bal_color_q = "#2f9e44" if diff < 0.01 else "#c92a2a"
                        st.markdown(f"""
                        <table style="width:100%;border-collapse:collapse;direction:rtl;background:white;border-radius:10px;overflow:hidden">
                            <thead><tr style="background:#1e2a4a;color:white">
                                <th style="padding:.6rem .8rem;text-align:right;font-size:.82rem">الحساب</th>
                                <th style="padding:.6rem .8rem;text-align:right;font-size:.82rem">الكود</th>
                                <th style="padding:.6rem .8rem;text-align:right;font-size:.82rem">البيان</th>
                                <th style="padding:.6rem .8rem;text-align:left;font-size:.82rem">مدين</th>
                                <th style="padding:.6rem .8rem;text-align:left;font-size:.82rem">دائن</th>
                            </tr></thead>
                            <tbody>{qrows_html}</tbody>
                            <tfoot><tr style="background:#f0f4ff;font-weight:900">
                                <td colspan="3" style="padding:.6rem .8rem;color:#1e2a4a">الإجمالي</td>
                                <td style="padding:.6rem .8rem;color:#c92a2a;text-align:left;font-family:monospace">{tot_d:,.2f}</td>
                                <td style="padding:.6rem .8rem;color:#2f9e44;text-align:left;font-family:monospace">{tot_c:,.2f}</td>
                            </tr>
                            <tr><td colspan="5" style="padding:.4rem .8rem;color:{bal_color_q};text-align:center;font-weight:700">{bal_status}</td></tr>
                            </tfoot>
                        </table>""", unsafe_allow_html=True)
                        if st.button("✖️ إغلاق", key="close_popup"): st.session_state.popup_entry_no = None; st.rerun()

                # ── جدول الحركات بشكل دفترة ──
                rows_html = ""
                btn_keys = []
                for idx, e in entries.iterrows():
                    d_val  = f"{e['debit']:,.2f}"  if e["debit"]  > 0 else "—"
                    c_val  = f"{e['credit']:,.2f}" if e["credit"] > 0 else "—"
                    rb     = e["running"]
                    rb_lbl = "مدين" if rb >= 0 else "دائن"
                    rb_clr = "#c92a2a" if rb >= 0 else "#2f9e44"
                    desc   = str(e["description"] or "").replace("\n"," ")[:60]
                    eno    = str(e["entry_no"] or "")
                    btn_keys.append((idx, eno))
                    rows_html += f"""
                    <tr style="border-bottom:1px solid #f0f2f8;cursor:pointer;transition:background .15s" onmouseover="this.style.background='#f8faff'" onmouseout="this.style.background='white'">
                        <td style="padding:.55rem 1rem;color:#374151;font-size:.85rem">{e['entry_date'] or ''}</td>
                        <td style="padding:.55rem .8rem;color:#3b5bdb;font-size:.82rem;text-align:center;font-weight:700;text-decoration:underline;cursor:pointer" title="اضغط لعرض القيد">🔍 {eno}</td>
                        <td style="padding:.55rem .8rem;color:#374151;font-size:.82rem;max-width:260px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{desc}</td>
                        <td style="padding:.55rem .8rem;color:#c92a2a;text-align:left;font-family:monospace;font-size:.85rem">{d_val}</td>
                        <td style="padding:.55rem .8rem;color:#2f9e44;text-align:left;font-family:monospace;font-size:.85rem">{c_val}</td>
                        <td style="padding:.55rem .8rem;color:{rb_clr};text-align:left;font-family:monospace;font-size:.85rem;font-weight:600">{abs(rb):,.2f}</td>
                        <td style="padding:.55rem .8rem;color:{rb_clr};text-align:center;font-size:.78rem">{rb_lbl}</td>
                    </tr>"""

                st.markdown(f"""
                <div style="background:white;border-radius:12px;overflow:hidden;box-shadow:0 1px 8px rgba(0,0,0,.06);max-height:620px;overflow-y:auto">
                <table style="width:100%;border-collapse:collapse;direction:rtl">
                    <thead style="position:sticky;top:0;z-index:1">
                        <tr style="background:#1e2a4a;color:white">
                            <th style="padding:.65rem 1rem;text-align:right;font-weight:700;font-size:.82rem;white-space:nowrap">التاريخ</th>
                            <th style="padding:.65rem .8rem;text-align:center;font-weight:700;font-size:.82rem">رقم القيد</th>
                            <th style="padding:.65rem .8rem;text-align:right;font-weight:700;font-size:.82rem">العملية</th>
                            <th style="padding:.65rem .8rem;text-align:left;font-weight:700;font-size:.82rem">مدين</th>
                            <th style="padding:.65rem .8rem;text-align:left;font-weight:700;font-size:.82rem">دائن</th>
                            <th style="padding:.65rem .8rem;text-align:left;font-weight:700;font-size:.82rem">الرصيد بعد</th>
                            <th style="padding:.65rem .8rem;text-align:center;font-weight:700;font-size:.82rem">النوع</th>
                        </tr>
                    </thead>
                    <tbody>{rows_html}</tbody>
                    <tfoot>
                        <tr style="background:#f0f4ff;border-top:2px solid #1e2a4a">
                            <td colspan="3" style="padding:.65rem 1rem;font-weight:900;color:#1e2a4a;font-size:.85rem">الإجمالي</td>
                            <td style="padding:.65rem .8rem;color:#c92a2a;font-family:monospace;font-weight:900;text-align:left">{total_d:,.2f}</td>
                            <td style="padding:.65rem .8rem;color:#2f9e44;font-family:monospace;font-weight:900;text-align:left">{total_c:,.2f}</td>
                            <td style="padding:.65rem .8rem;color:{bal_color};font-family:monospace;font-weight:900;text-align:left">{abs(bal):,.2f}</td>
                            <td style="padding:.65rem .8rem;color:{bal_color};font-weight:900;text-align:center;font-size:.82rem">{bal_lbl}</td>
                        </tr>
                    </tfoot>
                </table>
                </div>""", unsafe_allow_html=True)

                # ── أزرار رقم القيد ──
                st.markdown("<br>", unsafe_allow_html=True)
                unique_entries = entries["entry_no"].dropna().unique()
                if len(unique_entries) > 0:
                    st.markdown('<div style="font-size:.8rem;color:#7a8fc0;margin-bottom:.4rem">اضغط على رقم القيد لعرض تفاصيله:</div>', unsafe_allow_html=True)
                    btn_cols_per_row = 8
                    entry_list = list(unique_entries)
                    for i in range(0, len(entry_list), btn_cols_per_row):
                        cols = st.columns(btn_cols_per_row)
                        for j, eno in enumerate(entry_list[i:i+btn_cols_per_row]):
                            with cols[j]:
                                if st.button(str(eno), key=f"eno_btn_{eno}_{code}",
                                             use_container_width=True):
                                    st.session_state.popup_entry_no = str(eno)
                                    st.rerun()

                st.markdown("<br>", unsafe_allow_html=True)
                csv_out = pd.DataFrame({
                    "التاريخ": entries["entry_date"], "رقم القيد": entries["entry_no"],
                    "الوصف": entries["description"],
                    "مدين": entries["debit"], "دائن": entries["credit"],
                    "الرصيد التراكمي": entries["running"]
                })
                st.download_button(f"⬇️ تحميل دفتر {name}", data=csv_out.to_csv(index=False, encoding="utf-8-sig"),
                                   file_name=f"دفتر_{code}.csv", mime="text/csv")

elif page == "🏢  إدارة الشركات" and is_admin:
    st.markdown('<div class="page-header"><p class="ph-title">🏢 إدارة الشركات</p><p class="ph-sub">أضف وأدر شركاتك — بحد أقصى 5 شركات</p></div>', unsafe_allow_html=True)

    companies_df = get_companies()
    total_co, tree_co, _, j_co = get_stats(co_id)

    # ══ تدفق الإعداد الذكي ══
    has_tree = tree_co > 0
    has_journal = j_co > 0

    # ── الشركات الموجودة ──
    st.markdown('<div class="sec-title">الشركات المسجلة</div>', unsafe_allow_html=True)
    for _, co in companies_df.iterrows():
        co_stats = get_stats(co["id"])
        is_active = co["id"] == co_id
        bg = "white" if not is_active else "#e8f0fe"
        brd = "#3b5bdb" if is_active else "#e8ecf8"
        col1, col2, col3 = st.columns([4, 1, 1])
        with col1:
            st.markdown(f"""
            <div style="background:{bg};border-radius:10px;padding:.7rem 1.2rem;
                        border-right:4px solid {co['color']};border:1px solid {brd};
                        box-shadow:0 1px 4px rgba(0,0,0,.05)">
                <div style="font-weight:900;color:#1e2a4a;font-size:.95rem">
                    {"✅ " if is_active else ""}{co['name']}
                </div>
                <div style="color:#7a8fc0;font-size:.75rem;margin-top:2px">
                    🌳 {co_stats[0]:,} حساب &nbsp;|&nbsp; 📒 {co_stats[3]:,} حركة
                </div>
            </div>""", unsafe_allow_html=True)
        with col2:
            if not is_active:
                if st.button("🔀 تفعيل", key=f"act_{co['id']}", use_container_width=True):
                    st.session_state.active_company = co["id"]
                    load_all_accounts.clear(); get_cumulative_balances_all.clear(); get_all_leaf_accounts.clear()
                    st.rerun()
        with col3:
            if co["id"] != 1:
                if st.button("🗑️ حذف", key=f"del_{co['id']}", use_container_width=True):
                    if st.session_state.get(f"confirm_del_{co['id']}"):
                        delete_company(co["id"])
                        if st.session_state.get("active_company") == co["id"]:
                            st.session_state.active_company = 1
                        st.rerun()
                    else:
                        st.session_state[f"confirm_del_{co['id']}"] = True
                        st.warning(f"اضغط مرة ثانية لتأكيد حذف {co['name']}")

    # ── إضافة شركة ──
    if len(companies_df) < 5:
        with st.expander("➕ إضافة شركة جديدة"):
            with st.form("add_co_form"):
                co_name  = st.text_input("اسم الشركة *", placeholder="مثال: شركة الوفاء للتكيفات")
                co_color = st.color_picker("اللون", value="#3b5bdb")
                if st.form_submit_button("➕ إضافة", use_container_width=True):
                    if not co_name.strip(): st.error("❌ أدخل اسم الشركة")
                    else:
                        ok, msg = add_company(co_name.strip(), co_color)
                        if ok: st.success(msg); st.rerun()
                        else: st.error(msg)

    st.markdown("---")

    # ══ إعداد الشركة النشطة ══
    active_name = companies_df[companies_df["id"]==co_id]["name"].iloc[0] if not companies_df.empty else "الشركة"
    st.markdown(f'<div class="sec-title">⚙️ إعداد: {active_name}</div>', unsafe_allow_html=True)

    # ── مرحلة 1: شجرة الحسابات ──
    step1_done = has_tree
    with st.expander(f"{'✅' if step1_done else '1️⃣'} شجرة الحسابات — {total_co:,} حساب", expanded=not step1_done):
        if step1_done:
            st.markdown(f'<div class="success-box">✅ الشجرة مرفوعة — {total_co:,} حساب ({tree_co:,} نهائي)</div>', unsafe_allow_html=True)
                # ── شجرة الحسابات ──
        st.markdown('<div class="upload-box"><h4>🌳 رفع شجرة الحسابات</h4><p>ملف Excel فيه أعمدة: المستوى 1 ... المستوى 6، الكود</p></div>', unsafe_allow_html=True)
        uploaded = st.file_uploader("اختر ملف Excel", type=["xlsx","xls"], key="acc_up")
        if uploaded:
            try:
                df_up = pd.read_excel(uploaded, engine="openpyxl", dtype=str)
                st.success(f"✅ تم قراءة الملف — {len(df_up):,} سطر")
                st.dataframe(df_up.head(5), use_container_width=True)
                total_now,_,_,_ = get_stats(co_id)
                st.info(f"📊 الحسابات الموجودة حالياً: {total_now:,}")
                mode = tab_bar(["➕ أضف للموجود", "🔄 امسح وابدأ من أول"], "acc_mode")
                if st.button("🚀 استيراد شجرة الحسابات", use_container_width=True):
                    with st.spinner("جاري الاستيراد..."):
                        ins, skp = import_accounts_df(df_up, "add" if "أضف" in mode else "replace", company_id=co_id)
                    st.success(f"✅ أضيف: {ins:,} | تخطى: {skp:,}"); st.rerun()
            except Exception as e:
                st.error(f"❌ خطأ: {e}")

    # ── مرحلة 2: حركات دفتر الأستاذ ──
    if has_tree:
        with st.expander(f"{'✅' if has_journal else '2️⃣'} حركات دفتر الأستاذ — {j_co:,} حركة", expanded=not has_journal):
            if has_journal:
                st.markdown(f'<div class="success-box">✅ الحركات مرفوعة — {j_co:,} حركة</div>', unsafe_allow_html=True)
        st.markdown('<div class="upload-box"><h4>📒 رفع حركات دفتر الأستاذ</h4><p>يقبل الملف الخام من دفترة (CSV) أو ملف Excel منظم (xlsx)</p></div>', unsafe_allow_html=True)
        uploaded_j = st.file_uploader("اختر الملف", type=["xlsx","xls","csv"], key="j_up")

        if uploaded_j:
            try:
                fname = uploaded_j.name.lower()

                # ── تنظيف الملف الخام (CSV من دفترة) ──
                if fname.endswith(".csv"):
                    import io
                    raw = pd.read_csv(uploaded_j, encoding="utf-8-sig", dtype=str)
                    raw.columns = raw.columns.str.strip()

                    # استخراج كود واسم الحساب
                    raw['Account_Name'] = None
                    raw['Account_Code'] = None
                    mask_h = raw['رقم'].str.contains(r'\d+', na=False) & raw['رقم القيد'].isna()
                    raw.loc[mask_h, 'Account_Code'] = raw.loc[mask_h, 'رقم'].str.extract(r'(\d+)\s*$')[0]
                    raw.loc[mask_h, 'Account_Name'] = raw.loc[mask_h, 'رقم'].str.replace(r'\s*\d+\s*$', '', regex=True).str.strip()
                    raw['Account_Code'] = raw['Account_Code'].ffill()
                    raw['Account_Name'] = raw['Account_Name'].ffill()
                    raw = raw.dropna(subset=['رقم القيد']).copy()

                    # إعادة تسمية الأعمدة
                    col_rename = {}
                    for c in raw.columns:
                        cl = c.lower().strip()
                        if re.search(r'unnamed.*7|^دائن$', cl): col_rename[c] = 'دائن'
                        elif re.search(r'عملية|^مدين$', cl):   col_rename[c] = 'مدين'
                    raw.rename(columns=col_rename, inplace=True)

                    # توحيد التاريخ
                    def parse_date(v):
                        if pd.isna(v) or str(v).strip() in ('','nan'): return None
                        for fmt in ('%d-%m-%y','%d-%m-%Y','%Y-%m-%d','%d/%m/%Y','%d/%m/%y'):
                            try: return pd.to_datetime(str(v).strip(), format=fmt).strftime('%Y-%m-%d')
                            except: pass
                        try: return pd.to_datetime(str(v).strip(), dayfirst=True).strftime('%Y-%m-%d')
                        except: return str(v)

                    if 'التاريخ' in raw.columns:
                        raw['التاريخ'] = raw['التاريخ'].apply(parse_date)

                    # توحيد الأرقام
                    for col in ['مدين','دائن']:
                        if col in raw.columns:
                            raw[col] = pd.to_numeric(raw[col].astype(str).str.replace(',','',regex=False).str.strip(), errors='coerce').fillna(0.0)

                    final_cols = ['Account_Code','Account_Name','التاريخ','رقم القيد','الوصف','مدين','دائن']
                    df_j = raw[[c for c in final_cols if c in raw.columns]].reset_index(drop=True)
                    st.success(f"✅ تم تنظيف الملف تلقائياً — {len(df_j):,} حركة")

                else:
                    df_j = pd.read_excel(uploaded_j, engine="openpyxl", dtype=str)
                    # تنظيف عمود الكود من .0 الزيادة
                    code_col_raw = next((c for c in df_j.columns if 'code' in c.lower() or 'كود' in c), None)
                    if code_col_raw:
                        df_j[code_col_raw] = (df_j[code_col_raw].astype(str).str.strip()
                                               .str.replace(r'\.0$', '', regex=True)
                                               .str.replace(r'e\+\d+', '', regex=True))
                    # 1. حذف صفوف الهيدر المتسربة (Account_Code مش رقم)
                    code_col = next((c for c in df_j.columns if 'code' in c.lower() or 'كود' in c), None)
                    if code_col:
                        df_j = df_j[pd.to_numeric(df_j[code_col], errors='coerce').notna()].copy()
                    # 2. تحويل الأرقام وحذف صفوف الإجمالي
                    for col in ['مدين','دائن']:
                        if col in df_j.columns:
                            df_j[col] = pd.to_numeric(df_j[col], errors='coerce').fillna(0)
                    if 'مدين' in df_j.columns:
                        total_sum = df_j['مدين'].sum()
                        if total_sum > 0:
                            df_j = df_j[(df_j['مدين'] < total_sum * 0.5) & (df_j['دائن'] < total_sum * 0.5)]
                    st.success(f"✅ تم قراءة الملف — {len(df_j):,} سطر")

                # ════ فحص الملف قبل الاستيراد ════
                st.markdown("---")
                st.markdown('<div class="sec-title">🔍 تحقق من الملف قبل الاستيراد</div>', unsafe_allow_html=True)

                with st.spinner("جاري الفحص..."):
                    info = preview_journal_df(df_j, company_id=co_id)

                total_rows   = info["total"]
                in_tree      = info["in_tree"]
                not_in_tree  = info["not_in_tree"]
                missing      = info["missing_codes"]
                total_d      = info["total_d"]
                total_c      = info["total_c"]
                j_now        = info["j_total_now"]
                diff_file    = abs(total_d - total_c)
                is_bal       = diff_file < 0.01

                # بطاقات الإحصائيات
                c1,c2,c3,c4 = st.columns(4)
                with c1: st.markdown(f'<div class="check-card blue"><div class="cn" style="color:#3b5bdb">{total_rows:,}</div><div class="cl">إجمالي الحركات</div></div>', unsafe_allow_html=True)
                with c2: st.markdown(f'<div class="check-card red"><div class="cn" style="color:#c92a2a">{total_c:,.0f}</div><div class="cl">إجمالي المدين</div></div>', unsafe_allow_html=True)
                with c3: st.markdown(f'<div class="check-card green"><div class="cn" style="color:#2f9e44">{total_d:,.0f}</div><div class="cl">إجمالي الدائن</div></div>', unsafe_allow_html=True)
                with c4:
                    diff_color = "#2f9e44" if is_bal else "#c92a2a"
                    diff_text  = "✅ متوازن" if is_bal else f"فرق: {diff_file:,.0f}"
                    st.markdown(f'<div class="check-card {"green" if is_bal else "red"}"><div class="cn" style="color:{diff_color};font-size:1.2rem">{diff_text}</div><div class="cl">حالة الملف</div></div>', unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                c5, c6 = st.columns(2)
                with c5: st.markdown(f'<div class="check-card green"><div class="cn" style="color:#2f9e44">{in_tree:,}</div><div class="cl">حركات في الشجرة ✅</div></div>', unsafe_allow_html=True)
                with c6: st.markdown(f'<div class="check-card {"orange" if not_in_tree>0 else "green"}"><div class="cn" style="color:{"#e67700" if not_in_tree>0 else "#2f9e44"}">{not_in_tree:,}</div><div class="cl">حركات على حسابات جديدة {"⚠️" if not_in_tree>0 else "✅"}</div></div>', unsafe_allow_html=True)

                # تفاصيل الحسابات الجديدة
                if missing:
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown(f'<div class="warning-box">⚠️ {len(missing)} كود جديد — حدد الحساب الرئيسي لكل واحد</div>', unsafe_allow_html=True)

                    # جلب كل الحسابات للاختيار
                    conn_tmp = get_conn()
                    all_accs = pd.read_sql("SELECT code, name, acc_level FROM chart_of_accounts WHERE company_id=%s ORDER BY code", conn_tmp, params=(co_id,))
                    conn_tmp.close()
                    # فرز: الحسابات الرئيسية أولاً (is_leaf=0) ثم النهائية
                    acc_options = {f"{r['code']} — {r['name']}": r['code'] for _, r in all_accs.iterrows()}
                    choices = ["— اختر الحساب الرئيسي —"] + list(acc_options.keys())

                    confirmed_codes = {}
                    all_resolved = True
                    # عكس القاموس: كود → اسم
                    acc_options_rev = {v: k.split(" — ",1)[-1] for k,v in acc_options.items()}

                    # CSS لإصلاح لون القوائم المنسدلة
                    st.markdown("""
                    <style>
                    [data-baseweb="select"] [class*="ValueContainer"] { color: #1e2a4a !important; }
                    [data-baseweb="select"] [class*="SingleValue"] { color: #1e2a4a !important; }
                    [data-baseweb="select"] [class*="Input"] input { color: #1e2a4a !important; }
                    [data-baseweb="select"] [class*="option"] { color: #1e2a4a !important; background: white !important; }
                    [data-baseweb="select"] [class*="option"]:hover { background: #e8f0fe !important; }
                    [data-baseweb="popover"] { z-index: 9999 !important; }
                    [data-baseweb="popover"] * { color: #1e2a4a !important; background-color: white !important; }
                    [data-baseweb="menu"] { background: white !important; }
                    [data-baseweb="menu"] li { color: #1e2a4a !important; }
                    [data-baseweb="menu"] li:hover { background: #e8f0fe !important; }
                    </style>""", unsafe_allow_html=True)

                    # رأس الجدول
                    st.markdown("""
                    <div style="background:#1e2a4a;color:white;padding:.6rem 1rem;
                                border-radius:8px 8px 0 0;font-size:.82rem;font-weight:700;direction:rtl;
                                display:grid;grid-template-columns:3fr 1fr 3fr;gap:.5rem">
                        <span>اسم الحساب</span>
                        <span style="text-align:center">الكود</span>
                        <span>الحساب الرئيسي</span>
                    </div>""", unsafe_allow_html=True)

                    for i, (code, info) in enumerate(missing.items()):
                        display_name = info['name'] if info['name'] and info['name'] not in ("كود","nan","") else f"حساب {code}"
                        suggested    = info.get("suggested_parent")
                        conf         = info.get("confidence","none")
                        s_name       = info.get("suggested_parent_name","")
                        bg           = "white" if i % 2 == 0 else "#f8faff"

                        col_name, col_code, col_parent = st.columns([3, 1, 3])
                        with col_name:
                            st.markdown(f"""<div style="background:{bg};padding:.55rem .8rem;
                                border-right:3px solid #e67700;border-bottom:1px solid #f0f2f8">
                                <div style="font-weight:700;color:#1e2a4a;font-size:.87rem">{display_name}</div>
                                <div style="color:#7a8fc0;font-size:.74rem">{info['count']} حركة | مدين:{info['d']:,.0f} | دائن:{info['c']:,.0f}</div>
                            </div>""", unsafe_allow_html=True)
                        with col_code:
                            st.markdown(f"""<div style="background:{bg};padding:.55rem .4rem;
                                border-bottom:1px solid #f0f2f8;text-align:center">
                                <span style="background:#dbeafe;color:#1d4ed8;padding:3px 8px;
                                    border-radius:20px;font-size:.78rem;font-weight:700">{code}</span>
                            </div>""", unsafe_allow_html=True)
                        with col_parent:
                            reason    = info.get("reason","")
                            typed_key = f"typed_{code}"
                            ok_key    = f"ok_{code}"

                            # القيمة المحفوظة
                            saved = st.session_state.get(ok_key)

                            if saved:
                                # تم التأكيد — اعرض الحساب المختار
                                saved_name = acc_options_rev.get(saved, saved)
                                st.markdown(f"""<div style="background:#f0fdf4;border:1px solid #86efac;
                                    border-radius:8px;padding:.45rem .8rem;direction:rtl">
                                    <div style="font-weight:700;color:#166534;font-size:.84rem">✅ {saved_name}</div>
                                    <div style="color:#15803d;font-size:.72rem">{saved}</div>
                                </div>""", unsafe_allow_html=True)
                                if st.button("تعديل", key=f"edit_{code}", use_container_width=True):
                                    del st.session_state[ok_key]; st.rerun()
                                confirmed_codes[code] = {"name": display_name, "parent_code": saved}
                            else:
                                # عرض الاقتراح كقيمة افتراضية في الخانة
                                default_val = suggested if (suggested and conf=="high") else ""
                                typed = st.text_input(
                                    "", key=typed_key,
                                    value=st.session_state.get(typed_key, default_val),
                                    placeholder="اكتب الكود...",
                                    label_visibility="collapsed"
                                )
                                # اعرض اسم الحساب لو الكود موجود
                                matched_name = acc_options_rev.get(typed.strip(), "")
                                if matched_name:
                                    st.markdown(f'<div style="font-size:.75rem;color:#1e40af;margin-top:-8px">📁 {matched_name}</div>', unsafe_allow_html=True)
                                elif typed.strip():
                                    st.markdown(f'<div style="font-size:.75rem;color:#c92a2a;margin-top:-8px">❌ كود غير موجود</div>', unsafe_allow_html=True)
                                elif suggested and conf=="high":
                                    st.markdown(f'<div style="font-size:.72rem;color:#2f9e44;margin-top:-8px">🎯 {reason}</div>', unsafe_allow_html=True)

                                c_ok, c_skip = st.columns(2)
                                with c_ok:
                                    if st.button("✅ تأكيد", key=f"conf_{code}", use_container_width=True, disabled=not matched_name):
                                        st.session_state[ok_key] = typed.strip()
                                        confirmed_codes[code] = {"name": display_name, "parent_code": typed.strip()}
                                        st.rerun()
                                with c_skip:
                                    if st.button("⏭️ تجاهل", key=f"skip_{code}", use_container_width=True):
                                        # تجاهل هذا الكود — مش هيتضاف للشجرة
                                        st.session_state[ok_key] = "__skip__"
                                        st.rerun()
                                all_resolved = False

                    # احسب كام كود فاضي (مش مؤكد ومش متجاهل)
                    unresolved = [c for c in missing if
                                  f"ok_{c}" not in st.session_state
                                  and c not in confirmed_codes]
                    all_resolved = len(unresolved) == 0
                    # أضف الـ skip للـ confirmed بقيمة فارغة عشان ما يتضافش
                    for c in missing:
                        if st.session_state.get(f"ok_{c}") == "__skip__":
                            confirmed_codes[c] = {"name": missing[c]["name"], "parent_code": "__skip__"}

                    st.markdown("<br>", unsafe_allow_html=True)
                    if not all_resolved:
                        st.markdown(f'<div class="warning-box">⏳ {len(unresolved)} كود لم يتأكد بعد — أكد أو تجاهل لتفعيل الاستيراد</div>', unsafe_allow_html=True)

                else:
                    confirmed_codes = {}
                    all_resolved = True
                    st.markdown('<div class="success-box">✅ كل الكودات موجودة في شجرة الحسابات</div>', unsafe_allow_html=True)

                st.markdown(f'<div class="info-box">📊 الحركات الموجودة حالياً: <b>{j_now:,}</b></div>', unsafe_allow_html=True)

                # خيارات الاستيراد
                st.markdown("---")
                st.markdown('<div class="sec-title">⚙️ طريقة الاستيراد</div>', unsafe_allow_html=True)
                mode_j = tab_bar(["➕ أضف للموجود", "🔄 امسح وابدأ من أول"], "j_mode")

                btn_disabled = not all_resolved
                if st.button("🚀 استيراد الحركات", use_container_width=True, type="primary", disabled=btn_disabled):
                    with st.spinner("جاري إضافة الحسابات الجديدة للشجرة..."):
                        if confirmed_codes:
                            added = add_new_codes_to_tree(confirmed_codes, co_id=co_id)
                            st.info(f"✅ أُضيف {len(added)} حساب جديد للشجرة: {', '.join(added)}")
                    with st.spinner("جاري استيراد الحركات..."):
                        ins_j, skipped = import_journal_df(df_j, "add" if "أضف" in mode_j else "replace", company_id=co_id)
                    if skipped:
                        skip_names = ", ".join([f"{k} ({v['name']}) × {v['count']}" for k,v in list(skipped.items())[:5]])
                        st.warning(f"⚠️ تم تجاهل {sum(v['count'] for v in skipped.values()):,} حركة: {skip_names}")
                    st.success(f"✅ تم استيراد {ins_j:,} حركة بنجاح!")
                    st.rerun()

            except Exception as e:
                st.error(f"❌ خطأ: {e}")
    else:
        st.markdown('<div class="warning-box">⚠️ ارفع شجرة الحسابات أولاً ثم يمكنك رفع الحركات</div>', unsafe_allow_html=True)

elif page == "📑  القيود اليومية":
    st.markdown('<div class="page-header"><p class="ph-title">📑 القيود اليومية</p><p class="ph-sub">كل القيود المحاسبية مع فلتر التاريخ والحساب والوصف</p></div>', unsafe_allow_html=True)

    fc1, fc2, fc3, fc4 = st.columns([1.5, 1.5, 2, 1])
    with fc1: date_from = st.date_input("من تاريخ", value=None, key="jf_from", format="YYYY-MM-DD")
    with fc2: date_to   = st.date_input("إلى تاريخ", value=None, key="jf_to",  format="YYYY-MM-DD")
    with fc3: desc_q    = st.text_input("🔍 وصف أو رقم قيد", placeholder="اكتب...", key="jf_desc")
    with fc4: acc_q     = st.text_input("🔍 حساب", placeholder="كود أو اسم", key="jf_acc")

    conn_j = get_conn()
    q = "SELECT jl.*, je.entry_date, je.description FROM journal_lines jl JOIN journal_entries je ON jl.entry_id=je.id WHERE jl.company_id=%s"; p = [co_id]
    if date_from: q += " AND je.entry_date >= %s"; p.append(str(date_from))
    if date_to:   q += " AND je.entry_date <= %s"; p.append(str(date_to))
    if desc_q:    q += " AND (je.description LIKE %s OR jl.entry_no LIKE %s)"; p += [f"%{desc_q}%", f"%{desc_q}%"]
    if acc_q:     q += " AND (jl.account_code LIKE %s OR jl.account_name LIKE %s)"; p += [f"%{acc_q}%", f"%{acc_q}%"]
    q += " ORDER BY jl.id DESC"
    all_j = pd.read_sql(q, conn_j, params=p)
    conn_j.close()

    td_j = all_j["debit"].sum() if not all_j.empty else 0
    tc_j = all_j["credit"].sum() if not all_j.empty else 0
    diff_j = abs(td_j - tc_j)
    c1,c2,c3,c4 = st.columns(4)
    with c1: st.markdown(f'<div class="stat-card"><div class="s-num">{len(all_j):,}</div><div class="s-lbl">حركة</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="stat-card red"><div class="s-num" style="color:#c92a2a;font-size:1.1rem">{td_j:,.2f}</div><div class="s-lbl">مدين</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="stat-card green"><div class="s-num" style="color:#2f9e44;font-size:1.1rem">{tc_j:,.2f}</div><div class="s-lbl">دائن</div></div>', unsafe_allow_html=True)
    with c4:
        dclr = "#2f9e44" if diff_j < 0.01 else "#c92a2a"
        dtxt = "✅ متوازن" if diff_j < 0.01 else f"فرق: {diff_j:,.2f}"
        st.markdown(f'<div class="stat-card"><div class="s-num" style="color:{dclr};font-size:1rem">{dtxt}</div><div class="s-lbl">الحالة</div></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Popup القيد
    if "jpage_popup" not in st.session_state: st.session_state.jpage_popup = None
    if st.session_state.jpage_popup:
        eno = st.session_state.jpage_popup
        conn_pp = get_conn()
        qrows = pd.read_sql(
            "SELECT account_code, account_name, description, debit, credit FROM journal_lines WHERE entry_no=%s AND company_id=%s ORDER BY id",
            conn_pp, params=(str(eno), co_id))
        conn_pp.close()
        with st.expander(f"📋 القيد رقم {eno}", expanded=True):
            tot_d = qrows["debit"].sum(); tot_c = qrows["credit"].sum()
            diff_q = abs(tot_d-tot_c); bal_q = "#2f9e44" if diff_q<0.01 else "#c92a2a"
            bal_t = "✅ متوازن" if diff_q<0.01 else f"❌ فرق: {diff_q:,.2f}"
            qrows_html = ""
            for _, qr in qrows.iterrows():
                dv = f"{qr['debit']:,.2f}" if qr["debit"]>0 else "—"
                cv = f"{qr['credit']:,.2f}" if qr["credit"]>0 else "—"
                qrows_html += f'<tr style="border-bottom:1px solid #f0f2f8"><td style="padding:.5rem .8rem;font-weight:600;color:#1e2a4a">{qr["account_name"] or qr["account_code"]}</td><td style="padding:.5rem .8rem;color:#5a6a8a;font-size:.82rem">{qr["account_code"]}</td><td style="padding:.5rem .8rem;color:#374151;font-size:.82rem">{str(qr["description"] or "")[:50]}</td><td style="padding:.5rem .8rem;color:#c92a2a;text-align:left;font-family:monospace">{dv}</td><td style="padding:.5rem .8rem;color:#2f9e44;text-align:left;font-family:monospace">{cv}</td></tr>'
            st.markdown(f"""
            <table style="width:100%;border-collapse:collapse;direction:rtl;background:white;border-radius:10px;overflow:hidden">
            <thead><tr style="background:#1e2a4a;color:white">
                <th style="padding:.6rem .8rem;text-align:right;font-size:.82rem">الحساب</th>
                <th style="padding:.6rem .8rem;text-align:right;font-size:.82rem">الكود</th>
                <th style="padding:.6rem .8rem;text-align:right;font-size:.82rem">البيان</th>
                <th style="padding:.6rem .8rem;text-align:left;font-size:.82rem">مدين</th>
                <th style="padding:.6rem .8rem;text-align:left;font-size:.82rem">دائن</th>
            </tr></thead>
            <tbody>{qrows_html}</tbody>
            <tfoot>
                <tr style="background:#f0f4ff;font-weight:900">
                    <td colspan="3" style="padding:.6rem .8rem;color:#1e2a4a">الإجمالي</td>
                    <td style="padding:.6rem .8rem;color:#c92a2a;text-align:left;font-family:monospace">{tot_d:,.2f}</td>
                    <td style="padding:.6rem .8rem;color:#2f9e44;text-align:left;font-family:monospace">{tot_c:,.2f}</td>
                </tr>
                <tr><td colspan="5" style="padding:.4rem .8rem;color:{bal_q};text-align:center;font-weight:700">{bal_t}</td></tr>
            </tfoot></table>""", unsafe_allow_html=True)
            if st.button("✖️ إغلاق", key="close_jpage"):
                st.session_state.jpage_popup = None; st.rerun()

    if all_j.empty:
        st.info("لا توجد قيود بهذه الفلاتر")
    else:
        show_by = tab_bar(["📋 مجمّع بالقيد", "📄 كل الحركات"], "j_view")

        if "مجمّع" in show_by:
            grp = all_j.groupby(["entry_no","entry_date"]).agg(
                حسابات=("account_name", lambda x: " | ".join(x.dropna().unique()[:3])),
                مدين=("debit","sum"), دائن=("credit","sum")
            ).reset_index().sort_values(["entry_date","entry_no"], ascending=False)

            rows_html = ""
            for _, r in grp.iterrows():
                diff_r = abs(r["مدين"]-r["دائن"])
                ic = "✅" if diff_r < 0.01 else "❌"
                rows_html += f'<tr style="border-bottom:1px solid #f0f2f8"><td style="padding:.5rem .8rem;text-align:center"><span style="background:#e8f0fe;color:#3b5bdb;padding:2px 8px;border-radius:12px;font-weight:700;font-size:.82rem">{r["entry_no"]}</span></td><td style="padding:.5rem .8rem;color:#374151;font-size:.85rem">{r["entry_date"] or ""}</td><td style="padding:.5rem .8rem;color:#5a6a8a;font-size:.8rem;max-width:300px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{r["حسابات"]}</td><td style="padding:.5rem .8rem;color:#c92a2a;text-align:left;font-family:monospace;font-size:.85rem">{r["مدين"]:,.2f}</td><td style="padding:.5rem .8rem;color:#2f9e44;text-align:left;font-family:monospace;font-size:.85rem">{r["دائن"]:,.2f}</td><td style="padding:.5rem .8rem;text-align:center">{ic}</td></tr>'

            st.markdown(f"""
            <div style="background:white;border-radius:12px;overflow:hidden;box-shadow:0 1px 8px rgba(0,0,0,.06);max-height:600px;overflow-y:auto">
            <table style="width:100%;border-collapse:collapse;direction:rtl">
                <thead style="position:sticky;top:0;z-index:1"><tr style="background:#1e2a4a;color:white">
                    <th style="padding:.65rem .8rem;text-align:center;font-size:.82rem">رقم القيد</th>
                    <th style="padding:.65rem .8rem;text-align:right;font-size:.82rem">التاريخ</th>
                    <th style="padding:.65rem .8rem;text-align:right;font-size:.82rem">الحسابات</th>
                    <th style="padding:.65rem .8rem;text-align:left;font-size:.82rem">مدين</th>
                    <th style="padding:.65rem .8rem;text-align:left;font-size:.82rem">دائن</th>
                    <th style="padding:.65rem .8rem;text-align:center;font-size:.82rem">حالة</th>
                </tr></thead>
                <tbody>{rows_html}</tbody>
            </table></div>""", unsafe_allow_html=True)

            st.markdown("<div style='font-size:.8rem;color:#7a8fc0;margin-top:.5rem'>اضغط على رقم القيد لعرض تفاصيله:</div>", unsafe_allow_html=True)
            entry_nos = grp["entry_no"].tolist()
            for i in range(0, len(entry_nos), 10):
                cols_e = st.columns(10)
                for j, eno in enumerate(entry_nos[i:i+10]):
                    with cols_e[j]:
                        if st.button(str(eno), key=f"jp_{eno}_{i}", use_container_width=True):
                            st.session_state.jpage_popup = str(eno); st.rerun()
        else:
            display_j = pd.DataFrame({
                "رقم القيد": all_j["entry_no"], "التاريخ": all_j["entry_date"],
                "الحساب": all_j["account_name"], "الكود": all_j["account_code"],
                "الوصف": all_j["description"],
                "مدين": all_j["debit"].apply(lambda x: f"{x:,.2f}" if x>0 else "—"),
                "دائن": all_j["credit"].apply(lambda x: f"{x:,.2f}" if x>0 else "—"),
            })
            st.dataframe(display_j, use_container_width=True, hide_index=True, height=600)

        st.download_button("⬇️ تحميل القيود", data=all_j.to_csv(index=False, encoding="utf-8-sig"),
                           file_name="القيود_اليومية.csv", mime="text/csv")

# ════════════════════════════════════════════════════════
# ══ صفحة مراكز التكلفة ══
# ════════════════════════════════════════════════════════
elif page == "📊  مراكز التكلفة":
    st.markdown('<div class="page-header"><p class="ph-title">📊 مراكز التكلفة</p><p class="ph-sub">تحليل المصروفات حسب المشروع والتصنيف</p></div>', unsafe_allow_html=True)

    conn_cc = get_conn()
    cc_count = conn_cc.execute("SELECT COUNT(*) FROM cost_center_entries WHERE company_id=%s", (co_id,)).fetchone()[0]
    conn_cc.close()

    # ── رفع الملف ──
    with st.expander(f"{'✅' if cc_count>0 else '📤'} رفع ملف مراكز التكلفة — {cc_count:,} سجل", expanded=cc_count==0):
        st.markdown('<p style="color:#7a8fc0;font-size:.85rem">ارفع ملف Excel من دفترة كما هو — البرنامج ينظفه تلقائياً</p>', unsafe_allow_html=True)
        up_cc = st.file_uploader("ملف مراكز التكلفة", type=["xlsx","xls","csv"], key="cc_up")
        if up_cc:
            try:
                fname_cc = up_cc.name.lower()
                if fname_cc.endswith(".csv"):
                    df_cc = pd.read_csv(up_cc, encoding="utf-8-sig", dtype=str)
                else:
                    df_cc = pd.read_excel(up_cc, engine="openpyxl", dtype=str)
                df_cc.columns = [str(c).strip() for c in df_cc.columns]

                # ── اكتشاف الأعمدة تلقائياً ──
                col_map_cc = {}
                for c in df_cc.columns:
                    cl = c.strip()
                    if any(k in cl for k in ["رقم القيد","entry_no"]): col_map_cc["entry_no"] = c
                    elif any(k in cl for k in ["التاريخ","date"]):      col_map_cc["date"]     = c
                    elif any(k in cl for k in ["الحساب الفرعي","account_code","كود"]): col_map_cc["code"] = c
                    elif any(k in cl for k in ["اسم الحساب","account_name"]): col_map_cc["name"] = c
                    elif "مركز" in cl:                                   col_map_cc["center"]  = c
                    elif "التصنيف" in cl or "تصنيف" in cl:              col_map_cc["category"] = c
                    elif any(k in cl for k in ["الحالة","حالة","ضريبي"]): col_map_cc["tax"] = c
                    elif any(k in cl for k in ["مدين","debit"]):        col_map_cc["debit"]   = c
                    elif any(k in cl for k in ["دائن","credit"]):       col_map_cc["credit"]  = c
                    elif any(k in cl for k in ["الوصف","desc","بيان"]): col_map_cc["desc"]    = c

                st.success(f"✅ تم قراءة {len(df_cc):,} سجل")
                st.markdown(f'<div class="info-box">أعمدة تم التعرف عليها: {", ".join(f"{k}={v}" for k,v in col_map_cc.items())}</div>', unsafe_allow_html=True)

                mode_cc = tab_bar(["➕ أضف للموجود", "🔄 امسح وابدأ من أول"], "cc_mode")

                if st.button("🚀 استيراد مراكز التكلفة", use_container_width=True, type="primary"):
                    conn_cc2 = get_conn()
                    if "امسح" in mode_cc:
                        conn_cc2.execute("DELETE FROM cost_center_entries WHERE company_id=%s", (co_id,))
                        conn_cc2.commit()

                    rows_cc = []
                    for _, r in df_cc.iterrows():
                        def gv(k):
                            col = col_map_cc.get(k)
                            return str(r[col]).strip() if col and pd.notna(r.get(col)) and str(r.get(col)).strip() not in ("","nan") else ""
                        def gn(k):
                            col = col_map_cc.get(k)
                            try: return float(str(r[col]).replace(",","")) if col and pd.notna(r.get(col)) else 0.0
                            except: return 0.0

                        center = gv("center"); category = gv("category")
                        if not center and not category: continue
                        rows_cc.append((co_id, gv("entry_no"), gv("date"),
                                        _normalize_code(gv("code")) if gv("code") else "",
                                        gv("name"), center, category, gv("tax"), gn("debit"), gn("credit"), gv("desc")))

                    conn_cc2.executemany(
                        "INSERT INTO cost_center_entries (company_id,entry_no,entry_date,account_code,account_name,cost_center,category,tax_status,debit,credit,description) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        rows_cc)
                    conn_cc2.commit(); conn_cc2.close()
                    st.success(f"✅ تم استيراد {len(rows_cc):,} سجل"); st.rerun()
            except Exception as e:
                st.error(f"❌ خطأ: {e}")

    if cc_count == 0:
        st.info("ارفع ملف مراكز التكلفة أولاً")
    else:
        # ── فلاتر ──
        conn_cc3 = get_conn()
        all_cc = pd.read_sql("SELECT * FROM cost_center_entries WHERE company_id=%s", conn_cc3, params=(co_id,))
        conn_cc3.close()

        all_cc["debit"] = pd.to_numeric(all_cc["debit"], errors='coerce').fillna(0)
        all_cc["credit"] = pd.to_numeric(all_cc["credit"], errors='coerce').fillna(0)

        # دمج ضريبي وغير ضريبي — إظهار التصنيف بدون الحالة
        all_cc["category_clean"] = all_cc["category"].str.replace(r'\s*(ضريبي|غير ضريبي)\s*$', '', regex=True).str.strip()

        f1, f2, f3 = st.columns(3)
        with f1:
            centers_list = ["كل المشاريع"] + sorted(all_cc["cost_center"].dropna().unique().tolist())
            sel_center = st.selectbox("المشروع", centers_list, key="cc_center")
        with f2:
            cats_list = ["كل التصنيفات"] + sorted(all_cc["category_clean"].dropna().unique().tolist())
            sel_cat = st.selectbox("التصنيف", cats_list, key="cc_cat")
        with f3:
            date_range = st.date_input("الفترة", value=[], key="cc_date")

        # تطبيق الفلتر
        filtered_cc = all_cc.copy()
        if sel_center != "كل المشاريع": filtered_cc = filtered_cc[filtered_cc["cost_center"]==sel_center]
        if sel_cat != "كل التصنيفات":  filtered_cc = filtered_cc[filtered_cc["category_clean"]==sel_cat]

        # ── Pivot Table: مشروع × تصنيف ──
        pivot_cc = filtered_cc.groupby(["cost_center","category_clean"])["debit"].sum().reset_index()
        pivot_cc = pivot_cc[pivot_cc["debit"]>0]

        # ── إحصائيات ──
        total_cc = filtered_cc["debit"].sum()
        s1,s2,s3,s4 = st.columns(4)
        with s1: st.markdown(f'<div class="stat-card"><div class="s-num">{total_cc:,.0f}</div><div class="s-lbl">إجمالي المصروفات</div></div>', unsafe_allow_html=True)
        with s2: st.markdown(f'<div class="stat-card green"><div class="s-num" style="color:#2f9e44">{filtered_cc["cost_center"].nunique()}</div><div class="s-lbl">مشروع</div></div>', unsafe_allow_html=True)
        with s3: st.markdown(f'<div class="stat-card orange"><div class="s-num" style="color:#e67700">{filtered_cc["category_clean"].nunique()}</div><div class="s-lbl">تصنيف</div></div>', unsafe_allow_html=True)
        with s4: st.markdown(f'<div class="stat-card"><div class="s-num">{len(filtered_cc):,}</div><div class="s-lbl">سجل</div></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # ── اختيار العرض ──
        view_cc = tab_bar(["🔀 جدول مقارن", "📋 حسب المشروع", "📋 حسب التصنيف", "🔗 مرتبط بالقيود"], "cc_view")

        if "مقارن" in view_cc:
            # Pivot بالمشاريع والتصنيفات
            piv = pivot_cc.pivot_table(index="cost_center", columns="category_clean", values="debit", fill_value=0)
            piv["الإجمالي"] = piv.sum(axis=1)
            piv = piv.sort_values("الإجمالي", ascending=False)
            piv_show = piv.map(lambda x: f"{x:,.0f}" if x>0 else "—")
            st.dataframe(piv_show, use_container_width=True, height=550)
            csv_piv = piv.to_csv(encoding="utf-8-sig")
            st.download_button("⬇️ تحميل الجدول", data=csv_piv, file_name="مراكز_التكلفة_pivot.csv", mime="text/csv")

        elif "المشروع" in view_cc:
            by_center = filtered_cc.groupby("cost_center")["debit"].sum().sort_values(ascending=False).reset_index()
            by_center.columns = ["المشروع","الإجمالي"]
            by_center["النسبة"] = (by_center["الإجمالي"]/total_cc*100).round(1).astype(str)+"%"
            by_center["الإجمالي"] = by_center["الإجمالي"].apply(lambda x: f"{x:,.2f}")
            st.dataframe(by_center, use_container_width=True, hide_index=True, height=550)

        elif "التصنيف" in view_cc:
            by_cat = filtered_cc.groupby("category_clean")["debit"].sum().sort_values(ascending=False).reset_index()
            by_cat.columns = ["التصنيف","الإجمالي"]
            by_cat["النسبة"] = (by_cat["الإجمالي"]/total_cc*100).round(1).astype(str)+"%"
            by_cat["الإجمالي"] = by_cat["الإجمالي"].apply(lambda x: f"{x:,.2f}")
            st.dataframe(by_cat, use_container_width=True, hide_index=True, height=550)

        elif "القيود" in view_cc:
            # ربط مراكز التكلفة بالقيود
            conn_lnk = get_conn()
            linked = pd.read_sql("""
                SELECT cc.entry_no, cc.entry_date, cc.cost_center, cc.category_clean,
                       cc.debit as cc_debit,
                       j.account_name, j.description
                FROM (SELECT *, category as category_clean FROM cost_center_entries WHERE company_id=%s) cc
                LEFT JOIN journal_entries j ON cc.entry_no = j.entry_no AND j.company_id=%s
                WHERE cc.debit > 0
                LIMIT 500
            """, conn_lnk, params=(co_id, co_id))
            conn_lnk.close()
            if linked.empty:
                st.info("لا توجد قيود مرتبطة — تأكد إن ملف الأستاذ مرفوع")
            else:
                st.dataframe(linked, use_container_width=True, hide_index=True, height=550)


# ════════════════════════════════════════════════════════
# ══ صفحة المخزن والمستندات ══
# ════════════════════════════════════════════════════════
elif page == "📦  المخزن والمستندات":
    st.markdown('<div class="page-header"><p class="ph-title">📦 المخزن والمستندات</p><p class="ph-sub">رفع وتحليل كل مستندات الشركة</p></div>', unsafe_allow_html=True)

    # ── إحصائيات سريعة ──
    conn_m = get_conn()
    stk_count = conn_m.execute("SELECT COUNT(*) FROM stock_movements WHERE company_id=%s", (co_id,)).fetchone()[0]
    pur_count = conn_m.execute("SELECT COUNT(*) FROM purchases WHERE company_id=%s", (co_id,)).fetchone()[0]
    sal_count = conn_m.execute("SELECT COUNT(*) FROM sales_invoices WHERE company_id=%s", (co_id,)).fetchone()[0]
    exp_count = conn_m.execute("SELECT COUNT(*) FROM expenses WHERE company_id=%s", (co_id,)).fetchone()[0]
    rec_count = conn_m.execute("SELECT COUNT(*) FROM receipts WHERE company_id=%s", (co_id,)).fetchone()[0]
    pay_count = conn_m.execute("SELECT COUNT(*) FROM payroll WHERE company_id=%s", (co_id,)).fetchone()[0]
    conn_m.close()

    tabs_doc = st.tabs([
        f"📦 إذونات مخزن ({stk_count:,})",
        f"🛒 مشتريات ({pur_count:,})",
        f"🧾 مبيعات ({sal_count:,})",
        f"💸 مصروفات ({exp_count:,})",
        f"💰 سندات قبض ({rec_count:,})",
        f"👥 مرتبات ({pay_count:,})",
    ])

    # ════ تاب 1: إذونات المخزن ════
    with tabs_doc[0]:
        with st.expander(f"{'✅' if stk_count>0 else '📤'} رفع إذونات المخزن", expanded=stk_count==0):
            st.markdown('<div class="info-box">يقبل ملفين: <b>Format عادي</b> (أعمدة: المنتج، التصنيف، الفرع، النوع...) أو <b>Format أستاذ دفترة</b> (كل منتج header ثم حركاته)</div>', unsafe_allow_html=True)
            up_stk = st.file_uploader("ملف الإذونات (CSV أو Excel)", type=["csv","xlsx"], key="stk_up")
            if up_stk:
                try:
                    df_stk_raw = pd.read_csv(up_stk, encoding="utf-8-sig", dtype=str) if up_stk.name.endswith(".csv") else pd.read_excel(up_stk, engine="openpyxl", dtype=str)
                    df_stk_raw.columns = [c.strip() for c in df_stk_raw.columns]

                    # تحديد الـ format
                    is_ledger_format = "المنتج" not in df_stk_raw.columns and df_stk_raw.iloc[:,0].astype(str).str.contains("#", na=False).any()

                    if is_ledger_format:
                        st.info("✅ Format: أستاذ مخزن دفترة")
                        df_stk_data, last_bal_preview, wh_col = parse_stock_ledger(df_stk_raw)
                        df_stk = df_stk_data
                        st.markdown(f'<div class="success-box">✅ {len(df_stk):,} حركة | {df_stk["product_name"].nunique()} منتج | {df_stk[wh_col].nunique()} مخزن</div>', unsafe_allow_html=True)
                        # عرض ملخص رصيد سريع
                        st.dataframe(last_bal_preview[["product_name", wh_col, "المخزون بعد", "متوسط سعر التكلفة", "قيمة المخزون بعد"]].rename(columns={
                            "product_name":"المنتج","المخزون بعد":"الرصيد","متوسط سعر التكلفة":"متوسط السعر","قيمة المخزون بعد":"القيمة"
                        }).sort_values("القيمة", ascending=False).head(10),
                        use_container_width=True, hide_index=True)
                    else:
                        st.info("✅ Format: إذونات عادي")
                        df_stk = df_stk_raw[df_stk_raw["المنتج"].notna()].copy()
                        st.success(f"✅ {len(df_stk):,} حركة")

                    mode_stk = tab_bar(["➕ أضف", "🔄 امسح"], "stk_mode")
                    if st.button("🚀 استيراد", use_container_width=True, type="primary"):
                        conn_s = get_conn()
                        if "امسح" in mode_stk: conn_s.execute("DELETE FROM stock_movements WHERE company_id=%s", (co_id,)); conn_s.commit()
                        rows_s = []
                        if is_ledger_format:
                            wh_col_name = df_stk.columns[2] if len(df_stk.columns) > 2 else "المستودع"
                            for _, r in df_stk.iterrows():
                                def gv(c): return str(r.get(c,"") or "").strip() if pd.notna(r.get(c)) else ""
                                def gn(c):
                                    try: return float(str(r.get(c,0)).replace(",",""))
                                    except: return 0.0
                                qty = gn("الكمية"); price = gn("سعر الوحدة (EGP)")
                                prod = str(r.get("product_name","") or "").strip()
                                wh   = str(r.get(wh_col_name,"") or "").strip()
                                doc  = gv("المصدر"); date = gv("العملية")
                                mv_type = "اضافة" if qty > 0 else "صرف" if qty < 0 else "تسوية"
                                rows_s.append((co_id, doc, date, mv_type, wh, prod, "",
                                              "", abs(qty), price, abs(qty)*price, "", "", "", ""))
                        else:
                            def g(r,c): return str(r.get(c,"") or "").strip() if pd.notna(r.get(c)) else ""
                            def gn(r,c):
                                try: return float(str(r.get(c,"")).replace(",",""))
                                except: return 0.0
                            for _, r in df_stk.iterrows():
                                qty = gn(r,"الكمية"); price = gn(r,"سعر الوحدة")
                                rows_s.append((co_id, g(r,"رقم إذن التحويل"), g(r,"التاريخ"), g(r,"النوع"),
                                              g(r,"الفرع"), g(r,"المنتج"), g(r,"رقم المنتج"),
                                              g(r,"التصنيف"), qty, price, qty*price,
                                              g(r,"مركز التكلفة"), g(r,"العميل"), g(r,"المورد"), g(r,"الموظف")))
                        conn_s.executemany("INSERT INTO stock_movements (company_id,doc_no,doc_date,movement_type,warehouse,product_name,product_code,category,qty,unit_price,total,cost_center,client,supplier,employee) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", rows_s)
                        conn_s.commit(); conn_s.close()
                        st.success(f"✅ تم استيراد {len(rows_s):,} حركة"); st.rerun()
                except Exception as e: st.error(f"❌ {e}")

        if stk_count > 0:
            conn_stk = get_conn()
            df_mv = pd.read_sql("SELECT * FROM stock_movements WHERE company_id=%s", conn_stk, params=(co_id,))
            conn_stk.close()
            for c in ["qty","unit_price","total"]:
                df_mv[c] = pd.to_numeric(df_mv[c], errors='coerce').fillna(0)
            # تطبيق الـ mappings
            df_mv = apply_mappings(df_mv, co_id, "product_name", "product_code", "category", "cost_center")

            # ── دالة حساب رصيد المخزن ──
            def calc_stock(data, search="", cat_f="كل التصنيفات"):
                d = data.copy()
                if cat_f != "كل التصنيفات": d = d[d["category"]==cat_f]
                if search: d = d[d["product_name"].str.contains(search, case=False, na=False)]
                adds = d[d["movement_type"]=="اضافة"]
                outs = d[d["movement_type"]=="صرف"]
                qty_in  = adds.groupby("product_name")["qty"].sum()
                qty_out = outs.groupby("product_name")["qty"].sum()
                tot_in  = adds.groupby("product_name")["total"].sum()
                s = pd.DataFrame({"الداخل": qty_in, "الخارج": qty_out, "إجمالي_الشراء": tot_in}).fillna(0)
                s["الرصيد"]       = (s["الداخل"] - s["الخارج"]).round(3)
                s["متوسط_السعر"]  = (s["إجمالي_الشراء"] / s["الداخل"].replace(0,1)).round(2)
                s["قيمة_الرصيد"]  = (s["الرصيد"] * s["متوسط_السعر"]).round(2)
                cat_map = data.drop_duplicates("product_name").set_index("product_name")["category"]
                s["التصنيف"] = s.index.map(cat_map)
                s = s.reset_index().rename(columns={"product_name":"المنتج"})
                return s[s["الرصيد"].abs() > 0.001].sort_values("قيمة_الرصيد", ascending=False)

            def show_stock_report(data, key_suffix=""):
                """عرض تقرير رصيد مخزن واحد — مع فرز وإجماليات"""
                cat_list = ["كل التصنيفات"] + sorted(data["category"].dropna().unique().tolist())

                # ── فلاتر ──
                fc1, fc2, fc3, fc4 = st.columns([2, 2, 2, 1])
                with fc1:
                    sel_cat = st.selectbox("🏷️ التصنيف", cat_list, key=f"cat_{key_suffix}")
                with fc2:
                    sort_by = st.selectbox("فرز حسب", [
                        "قيمة_الرصيد ↓", "الرصيد ↓", "الرصيد ↑",
                        "متوسط_السعر ↓", "الداخل ↓", "الخارج ↓", "المنتج أ-ي"
                    ], key=f"sort_{key_suffix}")
                with fc3:
                    show_filter = st.selectbox("عرض", [
                        "الكل", "رصيد موجب فقط", "رصيد سالب فقط", "بدون حركة صادرة"
                    ], key=f"shw_{key_suffix}")
                with fc4:
                    search_p = st.text_input("", placeholder="🔍", key=f"srch_{key_suffix}", label_visibility="collapsed")

                stk = calc_stock(data, search_p, sel_cat)

                # تطبيق فلتر العرض
                if show_filter == "رصيد موجب فقط":   stk = stk[stk["الرصيد"] > 0]
                elif show_filter == "رصيد سالب فقط": stk = stk[stk["الرصيد"] < 0]
                elif show_filter == "بدون حركة صادرة": stk = stk[stk["الخارج"] == 0]

                # تطبيق الفرز
                sort_map = {
                    "قيمة_الرصيد ↓": ("قيمة_الرصيد", False),
                    "الرصيد ↓":       ("الرصيد", False),
                    "الرصيد ↑":       ("الرصيد", True),
                    "متوسط_السعر ↓":  ("متوسط_السعر", False),
                    "الداخل ↓":       ("الداخل", False),
                    "الخارج ↓":       ("الخارج", False),
                    "المنتج أ-ي":     ("المنتج", True),
                }
                scol, sasc = sort_map.get(sort_by, ("قيمة_الرصيد", False))
                stk = stk.sort_values(scol, ascending=sasc)

                # ── إحصائيات ──
                total_val = stk["قيمة_الرصيد"].sum()
                s1,s2,s3,s4,s5 = st.columns(5)
                with s1: st.markdown(f'<div class="stat-card"><div class="s-num" style="font-size:1rem">{total_val:,.0f}</div><div class="s-lbl">قيمة الرصيد</div></div>', unsafe_allow_html=True)
                with s2: st.markdown(f'<div class="stat-card green"><div class="s-num">{len(stk):,}</div><div class="s-lbl">منتج</div></div>', unsafe_allow_html=True)
                with s3: st.markdown(f'<div class="stat-card blue"><div class="s-num" style="color:#3b5bdb">{stk["الداخل"].sum():,.0f}</div><div class="s-lbl">إجمالي وارد</div></div>', unsafe_allow_html=True)
                with s4: st.markdown(f'<div class="stat-card orange"><div class="s-num" style="color:#e67700">{stk["الخارج"].sum():,.0f}</div><div class="s-lbl">إجمالي صادر</div></div>', unsafe_allow_html=True)
                with s5: st.markdown(f'<div class="stat-card red"><div class="s-num" style="color:#c92a2a">{(stk["الرصيد"]<0).sum()}</div><div class="s-lbl">رصيد سالب</div></div>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)

                if stk.empty:
                    st.info("لا توجد بيانات"); return

                # ── إجماليات التصنيف (لو كل التصنيفات) ──
                if sel_cat == "كل التصنيفات":
                    cat_totals = stk.groupby("التصنيف").agg(
                        عدد_المنتجات=("المنتج","count"),
                        إجمالي_وارد=("الداخل","sum"),
                        إجمالي_صادر=("الخارج","sum"),
                        رصيد_الكمية=("الرصيد","sum"),
                        قيمة_الرصيد=("قيمة_الرصيد","sum")
                    ).reset_index().sort_values("قيمة_الرصيد", ascending=False)

                    with st.expander("📊 ملخص التصنيفات", expanded=False):
                        st.dataframe(
                            cat_totals.style.format({
                                "إجمالي_وارد": "{:,.2f}", "إجمالي_صادر": "{:,.2f}",
                                "رصيد_الكمية": "{:,.2f}", "قيمة_الرصيد": "{:,.2f}"
                            }),
                            use_container_width=True, hide_index=True, height=300
                        )

                # ── الجدول التفصيلي ──
                disp = stk[["المنتج","التصنيف","الداخل","الخارج","الرصيد","متوسط_السعر","قيمة_الرصيد"]].copy()

                def highlight_row(row):
                    if row["الرصيد"] < 0:
                        return ["background-color:#fff0f0;color:#c92a2a"] * len(row)
                    elif row["الرصيد"] == 0:
                        return ["color:#9ca3af"] * len(row)
                    return [""] * len(row)

                st.dataframe(
                    disp.style.format({
                        "الداخل": "{:,.2f}", "الخارج": "{:,.2f}",
                        "الرصيد": "{:,.2f}", "متوسط_السعر": "{:,.2f}",
                        "قيمة_الرصيد": "{:,.2f}"
                    }).apply(highlight_row, axis=1),
                    use_container_width=True, hide_index=True, height=520
                )

                # ── تحميل ──
                col_dl1, col_dl2 = st.columns(2)
                with col_dl1:
                    st.download_button("⬇️ تفصيلي CSV", data=disp.to_csv(index=False, encoding="utf-8-sig"),
                                       file_name=f"رصيد_{key_suffix}.csv", mime="text/csv", key=f"dl_{key_suffix}")
                with col_dl2:
                    if sel_cat == "كل التصنيفات":
                        st.download_button("⬇️ ملخص التصنيفات", data=cat_totals.to_csv(index=False, encoding="utf-8-sig"),
                                           file_name=f"تصنيفات_{key_suffix}.csv", mime="text/csv", key=f"dlc_{key_suffix}")

            # ── Partition المخازن ──
            warehouses = sorted(df_mv["warehouse"].dropna().unique().tolist())
            view_stk = tab_bar(["📦 رصيد المخازن", "📋 حركة منتج", "🏷️ حسب التصنيف"], "stk_view")

            if view_stk == "📦 رصيد المخازن":
                if len(warehouses) == 1:
                    # مخزن واحد — عرض مباشر
                    st.markdown(f'<div class="ledger-header"><div style="font-size:1rem;font-weight:900;color:#1e2a4a">🏭 {warehouses[0]}</div></div>', unsafe_allow_html=True)
                    show_stock_report(df_mv, warehouses[0][:20].replace(" ","_"))
                else:
                    # أكتر من مخزن — tabs
                    wh_tabs = st.tabs([f"🏭 {w}" for w in warehouses] + ["⚖️ مقارنة المخازن"])
                    for i, wh in enumerate(warehouses):
                        with wh_tabs[i]:
                            wh_data = df_mv[df_mv["warehouse"]==wh]
                            show_stock_report(wh_data, f"wh{i}")
                    # تاب المقارنة
                    with wh_tabs[-1]:
                        compare = []
                        for wh in warehouses:
                            wh_stk = calc_stock(df_mv[df_mv["warehouse"]==wh])
                            compare.append({
                                "المخزن": wh,
                                "عدد المنتجات": len(wh_stk),
                                "إجمالي الوارد": wh_stk["الداخل"].sum(),
                                "إجمالي الصادر": wh_stk["الخارج"].sum(),
                                "قيمة الرصيد": wh_stk["قيمة_الرصيد"].sum(),
                            })
                        st.dataframe(pd.DataFrame(compare), use_container_width=True, hide_index=True)

            elif view_stk == "📋 حركة منتج":
                all_products = sorted(df_mv["product_name"].dropna().unique().tolist())
                fc1, fc2 = st.columns([3,2])
                with fc1: sel_prod = st.selectbox("المنتج", ["— اختر —"] + all_products, key="stk_prod")
                with fc2: sel_wh_mv = st.selectbox("المخزن", ["كل المخازن"] + warehouses, key="stk_wh_mv")
                if sel_prod != "— اختر —":
                    prod_df = df_mv[df_mv["product_name"]==sel_prod].copy()
                    if sel_wh_mv != "كل المخازن": prod_df = prod_df[prod_df["warehouse"]==sel_wh_mv]
                    prod_df = prod_df.sort_values("doc_date")
                    prod_df["qty_signed"] = prod_df.apply(lambda r: r["qty"] if r["movement_type"]=="اضافة" else -r["qty"], axis=1)
                    prod_df["الرصيد التراكمي"] = prod_df["qty_signed"].cumsum().round(3)
                    # header
                    last_avg = (prod_df[prod_df["movement_type"]=="اضافة"]["total"].sum() /
                                max(prod_df[prod_df["movement_type"]=="اضافة"]["qty"].sum(), 1))
                    bal_q = prod_df["qty_signed"].sum()
                    st.markdown(f"""
                    <div style="background:white;border-radius:10px;padding:1rem 1.5rem;
                                border-right:5px solid #3b5bdb;box-shadow:0 1px 6px rgba(0,0,0,.06);
                                display:flex;gap:2rem;direction:rtl;margin-bottom:1rem">
                        <div><div style="font-size:1.3rem;font-weight:900;color:#1e2a4a">{sel_prod}</div></div>
                        <div><div style="font-weight:700;color:#2f9e44">{bal_q:,.2f}</div><div style="font-size:.75rem;color:#7a8fc0">الرصيد الحالي</div></div>
                        <div><div style="font-weight:700;color:#3b5bdb">{last_avg:,.2f}</div><div style="font-size:.75rem;color:#7a8fc0">متوسط السعر</div></div>
                        <div><div style="font-weight:700;color:#1e2a4a">{bal_q*last_avg:,.2f}</div><div style="font-size:.75rem;color:#7a8fc0">قيمة الرصيد</div></div>
                    </div>""", unsafe_allow_html=True)
                    st.dataframe(
                        prod_df[["doc_date","movement_type","warehouse","qty","unit_price","total","cost_center","الرصيد التراكمي"]].rename(columns={
                            "doc_date":"التاريخ","movement_type":"النوع","warehouse":"المخزن",
                            "qty":"الكمية","unit_price":"سعر الوحدة","total":"الإجمالي","cost_center":"مركز التكلفة"
                        }),
                        use_container_width=True, hide_index=True, height=500)

            else:  # حسب التصنيف
                cat_sum = df_mv.groupby(["category","movement_type"])["total"].sum().unstack(fill_value=0)
                cat_sum.columns.name = None
                cat_sum["صافي"] = cat_sum.get("اضافة",0) - cat_sum.get("صرف",0)
                cat_sum = cat_sum.sort_values("صافي", ascending=False).reset_index().rename(columns={"category":"التصنيف"})
                st.dataframe(cat_sum, use_container_width=True, hide_index=True, height=550)

    # ════ تاب 2: مشتريات ════
    with tabs_doc[1]:
        with st.expander(f"{'✅' if pur_count>0 else '📤'} رفع فواتير المشتريات", expanded=pur_count==0):
            up_pur = st.file_uploader("ملف المشتريات", type=["csv","xlsx"], key="pur_up")
            if up_pur:
                try:
                    df_pur = pd.read_csv(up_pur, encoding="utf-8-sig", dtype=str) if up_pur.name.endswith(".csv") else pd.read_excel(up_pur, engine="openpyxl", dtype=str)
                    df_pur.columns = [c.strip() for c in df_pur.columns]
                    st.success(f"✅ {len(df_pur):,} سطر")
                    if st.button("🚀 استيراد المشتريات", use_container_width=True, type="primary", key="pur_imp"):
                        conn_p = get_conn()
                        def g(r,c): return str(r.get(c,"") or "").strip() if pd.notna(r.get(c)) else ""
                        def gn(r,c):
                            try: return float(str(r.get(c,"")).replace(",",""))
                            except: return 0.0
                        rows_p = [(co_id, g(r,"المعرف"), g(r,"التاريخ"), g(r,"المورد"),
                                  g(r,"الاسم"), g(r,"كود المنتج"), g(r,"البند"),
                                  gn(r,"الكمية"), gn(r,"سعر الوحدة"), gn(r,"إجمالي الضرائب"), gn(r,"الإجمالي (EGP)"),
                                  g(r,"موظف")) for _, r in df_pur.iterrows()]
                        conn_p.executemany("INSERT INTO purchases (company_id,doc_no,doc_date,supplier,product_name,product_code,category,qty,unit_price,tax,total,employee) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", rows_p)
                        conn_p.commit(); conn_p.close()
                        st.success(f"✅ {len(rows_p):,} فاتورة"); st.rerun()
                except Exception as e: st.error(f"❌ {e}")

        if pur_count > 0:
            conn_pur2 = get_conn()
            df_pur2 = pd.read_sql("SELECT * FROM purchases WHERE company_id=%s", conn_pur2, params=(co_id,))
            conn_pur2.close()
            df_pur2["total"] = pd.to_numeric(df_pur2["total"], errors='coerce').fillna(0)
            df_pur2["qty"]   = pd.to_numeric(df_pur2["qty"],   errors='coerce').fillna(0)

            c1,c2 = st.columns(2)
            with c1: st.metric("إجمالي المشتريات", f"{df_pur2['total'].sum():,.2f}")
            with c2: st.metric("عدد الفواتير", f"{df_pur2['doc_no'].nunique():,}")

            view_pur = st.radio("", ["حسب المورد","حسب المنتج","كل الفواتير"], horizontal=True, key="pur_view")
            if view_pur == "حسب المورد":
                st.dataframe(df_pur2.groupby("supplier")["total"].sum().sort_values(ascending=False).reset_index(), use_container_width=True, hide_index=True)
            elif view_pur == "حسب المنتج":
                st.dataframe(df_pur2.groupby("product_name").agg(كمية=("qty","sum"), قيمة=("total","sum")).sort_values("قيمة",ascending=False).reset_index(), use_container_width=True, hide_index=True)
            else:
                st.dataframe(df_pur2[["doc_no","doc_date","supplier","product_name","qty","unit_price","total"]].head(500), use_container_width=True, hide_index=True, height=480)

    # ════ تاب 3: مبيعات ════
    with tabs_doc[2]:
        with st.expander(f"{'✅' if sal_count>0 else '📤'} رفع فواتير المبيعات", expanded=sal_count==0):
            up_sal = st.file_uploader("ملف المبيعات", type=["csv","xlsx"], key="sal_up")
            if up_sal:
                try:
                    df_sal = pd.read_csv(up_sal, encoding="utf-8-sig", dtype=str) if up_sal.name.endswith(".csv") else pd.read_excel(up_sal, engine="openpyxl", dtype=str)
                    df_sal.columns = [c.strip() for c in df_sal.columns]
                    st.success(f"✅ {len(df_sal):,} سطر")
                    if st.button("🚀 استيراد المبيعات", use_container_width=True, type="primary", key="sal_imp"):
                        conn_sl = get_conn()
                        def g(r,c): return str(r.get(c,"") or "").strip() if pd.notna(r.get(c)) else ""
                        def gn(r,c):
                            try: return float(str(r.get(c,"")).replace(",",""))
                            except: return 0.0
                        rows_sl = [(co_id, g(r,"رقم الفاتورة"), g(r,"التاريخ"), g(r,"العميل"),
                                   g(r,"الاسم"), g(r,"كود المنتج"),
                                   gn(r,"الكمية"), gn(r,"سعر الوحدة"), gn(r,"الخصم"), gn(r,"الضرائب"), gn(r,"الإجمالي (EGP)"),
                                   g(r,"بيعت بواسطة")) for _, r in df_sal.iterrows()]
                        conn_sl.executemany("INSERT INTO sales_invoices (company_id,doc_no,doc_date,client,product_name,product_code,qty,unit_price,discount,tax,total,employee) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", rows_sl)
                        conn_sl.commit(); conn_sl.close()
                        st.success(f"✅ {len(rows_sl):,}"); st.rerun()
                except Exception as e: st.error(f"❌ {e}")

        if sal_count > 0:
            conn_sal2 = get_conn()
            df_sal2 = pd.read_sql("SELECT * FROM sales_invoices WHERE company_id=%s", conn_sal2, params=(co_id,))
            conn_sal2.close()
            df_sal2["total"] = pd.to_numeric(df_sal2["total"], errors='coerce').fillna(0)
            c1,c2 = st.columns(2)
            with c1: st.metric("إجمالي المبيعات", f"{df_sal2['total'].sum():,.2f}")
            with c2: st.metric("عدد الفواتير", f"{df_sal2['doc_no'].nunique():,}")
            st.dataframe(df_sal2[["doc_no","doc_date","client","product_name","qty","unit_price","total"]].head(300), use_container_width=True, hide_index=True, height=460)

    # ════ تاب 4: مصروفات ════
    with tabs_doc[3]:
        with st.expander(f"{'✅' if exp_count>0 else '📤'} رفع المصروفات", expanded=exp_count==0):
            up_exp = st.file_uploader("ملف المصروفات", type=["csv","xlsx"], key="exp_up")
            if up_exp:
                try:
                    df_exp = pd.read_csv(up_exp, encoding="utf-8-sig", dtype=str) if up_exp.name.endswith(".csv") else pd.read_excel(up_exp, engine="openpyxl", dtype=str)
                    df_exp.columns = [c.strip() for c in df_exp.columns]
                    st.success(f"✅ {len(df_exp):,} سطر")
                    if st.button("🚀 استيراد المصروفات", use_container_width=True, type="primary", key="exp_imp"):
                        conn_e = get_conn()
                        def g(r,c): return str(r.get(c,"") or "").strip() if pd.notna(r.get(c)) else ""
                        def gn(r,c):
                            try: return float(str(r.get(c,"")).replace(",",""))
                            except: return 0.0
                        rows_e = [(co_id, g(r,"الكود"), g(r,"التاريخ"), g(r,"خزينة"),
                                  g(r,"التصنيف"), g(r,"البائع"), g(r,"الحساب الفرعي"),
                                  g(r,"موظف"), g(r,"ملاحظة"),
                                  gn(r,"المبلغ (EGP)"), gn(r,"الضرائب"), gn(r,"الإجمالي مع الضريبة (EGP)")) for _, r in df_exp.iterrows()]
                        conn_e.executemany("INSERT INTO expenses (company_id,doc_no,doc_date,treasury,category,supplier,account_code,employee,notes,amount,tax,total) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", rows_e)
                        conn_e.commit(); conn_e.close()
                        st.success(f"✅ {len(rows_e):,}"); st.rerun()
                except Exception as e: st.error(f"❌ {e}")

        if exp_count > 0:
            conn_exp2 = get_conn()
            df_exp2 = pd.read_sql("SELECT * FROM expenses WHERE company_id=%s", conn_exp2, params=(co_id,))
            conn_exp2.close()
            df_exp2["total"] = pd.to_numeric(df_exp2["total"], errors='coerce').fillna(0)
            c1,c2,c3 = st.columns(3)
            with c1: st.metric("إجمالي المصروفات", f"{df_exp2['total'].sum():,.2f}")
            with c2: st.metric("عدد السجلات", f"{len(df_exp2):,}")
            with c3: st.metric("عدد الموردين", f"{df_exp2['supplier'].nunique():,}")
            view_exp = st.radio("", ["حسب التصنيف","حسب المورد","كل السجلات"], horizontal=True, key="exp_view")
            if view_exp == "حسب التصنيف":
                st.dataframe(df_exp2.groupby("category")["total"].sum().sort_values(ascending=False).reset_index(), use_container_width=True, hide_index=True)
            elif view_exp == "حسب المورد":
                st.dataframe(df_exp2.groupby("supplier")["total"].sum().sort_values(ascending=False).reset_index(), use_container_width=True, hide_index=True)
            else:
                st.dataframe(df_exp2[["doc_no","doc_date","category","supplier","notes","amount","tax","total"]].head(300), use_container_width=True, hide_index=True, height=460)

    # ════ تاب 5: سندات القبض ════
    with tabs_doc[4]:
        with st.expander(f"{'✅' if rec_count>0 else '📤'} رفع سندات القبض", expanded=rec_count==0):
            up_rec = st.file_uploader("ملف سندات القبض", type=["csv","xlsx"], key="rec_up")
            if up_rec:
                try:
                    df_rec = pd.read_csv(up_rec, encoding="utf-8-sig", dtype=str) if up_rec.name.endswith(".csv") else pd.read_excel(up_rec, engine="openpyxl", dtype=str)
                    df_rec.columns = [c.strip() for c in df_rec.columns]
                    st.success(f"✅ {len(df_rec):,} سطر")
                    if st.button("🚀 استيراد سندات القبض", use_container_width=True, type="primary", key="rec_imp"):
                        conn_r = get_conn()
                        def g(r,c): return str(r.get(c,"") or "").strip() if pd.notna(r.get(c)) else ""
                        def gn(r,c):
                            try: return float(str(r.get(c,"")).replace(",",""))
                            except: return 0.0
                        rows_r = [(co_id, g(r,"الكود"), g(r,"التاريخ"), g(r,"خزينة"),
                                  g(r,"التصنيف"), g(r,"العميل"), g(r,"الحساب الفرعي"),
                                  g(r,"موظف"), g(r,"ملاحظة"), gn(r,"المبلغ (EGP)")) for _, r in df_rec.iterrows()]
                        conn_r.executemany("INSERT INTO receipts (company_id,doc_no,doc_date,treasury,category,client,account_code,employee,notes,amount) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", rows_r)
                        conn_r.commit(); conn_r.close()
                        st.success(f"✅ {len(rows_r):,}"); st.rerun()
                except Exception as e: st.error(f"❌ {e}")

        if rec_count > 0:
            conn_rec2 = get_conn()
            df_rec2 = pd.read_sql("SELECT * FROM receipts WHERE company_id=%s", conn_rec2, params=(co_id,))
            conn_rec2.close()
            df_rec2["amount"] = pd.to_numeric(df_rec2["amount"], errors='coerce').fillna(0)
            c1,c2 = st.columns(2)
            with c1: st.metric("إجمالي المقبوضات", f"{df_rec2['amount'].sum():,.2f}")
            with c2: st.metric("عدد العملاء", f"{df_rec2['client'].nunique():,}")
            st.dataframe(df_rec2.groupby("client")["amount"].sum().sort_values(ascending=False).reset_index(), use_container_width=True, hide_index=True)

    # ════ تاب 6: مرتبات ════
    with tabs_doc[5]:
        with st.expander(f"{'✅' if pay_count>0 else '📤'} رفع المرتبات", expanded=pay_count==0):
            up_pay = st.file_uploader("ملف المرتبات", type=["csv","xlsx"], key="pay_up")
            if up_pay:
                try:
                    df_pay = pd.read_csv(up_pay, encoding="utf-8-sig", dtype=str) if up_pay.name.endswith(".csv") else pd.read_excel(up_pay, engine="openpyxl", dtype=str)
                    df_pay.columns = [c.strip() for c in df_pay.columns]
                    st.success(f"✅ {len(df_pay):,} سطر")
                    if st.button("🚀 استيراد المرتبات", use_container_width=True, type="primary", key="pay_imp"):
                        conn_pw = get_conn()
                        def g(r,c): return str(r.get(c,"") or "").strip() if pd.notna(r.get(c)) else ""
                        def gn(r,c):
                            try: return float(str(r.get(c,"")).replace(",",""))
                            except: return 0.0
                        # الأعمدة المالية: اجمع كل البدلات والخصومات
                        money_cols_pay = [c for c in df_pay.columns if "(EGP)" in c]
                        allow_cols = [c for c in money_cols_pay if any(k in c for k in ["بدل","Over Time","Bounce","مكافأ","عمل","رصيد اجازات","عمولة"])]
                        deduct_cols = [c for c in money_cols_pay if any(k in c for k in ["خصم","غياب","ساعات العمل","Loan","اجازة"])]
                        rows_pw = []
                        for _, r in df_pay.iterrows():
                            basic = gn(r,"Basic  (EGP)")
                            allw  = sum(gn(r,c) for c in allow_cols)
                            dedt  = sum(gn(r,c) for c in deduct_cols)
                            gross = gn(r,"إجمالي الراتب (EGP)") or (basic+allw-dedt)
                            net   = gn(r,"صافي الراتب (EGP)") or gross
                            rows_pw.append((co_id, g(r,"قسيمه الراتب"), g(r,"موظف"), g(r,"الحالة"),
                                           g(r,"تاريخ البدء"), g(r,"تاريخ الإنتهاء"),
                                           basic, allw, dedt, gross, net))
                        conn_pw.executemany("INSERT INTO payroll (company_id,slip_no,employee,status,start_date,end_date,basic,allowances,deductions,gross,net) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", rows_pw)
                        conn_pw.commit(); conn_pw.close()
                        st.success(f"✅ {len(rows_pw):,} قسيمة"); st.rerun()
                except Exception as e: st.error(f"❌ {e}")

        if pay_count > 0:
            conn_pw2 = get_conn()
            df_pw2 = pd.read_sql("SELECT * FROM payroll WHERE company_id=%s", conn_pw2, params=(co_id,))
            conn_pw2.close()
            for col in ["basic","allowances","deductions","gross","net"]:
                df_pw2[col] = pd.to_numeric(df_pw2[col], errors='coerce').fillna(0)
            c1,c2,c3 = st.columns(3)
            with c1: st.metric("إجمالي الرواتب الصافية", f"{df_pw2['net'].sum():,.2f}")
            with c2: st.metric("إجمالي الرواتب الإجمالية", f"{df_pw2['gross'].sum():,.2f}")
            with c3: st.metric("عدد الموظفين", f"{df_pw2['employee'].nunique():,}")
            st.dataframe(df_pw2[["employee","start_date","end_date","basic","allowances","deductions","gross","net"]].sort_values("net",ascending=False), use_container_width=True, hide_index=True, height=480)
            st.download_button("⬇️ تحميل المرتبات", data=df_pw2.to_csv(index=False, encoding="utf-8-sig"), file_name="المرتبات.csv", mime="text/csv")


# ════════════════════════════════════════════════════════
# ══ صفحة إدارة التطابق (Mapping) ══
# ════════════════════════════════════════════════════════
elif page == "🔗  إدارة التطابق":
    st.markdown('<div class="page-header"><p class="ph-title">🔗 إدارة التطابق</p><p class="ph-sub">دمج المنتجات المكررة والتصنيفات ومراكز التكلفة</p></div>', unsafe_allow_html=True)

    map_tabs = st.tabs(["📦 المنتجات", "🏷️ التصنيفات", "📍 مراكز التكلفة"])

    # ════ تاب 1: المنتجات ════
    with map_tabs[0]:
        st.markdown("""<div class="info-box">هنا تقدر تدمج منتجات بنفس الاسم أو أكواد مختلفة تحت اسم موحد واحد.
        بعد الدمج، كل التقارير هتعرض الاسم الموحد.</div>""", unsafe_allow_html=True)

        # جلب كل المنتجات من المخزن
        conn_mp = get_conn()
        all_prods = pd.read_sql(
            "SELECT DISTINCT product_name, product_code, category FROM stock_movements WHERE company_id=%s AND product_name IS NOT NULL ORDER BY product_name",
            conn_mp, params=(co_id,))
        existing_maps = pd.read_sql(
            "SELECT * FROM product_mapping WHERE company_id=%s AND entity_type='product'",
            conn_mp, params=(co_id,))
        conn_mp.close()

        if all_prods.empty:
            st.info("ارفع بيانات المخزن أولاً"); 
        else:
            # اكتشاف تلقائي للمكرر
            dup_names = all_prods.groupby("product_name")["product_code"].nunique()
            dup_names = dup_names[dup_names > 1].index.tolist()
            dup_cats  = all_prods.groupby("product_name")["category"].nunique()
            dup_cats  = dup_cats[dup_cats > 1].index.tolist()
            all_dups  = list(set(dup_names + dup_cats))

            c1, c2 = st.columns([2,1])
            with c1:
                st.markdown(f'<div class="warning-box">⚠️ {len(all_dups)} منتج مكرر تلقائياً — {len(dup_names)} بأكواد مختلفة، {len(dup_cats)} بتصنيفات مختلفة</div>', unsafe_allow_html=True)
            with c2:
                show_only_dups = st.checkbox("عرض المكرر فقط", value=True, key="show_dups")

            # جدول للإضافة
            st.markdown('<div class="sec-title">➕ إضافة تطابق جديد</div>', unsafe_allow_html=True)

            display_prods = all_prods[all_prods["product_name"].isin(all_dups)] if show_only_dups else all_prods
            prod_options = sorted(display_prods["product_name"].unique().tolist())

            with st.form("add_prod_map"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    src_prod = st.selectbox("الاسم الأصلي (المصدر)", ["—"] + prod_options, key="mp_src")
                with col2:
                    # اقتراح الاسم الموحد
                    default_unified = src_prod if src_prod != "—" else ""
                    unified_name = st.text_input("الاسم الموحد", value=default_unified, key="mp_dst")
                with col3:
                    cat_opts = sorted(all_prods["category"].dropna().unique().tolist())
                    unified_cat = st.selectbox("التصنيف الموحد (اختياري)", ["— نفس الأصلي —"] + cat_opts, key="mp_cat")

                # عرض تفاصيل المنتج المختار
                if src_prod != "—":
                    prod_detail = all_prods[all_prods["product_name"]==src_prod]
                    st.markdown(f"""<div style="background:#f8faff;border-radius:8px;padding:.5rem .8rem;font-size:.8rem;color:#374151">
                        الكود: {' / '.join(prod_detail["product_code"].dropna().unique().tolist())} &nbsp;|&nbsp;
                        التصنيف: {' / '.join(prod_detail["category"].dropna().unique().tolist())}
                    </div>""", unsafe_allow_html=True)

                save_map = st.form_submit_button("💾 حفظ التطابق", use_container_width=True)
                if save_map and src_prod != "—" and unified_name.strip():
                    codes = all_prods[all_prods["product_name"]==src_prod]["product_code"].dropna().unique().tolist()
                    cat_val = None if unified_cat == "— نفس الأصلي —" else unified_cat
                    conn_sv = get_conn()
                    for code in (codes if codes else [""]):
                        conn_sv.execute(
                            "REPLACE INTO product_mapping (company_id,original_name,original_code,mapped_name,mapped_category,entity_type) VALUES (%s,%s,%s,%s,%s,%s)",
                            (co_id, src_prod, str(code), unified_name.strip(), cat_val, "product"))
                    conn_sv.commit(); conn_sv.close()
                    st.success(f"✅ تم: '{src_prod}' → '{unified_name}'"); st.rerun()

            # عرض التطابقات الموجودة
            if not existing_maps.empty:
                st.markdown('<div class="sec-title">التطابقات المحفوظة</div>', unsafe_allow_html=True)
                disp_maps = existing_maps[["original_name","original_code","mapped_name","mapped_category"]].rename(columns={
                    "original_name":"الأصلي","original_code":"الكود","mapped_name":"الموحد","mapped_category":"التصنيف الموحد"
                })
                st.dataframe(disp_maps, use_container_width=True, hide_index=True, height=250)
                if st.button("🗑️ مسح كل التطابقات", key="clear_pmaps"):
                    conn_cl = get_conn()
                    conn_cl.execute("DELETE FROM product_mapping WHERE company_id=%s AND entity_type='product'", (co_id,))
                    conn_cl.commit(); conn_cl.close()
                    st.rerun()

    # ════ تاب 2: التصنيفات ════
    with map_tabs[1]:
        st.markdown("""<div class="info-box">دمج تصنيفات متشابهة — مثلاً "اكسسوارات" و"اكسسورات" يبقوا تصنيف واحد.</div>""", unsafe_allow_html=True)

        conn_cm = get_conn()
        all_cats_db = pd.read_sql(
            "SELECT DISTINCT category FROM stock_movements WHERE company_id=%s AND category IS NOT NULL ORDER BY category",
            conn_cm, params=(co_id,))
        existing_cmaps = pd.read_sql("SELECT * FROM category_mapping WHERE company_id=%s", conn_cm, params=(co_id,))
        conn_cm.close()

        if all_cats_db.empty:
            st.info("ارفع بيانات المخزن أولاً")
        else:
            cats_list = all_cats_db["category"].tolist()
            # اقتراح تلقائي للمتشابهة
            from difflib import SequenceMatcher
            similar_pairs = []
            for i in range(len(cats_list)):
                for j in range(i+1, len(cats_list)):
                    ratio = SequenceMatcher(None, cats_list[i], cats_list[j]).ratio()
                    if ratio >= 0.7:
                        similar_pairs.append((cats_list[i], cats_list[j], round(ratio*100)))

            if similar_pairs:
                st.markdown(f'<div class="warning-box">⚠️ {len(similar_pairs)} تصنيف متشابه تلقائياً</div>', unsafe_allow_html=True)
                for a, b, pct in similar_pairs[:10]:
                    col1, col2, col3, col4 = st.columns([3,3,1,1])
                    with col1: st.markdown(f'<div style="padding:.3rem .5rem;background:#fff8e1;border-radius:6px;font-size:.85rem">{a}</div>', unsafe_allow_html=True)
                    with col2: st.markdown(f'<div style="padding:.3rem .5rem;background:#fff8e1;border-radius:6px;font-size:.85rem">{b}</div>', unsafe_allow_html=True)
                    with col3: st.markdown(f'<div style="padding:.3rem;color:#e67700;font-weight:700;font-size:.82rem">{pct}%</div>', unsafe_allow_html=True)
                    with col4:
                        if st.button("دمج ←", key=f"merge_cat_{a}_{b}"):
                            conn_mc = get_conn()
                            conn_mc.execute("REPLACE INTO category_mapping (company_id,original_category,mapped_category) VALUES (%s,%s,%s)", (co_id, b, a))
                            conn_mc.commit(); conn_mc.close()
                            st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="sec-title">➕ إضافة تطابق يدوي</div>', unsafe_allow_html=True)
            with st.form("add_cat_map"):
                col1, col2 = st.columns(2)
                with col1: src_cat = st.selectbox("التصنيف الأصلي", ["—"] + cats_list, key="cm_src")
                with col2: dst_cat = st.selectbox("يُدمج مع", ["—"] + cats_list, key="cm_dst")
                if st.form_submit_button("💾 دمج", use_container_width=True) and src_cat != "—" and dst_cat != "—" and src_cat != dst_cat:
                    conn_mc2 = get_conn()
                    conn_mc2.execute("REPLACE INTO category_mapping (company_id,original_category,mapped_category) VALUES (%s,%s,%s)", (co_id, src_cat, dst_cat))
                    conn_mc2.commit(); conn_mc2.close()
                    st.success(f"✅ '{src_cat}' → '{dst_cat}'"); st.rerun()

            if not existing_cmaps.empty:
                st.markdown('<div class="sec-title">التطابقات المحفوظة</div>', unsafe_allow_html=True)
                st.dataframe(existing_cmaps[["original_category","mapped_category"]].rename(columns={"original_category":"الأصلي","mapped_category":"الموحد"}),
                             use_container_width=True, hide_index=True)
                if st.button("🗑️ مسح", key="clr_cmaps"):
                    conn_cl2 = get_conn()
                    conn_cl2.execute("DELETE FROM category_mapping WHERE company_id=%s", (co_id,))
                    conn_cl2.commit(); conn_cl2.close(); st.rerun()

    # ════ تاب 3: مراكز التكلفة ════
    with map_tabs[2]:
        st.markdown("""<div class="info-box">دمج مراكز تكلفة بأسماء مختلفة لنفس المشروع.</div>""", unsafe_allow_html=True)

        conn_cc = get_conn()
        all_cc_db = pd.read_sql(
            "SELECT DISTINCT cost_center FROM stock_movements WHERE company_id=%s AND cost_center IS NOT NULL AND cost_center!='' UNION SELECT DISTINCT cost_center FROM cost_center_entries WHERE company_id=%s AND cost_center IS NOT NULL AND cost_center!='' ORDER BY cost_center",
            conn_cc, params=(co_id, co_id))
        existing_ccmaps = pd.read_sql("SELECT * FROM cost_center_mapping WHERE company_id=%s", conn_cc, params=(co_id,))
        conn_cc.close()

        if all_cc_db.empty:
            st.info("لا توجد مراكز تكلفة")
        else:
            cc_list = all_cc_db["cost_center"].tolist()
            st.markdown(f'<div class="info-box">📍 {len(cc_list)} مركز تكلفة</div>', unsafe_allow_html=True)

            with st.form("add_cc_map"):
                col1, col2 = st.columns(2)
                with col1: src_cc = st.selectbox("مركز التكلفة الأصلي", ["—"] + cc_list, key="ccm_src")
                with col2: dst_cc = st.text_input("الاسم الموحد", key="ccm_dst", placeholder="اكتب الاسم الموحد...")
                if st.form_submit_button("💾 دمج", use_container_width=True) and src_cc != "—" and dst_cc.strip():
                    conn_cc3 = get_conn()
                    conn_cc3.execute("REPLACE INTO cost_center_mapping (company_id,original_name,mapped_name) VALUES (%s,%s,%s)", (co_id, src_cc, dst_cc.strip()))
                    conn_cc3.commit(); conn_cc3.close()
                    st.success(f"✅ '{src_cc}' → '{dst_cc}'"); st.rerun()

            if not existing_ccmaps.empty:
                st.markdown('<div class="sec-title">التطابقات المحفوظة</div>', unsafe_allow_html=True)
                st.dataframe(existing_ccmaps[["original_name","mapped_name"]].rename(columns={"original_name":"الأصلي","mapped_name":"الموحد"}),
                             use_container_width=True, hide_index=True)
                if st.button("🗑️ مسح", key="clr_ccmaps"):
                    conn_cl3 = get_conn()
                    conn_cl3.execute("DELETE FROM cost_center_mapping WHERE company_id=%s", (co_id,))
                    conn_cl3.commit(); conn_cl3.close(); st.rerun()

# ════════════════════════════════════════════════════════
# ══ صفحة تقرير التكلفة المدمج ══
# ════════════════════════════════════════════════════════
elif page == "🔬  تقرير التكلفة المدمج":
    st.markdown('<div class="page-header"><p class="ph-title">🔬 تقرير التكلفة المدمج</p><p class="ph-sub">كمية وقيمة المصروفات على مراكز التكلفة — مدمج من الإذونات ومراكز التكلفة</p></div>', unsafe_allow_html=True)

    conn_lnk = get_conn()
    inv_count = conn_lnk.execute("SELECT COUNT(*) FROM stock_movements WHERE company_id=%s AND movement_type='صرف'", (co_id,)).fetchone()[0]
    cc_count2 = conn_lnk.execute("SELECT COUNT(*) FROM cost_center_entries WHERE company_id=%s", (co_id,)).fetchone()[0]
    conn_lnk.close()

    if inv_count == 0 or cc_count2 == 0:
        st.markdown('<div class="warning-box">⚠️ محتاج ترفع إذونات المخزن ومراكز التكلفة أولاً من صفحة المخزن والمستندات</div>', unsafe_allow_html=True)
        if inv_count == 0: st.markdown('- ❌ إذونات المخزن', unsafe_allow_html=True)
        if cc_count2 == 0: st.markdown('- ❌ مراكز التكلفة', unsafe_allow_html=True)
    else:
        # ── جلب البيانات ──
        conn_r = get_conn()
        df_inv2 = pd.read_sql(
            "SELECT * FROM stock_movements WHERE company_id=%s AND movement_type='صرف'",
            conn_r, params=(co_id,))
        df_cc2  = pd.read_sql(
            "SELECT * FROM cost_center_entries WHERE company_id=%s",
            conn_r, params=(co_id,))
        conn_r.close()

        # تحويل الأرقام
        for c in ["qty","unit_price","total"]: df_inv2[c] = pd.to_numeric(df_inv2[c], errors='coerce').fillna(0)
        df_cc2["debit"] = pd.to_numeric(df_cc2["debit"], errors='coerce').fillna(0)

        # تنظيف ضريبي/غير ضريبي من التصنيف
        import re
        df_cc2["cat_clean"] = df_cc2["category"].str.replace(r'\s*(ضريبي|غير ضريبي)\s*$','',regex=True).str.strip()
        df_inv2["cat_clean"] = df_inv2["category"].str.replace(r'\s*(ضريبي|غير ضريبي)\s*$','',regex=True).str.strip()

        # ── فلاتر ──
        all_centers = sorted(df_cc2["cost_center"].dropna().unique().tolist())
        all_cats    = sorted(df_cc2["cat_clean"].dropna().unique().tolist())
        date_min = df_cc2["entry_date"].dropna().min()
        date_max = df_cc2["entry_date"].dropna().max()

        f1, f2, f3, f4 = st.columns([2, 2, 1.5, 1.5])
        with f1: sel_ctr = st.selectbox("مركز التكلفة", ["كل المراكز"] + all_centers, key="lnk_center")
        with f2: sel_cat = st.selectbox("التصنيف", ["كل التصنيفات"] + all_cats, key="lnk_cat")
        with f3: d_from  = st.date_input("من", value=None, key="lnk_from")
        with f4: d_to    = st.date_input("إلى", value=None, key="lnk_to")

        # تطبيق الفلاتر
        fcc  = df_cc2.copy()
        finv = df_inv2.copy()
        if sel_ctr != "كل المراكز":
            fcc  = fcc[fcc["cost_center"]==sel_ctr]
            finv = finv[finv["cost_center"]==sel_ctr]
        if sel_cat != "كل التصنيفات":
            fcc  = fcc[fcc["cat_clean"]==sel_cat]
            finv = finv[finv["cat_clean"]==sel_cat]
        if d_from: fcc = fcc[fcc["entry_date"] >= str(d_from)]
        if d_to:   fcc = fcc[fcc["entry_date"] <= str(d_to)]

        # ── تقرير 1: مراكز التكلفة × تصنيف (قيمة + كمية) ──
        view_lnk = tab_bar(["📊 مركز × تصنيف", "📦 كمية بالتصنيف", "🔍 منتج محدد", "⚠️ بدون كمية"], "lnk_view")

        if view_lnk == "📊 مركز × تصنيف":
            # قيمة محاسبية من مراكز التكلفة
            cc_grp = fcc.groupby(["cost_center","cat_clean"])["debit"].sum().reset_index()
            cc_grp.columns = ["المشروع","التصنيف","القيمة المحاسبية"]

            # كمية وقيمة من الإذونات المباشرة
            inv_grp = finv[finv["cost_center"].notna() & (finv["cost_center"]!="")].groupby(
                ["cost_center","cat_clean"]).agg(كمية=("qty","sum"), قيمة_الإذن=("total","sum")).reset_index()
            inv_grp.columns = ["المشروع","التصنيف","الكمية","قيمة الإذن"]

            merged = cc_grp.merge(inv_grp, on=["المشروع","التصنيف"], how="left")
            merged["الكمية"] = merged["الكمية"].fillna(0)
            merged["قيمة الإذن"] = merged["قيمة الإذن"].fillna(0)
            merged["لها كمية"] = merged["الكمية"] > 0
            merged = merged.sort_values("القيمة المحاسبية", ascending=False)

            # إحصائيات
            s1,s2,s3,s4 = st.columns(4)
            with s1: st.markdown(f'<div class="stat-card"><div class="s-num" style="font-size:1rem">{merged["القيمة المحاسبية"].sum():,.0f}</div><div class="s-lbl">إجمالي القيمة</div></div>', unsafe_allow_html=True)
            with s2: st.markdown(f'<div class="stat-card green"><div class="s-num">{merged[merged["لها كمية"]]["الكمية"].sum():,.1f}</div><div class="s-lbl">كمية مباشرة</div></div>', unsafe_allow_html=True)
            with s3: st.markdown(f'<div class="stat-card orange"><div class="s-num">{merged["لها كمية"].sum()}</div><div class="s-lbl">بيانات مكتملة</div></div>', unsafe_allow_html=True)
            with s4: st.markdown(f'<div class="stat-card red"><div class="s-num">{(~merged["لها كمية"]).sum()}</div><div class="s-lbl">تحتاج كمية يدوي</div></div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

            # الجدول
            disp = merged[["المشروع","التصنيف","القيمة المحاسبية","الكمية","قيمة الإذن"]].copy()
            disp["القيمة المحاسبية"] = disp["القيمة المحاسبية"].apply(lambda x: f"{x:,.2f}")
            disp["الكمية"] = disp["الكمية"].apply(lambda x: f"{x:,.2f}" if x > 0 else "⚠️ —")
            disp["قيمة الإذن"] = disp["قيمة الإذن"].apply(lambda x: f"{x:,.2f}" if x > 0 else "—")
            st.dataframe(disp, use_container_width=True, hide_index=True, height=580)
            st.download_button("⬇️ تحميل", data=merged.to_csv(index=False, encoding="utf-8-sig"),
                               file_name="تقرير_التكلفة_المدمج.csv", mime="text/csv")

        elif view_lnk == "📦 كمية بالتصنيف":
            # من الإذونات فقط — كمية دقيقة
            inv_cat = finv[finv["cost_center"].notna() & (finv["cost_center"]!="")].groupby("cat_clean").agg(
                كمية=("qty","sum"), قيمة=("total","sum"), منتجات=("product_name","nunique")
            ).reset_index().rename(columns={"cat_clean":"التصنيف"}).sort_values("قيمة",ascending=False)

            st.markdown('<div class="info-box">💡 هذا التقرير من الإذونات التي لها مركز تكلفة مباشر فقط</div>', unsafe_allow_html=True)
            st.dataframe(inv_cat, use_container_width=True, hide_index=True, height=480)

        elif view_lnk == "🔍 منتج محدد":
            all_prods = sorted(finv["product_name"].dropna().unique().tolist())
            sel_prod2 = st.selectbox("المنتج", ["— اختر —"] + all_prods, key="lnk_prod")
            if sel_prod2 != "— اختر —":
                prod_data = finv[finv["product_name"]==sel_prod2]
                prod_cc = prod_data.groupby("cost_center").agg(
                    كمية=("qty","sum"), قيمة=("total","sum"), عدد_الإذونات=("doc_no","nunique")
                ).reset_index().rename(columns={"cost_center":"المشروع"}).sort_values("كمية",ascending=False)

                total_q = prod_data["qty"].sum()
                avg_p   = prod_data["total"].sum() / max(total_q,1)
                st.markdown(f"""<div class="ledger-header">
                    <div style="font-size:1.1rem;font-weight:900;color:#1e2a4a">{sel_prod2}</div>
                    <div style="display:flex;gap:2rem;margin-top:.5rem;flex-wrap:wrap">
                        <div><b style="color:#c92a2a">{total_q:,.2f}</b><br><span style="font-size:.75rem;color:#666">إجمالي الكمية</span></div>
                        <div><b style="color:#2f9e44">{prod_data["total"].sum():,.2f}</b><br><span style="font-size:.75rem;color:#666">إجمالي القيمة</span></div>
                        <div><b style="color:#3b5bdb">{avg_p:,.2f}</b><br><span style="font-size:.75rem;color:#666">متوسط السعر</span></div>
                        <div><b style="color:#1e2a4a">{prod_data["cost_center"].nunique()}</b><br><span style="font-size:.75rem;color:#666">مشروع</span></div>
                    </div>
                </div>""", unsafe_allow_html=True)
                st.dataframe(prod_cc, use_container_width=True, hide_index=True)

        else:  # بدون كمية
            no_qty = fcc.groupby(["cost_center","cat_clean"])["debit"].sum().reset_index()
            no_qty.columns = ["المشروع","التصنيف","القيمة"]
            # استثناء اللي عندها كمية
            has_qty = set(zip(
                finv[finv["cost_center"].notna() & (finv["cost_center"]!="")]["cost_center"],
                finv[finv["cost_center"].notna() & (finv["cost_center"]!="")]["cat_clean"]
            ))
            no_qty["لها_كمية"] = no_qty.apply(lambda r: (r["المشروع"],r["التصنيف"]) in has_qty, axis=1)
            missing_qty = no_qty[~no_qty["لها_كمية"]].drop(columns=["لها_كمية"]).sort_values("القيمة",ascending=False)

            st.markdown(f'<div class="warning-box">⚠️ {len(missing_qty)} تصنيف/مشروع بدون كمية — تحتاج إدخال يدوي</div>', unsafe_allow_html=True)
            st.markdown('<div class="info-box">💡 سيتم إضافة إمكانية التعديل اليدوي للكمية في التحديث القادم</div>', unsafe_allow_html=True)
            st.dataframe(missing_qty, use_container_width=True, hide_index=True, height=550)
            st.download_button("⬇️ تحميل للمراجعة", data=missing_qty.to_csv(index=False, encoding="utf-8-sig"),
                               file_name="يحتاج_كمية.csv", mime="text/csv")


# ════════════════════════════════════════════════════════
# ══ صفحة ربط الإذونات بالقيود ══
# ════════════════════════════════════════════════════════
elif page == "🔀  ربط الاذونات بالقيود":
    st.markdown('<div class="page-header"><p class="ph-title">ربط الاذونات بالقيود</p><p class="ph-sub">مطابقة حركات المخزن مع قيود دفتر الأستاذ عن طريق رقم الإذن</p></div>', unsafe_allow_html=True)

    import re as _re

    conn_lnk2 = get_conn()
    stk_count2 = conn_lnk2.execute("SELECT COUNT(*) FROM stock_movements WHERE company_id=%s", (co_id,)).fetchone()[0]
    j_count2   = conn_lnk2.execute("SELECT COUNT(*) FROM journal_lines WHERE company_id=%s",  (co_id,)).fetchone()[0]
    conn_lnk2.close()

    if stk_count2 == 0 or j_count2 == 0:
        st.markdown('<div class="warning-box">محتاج ترفع إذونات المخزن وحركات دفتر الأستاذ أولاً</div>', unsafe_allow_html=True)
        if stk_count2 == 0: st.markdown("- إذونات المخزن: غير مرفوعة")
        if j_count2   == 0: st.markdown("- حركات دفتر الأستاذ: غير مرفوعة")
    else:
        # ── جلب البيانات ──
        conn_lnk3 = get_conn()
        df_stk_lnk = pd.read_sql("SELECT doc_no, doc_date, movement_type, warehouse, product_name, product_code, qty, unit_price, total FROM stock_movements WHERE company_id=%s", conn_lnk3, params=(co_id,))
        df_j_lnk   = pd.read_sql("SELECT entry_no, account_code, account_name, notes as description, debit, credit FROM journal_lines WHERE company_id=%s", conn_lnk3, params=(co_id,))
        conn_lnk3.close()

        for c in ["qty","unit_price","total"]:
            df_stk_lnk[c] = pd.to_numeric(df_stk_lnk[c], errors="coerce").fillna(0)
        for c in ["debit","credit"]:
            df_j_lnk[c] = pd.to_numeric(df_j_lnk[c], errors="coerce").fillna(0)

        # ── استخراج رقم الإذن من الوصف ──
        # يدعم: #7583 | (7583) | اذن 7583 | إذن رقم 7583
        def extract_doc_from_desc(val):
            s = str(val or "").strip()
            # أنماط متعددة
            patterns = [
                r'#(\d{3,})',           # #7583
                r'\(#%s(\d{3,})\)',    # (#7583) أو (7583)
                r'رقم[\s:]+(\d{3,})', # رقم 7583
                r'اذن[\s:]+(\d{3,})', # اذن 7583
                r'إذن[\s:]+(\d{3,})', # إذن 7583
                r'no[.\s:]+(\d{3,})', # No. 7583
            ]
            for p in patterns:
                m = _re.search(p, s, _re.IGNORECASE)
                if m: return m.group(1)
            return ""

        df_j_lnk["extracted_doc_no"] = df_j_lnk["description"].apply(extract_doc_from_desc)

        # ── إحصائيات الاستخراج ──
        matched_j   = df_j_lnk[df_j_lnk["extracted_doc_no"] != ""]
        unmatched_j = df_j_lnk[df_j_lnk["extracted_doc_no"] == ""]

        stk_doc_nos = set(df_stk_lnk["doc_no"].astype(str).str.strip())
        j_doc_nos   = set(matched_j["extracted_doc_no"].astype(str).str.strip())
        common_docs = stk_doc_nos & j_doc_nos

        c1,c2,c3,c4 = st.columns(4)
        with c1: st.markdown(f'<div class="stat-card"><div class="s-num">{len(stk_doc_nos):,}</div><div class="s-lbl">إذن في المخزن</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="stat-card green"><div class="s-num" style="color:#2f9e44">{len(j_doc_nos):,}</div><div class="s-lbl">إذن في القيود</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="stat-card"><div class="s-num" style="color:#3b5bdb">{len(common_docs):,}</div><div class="s-lbl">مطابق</div></div>', unsafe_allow_html=True)
        with c4: st.markdown(f'<div class="stat-card orange"><div class="s-num" style="color:#e67700">{len(stk_doc_nos - j_doc_nos):,}</div><div class="s-lbl">غير مطابق</div></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # ── عرض عينة من الوصف عشان نتحقق من الاستخراج ──
        with st.expander("عينة من استخراج رقم الإذن من الوصف"):
            sample = df_j_lnk[df_j_lnk["extracted_doc_no"] != ""][["description","extracted_doc_no"]].head(15)
            st.dataframe(sample, use_container_width=True, hide_index=True)
            if len(unmatched_j) > 0:
                st.markdown(f'<div class="warning-box">{len(unmatched_j):,} قيد مش عارف يستخرج منه رقم الإذن — اضغط لعرض عينة</div>', unsafe_allow_html=True)
                st.dataframe(unmatched_j[["description","entry_no"]].head(10), use_container_width=True, hide_index=True)

        # ── اختيار طريقة العرض ──
        view_lnk2 = tab_bar([
            "تقرير مدمج",
            "اذن محدد",
            "قيود بدون اذن",
            "اذونات بدون قيود",
        ], "lnk2_view")

        if view_lnk2 == "تقرير مدمج":
            st.markdown('<div class="sec-title">تقرير مدمج — كل إذن مع قيوده المحاسبية</div>', unsafe_allow_html=True)

            # دمج المخزن مع القيود
            df_stk_lnk["doc_no"] = df_stk_lnk["doc_no"].astype(str).str.strip()
            matched_j2 = matched_j.copy()
            matched_j2["extracted_doc_no"] = matched_j2["extracted_doc_no"].astype(str).str.strip()

            # ملخص لكل إذن في المخزن
            stk_summary = df_stk_lnk.groupby("doc_no").agg(
                المنتجات   = ("product_name", lambda x: " | ".join(x.unique()[:2])),
                الكمية     = ("qty", "sum"),
                قيمة_المخزن= ("total", "sum"),
                التاريخ    = ("doc_date", "first"),
                المخزن     = ("warehouse", "first"),
            ).reset_index()

            # ملخص لكل إذن في القيود
            j_summary = matched_j2.groupby("extracted_doc_no").agg(
                مدين_القيود  = ("debit", "sum"),
                دائن_القيود  = ("credit", "sum"),
                عدد_القيود   = ("entry_no", "nunique"),
                الحسابات     = ("account_name", lambda x: " | ".join(x.dropna().unique()[:3])),
            ).reset_index().rename(columns={"extracted_doc_no": "doc_no"})

            merged = stk_summary.merge(j_summary, on="doc_no", how="outer")

            # حساب الفرق
            merged["قيمة_المخزن"]  = merged["قيمة_المخزن"].fillna(0)
            merged["مدين_القيود"]  = merged["مدين_القيود"].fillna(0)
            merged["الفرق"]        = (merged["قيمة_المخزن"] - merged["مدين_القيود"]).round(2)
            merged["الحالة"]       = merged["الفرق"].apply(
                lambda x: "متطابق" if abs(x) < 0.01 else ("فرق" if abs(x) < 100 else "فرق كبير"))

            # فلتر الحالة
            f1, f2 = st.columns([2, 3])
            with f1:
                status_filter = st.selectbox("فلتر الحالة", ["الكل","متطابق","فرق","فرق كبير"], key="lnk2_status")
            with f2:
                doc_search = st.text_input("بحث برقم الإذن أو اسم المنتج", placeholder="اكتب...", key="lnk2_srch")

            if status_filter != "الكل":
                merged = merged[merged["الحالة"] == status_filter]
            if doc_search:
                merged = merged[
                    merged["doc_no"].str.contains(doc_search, na=False) |
                    merged["المنتجات"].str.contains(doc_search, case=False, na=False)
                ]

            # جدول HTML
            rows_html = ""
            for _, r in merged.sort_values("التاريخ", ascending=False).head(200).iterrows():
                status_color = {"متطابق":"#2f9e44","فرق":"#e67700","فرق كبير":"#c92a2a"}.get(r.get("الحالة",""), "#7a8fc0")
                status_bg    = {"متطابق":"#f0fdf4","فرق":"#fffbeb","فرق كبير":"#fef2f2"}.get(r.get("الحالة",""), "white")
                rows_html += f"""<tr style="background:{status_bg};border-bottom:1px solid #f0f2f8">
                    <td style="padding:.45rem .8rem;color:#3b5bdb;font-weight:700;font-size:.85rem">{r["doc_no"]}</td>
                    <td style="padding:.45rem .8rem;color:#374151;font-size:.82rem">{str(r.get("التاريخ",""))[:10]}</td>
                    <td style="padding:.45rem .8rem;color:#374151;font-size:.8rem;max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{r.get("المنتجات","")}</td>
                    <td style="padding:.45rem .8rem;color:#7a8fc0;font-size:.8rem">{r.get("المخزن","")}</td>
                    <td style="padding:.45rem .8rem;color:#1e2a4a;text-align:left;font-family:monospace">{r.get("الكمية",0):,.2f}</td>
                    <td style="padding:.45rem .8rem;color:#3b5bdb;text-align:left;font-family:monospace">{r.get("قيمة_المخزن",0):,.2f}</td>
                    <td style="padding:.45rem .8rem;color:#2f9e44;text-align:left;font-family:monospace">{r.get("مدين_القيود",0):,.2f}</td>
                    <td style="padding:.45rem .8rem;color:#c92a2a;text-align:left;font-family:monospace">{r.get("الفرق",0):,.2f}</td>
                    <td style="padding:.45rem .8rem;text-align:center">
                        <span style="background:{status_color};color:white;padding:2px 8px;border-radius:10px;font-size:.72rem;font-weight:700">{r.get("الحالة","")}</span>
                    </td>
                    <td style="padding:.45rem .8rem;color:#7a8fc0;font-size:.75rem;max-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{r.get("الحسابات","")}</td>
                </tr>"""

            tot_stk = merged["قيمة_المخزن"].sum()
            tot_j   = merged["مدين_القيود"].sum()
            tot_dif = merged["الفرق"].sum()

            st.markdown(f"""
            <div style="background:white;border-radius:12px;overflow:hidden;box-shadow:0 1px 8px rgba(0,0,0,.06);max-height:600px;overflow-y:auto">
            <table style="width:100%;border-collapse:collapse;direction:rtl">
                <thead style="position:sticky;top:0;z-index:1"><tr style="background:#1e2a4a;color:white">
                    <th style="padding:.55rem .6rem;font-size:.78rem">رقم الإذن</th>
                    <th style="padding:.55rem .6rem;font-size:.78rem">التاريخ</th>
                    <th style="padding:.55rem .6rem;font-size:.78rem">المنتجات</th>
                    <th style="padding:.55rem .6rem;font-size:.78rem">المخزن</th>
                    <th style="padding:.55rem .6rem;font-size:.78rem;text-align:left">الكمية</th>
                    <th style="padding:.55rem .6rem;font-size:.78rem;text-align:left">قيمة المخزن</th>
                    <th style="padding:.55rem .6rem;font-size:.78rem;text-align:left">مدين القيود</th>
                    <th style="padding:.55rem .6rem;font-size:.78rem;text-align:left">الفرق</th>
                    <th style="padding:.55rem .6rem;font-size:.78rem;text-align:center">الحالة</th>
                    <th style="padding:.55rem .6rem;font-size:.78rem">الحسابات</th>
                </tr></thead>
                <tbody>{rows_html}</tbody>
                <tfoot><tr style="background:#f0f4ff;font-weight:900;border-top:2px solid #1e2a4a">
                    <td colspan="5" style="padding:.55rem .8rem;color:#1e2a4a">الإجمالي</td>
                    <td style="padding:.55rem .6rem;color:#3b5bdb;font-family:monospace;text-align:left">{tot_stk:,.2f}</td>
                    <td style="padding:.55rem .6rem;color:#2f9e44;font-family:monospace;text-align:left">{tot_j:,.2f}</td>
                    <td style="padding:.55rem .6rem;color:#c92a2a;font-family:monospace;text-align:left">{tot_dif:,.2f}</td>
                    <td colspan="2"></td>
                </tr></tfoot>
            </table></div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.download_button("تحميل التقرير المدمج",
                data=merged.to_csv(index=False, encoding="utf-8-sig"),
                file_name="ربط_الاذونات_بالقيود.csv", mime="text/csv")

        elif view_lnk2 == "اذن محدد":
            all_docs = sorted(common_docs)
            sel_doc = st.selectbox("اختر رقم الإذن", ["— اختر —"] + all_docs, key="lnk2_doc")
            if sel_doc != "— اختر —":
                # حركات المخزن
                stk_rows = df_stk_lnk[df_stk_lnk["doc_no"]==sel_doc]
                # قيود الأستاذ
                j_rows   = matched_j[matched_j["extracted_doc_no"]==sel_doc]

                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown(f'<div class="ledger-header"><div style="font-weight:900;color:#1e2a4a">حركات المخزن — إذن {sel_doc}</div></div>', unsafe_allow_html=True)
                    st.dataframe(stk_rows[["doc_date","movement_type","warehouse","product_name","qty","unit_price","total"]].rename(columns={"doc_date":"التاريخ","movement_type":"النوع","warehouse":"المخزن","product_name":"المنتج","qty":"الكمية","unit_price":"السعر","total":"الإجمالي"}),
                        use_container_width=True, hide_index=True)
                    tot_stk_doc = stk_rows["total"].sum()
                    st.markdown(f'<div class="success-box">إجمالي قيمة المخزن: <b>{tot_stk_doc:,.2f}</b></div>', unsafe_allow_html=True)

                with col_b:
                    st.markdown(f'<div class="ledger-header" style="border-right-color:#2f9e44"><div style="font-weight:900;color:#1e2a4a">القيود المحاسبية — إذن {sel_doc}</div></div>', unsafe_allow_html=True)
                    st.dataframe(j_rows[["entry_date","entry_no","account_name","description","debit","credit"]].rename(columns={"entry_date":"التاريخ","entry_no":"القيد","account_name":"الحساب","description":"الوصف","debit":"مدين","credit":"دائن"}),
                        use_container_width=True, hide_index=True)
                    tot_j_doc = j_rows["debit"].sum()
                    diff_doc  = tot_stk_doc - tot_j_doc
                    clr = "#2f9e44" if abs(diff_doc) < 0.01 else "#c92a2a"
                    st.markdown(f'<div style="background:#f0fdf4;border:1px solid #86efac;border-radius:8px;padding:.6rem 1rem;direction:rtl"><b style="color:#166534">إجمالي مدين القيود: {tot_j_doc:,.2f}</b><br><span style="color:{clr};font-weight:700">الفرق: {diff_doc:,.2f}</span></div>', unsafe_allow_html=True)

        elif view_lnk2 == "قيود بدون اذن":
            st.markdown('<div class="info-box">قيود مش عارف يستخرج منها رقم الإذن — ممكن تحتاج مراجعة</div>', unsafe_allow_html=True)
            st.dataframe(
                unmatched_j[["entry_date","entry_no","account_name","description","debit","credit"]].head(300),
                use_container_width=True, hide_index=True, height=500)
            st.download_button("تحميل", data=unmatched_j.to_csv(index=False, encoding="utf-8-sig"),
                file_name="قيود_بدون_اذن.csv", mime="text/csv")

        else:  # إذونات بدون قيود
            no_j_docs = stk_doc_nos - j_doc_nos
            st.markdown(f'<div class="warning-box">{len(no_j_docs)} إذن في المخزن مش موجود في قيود الأستاذ</div>', unsafe_allow_html=True)
            no_j_df = df_stk_lnk[df_stk_lnk["doc_no"].isin(no_j_docs)].groupby("doc_no").agg(
                التاريخ   = ("doc_date","first"),
                المنتجات  = ("product_name", lambda x: " | ".join(x.unique()[:3])),
                الكمية    = ("qty","sum"),
                القيمة    = ("total","sum"),
            ).reset_index().sort_values("القيمة", ascending=False)
            st.dataframe(no_j_df, use_container_width=True, hide_index=True, height=500)
            st.download_button("تحميل", data=no_j_df.to_csv(index=False, encoding="utf-8-sig"),
                file_name="اذونات_بدون_قيود.csv", mime="text/csv")

# ══════════════════════════════════════════════════════════
# 💸 صفحة المصروفات
# ══════════════════════════════════════════════════════════
elif page == "💸  المصروفات":
    st.markdown('<div class="page-header"><p class="ph-title">💸 المصروفات</p><p class="ph-sub">تسجيل مصروفات بسطور متعددة مع تحويلها لقيود محاسبية</p></div>', unsafe_allow_html=True)

    st.markdown("""<style>
    .exp-tbl{width:100%;border-collapse:collapse;direction:rtl;font-size:13.5px;margin-bottom:4px}
    .exp-tbl th{background:#1B3A6B;color:#fff;padding:8px 10px;text-align:right;font-weight:600;white-space:nowrap}
    .exp-tbl td{padding:6px 10px;border-bottom:1px solid #e4eaf5;text-align:right;vertical-align:middle}
    .exp-tbl tr:nth-child(even){background:#f8faff}
    .exp-tbl tr:hover{background:#eef3ff}
    .exp-tbl .num{font-family:monospace;font-weight:700}
    .exp-tbl tfoot td{background:#1B3A6B;color:#C9A227;font-weight:700;padding:8px 10px}
    div[data-testid="stHorizontalBlock"]{gap:4px!important}
    </style>""", unsafe_allow_html=True)

    conn_h = get_conn()
    df_tr  = pd.read_sql("SELECT code, name FROM chart_of_accounts WHERE is_leaf=1 AND company_id=%s AND (code LIKE '1201%%' OR code LIKE '1202%%' OR code LIKE '12048%%') ORDER BY code", conn_h, params=(co_id,))
    df_tax = pd.read_sql("SELECT code, name FROM chart_of_accounts WHERE is_leaf=1 AND company_id=%s AND code IN ('216002','216003','222001','222002','223001','223002') ORDER BY code", conn_h, params=(co_id,))
    df_all = pd.read_sql("SELECT code, name FROM chart_of_accounts WHERE is_leaf=1 AND company_id=%s ORDER BY code", conn_h, params=(co_id,))
    conn_h.close()

    tr_opts  = [r['code'] + " - " + r['name'] for _, r in df_tr.iterrows()]
    tax_opts = [r['code'] + " - " + r['name'] for _, r in df_tax.iterrows()]
    all_opts = ["اختر حساب..."] + [r['code'] + " - " + r['name'] for _, r in df_all.iterrows()]
    CATS_E   = ["انتقالات","مواصلات","ضيافة","مستلزمات مكتبية","صيانة","إيجارات",
                "فواتير خدمات","مصروفات موقع","رواتب ومكافآت","مواد ومستلزمات","أخرى"]

    def get_next_exp_no():
        from datetime import date
        today = date.today().strftime("%Y-%m-%d")
        c = get_conn(); cur = c.cursor()
        cur.execute("SELECT COUNT(*) FROM expenses WHERE doc_date=%s AND company_id=%s", (today, co_id))
        n = cur.fetchone()[0]; c.close()
        return "EXP-" + date.today().strftime('%Y-%m-%d') + "-" + str(n+1).zfill(3)

    def to_je(d):
        import json as _j
        if d is None: return None
        try: return _j.dumps({str(k):str(v) for k,v in d.items()}, ensure_ascii=False)
        except: return _j.dumps({"data":str(d)}, ensure_ascii=False)

    def log_exp(tbl, act, rid, old, new, note):
        c = get_conn()
        c.execute("INSERT INTO audit_log (table_name,action,record_id,old_data,new_data,done_by,note) VALUES (%s,%s,%s,%s,%s,%s,%s)",
            (tbl,act,rid,to_je(old),to_je(new),st.session_state.get("user","unknown"),note))
        c.commit(); c.close()

    tab1, tab2, tab3, tab4 = st.tabs(["➕ إضافة مصروف", "📋 عرض وتعديل", "🗑️ سجل التدقيق", "🔴 المحذوفات"])

    with tab1:
        # ── رأس المستند ──
        st.markdown("#### 📄 بيانات المستند")
        hc1, hc2, hc3 = st.columns(3)
        with hc1:
            doc_no_e   = st.text_input("رقم السند", value=get_next_exp_no(), disabled=True)
            doc_date_e = st.date_input("التاريخ")
            inv_no_e   = st.text_input("رقم الفاتورة", placeholder="اختياري")
        with hc2:
            gen_desc_e = st.text_area("البيان العام *", height=100, placeholder="وصف عام للمصروف...")
            supplier_e = st.text_input("المورد / الجهة")
        with hc3:
            treasury_e = st.selectbox("الخزينة *", tr_opts if tr_opts else ["أضف خزينة من دليل الحسابات"])
            use_vat_e  = st.checkbox("تفعيل ضريبة على كل السطور")
            vat_acc_e  = None; vat_pct_e = 0.0
            if use_vat_e:
                vat_acc_e = st.selectbox("حساب الضريبة", tax_opts if tax_opts else ["216003 - ض.ق.م مدفوعة"], key="vat_ae")
                vat_pct_e = st.number_input("نسبة %", 0.0, 100.0, 14.0, format="%.1f", key="vat_pe")

        st.divider()
        st.markdown("#### 📝 سطور المصروفات")

        if "exp_lines_main" not in st.session_state:
            st.session_state.exp_lines_main = [{"acc":"","cat":CATS_E[0],"desc":"","amount":0.0,"tax_pct":0.0,"cc":"","notes":""}]

        lines   = st.session_state.exp_lines_main
        del_idx = None

        # ── السطور المتراصة ──
        # حسابات التكلفة التي تستلزم مركز تكلفة إجباري
        CC_REQUIRED_PREFIXES = ("54","67","68","69","70","71","72","73","74","75","76","77","78")

        for i, ln in enumerate(lines):
            lv = "collapsed" if i > 0 else "visible"
            # نقرأ القيمة الحالية من session state مباشرة عشان need_cc يكون فوري
            current_acc_key = f"ea_{i}"
            if current_acc_key in st.session_state:
                current_acc_val = str(st.session_state[current_acc_key] or "").split(" - ")[0]
            else:
                current_acc_val = str(ln.get("acc","") or "").split(" - ")[0]
            need_cc = current_acc_val.startswith(CC_REQUIRED_PREFIXES) and len(current_acc_val) > 2

            if need_cc:
                c1, c2, c3, c4, c5, c6 = st.columns([3, 2, 4, 2, 2, 0.5])
            else:
                c1, c2, c3, c4, c5, c6 = st.columns([3, 2, 5, 2, 0.1, 0.5])

            with c1:
                acc = st.selectbox("الحساب الفرعي *", all_opts, key=f"ea_{i}",
                    index=all_opts.index(ln["acc"]) if ln["acc"] in all_opts else 0,
                    label_visibility=lv)
                st.session_state.exp_lines_main[i]["acc"] = acc

            with c2:
                cat = st.selectbox("التصنيف *", CATS_E, key=f"ec_{i}",
                    index=CATS_E.index(ln["cat"]) if ln["cat"] in CATS_E else 0,
                    label_visibility=lv)
                st.session_state.exp_lines_main[i]["cat"] = cat

            with c3:
                desc = st.text_input("الوصف *", value=str(ln.get("desc","") or ""),
                    key=f"ea_desc_{i}", label_visibility=lv, placeholder="وصف السطر...")
                st.session_state.exp_lines_main[i]["desc"] = desc

            with c4:
                if need_cc:
                    amt = st.number_input("المبلغ *", min_value=1.0, value=max(1.0, float(ln["amount"])), format="%.2f",
                        key=f"ea_amt_{i}", label_visibility=lv)
                else:
                    amt = st.number_input("المبلغ *", min_value=1.0, value=max(1.0, float(ln["amount"])), format="%.2f",
                        key=f"ea_amt_{i}", label_visibility=lv)
                st.session_state.exp_lines_main[i]["amount"] = amt

            with c5:
                if need_cc:
                    cc = st.text_input("مركز التكلفة *", value=str(ln.get("cc","") or ""),
                        key=f"ea_cc_{i}", label_visibility=lv, placeholder="اسم المشروع...")
                    st.session_state.exp_lines_main[i]["cc"] = cc
                    if not cc:
                        st.caption("⚠️ مطلوب")
                else:
                    st.empty()

            with c6:
                if i == 0: st.write("")
                if st.button("➖", key=f"del_{i}", help="حذف السطر"):
                    del_idx = i

        if del_idx is not None:
            st.session_state.exp_lines_main.pop(del_idx); st.rerun()

        if st.button("➕ إضافة سطر", use_container_width=True, type="secondary"):
            st.session_state.exp_lines_main.append({"acc":"","cat":CATS_E[0],"desc":"","amount":0.0,"tax_pct":0.0,"cc":"","notes":""})
            st.rerun()

        # ── الإجمالي ──
        total_a = sum(float(l["amount"]) for l in lines)
        total_t = sum(round(float(l["amount"]) * (vat_pct_e if use_vat_e else float(l.get("tax_pct",0))) / 100, 2) for l in lines)
        total_n = round(total_a + total_t, 2)

        st.divider()
        mc1, mc2, mc3, mc4 = st.columns(4)
        with mc1: st.metric("عدد السطور", len([l for l in lines if float(l["amount"]) > 0]))
        with mc2: st.metric("إجمالي المبالغ", f"{total_a:,.2f}")
        with mc3: st.metric("إجمالي الضرائب", f"{total_t:,.2f}")
        with mc4: st.metric("🔴 الصافي للخزينة", f"{total_n:,.2f}")

        sc1, sc2 = st.columns([1,3])
        with sc1:
            if st.button("🔄 مسح", use_container_width=True):
                st.session_state.exp_lines_main = [{"acc":"","cat":CATS_E[0],"desc":"","amount":0.0,"tax_pct":0.0,"cc":"","notes":""}]
                st.rerun()
        with sc2:
            save_btn = st.button("💾 حفظ المصروف وتحويله لقيد", type="primary", use_container_width=True, key="save_exp_main")

        if save_btn:
            valid = [l for l in lines if float(l["amount"]) > 0 and l["acc"] and l["acc"] != "اختر حساب..."]
            errs = []
            if not gen_desc_e.strip(): errs.append("البيان العام مطلوب")
            if not tr_opts:            errs.append("لا توجد خزائن")
            if not valid:              errs.append("لا توجد سطور بمبالغ وحسابات")
            CC_REQ = ("54","67","68","69","70","71","72","73","74","75","76","77","78")
            for idx2, l in enumerate(valid):
                if not str(l.get("desc","")).strip(): errs.append(f"السطر {idx2+1}: الوصف مطلوب")
                ac2 = str(l.get("acc","")).split(" - ")[0]
                if ac2.startswith(CC_REQ) and len(ac2) > 2 and not str(l.get("cc","")).strip():
                    errs.append(f"السطر {idx2+1}: مركز التكلفة مطلوب لهذا الحساب")

            if errs:
                for e in errs: st.error("❌ " + e)
            else:
                from datetime import date as _date
                tr_code = treasury_e.split(" - ")[0]
                tr_name = treasury_e.split(" - ", 1)[1] if " - " in treasury_e else treasury_e

                total_a2 = sum(float(l["amount"]) for l in valid)
                total_t2 = sum(round(float(l["amount"]) * (vat_pct_e if use_vat_e else float(l.get("tax_pct",0))) / 100, 2) for l in valid)
                total_n2 = round(total_a2 + total_t2, 2)

                conn_s = get_conn(); cur_s = conn_s.cursor()
                today_s = _date.today().strftime("%Y-%m-%d")
                cur_s.execute("SELECT COUNT(*) FROM journal_entries WHERE entry_date=%s AND company_id=%s", (today_s, co_id))
                jc = cur_s.fetchone()[0]
                entry_no_s = "JRN-" + _date.today().strftime('%Y-%m-%d') + "-" + str(jc+1).zfill(3)

                cur_s.execute("INSERT INTO journal_entries (entry_no,entry_date,description,source,company_id,account_code,account_name) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                    (entry_no_s, doc_date_e.strftime("%Y-%m-%d"), gen_desc_e, "expense", co_id, "", ""))
                conn_s.commit(); eid = cur_s.lastrowid

                jl = []
                for ln in valid:
                    ac  = ln["acc"].split(" - ")[0]
                    an  = ln["acc"].split(" - ", 1)[1] if " - " in ln["acc"] else ln["acc"]
                    amt = float(ln["amount"])
                    tp  = vat_pct_e if use_vat_e else float(ln.get("tax_pct", 0))
                    tv  = round(amt * tp / 100, 2)
                    net = round(amt + tv, 2)
                    dl  = str(ln.get("desc","")) or gen_desc_e
                    nl  = str(ln.get("notes",""))
                    cat = str(ln.get("cat","أخرى"))

                    cur_s.execute("INSERT INTO expenses (company_id,doc_no,doc_date,treasury,category,supplier,account_code,employee,notes,amount,tax,total) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        (co_id, doc_no_e, doc_date_e.strftime("%Y-%m-%d"), tr_name, cat, supplier_e, ac, "", nl, amt, tv, net))
                    conn_s.commit()

                    jl.append((eid, entry_no_s, ac, an, amt, 0, doc_no_e, dl, co_id))
                    if tv > 0:
                        tac = vat_acc_e.split(" - ")[0] if use_vat_e and vat_acc_e else "216003"
                        tan = vat_acc_e.split(" - ",1)[1] if use_vat_e and vat_acc_e and " - " in vat_acc_e else "ض.ق.م مدفوعة"
                        jl.append((eid, entry_no_s, tac, tan, tv, 0, doc_no_e, dl, co_id))

                jl.append((eid, entry_no_s, tr_code, tr_name, 0, total_n2, doc_no_e, gen_desc_e, co_id))
                cur_s.executemany("INSERT INTO journal_lines (entry_id,entry_no,account_code,account_name,debit,credit,doc_no,notes,company_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)", jl)
                conn_s.commit(); cur_s.close(); conn_s.close()

                log_exp("expenses","INSERT",0,None,{"doc_no":doc_no_e,"total":total_n2,"lines":len(valid)},"إضافة مصروف")
                st.success("✅ تم حفظ " + doc_no_e + " → القيد " + entry_no_s + " (" + str(len(valid)) + " سطور)")
                st.balloons()
                st.session_state.exp_lines_main = [{"acc":"","cat":CATS_E[0],"desc":"","amount":0.0,"tax_pct":0.0,"cc":"","notes":""}]
                st.rerun()

    with tab2:
        conn_ev = get_conn()
        df_exp = pd.read_sql("SELECT id, doc_no, doc_date, treasury, category, supplier, account_code, amount, tax, total, notes FROM expenses WHERE company_id=%s AND (is_deleted IS NULL OR is_deleted=0) ORDER BY doc_date DESC, id DESC", conn_ev, params=(co_id,))
        conn_ev.close()
        if df_exp.empty:
            st.info("لا توجد مصروفات بعد")
        else:
            fc1, fc2, fc3 = st.columns(3)
            with fc1: srch_m = st.text_input("🔍 بحث")
            with fc2: cat_m  = st.selectbox("التصنيف", ["الكل"]+CATS_E, key="exp_cat_m")
            with fc3: st.metric("الإجمالي", f"{df_exp['total'].sum():,.2f} ج.م")
            if srch_m: df_exp = df_exp[df_exp.apply(lambda r: srch_m.lower() in str(r).lower(), axis=1)]
            if cat_m != "الكل": df_exp = df_exp[df_exp['category']==cat_m]
            st.dataframe(df_exp, use_container_width=True, hide_index=True,
                column_config={
                    "id":st.column_config.NumberColumn("ID",width="small"),
                    "doc_no":"رقم السند","doc_date":"التاريخ","treasury":"الخزينة",
                    "category":"التصنيف","supplier":"المورد","account_code":"الحساب",
                    "amount":st.column_config.NumberColumn("المبلغ",format="%.2f"),
                    "tax":st.column_config.NumberColumn("الضريبة",format="%.2f"),
                    "total":st.column_config.NumberColumn("الإجمالي",format="%.2f"),
                    "notes":"ملاحظات"})
            if is_admin:
                st.divider()
                sel_m = st.number_input("ID للتعديل/الحذف", min_value=1, step=1, key="exp_sel_m")
                conn_sm = get_conn()
                df_sm = pd.read_sql("SELECT * FROM expenses WHERE id=%s AND company_id=%s", conn_sm, params=(sel_m, co_id))
                conn_sm.close()
                if not df_sm.empty:
                    rm = df_sm.iloc[0]
                    st.info("✅ " + str(rm['doc_no']) + " | " + str(rm['supplier'] or '') + " | " + f"{float(rm['total']):,.2f} ج.م")
                    act_m = st.radio("العملية", ["تعديل","حذف"], horizontal=True, key="exp_act_m")
                    if act_m == "تعديل":
                        with st.form("edit_exp_m"):
                            em1, em2 = st.columns(2)
                            with em1:
                                nsu = st.text_input("المورد", value=str(rm['supplier'] or ''))
                                nam = st.number_input("المبلغ", value=float(rm['amount']), format="%.2f")
                                ntr = st.selectbox("الخزينة", tr_opts, index=next((i for i,x in enumerate(tr_opts) if str(rm.get('treasury','')) in x),0) if tr_opts else 0)
                            with em2:
                                nca = st.selectbox("التصنيف", CATS_E, index=CATS_E.index(rm['category']) if rm['category'] in CATS_E else 0)
                                nno = st.text_input("ملاحظات", value=str(rm['notes'] or ''))
                                nre = st.text_input("سبب التعديل *")
                            if st.form_submit_button("💾 حفظ", type="primary"):
                                if not nre: st.error("❌ السبب مطلوب!")
                                else:
                                    log_exp("expenses","UPDATE",sel_m,dict(rm),{"amount":nam},nre)
                                    ce = get_conn()
                                    ce.execute("UPDATE expenses SET supplier=%s,amount=%s,treasury=%s,category=%s,notes=%s WHERE id=%s AND company_id=%s",
                                        (nsu,nam,ntr.split(" - ",1)[1] if " - " in ntr else ntr,nca,nno,sel_m,co_id))
                                    ce.commit(); ce.close()
                                    st.success("✅ تم!"); st.rerun()
                    else:
                        dr_m = st.text_input("سبب الحذف *", key="exp_del_m")
                        if st.button("🗑️ تأكيد الحذف", type="primary", key="exp_delb_m"):
                            if not dr_m: st.error("❌ السبب مطلوب!")
                            else:
                                old_data = dict(df_sm.iloc[0])
                                log_exp("expenses","DELETE",sel_m,old_data,None,dr_m)
                                cd = get_conn()
                                # Soft Delete — مش بنمسح بنحط علامة
                                cd.execute("UPDATE expenses SET is_deleted=1, delete_reason=%s, deleted_by=%s, deleted_at=NOW() WHERE id=%s AND company_id=%s",
                                    (dr_m, st.session_state.get("user","unknown"), sel_m, co_id))
                                # كمان نحط علامة على القيد المرتبط
                                entry_no_del = str(old_data.get("doc_no",""))
                                cd.execute("UPDATE journal_entries SET is_deleted=1 WHERE entry_no LIKE %s AND company_id=%s",
                                    (f'%{entry_no_del}%', co_id))
                                cd.execute("UPDATE journal_lines SET is_deleted=1 WHERE doc_no=%s AND company_id=%s",
                                    (entry_no_del, co_id))
                                cd.commit(); cd.close()
                                st.success("✅ تم الحذف — القيد محفوظ في السجل"); st.rerun()
            else:
                st.warning("⚠️ التعديل والحذف للمدير فقط")

    with tab3:
        if is_admin:
            ca_m = get_conn()
            da_m = pd.read_sql("SELECT done_at, action, record_id, done_by, note FROM audit_log WHERE table_name='expenses' ORDER BY done_at DESC LIMIT 100", ca_m)
            ca_m.close()
            st.dataframe(da_m, use_container_width=True, hide_index=True) if not da_m.empty else st.info("لا يوجد سجل بعد")
        else:
            st.warning("⚠️ للمدير فقط")

    with tab4:
        if is_admin:
            conn_del = get_conn()
            df_del = pd.read_sql("""
                SELECT id, doc_no, doc_date, treasury, category, supplier,
                       account_code, amount, tax, total, delete_reason, deleted_by, deleted_at
                FROM expenses
                WHERE company_id=%s AND is_deleted=1
                ORDER BY deleted_at DESC
            """, conn_del, params=(co_id,))
            conn_del.close()

            if df_del.empty:
                st.info("لا توجد مصروفات محذوفة")
            else:
                st.metric("عدد المحذوفات", len(df_del))
                st.dataframe(df_del, use_container_width=True, hide_index=True,
                    column_config={
                        "id": st.column_config.NumberColumn("ID", width="small"),
                        "doc_no": "رقم السند",
                        "doc_date": "التاريخ",
                        "treasury": "الخزينة",
                        "category": "التصنيف",
                        "supplier": "المورد",
                        "account_code": "الحساب",
                        "amount": st.column_config.NumberColumn("المبلغ", format="%.2f"),
                        "tax": st.column_config.NumberColumn("الضريبة", format="%.2f"),
                        "total": st.column_config.NumberColumn("الإجمالي", format="%.2f"),
                        "delete_reason": "سبب الحذف",
                        "deleted_by": "حذف بواسطة",
                        "deleted_at": "وقت الحذف",
                    })

                st.divider()
                st.markdown("##### 🔄 استرجاع مصروف محذوف")
                restore_id = st.number_input("ID المصروف للاسترجاع", min_value=1, step=1, key="restore_id")
                if st.button("🔄 استرجاع", type="secondary", key="restore_btn"):
                    conn_r = get_conn()
                    conn_r.execute("UPDATE expenses SET is_deleted=0, delete_reason=NULL, deleted_by=NULL, deleted_at=NULL WHERE id=%s AND company_id=%s",
                        (restore_id, co_id))
                    conn_r.commit(); conn_r.close()
                    st.success("✅ تم الاسترجاع!"); st.rerun()
        else:
            st.warning("⚠️ للمدير فقط")



# ══════════════════════════════════════════════════════════
# 💰 صفحة سندات القبض
# ══════════════════════════════════════════════════════════
elif page == "💰  سندات القبض":
    st.markdown('<div class="page-header"><p class="ph-title">💰 سندات القبض</p><p class="ph-sub">تسجيل سندات القبض مع تحويلها لقيود محاسبية</p></div>', unsafe_allow_html=True)

    conn_rh = get_conn()
    df_tr_r = pd.read_sql("""SELECT code, name FROM chart_of_accounts WHERE is_leaf=1 AND company_id=%s
        AND (code LIKE '1201%%' OR code LIKE '1202%%' OR code LIKE '12048%%') ORDER BY code""",
        conn_rh, params=(co_id,))
    df_tax_r = pd.read_sql("""SELECT code, name FROM chart_of_accounts WHERE is_leaf=1 AND company_id=%s
        AND (code IN ('216002','216003','222001','222002','223001','223002') OR level3 LIKE '%%ضريب%%') ORDER BY code""",
        conn_rh, params=(co_id,))
    df_all_r = pd.read_sql("SELECT code, name FROM chart_of_accounts WHERE is_leaf=1 AND company_id=%s ORDER BY code", conn_rh, params=(co_id,))
    conn_rh.close()

    tr_opts_r   = [f"{r['code']} - {r['name']}" for _, r in df_tr_r.iterrows()]
    tax_opts_r  = [f"{r['code']} - {r['name']}" for _, r in df_tax_r.iterrows()]
    all_opts_r  = ["اختر حساب..."] + [f"{r['code']} - {r['name']}" for _, r in df_all_r.iterrows()]
    CATS_R = ["إيرادات مشاريع","دفعات عملاء","تحصيل ديون","مستخلصات","إيرادات أخرى"]
    PAY_METHODS = ["كاش","شيك","تحويل بنكي","بطاقة"]

    def get_next_rec():
        from datetime import date
        today = date.today().strftime("%Y-%m-%d")
        c = get_conn(); cur = c.cursor()
        cur.execute("SELECT COUNT(*) FROM receipts WHERE doc_date=%s AND company_id=%s", (today, co_id))
        n = cur.fetchone()[0]; c.close()
        return f"REC-{date.today().strftime('%Y-%m-%d')}-{str(n+1).zfill(3)}"

    def to_json_r(d):
        import json as _j
        if d is None: return None
        try: return _j.dumps({str(k): str(v) for k,v in d.items()}, ensure_ascii=False)
        except: return _j.dumps({"data": str(d)}, ensure_ascii=False)

    tab_r1, tab_r2, tab_r3 = st.tabs(["➕ إضافة سند قبض", "📋 عرض وتعديل", "🗑️ سجل التدقيق"])

    with tab_r1:
        st.markdown("#### 📄 بيانات السند")
        rh1, rh2, rh3 = st.columns(3)
        with rh1: doc_no_r = st.text_input("رقم السند", value=get_next_rec(), disabled=True)
        with rh2: doc_date_r = st.date_input("التاريخ", key="rec_date")
        with rh3: ref_r = st.text_input("رقم المرجع / الشيك", placeholder="اختياري")

        rh4, rh5 = st.columns([2,1])
        with rh4: desc_r = st.text_area("البيان *", height=80, placeholder="وصف سند القبض...")
        with rh5:
            client_r = st.text_input("العميل / الجهة")
            treasury_r = st.selectbox("الخزينة المستلِمة *", tr_opts_r) if tr_opts_r else None
            pay_r = st.selectbox("طريقة الدفع", PAY_METHODS)

        st.divider()
        st.markdown("#### 📝 سطور القبض")

        if "rec_lines" not in st.session_state:
            st.session_state.rec_lines = [{"acc":"","cat":"","desc":"","amount":0.0,"use_tax":False,"tax_acc":"","tax_pct":14.0,"wht_pct":0.0}]

        del_rec = []
        r_total = r_tax = r_net = 0.0

        for i, ln in enumerate(st.session_state.rec_lines):
            st.markdown(f"**السطر {i+1}**")
            rl1, rl2, rl3 = st.columns([3,2,1])
            with rl1:
                acc_r = st.selectbox("الحساب *", all_opts_r, key=f"rec_acc_{i}",
                    index=all_opts_r.index(ln["acc"]) if ln["acc"] in all_opts_r else 0)
                if acc_r == "اختر حساب...":
                    if st.button("➕ إضافة حساب", key=f"add_racc_{i}", type="secondary"):
                        st.info("💡 روح لـ 📋 دليل الحسابات")
                st.session_state.rec_lines[i]["acc"] = acc_r
            with rl2:
                cat_r = st.selectbox("التصنيف *", CATS_R, key=f"rec_cat_{i}",
                    index=CATS_R.index(ln["cat"]) if ln.get("cat") in CATS_R else 0)
                st.session_state.rec_lines[i]["cat"] = cat_r
            with rl3:
                amt_r = st.number_input("المبلغ *", min_value=0.0, value=float(ln.get("amount",0)), format="%.2f", key=f"rec_amt_{i}")
                st.session_state.rec_lines[i]["amount"] = amt_r
                use_tax_r = st.checkbox("ضريبة؟", value=ln.get("use_tax",False), key=f"rec_tax_chk_{i}")
                st.session_state.rec_lines[i]["use_tax"] = use_tax_r

            if use_tax_r:
                rt1, rt2, rt3 = st.columns(3)
                with rt1:
                    tax_acc_r = st.selectbox("حساب الضريبة", tax_opts_r, key=f"rec_tax_acc_{i}",
                        index=tax_opts_r.index(ln.get("tax_acc","")) if ln.get("tax_acc") in tax_opts_r else 0)
                    st.session_state.rec_lines[i]["tax_acc"] = tax_acc_r
                with rt2:
                    tax_p_r = st.number_input("ض.ق.م %", min_value=0.0, max_value=100.0, value=float(ln.get("tax_pct",14.0)), format="%.1f", key=f"rec_tp_{i}")
                    st.session_state.rec_lines[i]["tax_pct"] = tax_p_r
                with rt3:
                    wht_p_r = st.number_input("خصم %", min_value=0.0, max_value=100.0, value=float(ln.get("wht_pct",0.0)), format="%.1f", key=f"rec_wp_{i}")
                    st.session_state.rec_lines[i]["wht_pct"] = wht_p_r
            else:
                tax_p_r = wht_p_r = 0.0

            tv_r = round(amt_r * tax_p_r / 100, 2)
            wv_r = round(amt_r * wht_p_r / 100, 2)
            net_ln_r = round(amt_r - tv_r + wv_r, 2)
            r_total += amt_r; r_tax += tv_r; r_net += net_ln_r

            cd1, cd2 = st.columns([1,4])
            with cd2:
                if amt_r > 0: st.caption(f"💰 المبلغ: {amt_r:,.2f} | ضريبة: {tv_r:,.2f} | الصافي: {net_ln_r:,.2f}")
            with cd1:
                if len(st.session_state.rec_lines) > 1:
                    if st.button("🗑️", key=f"del_rl_{i}"): del_rec.append(i)
            st.divider()

        for idx in sorted(del_rec, reverse=True): st.session_state.rec_lines.pop(idx)
        if del_rec: st.rerun()

        if st.button("➕ إضافة سطر", type="secondary", use_container_width=True, key="add_rec_line"):
            st.session_state.rec_lines.append({"acc":"","cat":"","desc":"","amount":0.0,"use_tax":False,"tax_acc":"","tax_pct":14.0,"wht_pct":0.0})
            st.rerun()

        st.markdown("---")
        rc1, rc2, rc3 = st.columns(3)
        with rc1: st.metric("إجمالي المبالغ", f"{r_total:,.2f}")
        with rc2: st.metric("إجمالي الضرائب", f"{r_tax:,.2f}")
        with rc3: st.metric("الصافي", f"{r_net:,.2f}")

        if st.button("💾 حفظ سند القبض وتحويله لقيد", type="primary", use_container_width=True, key="save_rec"):
            errs = []
            if not desc_r: errs.append("البيان مطلوب")
            if not treasury_r: errs.append("الخزينة مطلوبة")
            if r_total <= 0: errs.append("المبلغ الإجمالي يجب أن يكون أكبر من صفر")
            for i, ln in enumerate(st.session_state.rec_lines):
                if not ln["acc"] or ln["acc"] == "اختر حساب...": errs.append(f"السطر {i+1}: الحساب مطلوب")
                if ln["amount"] <= 0: errs.append(f"السطر {i+1}: المبلغ مطلوب")

            if errs:
                for e in errs: st.error(f"❌ {e}")
            else:
                from datetime import date as _date
                tr_code_r = treasury_r.split(" - ")[0]
                tr_name_r = treasury_r.split(" - ", 1)[1] if " - " in treasury_r else treasury_r

                conn_rs = get_conn(); cur_rs = conn_rs.cursor()
                today = _date.today().strftime("%Y-%m-%d")
                cur_rs.execute("SELECT COUNT(*) FROM journal_entries WHERE entry_date=%s AND company_id=%s", (today, co_id))
                jc = cur_rs.fetchone()[0]
                entry_no_r = f"JRN-{_date.today().strftime('%Y-%m-%d')}-{str(jc+1).zfill(3)}"

                cur_rs.execute("INSERT INTO journal_entries (entry_no,entry_date,description,source,company_id,account_code,account_name) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                    (entry_no_r, doc_date_r.strftime("%Y-%m-%d"), desc_r, "receipt", co_id, "", ""))
                conn_rs.commit(); eid_r = cur_rs.lastrowid

                jl_r = [(eid_r, entry_no_r, tr_code_r, tr_name_r, r_net, 0, doc_no_r, desc_r, co_id)]

                for ln in st.session_state.rec_lines:
                    ac = ln["acc"].split(" - ")[0]
                    an = ln["acc"].split(" - ", 1)[1] if " - " in ln["acc"] else ln["acc"]
                    amt = float(ln["amount"])
                    tp = float(ln.get("tax_pct",0)) if ln.get("use_tax") else 0
                    wp = float(ln.get("wht_pct",0)) if ln.get("use_tax") else 0
                    tv = round(amt * tp / 100, 2); wv = round(amt * wp / 100, 2)

                    cur_rs.execute("INSERT INTO receipts (company_id,doc_no,doc_date,treasury,category,client,account_code,employee,notes,amount) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        (co_id, doc_no_r, doc_date_r.strftime("%Y-%m-%d"), tr_name_r, ln["cat"], client_r, ac, "", ln.get("desc",""), amt))
                    conn_rs.commit()

                    jl_r.append((eid_r, entry_no_r, ac, an, 0, amt, doc_no_r, desc_r, co_id))
                    if tv > 0 and ln.get("tax_acc"):
                        tac = ln["tax_acc"].split(" - ")[0]; tan = ln["tax_acc"].split(" - ",1)[1] if " - " in ln["tax_acc"] else ln["tax_acc"]
                        jl_r.append((eid_r, entry_no_r, tac, tan, 0, tv, doc_no_r, desc_r, co_id))
                    if wv > 0:
                        jl_r.append((eid_r, entry_no_r, "222001", "ضريبة خصم محصلة", wv, 0, doc_no_r, desc_r, co_id))

                cur_rs.executemany("INSERT INTO journal_lines (entry_id,entry_no,account_code,account_name,debit,credit,doc_no,notes,company_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)", jl_r)
                conn_rs.commit(); cur_rs.close(); conn_rs.close()

                st.success(f"✅ تم حفظ سند القبض {doc_no_r} والقيد {entry_no_r}")
                st.balloons()
                st.session_state.rec_lines = [{"acc":"","cat":"","desc":"","amount":0.0,"use_tax":False,"tax_acc":"","tax_pct":14.0,"wht_pct":0.0}]
                st.rerun()

    with tab_r2:
        conn_rv = get_conn()
        df_rec = pd.read_sql("SELECT id, doc_no, doc_date, treasury, category, client, account_code, amount, notes FROM receipts WHERE company_id=%s ORDER BY doc_date DESC, id DESC", conn_rv, params=(co_id,))
        conn_rv.close()

        if df_rec.empty:
            st.info("لا توجد سندات قبض بعد")
        else:
            rf1, rf2, rf3 = st.columns(3)
            with rf1: srch_r = st.text_input("🔍 بحث", key="rec_srch")
            with rf2: cat_fr = st.selectbox("التصنيف", ["الكل"] + CATS_R, key="rec_cat_f")
            with rf3: st.metric("الإجمالي", f"{df_rec['amount'].sum():,.2f} ج.م")

            if srch_r: df_rec = df_rec[df_rec.apply(lambda r: srch_r.lower() in str(r).lower(), axis=1)]
            if cat_fr != "الكل": df_rec = df_rec[df_rec['category'] == cat_fr]

            st.dataframe(df_rec, use_container_width=True, hide_index=True,
                column_config={"id": st.column_config.NumberColumn("ID", width="small"),
                    "doc_no": "رقم السند", "doc_date": "التاريخ", "treasury": "الخزينة",
                    "category": "التصنيف", "client": "العميل", "account_code": "الحساب",
                    "amount": st.column_config.NumberColumn("المبلغ", format="%.2f"), "notes": "ملاحظات"})

            if is_admin:
                st.divider()
                sel_r = st.number_input("ID السجل", min_value=1, step=1, key="rec_sel")
                conn_rs2 = get_conn()
                df_rs2 = pd.read_sql("SELECT * FROM receipts WHERE id=%s AND company_id=%s", conn_rs2, params=(sel_r, co_id))
                conn_rs2.close()
                if not df_rs2.empty:
                    rr = df_rs2.iloc[0]
                    st.info(f"✅ {rr['doc_no']} | {rr['client']} | {float(rr['amount']):,.2f} ج.م")
                    act_r = st.radio("العملية", ["تعديل", "حذف"], horizontal=True, key="rec_act")
                    if act_r == "تعديل":
                        with st.form("edit_rec"):
                            rrc1, rrc2 = st.columns(2)
                            with rrc1:
                                new_cl = st.text_input("العميل", value=str(rr['client'] or ''))
                                new_am = st.number_input("المبلغ", value=float(rr['amount']), format="%.2f")
                            with rrc2:
                                new_tr_r = st.selectbox("الخزينة", tr_opts_r, index=next((i for i,x in enumerate(tr_opts_r) if str(rr.get('treasury','')) in x), 0) if tr_opts_r else 0)
                                reason_r = st.text_input("سبب التعديل *")
                            if st.form_submit_button("💾 حفظ", type="primary"):
                                if not reason_r:
                                    st.error("❌ السبب مطلوب!")
                                else:
                                    conn_er2 = get_conn()
                                    conn_er2.execute("UPDATE receipts SET client=%s,amount=%s,treasury=%s WHERE id=%s AND company_id=%s",
                                        (new_cl, new_am, new_tr_r.split(" - ",1)[1] if " - " in new_tr_r else new_tr_r, sel_r, co_id))
                                    conn_er2.commit(); conn_er2.close()
                                    st.success("✅ تم!"); st.rerun()
                    else:
                        del_rr = st.text_input("سبب الحذف *", key="rec_del_r2")
                        if st.button("🗑️ تأكيد الحذف", type="primary", key="rec_del2"):
                            if not del_rr:
                                st.error("❌ السبب مطلوب!")
                            else:
                                conn_dr2 = get_conn()
                                conn_dr2.execute("DELETE FROM receipts WHERE id=%s AND company_id=%s", (sel_r, co_id))
                                conn_dr2.commit(); conn_dr2.close()
                                st.success("✅ تم الحذف!"); st.rerun()
            else:
                st.warning("⚠️ للمدير فقط")

    with tab_r3:
        if is_admin:
            conn_ra2 = get_conn()
            df_ra2 = pd.read_sql("SELECT done_at, action, record_id, done_by, note FROM audit_log WHERE table_name='receipts' ORDER BY done_at DESC LIMIT 100", conn_ra2)
            conn_ra2.close()
            st.dataframe(df_ra2, use_container_width=True, hide_index=True) if not df_ra2.empty else st.info("لا يوجد سجل بعد")
        else:
            st.warning("⚠️ للمدير فقط")

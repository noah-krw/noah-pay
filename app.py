# -*- coding: utf-8 -*-
import streamlit as st
import streamlit.components.v1 as components
import math, json, os, re, requests

# ============================================================
# 정산 매크로 v98.1 - [f-string 문법 오류 수정 완료]
# ============================================================

DB_FILE = "merchants_v96.json"

def get_bithumb_price():
    try:
        url = "https://api.bithumb.com/public/ticker/USDT_KRW"
        res = requests.get(url, timeout=3).json()
        if res['status'] == '0000':
            return int(float(res['data']['closing_price']))
    except:
        return 0
    return 0

def get_default_data():
    return {
        'my_wallet': 'TDaQt8oASZhVsuaEdpevqCacGKseGKCWhQ',
        'merchants': {
            'spfxm': {'wallet': 'TWbFbzW5GRkAkVrY4fLuXhNA576DCkoGbh', 'fee': '4', 'note': '메인 업체'}
        }
    }

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return get_default_data()

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def extract_int(text):
    if not text: return 0
    num_str = re.sub(r'[^0-9]', '', str(text))
    return int(num_str) if num_str else 0

def fmt(n): return f"{n:,}"

def editable_box(text, color_type="blue", box_id="default"):
    if not text: return 
    colors = {
        "blue":   {"border": "#4a90d9", "glow": "rgba(74,144,217,0.25)", "bg": "#07101e", "text": "#a8c7e8", "btn_bg": "#0d2040", "btn_hover": "#4a90d9"},
        "green":  {"border": "#2ecc71", "glow": "rgba(46,204,113,0.2)",  "bg": "#04120a", "text": "#7dcea0", "btn_bg": "#0a2016", "btn_hover": "#2ecc71"},
        "yellow": {"border": "#f39c12", "glow": "rgba(243,156,18,0.2)",  "bg": "#16100a", "text": "#f8c471", "btn_bg": "#241800", "btn_hover": "#f39c12"},
        "red":    {"border": "#e74c3c", "glow": "rgba(231,76,60,0.2)",   "bg": "#160608", "text": "#f1948a", "btn_bg": "#240808", "btn_hover": "#e74c3c"},
        "sky":    {"border": "#5dade2", "glow": "rgba(93,173,226,0.2)",  "bg": "#081622", "text": "#5dade2", "btn_bg": "#0c1e30", "btn_hover": "#5dade2"},
    }
    c = colors.get(color_type, colors["blue"])
    line_count = text.count("\n") + 1
    height = max(160, line_count * 26 + 90)

    # 파이썬 f-string 내의 자바스크립트 중괄호를 {{ }}로 이스케이프 처리함
    html_code = f"""
    <div style="margin-bottom:14px; position:relative;">
        <div style="
            border-left: 3px solid {c['border']};
            border-radius: 0 8px 8px 0;
            box-shadow: 0 0 18px {c['glow']}, inset 0 0 30px rgba(0,0,0,0.3);
            overflow: hidden;
            background: {c['bg']};
        ">
            <textarea id="copy_area_{box_id}" style="
                width: 100%;
                height: {height - 55}px;
                background: #ffffff;
                color: #1a1a1a;
                border: none;
                outline: none;
                font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
                font-size: 14px;
                line-height: 1.7;
                padding: 14px 16px;
                box-sizing: border-box;
                resize: none;
                cursor: text;
                letter-spacing: 0.02em;
            ">{text}</textarea>
            <div style="
                display: flex;
                align-items: center;
                justify-content: flex-end;
                gap: 10px;
                padding: 8px 12px 10px;
                border-top: 1px solid rgba(255,255,255,0.08);
                background: rgba(0,0,0,0.2);
            ">
                <span style="font-family:'Courier New',monospace;font-size:13px;font-weight:600;color:{c['text']};letter-spacing:0.05em;opacity:0.6;">✎ 직접 수정 가능</span>
                <button id="btn_{box_id}" onclick="copyText_{box_id}()" style="
                    display: flex;
                    align-items: center;
                    gap: 7px;
                    padding: 7px 18px;
                    background: {c['btn_bg']};
                    color: {c['text']};
                    border: 1px solid {c['border']};
                    border-radius: 6px;
                    cursor: pointer;
                    font-family: 'Courier New', monospace;
                    font-size: 13px;
                    font-weight: 600;
                    letter-spacing: 0.05em;
                    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
                    text-transform: uppercase;
                " 
                onmouseover="this.style.background='{c['btn_hover']}'; this.style.color='#000'; this.style.transform='translateY(-1px)'; this.style.boxShadow='0 4px 15px {c['glow']}';"
                onmouseout="this.style.background='{c['btn_bg']}'; this.style.color='{c['text']}'; this.style.transform='translateY(0)'; this.style.boxShadow='none';">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                        <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                    </svg>
                    COPY
                </button>
            </div>
        </div>
    </div>
    <script>
    function copyText_{box_id}() {{
        const textArea = document.getElementById('copy_area_{box_id}');
        const btn = document.getElementById('btn_{box_id}');
        textArea.select();
        textArea.setSelectionRange(0, 99999);
        try {{
            const success = document.execCommand('copy');
            if (success) {{
                btn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg> COPIED`;
                btn.style.background = '{c['border']}';
                btn.style.color = '#000';
                btn.style.borderColor = '{c['border']}';
                btn.style.transform = 'scale(1.03)';
                setTimeout(() => {{
                    btn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg> COPY`;
                    btn.style.background = '{c['btn_bg']}';
                    btn.style.color = '{c['text']}';
                    btn.style.borderColor = '{c['border']}';
                    btn.style.transform = 'scale(1)';
                }}, 1800);
            }}
        }} catch (err) {{ console.error('복사 실패:', err); }}
    }}
    </script>
    """
    components.html(html_code, height=height)

st.set_page_config(page_title="단계별 정산 시스템 v98.1", layout="centered")

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Noto+Sans+KR:wght@300;400;500;700&display=swap" rel="stylesheet">
<style>
    [data-testid="stAppViewContainer"] {
        background-color: #060c16 !important;
        background-image: 
            radial-gradient(ellipse at 20% 0%, rgba(30,60,100,0.35) 0%, transparent 60%),
            radial-gradient(ellipse at 80% 100%, rgba(20,80,60,0.2) 0%, transparent 60%);
        color: #c8d6e5 !important;
    }
    [data-testid="stHeader"] { background: transparent !important; }
    [data-testid="stSidebar"] {
        background: #080e1a !important;
        border-right: 1px solid rgba(74,144,217,0.15) !important;
    }
    [data-testid="stSidebar"] button {
        width: 100%;
        background: #0d1a2e !important;
        color: #7aa8cc !important;
        border: 1px solid rgba(74,144,217,0.25) !important;
        border-radius: 8px !important;
        font-family: 'Space Mono', monospace !important;
        font-size: 0.9em !important;
        font-weight: 600 !important;
        letter-spacing: 0.08em !important;
        padding: 11px 0 !important;
        transition: all 0.2s ease !important;
    }
    .main-title {
        font-family: 'Space Mono', monospace;
        color: #4a90d9;
        font-size: 1.6em;
        font-weight: 700;
        text-align: center;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        margin-bottom: 28px;
        padding: 18px 0 16px;
        border-bottom: 1px solid rgba(74,144,217,0.25);
    }
    .section-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-top: 32px;
        margin-bottom: 14px;
        padding: 10px 16px;
        background: rgba(255,255,255,0.02);
        border-radius: 8px;
        border-left: 3px solid var(--hdr-color, #4a90d9);
    }
    div[data-baseweb="input"] {
        background-color: #0b1525 !important;
        border-radius: 7px !important;
        border: 1px solid rgba(74,144,217,0.25) !important;
    }
    input {
        color: #dce8f5 !important;
        font-family: 'Space Mono', monospace !important;
        font-size: 1.1em !important;
    }
</style>
""", unsafe_allow_html=True)

def section_header(num, title, color="#4a90d9", rgb="74,144,217"):
    st.markdown(f"""
    <div class="section-header" style="--hdr-color:{color}; --hdr-rgb:{rgb};">
        <span style="font-family:'Space Mono',monospace; font-size:0.75em; font-weight:700; color:{color}; letter-spacing:0.1em; opacity:0.7;">{num}</span>
        <span style="font-family:'Noto Sans KR',sans-serif; font-size:0.92em; font-weight:700; color:#d0dff0; letter-spacing:0.08em; text-transform:uppercase;">{title}</span>
    </div>
    """, unsafe_allow_html=True)

if 'db' not in st.session_state: st.session_state.db = load_data()
if 'page' not in st.session_state: st.session_state.page = 'settle'

with st.sidebar:
    st.markdown("<div style='text-align:center; color:#4a90d9; font-weight:700; padding:20px 0;'>💹 SETTLEMENT</div>", unsafe_allow_html=True)
    if st.button("🚀  정산 작업"): st.session_state.page = 'settle'; st.rerun()
    if st.button("⚙️  머천트 관리"): st.session_state.page = 'admin'; st.rerun()
    st.divider()
    if st.button("⟳  NEW SESSION"):
        for k in ["s_b", "s_s", "s_amt", "bal_in", "w_in", "t_b", "t_u", "t_s"]: st.session_state[k] = ""
        st.rerun()

if st.session_state.page == 'settle':
    st.markdown('<div class="main-title">단계별 정산 시스템</div>', unsafe_allow_html=True)
    merchants = st.session_state.db['merchants']
    selected_m = st.selectbox("업체 선택", sorted(list(merchants.keys())))
    m_info = merchants[selected_m]

    section_header("01", "정산 환율", "#4a90d9", "74,144,217")
    col_price, col_btn = st.columns([3, 1])
    with col_btn:
        st.markdown("<div style='padding-top:28px;'></div>", unsafe_allow_html=True)
        if st.button("⚡ 시세호출"):
            st.session_state.s_b = str(get_bithumb_price())
            st.rerun()
    with col_price:
        sb_val = extract_int(st.text_input("빗썸 시세 (USDT_KRW)", key="s_b"))

    sel_p = st.radio("적용 배수", ["4%", "4.5%", "5%"], index=0, horizontal=True)
    m_map = {"4%": 1.04, "4.5%": 1.045, "5%": 1.05}
    ss_val = extract_int(st.text_input("수동 환율 (입력 시 시세 무시)", key="s_s"))
    s_rate = ss_val if ss_val > 0 else math.ceil(sb_val * m_map[sel_p])
    if s_rate > 0: editable_box(f"1usdt = {fmt(s_rate)} krw", "sky", "rate_01")

    section_header("02", "정산 멘트 생성")
    amt = extract_int(st.text_input("정산 금액 (KRW) 입력", key="s_amt"))
    if amt > 0 and s_rate > 0:
        u_val = round(amt / s_rate, 2)
        s_msg = (f"- {selected_m} settlement amount : {fmt(amt)} krw\n- exchange to usdt : {u_val:,.2f} usdt\n- 1usdt = {fmt(s_rate)} krw\n\n{m_info['wallet']}\n\nPlease confirm the address and calculation.\nOnce approved, we will proceed immediately")
        editable_box(s_msg, "blue", "res_02")

    section_header("03", "최종 잔액 보고")
    bal_in = extract_int(st.text_input("현재 잔액 입력 (KRW)", key="bal_in"))
    if bal_in > 0 and amt > 0:
        u_ceil = math.ceil(amt / s_rate)
        b_msg = (f"Balance & settlement update\n\n- {selected_m}\nsettlement amount : {fmt(amt)} krw\nexchange to usdt : {fmt(u_ceil)} usdt\n1usdt = {fmt(s_rate)} krw\n\n- {selected_m} : {fmt(bal_in)} krw")
        editable_box(b_msg, "green", "res_03")

    section_header("04", "마크업 수수료", "#f39c12")
    if amt > 0:
        m_fee = float(m_info.get('fee', 0.5))
        markup = math.ceil(amt * (m_fee / 100))
        editable_box(f"드래곤 테더정산 마크업 {m_fee}% {selected_m} / {fmt(amt)} / {fmt(markup)}", "yellow", "res_04")

    section_header("05", "정산(SETTLEMENT) 요청", "#e74c3c")
    w_bal = extract_int(st.text_input("하이 밸런스 경고용 잔액", key="w_in"))
    if w_bal > 0:
        st.markdown(f'<p style="color:#5dade2; font-family:Space Mono,monospace; margin-bottom:8px;">▸ 적용 환율 &nbsp; 1usdt = {fmt(s_rate)} krw</p>', unsafe_allow_html=True)
        w_msg = (f"Hello, Team\nCurrently, the balance of the merchants is too high.\nTo ensure a safe balance, please proceed with USDT settlement.\n\nBalance update\n- {selected_m} : {fmt(w_bal)} krw")
        editable_box(w_msg, "red", "res_05")

    st.divider()
    section_header("06", "TOP-UP 탑업", "#2ecc71")
    t1, t2 = st.columns(2)
    with t1: tb_val = extract_int(st.text_input("탑업 시세(빗썸)", key="t_b"))
    with t2: tu_amt = extract_int(st.text_input("수량(USDT)", key="t_u"))
    ts_val = extract_int(st.text_input("수동 환율 ", key="t_s"))
    t_rate = ts_val if ts_val > 0 else (tb_val - math.ceil(tb_val * 0.005) if tb_val > 0 else 0)
    if tu_amt > 0 and t_rate > 0:
        my_w = st.session_state.db.get('my_wallet', '')
        t_msg = (f"top-up\n\nmid : {selected_m}\ntop-up amount : {fmt(tu_amt)} usdt\nexchange to KRW : {fmt(tu_amt * t_rate)} krw\n1usdt = {fmt(t_rate)} krw\n\n{my_w}\n\nPlease check the invoice.")
        editable_box(t_msg, "green", "res_06_req")

elif st.session_state.page == 'admin':
    st.markdown('<div class="main-title">머천트 및 지갑 관리</div>', unsafe_allow_html=True)
    my_w = st.text_input("내 USDT 지갑 주소", value=st.session_state.db.get('my_wallet', ''))
    if st.button("저장"): st.session_state.db['my_wallet'] = my_w; save_data(st.session_state.db); st.toast("저장완료")
    with st.form("new_m"):
        n_name = st.text_input("업체명"); n_wallet = st.text_input("지갑주소"); n_fee = st.text_input("수수료", value="0.5")
        if st.form_submit_button("등록"):
            st.session_state.db['merchants'][n_name] = {"wallet": n_wallet, "fee": n_fee}
            save_data(st.session_state.db); st.rerun()
# -*- coding: utf-8 -*-
import streamlit as st
import streamlit.components.v1 as components
import math, json, os, re, requests, time, datetime

# ============================================================
# 정산 매크로 v98.7 - [v97.0 전체 기능 + 김프 자동화 통합]
# ============================================================

DB_FILE = "merchants_v96.json"

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

# 업비트 환율 + 빗썸 시세 데이터 가져오기
def fetch_market_data():
    res_data = {"usdt_krw": 0, "usd_krw": 0, "kp": 0.0}
    try:
        r1 = requests.get('https://api.bithumb.com/public/ticker/USDT_KRW', timeout=1.5)
        if r1.json().get('status') == '0000':
            res_data["usdt_krw"] = float(r1.json()['data']['closing_price'])
        
        r2 = requests.get('https://quotation-api-cdn.dunamu.com/v1/forex/recent?codes=FRX.KRWUSD', timeout=1.5)
        res_data["usd_krw"] = r2.json()[0]['basePrice']
        
        if res_data["usdt_krw"] > 0 and res_data["usd_krw"] > 0:
            res_data["kp"] = ((res_data["usdt_krw"] / res_data["usd_krw"]) - 1) * 100
    except: pass
    return res_data

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

    html_code = f"""
    <div style="margin-bottom:14px; position:relative;">
        <div style="border-left: 3px solid {c['border']}; border-radius: 0 8px 8px 0; box-shadow: 0 0 18px {c['glow']}, inset 0 0 30px rgba(0,0,0,0.3); overflow: hidden; background: {c['bg']};">
            <textarea id="copy_area_{box_id}" style="width: 100%; height: {height - 55}px; background: #ffffff; color: #1a1a1a; border: none; outline: none; font-family: 'JetBrains Mono', monospace; font-size: 14px; line-height: 1.7; padding: 14px 16px; box-sizing: border-box; resize: none; letter-spacing: 0.02em;">{text}</textarea>
            <div style="display: flex; align-items: center; justify-content: flex-end; gap: 10px; padding: 8px 12px 10px; border-top: 1px solid rgba(255,255,255,0.08); background: rgba(0,0,0,0.2);">
                <span style="font-family:'Courier New',monospace;font-size:13px;font-weight:600;color:{c['text']};opacity:0.6;">✎ 직접 수정 가능</span>
                <button id="btn_{box_id}" onclick="copyText_{box_id}()" style="display: flex; align-items: center; gap: 7px; padding: 7px 18px; background: {c['btn_bg']}; color: {c['text']}; border: 1px solid {c['border']}; border-radius: 6px; cursor: pointer; font-family: 'Courier New', monospace; font-size: 13px; font-weight: 600; transition: all 0.25s;">COPY</button>
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
            document.execCommand('copy');
            btn.innerHTML = 'COPIED';
            btn.style.background = '{c['border']}';
            btn.style.color = '#000';
            setTimeout(() => {{
                btn.innerHTML = 'COPY';
                btn.style.background = '{c['btn_bg']}';
                btn.style.color = '{c['text']}';
            }}, 1500);
        }} catch (err) {{}}
    }}
    </script>
    """
    components.html(html_code, height=height)

st.set_page_config(page_title="단계별 정산 시스템 v98.7", layout="centered")

# CSS 스타일 복구
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Noto+Sans+KR:wght@300;400;500;700&display=swap" rel="stylesheet">
<style>
    [data-testid="stAppViewContainer"] { background-color: #060c16 !important; background-image: radial-gradient(ellipse at 20% 0%, rgba(30,60,100,0.35) 0%, transparent 60%), radial-gradient(ellipse at 80% 100%, rgba(20,80,60,0.2) 0%, transparent 60%); color: #c8d6e5 !important; }
    [data-testid="stHeader"] { background: transparent !important; }
    [data-testid="stSidebar"] { background: #080e1a !important; border-right: 1px solid rgba(74,144,217,0.15) !important; }
    [data-testid="stSidebar"] button { width: 100%; background: #0d1a2e !important; color: #7aa8cc !important; border: 1px solid rgba(74,144,217,0.25) !important; border-radius: 8px !important; font-family: 'Space Mono', monospace !important; font-size: 0.9em !important; font-weight: 600 !important; letter-spacing: 0.08em !important; padding: 11px 0 !important; transition: all 0.2s ease !important; }
    [data-testid="stSidebar"] button:hover { background: #1a2e48 !important; border-color: #4a90d9 !important; color: #cde4f8 !important; }
    .main-title { font-family: 'Space Mono', monospace; color: #4a90d9; font-size: 1.6em; font-weight: 700; text-align: center; letter-spacing: 0.18em; text-transform: uppercase; margin-bottom: 28px; padding: 18px 0 16px; border-bottom: 1px solid rgba(74,144,217,0.25); position: relative; }
    .section-header { display: flex; align-items: center; gap: 12px; margin-top: 32px; margin-bottom: 14px; padding: 10px 16px; background: rgba(255,255,255,0.02); border-radius: 8px; border-left: 3px solid var(--hdr-color, #4a90d9); position: relative; overflow: hidden; }
    div[data-baseweb="input"] { background-color: #0b1525 !important; border-radius: 7px !important; border: 1px solid rgba(74,144,217,0.25) !important; }
    input { color: #dce8f5 !important; font-family: 'Space Mono', monospace !important; font-size: 1.1em !important; background: transparent !important; }
</style>
""", unsafe_allow_html=True)

def section_header(num, title, color="#4a90d9", rgb="74,144,217"):
    st.markdown(f"""
    <div class="section-header" style="--hdr-color:{color}; --hdr-rgb:{rgb};">
        <span style="font-family:'Space Mono',monospace; font-size:0.75em; font-weight:700; color:{color}; opacity:0.7;">{num}</span>
        <span style="font-family:'Noto Sans KR',sans-serif; font-size:0.92em; font-weight:700; color:#d0dff0;">{title}</span>
        <span style="flex:1; height:1px; background:linear-gradient(90deg, rgba({rgb},0.3) 0%, transparent 100%);"></span>
    </div>
    """, unsafe_allow_html=True)

if 'db' not in st.session_state: st.session_state.db = load_data()
if 'page' not in st.session_state: st.session_state.page = 'settle'

# 데이터 갱신 (30초)
now_ts = time.time()
if 'last_fetch' not in st.session_state or (now_ts - st.session_state.last_fetch) > 30:
    st.session_state.market = fetch_market_data()
    st.session_state.last_fetch = now_ts

with st.sidebar:
    st.markdown("<div style='color:#4a90d9; font-weight:700; text-align:center; padding-bottom:16px;'>💹 SETTLEMENT</div>", unsafe_allow_html=True)
    if st.button("🚀  정산 작업", use_container_width=True): st.session_state.page = 'settle'; st.rerun()
    if st.button("⚙️  머천트 관리", use_container_width=True): st.session_state.page = 'admin'; st.rerun()
    st.divider()
    reset_keys = ["s_b", "s_s", "s_amt", "bal_in", "w_in", "t_b", "t_u", "t_s"]
    if st.button("⟳  NEW SESSION", use_container_width=True):
        for k in reset_keys: st.session_state[k] = ""
        st.toast("초기화 완료"); st.rerun()

if st.session_state.page == 'settle':
    st.markdown('<div class="main-title">단계별 정산 시스템</div>', unsafe_allow_html=True)
    
    # ── 김프 전광판 ──────────────────
    m = st.session_state.market
    kp_color = "#e74c3c" if m['kp'] >= 2.0 else "#2ecc71"
    st.markdown(f"""
    <div style='padding:14px 22px; margin-bottom:14px; background:linear-gradient(135deg,#030f1c,#041810); border:1px solid rgba(93,173,226,0.3); border-radius:10px; display:flex; align-items:center; justify-content:space-between;'>
        <div><div style='font-size:0.65em; color:#5dade2;'>BITHUMB USDT</div><div style='font-size:1.8em; font-weight:700;'>&#8361; {fmt(int(m['usdt_krw']))}</div></div>
        <div style='text-align:right;'><div style='font-size:0.65em; color:{kp_color};'>KIMCHI PREMIUM</div><div style='font-size:1.8em; font-weight:700; color:{kp_color};'>{m['kp']:.2f}%</div></div>
    </div>
    """, unsafe_allow_html=True)

    merchants = st.session_state.db['merchants']
    selected_m = st.selectbox("업체 선택", sorted(list(merchants.keys())))
    m_info = merchants[selected_m]

    # 01~06 모든 섹션 복구
    section_header("01", "정산 환율")
    auto_idx = 0 if m['kp'] >= 2.0 else 1
    sel_p = st.radio("적용 배수", ["4%", "4.5%", "5%"], index=auto_idx, horizontal=True)
    m_map = {"4%": 1.04, "4.5%": 1.045, "5%": 1.05}
    c1, c2 = st.columns(2)
    with c1: sb_val = extract_int(st.text_input("빗썸 시세", value=str(int(m['usdt_krw'])), key="s_b"))
    with c2: ss_val = extract_int(st.text_input("수동 환율", key="s_s"))
    s_rate = ss_val if ss_val > 0 else math.ceil(sb_val * m_map[sel_p])
    if s_rate > 0: editable_box(f"1usdt = {fmt(s_rate)} krw", "sky", "rate_01")

    section_header("02", "정산 멘트 생성")
    amt = extract_int(st.text_input("정산 금액 (KRW) 입력", key="s_amt"))
    if amt > 0 and s_rate > 0:
        u_val = round(amt / s_rate, 2)
        s_msg = (f"- {selected_m} settlement amount : {fmt(amt)} krw\n- exchange to usdt : {u_val:,.2f} usdt\n- 1usdt = {fmt(s_rate)} krw\n\n{m_info['wallet']}\n\nPlease confirm.")
        editable_box(s_msg, "blue", "res_02")

    section_header("03", "최종 잔액 보고")
    bal_in = extract_int(st.text_input("현재 잔액 입력", key="bal_in"))
    if bal_in > 0 and amt > 0:
        b_msg = f"Balance update\n- {selected_m} settlement : {fmt(amt)} krw\n- {selected_m} balance : {fmt(bal_in)} krw"
        editable_box(b_msg, "green", "res_03")

    section_header("04", "마크업 수수료", "#f39c12", "243,156,18")
    if amt > 0:
        m_fee = float(m_info.get('fee', 0.5))
        markup = math.ceil(amt * (m_fee / 100))
        editable_box(f"마크업 {m_fee}% {selected_m} / {fmt(amt)} / {fmt(markup)}", "yellow", "res_04")

    section_header("05", "정산 (SETTLEMENT) 요청", "#e74c3c", "231,76,60")
    w_bal = extract_int(st.text_input("경고용 잔액", key="w_in"))
    if w_bal > 0:
        editable_box(f"Hello Team, balance is too high.\n- {selected_m} : {fmt(w_bal)} krw", "red", "res_05")

    st.divider()
    section_header("06", "TOP-UP 탑업", "#2ecc71", "46,204,113")
    t1, t2 = st.columns(2)
    with t1: tb_val = extract_int(st.text_input("탑업 시세", key="t_b"))
    with t2: tu_amt = extract_int(st.text_input("수량(USDT)", key="t_u"))
    t_rate = tb_val - math.ceil(tb_val * 0.005) if tb_val > 0 else 0
    if tu_amt > 0 and t_rate > 0:
        editable_box(f"top-up {selected_m}\n- amount : {fmt(tu_amt)} usdt\n- krw : {fmt(tu_amt * t_rate)} krw", "green", "res_06")

elif st.session_state.page == 'admin':
    st.markdown('<div class="main-title">머천트 및 지갑 관리</div>', unsafe_allow_html=True)
    # 관리자 기능 (업체 추가/수정/삭제) 전체 복구 완료
    my_w = st.text_input("내 지갑 주소", value=st.session_state.db.get('my_wallet', ''))
    if st.button("저장"): st.session_state.db['my_wallet'] = my_w; save_data(st.session_state.db); st.toast("저장됨")
    with st.form("new_m"):
        n_name = st.text_input("업체명"); n_wallet = st.text_input("지갑주소"); n_fee = st.text_input("수수료", value="0.5")
        if st.form_submit_button("등록"):
            st.session_state.db['merchants'][n_name] = {"wallet": n_wallet, "fee": n_fee}
            save_data(st.session_state.db); st.rerun()
    for name in sorted(st.session_state.db['merchants'].keys()):
        with st.expander(f"📦 {name} 관리"):
            info = st.session_state.db['merchants'][name]
            u_w = st.text_input("지갑", value=info['wallet'], key=f"w_{name}")
            u_f = st.text_input("수수료", value=info['fee'], key=f"f_{name}")
            if st.button("저장", key=f"s_{name}"):
                st.session_state.db['merchants'][name] = {"wallet": u_w, "fee": u_f}
                save_data(st.session_state.db); st.toast("수정됨")
            if st.button("삭제", key=f"d_{name}"): del st.session_state.db['merchants'][name]; save_data(st.session_state.db); st.rerun()
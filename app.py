# -*- coding: utf-8 -*-
import streamlit as st
import streamlit.components.v1 as components
import math, json, os, re, requests, time, datetime

# ============================================================
# 정산 매크로 v98.5 - [업비트 환율 API 연동 실시간 김프 계산]
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

# 데이터 가져오기 (빗썸 USDT + 업비트 환율)
def fetch_market_data():
    data = {"usdt_krw": 0, "usd_krw": 0, "kp": 0.0}
    try:
        # 1. 빗썸 USDT/KRW 시세
        r1 = requests.get('https://api.bithumb.com/public/ticker/USDT_KRW', timeout=2)
        if r1.json().get('status') == '0000':
            data["usdt_krw"] = float(r1.json()['data']['closing_price'])
        
        # 2. 업비트(두나무) 실시간 환율 (가장 빠름)
        r2 = requests.get('https://quotation-api-cdn.dunamu.com/v1/forex/recent?codes=FRX.KRWUSD', timeout=2)
        data["usd_krw"] = r2.json()[0]['basePrice']
        
        # 3. 김프 계산
        if data["usdt_krw"] > 0 and data["usd_krw"] > 0:
            data["kp"] = ((data["usdt_krw"] / data["usd_krw"]) - 1) * 100
    except: pass
    return data

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

st.set_page_config(page_title="단계별 정산 시스템 v98.5", layout="centered")

# 스타일 로드
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #060c16 !important; color: #c8d6e5 !important; }
    .main-title { font-family: 'Space Mono', monospace; color: #4a90d9; font-size: 1.6em; font-weight: 700; text-align: center; letter-spacing: 0.18em; text-transform: uppercase; margin-bottom: 28px; padding: 18px 0 16px; border-bottom: 1px solid rgba(74,144,217,0.25); }
    .section-header { display: flex; align-items: center; gap: 12px; margin-top: 32px; margin-bottom: 14px; padding: 10px 16px; background: rgba(255,255,255,0.02); border-radius: 8px; border-left: 3px solid #4a90d9; }
    div[data-baseweb="input"] { background-color: #0b1525 !important; border-radius: 7px !important; border: 1px solid rgba(74,144,217,0.25) !important; }
    input { color: #dce8f5 !important; font-family: 'Space Mono', monospace !important; }
</style>
""", unsafe_allow_html=True)

if 'db' not in st.session_state: st.session_state.db = load_data()
if 'page' not in st.session_state: st.session_state.page = 'settle'

# 데이터 갱신 로직 (30초)
now = time.time()
if 'last_fetch' not in st.session_state or (now - st.session_state.last_fetch) > 30:
    st.session_state.market = fetch_market_data()
    st.session_state.last_fetch = now

# 사이드바
with st.sidebar:
    st.markdown("<h3 style='text-align:center; color:#4a90d9;'>💹 SETTLEMENT</h3>", unsafe_allow_html=True)
    if st.button("🚀  정산 작업", use_container_width=True): st.session_state.page = 'settle'; st.rerun()
    if st.button("⚙️  머천트 관리", use_container_width=True): st.session_state.page = 'admin'; st.rerun()
    if st.button("⟳  NEW SESSION", use_container_width=True):
        for k in ["s_b", "s_s", "s_amt", "bal_in", "w_in", "t_b", "t_u", "t_s"]: st.session_state[k] = ""
        st.rerun()

if st.session_state.page == 'settle':
    st.markdown('<div class="main-title">단계별 정산 시스템</div>', unsafe_allow_html=True)
    
    # ── 전광판 (시세 + 김프) ──────────────────────────────────────────
    m = st.session_state.market
    kp_color = "#e74c3c" if m['kp'] >= 2.0 else "#2ecc71"
    
    html = f"""
    <div style='padding:14px 22px; margin-bottom:14px; background:linear-gradient(135deg,#030f1c,#041810); border:1px solid rgba(93,173,226,0.3); border-radius:10px; display:flex; align-items:center; justify-content:space-between;'>
        <div>
            <div style='font-family:Space Mono,monospace; font-size:0.65em; color:#5dade2; letter-spacing:0.1em;'>BITHUMB USDT</div>
            <div style='font-family:Space Mono,monospace; font-size:1.8em; font-weight:700; color:#ffffff;'>&#8361; {fmt(int(m['usdt_krw']))}</div>
        </div>
        <div style='text-align:right;'>
            <div style='font-family:Space Mono,monospace; font-size:0.65em; color:{kp_color}; letter-spacing:0.1em;'>KIMCHI PREMIUM</div>
            <div style='font-family:Space Mono,monospace; font-size:1.8em; font-weight:700; color:{kp_color};'>{m['kp']:.2f}%</div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

    merchants = st.session_state.db['merchants']
    selected_m = st.selectbox("업체 선택", sorted(list(merchants.keys())))
    m_info = merchants[selected_m]

    # 01. 환율 설정
    st.markdown('<div class="section-header">01. 정산 환율</div>', unsafe_allow_html=True)
    
    # 김프에 따른 배수 자동 추천 (2% 이상이면 4%, 미만이면 4.5% - 사용자 규칙 반영)
    auto_idx = 0 if m['kp'] >= 2.0 else 1
    sel_p = st.radio("적용 배수 (김프 기준 자동추천)", ["4%", "4.5%", "5%"], index=auto_idx, horizontal=True)
    m_map = {"4%": 1.04, "4.5%": 1.045, "5%": 1.05}

    c1, c2 = st.columns(2)
    with c1:
        # 실시간 시세 자동 입력
        sb_val = extract_int(st.text_input("빗썸 시세", value=str(int(m['usdt_krw'])), key="s_b"))
    with c2:
        ss_val = extract_int(st.text_input("수동 환율", key="s_s"))
    
    s_rate = ss_val if ss_val > 0 else math.ceil(sb_val * m_map[sel_p])
    if s_rate > 0: editable_box(f"1usdt = {fmt(s_rate)} krw", "sky", "rate_01")

    # 02. 정산 멘트
    st.markdown('<div class="section-header">02. 정산 멘트 생성</div>', unsafe_allow_html=True)
    amt = extract_int(st.text_input("정산 금액 (KRW) 입력", key="s_amt"))
    if amt > 0 and s_rate > 0:
        u_val = round(amt / s_rate, 2)
        s_msg = (f"- {selected_m} settlement amount : {fmt(amt)} krw\n- exchange to usdt : {u_val:,.2f} usdt\n- 1usdt = {fmt(s_rate)} krw\n\n{m_info['wallet']}\n\nPlease confirm calculations.")
        editable_box(s_msg, "blue", "res_02")

    # 자동 리프레시를 위한 빈 공간
    st.empty()
    time.sleep(0.1) # 루프 방지

elif st.session_state.page == 'admin':
    st.markdown('<div class="main-title">머천트 및 지갑 관리</div>', unsafe_allow_html=True)
    # 관리자 페이지 로직 유지 (생략)
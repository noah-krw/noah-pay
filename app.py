# -*- coding: utf-8 -*-
import streamlit as st
import streamlit.components.v1 as components
import math, json, os, re, requests, time

# ============================================================
# 정산 매크로 v97.0 - [디자인 개선: 헤더, 복사버튼, 텍스트박스, 입력필드]
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
        
        // 선택 및 복사
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
        }} catch (err) {{
            console.error('복사 실패:', err);
        }}
    }}
    </script>
    """
    components.html(html_code, height=height)


st.set_page_config(page_title="단계별 정산 시스템 v97", layout="centered")

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Noto+Sans+KR:wght@300;400;500;700&display=swap" rel="stylesheet">

<style>
    /* ── 전체 배경 ── */
    [data-testid="stAppViewContainer"] {
        background-color: #060c16 !important;
        background-image: 
            radial-gradient(ellipse at 20% 0%, rgba(30,60,100,0.35) 0%, transparent 60%),
            radial-gradient(ellipse at 80% 100%, rgba(20,80,60,0.2) 0%, transparent 60%);
        color: #c8d6e5 !important;
    }
    [data-testid="stHeader"] { background: transparent !important; }
    
    /* ── 사이드바 ── */
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
    [data-testid="stSidebar"] button:hover {
        background: #1a2e48 !important;
        border-color: #4a90d9 !important;
        color: #cde4f8 !important;
        box-shadow: 0 0 12px rgba(74,144,217,0.2) !important;
    }
    /* NEW SESSION 버튼 override */
    [data-testid="stSidebar"] button[data-testid="baseButton-secondary"]:nth-of-type(3) {
        background: linear-gradient(135deg, #0a2e1a, #0d2535) !important;
        color: #2ecc71 !important;
        border: 1.5px solid #2ecc71 !important;
        font-size: 1.0em !important;
        padding: 13px 0 !important;
        box-shadow: 0 0 14px rgba(46,204,113,0.15) !important;
        letter-spacing: 0.15em !important;
    }

    /* ── 메인 타이틀 ── */
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
        position: relative;
    }
    .main-title::after {
        content: '';
        display: block;
        width: 60px;
        height: 2px;
        background: linear-gradient(90deg, #4a90d9, transparent);
        margin: 10px auto 0;
    }

    /* ── 섹션 헤더 ── */
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
        position: relative;
        overflow: hidden;
    }
    .section-header::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: linear-gradient(90deg, rgba(var(--hdr-rgb, 74,144,217),0.08) 0%, transparent 100%);
        pointer-events: none;
    }
    .section-header .num {
        font-family: 'Space Mono', monospace;
        font-size: 0.75em;
        font-weight: 700;
        color: var(--hdr-color, #4a90d9);
        letter-spacing: 0.1em;
        opacity: 0.7;
        white-space: nowrap;
    }
    .section-header .title {
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 0.92em;
        font-weight: 700;
        color: #d0dff0;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }
    .section-header .line {
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, rgba(var(--hdr-rgb, 74,144,217),0.3) 0%, transparent 100%);
    }

    /* ── 입력 필드 ── */
    div[data-baseweb="input"] {
        background-color: #0b1525 !important;
        border-radius: 7px !important;
        border: 1px solid rgba(74,144,217,0.25) !important;
        transition: border-color 0.2s ease !important;
    }
    div[data-baseweb="input"]:focus-within {
        border-color: rgba(74,144,217,0.7) !important;
        box-shadow: 0 0 0 2px rgba(74,144,217,0.1) !important;
    }
    input {
        color: #dce8f5 !important;
        font-weight: 400 !important;
        font-family: 'Space Mono', monospace !important;
        font-size: 1.1em !important;
        background: transparent !important;
        caret-color: #4a90d9 !important;
    }
    /* 라벨 */
    label[data-testid="stWidgetLabel"] > div > p {
        color: #6a8aaa !important;
        font-size: 0.82em !important;
        font-family: 'Space Mono', monospace !important;
        letter-spacing: 0.06em !important;
        text-transform: uppercase !important;
    }
    /* 라디오 */
    [data-testid="stRadio"] label {
        font-family: 'Space Mono', monospace !important;
        font-size: 0.88em !important;
        color: #7aa8cc !important;
    }
    /* 셀렉트박스 */
    div[data-baseweb="select"] > div {
        background-color: #0b1525 !important;
        border: 1px solid rgba(74,144,217,0.25) !important;
        border-radius: 7px !important;
        color: #a8c7e8 !important;
        font-family: 'Space Mono', monospace !important;
    }

    /* ── rate-text ── */
    .rate-text {
        font-family: 'Space Mono', monospace;
        color: #5dade2;
        font-size: 0.95em;
        margin: 8px 0 6px;
        padding: 8px 14px;
        background: rgba(93,173,226,0.07);
        border-radius: 6px;
        letter-spacing: 0.04em;
    }

    /* ── divider ── */
    hr {
        border-color: rgba(74,144,217,0.1) !important;
        margin: 24px 0 !important;
    }

    /* ── NEW SESSION 버튼 ── */
    [data-testid="stSidebar"] button[kind="secondary"]:has(+ *),
    div[data-testid="stSidebar"] div:has(> button[key="reset_inputs"]) button {
        background: linear-gradient(135deg, #0d2a1a, #0a1f2e) !important;
        border-color: rgba(46,204,113,0.4) !important;
        color: #2ecc71 !important;
    }
    div[data-testid="stSidebar"] div:has(> button[key="reset_inputs"]) button:hover {
        background: #2ecc71 !important;
        color: #000 !important;
    }

    /* ── 스크롤바 ── */
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: #060c16; }
    ::-webkit-scrollbar-thumb { background: #1e3a5f; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ── 헤더 헬퍼 ──────────────────────────────────────────────
def section_header(num, title, color="#4a90d9", rgb="74,144,217"):
    st.markdown(f"""
    <div class="section-header" style="--hdr-color:{color}; --hdr-rgb:{rgb};">
        <span class="num">{num}</span>
        <span class="title">{title}</span>
        <span class="line"></span>
    </div>
    """, unsafe_allow_html=True)

# ── 세션 초기화 ────────────────────────────────────────────
if 'db' not in st.session_state: st.session_state.db = load_data()
if 'page' not in st.session_state: st.session_state.page = 'settle'

# ── 사이드바 ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="font-family:'Space Mono',monospace; font-size:1.1em; font-weight:700;
                color:#4a90d9; letter-spacing:0.15em; text-align:center;
                padding:10px 0 20px; border-bottom:1px solid rgba(74,144,217,0.2); margin-bottom:16px;">
        💹 SETTLEMENT
    </div>
    """, unsafe_allow_html=True)
    if st.button("🚀  정산 작업", use_container_width=True): st.session_state.page = 'settle'; st.rerun()
    if st.button("⚙️  머천트 관리", use_container_width=True): st.session_state.page = 'admin'; st.rerun()

    st.divider()

    reset_keys = ["s_b", "s_s", "s_amt", "bal_in", "w_in", "t_b", "t_u", "t_s"]
    if st.button("⟳  NEW SESSION", key="reset_inputs", use_container_width=True):
        for k in reset_keys:
            st.session_state[k] = ""
        st.session_state.page = 'settle'
        st.toast("입력값이 초기화되었습니다", icon="🔄")
        st.rerun()

    st.divider()
    if st.button("🔄  데이터 복구", use_container_width=True):
        st.session_state.db = get_default_data()
        save_data(st.session_state.db); st.success("복구 완료"); st.rerun()

# ══════════════════════════════════════════════════════════
# 정산 페이지
# ══════════════════════════════════════════════════════════
if st.session_state.page == 'settle':

    # 30초 자동갱신 트리거
    if "bithumb_ts" in st.session_state and (time.time() - st.session_state.get("bithumb_ts", 0)) > 30:
        st.session_state.bithumb_price = 0  # 강제 재요청
        st.rerun()

    st.markdown('<div class="main-title">단계별 정산 시스템</div>', unsafe_allow_html=True)

    merchants = st.session_state.db['merchants']
    sorted_keys = sorted(list(merchants.keys()))
    default_idx = sorted_keys.index('spfxm') if 'spfxm' in sorted_keys else 0
    selected_m = st.selectbox("업체 선택", sorted_keys, index=default_idx)
    m_info = merchants[selected_m]

    # ── 01 ─────────────────────────────────────────────────
    section_header("01", "정산 환율", "#4a90d9", "74,144,217")
    sel_p = st.radio("적용 배수", ["4%", "4.5%", "5%"], index=0, horizontal=True)
    m_map = {"4%": 1.04, "4.5%": 1.045, "5%": 1.05}

    import datetime

    @st.cache_data(ttl=30, show_spinner=False)
    def fetch_market_data(_ts):
        bithumb, kimchi = 0, None
        try:
            r1 = requests.get("https://api.bithumb.com/public/ticker/USDT_KRW", timeout=3)
            if r1.json().get("status") == "0000":
                bithumb = int(float(r1.json()["data"]["closing_price"]))
        except: pass
        try:
            r2 = requests.get("https://api.upbit.com/v1/ticker?markets=KRW-BTC", timeout=3)
            r3 = requests.get("https://api.bithumb.com/public/ticker/BTC_KRW", timeout=3)
            upbit_btc   = float(r2.json()[0]["trade_price"])
            bithumb_btc = float(r3.json()["data"]["closing_price"])
            if bithumb_btc > 0:
                kimchi = round(((upbit_btc / bithumb_btc) - 1) * 100, 2)
        except: pass
        return bithumb, kimchi

    now_ts2 = int(time.time() // 30)
    bithumb, kimchi = fetch_market_data(now_ts2)
    st.session_state.bithumb_price = bithumb
    st.session_state.kimchi = kimchi
    st.session_state.usd_krw = bithumb
    st.session_state.bithumb_ts = time.time()

    live_price = st.session_state.get("bithumb_price", 0)
    kimchi     = st.session_state.get("kimchi", None)
    usd_krw    = st.session_state.get("usd_krw", 0)
    fetched_time = datetime.datetime.fromtimestamp(st.session_state.get("bithumb_ts", now_ts)).strftime("%H:%M:%S")

    # ── 전광판 ────────────────────────────────────────────
    if kimchi is not None:
        k_color  = "#2ecc71" if kimchi >= 0 else "#e74c3c"
        k_glow   = "rgba(46,204,113,0.3)" if kimchi >= 0 else "rgba(231,76,60,0.3)"
        k_sign   = "+" if kimchi >= 0 else ""
        k_label  = "PREMIUM" if kimchi >= 0 else "DISCOUNT"
    else:
        k_color, k_glow, k_sign, k_label = "#888", "transparent", "", "N/A"

    bithumb_str = ("&#8361; " + fmt(live_price)) if live_price > 0 else "&mdash;"
    kimchi_str  = (k_sign + str(kimchi) + "%") if kimchi is not None else "&mdash;"

    html = (
        "<style>@keyframes blink{0%,100%{opacity:1;}50%{opacity:0.15;}}</style>"

        "<div style='padding:12px 18px;margin-bottom:8px;"
        "background:linear-gradient(135deg,#030f1c,#041810);"
        "border:1px solid rgba(93,173,226,0.3);border-radius:10px;"
        "box-shadow:0 0 18px rgba(93,173,226,0.1);"
        "display:flex;align-items:center;justify-content:space-between;'>"
        "<div>"
        "<div style='font-family:Space Mono,monospace;font-size:0.65em;"
        "color:#5dade2;letter-spacing:0.12em;margin-bottom:6px;'>"
        "BITHUMB &nbsp; USDT / KRW &nbsp;"
        "<span style='display:inline-block;width:6px;height:6px;border-radius:50%;"
        "background:#2ecc71;box-shadow:0 0 6px #2ecc71;"
        "animation:blink 1.5s infinite;vertical-align:middle;'></span>"
        "</div>"
        "<div style='font-family:Space Mono,monospace;font-size:1.7em;"
        "font-weight:700;color:#fff;letter-spacing:0.03em;'>" + bithumb_str + "</div>"
        "</div>"
        "<div style='font-family:Space Mono,monospace;font-size:0.65em;"
        "color:rgba(255,255,255,0.2);'>" + fetched_time + " 기준</div>"
        "</div>"

        "<div style='padding:12px 22px;margin-bottom:16px;"
        "background:linear-gradient(135deg,#060606,#0a0a0a);"
        "border:1px solid " + k_color + "55;border-radius:10px;"
        "box-shadow:0 0 20px " + k_glow + ";"
        "display:flex;align-items:center;justify-content:space-between;'>"
        "<div style='display:flex;align-items:center;gap:10px;'>"
        "<span style='font-family:Space Mono,monospace;font-size:0.65em;"
        "color:" + k_color + ";letter-spacing:0.15em;'>KIMCHI PREMIUM</span>"
        "<span style='font-family:Space Mono,monospace;font-size:0.65em;"
        "padding:2px 8px;border-radius:4px;"
        "background:" + k_color + "22;color:" + k_color + ";'>" + k_label + "</span>"
        "</div>"
        "<div style='font-family:Space Mono,monospace;font-size:1.9em;"
        "font-weight:700;color:" + k_color + ";"
        "text-shadow:0 0 16px " + k_glow + ";'>" + kimchi_str + "</div>"
        "</div>"
    )
    st.markdown(html, unsafe_allow_html=True)

    sc1, sc2 = st.columns(2)
    with sc1:
        sb_default = str(live_price) if live_price > 0 and not st.session_state.get("s_b") else st.session_state.get("s_b", "")
        sb_val = extract_int(st.text_input("빗썸 시세", value=sb_default, key="s_b"))
    with sc2: ss_val = extract_int(st.text_input("수동 환율", key="s_s"))
    s_rate = ss_val if ss_val > 0 else math.ceil(sb_val * m_map[sel_p])

    # 30초 후 자동 리런
    if now_ts - st.session_state.get("bithumb_ts", 0) > 30:
        st.rerun()

    if s_rate > 0:
        editable_box(f"1usdt = {fmt(s_rate)} krw", "sky", "rate_01")

    # ── 02 ─────────────────────────────────────────────────
    section_header("02", "정산 멘트 생성", "#4a90d9", "74,144,217")
    amt = extract_int(st.text_input("정산 금액 (KRW) 입력", key="s_amt"))
    if amt > 0 and s_rate > 0:
        u_val = round(amt / s_rate, 2)
        s_msg = (f"- {selected_m} settlement amount : {fmt(amt)} krw\n"
                 f"- exchange to usdt : {u_val:,.2f} usdt\n"
                 f"- 1usdt = {fmt(s_rate)} krw\n\n"
                 f"{m_info['wallet']}\n\n"
                 f"Please confirm the address and calculation.\n"
                 f"Once approved, we will proceed immediately")
        editable_box(s_msg, "blue", "res_02")

    # ── 03 ─────────────────────────────────────────────────
    section_header("03", "최종 잔액 보고", "#4a90d9", "74,144,217")
    bal_in = extract_int(st.text_input("현재 잔액 입력 (KRW)", key="bal_in"))
    if bal_in > 0 and amt > 0:
        u_ceil = math.ceil(amt / s_rate)
        b_msg = (f"Balance & settlement update\n\n"
                 f"- {selected_m}\n"
                 f"settlement amount : {fmt(amt)} krw\n"
                 f"exchange to usdt : {fmt(u_ceil)} usdt\n"
                 f"1usdt = {fmt(s_rate)} krw\n\n"
                 f"- {selected_m} : {fmt(bal_in)} krw")
        editable_box(b_msg, "green", "res_03")

    # ── 04 ─────────────────────────────────────────────────
    section_header("04", "마크업 수수료", "#f39c12", "243,156,18")
    if amt > 0:
        m_fee = float(m_info.get('fee', 0.5))
        markup = math.ceil(amt * (m_fee / 100))
        markup_msg = f"드래곤 테더정산 마크업 {m_fee}% {selected_m} / {fmt(amt)} / {fmt(markup)}"
        editable_box(markup_msg, "yellow", "res_04")

    # ── 05 ─────────────────────────────────────────────────
    section_header("05", "정산 (SETTLEMENT) 요청", "#e74c3c", "231,76,60")
    w_bal = extract_int(st.text_input("하이 밸런스 경고용 잔액", key="w_in"))
    if w_bal > 0:
        st.markdown(f'<p class="rate-text">▸ 적용 환율 &nbsp; 1usdt = {fmt(s_rate)} krw</p>', unsafe_allow_html=True)
        w_msg = (f"Hello, Team\n"
                 f"Currently, the balance of the merchants is too high.\n"
                 f"To ensure a safe balance, please proceed with USDT settlement.\n"
                 f"Thank you\n\n"
                 f"Balance update\n\n"
                 f"- {selected_m} : {fmt(w_bal)} krw")
        editable_box(w_msg, "red", "res_05")

    st.divider()

    # ── 06 ─────────────────────────────────────────────────
    section_header("06", "TOP-UP 탑업", "#2ecc71", "46,204,113")

    t_row1_col1, t_row1_col2 = st.columns(2)
    with t_row1_col1: tb_val = extract_int(st.text_input("탑업 시세(빗썸)", key="t_b"))
    with t_row1_col2: tu_amt = extract_int(st.text_input("수량(USDT)", key="t_u"))

    t_row2_col1, t_row2_col2 = st.columns(2)
    with t_row2_col1: ts_val = extract_int(st.text_input("수동 환율", key="t_s"))
    with t_row2_col2:
        t_rate = ts_val if ts_val > 0 else (tb_val - math.ceil(tb_val * 0.005) if tb_val > 0 else 0)
        if t_rate > 0:
            st.markdown(
                f"<div style='padding-top:32px; font-family:Space Mono,monospace; "
                f"color:#5dade2; font-size:0.95em; letter-spacing:0.04em;'>"
                f"1usdt = {fmt(t_rate)} krw</div>",
                unsafe_allow_html=True
            )

    if tu_amt > 0 and t_rate > 0:
        total_t_krw = tu_amt * t_rate
        my_w = st.session_state.db.get('my_wallet', '')
        t_msg = (f"top-up\n\n"
                 f"mid : {selected_m}\n"
                 f"top-up amount : {fmt(tu_amt)} usdt\n"
                 f"exchange to KRW : {fmt(total_t_krw)} krw\n"
                 f"1usdt = {fmt(t_rate)} krw\n\n"
                 f"{my_w}\n\n"
                 f"Please check the invoice and transfer the USDT to the address provided.")
        editable_box(t_msg, "green", "res_06_req")

        m_fee_t = float(m_info.get('fee', 0.5))
        base_p = ts_val if ts_val > 0 else tb_val
        t_markup = math.ceil((tu_amt * base_p) * (m_fee_t / 100))
        f_msg = f"드래곤 테더탑업 마크업 {m_fee_t}% {selected_m} / {fmt(tu_amt * base_p)} / {fmt(t_markup)}"
        editable_box(f_msg, "yellow", "res_06_fee")

# ══════════════════════════════════════════════════════════
# 관리자 페이지
# ══════════════════════════════════════════════════════════
elif st.session_state.page == 'admin':
    st.markdown('<div class="main-title">머천트 및 지갑 관리</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="
        margin-top: 8px;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 10px 16px;
        background: rgba(255,255,255,0.02);
        border-radius: 8px;
        border-left: 3px solid #4a90d9;
        overflow: hidden;
        position: relative;
    ">
        <div style="position:absolute;top:0;left:0;right:0;bottom:0;
            background:linear-gradient(90deg,rgba(74,144,217,0.07) 0%,transparent 100%);
            pointer-events:none;"></div>
        <span style="font-family:'Space Mono',monospace;font-size:0.75em;font-weight:700;
            color:#4a90d9;letter-spacing:0.1em;opacity:0.7;">MY</span>
        <span style="font-family:'Noto Sans KR',sans-serif;font-size:0.92em;font-weight:700;
            color:#d0dff0;letter-spacing:0.08em;text-transform:uppercase;">내 지갑 주소</span>
        <span style="flex:1;height:1px;background:linear-gradient(90deg,rgba(74,144,217,0.3) 0%,transparent 100%);"></span>
    </div>
    """, unsafe_allow_html=True)

    my_w = st.text_input("내 USDT 지갑 주소", value=st.session_state.db.get('my_wallet', ''), label_visibility="collapsed")
    if st.button("저장", use_container_width=True):
        st.session_state.db['my_wallet'] = my_w
        save_data(st.session_state.db); st.toast("지갑 정보가 저장되었습니다.")

    st.markdown("""
    <div style="
        margin-top: 32px;
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 10px 16px;
        background: rgba(255,255,255,0.02);
        border-radius: 8px;
        border-left: 3px solid #a855f7;
        position: relative;
        overflow: hidden;
    ">
        <div style="position:absolute;top:0;left:0;right:0;bottom:0;
            background:linear-gradient(90deg,rgba(168,85,247,0.07) 0%,transparent 100%);
            pointer-events:none;"></div>
        <span style="font-family:'Space Mono',monospace;font-size:0.75em;font-weight:700;
            color:#a855f7;letter-spacing:0.1em;opacity:0.7;">NEW</span>
        <span style="font-family:'Noto Sans KR',sans-serif;font-size:0.92em;font-weight:700;
            color:#d0dff0;letter-spacing:0.08em;text-transform:uppercase;">업체 추가</span>
        <span style="flex:1;height:1px;background:linear-gradient(90deg,rgba(168,85,247,0.3) 0%,transparent 100%);"></span>
    </div>
    """, unsafe_allow_html=True)

    with st.form("new_merchant"):
        n_name   = st.text_input("업체명")
        n_wallet = st.text_input("지갑주소")
        n_fee    = st.text_input("마크업 수수료 (%)", value="0.5")
        n_note   = st.text_input("비고")
        if st.form_submit_button("등록", use_container_width=True):
            st.session_state.db['merchants'][n_name] = {"wallet": n_wallet, "fee": n_fee, "note": n_note}
            save_data(st.session_state.db); st.toast(f"{n_name} 업체 등록됨"); st.rerun()

    st.markdown("""
    <div style="
        margin-top: 32px;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 10px 16px;
        background: rgba(255,255,255,0.02);
        border-radius: 8px;
        border-left: 3px solid #2ecc71;
        position: relative;
        overflow: hidden;
    ">
        <div style="position:absolute;top:0;left:0;right:0;bottom:0;
            background:linear-gradient(90deg,rgba(46,204,113,0.07) 0%,transparent 100%);
            pointer-events:none;"></div>
        <span style="font-family:'Space Mono',monospace;font-size:0.75em;font-weight:700;
            color:#2ecc71;letter-spacing:0.1em;opacity:0.7;">LIST</span>
        <span style="font-family:'Noto Sans KR',sans-serif;font-size:0.92em;font-weight:700;
            color:#d0dff0;letter-spacing:0.08em;text-transform:uppercase;">등록 업체 관리</span>
        <span style="flex:1;height:1px;background:linear-gradient(90deg,rgba(46,204,113,0.3) 0%,transparent 100%);"></span>
    </div>
    """, unsafe_allow_html=True)

    for name in sorted(st.session_state.db['merchants'].keys()):
        with st.expander(f"📦 {name} 관리"):
            info = st.session_state.db['merchants'][name]
            u_w = st.text_input("지갑주소",          value=info['wallet'],          key=f"w_{name}")
            u_f = st.text_input("마크업 수수료 (%)", value=info['fee'],             key=f"f_{name}")
            u_n = st.text_input("비고",              value=info.get('note', ''),   key=f"n_{name}")
            col_save, col_del = st.columns([3, 1])
            with col_save:
                if st.button("변경사항 저장", key=f"s_{name}", use_container_width=True):
                    st.session_state.db['merchants'][name] = {"wallet": u_w, "fee": u_f, "note": u_n}
                    save_data(st.session_state.db); st.toast(f"{name} 변경사항이 저장되었습니다.")
            with col_del:
                if st.button("삭제", key=f"d_{name}", use_container_width=True):
                    del st.session_state.db['merchants'][name]; save_data(st.session_state.db); st.rerun()
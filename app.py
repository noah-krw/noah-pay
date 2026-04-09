# -*- coding: utf-8 -*-
import streamlit as st
import streamlit.components.v1 as components
import math, json, os, re, requests, time, datetime, base64

# ── GitHub 연동 함수 ──────────────────────────────────────
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "")
GITHUB_REPO  = st.secrets.get("GITHUB_REPO", "noah-krw/ops-manager-tool")
GITHUB_FILE  = st.secrets.get("GITHUB_FILE", "merchants.json")
GITHUB_API   = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE}"

def load_data():
    """GitHub에서 merchants.json 읽기"""
    try:
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        r = requests.get(GITHUB_API, headers=headers, timeout=5)
        if r.status_code == 200:
            content = base64.b64decode(r.json()["content"]).decode("utf-8")
            return json.loads(content)
    except:
        pass
    return get_default_data()

def save_data(data):
    """GitHub에 merchants.json 저장"""
    try:
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        # 현재 파일 SHA 가져오기 (업데이트에 필요)
        r = requests.get(GITHUB_API, headers=headers, timeout=5)
        sha = r.json().get("sha", "") if r.status_code == 200 else ""
        content = base64.b64encode(json.dumps(data, indent=4, ensure_ascii=False).encode()).decode()
        payload = {
            "message": "Update merchants.json via Streamlit",
            "content": content,
            "sha": sha
        }
        requests.put(GITHUB_API, headers=headers, json=payload, timeout=5)
    except Exception as e:
        st.error(f"저장 실패: {e}")

def get_default_data():
    return {
        'my_wallet': 'TDaQt8oASZhVsuaEdpevqCacGKseGKCWhQ',
        'merchants': {
            'spfxm': {'wallet': 'TWbFbzW5GRkAkVrY4fLuXhNA576DCkoGbh', 'fee': '4', 'note': '메인 업체'}
        }
    }

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
    <div style="margin-bottom:14px;">
        <div style="border-left:3px solid {c['border']};border-radius:0 8px 8px 0;
            box-shadow:0 0 18px {c['glow']},inset 0 0 30px rgba(0,0,0,0.3);
            overflow:hidden;background:{c['bg']};">
            <textarea id="copy_area_{box_id}" style="width:100%;height:{height-55}px;
                background:#ffffff;color:#1a1a1a;border:none;outline:none;
                font-family:'Courier New',monospace;font-size:14px;line-height:1.7;
                padding:14px 16px;box-sizing:border-box;resize:none;">{text}</textarea>
            <div style="display:flex;align-items:center;justify-content:flex-end;
                gap:10px;padding:8px 12px 10px;border-top:1px solid rgba(255,255,255,0.08);
                background:rgba(0,0,0,0.2);">
                <span style="font-family:'Courier New',monospace;font-size:13px;
                    color:{c['text']};opacity:0.6;">✎ 직접 수정 가능</span>
                <button id="btn_{box_id}" onclick="copyText_{box_id}()" style="
                    padding:7px 18px;background:{c['btn_bg']};color:{c['text']};
                    border:1px solid {c['border']};border-radius:6px;cursor:pointer;
                    font-family:'Courier New',monospace;font-size:13px;font-weight:600;">COPY</button>
            </div>
        </div>
    </div>
    <script>
    function copyText_{box_id}() {{
        const t = document.getElementById('copy_area_{box_id}');
        const b = document.getElementById('btn_{box_id}');
        t.select(); t.setSelectionRange(0,99999);
        try {{
            document.execCommand('copy');
            b.innerText='COPIED'; b.style.background='{c['border']}'; b.style.color='#000';
            setTimeout(()=>{{b.innerText='COPY';b.style.background='{c['btn_bg']}';b.style.color='{c['text']}';}},1800);
        }} catch(e) {{}}
    }}
    </script>"""
    components.html(html_code, height=height)


st.set_page_config(page_title="단계별 정산 시스템 v97", layout="centered")
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Noto+Sans+KR:wght@300;400;500;700&display=swap" rel="stylesheet">
<style>
    [data-testid="stAppViewContainer"] {
        background-color: #060c16 !important;
        background-image: radial-gradient(ellipse at 20% 0%, rgba(30,60,100,0.35) 0%, transparent 60%),
            radial-gradient(ellipse at 80% 100%, rgba(20,80,60,0.2) 0%, transparent 60%);
        color: #c8d6e5 !important;
    }
    [data-testid="stHeader"] { background: transparent !important; }
    [data-testid="stSidebar"] { background: #080e1a !important; border-right: 1px solid rgba(74,144,217,0.15) !important; }
    [data-testid="stSidebar"] button {
        width:100%; background:#0d1a2e !important; color:#7aa8cc !important;
        border:1px solid rgba(74,144,217,0.25) !important; border-radius:8px !important;
        font-family:'Space Mono',monospace !important; font-size:0.9em !important;
        font-weight:600 !important; letter-spacing:0.08em !important;
        padding:11px 0 !important; transition:all 0.2s ease !important;
    }
    [data-testid="stSidebar"] button:hover {
        background:#1a2e48 !important; border-color:#4a90d9 !important;
        color:#cde4f8 !important; box-shadow:0 0 12px rgba(74,144,217,0.2) !important;
    }
    .main-title {
        font-family:'Space Mono',monospace; color:#4a90d9; font-size:2.4em; font-weight:700;
        text-align:center; letter-spacing:0.22em; text-transform:uppercase;
        margin-bottom:28px; padding:22px 0 18px;
        border-bottom:1px solid rgba(74,144,217,0.25);
        text-shadow:0 0 30px rgba(74,144,217,0.4);
    }
    .main-title::after { content:''; display:block; width:80px; height:2px;
        background:linear-gradient(90deg,transparent,#4a90d9,transparent); margin:12px auto 0; }
    .section-header {
        display:flex; align-items:center; gap:12px; margin-top:32px; margin-bottom:14px;
        padding:10px 16px; background:rgba(255,255,255,0.02); border-radius:8px;
        border-left:3px solid var(--hdr-color,#4a90d9); position:relative; overflow:hidden;
    }
    .section-header::before { content:''; position:absolute; top:0;left:0;right:0;bottom:0;
        background:linear-gradient(90deg,rgba(var(--hdr-rgb,74,144,217),0.08) 0%,transparent 100%); pointer-events:none; }
    .section-header .num { font-family:'Space Mono',monospace; font-size:0.75em; font-weight:700;
        color:var(--hdr-color,#4a90d9); letter-spacing:0.1em; opacity:0.7; }
    .section-header .title { font-family:'Noto Sans KR',sans-serif; font-size:0.92em; font-weight:700;
        color:#d0dff0; letter-spacing:0.08em; text-transform:uppercase; }
    .section-header .line { flex:1; height:1px;
        background:linear-gradient(90deg,rgba(var(--hdr-rgb,74,144,217),0.3) 0%,transparent 100%); }
    div[data-baseweb="input"] { background-color:#0b1525 !important; border-radius:7px !important;
        border:1px solid rgba(74,144,217,0.25) !important; }
    div[data-baseweb="input"]:focus-within { border-color:rgba(74,144,217,0.7) !important; }
    input { color:#dce8f5 !important; font-family:'Space Mono',monospace !important;
        font-size:1.1em !important; background:transparent !important; caret-color:#4a90d9 !important; }
    label[data-testid="stWidgetLabel"] > div > p { color:#6a8aaa !important; font-size:0.82em !important;
        font-family:'Space Mono',monospace !important; letter-spacing:0.06em !important; text-transform:uppercase !important; }
    [data-testid="stRadio"] label { font-family:'Space Mono',monospace !important; font-size:0.88em !important; color:#7aa8cc !important; }
    div[data-baseweb="select"] > div { background-color:#0b1525 !important;
        border:1px solid rgba(74,144,217,0.25) !important; border-radius:7px !important;
        color:#a8c7e8 !important; font-family:'Space Mono',monospace !important; }
    .rate-text { font-family:'Space Mono',monospace; color:#5dade2; font-size:0.95em;
        margin:8px 0 6px; padding:8px 14px; background:rgba(93,173,226,0.07); border-radius:6px; }
    hr { border-color:rgba(74,144,217,0.1) !important; margin:24px 0 !important; }
    div[data-testid="stSidebar"] div:has(> button[key="reset_inputs"]) button {
        background:linear-gradient(135deg,#0d2a1a,#0a1f2e) !important;
        border-color:rgba(46,204,113,0.4) !important; color:#2ecc71 !important; }
    div[data-testid="stSidebar"] div:has(> button[key="reset_inputs"]) button:hover {
        background:#2ecc71 !important; color:#000 !important; }
    ::-webkit-scrollbar { width:5px; }
    ::-webkit-scrollbar-track { background:#060c16; }
    ::-webkit-scrollbar-thumb { background:#1e3a5f; border-radius:10px; }
</style>
""", unsafe_allow_html=True)

def section_header(num, title, color="#4a90d9", rgb="74,144,217"):
    st.markdown(f"""
    <div class="section-header" style="--hdr-color:{color};--hdr-rgb:{rgb};">
        <span class="num">{num}</span>
        <span class="title">{title}</span>
        <span class="line"></span>
    </div>""", unsafe_allow_html=True)

if 'db' not in st.session_state: st.session_state.db = load_data()
if 'page' not in st.session_state: st.session_state.page = 'settle'

if 'bithumb_price' not in st.session_state:
    try:
        _r = requests.get('https://api.bithumb.com/public/ticker/USDT_KRW', timeout=3)
        if _r.json().get('status') == '0000':
            st.session_state.bithumb_price = int(float(_r.json()['data']['closing_price']))
        else:
            st.session_state.bithumb_price = 0
    except:
        st.session_state.bithumb_price = 0
    st.session_state.bithumb_ts = time.time()

with st.sidebar:
    st.markdown("""
    <div style="font-family:'Space Mono',monospace;font-size:1.1em;font-weight:700;
        color:#4a90d9;letter-spacing:0.15em;text-align:center;
        padding:10px 0 20px;border-bottom:1px solid rgba(74,144,217,0.2);margin-bottom:16px;">
        💹 SETTLEMENT
    </div>""", unsafe_allow_html=True)
    if st.button("🚀  USDT 정산", use_container_width=True):
        st.session_state.page = 'settle'; st.rerun()
    if st.button("📤  USDT 탑업", use_container_width=True):
        st.session_state.page = 'topup'; st.rerun()
    if st.button("⚙️  머천트 관리", use_container_width=True):
        st.session_state.page = 'admin'; st.rerun()
    st.divider()
    reset_keys = ["t_b","t_u","t_k","t_s"] if st.session_state.page == "topup" else ["s_b","s_s","s_amt","bal_in","w_in"]
    if st.button("⟳  NEW SESSION", key="reset_inputs", use_container_width=True):
        for k in reset_keys: st.session_state[k] = ""
        st.toast("입력값이 초기화되었습니다", icon="🔄"); st.rerun()
    st.divider()
    if st.button("🔄  데이터 복구", use_container_width=True):
        st.session_state.db = get_default_data()
        save_data(st.session_state.db); st.success("복구 완료"); st.rerun()

# ══════════════════════════════════════════════════════════
# 정산 페이지
# ══════════════════════════════════════════════════════════
if st.session_state.page == 'settle':
    st.markdown('<div class="main-title">USDT 정산</div>', unsafe_allow_html=True)
    merchants = st.session_state.db['merchants']
    sorted_keys = sorted(list(merchants.keys()))
    default_idx = sorted_keys.index('spfxm') if 'spfxm' in sorted_keys else 0
    selected_m = st.selectbox("", sorted_keys, index=default_idx, label_visibility="collapsed")
    m_info = merchants[selected_m]
    m_map = {"4%": 1.04, "4.5%": 1.045, "5%": 1.05}
    sel_p = st.radio("", ["4%", "4.5%", "5%"], index=0, horizontal=True, label_visibility="collapsed")

    section_header("01", "정산 환율", "#4a90d9", "74,144,217")
    live_price = st.session_state.get("bithumb_price", 0)
    kst = datetime.timezone(datetime.timedelta(hours=9))
    fetched_time = datetime.datetime.fromtimestamp(st.session_state.get("bithumb_ts", time.time()), tz=kst).strftime("%H:%M:%S")
    bithumb_str = ("&#8361; " + fmt(live_price)) if live_price > 0 else "&mdash;"
    html = (
        "<style>@keyframes blink{0%,100%{opacity:1;}50%{opacity:0.15;}}</style>"
        "<div style='padding:14px 22px;margin-bottom:14px;background:linear-gradient(135deg,#030f1c,#041810);"
        "border:1px solid rgba(93,173,226,0.3);border-radius:10px;box-shadow:0 0 18px rgba(93,173,226,0.1);"
        "display:flex;align-items:center;justify-content:space-between;'>"
        "<div style='display:flex;align-items:center;gap:8px;'>"
        "<span style='display:inline-block;width:7px;height:7px;border-radius:50%;background:#2ecc71;"
        "box-shadow:0 0 7px #2ecc71;animation:blink 1.5s infinite;'></span>"
        "<span style='font-family:Space Mono,monospace;font-size:0.68em;color:#5dade2;letter-spacing:0.1em;'>BITHUMB &nbsp; USDT / KRW</span>"
        "</div>"
        "<div style='display:flex;flex-direction:column;align-items:center;gap:3px;'>"
        "<div style='font-family:Space Mono,monospace;font-size:1.8em;font-weight:700;color:#ffffff;'>" + bithumb_str + "</div>"
        "<div style='font-family:Space Mono,monospace;font-size:0.68em;color:#5dade2;'>" + fetched_time + "</div>"
        "</div>"
        "<a href='https://search.naver.com/search.naver?query=%EB%B9%97%EC%8D%B8+%ED%85%8C%EB%8D%94+%EC%8B%9C%EC%84%B8' "
        "target='_blank' style='font-family:Space Mono,monospace;font-size:0.85em;font-weight:700;"
        "color:#2ecc71;border:1px solid rgba(46,204,113,0.5);border-radius:8px;padding:10px 20px;"
        "text-decoration:none;background:rgba(46,204,113,0.08);'>김프 확인</a></div>"
    )
    st.markdown(html, unsafe_allow_html=True)
    if st.button('⟳  시세 새로고침', key='refresh_ticker'):
        if 'bithumb_price' in st.session_state: del st.session_state['bithumb_price']
        st.rerun()

    sc1, sc2 = st.columns(2)
    with sc1:
        if st.session_state.get("s_b", "") == "" and live_price > 0:
            st.session_state["s_b"] = str(live_price)
        sb_val = extract_int(st.text_input("빗썸 시세", key="s_b"))
    with sc2: ss_val = extract_int(st.text_input("수동 환율", key="s_s"))
    s_rate = ss_val if ss_val > 0 else math.ceil(sb_val * m_map[sel_p])
    if s_rate > 0: editable_box(f"1usdt = {fmt(s_rate)} krw", "sky", "rate_01")

    section_header("02", "정산 멘트 생성", "#4a90d9", "74,144,217")
    amt = extract_int(st.text_input("정산 금액 (KRW) 입력", key="s_amt"))
    if amt > 0 and s_rate > 0:
        u_val = round(amt / s_rate, 2)
        s_msg = (f"mid : {selected_m}\nsettlement amount : {fmt(amt)} krw\n"
                 f"exchange to usdt : {u_val:,.2f} usdt\n1usdt = {fmt(s_rate)} krw\n\n"
                 f"{m_info['wallet']}\n\nPlease confirm the address and calculation.\n"
                 f"Once approved, we will proceed immediately")
        editable_box(s_msg, "blue", "res_02")

    section_header("03", "최종 잔액 보고", "#4a90d9", "74,144,217")
    bal_in = extract_int(st.text_input("현재 잔액 입력 (KRW)", key="bal_in"))
    if bal_in > 0 and amt > 0 and s_rate > 0:
        u_ceil = math.ceil(amt / s_rate)
        b_msg = (f"Balance & settlement update\n\n- {selected_m}\n"
                 f"settlement amount : {fmt(amt)} krw\nexchange to usdt : {fmt(u_ceil)} usdt\n"
                 f"1usdt = {fmt(s_rate)} krw\n\n- {selected_m} : {fmt(bal_in)} krw")
        editable_box(b_msg, "green", "res_03")

    section_header("04", "마크업 수수료", "#f39c12", "243,156,18")
    if amt > 0:
        m_fee = float(m_info.get('fee', 0.5))
        markup = math.ceil(amt * (m_fee / 100))
        markup_msg = f"드래곤 테더정산 마크업 {m_fee}% {selected_m} / {fmt(amt)} / {fmt(markup)}"
        editable_box(markup_msg, "yellow", "res_04")

    section_header("05", "정산 (SETTLEMENT) 요청", "#e74c3c", "231,76,60")
    w_bal = extract_int(st.text_input("하이 밸런스 경고용 잔액", key="w_in"))
    if w_bal > 0 and s_rate > 0:
        st.markdown(f'<p class="rate-text">▸ 적용 환율 &nbsp; 1usdt = {fmt(s_rate)} krw</p>', unsafe_allow_html=True)
        w_msg = (f"Hello, Team\nCurrently, the balance of the merchants is too high.\n"
                 f"To ensure a safe balance, please proceed with USDT settlement.\nThank you\n\n"
                 f"Balance update\n\n- {selected_m} : {fmt(w_bal)} krw")
        editable_box(w_msg, "red", "res_05")

# ══════════════════════════════════════════════════════════
# 탑업 페이지
# ══════════════════════════════════════════════════════════
elif st.session_state.page == 'topup':
    st.markdown('<div class="main-title">USDT 탑업</div>', unsafe_allow_html=True)
    merchants = st.session_state.db['merchants']
    sorted_keys = sorted(list(merchants.keys()))
    default_idx = sorted_keys.index('spfxm') if 'spfxm' in sorted_keys else 0
    selected_m = st.selectbox("", sorted_keys, index=default_idx, label_visibility="collapsed", key="topup_merchant")
    m_info = merchants[selected_m]
    live_price = st.session_state.get("bithumb_price", 0)
    kst = datetime.timezone(datetime.timedelta(hours=9))
    fetched_time = datetime.datetime.fromtimestamp(st.session_state.get("bithumb_ts", time.time()), tz=kst).strftime("%H:%M:%S")
    bithumb_str = ("&#8361; " + fmt(live_price)) if live_price > 0 else "&mdash;"
    topup_html = (
        "<style>@keyframes blink2{0%,100%{opacity:1;}50%{opacity:0.15;}}</style>"
        "<div style='padding:14px 22px;margin-bottom:14px;background:linear-gradient(135deg,#030f1c,#041810);"
        "border:1px solid rgba(93,173,226,0.3);border-radius:10px;display:flex;align-items:center;justify-content:space-between;'>"
        "<div style='display:flex;align-items:center;gap:8px;'>"
        "<span style='display:inline-block;width:7px;height:7px;border-radius:50%;background:#2ecc71;"
        "box-shadow:0 0 7px #2ecc71;animation:blink2 1.5s infinite;'></span>"
        "<span style='font-family:Space Mono,monospace;font-size:0.68em;color:#5dade2;'>BITHUMB &nbsp; USDT / KRW</span>"
        "</div>"
        "<div style='display:flex;flex-direction:column;align-items:center;gap:3px;'>"
        "<div style='font-family:Space Mono,monospace;font-size:1.8em;font-weight:700;color:#ffffff;'>" + bithumb_str + "</div>"
        "<div style='font-family:Space Mono,monospace;font-size:0.68em;color:#5dade2;'>" + fetched_time + "</div>"
        "</div>"
        "<a href='https://search.naver.com/search.naver?query=%EB%B9%97%EC%8D%B8+%ED%85%8C%EB%8D%94+%EC%8B%9C%EC%84%B8' "
        "target='_blank' style='font-family:Space Mono,monospace;font-size:0.85em;font-weight:700;"
        "color:#2ecc71;border:1px solid rgba(46,204,113,0.5);border-radius:8px;padding:10px 20px;"
        "text-decoration:none;background:rgba(46,204,113,0.08);'>김프 확인</a></div>"
    )
    st.markdown(topup_html, unsafe_allow_html=True)

    section_header("01", "TOP-UP 탑업", "#2ecc71", "46,204,113")
    t_row1_col1, t_row1_col2 = st.columns(2)
    with t_row1_col1:
        if st.session_state.get("t_b", "") == "" and live_price > 0:
            st.session_state["t_b"] = str(live_price)
        tb_val = extract_int(st.text_input("탑업 시세(빗썸)", key="t_b"))
    with t_row1_col2: ts_val = extract_int(st.text_input("수동 환율", key="t_s"))

    t_rate = ts_val if ts_val > 0 else (tb_val - math.ceil(tb_val * 0.005) if tb_val > 0 else 0)
    if t_rate > 0:
        st.markdown(f"<div style='font-family:Space Mono,monospace;color:#5dade2;font-size:0.95em;"
                    f"margin-bottom:12px;padding:8px 14px;background:rgba(93,173,226,0.07);border-radius:6px;'>"
                    f"▸ 적용 환율 &nbsp; 1usdt = {fmt(t_rate)} krw</div>", unsafe_allow_html=True)

    t_mode = st.radio("", ["USDT 수량으로 입력", "KRW 금액으로 입력"],
                      horizontal=True, label_visibility="collapsed", key="t_mode")
    if t_mode == "USDT 수량으로 입력":
        tu_amt_raw = extract_int(st.text_input("수량 (USDT)", key="t_u"))
        tu_amt = tu_amt_raw if (t_rate > 0 and tu_amt_raw > 0) else 0
        total_t_krw = tu_amt * t_rate
    else:
        tu_krw_raw = extract_int(st.text_input("금액 (KRW)", key="t_k"))
        if t_rate > 0 and tu_krw_raw > 0:
            total_t_krw = tu_krw_raw
            tu_amt = round(tu_krw_raw / t_rate, 2)
        else:
            tu_amt = 0; total_t_krw = 0

    if tu_amt > 0 and t_rate > 0:
        my_w = st.session_state.db.get('my_wallet', '')
        t_msg = (f"mid : {selected_m}\ntop-up usdt : {fmt(int(tu_amt))} usdt\n"
                 f"exchange to krw : {fmt(int(total_t_krw))} krw\n1usdt = {fmt(t_rate)} krw\n\n"
                 f"{my_w}\n\nPlease check the invoice and transfer the USDT to the address provided.")
        editable_box(t_msg, "green", "res_06_req")
        m_fee_t = float(m_info.get('fee', 0.5))
        base_p = ts_val if ts_val > 0 else tb_val
        t_markup = math.ceil((int(tu_amt) * base_p) * (m_fee_t / 100))
        f_msg = f"{selected_m} 탑업 수수료 / {fmt(int(tu_amt) * base_p)} / {m_fee_t}% / {fmt(t_markup)}"
        editable_box(f_msg, "yellow", "res_06_fee")

# ══════════════════════════════════════════════════════════
# 관리자 페이지
# ══════════════════════════════════════════════════════════
elif st.session_state.page == 'admin':
    st.markdown('<div class="main-title">머천트 및 지갑 관리</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-top:8px;margin-bottom:14px;display:flex;align-items:center;gap:12px;
        padding:10px 16px;background:rgba(255,255,255,0.02);border-radius:8px;
        border-left:3px solid #4a90d9;position:relative;overflow:hidden;">
        <span style="font-family:'Space Mono',monospace;font-size:0.75em;font-weight:700;color:#4a90d9;opacity:0.7;">MY</span>
        <span style="font-family:'Noto Sans KR',sans-serif;font-size:0.92em;font-weight:700;color:#d0dff0;text-transform:uppercase;">내 지갑 주소</span>
    </div>""", unsafe_allow_html=True)
    my_w = st.text_input("내 USDT 지갑 주소", value=st.session_state.db.get('my_wallet', ''), label_visibility="collapsed")
    if st.button("저장", use_container_width=True):
        st.session_state.db['my_wallet'] = my_w
        save_data(st.session_state.db); st.toast("지갑 정보가 저장되었습니다. ✅")

    st.markdown("""
    <div style="margin-top:32px;display:flex;align-items:center;gap:12px;
        padding:10px 16px;background:rgba(255,255,255,0.02);border-radius:8px;
        border-left:3px solid #a855f7;position:relative;overflow:hidden;">
        <span style="font-family:'Space Mono',monospace;font-size:0.75em;font-weight:700;color:#a855f7;opacity:0.7;">NEW</span>
        <span style="font-family:'Noto Sans KR',sans-serif;font-size:0.92em;font-weight:700;color:#d0dff0;text-transform:uppercase;">업체 추가</span>
    </div>""", unsafe_allow_html=True)
    with st.form("new_merchant"):
        n_name   = st.text_input("업체명")
        n_wallet = st.text_input("지갑주소")
        n_fee    = st.text_input("마크업 수수료 (%)", value="0.5")
        n_note   = st.text_input("비고")
        if st.form_submit_button("등록", use_container_width=True):
            st.session_state.db['merchants'][n_name] = {"wallet": n_wallet, "fee": n_fee, "note": n_note}
            save_data(st.session_state.db); st.toast(f"{n_name} 업체 등록됨 ✅"); st.rerun()

    st.markdown("""
    <div style="margin-top:32px;margin-bottom:14px;display:flex;align-items:center;gap:12px;
        padding:10px 16px;background:rgba(255,255,255,0.02);border-radius:8px;
        border-left:3px solid #2ecc71;position:relative;overflow:hidden;">
        <span style="font-family:'Space Mono',monospace;font-size:0.75em;font-weight:700;color:#2ecc71;opacity:0.7;">LIST</span>
        <span style="font-family:'Noto Sans KR',sans-serif;font-size:0.92em;font-weight:700;color:#d0dff0;text-transform:uppercase;">등록 업체 관리</span>
    </div>""", unsafe_allow_html=True)
    for name in sorted(st.session_state.db['merchants'].keys()):
        with st.expander(f"📦 {name} 관리"):
            info = st.session_state.db['merchants'][name]
            u_w = st.text_input("지갑주소",          value=info['wallet'],        key=f"w_{name}")
            u_f = st.text_input("마크업 수수료 (%)", value=info['fee'],           key=f"f_{name}")
            u_n = st.text_input("비고",             value=info.get('note',''),   key=f"n_{name}")
            col_save, col_del = st.columns([3, 1])
            with col_save:
                if st.button("변경사항 저장", key=f"s_{name}", use_container_width=True):
                    st.session_state.db['merchants'][name] = {"wallet": u_w, "fee": u_f, "note": u_n}
                    save_data(st.session_state.db); st.toast(f"{name} 저장됨 ✅")
            with col_del:
                if st.button("삭제", key=f"d_{name}", use_container_width=True):
                    del st.session_state.db['merchants'][name]
                    save_data(st.session_state.db); st.rerun()
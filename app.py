# -*- coding: utf-8 -*-
import streamlit as st
import streamlit.components.v1 as components
import math, json, os, re

# ============================================================
# 정산 매크로 v93.0 - Noah 실장님 최종 지시사항 반영 (에러 해결)
# ============================================================

DB_FILE = "merchants.json"

def get_default_data():
    return {
        'my_wallet': 'TDaQt8oASZhVsuaEdpevqCacGKseGKCWhQ',
        'merchants': {
            'spfxm': {'wallet': 'TWbFbzW5GRkAkVrY4fLuXhNA576DCkoGbh', 'fee': '4'},
            'dr188': {'wallet': 'TBMTb9TFFXDuqhjLKLp9Yo26QHRnnG6jPN', 'fee': '0.5'},
            'V99': {'wallet': 'TRX_Wallet_V99', 'fee': '1.5'}
        }
    }

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if 'merchants' not in data: data = {'my_wallet': '', 'merchants': data}
                return data
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

def copy_box(text, color_type="blue", box_id="default"):
    colors = {
        "blue": {"border": "#4a90d9", "bg": "#060d18", "text": "#a8c7e8"},
        "green": {"border": "#27ae60", "bg": "#06180d", "text": "#7dcea0"},
        "yellow": {"border": "#f39c12", "bg": "#181406", "text": "#f8c471"},
        "red": {"border": "#e74c3c", "bg": "#180606", "text": "#f1948a"}
    }
    c = colors.get(color_type, colors["blue"])
    js_text = json.dumps(text)
    line_count = text.count("\n") + 1
    box_height = max(100, line_count * 25 + 60)
    html_code = f"""
    <div style="position:relative; background:{c['bg']}; border:1px solid #1e3a5f; border-left:4px solid {c['border']}; 
                border-radius:6px; padding:15px; font-family:monospace; font-size:14px; line-height:1.6; color:{c['text']};">
        <button onclick="copyToClipboard(this)" style="position:absolute; top:10px; right:10px; background:#0f2040; color:#5dade2; 
                border:1px solid #1e3a5f; border-radius:4px; padding:4px 8px; cursor:pointer; font-size:11px;">📋 복사</button>
        <pre style="margin:0; white-space:pre-wrap; word-break:break-all; font-family:inherit;">{text}</pre>
    </div>
    <script>
    function copyToClipboard(btn) {{
        const text = {js_text};
        const el = document.createElement('textarea'); el.value = text; document.body.appendChild(el);
        el.select(); document.execCommand('copy'); document.body.removeChild(el);
        btn.innerText = '✅ 완료';
        setTimeout(() => {{ btn.innerText = '📋 복사'; }}, 1000);
    }}
    </script>
    """
    components.html(html_code, height=box_height, key=f"cbox_{box_id}")

st.set_page_config(page_title="정산 매크로 v93.0", layout="centered")

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #0a0e17 !important; color: #c8d6e5 !important; }
    div[data-baseweb="input"], div[data-baseweb="textarea"] { background-color: #ffffff !important; border-radius: 6px !important; }
    input, textarea { 
        color: #d4ac0d !important; 
        -webkit-text-fill-color: #d4ac0d !important;
        font-weight: bold !important; 
        font-family: monospace !important; 
        font-size: 1.2em !important; 
    }
    .label-header { color: #4a90d9; font-weight: bold; font-size: 1.25em; border-bottom: 2px solid #1e2d45; padding-bottom: 8px; margin-top: 35px; margin-bottom: 15px; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

if 'db' not in st.session_state: st.session_state.db = load_data()
if 'page' not in st.session_state: st.session_state.page = 'settle'

with st.sidebar:
    st.title("💹 SETTLEMENT")
    if st.button("🚀 정산 작업"): st.session_state.page = 'settle'; st.rerun()
    if st.button("⚙️ 머천트 관리"): st.session_state.page = 'admin'; st.rerun()

if st.session_state.page == 'settle':
    st.title("🚀 실시간 정산 작업")
    merchants = st.session_state.db['merchants']
    sorted_keys = sorted(list(merchants.keys()))
    default_idx = sorted_keys.index('spfxm') if 'spfxm' in sorted_keys else 0
    selected_m = st.selectbox("업체 선택", sorted_keys, index=default_idx)
    m_info = merchants[selected_m]
    
    st.markdown('<div class="label-header">01. 환율 설정</div>', unsafe_allow_html=True)
    sel_p = st.radio("적용 배수", ["4%", "4.5%", "5%"], index=0, horizontal=True)
    m_map = {"4%": 1.04, "4.5%": 1.045, "5%": 1.05}
    c1, c2 = st.columns(2)
    with c1: b_val = extract_int(st.text_input("빗썸 시세", key="b_v_in"))
    with c2: s_val = extract_int(st.text_input("수동 환율", key="s_v_in"))
    rate = s_val if s_val > 0 else math.ceil(b_val * m_map[sel_p])
    if rate > 0: copy_box(f"1 USDT = {fmt(rate)} KRW", "blue", box_id="rate")

    st.markdown('<div class="label-header">02. 정산 요청</div>', unsafe_allow_html=True)
    amount = extract_int(st.text_input("정산 금액 (KRW)", key="amt_v_in"))
    edit_msg = st.text_area("멘트 수정", value="Please confirm the address and calculation.\nOnce approved, we will proceed immediately", height=80, key="msg_v_in")
    if amount > 0:
        u_val = round(amount / rate, 2)
        s_msg = f"- {selected_m} settlement amount : {fmt(amount)} krw\n- exchange to usdt : {u_val:,.2f} usdt\n- 1usdt = {fmt(rate)} krw\n\n{m_info['wallet']}\n\n{edit_msg}"
        copy_box(s_msg, "blue", box_id="settle")

    st.markdown('<div class="label-header">03. 최종 잔액 보고</div>', unsafe_allow_html=True)
    bal_in = extract_int(st.text_input("현재 잔액 입력 (KRW)", key="bal_v_in"))
    if bal_in > 0 and amount > 0:
        u_ceil = math.ceil(amount / rate)
        b_msg = f"Balance & settlement update\n\n- {selected_m}\nsettlement amount : {fmt(amount)} krw\nexchange to usdt : {fmt(u_ceil)} usdt\n1usdt = {fmt(rate)} krw\n\n- {selected_m} : {fmt(bal_in)} krw"
        copy_box(b_msg, "green", box_id="balance")

    st.markdown('<div class="label-header">04. 마크업 수수료</div>', unsafe_allow_html=True)
    m_fee = float(m_info.get('fee', 0.5))
    markup = math.ceil(amount * (m_fee / 100))
    if amount > 0:
        copy_box(f"드래곤 테더정산 마크업 {m_fee}% {selected_m} / {fmt(amount)} / {fmt(markup)}", "yellow", box_id="markup")

    st.divider()
    st.markdown('<div class="label-header" style="color:#2ecc71;">06. TOP-UP 요청</div>', unsafe_allow_html=True)
    cl, cr = st.columns(2) 
    with cl: tm_rate = extract_int(st.text_input("탑업 시세", key="tm_v_in"))
    with cr: t_usdt = extract_int(st.text_input("탑업 USDT", key="tu_v_in"))
    t_rate = tm_rate - math.ceil(tm_rate * 0.005) if tm_rate > 0 else 0
    if t_usdt > 0 and t_rate > 0:
        my_w = st.session_state.db.get('my_wallet', '')
        copy_box(f"top-up\n\nmid : {selected_m}\ntop-up amount : {fmt(t_usdt)} usdt\nexchange to KRW : {fmt(t_usdt * t_rate)} krw\n1usdt = {fmt(t_rate)} krw\n\n{my_w}\n\nPlease check...", "green", box_id="topup")

elif st.session_state.page == 'admin':
    st.title("⚙️ 머천트 및 내 지갑 관리")
    st.subheader("💳 내 USDT 지갑 (Top-up용)")
    my_w = st.text_input("지갑 주소", value=st.session_state.db.get('my_wallet', ''), key="my_w_admin")
    if st.button("저장하기", key="save_my_w"):
        st.session_state.db['my_wallet'] = my_w
        save_data(st.session_state.db); st.success("저장 완료!")
    st.divider()
    with st.form("new_m_admin"):
        st.subheader("➕ 신규 업체 등록")
        n_name = st.text_input("업체 이름")
        n_wallet = st.text_input("업체 지갑 주소")
        n_fee = st.text_input("마크업 요율 (%)", value="0.5")
        if st.form_submit_button("등록"):
            if n_name and n_wallet:
                st.session_state.db['merchants'][n_name] = {"wallet": n_wallet, "fee": n_fee}
                save_data(st.session_state.db); st.rerun()
    st.divider()
    for name in sorted(st.session_state.db['merchants'].keys()):
        with st.expander(f"📦 {name}"):
            info = st.session_state.db['merchants'][name]
            u_w = st.text_input("지갑", value=info['wallet'], key=f"w_{name}_admin")
            u_f = st.text_input("요율", value=info['fee'], key=f"f_{name}_admin")
            if st.button("저장", key=f"s_{name}_admin"):
                st.session_state.db['merchants'][name] = {"wallet": u_w, "fee": u_f}
                save_data(st.session_state.db); st.rerun()
            if st.button("삭제", key=f"d_{name}_admin"):
                del st.session_state.db['merchants'][name]
                save_data(st.session_state.db); st.rerun()
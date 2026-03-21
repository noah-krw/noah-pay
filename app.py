# -*- coding: utf-8 -*-
import streamlit as st
import streamlit.components.v1 as components
import math, json, os, re

# ============================================================
# 정산 매크로 v92.3 - Noah 실장님 퇴근 보장 최종 복구본
# ============================================================

DB_FILE = "merchants_v2.json"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    # 데이터 유실 대비 강제 복구용 기본값
    return {
        'my_wallets': {'tl': 'TDaQt8oASZhVsuaEdpevqCacGKseGKCWhQ', 'ada': ''}, 
        'merchants': {
            'spfxm': {'wallet': 'TWbFbzW5GRkAkVrY4fLuXhNA576DCkoGbh', 'fee': '4', 'memo': '주력'},
            'V99': {'wallet': 'TRX_Wallet_V99_Address', 'fee': '3', 'memo': '기존'},
            'dr188': {'wallet': 'TRX_Wallet_dr188_Address', 'fee': '3', 'memo': '드래곤'}
        }
    }

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def extract_int(text):
    if not text: return 0
    num_str = re.sub(r'[^0-9]', '', str(text))
    return int(num_str) if num_str else 0

def fmt(n): return f"{n:,}"

def copy_box(text, color_type="blue", key=None):
    colors = {"blue": "#4a90d9", "green": "#27ae60", "yellow": "#f39c12", "red": "#e74c3c"}
    bg_colors = {"blue": "#060d18", "green": "#06180d", "yellow": "#181406", "red": "#180606"}
    c, bg = colors.get(color_type, "#4a90d9"), bg_colors.get(color_type, "#060d18")
    line_count = text.count("\n") + 1
    box_height = (line_count * 25) + 60
    st.markdown(f"""<style>.stTextArea textarea[key="{key}"] {{ background-color: {bg} !important; color: {c} !important; border-left: 4px solid {c} !important; font-family: monospace !important; font-size: 15px !important; line-height: 1.6 !important; }}</style>""", unsafe_allow_html=True)
    edited_text = st.text_area("수정", value=text, height=box_height, key=key, label_visibility="collapsed")
    if st.button("📋 복사", key=f"btn_{key}"):
        js = f"<script>navigator.clipboard.writeText(`{edited_text}`);</script>"
        components.html(js, height=0); st.toast("복사 완료!")

st.set_page_config(page_title="정산 매크로 v92.3", layout="centered")

# --- Noah 실장님 지향 깔끔 다크 UI ---
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #0e1117 !important; color: #ffffff !important; }
    input { color: #f1c40f !important; -webkit-text-fill-color: #f1c40f !important; font-weight: bold !important; font-size: 1.1rem !important; }
    div[data-baseweb="select"] > div { background-color: #1c2331 !important; color: #f1c40f !important; }
    h3 { color: #4a90d9; border-bottom: 2px solid #34495e; padding-bottom: 5px; margin-top: 25px; }
    div[role="radiogroup"] { display: flex; gap: 10px; background: transparent !important; }
    div[role="radiogroup"] label { background-color: #2c3e50 !important; padding: 10px 25px !important; border-radius: 5px !important; color: white !important; font-weight: bold !important; }
    div[data-checked="true"] { background-color: #4a90d9 !important; }
</style>
""", unsafe_allow_html=True)

if 'db' not in st.session_state: st.session_state.db = load_data()
if 'page' not in st.session_state: st.session_state.page = 'settle'

with st.sidebar:
    st.title("💹 SETTLEMENT")
    if st.button("🚀 정산 작업"): st.session_state.page = 'settle'; st.rerun()
    if st.button("⚙️ 머천트 설정"): st.session_state.page = 'admin'; st.rerun()
    st.divider()
    if st.button("🔄 데이터 강제 복구"): 
        st.session_state.db = load_data()
        save_data(st.session_state.db)
        st.success("데이터 복구 완료!"); st.rerun()

if st.session_state.page == 'settle':
    merchants = st.session_state.db.get('merchants', {})
    m_list = sorted(list(merchants.keys()))
    if 'spfxm' in m_list:
        m_list.remove('spfxm'); m_list.insert(0, 'spfxm')
    
    if not m_list:
        st.warning("데이터 복구 버튼을 눌러주세요."); st.stop()

    selected_m = st.selectbox("🏢 업체 선택", m_list)
    m_info = merchants[selected_m]
    m_fee = float(m_info.get('fee', 0.5))

    st.markdown("### 01. 환율 설정")
    m_map = {"4%": 1.04, "4.5%": 1.045, "5%": 1.05}
    sel_label = st.radio("배수", list(m_map.keys()), horizontal=True, label_visibility="collapsed")
    c1, c2 = st.columns(2)
    with c1: b_val = extract_int(st.text_input("빗썸 시세"))
    with c2: s_val = extract_int(st.text_input("수동 환율"))
    rate = s_val if s_val > 0 else math.ceil(b_val * m_map[sel_label])
    if rate > 0: copy_box(f"1 USDT = {fmt(rate)} KRW", "blue", key="r_res")

    st.markdown("### 02. 정산 요청")
    amt = extract_int(st.text_input("정산 금액 (KRW)"))
    if amt > 0:
        u_val = round(amt / rate, 2)
        msg = f"- {selected_m} settlement amount : {fmt(amt)} krw\n- exchange to usdt : {u_val:,.2f} usdt\n- 1usdt = {fmt(rate)} krw\n\n{m_info['wallet']}\n\nPlease confirm the address and calculation. Once approved, we will proceed immediately."
        copy_box(msg, "blue", key="s_res")
        
        markup = math.ceil(amt * (m_fee / 100))
        copy_box(f"드래곤 테더정산 마크업 {m_fee}% {selected_m} / {fmt(amt)} / {fmt(markup)}", "yellow", key="f_res")

    st.markdown("### 03. 잔액 및 경고")
    c3, c4 = st.columns(2)
    with c3: bal_in = extract_int(st.text_input("업데이트 잔액"))
    with c4: warn_in = extract_int(st.text_input("경고용 잔액"))
    if bal_in > 0:
        copy_box(f"Balance & settlement update\n\n- {selected_m}\nsettlement amount : {fmt(amt)} krw\nexchange to usdt : {fmt(math.ceil(amt/rate))} usdt\n1usdt = {fmt(rate)} krw\n\n- {selected_m} : {fmt(bal_in)} krw", "green", key="b_res")
    if warn_in > 0:
        copy_box(f"Hello, Team\nCurrently, the balance of the merchants is too high.\nTo ensure a safe balance, please proceed with USDT settlement.\nThank you\n\nBalance update\n\n- {selected_m} : {fmt(warn_in)} krw", "red", key="w_res")

elif st.session_state.page == 'admin':
    st.title("⚙️ 머천트 설정")
    # 업체 추가 폼
    with st.expander("➕ 새 업체 추가", expanded=True):
        new_name = st.text_input("업체명")
        new_wallet = st.text_input("지갑 주소")
        new_fee = st.text_input("마크업 요율 (%)", value="0.5")
        new_memo = st.text_input("비고")
        if st.button("저장하기"):
            st.session_state.db['merchants'][new_name] = {'wallet': new_wallet, 'fee': new_fee, 'memo': new_memo}
            save_data(st.session_state.db); st.rerun()

    st.divider()
    # 업체 리스트 및 삭제
    for name, info in list(st.session_state.db['merchants'].items()):
        c1, c2 = st.columns([4, 1])
        with c1: st.write(f"**{name}** ({info['fee']}%) - {info['wallet']}")
        with c2: 
            if st.button("삭제", key=f"del_{name}"):
                del st.session_state.db['merchants'][name]
                save_data(st.session_state.db); st.rerun()
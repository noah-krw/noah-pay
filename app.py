import streamlit as st
import math
import json
import os
import re

# [정산 매크로 v76 - Noah 전용: 머천트 추가/삭제/알림 강화 버전]

DB_FILE = "merchants.json"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    # 기본 리스트 (Noah가 언급한 업체들 우선 등록)
    return {
        'dr188': {'wallet': 'TRX_Wallet_dr188', 'fee': '0.5'},
        'drgtssen': {'wallet': 'TRX_Wallet_drgtssen', 'fee': '0.5'},
        'Dpinnacle': {'wallet': 'TRX_Wallet_Dpinnacle', 'fee': '0.5'},
        'drSpinmama': {'wallet': 'TRX_Wallet_drSpinmama', 'fee': '0.5'},
        'drbetssen': {'wallet': 'TRX_Wallet_drbetssen', 'fee': '0.5'}
    }

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def extract_int(text):
    num_str = re.sub(r'[^0-9]', '', text)
    return int(num_str) if num_str else 0

st.set_page_config(page_title="정산 매크로 v76", layout="centered")

st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] { background-color: #1e1e1e !important; color: #e0e0e0 !important; }
    div[data-baseweb="input"] { background-color: #2d2d2d !important; border: 1px solid #444 !important; }
    input { color: #f1c40f !important; font-size: 1.1em !important; font-weight: bold !important; }
    .stButton>button { width: 100%; border-radius: 4px; background-color: #34495e; color: white; border: none; font-weight: bold; height: 45px; }
    .m-header { background-color: #000; color: #ffffff; padding: 10px; border-radius: 4px; text-align: center; margin-bottom: 20px; border: 1px solid #333; font-size: 1.1em; font-weight: bold; }
    .label { color: #5dade2; font-weight: bold; margin-top: 15px; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

if 'db' not in st.session_state:
    st.session_state.db = load_data()

if 'page' not in st.session_state:
    st.session_state.page = 'settle'

with st.sidebar:
    st.title("메뉴")
    if st.button("🚀 정산 작업"): st.session_state.page = 'settle'
    if st.button("⚙️ 머천트 설정"): st.session_state.page = 'admin'

if st.session_state.page == 'settle':
    st.title("🚀 실시간 정산 작업")
    selected_m = st.selectbox("업체 선택", list(st.session_state.db.keys()))
    m_info = st.session_state.db.get(selected_m, {"wallet": "-", "fee": "0.5"})
    st.markdown(f'<div class="m-header">{selected_m} 정산 모드</div>', unsafe_allow_html=True)

    st.markdown('<p class="label">1. 환율 설정</p>', unsafe_allow_html=True)
    rate_choice = st.radio("배수", ["4%", "4.5%", "5%"], index=1, horizontal=True, label_visibility="collapsed")
    multiplier = 1.04 if rate_choice == "4%" else 1.045 if rate_choice == "4.5%" else 1.05

    c1, c2 = st.columns(2)
    with c1: b_val = extract_int(st.text_input("빗썸 시세", value="0", key="bithumb"))
    with c2: s_val = extract_int(st.text_input("수동 환율", value="0", key="manual"))
    
    current_rate = s_val if s_val > 0 else math.ceil(b_val * multiplier)
    st.code(f"1 USDT = {current_rate:,} KRW", language="text")

    st.markdown('<p class="label">2. 정산 문구</p>', unsafe_allow_html=True)
    amount = extract_int(st.text_input("정산 금액", value="0", key="amt_in"))
    if amount > 0:
        usdt_val = round(amount / current_rate, 2)
        confirm_msg = (
            f"- {selected_m} settlement amount : {amount:,} krw\n"
            f"- exchange to usdt : {usdt_val:,.2f} usdt\n"
            f"- 1usdt = {current_rate:,} krw\n\n"
            f"{m_info['wallet']}\n\n"
            f"Please confirm the address and calculation.\n"
            f"Once approved, we will proceed immediately"
        )
        st.code(confirm_msg, language="text")

    st.markdown('<p class="label">3. 최종 잔액 보고</p>', unsafe_allow_html=True)
    balance = extract_int(st.text_input("잔액 입력", value="0", key="bal_in"))
    if balance > 0 and amount > 0:
        final_msg = (
            f"Balance & settlement update\n\n- {selected_m}\nsettlement amount : {amount:,} krw\nexchange to usdt : {math.ceil(amount / current_rate):,} usdt\n1usdt = {current_rate:,} krw\n\n- {selected_m} : {balance:,} krw"
        )
        st.code(final_msg, language="text")

    st.markdown('<p class="label">4. 게이트 수수료</p>', unsafe_allow_html=True)
    if st.button("수수료 멘트 생성"):
        if amount > 0:
            f_val = float(m_info.get('fee', 0.5))
            fee_krw = int(amount * f_val / 100)
            fee_msg = f"드래곤 테더정산 수수료 {f_val}% {selected_m} / {amount:,} / {fee_krw:,}"
            st.code(fee_msg, language="text")

else:
    st.title("⚙️ 머천트 설정 관리")
    
    # 1. 신규 추가 섹션
    with st.form("add_merchant_form"):
        st.subheader("➕ 새 머천트 추가")
        new_name = st.text_input("업체 이름 (예: drgtkore)")
        new_wallet = st.text_input("지갑 주소")
        new_fee = st.text_input("요율 (%)", value="0.5")
        if st.form_submit_button("신규 업체 등록"):
            if new_name and new_wallet:
                st.session_state.db[new_name] = {"wallet": new_wallet, "fee": new_fee}
                save_data(st.session_state.db)
                st.success(f"✅ {new_name} 업체가 성공적으로 등록되었습니다!")
                st.rerun()
            else:
                st.error("이름과 지갑 주소를 모두 입력해주세요.")

    st.divider()

    # 2. 기존 업체 수정 및 삭제
    st.subheader("📂 기존 업체 관리")
    for name, info in list(st.session_state.db.items()):
        with st.expander(f"🏢 {name} 정보 수정"):
            u_wallet = st.text_input(f"지갑 주소", value=info['wallet'], key=f"w_{name}")
            u_fee = st.text_input(f"요율 (%)", value=info['fee'], key=f"f_{name}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"{name} 저장", key=f"s_{name}"):
                    st.session_state.db[name] = {"wallet": u_wallet, "fee": u_fee}
                    save_data(st.session_state.db)
                    st.success(f"✅ {name} 정보가 업데이트되었습니다!")
                    st.rerun()
            with col2:
                if st.button(f"🗑️ {name} 삭제", key=f"d_{name}"):
                    del st.session_state.db[name]
                    save_data(st.session_state.db)
                    st.warning(f"⚠️ {name} 업체가 삭제되었습니다.")
                    st.rerun()
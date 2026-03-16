import streamlit as st
import math
import json
import os
import re

# [정산 매크로 v76 - Noah 커스텀: 환율 선택 기능 추가]

DB_FILE = "merchants.json"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return {
        'spfxm': {'wallet': 'TRX_Wallet_Example_1', 'fee': '0.5'},
        'V99': {'wallet': 'TRX_Wallet_Example_2', 'fee': '1.5'}
    }

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def extract_int(text):
    num_str = re.sub(r'[^0-9]', '', text)
    return int(num_str) if num_str else 0

st.set_page_config(page_title="정산 매크로 v76", layout="centered")

# CSS: 기존 v76 스타일 유지
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] { background-color: #1e1e1e !important; color: #e0e0e0 !important; }
    div[data-baseweb="input"] { background-color: #2d2d2d !important; border: 1px solid #444 !important; }
    input { color: #f1c40f !important; font-size: 1.2em !important; font-weight: bold !important; }
    .stButton>button { width: 100%; border-radius: 4px; background-color: #34495e; color: white; border: none; font-weight: bold; }
    .m-header { background-color: #000; color: #ffffff; padding: 12px; border-radius: 4px; text-align: center; margin-bottom: 20px; border: 1px solid #333; font-size: 1.2em; font-weight: bold; }
    .label { color: #5dade2; font-weight: bold; margin-top: 15px; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

db = load_data()

if 'page' not in st.session_state:
    st.session_state.page = 'settle'

# ---------------------------------------------------------
# 사이드바: 환율 선택 기능 추가
# ---------------------------------------------------------
with st.sidebar:
    st.title("메뉴 바로가기")
    if st.button("🚀 실시간 정산 작업"):
        st.session_state.page = 'settle'
    if st.button("⚙️ 머천트 설정 관리"):
        st.session_state.page = 'admin'
    
    st.markdown("---")
    st.subheader("💡 환율 배수 선택")
    rate_option = st.radio(
        "적용할 KP를 선택하세요",
        ("4% (1.04)", "4.5% (1.045)", "5% (1.05)"),
        index=1 # 기본값 4.5%
    )
    
    if "4.5%" in rate_option:
        kp_multiplier = 1.045
    elif "4%" in rate_option:
        kp_multiplier = 1.04
    else:
        kp_multiplier = 1.05

# ---------------------------------------------------------
# 페이지 1: 정산 작업창 (기존 디자인 유지)
# ---------------------------------------------------------
if st.session_state.page == 'settle':
    st.title("🚀 실시간 정산 작업")
    selected_m = st.selectbox("정산 업체 선택", list(db.keys()))
    m_info = db.get(selected_m, {"wallet": "-", "fee": "0.5"})
    st.markdown(f'<div class="m-header">{selected_m} 정산 모드</div>', unsafe_allow_html=True)

    # 1. 환율
    st.markdown('<p class="label">1. 환율 설정</p>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        b_raw = st.text_input("빗썸 시세", value="0", key="bithumb")
        b_val = extract_int(b_raw)
    with c2:
        s_raw = st.text_input("수동 환율", value="0", key="manual")
        s_val = extract_int(s_raw)
    
    # 사이드바에서 선택한 배수 적용
    current_rate = s_val if s_val > 0 else math.ceil(b_val * kp_multiplier)
    st.code(f"1usdt = {current_rate:,} krw (배수: {kp_multiplier})", language="text")

    # 2. 정산 문구
    st.markdown('<p class="label">2. 정산 금액 (KRW)</p>', unsafe_allow_html=True)
    amt_raw = st.text_input("정산 금액", value="0", key="amt_in")
    amount = extract_int(amt_raw)
    if amount > 0:
        usdt_val = round(amount / current_rate, 2)
        confirm_msg = f"- {selected_m} settlement amount : {amount:,} krw\n- exchange to usdt : {usdt_val:,.2f} usdt\n- 1usdt = {current_rate:,} krw\n\n{m_info['wallet']}\n\nPlease confirm the address and calculation."
        st.code(confirm_msg, language="text")

    # 3. 잔액 보고
    st.markdown('<p class="label">3. 최종 잔액 보고</p>', unsafe_allow_html=True)
    bal_raw = st.text_input("잔액 입력", value="0", key="bal_in")
    balance = extract_int(bal_raw)
    if balance > 0 and amount > 0:
        final_msg = f"Balance & settlement update\n\n- {selected_m}\nsettlement amount : {amount:,} krw\nexchange to usdt : {math.ceil(amount / current_rate):,} usdt\n1usdt = {current_rate:,} krw\n\n- {selected_m} : {balance:,} krw"
        st.code(final_msg, language="text")

    # 4. 수수료
    if st.button("게이트 수수료 멘트 생성"):
        if amount > 0:
            f_val = float(m_info.get('fee', 0.5))
            fee_krw = int(amount * f_val / 100)
            st.code(f"드래곤 테더정산 수수료 {f_val}% {selected_m} / {amount:,} / {fee_krw:,}", language="text")

# ---------------------------------------------------------
# 페이지 2: 머천트 설정 관리
# ---------------------------------------------------------
else:
    st.title("⚙️ 머천트 설정 관리")
    # ... (기존과 동일한 관리 코드)
    for name, info in list(db.items()):
        with st.expander(f"🏢 {name} 수정/삭제"):
            u_wallet = st.text_input(f"지갑 주소", value=info['wallet'], key=f"w_{name}")
            u_fee = st.text_input(f"요율 (%)", value=info['fee'], key=f"f_{name}")
            c1, c2 = st.columns(2)
            with c1:
                if st.button(f"{name} 저장", key=f"s_{name}"):
                    db[name] = {"wallet": u_wallet, "fee": u_fee}
                    save_data(db)
                    st.success("저장 완료!")
                    st.rerun()
            with c2:
                if st.button(f"{name} 삭제", key=f"d_{name}"):
                    del db[name]
                    save_data(db)
                    st.warning("삭제 완료!")
                    st.rerun()
    st.markdown("---")
    with st.expander("➕ 새 머천트 추가"):
        new_name = st.text_input("신규 업체명 (영문)")
        new_wallet = st.text_input("신규 지갑 주소")
        new_fee = st.text_input("기본 수수료 (%)", value="0.5")
        if st.button("업체 등록"):
            if new_name:
                db[new_name] = {"wallet": new_wallet, "fee": new_fee}
                save_data(db)
                st.success(f"{new_name} 등록 완료!")
                st.rerun()
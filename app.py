import streamlit as st
import math
import json
import os
import re

# [정산 매크로 v76 - Noah 전용: 머천트 풀세팅 및 관리 UI 강화 버전]

DB_FILE = "merchants.json"

def load_data():
    # Noah가 준 모든 업체 정보 기본 세팅
    default_list = {
        'dr188': {'wallet': 'TBMTb9TFFXDuqhjLKLp9Yo26QHRnnG6jPN', 'fee': '0.5'},
        'drgtssen': {'wallet': 'TRX_Wallet_drgtssen', 'fee': '0.5'},
        'Dpinnacle': {'wallet': 'TRX_Wallet_Dpinnacle', 'fee': '0.5'},
        'drSpinmama': {'wallet': 'TRX_Wallet_drSpinmama', 'fee': '0.5'},
        'drbetssen': {'wallet': 'TRX_Wallet_drbetssen', 'fee': '0.5'},
        'NextbetM/G': {'wallet': 'TRX_Wallet_Nextbet', 'fee': '0.5'},
        'DafabetM/G': {'wallet': 'TRX_Wallet_Dafabet', 'fee': '0.5'},
        'drgtkore': {'wallet': 'TRX_Wallet_drgtkore', 'fee': '0.5'},
        'drolymp': {'wallet': 'TRX_Wallet_drolymp', 'fee': '0.5'},
        'drbetkore': {'wallet': 'TRX_Wallet_drbetkore', 'fee': '0.5'},
        'drTapTap': {'wallet': 'TRX_Wallet_drTapTap', 'fee': '0.5'},
        'spfxm': {'wallet': 'TRX_Wallet_spfxm', 'fee': '0.5'},
        'V99': {'wallet': 'TRX_Wallet_V99', 'fee': '1.5'}
    }
    
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return default_list

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def extract_int(text):
    num_str = re.sub(r'[^0-9]', '', text)
    return int(num_str) if num_str else 0

st.set_page_config(page_title="정산 매크로 v76", layout="centered")

# CSS: 저장/삭제 버튼 색상 및 레이아웃
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] { background-color: #1e1e1e !important; color: #e0e0e0 !important; }
    div[data-baseweb="input"] { background-color: #2d2d2d !important; border: 1px solid #444 !important; }
    input { color: #f1c40f !important; font-size: 1.1em !important; font-weight: bold !important; }
    .m-header { background-color: #000; color: #ffffff; padding: 10px; border-radius: 4px; text-align: center; margin-bottom: 20px; border: 1px solid #333; font-size: 1.1em; font-weight: bold; }
    .label { color: #5dade2; font-weight: bold; margin-top: 15px; margin-bottom: 5px; }
    
    /* 버튼 스타일 커스텀 */
    div.stButton > button:first-child { width: 100%; height: 45px; font-weight: bold; border-radius: 5px; border: none; }
    .btn-save > div.stButton > button { background-color: #007bff !important; color: white !important; } /* 파란색 저장 */
    .btn-del > div.stButton > button { background-color: #dc3545 !important; color: white !important; } /* 빨간색 삭제 */
    .btn-add > div.stButton > button { background-color: #28a745 !important; color: white !important; } /* 초록색 추가 */
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
    sorted_keys = sorted(list(st.session_state.db.keys()))
    selected_m = st.selectbox("업체 선택", sorted_keys)
    m_info = st.session_state.db.get(selected_m, {"wallet": "-", "fee": "0.5"})
    st.markdown(f'<div class="m-header">{selected_m} 정산 모드</div>', unsafe_allow_html=True)

    # 1. 환율 설정
    st.markdown('<p class="label">1. 환율 설정</p>', unsafe_allow_html=True)
    rate_choice = st.radio("배수", ["4%", "4.5%", "5%"], index=1, horizontal=True, label_visibility="collapsed")
    multiplier = 1.04 if rate_choice == "4%" else 1.045 if rate_choice == "4.5%" else 1.05
    c1, c2 = st.columns(2)
    with c1: b_val = extract_int(st.text_input("빗썸 시세", value="0", key="bithumb"))
    with c2: s_val = extract_int(st.text_input("수동 환율", value="0", key="manual"))
    current_rate = s_val if s_val > 0 else math.ceil(b_val * multiplier)
    st.code(f"1 USDT = {current_rate:,} KRW", language="text")

    # 2. 정산 문구
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

    # 3. 최종 잔액 보고
    st.markdown('<p class="label">3. 최종 잔액 보고</p>', unsafe_allow_html=True)
    balance = extract_int(st.text_input("잔액 입력", value="0", key="bal_in"))
    if balance > 0 and amount > 0:
        final_msg = f"Balance & settlement update\n\n- {selected_m}\nsettlement amount : {amount:,} krw\nexchange to usdt : {math.ceil(amount / current_rate):,} usdt\n1usdt = {current_rate:,} krw\n\n- {selected_m} : {balance:,} krw"
        st.code(final_msg, language="text")

    # 4. 게이트 수수료
    st.markdown('<p class="label">4. 게이트 수수료</p>', unsafe_allow_html=True)
    if st.button("수수료 멘트 생성"):
        if amount > 0:
            f_val = float(m_info.get('fee', 0.5))
            fee_krw = int(amount * f_val / 100)
            fee_msg = f"드래곤 테더정산 수수료 {f_val}% {selected_m} / {amount:,} / {fee_krw:,}"
            st.code(fee_msg, language="text")

else:
    st.title("⚙️ 머천트 설정 관리")
    
    # 신규 등록
    with st.form("new_m"):
        st.subheader("➕ 신규 업체 등록")
        n_name = st.text_input("업체 이름")
        n_wallet = st.text_input("지갑 주소")
        n_fee = st.text_input("요율 (%)", value="0.5")
        st.markdown('<div class="btn-add">', unsafe_allow_html=True)
        if st.form_submit_button("신규 업체 등록 완료"):
            if n_name and n_wallet:
                st.session_state.db[n_name] = {"wallet": n_wallet, "fee": n_fee}
                save_data(st.session_state.db)
                st.success(f"✅ {n_name} 등록 성공!")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    # 업체 수정/삭제
    st.subheader("📂 업체 목록 수정")
    for name in sorted(list(st.session_state.db.keys())):
        info = st.session_state.db[name]
        with st.expander(f"🏢 {name}"):
            u_w = st.text_input("지갑 주소", value=info['wallet'], key=f"w_{name}")
            u_f = st.text_input("요율 (%)", value=info['fee'], key=f"f_{name}")
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown('<div class="btn-save">', unsafe_allow_html=True)
                if st.button("저장", key=f"s_{name}"):
                    st.session_state.db[name] = {"wallet": u_w, "fee": u_f}
                    save_data(st.session_state.db)
                    st.success(f"✅ {name} 저장 완료!")
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            with c2:
                st.markdown('<div class="btn-del">', unsafe_allow_html=True)
                if st.button("삭제", key=f"d_{name}"):
                    del st.session_state.db[name]
                    save_data(st.session_state.db)
                    st.warning(f"⚠️ {name} 삭제 완료.")
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
import streamlit as st
import math
import json
import os
import re

# [정산 매크로 v76 - Noah 전용: 이름 변경/비고란/UI 최적화 버전]

DB_FILE = "merchants.json"

def load_data():
    full_list = {
        'dr188': {'wallet': 'TBMTb9TFFXDuqhjLKLp9Yo26QHRnnG6jPN', 'fee': '0.5', 'note': '드래곤 메인'},
        'drgtssen': {'wallet': 'TRX_Wallet_drgtssen', 'fee': '0.5', 'note': ''},
        'Dpinnacle': {'wallet': 'TRX_Wallet_Dpinnacle', 'fee': '0.5', 'note': ''},
        'drSpinmama': {'wallet': 'TRX_Wallet_drSpinmama', 'fee': '0.5', 'note': ''},
        'drbetssen': {'wallet': 'TRX_Wallet_drbetssen', 'fee': '0.5', 'note': ''},
        'NextbetM/G': {'wallet': 'TRX_Wallet_Nextbet', 'fee': '0.5', 'note': ''},
        'DafabetM/G': {'wallet': 'TRX_Wallet_Dafabet', 'fee': '0.5', 'note': ''},
        'drgtkore': {'wallet': 'TRX_Wallet_drgtkore', 'fee': '0.5', 'note': ''},
        'drolymp': {'wallet': 'TRX_Wallet_drolymp', 'fee': '0.5', 'note': ''},
        'drbetkore': {'wallet': 'TRX_Wallet_drbetkore', 'fee': '0.5', 'note': ''},
        'drTapTap': {'wallet': 'TRX_Wallet_drTapTap', 'fee': '0.5', 'note': ''},
        'spfxm': {'wallet': 'TRX_Wallet_spfxm', 'fee': '0.5', 'note': '기존 관리 업체'},
        'V99': {'wallet': 'TRX_Wallet_V99', 'fee': '1.5', 'note': 'VVIP 전용'}
    }
    if not os.path.exists(DB_FILE):
        save_data(full_list)
        return full_list
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            db = json.load(f)
            # 호환성을 위해 note 필드 없는 경우 추가
            for k in db:
                if 'note' not in db[k]: db[k]['note'] = ''
            return db
    except:
        return full_list

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
    .m-header { background-color: #000; color: #ffffff; padding: 10px; border-radius: 4px; text-align: center; margin-bottom: 20px; border: 1px solid #333; font-size: 1.1em; font-weight: bold; }
    .label { color: #5dade2; font-weight: bold; margin-top: 15px; margin-bottom: 5px; }
    
    /* 업체명 굵게 */
    .stExpander p { font-weight: bold !important; font-size: 1.1em !important; }
    
    /* 버튼 스타일 및 정렬 */
    div.stButton > button { width: 100%; height: 40px; font-weight: bold; border-radius: 5px; border: none; }
    .btn-save button { background-color: #007bff !important; color: white !important; }
    .btn-del button { background-color: #dc3545 !important; color: white !important; border: 1px solid #dc3545 !important; }
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
    m_info = st.session_state.db.get(selected_m)
    
    st.markdown(f'<div class="m-header">{selected_m} 정산 모드</div>', unsafe_allow_html=True)
    if m_info.get('note'):
        st.info(f"📌 비고: {m_info['note']}")

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
        confirm_msg = f"- {selected_m} settlement amount : {amount:,} krw\n- exchange to usdt : {usdt_val:,.2f} usdt\n- 1usdt = {current_rate:,} krw\n\n{m_info['wallet']}\n\nPlease confirm the address and calculation.\nOnce approved, we will proceed immediately"
        st.code(confirm_msg, language="text")

    st.markdown('<p class="label">3. 최종 잔액 보고</p>', unsafe_allow_html=True)
    balance = extract_int(st.text_input("잔액 입력", value="0", key="bal_in"))
    if balance > 0 and amount > 0:
        final_msg = f"Balance & settlement update\n\n- {selected_m}\nsettlement amount : {amount:,} krw\nexchange to usdt : {math.ceil(amount / current_rate):,} usdt\n1usdt = {current_rate:,} krw\n\n- {selected_m} : {balance:,} krw"
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
    
    # 신규 등록
    with st.form("new_m", clear_on_submit=True):
        st.subheader("➕ 신규 업체 등록")
        col_n1, col_n2 = st.columns(2)
        with col_n1: n_name = st.text_input("업체 이름")
        with col_n2: n_fee = st.text_input("요율 (%)", value="0.5")
        n_wallet = st.text_input("지갑 주소")
        n_note = st.text_area("비고 (특이사항)")
        if st.form_submit_button("신규 업체 등록 완료"):
            if n_name and n_wallet:
                st.session_state.db[n_name] = {"wallet": n_wallet, "fee": n_fee, "note": n_note}
                save_data(st.session_state.db)
                st.success(f"✅ {n_name} 등록 성공!")
                st.rerun()

    st.divider()
    st.subheader("📂 업체 목록 수정")
    
    # 업체명 변경 로직 포함
    for original_name in sorted(list(st.session_state.db.keys())):
        info = st.session_state.db[original_name]
        with st.expander(f"{original_name}"):
            new_name = st.text_input("업체명 변경", value=original_name, key=f"nm_{original_name}")
            u_w = st.text_input("지갑 주소", value=info['wallet'], key=f"w_{original_name}")
            u_f = st.text_input("요율 (%)", value=info['fee'], key=f"f_{original_name}")
            u_n = st.text_area("비고", value=info.get('note', ''), key=f"n_{original_name}")
            
            # 버튼 가깝게 배치
            c1, c2, c3 = st.columns([1, 1, 2])
            with c1:
                st.markdown('<div class="btn-save">', unsafe_allow_html=True)
                if st.button("저장", key=f"s_{original_name}"):
                    # 이름이 바뀌었으면 기존 키 삭제 후 새 키 생성
                    if new_name != original_name:
                        del st.session_state.db[original_name]
                    st.session_state.db[new_name] = {"wallet": u_w, "fee": u_f, "note": u_n}
                    save_data(st.session_state.db)
                    st.success("변경 완료!")
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            with c2:
                st.markdown('<div class="btn-del">', unsafe_allow_html=True)
                if st.button("삭제", key=f"d_{original_name}"):
                    del st.session_state.db[original_name]
                    save_data(st.session_state.db)
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
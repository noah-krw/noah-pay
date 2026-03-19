import streamlit as st
import math
import json
import os
import re

# [정산 매크로 v79 - Noah 전용: 데이터 보존 및 스텝4 복구 버전]

DB_FILE = "merchants.json"

def get_default_list():
    """스크린샷 및 이전 기록 기반 전체 머천트 리스트"""
    return {
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
        'spfxm': {'wallet': 'TWbFbzW5GRkAkVrY4fLuXhNA576DCkoGbh', 'fee': '0.5', 'note': '기존 관리 업체 (지갑주소 업데이트 완료)'},
        'V99': {'wallet': 'TRX_Wallet_V99', 'fee': '1.5', 'note': 'VVIP 전용'}
    }

def load_data():
    defaults = get_default_list()
    if not os.path.exists(DB_FILE):
        save_data(defaults)
        return defaults
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            db = json.load(f)
            # 파일 데이터가 비어있거나 너무 적으면 기본값 로드
            return db if len(db) >= 3 else defaults
    except:
        return defaults

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def extract_int(text):
    num_str = re.sub(r'[^0-9]', '', text)
    return int(num_str) if num_str else 0

st.set_page_config(page_title="정산 매크로 v79", layout="centered")

st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] { background-color: #1e1e1e !important; color: #e0e0e0 !important; }
    div[data-baseweb="input"] { background-color: #2d2d2d !important; border: 1px solid #444 !important; }
    input { color: #f1c40f !important; font-size: 1.1em !important; font-weight: bold !important; }
    .m-header { background-color: #000; color: #ffffff; padding: 10px; border-radius: 4px; text-align: center; margin-bottom: 20px; border: 1px solid #333; font-size: 1.1em; font-weight: bold; }
    .label { color: #5dade2; font-weight: bold; margin-top: 15px; margin-bottom: 5px; }
    .stButton > button { width: 100% !important; height: 40px !important; font-weight: bold !important; border-radius: 5px !important; }
    .btn-save button { background-color: #007bff !important; color: white !important; }
    .btn-del button { background-color: #dc3545 !important; color: white !important; }
    [data-testid="column"] { padding: 0 2px !important; }
    </style>
    """, unsafe_allow_html=True)

if 'db' not in st.session_state: st.session_state.db = load_data()
if 'page' not in st.session_state: st.session_state.page = 'settle'

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
    
    # 1. 환율 설정
    st.markdown('<p class="label">1. 환율 설정</p>', unsafe_allow_html=True)
    multiplier = st.radio("배수", [1.04, 1.045, 1.05], format_func=lambda x: f"{(x-1)*100:.1f}%", index=1, horizontal=True)
    c1, c2 = st.columns(2)
    with c1: 
        b_raw = st.text_input("빗썸 시세", value="0")
        b_val = extract_int(b_raw)
        if b_val > 0: st.caption(f"확인: {b_val:,} 원")
    with c2: 
        s_raw = st.text_input("수동 환율", value="0")
        s_val = extract_int(s_raw)
        if s_val > 0: st.caption(f"확인: {s_val:,} 원")
        
    current_rate = s_val if s_val > 0 else math.ceil(b_val * multiplier)
    st.code(f"1 USDT = {current_rate:,} KRW", language="text")

    # 2. 정산 문구
    st.markdown('<p class="label">2. 정산 요청 (USDT 변환)</p>', unsafe_allow_html=True)
    a_raw = st.text_input("정산 금액", value="0")
    amount = extract_int(a_raw)
    if amount > 0: st.caption(f"입력 확인: {amount:,} 원")
    
    usdt_val = 0
    settle_msg = ""
    if amount > 0:
        usdt_val = round(amount / current_rate, 2)
        settle_msg = f"- {selected_m} settlement amount : {amount:,} krw\n- exchange to usdt : {usdt_val:,.2f} usdt\n- 1usdt = {current_rate:,} krw\n\n{m_info['wallet']}\n\nPlease confirm the address and calculation.\nOnce approved, we will proceed immediately"
        st.code(settle_msg, language="text")

    # 3. 최종 잔액 보고
    st.markdown('<p class="label">3. 최종 잔액 보고</p>', unsafe_allow_html=True)
    bal_raw = st.text_input("잔액 입력", value="0")
    balance = extract_int(bal_raw)
    if balance > 0: st.caption(f"입력 확인: {balance:,} 원")
    
    balance_msg = ""
    if balance > 0 and amount > 0:
        balance_msg = f"Balance & settlement update\n\n- {selected_m}\nsettlement amount : {amount:,} krw\nexchange to usdt : {math.ceil(amount / current_rate):,} usdt\n1usdt = {current_rate:,} krw\n\n- {selected_m} : {balance:,} krw"
        st.code(balance_msg, language="text")

    # 4. 마크업 복사
    st.markdown('<p class="label" style="color:#f1c40f;">4. 텔레그램 마크업 복사</p>', unsafe_allow_html=True)
    if amount > 0 and balance > 0:
        full_markup = f"**[Settlement Report]**\n\n{settle_msg}\n\n---\n\n{balance_msg}"
        st.code(full_markup, language="markdown")

    # 벨런스 경고
    st.markdown('<p class="label" style="color:#e74c3c;">🚨 벨런스 경고 전용</p>', unsafe_allow_html=True)
    warn_raw = st.text_input("경고용 벨런스 입력", value="0", key="warn_bal")
    warn_bal = extract_int(warn_raw)
    if warn_bal > 0:
        st.caption(f"입력 확인: {warn_bal:,} 원")
        st.code(f"Hello, Team\nCurrently, the balance of the merchants is too high.\nTo ensure a safe balance, please proceed with USDT settlement.\nThank you\n\nBalance update\n\n- {selected_m} : {warn_bal:,} krw", language="text")

else:
    # 업체 설정 화면 (데이터 보호를 위해 기존 구조 엄격 유지)
    st.title("⚙️ 머천트 설정 관리")
    with st.form("new_m", clear_on_submit=True):
        st.subheader("➕ 신규 업체 등록")
        n_name = st.text_input("업체 이름")
        n_wallet = st.text_input("지갑 주소")
        col_f1, col_f2 = st.columns(2)
        with col_f1: n_fee = st.text_input("요율 (%)", value="0.5")
        with col_f2: n_note = st.text_input("비고 (특이사항)")
        if st.form_submit_button("신규 업체 등록 완료"):
            if n_name and n_wallet:
                st.session_state.db[n_name] = {"wallet": n_wallet, "fee": n_fee, "note": n_note}
                save_data(st.session_state.db); st.success(f"✅ {n_name} 등록 성공!"); st.rerun()

    st.divider()
    st.subheader("📂 업체 목록 수정")
    for orig_name in sorted(list(st.session_state.db.keys())):
        info = st.session_state.db[orig_name]
        with st.expander(f"**{orig_name}**"):
            new_nm = st.text_input("업체명", value=orig_name, key=f"nm_{orig_name}")
            u_w = st.text_input("지갑 주소", value=info['wallet'], key=f"w_{orig_name}")
            u_f = st.text_input("요율", value=info['fee'], key=f"f_{orig_name}")
            u_n = st.text_area("비고", value=info.get('note',''), key=f"n_{orig_name}")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown('<div class="btn-save">', unsafe_allow_html=True)
                if st.button("저장", key=f"s_{orig_name}"):
                    if new_nm != orig_name: del st.session_state.db[orig_name]
                    st.session_state.db[new_nm] = {"wallet": u_w, "fee": u_f, "note": u_n}
                    save_data(st.session_state.db)
                    st.success(f"✅ {new_nm} 저장 완료!")
                st.markdown('</div>', unsafe_allow_html=True)
            with c2:
                st.markdown('<div class="btn-del">', unsafe_allow_html=True)
                if st.button("삭제", key=f"d_{orig_name}"):
                    del st.session_state.db[orig_name]
                    save_data(st.session_state.db)
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
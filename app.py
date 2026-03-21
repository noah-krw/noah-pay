# -*- coding: utf-8 -*-
import streamlit as st
import streamlit.components.v1 as components
import math
import json
import os
import re
from datetime import datetime

# ============================================================
# 정산 매크로 v88 - Noah 전용 디자인 통합본
# ============================================================

DB_FILE = "merchants.json"

# --- 데이터 관리 ---
def get_default_list():
    return {
        'dr188': {'wallet': 'TBMTb9TFFXDuqhjLKLp9Yo26QHRnnG6jPN', 'fee': '0.5', 'note': '드래곤 메인'},
        'drgtssen': {'wallet': 'TRX_Wallet_drgtssen', 'fee': '0.5', 'note': ''},
        'Dpinnacle': {'wallet': 'TRX_Wallet_Dpinnacle', 'fee': '0.5', 'note': ''},
        'drSpinmama': {'wallet': 'TRX_Wallet_drSpinmama', 'fee': '0.5', 'note': ''},
        'drbetssen': {'wallet': 'TRX_Wallet_drbetssen', 'fee': '0.5', 'note': ''},
        'NextbetM/G': {'wallet': 'TRX_Wallet_Nextbet', 'fee': '0.5', 'note': ''},
        'DafabetM/G': {'wallet': 'TRX_Wallet_Dafabet', 'fee': '4.5', 'note': ''},
        'drgtkore': {'wallet': 'TRX_Wallet_drgtkore', 'fee': '0.5', 'note': ''},
        'drolymp': {'wallet': 'TRX_Wallet_drolymp', 'fee': '0.5', 'note': ''},
        'drbetkore': {'wallet': 'TRX_Wallet_drbetkore', 'fee': '0.5', 'note': ''},
        'drTapTap': {'wallet': 'TRX_Wallet_drTapTap', 'fee': '0.5', 'note': ''},
        'spfxm': {'wallet': 'TWbFbzW5GRkAkVrY4fLuXhNA576DCkoGbh', 'fee': '4', 'note': '가장 많이 쓰는 업체'},
        'V99': {'wallet': 'TRX_Wallet_V99', 'fee': '1.5', 'note': 'VVIP 전용'}
    }

def load_data():
    defaults = get_default_list()
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                db = json.load(f)
                return db if len(db) >= 1 else defaults
        except: return defaults
    save_data(defaults)
    return defaults

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# --- 유틸리티 ---
def extract_int(text):
    num_str = re.sub(r'[^0-9]', '', str(text))
    return int(num_str) if num_str else 0

def fmt(n): return f"{n:,}"

# --- 복사 가능 결과 박스 (UI 업그레이드) ---
def copy_box(text, color_type="blue"):
    colors = {
        "blue": {"border": "#4a90d9", "bg": "#060d18", "text": "#a8c7e8"},
        "green": {"border": "#27ae60", "bg": "#06180d", "text": "#7dcea0"},
        "yellow": {"border": "#f39c12", "bg": "#181406", "text": "#f8c471"},
        "red": {"border": "#e74c3c", "bg": "#180606", "text": "#f1948a"}
    }
    c = colors.get(color_type, colors["blue"])
    js_text = json.dumps(text)
    line_count = text.count("\n") + 1
    height = max(80, line_count * 24 + 50)

    html_code = f"""
    <div style="position:relative; background:{c['bg']}; border:1px solid #1e3a5f; border-left:4px solid {c['border']}; 
                border-radius:6px; padding:15px; font-family:monospace; font-size:13.5px; line-height:1.6; color:{c['text']};">
        <button onclick="copyToClipboard()" style="position:absolute; top:10px; right:10px; background:#0f2040; color:#5dade2; 
                border:1px solid #1e3a5f; border-radius:4px; padding:4px 8px; cursor:pointer; font-size:11px;">📋 복사</button>
        <pre id="copyTarget" style="margin:0; white-space:pre-wrap; word-break:break-all;">{text}</pre>
    </div>
    <script>
    function copyToClipboard() {{
        const text = {js_text};
        const el = document.createElement('textarea');
        el.value = text;
        document.body.appendChild(el);
        el.select();
        document.execCommand('copy');
        document.body.removeChild(el);
        alert('복사되었습니다!');
    }}
    </script>
    """
    components.html(html_code, height=height)

# --- 페이지 설정 및 스타일 ---
st.set_page_config(page_title="정산 매크로 v88", layout="centered")

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #0a0e17 !important; color: #c8d6e5 !important; }
    div[data-baseweb="input"] { background-color: #ffffff !important; border-radius: 6px !important; }
    input { color: #000000 !important; font-weight: bold !important; font-family: monospace !important; }
    .label-header { color: #4a90d9; font-weight: bold; font-size: 0.85em; border-bottom: 1px solid #1e2d45; padding-bottom: 5px; margin-top: 25px; margin-bottom: 10px; text-transform: uppercase; }
    .status-val { color: #f1c40f; font-size: 0.8em; margin-top: -10px; margin-bottom: 5px; font-family: monospace; }
</style>
""", unsafe_allow_html=True)

if 'db' not in st.session_state: st.session_state.db = load_data()
if 'page' not in st.session_state: st.session_state.page = 'settle'

# --- 사이드바 ---
with st.sidebar:
    st.title("💹 정산 매크로")
    if st.button("🚀 정산 작업"): st.session_state.page = 'settle'
    if st.button("⚙️ 머천트 설정"): st.session_state.page = 'admin'
    st.divider()
    st.caption(f"접속 시간: {datetime.now().strftime('%H:%M:%S')}")

# --- 메인 페이지 ---
if st.session_state.page == 'settle':
    st.title("🚀 실시간 정산 작업")
    
    # 업체 선택
    sorted_keys = sorted(list(st.session_state.db.keys()))
    default_idx = sorted_keys.index('spfxm') if 'spfxm' in sorted_keys else 0
    selected_m = st.selectbox("업체 선택", sorted_keys, index=default_idx)
    m_info = st.session_state.db[selected_m]
    
    # 1. 환율 설정
    st.markdown('<div class="label-header">01. 환율 설정</div>', unsafe_allow_html=True)
    multiplier = st.radio("적용 배수", [1.04, 1.045, 1.05], format_func=lambda x: f"{(x-1)*100:.1f}%", index=0, horizontal=True)
    c1, c2 = st.columns(2)
    with c1:
        b_val = extract_int(st.text_input("빗썸 시세", value="0"))
        if b_val > 0: st.markdown(f'<div class="status-val">→ {fmt(b_val)} 원</div>', unsafe_allow_html=True)
    with c2:
        s_val = extract_int(st.text_input("수동 환율 (우선 적용)", value="0"))
        if s_val > 0: st.markdown(f'<div class="status-val">→ {fmt(s_val)} 원</div>', unsafe_allow_html=True)
    
    current_rate = s_val if s_val > 0 else math.ceil(b_val * multiplier)
    if current_rate > 0:
        copy_box(f"1 USDT = {fmt(current_rate)} KRW", "blue")

    # 2. 정산 요청
    st.markdown('<div class="label-header">02. 정산 요청 (USDT 변환)</div>', unsafe_allow_html=True)
    amount = extract_int(st.text_input("정산 금액 (KRW)"))
    if amount > 0:
        st.markdown(f'<div class="status-val">→ {fmt(amount)} 원</div>', unsafe_allow_html=True)
        usdt_val = round(amount / current_rate, 2)
        settle_msg = f"- {selected_m} settlement amount : {fmt(amount)} krw\n- exchange to usdt : {usdt_val:,.2f} usdt\n- 1usdt = {fmt(current_rate)} krw\n\n{m_info['wallet']}\n\nPlease confirm the address and calculation.\nOnce approved, we will proceed immediately"
        copy_box(settle_msg, "blue")

    # 3. 최종 잔액 보고
    st.markdown('<div class="label-header">03. 최종 잔액 보고</div>', unsafe_allow_html=True)
    balance = extract_int(st.text_input("현재 잔액 입력 (KRW)"))
    if balance > 0:
        st.markdown(f'<div class="status-val">→ {fmt(balance)} 원</div>', unsafe_allow_html=True)
        usdt_ceil = math.ceil(amount / current_rate)
        balance_msg = f"Balance & settlement update\n\n- {selected_m}\nsettlement amount : {fmt(amount)} krw\nexchange to usdt : {fmt(usdt_ceil)} usdt\n1usdt = {fmt(current_rate)} krw\n\n- {selected_m} : {fmt(balance)} krw"
        copy_box(balance_msg, "green")

    # 4. 수수료 마크업 (원라인)
    if amount > 0:
        st.markdown('<div class="label-header">04. 수수료 마크업 (내부 보고용)</div>', unsafe_allow_html=True)
        fee_rate = float(m_info.get('fee', 0.5))
        calc_fee = math.ceil(amount * (fee_rate / 100))
        dragon_list = ['dr188', 'drgtssen', 'Dpinnacle', 'drSpinmama', 'drbetssen', 'NextbetM/G', 'DafabetM/G', 'drgtkore', 'drolymp', 'drbetkore', 'drTapTap', 'spfxm']
        prefix = "드래곤 테더정산" if selected_m in dragon_list else "일반 테더정산"
        markup_msg = f"{prefix} 수수료 {fee_rate}% {selected_m} / {fmt(amount)} / {fmt(calc_fee)}"
        copy_box(markup_msg, "yellow")

    # 5. 탑업(Top-up) 요청
    st.divider()
    st.markdown('<div class="label-header" style="color:#2ecc71;">05. TOP-UP 요청 (수수료 0.5% 차감)</div>', unsafe_allow_html=True)
    topup_usdt = extract_int(st.text_input("탑업 USDT 수량"))
    if topup_usdt > 0: st.markdown(f'<div class="status-val">→ {fmt(topup_usdt)} USDT</div>', unsafe_allow_html=True)
    
    tc1, tc2 = st.columns(2)
    with tc1:
        tm_rate = extract_int(st.text_input("탑업용 빗썸 시세"))
    with tc2:
        ts_rate = extract_int(st.text_input("탑업용 수동 환율"))
    
    if ts_rate > 0: final_t_rate = ts_rate
    elif tm_rate > 0: final_t_rate = tm_rate - math.ceil(tm_rate * 0.005)
    else: final_t_rate = 0

    if topup_usdt > 0 and final_t_rate > 0:
        total_krw = topup_usdt * final_t_rate
        topup_msg = f"top-up\n\nmid : {selected_m}\ntop-up amount : {fmt(topup_usdt)} usdt\nexchange to KRW : {fmt(total_krw)} krw\n1usdt = {fmt(final_t_rate)} krw\n\n{m_info['wallet']}\n\nPlease check the invoice and transfer the USDT to the address provided."
        copy_box(topup_msg, "green")
        
        # 탑업 마크업
        base_rate = ts_rate if ts_rate > 0 else tm_rate
        total_market_krw = topup_usdt * base_rate
        total_fee_krw = math.ceil(total_market_krw * 0.005)
        copy_box(f"드래곤 테더탑업 수수료 0.5% {selected_m} / {fmt(total_market_krw)} / {fmt(total_fee_krw)}", "yellow")

else:
    # 설정 페이지
    st.title("⚙️ 머천트 설정 관리")
    # (업체 등록 및 수정 로직은 이전과 동일하게 유지)
    with st.form("new_merchant"):
        st.subheader("➕ 신규 업체 등록")
        n_name = st.text_input("업체 이름")
        n_wallet = st.text_input("지갑 주소")
        n_fee = st.text_input("수수료 (%)", value="0.5")
        if st.form_submit_button("등록 완료"):
            if n_name and n_wallet:
                st.session_state.db[n_name] = {"wallet": n_wallet, "fee": n_fee}
                save_data(st.session_state.db); st.success("등록 완료!"); st.rerun()

    st.divider()
    for name in sorted(st.session_state.db.keys()):
        with st.expander(f"📦 {name}"):
            info = st.session_state.db[name]
            u_w = st.text_input("지갑", value=info['wallet'], key=f"w_{name}")
            u_f = st.text_input("요율", value=info['fee'], key=f"f_{name}")
            if st.button("저장", key=f"btn_{name}"):
                st.session_state.db[name] = {"wallet": u_w, "fee": u_f}
                save_data(st.session_state.db); st.success("저장됨")
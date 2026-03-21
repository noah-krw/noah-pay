# -*- coding: utf-8 -*-
import streamlit as st
import streamlit.components.v1 as components
import math
import json
import os
import re

# ============================================================
# 정산 매크로 v90.0 - Noah 전용 (박스 높이 최적화 및 가변형 편집)
# ============================================================

DB_FILE = "merchants.json"

def get_default_list():
    return {
        'spfxm': {'wallet': 'TWbFbzW5GRkAkVrY4fLuXhNA576DCkoGbh', 'fee': '4'},
        'dr188': {'wallet': 'TBMTb9TFFXDuqhjLKLp9Yo26QHRnnG6jPN', 'fee': '0.5'},
        'V99': {'wallet': 'TRX_Wallet_V99', 'fee': '1.5'}
    }

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return get_default_list()

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def extract_int(text):
    if not text: return 0
    num_str = re.sub(r'[^0-9]', '', str(text))
    return int(num_str) if num_str else 0

def fmt(n): return f"{n:,}"

# --- 내용 길이에 따라 높이가 조절되는 편집 박스 ---
def copy_box(text, color_type="blue", key=None):
    colors = {
        "blue": {"border": "#4a90d9", "bg": "#060d18", "text": "#a8c7e8"},
        "green": {"border": "#27ae60", "bg": "#06180d", "text": "#7dcea0"},
        "yellow": {"border": "#f39c12", "bg": "#181406", "text": "#f8c471"},
        "red": {"border": "#e74c3c", "bg": "#180606", "text": "#f1948a"}
    }
    c = colors.get(color_type, colors["blue"])
    
    # 줄 수 계산하여 높이 동적 할당 (한 줄은 최소 높이로)
    line_count = text.count("\n") + 1
    # 한 줄일 때 약 68px, 여러 줄일 때 줄당 약 25px 추가
    box_height = 68 if line_count == 1 else (line_count * 25) + 40
    
    st.markdown(f"""
    <style>
    div[data-testid="stFormSubmitButton"] > button {{ width: 100%; }}
    .stTextArea textarea[key="{key}"] {{
        background-color: {c['bg']} !important;
        color: {c['text']} !important;
        border: 1px solid #1e3a5f !important;
        border-left: 4px solid {c['border']} !important;
        font-family: monospace !important;
        font-size: 14px !important;
        line-height: 1.5 !important;
        padding: 10px !important;
    }}
    </style>
    """, unsafe_allow_html=True)
    
    edited_text = st.text_area("결과 확인 (수정 가능)", value=text, height=box_height, key=key, label_visibility="collapsed")
    
    if st.button("📋 복사", key=f"btn_{key}"):
        # 가상 textarea 생성하여 클립보드 복사 로직
        js_code = f"""
        <script>
        function copy() {{
            const text = `{edited_text}`;
            const el = document.createElement('textarea');
            el.value = text;
            document.body.appendChild(el);
            el.select();
            document.execCommand('copy');
            document.body.removeChild(el);
        }}
        copy();
        </script>
        """
        components.html(js_code, height=0)
        st.toast("클립보드에 복사되었습니다!")

st.set_page_config(page_title="정산 매크로 v90.0", layout="centered")

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #0a0e17 !important; color: #c8d6e5 !important; }
    div[data-baseweb="input"] { background-color: #ffffff !important; border-radius: 6px !important; }
    input { 
        color: #d4ac0d !important; 
        -webkit-text-fill-color: #d4ac0d !important;
        font-weight: bold !important; 
        font-family: monospace !important; 
        font-size: 1.2em !important; 
    }
    .label-header { color: #4a90d9; font-weight: bold; font-size: 1.25em; border-bottom: 2px solid #1e2d45; padding-bottom: 8px; margin-top: 30px; margin-bottom: 10px; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

if 'db' not in st.session_state: st.session_state.db = load_data()
if 'page' not in st.session_state: st.session_state.page = 'settle'

with st.sidebar:
    st.title("💹 정산 매크로")
    if st.button("🚀 정산 작업"): st.session_state.page = 'settle'; st.rerun()
    if st.button("⚙️ 머천트 관리"): st.session_state.page = 'admin'; st.rerun()

if st.session_state.page == 'settle':
    st.title("🚀 실시간 정산 작업")
    sorted_keys = sorted(list(st.session_state.db.keys()))
    default_idx = sorted_keys.index('spfxm') if 'spfxm' in sorted_keys else 0
    selected_m = st.selectbox("업체 선택", sorted_keys, index=default_idx)
    m_info = st.session_state.db[selected_m]
    
    st.markdown('<div class="label-header">01. 환율 설정</div>', unsafe_allow_html=True)
    multiplier = st.radio("적용 배수", [1.04, 1.045, 1.05], index=0, horizontal=True)
    c1, c2 = st.columns(2)
    with c1: b_val = extract_int(st.text_input("빗썸 시세", key="b_val", value="0"))
    with c2: s_val = extract_int(st.text_input("수동 환율", key="s_val", value="0"))
    current_rate = s_val if s_val > 0 else math.ceil(b_val * multiplier)
    if current_rate > 0: copy_box(f"1 USDT = {fmt(current_rate)} KRW", "blue", key="rate_res")

    st.markdown('<div class="label-header">02. 정산 요청</div>', unsafe_allow_html=True)
    amount = extract_int(st.text_input("정산 금액 (KRW)", key="amt_in"))
    if amount > 0:
        usdt_val = round(amount / current_rate, 2)
        settle_msg = f"- {selected_m} settlement amount : {fmt(amount)} krw\n- exchange to usdt : {usdt_val:,.2f} usdt\n- 1usdt = {fmt(current_rate)} krw\n\n{m_info['wallet']}\n\nPlease confirm the address and calculation.\nOnce approved, we will proceed immediately"
        copy_box(settle_msg, "blue", key="settle_res")

    st.markdown('<div class="label-header">03. 최종 잔액 보고</div>', unsafe_allow_html=True)
    balance = extract_int(st.text_input("현재 잔액 입력 (KRW)", key="bal_in"))
    if balance > 0:
        usdt_ceil = math.ceil(amount / current_rate)
        balance_msg = f"Balance & settlement update\n\n- {selected_m}\nsettlement amount : {fmt(amount)} krw\nexchange to usdt : {fmt(usdt_ceil)} usdt\n1usdt = {fmt(current_rate)} krw\n\n- {selected_m} : {fmt(balance)} krw"
        copy_box(balance_msg, "green", key="balance_res")

    st.markdown('<div class="label-header">04. 마크업 수수료 계산</div>', unsafe_allow_html=True)
    m_fee_rate = float(m_info.get('fee', 0.5))
    markup_fee = math.ceil(amount * (m_fee_rate / 100))
    if amount > 0:
        copy_box(f"마크업 수수료 {m_fee_rate}% {selected_m} / {fmt(amount)} / {fmt(markup_fee)}", "yellow", key="markup_res")

    # (이하 생략 - TOP-UP 등 로직 동일)
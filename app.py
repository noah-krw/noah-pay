# -*- coding: utf-8 -*-
import streamlit as st
import streamlit.components.v1 as components
import math, json, os, re

# ============================================================
# 정산 매크로 v93.2 - Noah 실장님 지시사항 완벽 구현본
# ============================================================

DB_FILE = "merchants_v4.json"

def get_default_data():
    return {
        'my_wallet': 'TDaQt8oASZhVsuaEdpevqCacGKseGKCWhQ',
        'merchants': {
            'spfxm': {'wallet': 'TWbFbzW5GRkAkVrY4fLuXhNA576DCkoGbh', 'fee': '4', 'note': '가장 많이 사용하는 업체'},
            'dr188': {'wallet': 'TBMTb9TFFXDuqhjLKLp9Yo26QHRnnG6jPN', 'fee': '0.5', 'note': '드래곤 메인'},
            'V99': {'wallet': 'TRX_Wallet_V99', 'fee': '1.5', 'note': 'VVIP 전용'}
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

# [핵심] 결과창에서 직접 수정 가능한 복사 박스
def copy_box(text, color_type="blue", key=None):
    colors = {
        "blue": {"border": "#4a90d9", "bg": "#060d18", "text": "#a8c7e8"},
        "green": {"border": "#27ae60", "bg": "#06180d", "text": "#7dcea0"},
        "yellow": {"border": "#f39c12", "bg": "#181406", "text": "#f8c471"},
        "red": {"border": "#e74c3c", "bg": "#180606", "text": "#f1948a"}
    }
    c = colors.get(color_type, colors["blue"])
    line_count = text.count("\n") + 1
    height = max(130, line_count * 25 + 50)
    
    # 결과창 자체를 수정 가능한 text_area로 구현
    st.markdown(f"""<style>div[data-baseweb="textarea"] textarea[key="{key}"] {{ background-color: {c['bg']} !important; color: {c['text']} !important; border-left: 5px solid {c['border']} !important; font-family: monospace !important; font-size: 15px !important; }}</style>""", unsafe_allow_html=True)
    edited_text = st.text_area("결과 (수정 가능)", value=text, height=height, key=key, label_visibility="collapsed")
    
    if st.button("📋 복사", key=f"btn_{key}"):
        js = f"<script>navigator.clipboard.writeText(`{edited_text}`);</script>"
        components.html(js, height=0)
        st.toast("클립보드에 복사되었습니다!")

st.set_page_config(page_title="정산 매크로 v93.2", layout="centered")

# --- v89.8 디자인 CSS (흰색 입력창 + 금색 글자) ---
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #0a0e17 !important; color: #c8d6e5 !important; }
    div[data-baseweb="input"] { background-color: #ffffff !important; border-radius: 6px !important; }
    input { color: #d4ac0d !important; -webkit-text-fill-color: #d4ac0d !important; font-weight: bold !important; font-family: monospace !important; font-size: 1.25em !important; }
    .label-header { color: #4a90d9; font-weight: bold; font-size: 1.25em; border-bottom: 2px solid #1e2d45; padding-bottom: 8px; margin-top: 35px; margin-bottom: 15px; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

if 'db' not in st.session_state: st.session_state.db = load_data()
if 'page' not in st.session_state: st.session_state.page = 'settle'

with st.sidebar:
    st.title("💹 SETTLEMENT")
    if st.button("🚀 정산 작업"): st.session_state.page = 'settle'; st.rerun()
    if st.button("⚙️ 머천트 관리"): st.session_state.page = 'admin'; st.rerun()
    st.divider()
    if st.button("🔄 데이터 초기화/복구"):
        st.session_state.db = get_default_data()
        save_data(st.session_state.db); st.success("데이터가 초기값으로 복구되었습니다."); st.rerun()

if st.session_state.page == 'settle':
    st.title("🚀 실시간 정산 작업")
    merchants = st.session_state.db['merchants']
    sorted_keys = sorted(list(merchants.keys()))
    default_idx = sorted_keys.index('spfxm') if 'spfxm' in sorted_keys else 0
    selected_m = st.selectbox("업체 선택", sorted_keys, index=default_idx)
    m_info = merchants[selected_m]
    
    st.info(f"📝 업체 비고: {m_info.get('note', '없음')}")

    st.markdown('<div class="label-header">01. 환율 설정</div>', unsafe_allow_html=True)
    sel_p = st.radio("적용 배수", ["4%", "4.5%", "5%"], index=0, horizontal=True)
    m_map = {"4%": 1.04, "4.5%": 1.045, "5%": 1.05}
    c1, c2 = st.columns(2)
    with c1: b_val = extract_int(st.text_input("빗썸 시세", key="b_in"))
    with c2: s_val = extract_int(st.text_input("수동 환율", key="s_in"))
    rate = s_val if s_val > 0 else math.ceil(b_val * m_map[sel_p])
    if rate > 0: copy_box(f"1 USDT = {fmt(rate)} KRW", "blue", key="res_rate")

    st.markdown('<div class="label-header">02. 정산 요청</div>', unsafe_allow_html=True)
    amount = extract_int(st.text_input("정산 금액 (KRW)", key="amt_in"))
    if amount > 0:
        u_val = round(amount / rate, 2)
        # 학습된 정산 멘트 고정
        s_msg = f"- {selected_m} settlement amount : {fmt(amount)} krw\n- exchange to usdt : {u_val:,.2f} usdt\n- 1usdt = {fmt(rate)} krw\n\n{m_info['wallet']}\n\nPlease confirm the address and calculation.\nOnce approved, we will proceed immediately"
        copy_box(s_msg, "blue", key="res_settle")

    st.markdown('<div class="label-header">03. 최종 잔액 보고</div>', unsafe_allow_html=True)
    bal_in = extract_int(st.text_input("현재 잔액 입력 (KRW)", key="bal_in"))
    if bal_in > 0 and amount > 0:
        u_ceil = math.ceil(amount / rate)
        b_msg = f"Balance & settlement update\n\n- {selected_m}\nsettlement amount : {fmt(amount)} krw\nexchange to usdt : {fmt(u_ceil)} usdt\n1usdt = {fmt(rate)} krw\n\n- {selected_m} : {fmt(bal_in)} krw"
        copy_box(b_msg, "green", key="res_balance")

    st.markdown('<div class="label-header">04. 마크업 수수료</div>', unsafe_allow_html=True)
    m_fee = float(m_info.get('fee', 0.5))
    markup = math.ceil(amount * (m_fee / 100))
    if amount > 0:
        copy_box(f"드래곤 테더정산 마크업 {m_fee}% {selected_m} / {fmt(amount)} / {fmt(markup)}", "yellow", key="res_markup")

    st.divider()
    st.markdown('<div class="label-header" style="color:#2ecc71;">06. TOP-UP 요청</div>', unsafe_allow_html=True)
    cl, cr = st.columns(2) 
    with cl: tm_rate = extract_int(st.text_input("탑업 빗썸 시세", key="tm_in"))
    with cr: t_usdt = extract_int(st.text_input("탑업 USDT 수량", key="tu_in"))
    t_rate = tm_rate - math.ceil(tm_rate * 0.005) if tm_rate > 0 else 0
    if t_usdt > 0 and t_rate > 0:
        total_krw = t_usdt * t_rate
        my_wallet = st.session_state.db.get('my_wallet', '')
        copy_box(f"top-up\n\nmid : {selected_m}\ntop-up amount : {fmt(t_usdt)} usdt\nexchange to KRW : {fmt(total_krw)} krw\n1usdt = {fmt(t_rate)} krw\n\n{my_wallet}\n\nPlease check...", "green", key="res_topup")

elif st.session_state.page == 'admin':
    st.title("⚙️ 머천트 및 내 지갑 관리")
    
    st.subheader("💳 내 USDT 지갑 (Top-up용)")
    my_w = st.text_input("지갑 주소", value=st.session_state.db.get('my_wallet', ''))
    if st.button("내 지갑 저장"):
        st.session_state.db['my_wallet'] = my_w
        save_data(st.session_state.db); st.success("저장 완료!")

    st.divider()
    with st.form("new_merchant_form"):
        st.subheader("➕ 신규 업체 등록")
        n_name = st.text_input("업체 이름")
        n_wallet = st.text_input("업체 지갑 주소")
        n_fee = st.text_input("마크업 요율 (%)", value="0.5")
        n_note = st.text_input("비고 (Note)")
        if st.form_submit_button("등록"):
            if n_name and n_wallet:
                st.session_state.db['merchants'][n_name] = {"wallet": n_wallet, "fee": n_fee, "note": n_note}
                save_data(st.session_state.db); st.rerun()
    
    st.divider()
    st.subheader("📦 머천트 리스트")
    for name in sorted(st.session_state.db['merchants'].keys()):
        with st.expander(f"업체: {name}"):
            info = st.session_state.db['merchants'][name]
            u_w = st.text_input("지갑 주소", value=info['wallet'], key=f"w_{name}")
            u_f = st.text_input("요율 (%)", value=info['fee'], key=f"f_{name}")
            u_n = st.text_input("비고 (Note)", value=info.get('note', ''), key=f"n_{name}")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("저장", key=f"s_{name}"):
                    st.session_state.db['merchants'][name] = {"wallet": u_w, "fee": u_f, "note": u_n}
                    save_data(st.session_state.db); st.rerun()
            with c2:
                if st.button("삭제", key=f"d_{name}"):
                    del st.session_state.db['merchants'][name]
                    save_data(st.session_state.db); st.rerun()
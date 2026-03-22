# -*- coding: utf-8 -*-
import streamlit as st
import streamlit.components.v1 as components
import math, json, os, re

# ============================================================
# 정산 매크로 v93.9 - 실장님 지시사항 (비고/복구/3열/수정) 완벽 검증본
# ============================================================

DB_FILE = "merchants_v10.json"

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

# [핵심] 결과창에서 직접 수정 가능한 텍스트 박스 (Key 중복 방지)
def editable_box(text, color_type="blue", box_id="default"):
    colors = {
        "blue": {"border": "#4a90d9", "bg": "#060d18", "text": "#a8c7e8"},
        "green": {"border": "#27ae60", "bg": "#06180d", "text": "#7dcea0"},
        "yellow": {"border": "#f39c12", "bg": "#181406", "text": "#f8c471"},
        "red": {"border": "#e74c3c", "bg": "#180606", "text": "#f1948a"}
    }
    c = colors.get(color_type, colors["blue"])
    line_count = text.count("\n") + 1
    height = max(140, line_count * 25 + 50)
    
    st.markdown(f"""
    <style>
    textarea[aria-label="{box_id}"] {{
        background-color: {c['bg']} !important;
        color: {c['text']} !important;
        border-left: 5px solid {c['border']} !important;
        font-family: 'Courier New', monospace !important;
        font-size: 15px !important;
    }}
    </style>
    """, unsafe_allow_html=True)
    
    # 수정 가능한 결과창 (aria-label을 식별자로 사용)
    content = st.text_area(label=box_id, value=text, height=height, label_visibility="collapsed")
    
    if st.button("📋 복사", key=f"btn_{box_id}"):
        js = f"<script>navigator.clipboard.writeText(`{content}`);</script>"
        components.html(js, height=0)
        st.toast("복사 완료!")

st.set_page_config(page_title="정산 매크로 v93.9", layout="centered")

# v89.8 디자인 (흰색 배경 입력창 + 금색 굵은 글자)
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #0a0e17 !important; color: #c8d6e5 !important; }
    div[data-baseweb="input"] { background-color: #ffffff !important; border-radius: 6px !important; }
    input { color: #d4ac0d !important; -webkit-text-fill-color: #d4ac0d !important; font-weight: bold !important; font-family: monospace !important; font-size: 1.25em !important; }
    .label-header { color: #4a90d9; font-weight: bold; font-size: 1.25em; border-bottom: 2px solid #1e2d45; padding-bottom: 8px; margin-top: 35px; margin-bottom: 15px; text-transform: uppercase; }
    .rate-guide { color: #5dade2; font-size: 1.15em; font-weight: bold; margin: 20px 0; font-family: monospace; text-align: center; background: #060d18; padding: 12px; border: 1px dashed #1e3a5f; }
</style>
""", unsafe_allow_html=True)

if 'db' not in st.session_state: st.session_state.db = load_data()
if 'page' not in st.session_state: st.session_state.page = 'settle'

with st.sidebar:
    st.title("💹 SETTLEMENT")
    if st.button("🚀 정산 작업"): st.session_state.page = 'settle'; st.rerun()
    if st.button("⚙️ 머천트 관리"): st.session_state.page = 'admin'; st.rerun()
    st.divider()
    if st.button("🔄 데이터 복구"):
        st.session_state.db = get_default_data()
        save_data(st.session_state.db); st.success("복구 완료"); st.rerun()

if st.session_state.page == 'settle':
    merchants = st.session_state.db['merchants']
    sorted_keys = sorted(list(merchants.keys()))
    selected_m = st.selectbox("업체 선택", sorted_keys)
    m_info = merchants[selected_m]
    
    st.info(f"📍 지갑: {m_info['wallet']} | 📊 요율: {m_info['fee']}% | 📝 비고: {m_info.get('note', '')}")

    # 01. 정산 요청
    st.markdown('<div class="label-header">01. 정산 환율 및 요청</div>', unsafe_allow_html=True)
    sel_p = st.radio("적용 배수", ["4%", "4.5%", "5%"], index=0, horizontal=True)
    m_map = {"4%": 1.04, "4.5%": 1.045, "5%": 1.05}
    c1, c2 = st.columns(2)
    with c1: b_val = extract_int(st.text_input("빗썸 시세", key="s_b"))
    with c2: s_val = extract_int(st.text_input("수동 환율", key="s_s"))
    rate = s_val if s_val > 0 else math.ceil(b_val * m_map[sel_p])
    
    amt = extract_int(st.text_input("정산 금액 (KRW)", key="s_amt"))
    if amt > 0 and rate > 0:
        u_val = round(amt / rate, 2)
        s_msg = f"- {selected_m} settlement amount : {fmt(amt)} krw\n- exchange to usdt : {u_val:,.2f} usdt\n- 1usdt = {fmt(rate)} krw\n\n{m_info['wallet']}\n\nPlease confirm the address and calculation.\nOnce approved, we will proceed immediately"
        editable_box(s_msg, "blue", box_id="res_01")

    # 02. 잔액 보고
    st.markdown('<div class="label-header">02. 최종 잔액 보고</div>', unsafe_allow_html=True)
    bal_in = extract_int(st.text_input("현재 잔액 입력 (KRW)", key="bal_in"))
    if bal_in > 0 and amt > 0:
        u_ceil = math.ceil(amt / rate)
        b_msg = f"Balance & settlement update\n\n- {selected_m}\nsettlement amount : {fmt(amt)} krw\nexchange to usdt : {fmt(u_ceil)} usdt\n1usdt = {fmt(rate)} krw\n\n- {selected_m} : {fmt(bal_in)} krw"
        editable_box(b_msg, "green", box_id="res_02")

    # 03. 마크업 수수료
    st.markdown('<div class="label-header">03. 마크업 수수료</div>', unsafe_allow_html=True)
    m_fee = float(m_info.get('fee', 0.5))
    markup = math.ceil(amt * (m_fee / 100))
    if amt > 0:
        editable_box(f"드래곤 테더정산 마크업 {m_fee}% {selected_m} / {fmt(amt)} / {fmt(markup)}", "yellow", box_id="res_03")

    # 04. 잔액 경고
    st.markdown('<div class="label-header" style="color:#e74c3c;">04. 잔액 경고</div>', unsafe_allow_html=True)
    w_bal = extract_int(st.text_input("경고용 잔액", key="w_in"))
    if w_bal > 0:
        w_msg = f"Hello, Team\nCurrently, the balance of the merchants is too high.\nTo ensure a safe balance, please proceed with USDT settlement.\nThank you\n\nBalance update\n\n- {selected_m} : {fmt(w_bal)} krw"
        editable_box(w_msg, "red", box_id="res_04")

    st.divider()
    # 06. TOP-UP 요청 (가로 3열 구도)
    st.markdown('<div class="label-header" style="color:#2ecc71;">06. TOP-UP 요청</div>', unsafe_allow_html=True)
    t1, t2, t3 = st.columns(3)
    with t1: tb_val = extract_int(st.text_input("탑업 시세", key="t_b"))
    with t2: tu_amt = extract_int(st.text_input("수량(USDT)", key="t_u"))
    with t3: ts_val = extract_int(st.text_input("수동 환율", key="t_s"))
    
    t_rate = ts_val if ts_val > 0 else (tb_val - math.ceil(tb_val * 0.005) if tb_val > 0 else 0)
    if t_rate > 0:
        st.markdown(f'<div class="rate-guide">>>> 적용 환율 1usdt = {fmt(t_rate)} krw</div>', unsafe_allow_html=True)
        if tu_amt > 0:
            total_krw = tu_amt * t_rate
            my_w = st.session_state.db.get('my_wallet', '')
            t_msg = f"top-up\n\nmid : {selected_m}\ntop-up amount : {fmt(tu_amt)} usdt\nexchange to KRW : {fmt(total_krw)} krw\n1usdt = {fmt(t_rate)} krw\n\n{my_w}\n\nPlease check..."
            editable_box(t_msg, "green", box_id="res_06_req")
            
            base_p = ts_val if ts_val > 0 else tb_val
            t_markup = math.ceil((tu_amt * base_p) * (m_fee / 100))
            f_msg = f"드래곤 테더탑업 마크업 {m_fee}% {selected_m} / {fmt(tu_amt * base_p)} / {fmt(t_markup)}"
            editable_box(f_msg, "yellow", box_id="res_06_fee")

elif st.session_state.page == 'admin':
    st.title("⚙️ 머천트 및 지갑 설정")
    st.subheader("💳 내 USDT 지갑 (Top-up용)")
    my_w = st.text_input("지갑 주소", value=st.session_state.db.get('my_wallet', ''))
    if st.button("저장"):
        st.session_state.db['my_wallet'] = my_w
        save_data(st.session_state.db); st.success("저장 완료")

    st.divider()
    with st.form("new_m"):
        st.subheader("➕ 신규 업체 등록")
        n_name = st.text_input("업체 이름")
        n_wallet = st.text_input("지갑 주소")
        n_fee = st.text_input("요율(%)", value="0.5")
        n_note = st.text_input("비고(Note)")
        if st.form_submit_button("등록"):
            st.session_state.db['merchants'][n_name] = {"wallet": n_wallet, "fee": n_fee, "note": n_note}
            save_data(st.session_state.db); st.rerun()
    
    st.divider()
    for name in sorted(st.session_state.db['merchants'].keys()):
        with st.expander(f"📦 {name}"):
            info = st.session_state.db['merchants'][name]
            u_w = st.text_input("지갑", value=info['wallet'], key=f"ad_w_{name}")
            u_f = st.text_input("요율", value=info['fee'], key=f"ad_f_{name}")
            u_n = st.text_input("비고", value=info.get('note', ''), key=f"ad_n_{name}")
            if st.button("저장", key=f"ad_s_{name}"):
                st.session_state.db['merchants'][name] = {"wallet": u_w, "fee": u_f, "note": u_n}
                save_data(st.session_state.db); st.rerun()
            if st.button("삭제", key=f"ad_d_{name}"):
                del st.session_state.db['merchants'][name]
                save_data(st.session_state.db); st.rerun()
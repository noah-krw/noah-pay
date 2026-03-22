# -*- coding: utf-8 -*-
import streamlit as st
import streamlit.components.v1 as components
import math, json, os, re

# ============================================================
# 정산 매크로 v94.8 - [01번 2열 원복(진짜수정) / 06번 3열 완결]
# ============================================================

DB_FILE = "merchants_v19.json" # DB 초기화를 위해 파일명 변경

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

def editable_box(text, color_type="blue", box_id="default"):
    colors = {
        "blue": {"border": "#4a90d9", "bg": "#060d18", "text": "#a8c7e8"},
        "green": {"border": "#27ae60", "bg": "#06180d", "text": "#7dcea0"},
        "yellow": {"border": "#f39c12", "bg": "#181406", "text": "#f8c471"},
        "red": {"border": "#e74c3c", "bg": "#180606", "text": "#f1948a"}
    }
    c = colors.get(color_type, colors["blue"])
    line_count = text.count("\n") + 1
    height = max(140, line_count * 25 + 60)
    
    st.markdown(f"""<style>textarea[aria-label="{box_id}"] {{ background-color: {c['bg']} !important; color: {c['text']} !important; border-left: 5px solid {c['border']} !important; font-family: 'Courier New', monospace !important; font-size: 15px !important; line-height: 1.5 !important; }}</style>""", unsafe_allow_html=True)
    content = st.text_area(label=box_id, value=text, height=height, label_visibility="collapsed")
    if st.button("📋 복사", key=f"btn_{box_id}"):
        components.html(f"<script>navigator.clipboard.writeText(`{content}`);</script>", height=0)
        st.toast("복사 완료")

st.set_page_config(page_title="정산 매크로 v94.8", layout="centered")

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #0a0e17 !important; color: #c8d6e5 !important; }
    div[data-baseweb="input"] { background-color: #ffffff !important; border-radius: 6px !important; }
    input { color: #d4ac0d !important; -webkit-text-fill-color: #d4ac0d !important; font-weight: bold !important; font-family: 'Courier New', monospace !important; font-size: 1.25em !important; }
    .label-header { color: #4a90d9; font-weight: bold; font-size: 1.25em; border-bottom: 2px solid #1e2d45; padding-bottom: 8px; margin-top: 35px; margin-bottom: 15px; text-transform: uppercase; }
    .rate-guide { color: #5dade2; font-size: 1.15em; font-weight: bold; margin: 15px 0; font-family: monospace; text-align: center; background: #060d18; padding: 10px; border: 1px dashed #1e3a5f; }
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
    default_idx = sorted_keys.index('spfxm') if 'spfxm' in sorted_keys else 0
    selected_m = st.selectbox("업체 선택", sorted_keys, index=default_idx)
    m_info = merchants[selected_m]
    
    st.info(f"📝 비고: {m_info.get('note', '')}")

    # 01. 정산 환율 및 요청 (진짜 2열로 복구 완료)
    st.markdown('<div class="label-header">01. 정산 환율 및 요청</div>', unsafe_allow_html=True)
    sel_p = st.radio("적용 배수", ["4%", "4.5%", "5%"], index=0, horizontal=True)
    m_map = {"4%": 1.04, "4.5%": 1.045, "5%": 1.05}
    
    # [수정] 정산(01)은 [빗썸/환율] 2열만 씁니다. (수량 입력칸 삭제됨)
    sc1, sc2 = st.columns(2)
    with sc1: sb_val = extract_int(st.text_input("빗썸 시세", key="s_b"))
    with sc2: ss_val = extract_int(st.text_input("수동 환율", key="s_s"))
    s_rate = ss_val if ss_val > 0 else math.ceil(sb_val * m_map[sel_p])
    
    if s_rate > 0:
        st.markdown(f'<div class="rate-guide">>>> 적용 환율 1usdt = {fmt(s_rate)} krw</div>', unsafe_allow_html=True)
    
    # [중요] 정산은 KRW를 입력받는 한 줄 단독 입력창입니다.
    amt = extract_int(st.text_input("정산 금액 (KRW)", key="s_amt"))
    
    if amt > 0 and s_rate > 0:
        u_val = round(amt / s_rate, 2)
        s_msg = f"- {selected_m} settlement amount : {fmt(amt)} krw\n- exchange to usdt : {u_val:,.2f} usdt\n- 1usdt = {fmt(s_rate)} krw\n\n{m_info['wallet']}\n\nPlease confirm the address and calculation.\nOnce approved, we will proceed immediately"
        editable_box(s_msg, "blue", box_id="res_01")

    # 02. 잔액 보고
    st.markdown('<div class="label-header">02. 최종 잔액 보고</div>', unsafe_allow_html=True)
    bal_in = extract_int(st.text_input("현재 잔액 입력 (KRW)", key="bal_in"))
    if bal_in > 0 and amt > 0:
        u_ceil = math.ceil(amt / s_rate)
        b_msg = f"Balance & settlement update\n\n- {selected_m}\nsettlement amount : {fmt(amt)} krw\nexchange to usdt : {fmt(u_ceil)} usdt\n1usdt = {fmt(s_rate)} krw\n\n- {selected_m} : {fmt(bal_in)} krw"
        editable_box(b_msg, "green", box_id="res_02")

    # 03. 마크업 수수료
    st.markdown('<div class="label-header">03. 마크업 수수료</div>', unsafe_allow_html=True)
    m_fee = float(m_info.get('fee', 0.5))
    if amt > 0:
        markup = math.ceil(amt * (m_fee / 100))
        editable_box(f"드래곤 테더정산 마크업 {m_fee}% {selected_m} / {fmt(amt)} / {fmt(markup)}", "yellow", box_id="res_03")

    # 04. 잔액 경고
    st.markdown('<div class="label-header" style="color:#e74c3c;">04. 잔액 경고</div>', unsafe_allow_html=True)
    w_bal = extract_int(st.text_input("경고용 잔액", key="w_in"))
    if w_bal > 0:
        w_msg = f"Hello, Team\nCurrently, the balance of the merchants is too high.\nTo ensure a safe balance, please proceed with USDT settlement.\nThank you\n\nBalance
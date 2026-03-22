# -*- coding: utf-8 -*-
import streamlit as st
import streamlit.components.v1 as components
import math, json, os, re

# ============================================================
# 정산 매크로 v95.2 - [01번 2열 / 06번 3열 / 관리페이지 복구]
# ============================================================

DB_FILE = "merchants_v23.json"

def get_default_data():
    return {
        'my_wallet': 'TDaQt8oASZhVsuaEdpevqCacGKseGKCWhQ',
        'merchants': {
            'spfxm': {'wallet': 'TWbFbzW5GRkAkVrY4fLuXhNA576DCkoGbh', 'fee': '4', 'note': '메인 업체'},
            'dr188': {'wallet': 'TBMTb9TFFXDuqhjLKLp9Yo26QHRnnG6jPN', 'fee': '0.5', 'note': '드래곤 메인'},
            'V99': {'wallet': 'TRX_Wallet_V99', 'fee': '1.5', 'note': 'VVIP 전용'}
        }
    }

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
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

def editable_box(text, color_type="blue", box_id="default", placeholder=""):
    colors = {
        "blue": {"border": "#4a90d9", "bg": "#060d18", "text": "#a8c7e8"},
        "green": {"border": "#27ae60", "bg": "#06180d", "text": "#7dcea0"},
        "yellow": {"border": "#f39c12", "bg": "#181406", "text": "#f8c471"},
        "red": {"border": "#e74c3c", "bg": "#180606", "text": "#f1948a"},
        "sky": {"border": "#5dade2", "bg": "#0a1a2f", "text": "#5dade2"}
    }
    c = colors.get(color_type, colors["blue"])
    line_count = text.count("\n") + 1
    height = max(100, line_count * 25 + 50)
    
    st.markdown(f"""<style>textarea[aria-label="{box_id}"] {{ background-color: {c['bg']} !important; color: {c['text']} !important; border-left: 5px solid {c['border']} !important; font-family: 'Courier New', monospace !important; font-size: 15px !important; }}</style>""", unsafe_allow_html=True)
    content = st.text_area(label=box_id, value=text, height=height, placeholder=placeholder, label_visibility="collapsed")
    if st.button("📋 복사", key=f"btn_{box_id}"):
        components.html(f"<script>navigator.clipboard.writeText(`{content}`);</script>", height=0)
        st.toast("복사 완료")

st.set_page_config(page_title="정산 매크로 v95.2", layout="centered")

# v89.8 디자인 테마
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #0a0e17 !important; color: #c8d6e5 !important; }
    div[data-baseweb="input"] { background-color: #ffffff !important; border-radius: 6px !important; }
    input { color: #d4ac0d !important; -webkit-text-fill-color: #d4ac0d !important; font-weight: bold !important; font-family: 'Courier New', monospace !important; font-size: 1.25em !important; }
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

    # 01. 정산 환율 및 요청
    st.markdown('<div class="label-header">01. 정산 환율 및 요청</div>', unsafe_allow_html=True)
    sel_p = st.radio("적용 배수", ["4%", "4.5%", "5%"], index=0, horizontal=True)
    m_map = {"4%": 1.04, "4.5%": 1.045, "5%": 1.05}
    
    # [검증완료] 시세/환율 가로 2열 구도
    s_col1, s_col2 = st.columns(2)
    with s_col1: sb_val = extract_int(st.text_input("빗썸 시세", key="s_b"))
    with s_col2: ss_val = extract_int(st.text_input("수동 환율", key="s_s"))
    s_rate = ss_val if ss_val > 0 else math.ceil(sb_val * m_map[sel_p])
    
    # 환율 복사 버튼 (안내선 대체)
    st.write("▼ 적용 환율 (복사 가능)")
    editable_box(f"1usdt = {fmt(s_rate)} krw" if s_rate > 0 else "", "sky", "rate_01")
    
    # [검증완료] 정산금액 단독 1열
    amt = extract_int(st.text_input("정산 금액 (KRW)", key="s_amt"))
    s_msg = ""
    if amt > 0 and s_rate > 0:
        u_val = round(amt / s_rate, 2)
        s_msg = f"- {selected_m} settlement amount : {fmt(amt)} krw\n- exchange to usdt : {u_val:,.2f} usdt\n- 1usdt = {fmt(s_rate)} krw\n\n{m_info['wallet']}\n\nPlease confirm the address and calculation."
    editable_box(s_msg, "blue", "res_01", "금액 입력 시 정산 멘트 생성")

    # 02. 잔액 보고 / 03. 마크업 (생략된 것처럼 보이지 않게 박스 고정)
    st.markdown('<div class="label-header">02. 최종 잔액 보고</div>', unsafe_allow_html=True)
    bal_in = extract_int(st.text_input("현재 잔액 입력 (KRW)", key="bal_in"))
    b_msg = ""
    if bal_in > 0 and amt > 0:
        u_ceil = math.ceil(amt / s_rate)
        b_msg = f"Balance & settlement update\n\n- {selected_m}\nsettlement amount : {fmt(amt)} krw\nexchange to usdt : {fmt(u_ceil)} usdt\n1usdt = {fmt(s_rate)} krw\n\n- {selected_m} : {fmt(bal_in)} krw"
    editable_box(b_msg, "green", "res_02", "잔액 보고 멘트")

    st.markdown('<div class="label-header">03. 마크업 수수료</div>', unsafe_allow_html=True)
    m_fee = float(m_info.get('fee', 0.5))
    markup_msg = ""
    if amt > 0:
        markup = math.ceil(amt * (m_fee / 100))
        markup_msg = f"드래곤 테더정산 마크업 {m_fee}% {selected_m} / {fmt(amt)} / {fmt(markup)}"
    editable_box(markup_msg, "yellow", "res_03", "수수료 내역")

    # 05. Payout
    st.markdown('<div class="label-header">05. 환전(Payout) 요청</div>', unsafe_allow_html=True)
    p_amt = extract_int(st.text_input("환전 금액 (KRW)", key="p_amt"))
    p_msg = f"payout request\n\nmid : {selected_m}\npayout amount : {fmt(p_amt)} krw" if p_amt > 0 else ""
    editable_box(p_msg, "blue", "res_05", "환전 요청 멘트")

    st.divider()
    # 06. TOP-UP 요청 (그림판 3열 완결본)
    st.markdown('<div class="label-header" style="color:#2ecc71;">06. TOP-UP 요청</div>', unsafe_allow_html=True)
    t_col1, t_col2, t_col3 = st.columns(3)
    with t_col1: tb_val = extract_int(st.text_input("탑업 시세(빗썸)", key="t_b"))
    with t_col2: tu_amt = extract_int(st.text_input("수량(USDT)", key="t_u"))
    with t_col3: ts_val = extract_int(st.text_input("수동 환율", key="t_s"))
    
    t_rate = ts_val if ts_val > 0 else (tb_val - math.ceil(tb_val * 0.005) if tb_val > 0 else 0)
    
    st.write("▼ 적용 환율 (복사 가능)")
    editable_box(f"1usdt = {fmt(t_rate)} krw" if t_rate > 0 else "", "sky", "rate_06")
    
    t_msg, f_msg = "", ""
    if tu_amt > 0 and t_rate > 0:
        total_t_krw = tu_amt * t_rate
        my_w = st.session_state.db.get('my_wallet', '')
        t_msg = f"top-up\n\nmid : {selected_m}\ntop-up amount : {fmt(tu_amt)} usdt\nexchange to KRW : {fmt(total_t_krw)} krw\n1usdt = {fmt(t_rate)} krw\n\n{my_w}"
        t_markup = math.ceil((tu_amt * (ts_val if ts_val > 0 else tb_val)) * (m_fee / 100))
        f_msg = f"드래곤 테더탑업 마크업 {m_fee}% {selected_m} / {fmt(tu_amt * (ts_val if ts_val > 0 else tb_val))} / {fmt(t_markup)}"
    
    editable_box(t_msg, "green", "res_06_req", "탑업 요청 멘트")
    editable_box(f_msg, "yellow", "res_06_fee", "탑업 수수료 내역")

elif st.session_state.page == 'admin':
    st.title("⚙️ 머천트 및 지갑 관리")
    st.session_state.db['my_wallet'] = st.text_input("내 USDT 지갑 주소", value=st.session_state.db.get('my_wallet', ''))
    if st.button("내 지갑 저장"): save_data(st.session_state.db); st.success("저장완료")
    
    st.divider()
    with st.form("new_merchant"):
        st.subheader("➕ 업체 추가")
        n_name = st.text_input("업체명")
        n_wallet = st.text_input("지갑주소")
        n_fee = st.text_input("요율(%)", value="0.5")
        n_note = st.text_input("비고")
        if st.form_submit_button("등록"):
            st.session_state.db['merchants'][n_name] = {"wallet": n_wallet, "fee": n_fee, "note": n_note}
            save_data(st.session_state.db); st.rerun()
            
    st.divider()
    for name in sorted(st.session_state.db['merchants'].keys()):
        with st.expander(f"📦 {name} 수정/삭제"):
            info = st.session_state.db['merchants'][name]
            st.session_state.db['merchants'][name]['wallet'] = st.text_input("지갑", value=info['wallet'], key=f"w_{name}")
            st.session_state.db['merchants'][name]['fee'] = st.text_input("요율", value=info['fee'], key=f"f_{name}")
            st.session_state.db['merchants'][name]['note'] = st.text_input("비고", value=info.get('note',''), key=f"n_{name}")
            if st.button("변경저장", key=f"s_{name}"): save_data(st.session_state.db); st.rerun()
            if st.button("삭제", key=f"d_{name}"): 
                del st.session_state.db['merchants'][name]
                save_data(st.session_state.db); st.rerun()
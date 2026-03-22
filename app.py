# -*- coding: utf-8 -*-
import streamlit as st
import streamlit.components.v1 as components
import math, json, os, re

# ============================================================
# 정산 매크로 v94.9 - [Syntax Error 수정 / 01번 2열 / 06번 3열]
# ============================================================

DB_FILE = "merchants_v20.json"

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
        js = f"<script>navigator.clipboard.writeText(`{content}`);</script>"
        components.html(js, height=0)
        st.toast("복사 완료")

st.set_page_config(page_title="정산 매크로 v94.9", layout="centered")

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

    # 01. 정산 환율 및 요청 (2열 구도)
    st.markdown('<div class="label-header">01. 정산 환율 및 요청</div>', unsafe_allow_html=True)
    sel_p = st.radio("적용 배수", ["4%", "4.5%", "5%"], index=0, horizontal=True)
    m_map = {"4%": 1.04, "4.5%": 1.045, "5%": 1.05}
    
    sc1, sc2 = st.columns(2)
    with sc1: sb_val = extract_int(st.text_input("빗썸 시세", key="s_b"))
    with sc2: ss_val = extract_int(st.text_input("수동 환율", key="s_s"))
    s_rate = ss_val if ss_val > 0 else math.ceil(sb_val * m_map[sel_p])
    
    if s_rate > 0:
        st.markdown(f'<div class="rate-guide">>>> 적용 환율 1usdt = {fmt(s_rate)} krw</div>', unsafe_allow_html=True)
    
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
        w_msg = f"Hello, Team\nCurrently, the balance of the merchants is too high.\nTo ensure a safe balance, please proceed with USDT settlement.\nThank you\n\nBalance update\n\n- {selected_m} : {fmt(w_bal)} krw"
        editable_box(w_msg, "red", box_id="res_04")

    # 05. 환전(Payout) 요청
    st.markdown('<div class="label-header">05. 환전(Payout) 요청</div>', unsafe_allow_html=True)
    p_amt = extract_int(st.text_input("환전 금액 (KRW)", key="p_amt"))
    if p_amt > 0:
        p_msg = f"payout request\n\nmid : {selected_m}\npayout amount : {fmt(p_amt)} krw\n\nPlease check..."
        editable_box(p_msg, "blue", box_id="res_05")

    st.divider()
    # 06. TOP-UP 요청 (3열 가로 구도)
    st.markdown('<div class="label-header" style="color:#2ecc71;">06. TOP-UP 요청</div>', unsafe_allow_html=True)
    t1, t2, t3 = st.columns(3)
    with t1: tb_val = extract_int(st.text_input("탑업 시세(빗썸)", key="t_b"))
    with t2: tu_amt = extract_int(st.text_input("수량(USDT)", key="t_u"))
    with t3: ts_val = extract_int(st.text_input("수동 환율", key="t_s"))
    
    t_rate = ts_val if ts_val > 0 else (tb_val - math.ceil(tb_val * 0.005) if tb_val > 0 else 0)
    if t_rate > 0:
        st.markdown(f'<div class="rate-guide">>>> 적용 환율 1usdt = {fmt(t_rate)} krw</div>', unsafe_allow_html=True)
        if tu_amt > 0:
            total_t_krw = tu_amt * t_rate
            my_w = st.session_state.db.get('my_wallet', '')
            t_msg = f"top-up\n\nmid : {selected_m}\ntop-up amount : {fmt(tu_amt)} usdt\nexchange to KRW : {fmt(total_t_krw)} krw\n1usdt = {fmt(t_rate)} krw\n\n{my_w}\n\nPlease check..."
            editable_box(t_msg, "green", box_id="res_06_req")
            
            base_p = ts_val if ts_val > 0 else tb_val
            t_markup = math.ceil((tu_amt * base_p) * (m_fee / 100))
            f_msg = f"드래곤 테더탑업 마크업 {m_fee}% {selected_m} / {fmt(tu_amt * base_p)} / {fmt(t_markup)}"
            editable_box(f_msg, "yellow", box_id="res_06_fee")

elif st.session_state.page == 'admin':
    st.title("⚙️ 머천트 및 지갑 설정")
    my_w = st.text_input("내 USDT 지갑 주소", value=st.session_state.db.get('my_wallet', ''))
    if st.button("지갑 저장"):
        st.session_state.db['my_wallet'] = my_w
        save_data(st.session_state.db); st.success("저장 완료")
    
    st.divider()
    for name in sorted(st.session_state.db['merchants'].keys()):
        with st.expander(f"📦 {name} 관리"):
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
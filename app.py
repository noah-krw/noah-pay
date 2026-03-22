# -*- coding: utf-8 -*-
import streamlit as st
import streamlit.components.v1 as components
import math, json, os, re

# ============================================================
# 정산 매크로 v95.0 - [01번/06번 구도 완전 분리 + 복사버튼 강화]
# ============================================================

DB_FILE = "merchants_v21.json"

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

# [개선] 텍스트가 비어있어도 박스를 보여주어 "건너뛰는 느낌" 제거
def editable_box(text, color_type="blue", box_id="default", placeholder="내용을 입력하면 여기에 멘트가 생성됩니다"):
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
        js = f"<script>navigator.clipboard.writeText(`{content}`);</script>"
        components.html(js, height=0)
        st.toast("복사 완료!")

st.set_page_config(page_title="정산 매크로 v95.0", layout="centered")

# v89.8 디자인 (흰색 입력창 + 금색 굵은 글자)
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
    # spfxm 기본 고정
    default_idx = sorted_keys.index('spfxm') if 'spfxm' in sorted_keys else 0
    selected_m = st.selectbox("업체 선택", sorted_keys, index=default_idx)
    m_info = merchants[selected_m]
    
    st.info(f"📝 비고: {m_info.get('note', '')}")

    # 01. 정산 환율 및 요청
    st.markdown('<div class="label-header">01. 정산 환율 및 요청</div>', unsafe_allow_html=True)
    sel_p = st.radio("적용 배수", ["4%", "4.5%", "5%"], index=0, horizontal=True)
    m_map = {"4%": 1.04, "4.5%": 1.045, "5%": 1.05}
    
    sc1, sc2 = st.columns(2)
    with sc1: sb_val = extract_int(st.text_input("빗썸 시세", key="s_b"))
    with sc2: ss_val = extract_int(st.text_input("수동 환율", key="s_s"))
    s_rate = ss_val if ss_val > 0 else math.ceil(sb_val * m_map[sel_p])
    
    # [개선] 환율 가이드도 복사 가능한 박스로 구현
    if s_rate > 0:
        st.write("▼ 적용 환율 (복사 가능)")
        editable_box(f"1usdt = {fmt(s_rate)} krw", "sky", "rate_copy_01")
    
    amt = extract_int(st.text_input("정산 금액 (KRW)", key="s_amt"))
    
    # [개선] amt가 0이어도 박스 틀을 유지하여 "건너뛰기" 방지
    s_msg = ""
    if amt > 0 and s_rate > 0:
        u_val = round(amt / s_rate, 2)
        s_msg = f"- {selected_m} settlement amount : {fmt(amt)} krw\n- exchange to usdt : {u_val:,.2f} usdt\n- 1usdt = {fmt(s_rate)} krw\n\n{m_info['wallet']}\n\nPlease confirm the address and calculation.\nOnce approved, we will proceed immediately"
    editable_box(s_msg, "blue", "res_01", "금액을 입력하면 정산 멘트가 생성됩니다")

    # 02. 잔액 보고
    st.markdown('<div class="label-header">02. 최종 잔액 보고</div>', unsafe_allow_html=True)
    bal_in = extract_int(st.text_input("현재 잔액 입력 (KRW)", key="bal_in"))
    b_msg = ""
    if bal_in > 0 and amt > 0:
        u_ceil = math.ceil(amt / s_rate)
        b_msg = f"Balance & settlement update\n\n- {selected_m}\nsettlement amount : {fmt(amt)} krw\nexchange to usdt : {fmt(u_ceil)} usdt\n1usdt = {fmt(s_rate)} krw\n\n- {selected_m} : {fmt(bal_in)} krw"
    editable_box(b_msg, "green", "res_02", "잔액을 입력하면 보고 메시지가 생성됩니다")

    # 03. 마크업 수수료
    st.markdown('<div class="label-header">03. 마크업 수수료</div>', unsafe_allow_html=True)
    m_fee = float(m_info.get('fee', 0.5))
    markup_msg = ""
    if amt > 0:
        markup = math.ceil(amt * (m_fee / 100))
        markup_msg = f"드래곤 테더정산 마크업 {m_fee}% {selected_m} / {fmt(amt)} / {fmt(markup)}"
    editable_box(markup_msg, "yellow", "res_03", "수수료 내역")

    # 04. 잔액 경고 / 05. 환전은 기존과 동일하게 유지...

    st.divider()
    # 06. TOP-UP 요청 (그림판 3열 완결본)
    st.markdown('<div class="label-header" style="color:#2ecc71;">06. TOP-UP 요청</div>', unsafe_allow_html=True)
    t1, t2, t3 = st.columns(3)
    with t1: tb_val = extract_int(st.text_input("탑업 시세(빗썸)", key="t_b"))
    with t2: tu_amt = extract_int(st.text_input("수량(USDT)", key="t_u"))
    with t3: ts_val = extract_int(st.text_input("수동 환율", key="t_s"))
    
    t_rate = ts_val if ts_val > 0 else (tb_val - math.ceil(tb_val * 0.005) if tb_val > 0 else 0)
    
    if t_rate > 0:
        st.write("▼ 적용 환율 (복사 가능)")
        editable_box(f"1usdt = {fmt(t_rate)} krw", "sky", "rate_copy_06")
        
        t_msg, f_msg = "", ""
        if tu_amt > 0:
            total_t_krw = tu_amt * t_rate
            my_w = st.session_state.db.get('my_wallet', '')
            t_msg = f"top-up\n\nmid : {selected_m}\ntop-up amount : {fmt(tu_amt)} usdt\nexchange to KRW : {fmt(total_t_krw)} krw\n1usdt = {fmt(t_rate)} krw\n\n{my_w}\n\nPlease check..."
            
            base_p = ts_val if ts_val > 0 else tb_val
            t_markup = math.ceil((tu_amt * base_p) * (m_fee / 100))
            f_msg = f"드래곤 테더탑업 마크업 {m_fee}% {selected_m} / {fmt(tu_amt * base_p)} / {fmt(t_markup)}"
        
        # 그림판 구도: 결과 박스 2개 나란히 배치
        editable_box(t_msg, "green", "res_06_req", "탑업 요청 멘트")
        editable_box(f_msg, "yellow", "res_06_fee", "탑업 수수료 내역")

# 머천트 관리 페이지는 생략(기존 동일)
# -*- coding: utf-8 -*-
import streamlit as st
import streamlit.components.v1 as components
import math
import json
import os
import re

# ============================================================
# 정산 매크로 v91.5 - 누락 기능(잔액보고/경고) 전체 복구 완료
# ============================================================

DB_FILE = "merchants_v2.json"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if 'merchants' not in data: data['merchants'] = {}
                if 'my_wallets' not in data: data['my_wallets'] = {'tl': '', 'ada': ''}
                return data
        except: pass
    return {'my_wallets': {'tl': '', 'ada': ''}, 'merchants': {}}

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def extract_int(text):
    if not text: return 0
    num_str = re.sub(r'[^0-9]', '', str(text))
    return int(num_str) if num_str else 0

def fmt(n): return f"{n:,}"

def copy_box(text, color_type="blue", key=None):
    colors = {"blue": "#4a90d9", "green": "#27ae60", "yellow": "#f39c12", "red": "#e74c3c"}
    bg_colors = {"blue": "#060d18", "green": "#06180d", "yellow": "#181406", "red": "#180606"}
    c, bg = colors.get(color_type, "#4a90d9"), bg_colors.get(color_type, "#060d18")
    line_count = text.count("\n") + 1
    box_height = 68 if line_count == 1 else (line_count * 25) + 40
    st.markdown(f"""<style>.stTextArea textarea[key="{key}"] {{ background-color: {bg} !important; color: {c} !important; border-left: 4px solid {c} !important; font-family: monospace !important; font-size: 15px !important; }}</style>""", unsafe_allow_html=True)
    edited_text = st.text_area("수정", value=text, height=box_height, key=key, label_visibility="collapsed")
    if st.button("📋 복사", key=f"btn_{key}"):
        js = f"<script>navigator.clipboard.writeText(`{edited_text}`);</script>"
        components.html(js, height=0); st.toast("복사 완료!")

st.set_page_config(page_title="정산 매크로 v91.5", layout="centered")
if 'db' not in st.session_state: st.session_state.db = load_data()
if 'page' not in st.session_state: st.session_state.page = 'settle'

with st.sidebar:
    st.title("💹 정산 매크로")
    if st.button("🚀 정산 작업"): st.session_state.page = 'settle'; st.rerun()
    if st.button("⚙️ 머천트 관리"): st.session_state.page = 'admin'; st.rerun()

if st.session_state.page == 'settle':
    st.title("🚀 실시간 정산 작업")
    merchants = st.session_state.db.get('merchants', {})
    if not merchants:
        st.error("등록된 머천트가 없습니다. 관리 페이지에서 등록해 주세요.")
    else:
        selected_m = st.selectbox("업체 선택", sorted(list(merchants.keys())))
        m_info = merchants[selected_m]
        m_fee = float(m_info.get('fee', 0.5))
        
        # 01. 환율 설정
        st.markdown("### 01. 환율 설정")
        m_map = {"4%": 1.04, "4.5%": 1.045, "5%": 1.05}
        sel_label = st.radio("배수", list(m_map.keys()), horizontal=True, label_visibility="collapsed")
        c1, c2 = st.columns(2)
        with c1: b_val = extract_int(st.text_input("빗썸 시세", key="b_val", value="0"))
        with c2: s_val = extract_int(st.text_input("수동 환율", key="s_val", value="0"))
        rate = s_val if s_val > 0 else math.ceil(b_val * m_map[sel_label])
        if rate > 0: copy_box(f"1 USDT = {fmt(rate)} KRW", "blue", key="r_res")

        # 02. 정산 요청
        st.markdown("### 02. 정산 요청")
        amt = extract_int(st.text_input("정산 금액 (KRW)", key="amt_in"))
        if amt > 0:
            u_val = round(amt / rate, 2)
            copy_box(f"- {selected_m} settlement amount : {fmt(amt)} krw\n- exchange to usdt : {u_val:,.2f} usdt\n- 1usdt = {fmt(rate)} krw\n\n{m_info['wallet']}\n\nPlease confirm...", "blue", key="s_res")

        # 03. 최종 잔액 보고 (복구)
        st.markdown("### 03. 최종 잔액 보고")
        bal_in = extract_int(st.text_input("현재 잔액 입력 (KRW)", key="bal_in"))
        if bal_in > 0 and amt > 0:
            u_ceil = math.ceil(amt / rate)
            copy_box(f"Balance & settlement update\n\n- {selected_m}\nsettlement amount : {fmt(amt)} krw\nexchange to usdt : {fmt(u_ceil)} usdt\n1usdt = {fmt(rate)} krw\n\n- {selected_m} : {fmt(bal_in)} krw", "green", key="bal_res")

        # 04. 마크업 보고
        st.markdown("### 04. 마크업 보고")
        if amt > 0:
            markup = math.ceil(amt * (m_fee / 100))
            copy_box(f"드래곤 테더정산 마크업 {m_fee}% {selected_m} / {fmt(amt)} / {fmt(markup)}", "yellow", key="f_res")

        # 05. 잔액 경고 (복구)
        st.markdown("### 05. 잔액 경고")
        warn_in = extract_int(st.text_input("경고용 잔액 입력", key="warn_in"))
        if warn_in > 0:
            copy_box(f"Hello, Team\nCurrently, the balance of the merchants is too high.\nTo ensure a safe balance, please proceed with USDT settlement.\nThank you\n\nBalance update\n\n- {selected_m} : {fmt(warn_in)} krw", "red", key="w_res")

        # 06. TOP-UP 요청
        st.divider()
        st.markdown("### 06. TOP-UP 요청")
        cl, cr = st.columns([1, 1.2])
        with cl: tm_rate = extract_int(st.text_input("탑업 빗썸 시세", key="tm_rate"))
        with cr: t_usdt = extract_int(st.text_input("탑업 USDT 수량", key="t_usdt"))
        t_rate = tm_rate - math.ceil(tm_rate * 0.005) if tm_rate > 0 else 0
        if t_usdt > 0 and t_rate > 0:
            my_w = st.session_state.db.get('my_wallets', {'tl': '', 'ada': ''})
            copy_box(f"top-up\n\nmid : {selected_m}\ntop-up amount : {fmt(t_usdt)} usdt\nexchange to KRW : {fmt(t_usdt * t_rate)} krw\n1usdt = {fmt(t_rate)} krw\n\n{my_w['tl']}\n\nPlease check...", "green", key="t_res")
            t_markup = math.ceil((t_usdt * t_rate) * (m_fee / 100))
            copy_box(f"드래곤 테더탑업 마크업 {m_fee}% {selected_m} / {fmt(t_usdt * t_rate)} / {fmt(t_markup)}", "yellow", key="tf_res")

elif st.session_state.page == 'admin':
    st.title("⚙️ 머천트 및 마크업 관리")
    w_db = st.session_state.db.get('my_wallets', {'tl': '', 'ada': ''})
    with st.form("w_f"):
        c1, c2 = st.columns(2)
        utl, uada = c1.text_input("우리지갑 TL", value=w_db['tl']), c2.text_input("우리지갑 ADA", value=w_db['ada'])
        if st.form_submit_button("지갑 저장"):
            st.session_state.db['my_wallets'] = {'tl': utl, 'ada': uada}; save_data(st.session_state.db); st.rerun()

    with st.form("n_f"):
        n1, n2, n3 = st.columns([1, 2, 1])
        name, wal, fee = n1.text_input("업체명"), n2.text_input("지갑주소"), n3.text_input("마크업 요율 %", value="0.5")
        memo = st.text_area("비고 (Memo)")
        if st.form_submit_button("업체 등록"):
            if name: st.session_state.db['merchants'][name] = {"wallet": wal, "fee": fee, "memo": memo}; save_data(st.session_state.db); st.rerun()

    merchants = st.session_state.db.get('merchants', {})
    for m_name in sorted(merchants.keys()):
        with st.expander(f"📦 {m_name}"):
            info = merchants[m_name]
            u_w = st.text_input("지갑", value=info['wallet'], key=f"w_{m_name}")
            u_f = st.text_input("마크업 요율 %", value=info['fee'], key=f"f_{m_name}")
            u_m = st.text_area("비고", value=info.get('memo', ''), key=f"m_{m_name}")
            if st.button("수정 저장", key=f"s_{m_name}"):
                st.session_state.db['merchants'][m_name] = {"wallet": u_w, "fee": u_f, "memo": u_m}; save_data(st.session_state.db); st.rerun()
            if st.button("삭제", key=f"d_{m_name}"):
                del st.session_state.db['merchants'][m_name]; save_data(st.session_state.db); st.rerun()
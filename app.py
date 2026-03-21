# -*- coding: utf-8 -*-
import streamlit as st
import streamlit.components.v1 as components
import math
import json
import os
import re
from datetime import datetime

# ============================================================
# 정산 매크로 v2.1
# ============================================================

DB_FILE = "merchants.json"

# ─── 데이터 관리 ─────────────────────────────────────────

def get_default_list():
    return {
        'dr188':      {'wallet': 'TBMTb9TFFXDuqhjLKLp9Yo26QHRnnG6jPN', 'fee': '0.5',  'group': 'dragon',  'note': '드래곤 메인'},
        'drgtssen':   {'wallet': 'TRX_Wallet_drgtssen',                  'fee': '0.5',  'group': 'dragon',  'note': ''},
        'Dpinnacle':  {'wallet': 'TRX_Wallet_Dpinnacle',                 'fee': '0.5',  'group': 'dragon',  'note': ''},
        'drSpinmama': {'wallet': 'TRX_Wallet_drSpinmama',                'fee': '0.5',  'group': 'dragon',  'note': ''},
        'drbetssen':  {'wallet': 'TRX_Wallet_drbetssen',                 'fee': '0.5',  'group': 'dragon',  'note': ''},
        'NextbetM/G': {'wallet': 'TRX_Wallet_Nextbet',                   'fee': '0.5',  'group': 'dragon',  'note': ''},
        'DafabetM/G': {'wallet': 'TRX_Wallet_Dafabet',                   'fee': '4.5',  'group': 'dragon',  'note': ''},
        'drgtkore':   {'wallet': 'TRX_Wallet_drgtkore',                  'fee': '0.5',  'group': 'dragon',  'note': ''},
        'drolymp':    {'wallet': 'TRX_Wallet_drolymp',                   'fee': '0.5',  'group': 'dragon',  'note': ''},
        'drbetkore':  {'wallet': 'TRX_Wallet_drbetkore',                 'fee': '0.5',  'group': 'dragon',  'note': ''},
        'drTapTap':   {'wallet': 'TRX_Wallet_drTapTap',                  'fee': '0.5',  'group': 'dragon',  'note': ''},
        'spfxm':      {'wallet': 'TWbFbzW5GRkAkVrY4fLuXhNA576DCkoGbh',  'fee': '4',    'group': 'general', 'note': '가장 많이 쓰는 업체'},
        'V99':        {'wallet': 'TRX_Wallet_V99',                       'fee': '1.5',  'group': 'general', 'note': 'VVIP 전용'},
    }

def load_data():
    defaults = get_default_list()
    if not os.path.exists(DB_FILE):
        save_data(defaults)
        return defaults
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            db = json.load(f)
            for k, v in db.items():
                if 'group' not in v:
                    v['group'] = 'dragon' if (k.startswith('dr') or k in ['NextbetM/G','DafabetM/G','Dpinnacle']) else 'general'
            return db if len(db) >= 1 else defaults
    except Exception:
        return defaults

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ─── 유틸 ────────────────────────────────────────────────

def extract_int(text: str) -> int:
    num_str = re.sub(r'[^0-9]', '', str(text))
    return int(num_str) if num_str else 0

def fmt(n: int) -> str:
    return f"{n:,}"

DRAGON_KEYS = {
    'dr188','drgtssen','Dpinnacle','drSpinmama','drbetssen',
    'NextbetM/G','DafabetM/G','drgtkore','drolymp','drbetkore','drTapTap','spfxm'
}

# ─── 복사 가능한 결과 박스 ───────────────────────────────

def copy_box(text: str, color: str = "blue"):
    color_map = {
        "blue":   {"border": "#4a90d9", "text": "#a8c7e8"},
        "green":  {"border": "#27ae60", "text": "#7dcea0"},
        "yellow": {"border": "#f39c12", "text": "#f8c471"},
        "red":    {"border": "#e74c3c", "text": "#f1948a"},
    }
    c = color_map.get(color, color_map["blue"])
    js_text = json.dumps(text)
    line_count = text.count("\n") + 1
    height = max(72, line_count * 23 + 52)

    html_code = f"""<!DOCTYPE html><html><head><style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:transparent;font-family:'IBM Plex Mono','Courier New',monospace;}}
.wrap{{position:relative;background:#060d18;border:1px solid #1e3a5f;
  border-left:3px solid {c['border']};border-radius:6px;
  padding:12px 80px 12px 14px;font-size:13px;line-height:1.8;
  color:{c['text']};white-space:pre-wrap;word-break:break-all;}}
.btn{{position:absolute;top:8px;right:8px;background:#0f2040;color:#5dade2;
  border:1px solid #1e3a5f;border-radius:4px;padding:3px 10px;
  font-family:monospace;font-size:12px;font-weight:600;cursor:pointer;}}
.btn:hover{{background:#1a3a6c;color:#a8d4f5;}}
</style></head><body>
<div class="wrap">
  <button class="btn" id="btn" onclick="
    navigator.clipboard.writeText({js_text}).then(function(){{
      var b=document.getElementById('btn');
      b.innerText='✅ 복사됨';b.style.color='#27ae60';
      setTimeout(function(){{b.innerText='📋 복사';b.style.color='';
      }},1500);
    }});">📋 복사</button>{text}</div>
</body></html>"""
    components.html(html_code, height=height, scrolling=False)

# ─── 숫자 입력 + 콤마 확인 표시 ─────────────────────────

def num_input(label: str, key: str, placeholder: str = "0") -> int:
    val_raw = st.text_input(label, value="", placeholder=placeholder, key=key)
    val = extract_int(val_raw)
    if val > 0:
        st.markdown(
            f"<div style='margin-top:-10px;margin-bottom:6px;"
            f"font-family:IBM Plex Mono,monospace;font-size:0.82em;"
            f"color:#f1c40f;padding-left:4px;'>→ {fmt(val)}</div>",
            unsafe_allow_html=True
        )
    return val

# ─── 스텝 구분선 ─────────────────────────────────────────

def divider(label: str):
    st.markdown(
        f"<div style='margin:22px 0 10px;font-family:IBM Plex Mono,monospace;"
        f"font-size:0.7em;font-weight:600;letter-spacing:0.12em;color:#4a90d9;"
        f"text-transform:uppercase;border-bottom:1px solid #1e2d45;padding-bottom:6px;'>"
        f"{label}</div>",
        unsafe_allow_html=True
    )

# ─── 페이지 설정 ─────────────────────────────────────────

st.set_page_config(page_title="정산 매크로 v2.1", layout="centered", page_icon="💹")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans+KR:wght@300;400;600&display=swap');

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background: #0a0e17 !important;
    color: #c8d6e5 !important;
    font-family: 'IBM Plex Sans KR', sans-serif !important;
}
[data-testid="stSidebar"] {
    background: #0d1220 !important;
    border-right: 1px solid #1e2d45 !important;
}

/* 흰색 입력칸 */
div[data-baseweb="input"] > div {
    background: #ffffff !important;
    border: 1px solid #4a90d9 !important;
    border-radius: 6px !important;
}
input {
    color: #0a0e17 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 1em !important;
    font-weight: 700 !important;
}
input::placeholder { color: #9aaabf !important; font-weight: 400 !important; }

div[data-baseweb="select"] > div {
    background: #0d1525 !important;
    border: 1px solid #1e3055 !important;
}

.stButton > button {
    width: 100% !important;
    background: #0f2040 !important;
    color: #5dade2 !important;
    border: 1px solid #1e3a5f !important;
    border-radius: 6px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-weight: 600 !important;
    font-size: 0.85em !important;
}
.stButton > button:hover {
    background: #1a3a6c !important;
    border-color: #4a90d9 !important;
    color: #a8d4f5 !important;
}

div[role="radiogroup"] label { color: #8ab4d4 !important; font-size: 0.9em !important; }

button[data-baseweb="tab"] {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.82em !important;
    letter-spacing: 0.08em !important;
    color: #4a6080 !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #4a90d9 !important;
    border-bottom: 2px solid #4a90d9 !important;
}
section[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: 1px solid #1e3055 !important;
    color: #8ab4d4 !important;
    text-align: left !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: #111827 !important;
    color: #5dade2 !important;
}
hr { border-color: #1e2d45 !important; }
</style>
""", unsafe_allow_html=True)

# ─── 세션 초기화 ─────────────────────────────────────────

if 'db'   not in st.session_state: st.session_state.db   = load_data()
if 'page' not in st.session_state: st.session_state.page = 'settle'

# ─── 사이드바 ────────────────────────────────────────────

with st.sidebar:
    st.markdown("### 💹 정산 매크로")
    st.markdown(f"<small style='color:#2a4060;'>{datetime.now().strftime('%Y-%m-%d %H:%M')}</small>", unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🚀  정산 작업"):   st.session_state.page = 'settle'
    if st.button("⬆️  탑업 요청"):   st.session_state.page = 'topup'
    if st.button("⚙️  머천트 설정"): st.session_state.page = 'admin'
    st.markdown("---")
    mc = len(st.session_state.db)
    dc = sum(1 for v in st.session_state.db.values() if v.get('group') == 'dragon')
    st.markdown(f"<small style='color:#2a5070;'>머천트 {mc}개 · 드래곤 {dc}개</small>", unsafe_allow_html=True)

# ════════════════════════════════════════════════
#  PAGE 1 : 정산 작업
# ════════════════════════════════════════════════

if st.session_state.page == 'settle':

    st.markdown("## 🚀 정산 작업")

    sorted_keys   = sorted(st.session_state.db.keys())
    default_index = sorted_keys.index('spfxm') if 'spfxm' in sorted_keys else 0
    selected_m    = st.selectbox("**업체 선택**", sorted_keys, index=default_index)
    m_info        = st.session_state.db[selected_m]
    fee_rate      = float(m_info.get('fee', 0.5))
    is_dragon     = m_info.get('group', 'general') == 'dragon'
    badge_bg      = "#1a3a5c" if is_dragon else "#1a3a1a"
    badge_fg      = "#5dade2" if is_dragon else "#58d68d"
    badge_label   = "드래곤" if is_dragon else "일반"

    st.markdown(
        f"<div style='margin-bottom:20px;'>"
        f"<span style='font-size:1.05em;font-weight:600;'>{selected_m}</span>"
        f"<span style='display:inline-block;padding:2px 10px;border-radius:20px;"
        f"font-size:0.75em;font-weight:600;font-family:IBM Plex Mono,monospace;"
        f"margin-left:8px;background:{badge_bg};color:{badge_fg};'>{badge_label}</span>"
        f"<span style='display:inline-block;padding:2px 10px;border-radius:20px;"
        f"font-size:0.75em;font-weight:600;font-family:IBM Plex Mono,monospace;"
        f"margin-left:6px;background:#1a1a2e;color:#8888aa;'>수수료 {fee_rate}%</span>"
        f"</div>",
        unsafe_allow_html=True
    )

    # STEP 1: 환율 설정
    divider("01 / 환율 설정")
    multiplier = st.radio(
        "배수 선택",
        [1.04, 1.045, 1.05],
        format_func=lambda x: f"×{x}  ({(x-1)*100:.1f}%)",
        index=0, horizontal=True
    )
    c1, c2 = st.columns(2)
    with c1: b_val = num_input("빗썸 시세", "b_val", "예: 1450000")
    with c2: s_val = num_input("수동 환율", "s_val", "직접 입력")

    current_rate = s_val if s_val > 0 else (math.ceil(b_val * multiplier) if b_val > 0 else 0)

    if current_rate > 0:
        copy_box(f"1 USDT = {fmt(current_rate)} KRW", "blue")

    # STEP 2: 정산 요청
    divider("02 / 정산 요청")
    if current_rate == 0:
        st.markdown("<small style='color:#4a6880;'>환율을 먼저 입력해 주세요.</small>", unsafe_allow_html=True)
        amount = 0
    else:
        amount = num_input("정산 금액 (KRW)", "amount", "예: 10000000")
        if amount > 0:
            usdt_val   = round(amount / current_rate, 2)
            settle_msg = (
                f"- {selected_m} settlement amount : {fmt(amount)} krw\n"
                f"- exchange to usdt : {usdt_val:,.2f} usdt\n"
                f"- 1usdt = {fmt(current_rate)} krw\n\n"
                f"{m_info['wallet']}\n\n"
                f"Please confirm the address and calculation.\n"
                f"Once approved, we will proceed immediately"
            )
            copy_box(settle_msg, "blue")

    # STEP 3: 잔액 보고
    divider("03 / 잔액 보고")
    if current_rate == 0 or amount == 0:
        st.markdown("<small style='color:#4a6880;'>환율과 정산 금액을 먼저 입력해 주세요.</small>", unsafe_allow_html=True)
    else:
        balance = num_input("현재 잔액 (KRW)", "balance", "예: 5000000")
        if balance > 0:
            usdt_ceil   = math.ceil(amount / current_rate)
            balance_msg = (
                f"Balance & settlement update\n\n"
                f"- {selected_m}\n"
                f"settlement amount : {fmt(amount)} krw\n"
                f"exchange to usdt : {fmt(usdt_ceil)} usdt\n"
                f"1usdt = {fmt(current_rate)} krw\n\n"
                f"- {selected_m} : {fmt(balance)} krw"
            )
            copy_box(balance_msg, "green")

    # STEP 4: 수수료 마크업 (자동)
    if amount > 0:
        divider("04 / 수수료 마크업")
        calc_fee   = math.ceil(amount * (fee_rate / 100))
        prefix     = "드래곤 테더정산" if selected_m in DRAGON_KEYS else "일반 테더정산"
        markup_msg = f"{prefix} 수수료 {fee_rate}% {selected_m} / {fmt(amount)} / {fmt(calc_fee)}"
        copy_box(markup_msg, "yellow")

    # STEP 5: 잔액 경고
    divider("05 / 잔액 경고")
    warn_bal = num_input("경고 잔액 (KRW)", "warn_bal", "예: 500000")
    if warn_bal > 0:
        copy_box(f"Balance update - {selected_m} : {fmt(warn_bal)} krw", "red")


# ════════════════════════════════════════════════
#  PAGE 2 : 탑업 요청
# ════════════════════════════════════════════════

elif st.session_state.page == 'topup':

    st.markdown("## ⬆️ 탑업 요청")

    sorted_keys   = sorted(st.session_state.db.keys())
    default_index = sorted_keys.index('spfxm') if 'spfxm' in sorted_keys else 0
    selected_m    = st.selectbox("**업체 선택**", sorted_keys, index=default_index)
    m_info        = st.session_state.db[selected_m]

    divider("01 / 탑업 환율 (0.5% 차감)")
    c1, c2 = st.columns(2)
    with c1: t_market = num_input("빗썸 시세", "t_m_rate", "예: 1450000")
    with c2: t_manual = num_input("수동 환율", "t_s_rate", "직접 입력")

    if t_manual > 0:
        final_rate = t_manual
    elif t_market > 0:
        final_rate = t_market - math.ceil(t_market * 0.005)
    else:
        final_rate = 0

    if final_rate > 0:
        copy_box(f"1 USDT = {fmt(final_rate)} KRW", "blue")

    divider("02 / 탑업 수량")
    if final_rate == 0:
        st.markdown("<small style='color:#4a6880;'>환율을 먼저 입력해 주세요.</small>", unsafe_allow_html=True)
    else:
        topup_usdt = num_input("탑업 USDT 수량", "t_usdt", "예: 10000")
        if topup_usdt > 0:
            total_krw = topup_usdt * final_rate
            topup_msg = (
                f"top-up\n\n"
                f"mid : {selected_m}\n"
                f"top-up amount : {fmt(topup_usdt)} usdt\n"
                f"exchange to KRW : {fmt(total_krw)} krw\n"
                f"1usdt = {fmt(final_rate)} krw\n\n"
                f"{m_info['wallet']}\n\n"
                f"Please check the invoice and transfer the USDT to the address provided."
            )
            copy_box(topup_msg, "green")

            base_rate = t_manual if t_manual > 0 else t_market
            if base_rate > 0:
                divider("03 / 수수료 마크업")
                total_market = topup_usdt * base_rate
                total_fee    = math.ceil(total_market * 0.005)
                copy_box(f"드래곤 테더탑업 수수료 0.5% {selected_m} / {fmt(total_market)} / {fmt(total_fee)}", "yellow")


# ════════════════════════════════════════════════
#  PAGE 3 : 머천트 설정
# ════════════════════════════════════════════════

else:
    st.markdown("## ⚙️ 머천트 설정")

    with st.expander("➕ 신규 업체 등록", expanded=False):
        with st.form("new_merchant", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                n_name   = st.text_input("업체 이름",       key="new_name")
                n_wallet = st.text_input("지갑 주소",       key="new_wallet")
            with c2:
                n_fee    = st.text_input("수수료 요율 (%)", value="0.5", key="new_fee")
                n_group  = st.selectbox("그룹", ["dragon", "general"], key="new_group")
                n_note   = st.text_input("비고",             key="new_note")
            if st.form_submit_button("✅ 등록 완료"):
                if n_name and n_wallet:
                    st.session_state.db[n_name] = {
                        "wallet": n_wallet, "fee": n_fee,
                        "group": n_group, "note": n_note
                    }
                    save_data(st.session_state.db)
                    st.success(f"{n_name} 등록 완료!")
                    st.rerun()
                else:
                    st.warning("업체 이름과 지갑 주소는 필수입니다.")

    st.markdown("---")
    st.markdown("#### 📂 업체 목록")

    tab_all, tab_dragon, tab_general = st.tabs(["전체", "🐉 드래곤", "🟢 일반"])

    def render_merchant_list(keys, tab_prefix: str):
        # tab_prefix 로 위젯 key 중복 방지 (DuplicateElementKey 해결)
        for orig_name in sorted(keys):
            info = st.session_state.db.get(orig_name, {})
            with st.expander(f"**{orig_name}**  —  수수료 {info.get('fee','?')}%"):
                c1, c2 = st.columns(2)
                with c1:
                    new_nm = st.text_input("업체명",    value=orig_name,              key=f"{tab_prefix}_nm_{orig_name}")
                    u_w    = st.text_input("지갑 주소", value=info.get('wallet',''),   key=f"{tab_prefix}_w_{orig_name}")
                with c2:
                    u_f    = st.text_input("요율",      value=info.get('fee','0.5'),   key=f"{tab_prefix}_f_{orig_name}")
                    u_g    = st.selectbox(
                        "그룹", ["dragon","general"],
                        index=0 if info.get('group','dragon') == 'dragon' else 1,
                        key=f"{tab_prefix}_g_{orig_name}"
                    )
                    u_n    = st.text_input("비고",      value=info.get('note',''),     key=f"{tab_prefix}_n_{orig_name}")

                b1, b2 = st.columns(2)
                with b1:
                    if st.button("💾 저장", key=f"{tab_prefix}_s_{orig_name}"):
                        if new_nm != orig_name and orig_name in st.session_state.db:
                            del st.session_state.db[orig_name]
                        st.session_state.db[new_nm] = {
                            "wallet": u_w, "fee": u_f,
                            "group": u_g, "note": u_n
                        }
                        save_data(st.session_state.db)
                        st.success(f"{new_nm} 저장 완료!")
                        st.rerun()
                with b2:
                    if st.button("🗑️ 삭제", key=f"{tab_prefix}_d_{orig_name}"):
                        if orig_name in st.session_state.db:
                            del st.session_state.db[orig_name]
                            save_data(st.session_state.db)
                        st.rerun()

    all_keys     = list(st.session_state.db.keys())
    dragon_keys  = [k for k in all_keys if st.session_state.db[k].get('group') == 'dragon']
    general_keys = [k for k in all_keys if st.session_state.db[k].get('group') != 'dragon']

    with tab_all:     render_merchant_list(all_keys,     "all")
    with tab_dragon:  render_merchant_list(dragon_keys,  "drg")
    with tab_general: render_merchant_list(general_keys, "gen")
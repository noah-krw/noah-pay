import streamlit as st
import math
import json
import os
import re
from datetime import datetime

# ============================================================
# 정산 매크로 v2.0 - UI/UX 개선 + 성능 최적화
# ============================================================

DB_FILE = "merchants.json"

# ─── 데이터 관리 ───────────────────────────────────────────

@st.cache_data(ttl=0)
def get_default_list():
    return {
        'dr188':      {'wallet': 'TBMTb9TFFXDuqhjLKLp9Yo26QHRnnG6jPN', 'fee': '0.5',  'group': 'dragon', 'note': '드래곤 메인'},
        'drgtssen':   {'wallet': 'TRX_Wallet_drgtssen',                  'fee': '0.5',  'group': 'dragon', 'note': ''},
        'Dpinnacle':  {'wallet': 'TRX_Wallet_Dpinnacle',                 'fee': '0.5',  'group': 'dragon', 'note': ''},
        'drSpinmama': {'wallet': 'TRX_Wallet_drSpinmama',                'fee': '0.5',  'group': 'dragon', 'note': ''},
        'drbetssen':  {'wallet': 'TRX_Wallet_drbetssen',                 'fee': '0.5',  'group': 'dragon', 'note': ''},
        'NextbetM/G': {'wallet': 'TRX_Wallet_Nextbet',                   'fee': '0.5',  'group': 'dragon', 'note': ''},
        'DafabetM/G': {'wallet': 'TRX_Wallet_Dafabet',                   'fee': '4.5',  'group': 'dragon', 'note': ''},
        'drgtkore':   {'wallet': 'TRX_Wallet_drgtkore',                  'fee': '0.5',  'group': 'dragon', 'note': ''},
        'drolymp':    {'wallet': 'TRX_Wallet_drolymp',                   'fee': '0.5',  'group': 'dragon', 'note': ''},
        'drbetkore':  {'wallet': 'TRX_Wallet_drbetkore',                 'fee': '0.5',  'group': 'dragon', 'note': ''},
        'drTapTap':   {'wallet': 'TRX_Wallet_drTapTap',                  'fee': '0.5',  'group': 'dragon', 'note': ''},
        'spfxm':      {'wallet': 'TWbFbzW5GRkAkVrY4fLuXhNA576DCkoGbh',  'fee': '4',    'group': 'general','note': '가장 많이 쓰는 업체'},
        'V99':        {'wallet': 'TRX_Wallet_V99',                       'fee': '1.5',  'group': 'general','note': 'VVIP 전용'},
    }

def load_data():
    defaults = get_default_list()
    if not os.path.exists(DB_FILE):
        save_data(defaults)
        return defaults
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            db = json.load(f)
            # 구버전 데이터에 'group' 키가 없으면 보완
            for k, v in db.items():
                if 'group' not in v:
                    v['group'] = 'dragon' if k.startswith('dr') or k in ['NextbetM/G','DafabetM/G','Dpinnacle'] else 'general'
            return db if len(db) >= 3 else defaults
    except Exception:
        return defaults

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ─── 유틸 ──────────────────────────────────────────────────

def extract_int(text: str) -> int:
    num_str = re.sub(r'[^0-9]', '', str(text))
    return int(num_str) if num_str else 0

def fmt(n: int) -> str:
    return f"{n:,}"

DRAGON_KEYS = {'dr188','drgtssen','Dpinnacle','drSpinmama','drbetssen',
               'NextbetM/G','DafabetM/G','drgtkore','drolymp','drbetkore','drTapTap','spfxm'}

# ─── 페이지 설정 ───────────────────────────────────────────

st.set_page_config(page_title="정산 매크로 v2.0", layout="wide", page_icon="💹")

# ─── 복사 버튼 컴포넌트 ───────────────────────────────────

def copy_box(text: str, box_class: str = ""):
    """결과 텍스트 박스 + 우상단 복사 버튼"""
    import html as html_lib
    escaped = html_lib.escape(text)
    # JS용 이스케이프 (개행/따옴표)
    js_text = text.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
    uid = abs(hash(text)) % 999999

    st.markdown(f"""
<div class="copy-wrap {box_class}" id="wrap_{uid}">
  <button class="copy-btn" onclick="
    navigator.clipboard.writeText(\`{js_text}\`).then(function(){{
      var b = document.getElementById('btn_{uid}');
      b.innerText='✅ 복사됨';
      b.style.color='#27ae60';
      setTimeout(function(){{b.innerText='📋 복사'; b.style.color='';}} ,1500);
    }});
  " id="btn_{uid}">📋 복사</button>
  <pre class="result-pre">{escaped}</pre>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans+KR:wght@300;400;600&display=swap');

/* ── 전체 배경 ── */
html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background: #0a0e17 !important;
    color: #c8d6e5 !important;
    font-family: 'IBM Plex Sans KR', sans-serif !important;
}
[data-testid="stSidebar"] {
    background: #0d1220 !important;
    border-right: 1px solid #1e2d45 !important;
}

/* ── 카드 ── */
.card {
    background: #111827;
    border: 1px solid #1e2d45;
    border-radius: 10px;
    padding: 20px 24px;
    margin-bottom: 18px;
}
.card-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72em;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #4a90d9;
    margin-bottom: 14px;
    border-bottom: 1px solid #1e2d45;
    padding-bottom: 8px;
}

/* ── 복사 래퍼 ── */
.copy-wrap {
    position: relative;
    background: #060d18;
    border: 1px solid #1e3a5f;
    border-left: 3px solid #4a90d9;
    border-radius: 6px;
    margin-top: 10px;
    margin-bottom: 4px;
}
.copy-wrap.green  { border-left-color: #27ae60; }
.copy-wrap.yellow { border-left-color: #f39c12; }
.copy-wrap.red    { border-left-color: #e74c3c; }

.copy-btn {
    position: absolute;
    top: 8px; right: 10px;
    background: #0f2040;
    color: #5dade2;
    border: 1px solid #1e3a5f;
    border-radius: 4px;
    padding: 2px 10px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.75em;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s;
    z-index: 10;
}
.copy-btn:hover { background: #1a3a6c; border-color: #4a90d9; color: #a8d4f5; }

.result-pre {
    padding: 14px 16px;
    padding-right: 80px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.85em;
    line-height: 1.7;
    color: #a8c7e8;
    white-space: pre-wrap;
    word-break: break-all;
    margin: 0;
}
.copy-wrap.green  .result-pre { color: #7dcea0; }
.copy-wrap.yellow .result-pre { color: #f8c471; }
.copy-wrap.red    .result-pre { color: #f1948a; }

/* ── 요율 배지 ── */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.78em;
    font-weight: 600;
    font-family: 'IBM Plex Mono', monospace;
    margin-left: 8px;
}
.badge-dragon  { background: #1a3a5c; color: #5dade2; }
.badge-general { background: #1a3a1a; color: #58d68d; }

/* ── 환율 디스플레이 ── */
.rate-display {
    background: #060d18;
    border: 1px solid #1e3a5f;
    border-radius: 8px;
    padding: 12px 18px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.05em;
    color: #f1c40f;
    text-align: center;
    letter-spacing: 0.05em;
    margin: 8px 0;
}

/* ── 입력 필드 ── */
div[data-baseweb="input"] > div {
    background: #0d1525 !important;
    border: 1px solid #1e3055 !important;
    border-radius: 6px !important;
}
input {
    color: #f1c40f !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 1em !important;
    font-weight: 600 !important;
}
input::placeholder { color: #2a4060 !important; }

/* ── 셀렉트박스 ── */
div[data-baseweb="select"] > div {
    background: #0d1525 !important;
    border: 1px solid #1e3055 !important;
}

/* ── 버튼 ── */
.stButton > button {
    width: 100% !important;
    background: #0f2040 !important;
    color: #5dade2 !important;
    border: 1px solid #1e3a5f !important;
    border-radius: 6px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-weight: 600 !important;
    font-size: 0.85em !important;
    letter-spacing: 0.05em !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: #1a3a6c !important;
    border-color: #4a90d9 !important;
    color: #a8d4f5 !important;
}

/* ── 라디오 ── */
div[role="radiogroup"] label { color: #8ab4d4 !important; font-size: 0.9em !important; }

/* ── 탭 ── */
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

/* ── 사이드바 버튼 ── */
section[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: 1px solid #1e3055 !important;
    color: #8ab4d4 !important;
    text-align: left !important;
    font-size: 0.9em !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: #111827 !important;
    color: #5dade2 !important;
}

/* ── 구분선 ── */
hr { border-color: #1e2d45 !important; }

/* ── 캡션 ── */
.stCaption, small { color: #4a6880 !important; font-size: 0.78em !important; }

/* ── 성공/경고 메시지 ── */
.stSuccess { background: #0a1f10 !important; border-color: #27ae60 !important; }
.stWarning { background: #1f1500 !important; border-color: #f39c12 !important; }
</style>
""", unsafe_allow_html=True)

# ─── 세션 초기화 ───────────────────────────────────────────

if 'db'   not in st.session_state: st.session_state.db   = load_data()
if 'page' not in st.session_state: st.session_state.page = 'settle'

# ─── 사이드바 ──────────────────────────────────────────────

with st.sidebar:
    st.markdown("### 💹 정산 매크로")
    st.markdown(f"<small style='color:#2a4060;'>{datetime.now().strftime('%Y-%m-%d %H:%M')}</small>", unsafe_allow_html=True)
    st.markdown("---")

    if st.button("🚀  정산 작업"):   st.session_state.page = 'settle'
    if st.button("⬆️  탑업 요청"):   st.session_state.page = 'topup'
    if st.button("⚙️  머천트 설정"): st.session_state.page = 'admin'

    st.markdown("---")
    merchant_count = len(st.session_state.db)
    dragon_count   = sum(1 for v in st.session_state.db.values() if v.get('group') == 'dragon')
    st.markdown(f"<small style='color:#2a5070;'>머천트 {merchant_count}개 &nbsp;|&nbsp; 드래곤 {dragon_count}개</small>", unsafe_allow_html=True)

# ════════════════════════════════════════════════
#  PAGE 1 : 정산 작업
# ════════════════════════════════════════════════

if st.session_state.page == 'settle':

    st.markdown("## 🚀 정산 작업")

    sorted_keys    = sorted(st.session_state.db.keys())
    default_index  = sorted_keys.index('spfxm') if 'spfxm' in sorted_keys else 0
    selected_m     = st.selectbox("**업체 선택**", sorted_keys, index=default_index)
    m_info         = st.session_state.db[selected_m]
    is_dragon      = m_info.get('group', 'general') == 'dragon'
    fee_rate       = float(m_info.get('fee', 0.5))
    badge_cls      = "badge-dragon" if is_dragon else "badge-general"
    badge_label    = "드래곤" if is_dragon else "일반"

    st.markdown(
        f"<div style='margin-bottom:18px;'>"
        f"<span style='font-size:1.1em;font-weight:600;'>{selected_m}</span>"
        f"<span class='badge {badge_cls}'>{badge_label}</span>"
        f"<span class='badge' style='background:#1a1a2e;color:#8888aa;'>수수료 {fee_rate}%</span>"
        f"</div>",
        unsafe_allow_html=True
    )

    col_left, col_right = st.columns([1, 1], gap="large")

    # ── 왼쪽: 환율 + 정산 요청 ──
    with col_left:

        # 환율 설정
        st.markdown('<div class="card"><div class="card-title">01 / 환율 설정</div>', unsafe_allow_html=True)
        multiplier = st.radio(
            "배수 선택",
            [1.04, 1.045, 1.05],
            format_func=lambda x: f"×{x}  ({(x-1)*100:.1f}%)",
            index=0, horizontal=True
        )
        c1, c2 = st.columns(2)
        with c1:
            b_raw = st.text_input("빗썸 시세", value="", placeholder="예: 1,450,000", key="b_val")
            b_val = extract_int(b_raw)
        with c2:
            s_raw = st.text_input("수동 환율", value="", placeholder="직접 입력", key="s_val")
            s_val = extract_int(s_raw)

        current_rate = s_val if s_val > 0 else (math.ceil(b_val * multiplier) if b_val > 0 else 0)

        if current_rate > 0:
            src = "수동" if s_val > 0 else f"빗썸 × {multiplier}"
            st.markdown(f'<div class="rate-display">1 USDT = {fmt(current_rate)} KRW &nbsp;<small style="color:#4a6880;font-size:0.7em;">({src})</small></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # 정산 요청
        st.markdown('<div class="card"><div class="card-title">02 / 정산 요청</div>', unsafe_allow_html=True)
        amt_raw = st.text_input("정산 금액 (KRW)", value="", placeholder="예: 10,000,000", key="amount")
        amount  = extract_int(amt_raw)

        if amount > 0 and current_rate > 0:
            usdt_val   = round(amount / current_rate, 2)
            settle_msg = (
                f"- {selected_m} settlement amount : {fmt(amount)} krw\n"
                f"- exchange to usdt : {usdt_val:,.2f} usdt\n"
                f"- 1usdt = {fmt(current_rate)} krw\n\n"
                f"{m_info['wallet']}\n\n"
                f"Please confirm the address and calculation.\n"
                f"Once approved, we will proceed immediately"
            )
            copy_box(settle_msg)
        elif amount > 0 and current_rate == 0:
            st.warning("환율을 먼저 입력해 주세요.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ── 오른쪽: 잔액 보고 + 수수료 + 경고 ──
    with col_right:

        # 잔액 보고
        st.markdown('<div class="card"><div class="card-title">03 / 잔액 보고</div>', unsafe_allow_html=True)
        bal_raw = st.text_input("현재 잔액 (KRW)", value="", placeholder="예: 5,000,000", key="balance")
        balance = extract_int(bal_raw)

        if balance > 0 and amount > 0 and current_rate > 0:
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
        elif balance > 0:
            st.info("정산 금액과 환율도 입력해 주세요.")
        st.markdown('</div>', unsafe_allow_html=True)

        # 수수료 마크업
        st.markdown('<div class="card"><div class="card-title">04 / 수수료 마크업</div>', unsafe_allow_html=True)
        if amount > 0:
            calc_fee   = math.ceil(amount * (fee_rate / 100))
            prefix     = "드래곤 테더정산" if selected_m in DRAGON_KEYS else "일반 테더정산"
            markup_msg = f"{prefix} 수수료 {fee_rate}% {selected_m} / {fmt(amount)} / {fmt(calc_fee)}"
            copy_box(markup_msg, "yellow")
        else:
            st.markdown("<small style='color:#2a4060;'>정산 금액을 입력하면 자동 생성됩니다.</small>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # 잔액 경고
        st.markdown('<div class="card"><div class="card-title">05 / 잔액 경고</div>', unsafe_allow_html=True)
        warn_raw = st.text_input("경고 잔액 (KRW)", value="", placeholder="예: 500,000", key="warn_bal")
        warn_bal = extract_int(warn_raw)
        if warn_bal > 0:
            warn_msg = f"Balance update - {selected_m} : {fmt(warn_bal)} krw"
            copy_box(warn_msg, "red")
        st.markdown('</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════
#  PAGE 2 : 탑업 요청
# ════════════════════════════════════════════════

elif st.session_state.page == 'topup':

    st.markdown("## ⬆️ 탑업 요청")

    sorted_keys   = sorted(st.session_state.db.keys())
    default_index = sorted_keys.index('spfxm') if 'spfxm' in sorted_keys else 0
    selected_m    = st.selectbox("**업체 선택**", sorted_keys, index=default_index)
    m_info        = st.session_state.db[selected_m]

    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown('<div class="card"><div class="card-title">탑업 환율 설정 (수수료 0.5% 차감)</div>', unsafe_allow_html=True)

        t_market_raw = st.text_input("빗썸 시세", value="", placeholder="예: 1,450,000", key="t_m_rate")
        t_market     = extract_int(t_market_raw)

        t_manual_raw = st.text_input("수동 환율 (선택)", value="", placeholder="직접 입력 시 우선 적용", key="t_s_rate")
        t_manual     = extract_int(t_manual_raw)

        if t_manual > 0:
            final_rate = t_manual
            st.markdown(f'<div class="rate-display">1 USDT = {fmt(final_rate)} KRW &nbsp;<small style="color:#4a6880;font-size:0.7em;">(수동)</small></div>', unsafe_allow_html=True)
        elif t_market > 0:
            deduction  = math.ceil(t_market * 0.005)
            final_rate = t_market - deduction
            st.markdown(f'<div class="rate-display">1 USDT = {fmt(final_rate)} KRW &nbsp;<small style="color:#4a6880;font-size:0.7em;">(빗썸 - 0.5%)</small></div>', unsafe_allow_html=True)
        else:
            final_rate = 0

        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="card"><div class="card-title">탑업 수량 및 메시지</div>', unsafe_allow_html=True)

        topup_raw  = st.text_input("탑업 USDT 수량", value="", placeholder="예: 10,000", key="t_usdt")
        topup_usdt = extract_int(topup_raw)

        if topup_usdt > 0 and final_rate > 0:
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

            st.markdown("---")
            base_rate = t_manual if t_manual > 0 else t_market
            if base_rate > 0:
                total_market = topup_usdt * base_rate
                total_fee    = math.ceil(total_market * 0.005)
                markup_msg   = f"드래곤 테더탑업 수수료 0.5% {selected_m} / {fmt(total_market)} / {fmt(total_fee)}"
                copy_box(markup_msg, "yellow")

        elif topup_usdt > 0 and final_rate == 0:
            st.warning("환율을 입력해 주세요.")

        st.markdown('</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════
#  PAGE 3 : 머천트 설정
# ════════════════════════════════════════════════

else:
    st.markdown("## ⚙️ 머천트 설정")

    # 신규 등록
    with st.expander("➕ 신규 업체 등록", expanded=False):
        with st.form("new_merchant", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                n_name   = st.text_input("업체 이름")
                n_wallet = st.text_input("지갑 주소")
            with c2:
                n_fee   = st.text_input("수수료 요율 (%)", value="0.5")
                n_group = st.selectbox("그룹", ["dragon", "general"])
                n_note  = st.text_input("비고")
            if st.form_submit_button("✅ 등록 완료"):
                if n_name and n_wallet:
                    st.session_state.db[n_name] = {"wallet": n_wallet, "fee": n_fee, "group": n_group, "note": n_note}
                    save_data(st.session_state.db)
                    st.success(f"{n_name} 등록 완료!")
                    st.rerun()

    st.markdown("---")
    st.markdown("#### 📂 업체 목록")

    # 그룹별 탭
    tab_all, tab_dragon, tab_general = st.tabs(["전체", "🐉 드래곤", "🟢 일반"])

    def render_merchant_list(keys):
        for orig_name in sorted(keys):
            info = st.session_state.db[orig_name]
            with st.expander(f"**{orig_name}**  —  수수료 {info.get('fee','?')}%"):
                c1, c2 = st.columns(2)
                with c1:
                    new_nm  = st.text_input("업체명",    value=orig_name,              key=f"nm_{orig_name}")
                    u_w     = st.text_input("지갑 주소", value=info['wallet'],          key=f"w_{orig_name}")
                with c2:
                    u_f     = st.text_input("요율",      value=info['fee'],             key=f"f_{orig_name}")
                    u_g     = st.selectbox("그룹",       ["dragon","general"],
                                           index=0 if info.get('group','dragon')=='dragon' else 1,
                                           key=f"g_{orig_name}")
                    u_n     = st.text_input("비고",      value=info.get('note',''),     key=f"n_{orig_name}")

                b1, b2 = st.columns(2)
                with b1:
                    if st.button("💾 저장", key=f"s_{orig_name}"):
                        if new_nm != orig_name:
                            del st.session_state.db[orig_name]
                        st.session_state.db[new_nm] = {"wallet": u_w, "fee": u_f, "group": u_g, "note": u_n}
                        save_data(st.session_state.db)
                        st.success(f"{new_nm} 저장 완료!")
                with b2:
                    if st.button("🗑️ 삭제", key=f"d_{orig_name}"):
                        del st.session_state.db[orig_name]
                        save_data(st.session_state.db)
                        st.rerun()

    all_keys     = list(st.session_state.db.keys())
    dragon_keys  = [k for k in all_keys if st.session_state.db[k].get('group') == 'dragon']
    general_keys = [k for k in all_keys if st.session_state.db[k].get('group') != 'dragon']

    with tab_all:     render_merchant_list(all_keys)
    with tab_dragon:  render_merchant_list(dragon_keys)
    with tab_general: render_merchant_list(general_keys)
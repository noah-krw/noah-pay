import streamlit as st

st.set_page_config(page_title="Noah Settlement System", layout="wide")

st.title("💰 Noah 전용 정산 시스템")

# --- 1단계: 설정 및 입력 ---
st.sidebar.header("⚙️ 1. 환율 설정")
rate_choice = st.sidebar.radio(
    "적용 환율 (KP 선택)",
    ("4% (1.04)", "4.5% (1.045)", "5% (1.05)"),
    index=1
)

multiplier = 1.04 if "4%" in rate_choice else 1.045 if "4.5%" in rate_choice else 1.05
base_rate = st.sidebar.number_input("현재 빗썸 시세 (KRW)", min_value=1000, value=1450, step=1)
final_rate = int(-(-(base_rate * multiplier) // 1))

st.sidebar.info(f"💡 최종 적용 환율: {final_rate:,} 원")

st.header("Step 1. 정산 정보 입력")
col1, col2 = st.columns(2)

with col1:
    merchant = st.selectbox("업체 선택", ["일반 업체", "V99mm", "드래곤 게이트"])
    amount_usd = st.number_input("금액 (USDT/USD)", min_value=0.0, step=100.0)
    
with col2:
    trans_type = st.radio("거래 종류", ["입금 (Deposit)", "payout (출금)"])

# 요율 결정
if merchant == "V99mm":
    fee_rate = 0.03 if "입금" in trans_type else 0.015
else:
    fee_rate = 0.03 if "입금" in trans_type else 0.01

# --- 2단계: 계산 ---
raw_krw = amount_usd * final_rate
fee_amount = raw_krw * fee_rate
final_krw = int(-(-(raw_krw - fee_amount) // 1)) if "입금" in trans_type else int(-(-(raw_krw + fee_amount) // 1))

# 드래곤 게이트 0.5% 별도 계산
dragon_bonus = int(-(-(raw_krw * 0.005) // 1)) if merchant == "드래곤 게이트" else 0

st.divider()

# --- 3단계: 결과 및 복사 양식 ---
st.header("Step 2 & 3. 정산 결과 및 복사")

res_col1, res_col2 = st.columns(2)

with res_col1:
    st.metric("최종 정산 금액 (KRW)", f"{final_krw:,} 원")
    if dragon_bonus > 0:
        st.write(f"🐉 드래곤 게이트 추가 적립: **{dragon_bonus:,} 원**")

with res_col2:
    # 텔레그램 복사용 텍스트 생성
    status = "settlement"
    copy_text = f"""
    [ {merchant} {status} ]
    - 수량: {amount_usd:,.2f} USDT
    - 적용 환율: {final_rate:,} 원 ({rate_choice.split(' ')[0]} 적용)
    - 수수료: {int(fee_rate*100*10)/10}%
    - 최종 금액: {final_krw:,} KRW
    """
    if dragon_bonus > 0:
        copy_text += f"- 드래곤 추가 적립: {dragon_bonus:,} KRW"
    
    st.text_area("텔레그램 복사용 양식", value=copy_text.strip(), height=150)
    st.caption("위 박스의 내용을 복사해서 공유하세요.")

st.divider()
st.write("모든 결과값은 '올림' 처리되었습니다.")
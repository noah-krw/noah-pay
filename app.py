import streamlit as st

st.set_page_config(page_title="Noah Settlement System", layout="wide")

st.title("💰 Noah 정산 시스템 v1.1")

# 1. 환율 및 요율 설정 섹션
st.sidebar.header("⚙️ 설정")

# 환율 선택 기능 추가
rate_choice = st.sidebar.radio(
    "적용 환율 선택",
    ("4% (1.04)", "4.5% (1.045)", "5% (1.05)"),
    index=1
)

# 선택된 값에 따른 배수 설정
if "4.5%" in rate_choice:
    multiplier = 1.045
elif "4%" in rate_choice:
    multiplier = 1.04
else:
    multiplier = 1.05

st.sidebar.info(f"현재 적용 배수: {multiplier}")

# 2. 정산 입력 섹션
col1, col2 = st.columns(2)

with col1:
    st.subheader("📥 입금/출금 입력")
    category = st.selectbox("업체 선택", ["일반 업체", "V99mm", "드래곤 게이트"])
    amount_usd = st.number_input("금액 입력 (USDT/USD)", min_value=0.0, step=100.0)
    
    # 요율 설정
    if category == "V99mm":
        in_fee, out_fee = 0.03, 0.015
    else:
        in_fee, out_fee = 0.03, 0.01
        
    type_choice = st.radio("거래 종류", ["입금 (Deposit)", "payout (출금)"])

with col2:
    st.subheader("📝 settlement 결과")
    
    # 환율 계산 (임의 시세 1400원 가정, 필요시 입력창 추가 가능)
    base_rate = 1400 
    final_rate = base_rate * multiplier
    
    raw_krw = amount_usd * final_rate
    
    if "입금" in type_choice:
        fee_amount = raw_krw * in_fee
        final_krw = raw_krw - fee_amount
    else:
        fee_amount = raw_krw * out_fee
        final_krw = raw_krw + fee_amount
        
    # 드래곤 게이트 추가 적립 (0.5%)
    dragon_bonus = 0
    if category == "드래곤 게이트":
        dragon_bonus = raw_krw * 0.005

    st.metric("최종 KRW (올림 처리)", f"{int(-(-final_krw // 1)):,} 원")
    if dragon_bonus > 0:
        st.write(f"🐉 드래곤 게이트 추가 적립: {int(-(-dragon_bonus // 1)):,} 원")

st.divider()
st.write("모든 계산은 소수점 올림 처리됩니다.")
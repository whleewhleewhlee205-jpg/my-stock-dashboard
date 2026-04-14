import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime
import plotly.graph_objects as go

# 페이지 설정
st.set_page_config(page_title="K-방산 & 지수 실시간 모니터링", layout="wide")

# 종목 리스트 (LIG넥스원 추가)
target_stocks = {
    "코스피": "^KS11",
    "코스닥": "^KQ11",
    "LIG넥스원": "079550.KS",
    "한화에어로스페이스": "012450.KS",
    "한국항공우주": "047810.KS",
    "한화오션": "042660.KS",
    "현대로템": "064350.KS",
    "한화시스템": "272210.KS"
}


def get_stock_data():
    data_list = []
    for name, ticker in target_stocks.items():
        stock = yf.Ticker(ticker)
        # 2일치 데이터를 가져와서 전일 종가와 비교
        info = stock.history(period='2d')

        if len(info) >= 2:
            current_price = info['Close'].iloc[-1]
            prev_price = info['Close'].iloc[-2]
            change = current_price - prev_price
            change_rate = (change / prev_price) * 100

            data_list.append({
                "종목명": name,
                "현재가": round(current_price, 2),
                "대비": round(change, 2),
                "등락률(%)": round(change_rate, 2),
                "업데이트": datetime.now().strftime('%H:%M:%S')
            })
    return pd.DataFrame(data_list)


# 대시보드 제목
st.title("🎖️ K-방산 실시간 주가 대시보드")
st.markdown(f"**현재 시각:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (1분마다 자동 새로고침)")

# 1분 업데이트를 위한 루프
placeholder = st.empty()

while True:
    with placeholder.container():
        try:
            df = get_stock_data()

            # 상단 메트릭 (지수 및 주요 종목 요약)
            # 4개씩 두 줄로 배치
            rows = [df.iloc[0:4], df.iloc[4:8]]
            for row_data in rows:
                cols = st.columns(4)
                for i, (idx, row) in enumerate(row_data.iterrows()):
                    cols[i].metric(
                        label=row['종목명'],
                        value=f"{row['현재가']:,}",
                        delta=f"{row['등락률(%)']}%"
                    )

            st.divider()

            # 좌우 분할 레이아웃
            col_left, col_right = st.columns([1, 1])

            with col_left:
                st.subheader("📊 상세 시세표")
                st.dataframe(df, use_container_width=True, hide_index=True)

            with col_right:
                st.subheader("📈 종목별 등락률 (%)")
                fig = go.Figure(data=[
                    go.Bar(
                        x=df['종목명'],
                        y=df['등락률(%)'],
                        marker_color=['#FF4B4B' if x > 0 else '#1C83E1' for x in df['등락률(%)']]
                    )
                ])
                fig.update_layout(height=300, margin=dict(l=20, r=20, t=20, b=20))
                st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"데이터를 가져오는 중 오류가 발생했습니다: {e}")

        time.sleep(60)  # 60초 대기
        st.rerun()

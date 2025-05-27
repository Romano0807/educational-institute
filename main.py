import streamlit as st
import pandas as pd
import plotly.express as px

@st.cache_data
def load_data():
    df = pd.read_csv("academy_geocoded.csv")
    return df.dropna(subset=["위도", "경도"])

def main():
    st.title("📍 포항시 학원 평균 교습비 시각화 (지오코딩 완료 버전)")

    df = load_data()

    st.subheader("💰 평균 교습비 Top 20 학원")
    top20 = df.sort_values("총교습비", ascending=False).head(20)
    fig = px.bar(
        top20,
        x="학원명", y="총교습비",
        title="Top 20 평균 교습비 학원",
        labels={"학원명": "학원", "총교습비": "총 교습비"},
        height=600
    )
    st.plotly_chart(fig)

    st.subheader("🗺️ 포항시 전체 학원 지도")
    st.map(df.rename(columns={"위도": "lat", "경도": "lon"}))

    st.subheader("📄 학원 데이터 테이블")
    st.dataframe(df[["학원명", "주소", "총교습비", "위도", "경도"]])

if __name__ == "__main__":
    main()

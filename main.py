import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px

@st.cache_data
def load_data():
    df = pd.read_csv("academy_geocoded.csv")  # 반드시 위도/경도 포함된 CSV 파일
    df = df.dropna(subset=["위도", "경도"])
    df = df.rename(columns={"위도": "lat", "경도": "lon"})  # pydeck용 필수 컬럼명
    return df

def main():
    st.title("📍 포항시 학원 평균 교습비 시각화")

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

    st.subheader("🗺️ 전체 학원 위치 (지도 위 작은 점)")
    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state=pdk.ViewState(
            latitude=df["lat"].mean(),
            longitude=df["lon"].mean(),
            zoom=11,
            pitch=0,
        ),
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=df,
                get_position='[lon, lat]',
                get_radius=100,
                get_fill_color='[255, 0, 0, 140]',
                pickable=True,
            )
        ],
        tooltip={"text": "학원명: {학원명}\n총교습비: {총교습비}원"}
    ))

    st.subheader("📄 전체 학원 데이터")
    st.dataframe(df[["학원명", "주소", "총교습비", "lat", "lon"]])

if __name__ == "__main__":
    main()

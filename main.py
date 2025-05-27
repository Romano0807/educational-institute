import streamlit as st
import pandas as pd
import pydeck as pdk  # 더 나은 지도 표현

@st.cache_data
def load_data():
    df = pd.read_csv("academy_geocoded.csv")  # 위도/경도 포함된 파일
    df = df.dropna(subset=["위도", "경도"])
    return df

def main():
    st.title("📍 포항시 학원 지도 시각화")

    df = load_data()

    st.subheader("🗺️ 전체 학원 위치 (점으로 표시)")
    st.pydeck_chart(pdk.Deck(
        initial_view_state=pdk.ViewState(
            latitude=df["위도"].mean(),
            longitude=df["경도"].mean(),
            zoom=11,
            pitch=0,
        ),
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=df,
                get_position="[경도, 위도]",
                get_radius=100,
                get_fill_color="[200, 30, 0, 160]",
                pickable=True,
            ),
        ],
    ))

    st.subheader("📄 학원 데이터")
    st.dataframe(df[["학원명", "주소", "총교습비", "위도", "경도"]])

if __name__ == "__main__":
    main()

import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

@st.cache_data
def load_and_geocode_data():
    df = pd.read_csv("academy_geocoded.csv")  # 주소만 있는 경우를 포함
    df = df.rename(columns=lambda x: x.strip())

    if "위도" not in df.columns or "경도" not in df.columns or df["위도"].isnull().all():
        geolocator = Nominatim(user_agent="academy_mapper")
        geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
        latitudes, longitudes = [], []
        for addr in df["주소"]:
            try:
                location = geocode(addr)
                if location:
                    latitudes.append(location.latitude)
                    longitudes.append(location.longitude)
                else:
                    latitudes.append(None)
                    longitudes.append(None)
            except:
                latitudes.append(None)
                longitudes.append(None)
        df["위도"] = latitudes
        df["경도"] = longitudes
        df = df.dropna(subset=["위도", "경도"])
    return df

def main():
    st.title("📍 포항시 학원 평균 교습비 시각화")

    df = load_and_geocode_data()
    df = df.dropna(subset=["위도", "경도"])
    df = df.rename(columns={"위도": "lat", "경도": "lon"})

    st.subheader("💰 평균 교습비 Top 20 학원")
    top20 = df.sort_values("총교습비", ascending=False).head(20)
    fig = px.bar(
        top20,
        x="학원명", y="총교습비",
        title="Top 20 평균 교습비 학원",
        labels={"학원명": "학원", "총교습비": "총 교습비"},
        height=600
    )
    fig.update_traces(text=top20["총교습비"].apply(lambda x: f"{x:,}원"), textposition='outside')
    fig.update_layout(yaxis_tickformat=",", yaxis_title="총 교습비 (원)")
    st.plotly_chart(fig)

    st.subheader("🗺️ 전체 학원 위치")
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
                get_fill_color='[0, 100, 200, 160]',
                pickable=True,
            )
        ],
        tooltip={"text": "학원명: {학원명}\n총교습비: {총교습비}원"}
    ))

    st.subheader("📄 전체 학원 데이터")
    df_display = df[["학원명", "주소", "총교습비", "lat", "lon"]].copy()
    df_display["총교습비"] = df_display["총교습비"].apply(lambda x: f"{x:,}원")
    st.dataframe(df_display)

if __name__ == "__main__":
    main()

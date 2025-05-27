import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

@st.cache_data
def load_and_geocode_data():
    df = pd.read_csv("academy_geocoded.csv")
    df.columns = [col.strip() for col in df.columns]

    # 위도, 경도 컬럼 정리
    if "위도" in df.columns and "경도" in df.columns:
        df = df.rename(columns={"위도": "lat", "경도": "lon"})

    # 위도/경도 없을 경우 주소 기반으로 계산
    if "lat" not in df.columns or "lon" not in df.columns or df["lat"].isnull().all():
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

        df["lat"] = latitudes
        df["lon"] = longitudes

    df = df.dropna(subset=["lat", "lon"])
    return df

def main():
    st.title("📍 포항시 학원 평균 교습비 시각화")

    df = load_and_geocode_data()

    st.subheader("💰 평균 교습비 Top 20 학원")
    top20 = df.sort_values("총교습비", ascending=False).head(20)

    fig = px.bar(
        top20,
        x="학원명", y="총교습비",
        title="Top 20 평균 교습비 학원",
        labels={"학원명": "학원", "총교습비": "총 교습비"},
        height=600
    )
    fig.update_traces(
        text=top20["총교습비"].apply(lambda x: f"₩{x:,.0f}"),
        textposition='outside'
    )
    fig.update_layout(
        yaxis_tickformat="₩,.0f",
        yaxis_title="총 교습비 (원)",
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig)

    st.subheader("🗺️ 전체 학원 위치 지도")
    st.write(f"✅ 지도에 표시된 학원 수: {len(df)}곳")
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
        tooltip={"text": "학원명: {학원명}\n총교습비: ₩{총교습비}"}
    ))

    st.subheader("📄 전체 학원 데이터 테이블")
    df_display = df[["학원명", "주소", "총교습비", "lat", "lon"]].copy()
    df_display["총교습비"] = df_display["총교습비"].apply(lambda x: f"₩{x:,.0f}")
    st.dataframe(df_display)

if __name__ == "__main__":
    main()

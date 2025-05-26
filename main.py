import streamlit as st
import pandas as pd
import plotly.express as px
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import time

# 데이터 불러오기 및 전처리
@st.cache_data
def load_and_process_data():
    df = pd.read_excel("포항시 학원.xlsx", header=4)
    df = df.rename(columns={
        'Unnamed: 1': '학원명',
        'Unnamed: 3': '주소',
        '기숙사비': '총교습비'
    })
    df = df.dropna(subset=['학원명', '주소'])
    df['총교습비'] = (
        df['총교습비']
        .astype(str)
        .str.replace(",", "")
        .str.extract("(\d+)")
        .dropna()
        .astype(int)
    )
    df = df[['학원명', '주소', '총교습비']]
    df_grouped = df.groupby(['학원명', '주소'], as_index=False)['총교습비'].mean()
    return df_grouped

# 주소 -> 위도/경도 변환
@st.cache_data
def geocode_addresses(df):
    geolocator = Nominatim(user_agent="academy_locator")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    latitudes, longitudes = [], []
    for addr in df["주소"]:
        location = geocode(addr)
        if location:
            latitudes.append(location.latitude)
            longitudes.append(location.longitude)
        else:
            latitudes.append(None)
            longitudes.append(None)
        time.sleep(1)  # API 제한 고려
    df["위도"] = latitudes
    df["경도"] = longitudes
    return df.dropna(subset=["위도", "경도"])

# 메인 앱
def main():
    st.title("📍 포항시 학원 평균 교습비 지도 시각화")

    df = load_and_process_data()
    df_geo = geocode_addresses(df)

    st.subheader("학원별 평균 교습비")
    fig = px.bar(
        df.sort_values("총교습비", ascending=False).head(20),
        x="학원명", y="총교습비",
        title="Top 20 평균 교습비 학원"
    )
    st.plotly_chart(fig)

    st.subheader("지도 시각화")
    st.map(df_geo.rename(columns={"위도": "lat", "경도": "lon"}))

    st.subheader("학원 데이터")
    st.dataframe(df_geo[["학원명", "주소", "총교습비", "위도", "경도"]])

if __name__ == "__main__":
    main()

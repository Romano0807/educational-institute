import streamlit as st
import plotly.express as px
import pandas as pd

# 데이터 불러오기
@st.cache_data
def load_data():
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
    return df

df = load_data()

# 제목
st.title("📊 포항시 학원 평균 수업비 시각화")

# 평균 교습비 Top 20 시각화
st.subheader("🏫 평균 수업비 Top 20 학원")
top20 = df.groupby("학원명")["총교습비"].mean().sort_values(ascending=False).head(20).reset_index()
fig = px.bar(top20, x="학원명", y="총교습비", title="Top 20 학원 평균 수업비", height=600)
st.plotly_chart(fig)

# 학원별 데이터 표로 보기
st.subheader("📋 전체 학원 수업비 데이터")
st.dataframe(df)


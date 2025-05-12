import requests
import json

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

title = 'DS Toolkit'
st.set_page_config(page_title=title)
st.title(title)

@st.cache_data(ttl=3600, show_spinner="Fetching data from API...")
def get_video_data():
    response = requests.get('https://www.dreamingspanish.com/.netlify/functions/videos')
    return json.loads(response.text)

with open('dsvids51125.txt', 'r', encoding='utf-8') as file:
    dsvids = file.read()

video_data = json.loads(dsvids)
# video_data = get_video_data()
guides = pd.DataFrame.from_dict(video_data["guides"], orient='columns').sort_values(by=['isMainTeacher', 'name'], ascending=[False, True])
df = pd.DataFrame.from_dict(video_data["videos"], orient='columns')

column_map = {
    'superbeginner': { 'color': '#0ed4d4', 'name': 'Super Beginner' },
    'beginner':      { 'color': '#239fe3', 'name': 'Beginner' },
    'intermediate':  { 'color': '#ff7f3c', 'name': 'Intermediate' },
    'advanced':      { 'color': '#ff2e65', 'name': 'Advanced'  },
}

df['level'] = df['level'].apply(lambda level: column_map[level]['name'])
df['duration'] = df['duration'].div(3600).round(1)
df['difficulty'] = (df['difficultyScore'] * 0.0417 - 8.33392).round().astype(int)

domain = [column['name'] for column in column_map.values()]
colors = [column['color'] for column in column_map.values()]

col1, col2 = st.columns(2)

guide = 'All'
premium = 'Both'
with col1:
    guide = st.selectbox(
        'Guide',
        ['All'] + guides['name'].values.tolist(),
    )

with col2:
    premium = st.selectbox(
        'Subscription Level',
        ['All', 'Premium', 'Free'],
    )

if guide != 'All':
    df = df[df['guides'].apply(lambda x: guide in x)]

if premium == 'Premium':
    df = df[df['private'] == True]
elif premium == 'Free':
    df = df[df['private'] == False]

st.altair_chart(alt.Chart(df).mark_bar().encode(
    x=alt.X('difficulty', sort=None, title="Difficulty"),
    y=alt.Y('sum(duration)', title="Hours"),
    color=alt.Color(
        'level',
        title='Level',
        scale=alt.Scale(domain=domain, range=colors),
        sort=domain,
        legend=alt.Legend(orient='top-left')
    )
), use_container_width=True)

levels = (
        df
        .groupby("level")
        .agg(
            Hours=("duration", "sum"),
            Videos=("duration", "size"),
        )
        .reindex(domain)
)
levels.loc["Total"] = levels.sum()
st.dataframe(levels, use_container_width=True, column_config={
    "level": "Level",
    "Videos": "# of Videos"
})

st.write('---')
st.write('Forked from main branch on 5/11/25. Issue with API call so API result was grabbed maually from browser on 5/11/25 and saved to a file. Other changes to this application were made to use the stored copy instead of the API call.')
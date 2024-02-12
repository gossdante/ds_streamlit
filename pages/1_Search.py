import requests
import json

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

title = 'DS Toolkit - Search'
st.set_page_config(page_title=title,layout="wide")
st.title(title)

@st.cache_data(ttl=3600, show_spinner="Fetching data from API...")
def get_video_data():
    response = requests.get('https://dsbuscar.com/.netlify/functions/getvideos')
    return json.loads(response.text)

video_data = get_video_data()
df = pd.DataFrame.from_dict(video_data["videos"], orient='columns')

column_map = {
    'superbeginner': { 'color': '#0ed4d4', 'name': 'Super Beginner' },
    'beginner':      { 'color': '#239fe3', 'name': 'Beginner' },
    'intermediate':  { 'color': '#ff7f3c', 'name': 'Intermediate' },
    'advanced':      { 'color': '#ff2e65', 'name': 'Advanced'  },
}

def time_convert(sec):
    mins = sec // 60
    sec = sec % 60
    hours = mins // 60
    mins = mins % 60
    if hours > 0:
        return '%02d:%02d:%02d' % (hours, mins, sec)
    return '%02d:%02d' % (mins, sec)

def make_clickable(val):
    split = val.split('#')
    return '<a href="=%s">%s</a>' % (split[0], '#'.join(split[1:]))

df['level'] = df['level'].apply(lambda level: column_map[level]['name'])
df['formatted_duration'] = df['duration'].apply(time_convert)
df['difficulty'] = (df['difficultyScore'] * 0.0417 - 8.33392).round().astype(int)
df['title'] = "https://www.dreamingspanish.com/watch?id="+ df["_id"] + '#' + df["title"]
df = df[['title', 'level', 'difficulty', 'formatted_duration', 'duration', 'guides', 'private' ]]

keywords = st.text_input('Enter video keywords')
keywords = keywords.lower().split()

if len(keywords) > 0:
    df = df[df['title'].apply(lambda x: any([keyword in x[x.find('#')+1:].lower() for keyword in keywords]))]
    st.text("Total time: " + time_convert(df['duration'].sum()))
    st.dataframe(
        df.sort_values(by='difficulty'),
        column_config={
            'title': st.column_config.LinkColumn('Title', display_text="#(.*)$"),
            'private': st.column_config.CheckboxColumn('Premium'),
            'duration': None,
            'formatted_duration': "Duration",
        },
        hide_index=True,
        use_container_width=True,
    )

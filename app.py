import pandas as pd
import streamlit as st
from pygris import tracts
import geopandas as gp
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

st.set_page_config(layout = 'wide')
st.title('U.S. Trauma Hospital Locations')
st.caption('Based on the tutorial "Distance and proximity analysis in Python" by Kyle Walker')

with st.sidebar:
    st.write('Filter state')
    state = st.selectbox('State', 
                         options = ('CA', 'AZ', 'WI'))

@st.cache_data
def get_data(st_filter):
    state_tracts = tracts(st_filter, cb = True, 
                          year = 2021, 
                          cache = True).to_crs(6571)
    state_tracts = state_tracts.to_crs('EPSG:4326')
    return(state_tracts)

state_tracts = get_data(state)

@st.cache_data
def load_data(state):
    trauma = gp.read_file('trauma.geojson')
    trauma = trauma[trauma['STATE'] == state]
    return(trauma)
           
trauma = load_data(state)

col1, col2 = st.columns(2)

with st.container():
    with col1:
        st.subheader('Location of trauma centers')
        st.map(trauma)

    with col2:
        st.subheader('Raw data')
        st.write(trauma[['NAME', 'ADDRESS', 'CITY', 'STATE', 'ZIP']])
        
        state_tracts = state_tracts.to_crs(6571)
        trauma = trauma.to_crs(6571)
        state_buffer = gp.GeoDataFrame(geometry = state_tracts.dissolve().buffer(100000))
        state_trauma = gp.sjoin(trauma, state_buffer, how = "inner")
        tract_centroids = state_tracts.centroid
        dist = tract_centroids.geometry.apply(lambda g: state_trauma.distance(g, align = False))
        min_dist = dist.min(axis = 'columns') / 1000
        hist_values = np.histogram(min_dist, bins = 24, range=(0,24))[0]

with st.container():
        st.subheader('Minimum distance to trauma center from tract centroid')
        st.bar_chart(hist_values)

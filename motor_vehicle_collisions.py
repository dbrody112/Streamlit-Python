import streamlit as st
# To make things easier later, we're also importing numpy and pandas for
# working with sample data.
import numpy as np
import pandas as pd
import datetime as dt
import pydeck as pdk
import plotly.express as px

DATA_URL =r"C:\Users\potat\Downloads\streamlitProj\Motor_Vehicle_Collisions_-_Crashes.csv"


st.title("Motor Vehicle Collisions in New York City")
st.markdown("## This application is a Streamlit dashboard that can be used to"
" analyze motor vehicle collisions in NYC 💥 🚗 ")

@st.cache(persist = True)
def load_data(nrows):
        data  = pd.read_csv("C:/Users/potat/Downloads/streamlitProj/Motor_Vehicle_Collisions_-_Crashes.csv", nrows = nrows, parse_dates = [['CRASH DATE','CRASH TIME']])
        data.dropna(subset = ['LATITUDE','LONGITUDE'], inplace = True)
        lowercase = lambda x: str(x).lower()
        data.rename(lowercase, axis = 'columns', inplace = True)
        data.rename(columns = {'crash date_crash time':'date/time'}, inplace = True)
        data['date_time'] = data['date/time'] + dt.timedelta()
        return data

data = load_data(200000)
original_data = data

st.header("Where are the most people injured in NYC?")
injured_people = st.slider("Number of people injured in vehicle collisions:", 0, 19)
x = data["number of persons injured"]
y = data[x>=injured_people]
st.map(y[['latitude','longitude']])

if(st.checkbox("Show Raw Data",False)):
    st.subheader('Raw Data')
    st.write(y)

st.header("How many collisions occur during a given time of day?")
hour = st.slider("Hour to select: ", 0,24)
data = data[data['date/time'].dt.hour == hour]

st.markdown("Vehicle Collisions Between %i:00 and %i:00" %(hour,(hour+1) % 24))
midpoint = (np.average(data['latitude']), np.average(data['longitude']))
st.write(pdk.bindings.deck.Deck(map_style = "mapbox://styles/mapbox/light-v9", initial_view_state = {
    'latitude': midpoint[0], 
    'longitude': midpoint[1],
    'zoom': 11,
    'pitch':50
},mapbox_key = 'pk.eyJ1IjoiZGJyb2R5MTEyIiwiYSI6ImNrOWdnZnE5NDBjdjYzbGxpZXRuMzIxOHMifQ.evx5PzKb1UAAn-_711UsQg',layers = [
pdk.Layer(
"HexagonLayer",
data = data[['date/time','latitude','longitude']],
get_position = ['longitude','latitude'],
radius  = 100,
extruded = True,
pickable = True,
elevation_scale = 4,
elevation_range = [0,1000],
),
],
))

st.subheader("Breakdown by minute between %i:00 and %i:00" % (hour,(hour+1)%24))
filtered = data[(data['date/time'].dt.hour >= hour) & (data['date/time'].dt.hour < (hour+1))]
hist = np.histogram(filtered['date/time'].dt.minute, bins = 60, range =(0,60))[0]
chart_data = pd.DataFrame({'minute':range(60), 'crashes':hist})
fig = px.bar(chart_data,x = 'minute', y='crashes', hover_data = ['minute','crashes'], height = 400)
st.write(fig)

if(st.checkbox("Show Raw Data",False, key = '2')):
    st.subheader('Raw Data')
    st.write(data)
    
st.header("Top 5 Dangerous Streets by Affected Type")
select = st.selectbox('Affected type of people',['Pedestrians','Cyclists','Motorists'])
if(select == 'Pedestrians'):
    st.write(original_data[original_data["number of pedestrians injured"] >= 1][["on street name","number of pedestrians injured"]].sort_values(by =["number of pedestrians injured"], ascending = False).dropna(how='any')[:5])
elif(select == 'Cyclists'):
    st.write(original_data[original_data["number of cyclist injured"] >= 1][["on street name","number of cyclist injured"]].sort_values(by =["number of cyclist injured"], ascending = False).dropna(how='any')[:5])
elif(select == 'Motorists'):
    st.write(original_data[original_data["number of motorist injured"] >= 1][["on street name","number of motorist injured"]].sort_values(by =["number of motorist injured"], ascending = False).dropna(how='any')[:5])


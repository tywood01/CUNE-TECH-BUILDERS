import streamlit as  st
import pandas as pd
import pydeck as pdk
from urllib.error import URLError
import os
import sqlite3
from geopy.geocoders import Nominatim
import geopy.distance


# Simulate the user's location
current_loc = [40.9143752, -97.0922022]  # Latitude and Longitude
current_address = " 805 N Columbia Ave. Seward, NE 68433"

# Initialize page in session state
if "page" not in st.session_state:
    st.session_state.page = "login"  # Default page is "login"

def compute_distance(loc1, loc2):
    return geopy.distance.distance(loc1, loc2).miles

# Define a function to change pages
def switch_page(page_name):
    st.session_state.page = page_name

# Define the Sign-Up page
def signup_page():
    st.title("Sign Up")
    st.write("Please fill out the form below to sign up.")
    name = st.text_input("Name")
    address = st.text_input("Address")
    phone = st.text_input("Phone")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    
    # Button to submit and switch to "main" page
    if st.button("Submit"):
        # Here you could add form validation if needed
        switch_page("main")

# Define the login page
def login_page():
    st.title("Login")
    phone = st.text_input("Phone")
    password = st.text_input("Password", type="password")
    
    # Button to submit and switch to "main" page
    if st.button("Submit"):
        # Here you could add form validation if needed
        switch_page("main")

def profile_page():
    st.title("Profile")
    st.write("Welcome to your profile page!")
    if st.button("Go Back"):
        switch_page("main")

# Define the Location page
def location_page():

    @st.cache_data
    def from_sql_query(query):
        conn = sqlite3.connect('C:/Users/tytus/OneDrive/Desktop/TechBuildersRepo/CUNE-TECH-BUILDERS/app/data.db')
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    try:
        ALL_LAYERS = {
            "Responders": pdk.Layer(
                "HexagonLayer",
                data=from_sql_query("SELECT longitude AS lon, latitude AS lat FROM Users"),
                get_position=["lon", "lat"],
                radius=50,
                elevation_scale=4,
                elevation_range=[0, 1000],
                extruded=True,
            ),
            "Emergencies": pdk.Layer(
                "ScatterplotLayer",
                data=from_sql_query("SELECT longitude AS lon, latitude AS lat FROM Requests"),
                get_position=["lon", "lat"],
                get_color=[200, 30, 0, 160],
                get_radius=100000,
                radius_scale=0.05,
            ),
            "Request Locations": pdk.Layer(
                "TextLayer",
                data=from_sql_query("SELECT longitude AS lon, latitude AS lat, description AS name FROM Requests"),
                get_position=["lon", "lat"],
                get_text="name",
                get_color=[0, 0, 0, 200],
                get_size=10,
                get_alignment_baseline="'bottom'",
            ),
            "Responder Paths": pdk.Layer(
                "ArcLayer",
                data=from_sql_query("SELECT u.longitude AS lon, u.latitude AS lat, r.longitude AS lon2, r.latitude AS lat2 FROM Users u, Requests r"),
                get_source_position=["lon", "lat"],
                get_target_position=["lon2", "lat2"],
                get_source_color=[200, 30, 0, 160],
                get_target_color=[200, 30, 0, 160],
                auto_highlight=True,
                width_scale=0.0001,
                get_width=1,
                width_min_pixels=3,
                width_max_pixels=30,
            ),
        }
        st.sidebar.markdown("### Map Layers")
        selected_layers = [
            layer
            for layer_name, layer in ALL_LAYERS.items()
            if st.sidebar.checkbox(layer_name, True)
        ]
        if selected_layers:
            st.pydeck_chart(
                pdk.Deck(
                    map_style=None,
                    initial_view_state={
                        "latitude": current_loc[0],
                        "longitude": current_loc[1],
                        "zoom": 11,
                        "pitch": 50,
                    },
                    layers=selected_layers,
                )
            )
        else:
            st.error("Please choose at least one layer above.")
    except URLError as e:
        st.error(
            """
            **This demo requires internet access.**
            Connection error: %s
        """
            % e.reason
        )

    combined_stats = from_sql_query("""
        SELECT r.latitude AS lat, r.longitude AS lon, r.description, r.address, u.username 
        FROM Requests r 
        JOIN Users u ON r.user_id = u.id
    """)
    st.write("Request Stats:")
    for index, row in combined_stats.iterrows():
        distance = compute_distance(current_loc, (row['lat'], row['lon']))
        with st.expander(f"{row['description']} ({distance:.2f} miles away)"):
            st.write(f"Address: {row['address']}")
            st.write(f"Requested by: {row['username']}")

    if st.button("Main Page"):
        switch_page("main")



def request_page():
    st.title("Request Help")
    st.write("Please fill out the form below to request help.")
    description = st.text_area("Description of the emergency")
    status = "new"

    user_id = 1


    use_current_location = st.checkbox("Use current location", value=True)


    if not use_current_location:
        address_input = st.text_input("Enter the address")
        if address_input:
            geolocator = Nominatim(user_agent="geoapiExercises")
            location = geolocator.geocode(address_input)
            if location:
                latitude = location.latitude
                longitude = location.longitude
            else:
                st.error("Address not found. Please enter a valid address.")
    else:
        address_input = current_address
        st.write(f"Using current location: {current_address}")
        longitude = current_loc[1]
        latitude = current_loc[0]

    timestamp = "2023-10-05 15:00:00"
    
    is_submitted = st.button("Submit")
    
    if is_submitted:
        # Logic to send alerts
        st.success("Request has been sent to nearby helpers!")
        st.write("You will be contacted shortly.")
        conn = sqlite3.connect('C:/Users/tytus/OneDrive/Desktop/TechBuildersRepo/CUNE-TECH-BUILDERS/app/data.db')
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Requests (user_id, address, description, status, timestamp, longitude, latitude)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, address_input, description, status, timestamp, longitude, latitude))
        conn.commit()
        conn.close()


    if st.button("Main Page"):
        switch_page("main")
        
    

# Define the Main page
def main_page():
    st.title("Main Page")
    st.write("Welcome to the main page!")

    if st.button("Respond to requests"):
        switch_page("location")

    if st.button("Request Help"):
        switch_page("request")

        

# Render the appropriate page based on the session state
if st.session_state.page == "signup":
    signup_page()
elif st.session_state.page == "main":
    main_page()
elif st.session_state.page == "location":
    location_page()
elif st.session_state.page == "login":
    login_page()
elif st.session_state.page == "profile":
    profile_page()
elif st.session_state.page == "request":
    request_page()
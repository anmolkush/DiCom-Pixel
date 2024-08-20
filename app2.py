import streamlit as st
from converter.cnv import main as cnv_main
from annotation.annotation import annotation_main  # Import the annotation function
from image_zoom.app import main as zoom_main

# Set page configuration
st.set_page_config(page_title="DiCom Pixel", layout="centered")

# Serve static files
st.markdown("""
    <style>
        /* Hide the Streamlit hamburger menu */
        #MainMenu {visibility: hidden;}
        
        /* Customize the page */
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            margin: 0;
            background-color: rgb(255, 255, 255);
            background-image: url('/static/main.jpg'); /* Updated to use the static folder */
            background-size: cover;
            background-position: center;
            padding: 0;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: rgba(255, 255, 255, 0.9);
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        h1 {
            margin-top: 0;
        }
        .option-button {
            padding: 10px 20px;
            margin: 10px;
            font-size: 20px;
            cursor: pointer;
            background-color: #4770bb;
            color: white;
            border: none;
            border-radius: 5px;
            transition: background-color 0.3s, transform 0.1s;
        }
        .option-button:hover {
            background-color: #45a049;
        }
        .option-button:active {
            background-color: #3e8e41;
            transform: scale(0.98);
        }
    </style>
""", unsafe_allow_html=True)

# App title
st.markdown("<h1 style='text-align: center;'>Welcome to the DiCom Pixel App</h1>", unsafe_allow_html=True)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# Center buttons in a single row
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

with col1:
    if st.button('Converter'):
        st.session_state.page = 'converter'

with col2:
    if st.button('Annotations'):
        st.session_state.page = 'annotations'

with col3:
    if st.button('Metadata'):
        st.session_state.page = 'metadata'

with col4:
    if st.button('Zooming'):
        st.session_state.page = 'zooming'

# Navigation logic
if st.session_state.page == 'converter':
    cnv_main()
elif st.session_state.page == 'annotations':
    annotation_main()
elif st.session_state.page == 'metadata':
    st.write("Metadata Page")
elif st.session_state.page == 'zooming':
    zoom_main()

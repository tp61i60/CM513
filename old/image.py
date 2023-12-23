import streamlit as st
from PIL import Image

pic = Image.open('sunrise.jpg')


st.image(pic, caption='**Sunrise**')
import streamlit as st

# Define the pages
main_page = st.Page("main_page.py", title="Main Page", icon="🎈")
data_page = st.Page("data_page.py", title="Data Page", icon="🎈")

# Set up navigation
pg = st.navigation([main_page, data_page])

# Run the selected page
pg.run()
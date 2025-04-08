
# import streamlit as st
# import pandas as pd
# import ast
# import os
# import urllib.parse
# import validators  # Install with `pip install validators`

# # --- Configuration ---
# DATA_FILE = "F:/softograph/news_demo/processed_data/analyzed_articles.csv"

# # --- Data Loading Function ---
# @st.cache_data
# def load_data(data_path):
#     script_dir = os.getcwd()
#     absolute_data_path = os.path.join(script_dir, data_path)

#     if not os.path.exists(absolute_data_path):
#         st.error(f"Error: Data file not found at expected location: '{absolute_data_path}'")
#         st.warning("Please ensure you have run the `src/process_scraped_files.py` script first to generate the data file.")
#         st.markdown("""
#             **Steps to Generate Data:**
#             1. Navigate to the `src` directory.
#             2. Run the command: `python process_scraped_files.py`.
#             3. Ensure the `processed_data` folder contains `analyzed_articles.csv`.
#         """)
#         return pd.DataFrame()

#     try:
#         df = pd.read_csv(absolute_data_path)
#         for col in ['locations', 'names', 'categories']:
#             if col in df.columns:
#                 df[col] = df[col].apply(
#                     lambda x: ast.literal_eval(x)
#                     if isinstance(x, str) and x.startswith('[') and x.endswith(']')
#                     else []
#                 )
#         return df
#     except Exception as e:
#         st.error(f"An error occurred loading data from '{absolute_data_path}': {e}")
#         return pd.DataFrame()

# # --- Streamlit App Layout ---
# st.set_page_config(layout="wide")
# st.title("Newspaper Analysis App (From Scraped Data)")
# st.markdown("Data processed from Firecrawl JSON files using Gemini.")

# # Load the processed data
# with st.spinner("Loading data..."):
#     data_df = load_data(DATA_FILE)

# if not data_df.empty:
#     # --- Sidebar for Filtering ---
#     st.sidebar.header("Filter Articles")
#     location_input = st.sidebar.text_input("Enter a Location (e.g., Dhaka, USA):", key="location_filter")
#     category_input = st.sidebar.multiselect("Filter by Category:", options=data_df['categories'].explode().unique(), key="category_filter")
#     name_input = st.sidebar.text_input("Search by Name:", key="name_filter")

#     # --- Filtering Logic ---
#     filtered_df = data_df
#     if location_input:
#         location_search_term = location_input.strip().lower()
#         filtered_df = filtered_df[
#             filtered_df['locations'].apply(
#                 lambda loc_list: any(location_search_term in str(loc).lower() for loc in loc_list)
#             )
#         ]
#     if category_input:
#         filtered_df = filtered_df[filtered_df['categories'].apply(lambda cats: any(cat in category_input for cat in cats))]
#     if name_input:
#         name_search_term = name_input.strip().lower()
#         filtered_df = filtered_df[filtered_df['names'].apply(lambda names: any(name_search_term in str(name).lower() for name in names))]

#     # --- Display Results ---
#     st.subheader(f"Displaying Articles ({len(filtered_df)} found)")

#     if not filtered_df.empty:
#         # Pagination
#         articles_per_page = 10
#         total_pages = (len(filtered_df) // articles_per_page) + (1 if len(filtered_df) % articles_per_page != 0 else 0)
#         page_number = st.number_input("Page Number", min_value=1, max_value=total_pages, value=1)
#         start_idx = (page_number - 1) * articles_per_page
#         end_idx = start_idx + articles_per_page
#         paginated_df = filtered_df.iloc[start_idx:end_idx]

#         for _, row in paginated_df.iterrows():
#             with st.container(border=True):
#                 headline = str(row.get('headline', 'No Headline Available'))
#                 summary = str(row.get('summary', 'No Summary Available'))
#                 raw_url = str(row.get('url', '#'))  # Raw URL from the DataFrame

#                 # Validate and sanitize the URL
#                 if raw_url and raw_url != '#' and validators.url(raw_url):
#                     sanitized_url = raw_url.strip()  # Remove leading/trailing whitespace
#                     encoded_url = urllib.parse.quote(sanitized_url, safe=':/?&=%#')  # Encode unsafe characters
#                 else:
#                     encoded_url = '#'  # Fallback to '#' if URL is invalid

#                 # Generate the Markdown link
#                 if encoded_url != '#':
#                     st.markdown(f"### [{headline}]({encoded_url})")  # Properly formatted Markdown link
#                 else:
#                     st.markdown(f"### {headline}")  # No link if URL is invalid

#                 # Display article details
#                 categories = row.get('categories', [])
#                 locations = row.get('locations', [])
#                 names = row.get('names', [])

#                 categories_str = ', '.join(categories) if categories else 'Not Available'
#                 locations_str = ', '.join(locations) if locations else 'Not Available'
#                 names_str = ', '.join(names) if names else 'Not Available'

#                 st.caption(f"Categories: `{categories_str}`")
#                 st.write(summary)

#                 col1, col2 = st.columns(2)
#                 with col1:
#                     st.markdown("**Mentioned Locations:**")
#                     st.write(f"`{locations_str}`")
#                 with col2:
#                     st.markdown("**Mentioned Names:**")
#                     st.write(f"`{names_str}`")

#         # Export Button
#         st.download_button(
#             label="Export Filtered Articles as CSV",
#             data=filtered_df.to_csv(index=False, encoding='utf-8'),
#             file_name="filtered_articles.csv",
#             mime="text/csv"
#         )

#     elif location_input or category_input or name_input:
#         st.info(f"No articles found matching the filters.")
#     else:
#         st.info("Showing all articles. Use the sidebar to filter.")

# else:
#     st.warning("No data available. Please ensure the data file is generated correctly.")




# ********* create a sub locations ******

# import streamlit as st
# import pandas as pd
# import ast
# import os
# import urllib.parse
# import validators  # Install with `pip install validators`

# # --- Configuration ---
# DATA_FILE = "F:/softograph/news_demo/processed_data/analyzed_articles.csv"

# # --- Data Loading Function ---
# @st.cache_data
# def load_data(data_path):
#     script_dir = os.getcwd()
#     absolute_data_path = os.path.join(script_dir, data_path)

#     if not os.path.exists(absolute_data_path):
#         st.error(f"Error: Data file not found at expected location: '{absolute_data_path}'")
#         st.warning("Please ensure you have run the `src/process_scraped_files.py` script first to generate the data file.")
#         st.markdown("""
#             **Steps to Generate Data:**
#             1. Navigate to the `src` directory.
#             2. Run the command: `python process_scraped_files.py`.
#             3. Ensure the `processed_data` folder contains `analyzed_articles.csv`.
#         """)
#         return pd.DataFrame()
    

#     try:
#         df = pd.read_csv(absolute_data_path)
#         for col in ['locations', 'names', 'categories']:
#             if col in df.columns:
#                 df[col] = df[col].apply(
#                     lambda x: ast.literal_eval(x)
#                     if isinstance(x, str) and x.startswith('[') and x.endswith(']')
#                     else []
#                 )
#         return df
#     except Exception as e:
#         st.error(f"An error occurred loading data from '{absolute_data_path}': {e}")
#         return pd.DataFrame()

# # --- Streamlit App Layout ---
# st.set_page_config(layout="wide")
# st.title(" Newspaper Analysis App (From Scraped Data)")
# st.markdown("Data processed from Firecrawl JSON files using Gemini.")

# # Load the processed data
# with st.spinner("Loading data..."):
#     data_df = load_data(DATA_FILE)

# if not data_df.empty:
#     # --- Sidebar for Filtering ---
#     st.sidebar.header("Filter Articles")
    
#     # Main Location Input
#     main_location_input = st.sidebar.text_input("Enter Main Location (e.g., Bangladesh):", key="main_location_filter")
    
#     # Sub-Location Input
#     sub_location_input = st.sidebar.text_input("Enter Specific Area (e.g., District, Thana, Union, Village):", key="sub_location_filter")
    
#     # Category Filter
#     category_input = st.sidebar.multiselect("Filter by Category:", options=data_df['categories'].explode().unique(), key="category_filter")
    
#     # Name Filter
#     name_input = st.sidebar.text_input("Search by Name:", key="name_filter")

#     # --- Filtering Logic ---
#     filtered_df = data_df
    
#     # Filter by Main Location
#     if main_location_input:
#         main_location_search_term = main_location_input.strip().lower()
#         filtered_df = filtered_df[
#             filtered_df['locations'].apply(
#                 lambda loc_list: any(main_location_search_term in str(loc).lower() for loc in loc_list)
#             )
#         ]
    
#     # Filter by Sub-Location
#     if sub_location_input:
#         sub_location_search_term = sub_location_input.strip().lower()
#         filtered_df = filtered_df[
#             filtered_df['locations'].apply(
#                 lambda loc_list: any(sub_location_search_term in str(loc).lower() for loc in loc_list)
#             )
#         ]
    
#     # Filter by Category
#     if category_input:
#         filtered_df = filtered_df[filtered_df['categories'].apply(lambda cats: any(cat in category_input for cat in cats))]
    
#     # Filter by Name
#     if name_input:
#         name_search_term = name_input.strip().lower()
#         filtered_df = filtered_df[filtered_df['names'].apply(lambda names: any(name_search_term in str(name).lower() for name in names))]

#     # --- Display Results ---
#     st.subheader(f"Displaying Articles ({len(filtered_df)} found)")

#     if not filtered_df.empty:
#         # Pagination
#         articles_per_page = 10
#         total_pages = (len(filtered_df) // articles_per_page) + (1 if len(filtered_df) % articles_per_page != 0 else 0)
#         page_number = st.number_input("Page Number", min_value=1, max_value=total_pages, value=1)
#         start_idx = (page_number - 1) * articles_per_page
#         end_idx = start_idx + articles_per_page
#         paginated_df = filtered_df.iloc[start_idx:end_idx]

#         for _, row in paginated_df.iterrows():
#             with st.container(border=True):
#                 headline = str(row.get('headline', 'No Headline Available'))
#                 summary = str(row.get('summary', 'No Summary Available'))
#                 raw_url = str(row.get('url', '#'))  # Raw URL from the DataFrame

#                 # Validate and sanitize the URL
#                 if raw_url and raw_url != '#' and validators.url(raw_url):
#                     sanitized_url = raw_url.strip()  # Remove leading/trailing whitespace
#                     encoded_url = urllib.parse.quote(sanitized_url, safe=':/?&=%#')  # Encode unsafe characters
#                 else:
#                     encoded_url = '#'  # Fallback to '#' if URL is invalid

#                 # Generate the Markdown link
#                 if encoded_url != '#':
#                     st.markdown(f"### [{headline}]({encoded_url})")  # Properly formatted Markdown link
#                 else:
#                     st.markdown(f"### {headline}")  # No link if URL is invalid

#                 # Display article details
#                 categories = row.get('categories', [])
#                 locations = row.get('locations', [])
#                 names = row.get('names', [])

#                 categories_str = ', '.join(categories) if categories else 'Not Available'
#                 locations_str = ', '.join(locations) if locations else 'Not Available'
#                 names_str = ', '.join(names) if names else 'Not Available'

#                 st.caption(f"Categories: `{categories_str}`")
#                 st.write(summary)

#                 col1, col2 = st.columns(2)
#                 with col1:
#                     st.markdown("**Mentioned Locations:**")
#                     st.write(f"`{locations_str}`")
#                 with col2:
#                     st.markdown("**Mentioned Names:**")
#                     st.write(f"`{names_str}`")

#         # Export Button
#         st.download_button(
#             label="Export Filtered Articles as CSV",
#             data=filtered_df.to_csv(index=False, encoding='utf-8'),
#             file_name="filtered_articles.csv",
#             mime="text/csv"
#         )

#     elif main_location_input or sub_location_input or category_input or name_input:
#         st.info(f"No articles found matching the filters.")
#     else:
#         st.info("Showing all articles. Use the sidebar to filter.")

# else:
#     st.warning("No data available. Please ensure the data file is generated correctly.")




# ********* using openstreetmap******

import streamlit as st
import pandas as pd
import ast
import os
import urllib.parse
import validators
import requests  # For interacting with OpenStreetMap Nominatim API
import folium  # For OpenStreetMap integration
from streamlit_folium import st_folium  # To display Folium maps in Streamlit

# --- Configuration ---
DATA_FILE = "F:/softograph/news_demo/processed_data/analyzed_articles.csv"

# --- Data Loading Function ---
@st.cache_data
def load_data(data_path):
    script_dir = os.getcwd()
    absolute_data_path = os.path.join(script_dir, data_path)

    if not os.path.exists(absolute_data_path):
        st.error(f"Error: Data file not found at expected location: '{absolute_data_path}'")
        st.warning("Please ensure you have run the `src/process_scraped_files.py` script first to generate the data file.")
        st.markdown("""
            **Steps to Generate Data:**
            1. Navigate to the `src` directory.
            2. Run the command: `python process_scraped_files.py`.
            3. Ensure the `processed_data` folder contains `analyzed_articles.csv`.
        """)
        return pd.DataFrame()

    try:
        df = pd.read_csv(absolute_data_path)
        for col in ['locations', 'names', 'categories']:
            if col in df.columns:
                df[col] = df[col].apply(
                    lambda x: ast.literal_eval(x)
                    if isinstance(x, str) and x.startswith('[') and x.endswith(']')
                    else []
                )
        return df
    except Exception as e:
        st.error(f"An error occurred loading data from '{absolute_data_path}': {e}")
        return pd.DataFrame()

# --- Function to Reverse Geocode Coordinates Using OpenStreetMap Nominatim API ---
def reverse_geocode(lat, lng):
    nominatim_url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        "lat": lat,
        "lon": lng,
        "format": "json",
        "zoom": 18  # High zoom level for more precise location
    }
    headers = {
        "User-Agent": "NewsAnalysisApp/1.0"  # Required by Nominatim usage policy
    }
    try:
        response = requests.get(nominatim_url, params=params, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        if data and 'address' in data:
            # Extract relevant location details (city, village, district, etc.)
            address = data['address']
            location_name = (
                address.get('village') or
                address.get('town') or
                address.get('city') or
                address.get('county') or
                address.get('state') or
                address.get('country')
            )
            return location_name
        else:
            st.warning(f"No location found for coordinates: Latitude={lat}, Longitude={lng}")
            return None
    except Exception as e:
        st.error(f"Error reverse geocoding coordinates (Lat: {lat}, Lon: {lng}): {e}")
        return None

# --- Streamlit App Layout ---
st.set_page_config(layout="wide")
st.title("📰 Newspaper Analysis App (From Scraped Data)")
st.markdown("Data processed from Firecrawl JSON files using Gemini.")

# Load the processed data
with st.spinner("Loading data..."):
    data_df = load_data(DATA_FILE)

if not data_df.empty:
    # --- Sidebar for Filtering ---
    st.sidebar.header("Filter Articles")
    
    # Category Filter
    category_input = st.sidebar.multiselect("Filter by Category:", options=data_df['categories'].explode().unique(), key="category_filter")
    
    # Name Filter
    name_input = st.sidebar.text_input("Search by Name:", key="name_filter")

    # --- OpenStreetMap Integration ---
    st.subheader("Select a Location on the Map")
    m = folium.Map(location=[23.6850, 90.3563], zoom_start=7)  # Centered on Bangladesh
    map_output = st_folium(m, width=800, height=500)

    # Extract clicked location coordinates
    clicked_location = map_output.get("last_clicked")
    if clicked_location:
        lat, lng = clicked_location["lat"], clicked_location["lng"]
        st.success(f"Clicked Location: Latitude={lat}, Longitude={lng}")

        # Reverse geocode the clicked coordinates to get the location name
        location_name = reverse_geocode(lat, lng)
        if location_name:
            st.info(f"Location Name: {location_name}")
        else:
            st.warning("Could not determine the location name for the clicked coordinates.")
            location_name = None
    else:
        location_name = None

    # --- Filtering Logic ---
    filtered_df = data_df
    
    # Filter by Clicked Location
    if location_name:
        location_search_term = location_name.strip().lower()
        filtered_df = filtered_df[
            filtered_df['locations'].apply(
                lambda loc_list: any(location_search_term in str(loc).lower() for loc in loc_list)
            )
        ]
    
    # Filter by Category
    if category_input:
        filtered_df = filtered_df[filtered_df['categories'].apply(lambda cats: any(cat in category_input for cat in cats))]
    
    # Filter by Name
    if name_input:
        name_search_term = name_input.strip().lower()
        filtered_df = filtered_df[filtered_df['names'].apply(lambda names: any(name_search_term in str(name).lower() for name in names))]

    # --- Display Results ---
    st.subheader(f"Displaying Articles ({len(filtered_df)} found)")

    if not filtered_df.empty:
        # Pagination
        articles_per_page = 10
        total_pages = (len(filtered_df) // articles_per_page) + (1 if len(filtered_df) % articles_per_page != 0 else 0)
        page_number = st.number_input("Page Number", min_value=1, max_value=total_pages, value=1)
        start_idx = (page_number - 1) * articles_per_page
        end_idx = start_idx + articles_per_page
        paginated_df = filtered_df.iloc[start_idx:end_idx]

        for _, row in paginated_df.iterrows():
            with st.container(border=True):
                headline = str(row.get('headline', 'No Headline Available'))
                summary = str(row.get('summary', 'No Summary Available'))
                raw_url = str(row.get('url', '#'))  # Raw URL from the DataFrame

                # Validate and sanitize the URL
                if raw_url and raw_url != '#' and validators.url(raw_url):
                    sanitized_url = raw_url.strip()  # Remove leading/trailing whitespace
                    encoded_url = urllib.parse.quote(sanitized_url, safe=':/?&=%#')  # Encode unsafe characters
                else:
                    encoded_url = '#'  # Fallback to '#' if URL is invalid

                # Generate the Markdown link
                if encoded_url != '#':
                    st.markdown(f"### [{headline}]({encoded_url})")  # Properly formatted Markdown link
                else:
                    st.markdown(f"### {headline}")  # No link if URL is invalid

                # Display article details
                categories = row.get('categories', [])
                locations = row.get('locations', [])
                names = row.get('names', [])

                categories_str = ', '.join(categories) if categories else 'Not Available'
                locations_str = ', '.join(locations) if locations else 'Not Available'
                names_str = ', '.join(names) if names else 'Not Available'

                st.caption(f"Categories: `{categories_str}`")
                st.write(summary)

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Mentioned Locations:**")
                    st.write(f"`{locations_str}`")
                with col2:
                    st.markdown("**Mentioned Names:**")
                    st.write(f"`{names_str}`")

        # Export Button
        st.download_button(
            label="Export Filtered Articles as CSV",
            data=filtered_df.to_csv(index=False, encoding='utf-8'),
            file_name="filtered_articles.csv",
            mime="text/csv"
        )

    elif location_name or category_input or name_input:
        st.info(f"No articles found matching the filters.")
    else:
        st.info("Showing all articles. Use the sidebar or map to filter.")

else:
    st.warning("No data available. Please ensure the data file is generated correctly.")

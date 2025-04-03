import streamlit as st
import pandas as pd
from pymongo import MongoClient

# Connect to MongoDB (update with your connection details)
client = MongoClient('mongodb+srv://duck:quack@bubble.ggmhr.mongodb.net/?retryWrites=true&w=majority&appName=Bubble')  # Replace with your connection string
db = client['steam_db']
collection = db['games']

import streamlit as st
from pymongo import MongoClient

# Connect to MongoDB (replace with your connection string)
client = MongoClient('mongodb+srv://duck:quack@bubble.ggmhr.mongodb.net/?retryWrites=true&w=majority&appName=Bubble')
db = client['SteamGamesCloud']
collection = db['gamesCloud']

# Fetch data from MongoDB
data = list(collection.find({}, {'_id': 1, 'Title': 1, 'Original Price': 1, 'Discounted Price': 1, 'Release Date': 1, 'Link': 1, 'Game Description': 1, 'Recent Reviews Summary': 1, 'All Reviews Summary': 1, 'Recent Reviews Number': 1, 'All Reviews Number': 1, 'Developer':
1, 'Publisher': 1, 'Supported Languages': 1, 'Popular Tags': 1, 'Game Features': 1, 'Minimum Requirements': 1}))

# Streamlit app code
st.title('Forza Horizon 5 Showcase')

for item in data:
    st.header(item['Title'])
    st.image("https://store.steampowered.com/app/1551360/Forza_Horizon_5//header.jpg", width=200)  # Placeholder for actual image link
    st.write(f"Original Price: {item['Original Price']}")
    st.write(f"Discounted Price: {item['Discounted Price']}")
    st.write(f"Release Date: {item['Release Date']}")
    st.write(f"Description: {item['Game Description']}")
    st.write(f"Recent Reviews: {item['Recent Reviews Summary']} ({item['Recent Reviews Number']})")
    st.write(f"All Reviews: {item['All Reviews Summary']} ({item['All Reviews Number']})")
    st.write(f"Developer: {item['Developer']}")
    st.write(f"Publisher: {item['Publisher']}")
    st.write(f"Supported Languages: {', '.join(item['Supported Languages'])}")
    st.write(f"Popular Tags: {', '.join(item['Popular Tags'])}")
    st.write(f"Game Features: {', '.join(item['Game Features'])}")
    st.write(f"Minimum Requirements: {item['Minimum Requirements']}")

    # Add like button and logging mechanism if needed
    if st.button('Like'):
        st.write("Thank you for your like!")

# # Load data from MongoDB into DataFrame
# def load_data():
#     cursor = collection.find()
#     df = pd.DataFrame(list(cursor))
#     return df

# df = load_data()

# # # Check columns after loading data
# # st.write(f"Columns available in the DataFrame: {df.columns}")

# # Streamlit App UI
# st.title("Steam Games - Deals and Discounts")

# # Display basic game stats
# st.write("### Game Listings")
# st.write(f"Total Games Available: {len(df)}")

# # Filters for User Selection
# st.sidebar.header("Filter by:")

# # Handle missing 'Discounted Price' column and NaN values
# if 'Discounted Price' in df.columns:
#     # Remove dollar signs and convert to numeric for filtering
#     df['Discounted Price'] = df['Discounted Price'].replace({'\$': '', ',': ''}, regex=True).astype(float)
#     df['Original Price'] = df['Original Price'].replace({'\$': '', ',': ''}, regex=True).astype(float)

#     df = df.dropna(subset=['Discounted Price'])  # Drop rows where 'Discounted Price' is NaN
#     if not df.empty:
#         min_price, max_price = df['Discounted Price'].min(), df['Discounted Price'].max()
#     else:
#         min_price, max_price = 0, 100  # Default reasonable range if no valid price data exists
#     selected_price_range = st.sidebar.slider(
#         "Select Price Range", 
#         min_value=0,  # Ensure min_value is always at least 0
#         max_value=max_price, 
#         value=(min_price, max_price)  # Default range from min_price to max_price
#     )

#     # Apply Filters based on Discounted Price
#     filtered_df = df[
#         (df['Discounted Price'] >= selected_price_range[0]) &
#         (df['Discounted Price'] <= selected_price_range[1]) &
#         (df['Rating'] >= selected_rating)
#     ]
# else:
#     st.warning("Discounted Price data not available. Please check the MongoDB data.")
#     filtered_df = df  # No filtering on price if it's missing

# genres = df['Popular Tags'].dropna().unique()
# selected_genre = st.sidebar.selectbox("Select Genre", ["All"] + list(genres))

# selected_rating = st.sidebar.slider("Select Minimum Rating", 0.0, 5.0, 3.5)
# on_sale = st.sidebar.checkbox("Show only on-sale games")

# if selected_genre != "All":
#     filtered_df = filtered_df[filtered_df['Popular Tags'].str.contains(selected_genre, case=False, na=False)]

# if on_sale:
#     filtered_df = filtered_df[filtered_df['on_sale'] == True]

# # Display filtered game list
# st.write(f"### Showing {len(filtered_df)} games")
# st.dataframe(filtered_df[['Title', 'Discounted Price', 'Rating', 'Release Date', 'Popular Tags', 'on_sale']])

# # Sorting options
# sort_by = st.sidebar.selectbox("Sort by:", ["Discounted Price", "Rating", "Release Date"])
# if sort_by == "Discounted Price":
#     filtered_df = filtered_df.sort_values(by="Discounted Price", ascending=True)
# elif sort_by == "Rating":
#     filtered_df = filtered_df.sort_values(by="Rating", ascending=False)
# elif sort_by == "Release Date":
#     filtered_df = filtered_df.sort_values(by="Release Date", ascending=False)

# # Display sorted games
# st.write(f"### Sorted Games - {sort_by}")
# st.dataframe(filtered_df[['Title', 'Discounted Price', 'Rating', 'Release Date', 'Popular Tags', 'on_sale']])

# # Display detailed game info when clicked
# game_to_show = st.selectbox("Select a Game", filtered_df['Title'])
# game_details = filtered_df[filtered_df['Title'] == game_to_show].iloc[0]

# st.write("### Game Details")
# st.write(f"**Title**: {game_details['Title']}")
# st.write(f"**Discounted Price**: ${game_details['Discounted Price']}")
# st.write(f"**Original Price**: ${game_details['Original Price']}")
# st.write(f"**Rating**: {game_details['Rating']}/5")
# st.write(f"**Release Date**: {game_details['Release Date']}")
# st.write(f"**Description**: {game_details['Game Description']}")
# st.write(f"**Genres**: {game_details['Popular Tags']}")
# st.write(f"**Developer**: {game_details['Developer']}")
# st.write(f"**Publisher**: {game_details['Publisher']}")
# st.write(f"**Supported Languages**: {game_details['Supported Languages']}")
# st.write(f"**Link**: [Click here]({game_details['Link']})")
# st.write(f"**On Sale**: {'Yes' if game_details['on_sale'] else 'No'}")

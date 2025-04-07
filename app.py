import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from pymongo import MongoClient  # Add the MongoClient import
from io import StringIO
import json

<<<<<<< HEAD
# Connect to MongoDB (update with your connection details)
client = MongoClient('mongodb://localhost:27017/')  # Replace with your connection string
db = client['steam_db']
collection = db['games']
=======
@st.cache_resource
def load_data_from_mongo():
    # MongoDB Atlas connection string
    client = MongoClient('mongodb+srv://duck:quack@bubble.ggmhr.mongodb.net/?retryWrites=true&w=majority&appName=Bubble')
    db = client["SteamGamesCloud"]
    games_collection = db["gamesCloud"]

# Load the dataset from MongoDB Atlas
df = load_data_from_mongo()

# Step 2: Data Transformation (Adapted for the new dataset)
def clean_data(df):
    # Drop rows with missing values in important columns
    df = df.dropna(subset=['title', 'developer', 'publisher', 'genres', 'original_price', 'discounted_price'])
    
    # Convert 'price' and 'discounted_price' to numeric (remove '$' and ',' if any)
    df['original_price'] = df['original_price'].replace({'\$': '', ',': ''}, regex=True).astype(float)
    df['discounted_price'] = df['discounted_price'].replace({'\$': '', ',': ''}, regex=True).astype(float)
    
    # Extract year from the release date (adjust to your dataset's column name)
    df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
    df['release_year'] = df['release_date'].dt.year
    
    # Handle missing genres (some games may not have any genre listed)
    df['genres'] = df['genres'].fillna('Unknown')
    
    return df

df_clean = clean_data(df)  # Fixed variable reference

# Display the cleaned data in the app
st.write("Cleaned Data", df_clean.head())

# Step 3: Filter System

# Filter by Genre
genres = df_clean['genres'].str.split(',').explode().unique().tolist()  # Fixed genre splitting
selected_genres = st.multiselect("Select Genre(s)", genres, default=genres)

# Filter by Release Year
min_year = df_clean['release_year'].min()
max_year = df_clean['release_year'].max()
selected_years = st.slider("Select Release Year Range", min_year, max_year, (min_year, max_year))

# Filter by Price
min_price = df_clean['discounted_price'].min()
max_price = df_clean['discounted_price'].max()
selected_price_range = st.slider("Select Price Range", min_price, max_price, (min_price, max_price))

# Apply filters to the data
filtered_df = df_clean[
    df_clean['genres'].apply(lambda x: any(genre in selected_genres for genre in x.split(','))) &  # Fixed genre check
    (df_clean['release_year'] >= selected_years[0]) &
    (df_clean['release_year'] <= selected_years[1]) &
    (df_clean['discounted_price'] >= selected_price_range[0]) &
    (df_clean['discounted_price'] <= selected_price_range[1])
]

# Display filtered data
st.write(f"Filtered Data (Total {len(filtered_df)} games)", filtered_df)

# Step 4: "Like" Feature (Save Game to Wishlist)
st.subheader("Like a Game to Add to Your Wishlist")

# Simulate user login with a username
username = st.text_input("Enter your username:")

if username:
    # Check if the user exists in the users collection (we will simulate this part)
    if 'user_data' not in st.session_state:
        st.session_state.user_data = {"username": username, "wishlist": []}
    
    # Display User's Wishlist
    st.subheader(f"Welcome {username}!")
    st.write("Here are the games you've liked (your wishlist):")
    
    # Display the wishlist games for the current user
    wishlist_game_ids = st.session_state.user_data["wishlist"]
    
    # Simulate fetching games from the wishlist (mocking it here)
    wishlist_games = filtered_df[filtered_df['title'].isin(wishlist_game_ids)]
    
    if not wishlist_games.empty:
        st.write(wishlist_games[['title', 'price', 'discounted_price', 'release_date', 'genres']])
    else:
        st.write("Your wishlist is empty.")

# Loop through the filtered data and display each game with a "Like" button
st.subheader("Like a Game to Add to Your Wishlist")

for index, row in filtered_df.iterrows():
    game_title = row['title']
    game_price = row['original_price']
    game_discounted_price = row['discounted_price']
    game_release_date = row['release_date']
    game_genres = ', '.join(row['genres'].split(','))
    game_description = row['game_description']
    game_reviews_recent = row['recent_reviews_summary']
    game_reviews_all = row['all_reviews_summary']
    game_reviews_recent_num = row['recent_reviews_number']
    game_reviews_all_num = row['all_reviews_number']
    game_developer = row['developer']
    game_publisher = row['publisher']
    game_languages = ', '.join(row['supported_languages'])
    game_tags = ', '.join(row['popular_tags'])
    game_features = ', '.join(row['game_features'])
    game_requirements = row['minimum_requirements']
    game_link = row['link']
    
    # Display game details
    st.write(f"**{game_title}**")
    st.write(f"Price: ${game_price} | Discounted Price: ${game_discounted_price}")
    st.write(f"Release Date: {game_release_date.strftime('%Y-%m-%d')}")
    st.write(f"Genres: {game_genres}")
    st.write(f"Description: {game_description}")
    st.write(f"Recent Reviews: {game_reviews_recent}")
    st.write(f"All Reviews: {game_reviews_all}")
    st.write(f"Recent Reviews Number: {game_reviews_recent_num}")
    st.write(f"All Reviews Number: {game_reviews_all_num}")
    st.write(f"Developer: {game_developer}")
    st.write(f"Publisher: {game_publisher}")
    st.write(f"Supported Languages: {game_languages}")
    st.write(f"Popular Tags: {game_tags}")
    st.write(f"Game Features: {game_features}")
    st.write(f"Minimum Requirements: {game_requirements}")
    st.write(f"[Link to Game]({game_link})")
    
    # "Like" button (Add to wishlist)
    like_button = st.button(f"❤️ Like {game_title}", key=str(index))  # Fixed key for the button
    
    if like_button and username:
        # Add game to user's wishlist in session state (simulating MongoDB update)
        st.session_state.user_data["wishlist"].append(game_title)
        st.success(f"Game '{game_title}' has been added to your wishlist!")

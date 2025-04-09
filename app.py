import pandas as pd
import streamlit as st
from pymongo import MongoClient

@st.cache_resource
def load_data_from_mongo():
    # MongoDB Atlas connection string
    client = MongoClient('mongodb+srv://duck:quack@bubble.ggmhr.mongodb.net/?retryWrites=true&w=majority&appName=Bubble')
    db = client["SteamGamesCloud"]
    games_collection = db["gamesCloud"]
    users_collection = db["usersCloud"]

    # Fetch data from MongoDB
    games_data = list(games_collection.find())
    
    # Convert to DataFrame
    df = pd.DataFrame(games_data)
    return df

# Load the dataset from MongoDB
df = load_data_from_mongo()

def clean_data(df):
    # Drop rows with missing values in important columns
    df = df.dropna(subset=['title', 'developer', 'publisher', 'genres', 'original_price', 'discounted_price'])
    
    # Convert 'price' and 'discounted_price' to numeric (remove '$' and ',' if any)
    df['original_price'] = df['original_price'].replace({'\$': '', ',': ''}, regex=True).astype(float)
    df['discounted_price'] = df['discounted_price'].replace({'\$': '', ',': ''}, regex=True).astype(float)
    
    # Extract year from the release date
    df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
    df['release_year'] = df['release_date'].dt.year
    
    # Handle missing genres
    df['genres'] = df['genres'].apply(lambda x: ', '.join(x) if isinstance(x, list) else '')
    
    return df

df_clean = clean_data(df)

# Display the cleaned data
st.write("Cleaned Data", df_clean.head())

# Filter System
genres = df_clean['genres'].str.split(',').explode().unique().tolist()
selected_genres = st.multiselect("Select Genre(s)", genres, default=genres)

min_year = df_clean['release_year'].min()
max_year = df_clean['release_year'].max()
selected_years = st.slider("Select Release Year Range", min_year, max_year, (min_year, max_year))

min_price = df_clean['discounted_price'].min()
max_price = df_clean['discounted_price'].max()
selected_price_range = st.slider("Select Price Range", min_price, max_price, (min_price, max_price))

filtered_df = df_clean[
    df_clean['genres'].apply(lambda x: any(genre in selected_genres for genre in x.split(','))) &
    (df_clean['release_year'] >= selected_years[0]) &
    (df_clean['release_year'] <= selected_years[1]) &
    (df_clean['discounted_price'] >= selected_price_range[0]) &
    (df_clean['discounted_price'] <= selected_price_range[1])
]

st.write(f"Filtered Data (Total {len(filtered_df)} games)", filtered_df)

# Handle Wishlist
username = st.text_input("Enter your username:")

if username:
    if 'user_data' not in st.session_state:
        st.session_state.user_data = {"username": username, "wishlist": []}
    
    # Display User's Wishlist
    st.write("Here are the games you've liked (your wishlist):")
    wishlist_game_ids = st.session_state.user_data["wishlist"]
    
    if wishlist_game_ids:
        wishlist_games = df_clean[df_clean['title'].isin(wishlist_game_ids)]
        st.write(wishlist_games[['title', 'discounted_price', 'release_date']])
    else:
        st.write("Your wishlist is empty.")

# Display games with "Like" buttons
for index, row in filtered_df.iterrows():
    game_title = row['title']
    game_price = row['original_price']
    game_discounted_price = row['discounted_price']
    game_release_date = row['release_date']
    game_genres = ', '.join(row['genres'].split(','))
    
    st.write(f"**{game_title}**")
    st.write(f"Price: ${game_price} | Discounted Price: ${game_discounted_price}")
    st.write(f"Release Date: {game_release_date.strftime('%Y-%m-%d')}")
    st.write(f"Genres: {game_genres}")
    
    # "Like" button
    like_button = st.button(f"❤️ Like {game_title}", key=f"like_{index}")
    
    if like_button and username:
        if game_title not in st.session_state.user_data["wishlist"]:
            st.session_state.user_data["wishlist"].append(game_title)
            st.success(f"Game '{game_title}' has been added to your wishlist!")
        else:
            st.warning(f"Game '{game_title}' is already in your wishlist.")

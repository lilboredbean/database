from pymongo import MongoClient
import streamlit as st
<<<<<<< HEAD
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
=======
import ast
import requests

# MongoDB connection
def connect_to_mongo():
    try:
        client = MongoClient("mongodb+srv://duck:quack@bubble.ggmhr.mongodb.net/?retryWrites=true&w=majority&appName=Bubble", serverSelectionTimeoutMS=5000)
        db = client['SteamGamesCloud']  # Update with your DB name
        return db
    except Exception as e:
        st.error(f"Error connecting to MongoDB: {e}")
        return None

# Signup function
def signup():
    db = connect_to_mongo()
    users_collection = db["usersCloud"]
>>>>>>> f737360a044f626bb28e95c81edfff25f4edeeb5
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    
<<<<<<< HEAD
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
=======
    if st.button("Sign Up"):
            # Check if the username already exists in the usersCloud collection
            users_collection = db["usersCloud"]
            existing_user = users_collection.find_one({"username": username})
            if existing_user:
                st.error("Username already exists. Please choose another one.")
            else:
                if password == confirm_password:
                    # Store plain text password directly
                    users_collection.insert_one({"username": username, "password": password})
                    st.success("Account created successfully!")
                    st.session_state.logged_in = True
                    st.session_state.username = username  # Store the username in session state
                    st.session_state.is_signup = True  # To check that user has signed up
                else:
                    st.error("Passwords do not match!")

# Login function without bcrypt (verifying plain text passwords)
def login():
    db = connect_to_mongo()
    users_collection = db["usersCloud"]
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        user = users_collection.find_one({"username": username})
        
        if user is None:
            st.error("No user found with that username.")
        elif password == user["password"]:
            st.success("Login successful!")
            st.session_state.logged_in = True
            st.session_state.username = username  # Store the username in session state
            st.session_state.is_signup = False  # To check that user is logging in, not signing up
        else:
            st.error("Incorrect password.")
            
# Page to prompt user to log in or sign up
def user_account_page():
    st.title("Login / Sign Up")
    
    # Check if user is logged in
    if 'logged_in' in st.session_state and st.session_state.logged_in:
        st.success("You are already logged in as: " + st.session_state.username)
        return  # User is already logged in, return early

    # Show options to login or sign up
    option = st.radio("Choose an option", ("Login", "Sign Up"))
    if option == "Login":
        login()
    elif option == "Sign Up":
        signup()
 
def get_games_by_search(search_query):
    db = connect_to_mongo()
    if db is not None:  # Check if the connection is valid
        games_collection = db["games"]  # Replace with your actual collection name
        query = {}

        if search_query:
            query["Title"] = {"$regex": search_query, "$options": "i"}  # Case-insensitive search

        games = games_collection.find(query)
        return list(games)
>>>>>>> f737360a044f626bb28e95c81edfff25f4edeeb5
    else:
        return []

<<<<<<< HEAD
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
=======
# Query games from MongoDB based on platform filter
def get_games_by_platform(platform_filter):
    db = connect_to_mongo()
    if db is not None:  # Check if the connection is valid
        games_collection = db["games"]  # Replace with your actual collection name
        query = {}

        if platform_filter:
            query["Platforms"] = {"$in": platform_filter}

        games = games_collection.find(query)
        return list(games)
    else:
        return []

# Display a game card
def display_game_card(game):
    st.subheader(game["Title"])
    st.write(f"Release Date: {game['Release_Date']}")
    st.write(f"Rating: {game['Rating']}")
    st.write(f"Genres: {', '.join(game['Genres'])}")
    st.write(f"Platforms: {', '.join(game['Platforms'])}")
    st.write(f"Summary: {game['Summary'][:150]}...")  # Truncate summary for preview
    if st.button(f"View details for {game['Title']}"):
        show_game_details(game)

# Show detailed game information
def show_game_details(game):
    st.header(game["Title"])
    st.write(f"Release Date: {game['Release_Date']}")
    st.write(f"Rating: {game['Rating']}")
    st.write(f"Genres: {', '.join(game['Genres'])}")
    st.write(f"Platforms: {', '.join(game['Platforms'])}")
    st.write(f"Summary: {game['Summary']}")

# Game database page with search bar and platform filter
def game_database_page():
    # Search bar
    search_query = st.text_input("Search for games by title")

    # Platform filter
    platform_filter = st.multiselect(
        "Select Platforms",
        options=["Windows PC", "PlayStation 4", "Xbox One", "PlayStation 5", "Xbox Series"],
        default=[]
    )

    # Get the filtered games based on search query
    if search_query:
        games_by_search = get_games_by_search(search_query)
    else:
        games_by_search = []

    # Get the filtered games based on platform filter
    if platform_filter:
        games_by_platform = get_games_by_platform(platform_filter)
    else:
        games_by_platform = []

    # Combine the results from both filters (if any)
    # If both search and platform filters are applied, we'll intersect the two lists
    if search_query and platform_filter:
        filtered_games = [game for game in games_by_search if game in games_by_platform]
    elif search_query:
        filtered_games = games_by_search
    elif platform_filter:
        filtered_games = games_by_platform
    else:
        filtered_games = []  # No filters applied

    # Display the games
    for game in filtered_games:
        display_game_card(game)

# Assuming that a user's wishlist is stored as a list in MongoDB, we fetch it like this:

def add_to_wishlist(game_title):
    if not st.session_state.get('logged_in', False):
        st.error("Please log in to add games to your wishlist.")
        return
    
    db = connect_to_mongo()  # Connect to MongoDB
    if db is None:
        st.error("Could not connect to the database.")
        return
    
    users_collection = db["usersCloud"]
    username = st.session_state.username  # Get logged-in user’s username
    
    # Find the user document
    user = users_collection.find_one({"username": username})
    
    if user:
        wishlist = user.get("wishlist", [])
        
        # Check if the game is already in the wishlist
        if game_title not in [game["Title"] for game in wishlist]:
            wishlist.append({"Title": game_title})
            users_collection.update_one({"username": username}, {"$set": {"wishlist": wishlist}})
            st.success(f"{game_title} added to your wishlist!")
        else:
            st.warning(f"{game_title} is already in your wishlist.")
    else:
        st.error("User data not found.")

def remove_from_wishlist(game_title):
    if not st.session_state.get('logged_in', False):
        st.error("Please log in to remove games from your wishlist.")
        return
    
    db = connect_to_mongo()  # Connect to MongoDB
    if db is None:
        st.error("Could not connect to the database.")
        return
    
    users_collection = db["usersCloud"]
    username = st.session_state.username  # Get logged-in user’s username
    
    # Find the user document
    user = users_collection.find_one({"username": username})
    
    if user:
        wishlist = user.get("wishlist", [])
        
        # Remove the game from the wishlist
        updated_wishlist = [game for game in wishlist if game["Title"] != game_title]
        
        if len(updated_wishlist) < len(wishlist):
            users_collection.update_one({"username": username}, {"$set": {"wishlist": updated_wishlist}})
            st.success(f"{game_title} removed from your wishlist!")
        else:
            st.warning(f"{game_title} not found in your wishlist.")
    else:
        st.error("User data not found.")

def wishlist_page():
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        st.error("You need to log in to access your wishlist.")
        user_account_page()  # Show login/signup page
        return  # Exit the function if the user is not logged in
    
    db = connect_to_mongo()
    
    if db is None:
        st.error("Could not connect to the database.")
        return
    
    users_collection = db["usersCloud"]
    username = st.session_state.username
    
    user = users_collection.find_one({"username": username})
    
    if user:
        wishlist = user.get("wishlist", [])
        st.write("Your Wishlist:")
        
        for game in wishlist:
            st.write(game["Title"])
            if st.button(f"Remove {game['Title']} from Wishlist"):
                remove_from_wishlist(game["Title"])
        
        # Optionally, allow users to add games to wishlist
        game_title_to_add = st.text_input("Enter game title to add to your wishlist")
        if st.button("Add to Wishlist") and game_title_to_add:
            add_to_wishlist(game_title_to_add)
    else:
        st.error("User data not found.")
        
def main():
    st.title("Game Database")
    st.subheader("Make A Wish 💫")
    
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        user_account_page()  # Show login/signup page if not logged in
    else:
        option = st.sidebar.selectbox("Select Page", ("Game Database", "Wishlist"))
        
        if option == "Game Database":
            game_database_page()
        elif option == "Wishlist":
            wishlist_page()

if __name__ == "__main__":
    main()
>>>>>>> f737360a044f626bb28e95c81edfff25f4edeeb5

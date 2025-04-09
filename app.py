from pymongo import MongoClient
import streamlit as st
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

def transform_data(data):
    """
    Transforms string representations of lists in the dataset into actual Python lists.
    """
    if isinstance(data, str):  # Check if the data is a string
        try:
            # Safely evaluate the string to get the actual list
            return ast.literal_eval(data)
        except (ValueError, SyntaxError):
            # If the string is not a valid list format, return the original data
            return data
    return data  # Return data as is if it's not a string

# Apply transformation to each field
def transform_game_fields(games):
    """
    Transforms the 'Platforms' and 'Genres' fields for each game.
    """
    for game in games:
        if "Platforms" in game:
            game["Platforms"] = transform_data(game["Platforms"])
        if "Genres" in game:
            game["Genres"] = transform_data(game["Genres"])
    return games

# Signup function
def signup():
    db = connect_to_mongo()
    users_collection = db["usersCloud"]
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    
    if st.button("Sign Up"):
        existing_user = users_collection.find_one({"username": username})
        if existing_user:
            st.error("Username already exists. Please choose another one.")
        else:
            if password == confirm_password:
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
        games_collection = db["games"]
        query = {}

        if search_query:
            query["Title"] = {"$regex": search_query, "$options": "i"}  # Case-insensitive search

        games = games_collection.find(query)
        return list(games)
    else:
        return []

# Query games from MongoDB based on platform filter
def get_games_by_platform(platform_filter):
    db = connect_to_mongo()
    if db is not None:  # Check if the connection is valid
        games_collection = db["games"]
        query = {}

        if platform_filter:
            query["Platforms"] = {"$in": platform_filter}

        games = games_collection.find(query)
        return list(games)
    else:
        return []

def display_game_card(game):
    st.subheader(game["Title"])
    st.write(f"Release Date: {game['Release_Date']}")
    st.write(f"Rating: {game['Rating']}")
    
    genres = ", ".join(game["Genres"]) if "Genres" in game else "N/A"
    platforms = ", ".join(game["Platforms"]) if "Platforms" in game else "N/A"

    st.write(f"Genres: {genres}")
    st.write(f"Platforms: {platforms}")
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
    if search_query and platform_filter:
        filtered_games = [game for game in games_by_search if game in games_by_platform]
    elif search_query:
        filtered_games = games_by_search
    elif platform_filter:
        filtered_games = games_by_platform
    else:
        filtered_games = []  # No filters applied

    # Transform and display the games
    filtered_games = transform_game_fields(filtered_games)
    for game in filtered_games:
        display_game_card(game)

def main():
    game_database_page()

if __name__ == "__main__":
    main()

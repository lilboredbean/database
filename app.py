from pymongo import MongoClient
import streamlit as st
import ast

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
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    
    if st.button("Sign Up"):
        db = connect_to_mongo()
        if db:
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
 
# Query games from MongoDB based on filters or search
def get_filtered_games(search_query, platform_filter, genre_filter, rating_filter):
    db = connect_to_mongo()
    if db:
        games_collection = db["games"]  # Replace with your actual collection name
        query = {}
        
        if search_query:
            query["Title"] = {"$regex": search_query, "$options": "i"}  # Case-insensitive search
        
        if platform_filter:
            query["Platforms"] = {"$in": platform_filter}
        
        if genre_filter:
            query["Genres"] = {"$in": genre_filter}
        
        if rating_filter:
            query["Rating"] = {"$gte": rating_filter}

        games = games_collection.find(query)
        return list(games)
    return []

# Display a game card
def display_game_card(game):
    st.subheader(game["Title"])
    st.write(f"Release Date: {game['Release_Date']}")
    st.write(f"Rating: {game['Rating']}")
    
    # Display an image if available (replace with actual image URL if needed)
    if "Image_URL" in game and game["Image_URL"]:
        try:
            img = Image.open(game["Image_URL"])
            st.image(img, width=200)
        except:
            st.write("No image available.")
    
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
    
    # Optional: Add a trailer or more media
    if "Trailer_URL" in game and game["Trailer_URL"]:
        st.video(game["Trailer_URL"])

# Game database page with filters and search bar
def game_database_page():
    # Search bar
    search_query = st.text_input("Search for games by title")

    # Filters for platform, genre, and rating
    platform_filter = st.multiselect(
        "Select Platforms",
        options=["Windows PC", "PlayStation 4", "Xbox One", "PlayStation 5", "Xbox Series"],
        default=[]
    )
    
    genre_filter = st.multiselect(
        "Select Genres",
        options=["Adventure", "RPG", "Action", "Strategy", "Shooter"],
        default=[]
    )
    
    rating_filter = st.slider(
        "Select Minimum Rating",
        min_value=1,
        max_value=5,
        value=1  # Default to 1 to show all ratings
    )

    # Get the filtered games (or all if no filters are applied)
    games = get_filtered_games(search_query, platform_filter, genre_filter, rating_filter)

    # Display the game cards
    if games:
        for game in games:
            display_game_card(game)
    else:
        st.write("No games found with the selected filters or search query.")

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

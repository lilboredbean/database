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
 
def get_games(filters):
    db = connect_to_mongo()
    if db is None:
        st.error("Could not connect to the database.")
        return []
    
    games_collection = db["games"]
    query = {}

    # Add filters based on user input
    if filters.get("platform"):
        query["Platforms"] = {"$in": filters["platform"]}
    elif filters.get("genre"):
        query["Genres"] = {"$in": filters["genre"]}
    elif filters.get("rating"):
        query["Rating"] = {"$gte": filters["rating"]}
    elif filters.get("search_query"):
        query["Title"] = {"$regex": filters["search_query"], "$options": "i"}  # Case-insensitive search

    # Fetch games from the database based on the filters
    games = games_collection.find(query)
    return list(games)
    
def display_game_cards(games):
    for game in games:
        title = game.get('Title')
        release_date = game.get('Release_Date')
        rating = game.get('Rating')
        
        st.subheader(title)
        st.write(f"Release Date: {release_date}")
        st.write(f"Rating: {rating}")
        st.button('View Details', key=title, on_click=show_game_details, args=(game,))

def show_game_details(game):
    """Show more details of the game on button click"""
    st.subheader(game.get('Title'))
    st.write(f"**Release Date**: {game.get('Release_Date')}")
    st.write(f"**Developers**: {ast.literal_eval(game.get('Developers'))}")
    st.write(f"**Summary**: {game.get('Summary')}")
    st.write(f"**Platforms**: {ast.literal_eval(game.get('Platforms'))}")
    st.write(f"**Genres**: {ast.literal_eval(game.get('Genres'))}")
    st.write(f"**Rating**: {game.get('Rating')}")
    st.write(f"**Plays**: {game.get('Plays')}")
    st.write(f"**Reviews**: {game.get('Reviews')}")

def game_database_page():

    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        st.error("You need to log in to access the game database.")
        user_account_page()  # Show login/signup page
        return  # Exit the function if the user is not logged in
        
    st.title("Game Database")

    # Search and filter functionality
    search_query = st.text_input("Search for a game by title:")
    platforms = st.multiselect("Filter by Platform", ['PC', 'PlayStation', 'Xbox'])
    genres = st.multiselect("Filter by Genre", ['Action', 'RPG', 'Adventure', 'Strategy'])
    rating = st.slider("Filter by Rating", 0.0, 5.0, 4.0, 0.1)

    filters = {
        'platforms': platforms,
        'genres': genres,
        'rating': rating
    }

    # Fetch games based on filters
    games = get_games(filters) if search_query == "" else get_games(filters)  # Apply search query if any
    display_game_cards(games)

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

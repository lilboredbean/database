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

# Sign up function
def signup():
    db = connect_to_mongo()  # Make sure this function returns a valid db object or None
    
    if db is None:
        st.error("Could not connect to the database.")
        return
    
    # Assume you have a users collection
    users_collection = db["usersCloud"]
    
    # Logic for signing up a user (e.g., checking if user exists and adding to DB)
    st.title("Create an Account")
    username = st.text_input("Enter your username")
    password = st.text_input("Enter your password", type="password")
    
    if st.button("Sign Up"):
        if username and password:
            existing_user = users_collection.find_one({"username": username})
            if existing_user:
                st.error("Username already taken.")
            else:
                users_collection.insert_one({
                    "username": username,
                    "password": password
                })
                st.success("Sign up successful!")
        else:
            st.error("Please provide both username and password.")


# Login function
def login():
    db = connect_to_mongo()  # Make sure this function returns a valid db object or None
    
    if db is None:
        st.error("Could not connect to the database.")
        return
    
    # Assume the users are stored in the "usersCloud" collection
    users_collection = db["usersCloud"]
    
    # Collect login credentials from the user
    st.title("Login")
    username = st.text_input("Enter your username")
    password = st.text_input("Enter your password", type="password")
    
    if st.button("Login"):
        if username and password:
            # Check if the user exists in the database
            user = users_collection.find_one({"username": username})
            if user:
                # Here, you would typically verify the password (e.g., by hashing it and comparing)
                if user["password"] == password:
                    st.success("Login successful!")
                    # Proceed to the next page, like the game database page
                    # e.g., st.session_state.logged_in = True
                    # Redirect to the main page
                    # Alternatively, you could store the username in session state
                else:
                    st.error("Invalid password.")
            else:
                st.error("User not found.")
        else:
            st.error("Please provide both username and password.")

# Page to prompt user to log in or sign up
def user_account_page():
    st.title("Login")
    
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
    st.subtitle("Make A Wish 💫")
    
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

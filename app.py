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

# Sign up function
def signup():
    db = connect_to_mongo()  # Make sure this function returns a valid db object or None
    
    if db is None:
        st.error("Could not connect to the database.")
        return
    
    # Assume you have a users collection
    users_collection = db["usersCloud"]
    
    # Logic for signing up a user (e.g., checking if user exists and adding to DB)
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
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')

    if st.button("Login"):
        db = connect_to_mongo()
        if db:
            # Fetch user data from usersCloud collection
            users_collection = db["usersCloud"]
            user = users_collection.find_one({"username": username})

            if user:
                # Compare hashed password
                if user["password"] == hash_password(password):
                    st.success("Login successful!")
                    return username
                else:
                    st.error("Incorrect password.")
            else:
                st.error("User not found.")
    return None

# Get the user's wishlist from the database
def get_user_wishlist(username):
    db = connect_to_mongo()
    if db:
        wishlist_collection = db["wishlist"]
        user_wishlist = wishlist_collection.find_one({"username": username})
        if user_wishlist:
            return user_wishlist.get('games', [])
    return []

# Update the user's wishlist (add/remove games)
def update_wishlist(username, game_id, action):
    db = connect_to_mongo()
    if db:
        wishlist_collection = db["wishlist"]
        if action == 'add':
            wishlist_collection.update_one(
                {"username": username},
                {"$push": {"games": game_id}},
                upsert=True
            )
        elif action == 'remove':
            wishlist_collection.update_one(
                {"username": username},
                {"$pull": {"games": game_id}}
            )

def user_account_page():
    # User account login or signup
    page = st.radio("Choose page", ["Login", "Sign Up"])
    
    if page == "Login":
        username = login()
        if username:
            st.write(f"Welcome, {username}!")
            wishlist_page(username)  # Pass the username to wishlist page

    elif page == "Sign Up":
        signup()

def wishlist_page(username):
    st.title(f"{username}'s Wishlist")

    # Fetch user wishlist from the database
    wishlist = get_user_wishlist(username)
    
    if wishlist:
        for game_id in wishlist:
            game = get_games(filters={'game_id': game_id})[0]  # Fetch game by ID from the database
            st.subheader(game.get('Title'))
            st.button('Remove from Wishlist', key=game_id, on_click=update_wishlist, args=(username, game_id, 'remove'))
    else:
        st.write("Your wishlist is empty!")

    # Add a button to add more games from the database
    st.write("Add more games to your wishlist")
    game_id_to_add = st.text_input("Enter Game ID to add to Wishlist:")
    if like_button == st.button(f"❤️ Like {game_title}", key=str(index)):
    #"Like" button (Add to wishlist)
        update_wishlist(username, game_id_to_add, 'add')
        st.success(f"Game {game_id_to_add} added to wishlist.")

def main():
    page = st.sidebar.selectbox("Choose a page", ["Game Database", "Wishlist", "User Account"])
    
    if page == "Game Database":
        game_database_page()  # Show the game database page
    elif page == "Wishlist":
        username = st.session_state.get('username')
        if username:
            wishlist_page(username)  # Show wishlist page for the logged-in user
        else:
            st.write("Please log in to see your wishlist.")
    elif page == "User Account":
        user_account_page()  # Show login/signup page

if __name__ == "__main__":
    main()

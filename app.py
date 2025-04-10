from pymongo import MongoClient
import streamlit as st
import ast
import requests
import pandas as pd
import plotly.express as px

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
    else:
        return []

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

def eda_page():
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        st.error("You need to log in to access your wishlist.")
        user_account_page()  # Show login/signup page
        return  # Exit the function if the user is not logged in
    
    db = connect_to_mongo()
    
    if db is None:
        st.error("Could not connect to the database.")
        return
    
    games_collection = db["games"]
    games = list(games_collection.find())
    
    if not games:
        st.warning("No game data available.")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(games)

    # ⭐ Chart 1: Rating Distribution
    st.subheader("⭐ Rating Distribution")
    fig1 = px.histogram(df, x="Rating", nbins=20, title="Game Ratings", color_discrete_sequence=["#00cc96"])
    st.plotly_chart(fig1, use_container_width=True)

    # 📅 Chart 2: Releases Over Time
    st.subheader("📆 Number of Game Releases Over Time")
    df_by_year = df.dropna(subset=["Release_Date"])
    df_by_year["Year"] = df_by_year["Release_Date"].dt.year
    releases_per_year = df_by_year["Year"].value_counts().sort_index().reset_index()
    releases_per_year.columns = ["Year", "Number of Releases"]
    fig2 = px.line(releases_per_year, x="Year", y="Number of Releases", markers=True)
    st.plotly_chart(fig2)

    # 🧱 Chart 3: Most Reviewed Games
    st.subheader("🗣️ Most Reviewed Games")
    top_reviewed = df.sort_values(by="Reviews", ascending=False).head(10)
    fig3 = px.bar(top_reviewed, x="Title", y="Reviews", title="Top 10 Most Reviewed Games", color="Reviews", color_continuous_scale="Blues")
    st.plotly_chart(fig3, use_container_width=True)

    # 🎯 Chart 4: Plays vs Rating Scatter
    st.subheader("🎯 Plays vs. Rating")
    fig4 = px.scatter(df, x="Rating", y="Plays", hover_name="Title", color="Rating", size="Plays",
                      title="Plays vs. Rating", color_continuous_scale="Viridis")
    st.plotly_chart(fig4, use_container_width=True)

    # 🌡️ Chart 5: Heatmap - Avg Reviews per Year
    st.subheader("🌡️ Heatmap: Average Reviews by Year")
    
    # Convert Release_Date to datetime, if not already done
    df["Release_Date"] = pd.to_datetime(df["Release_Date"], errors="coerce")
    
    # Remove rows with invalid or missing Release_Date
    df = df.dropna(subset=["Release_Date"])
    
    # Extract the Year from Release_Date
    df["Year"] = df["Release_Date"].dt.year
    
    # Check if 'Year' column exists and is populated
    if "Year" not in df.columns or df["Year"].isna().sum() > 0:
        st.error("Error: Year column is missing or contains invalid data.")
        return
    
    # Group by Year and calculate average Reviews
    df_reviews_per_year = df.groupby("Year")["Reviews"].mean().reset_index()
    
    # Ensure the data is valid and not empty
    if df_reviews_per_year.empty:
        st.error("Error: Could not group data by year.")
        return
    
    # Round the reviews for clearer visualization in the heatmap
    df_reviews_per_year["Reviews"] = df_reviews_per_year["Reviews"].round(0)
    
    # Create the heatmap using plotly
    fig5 = px.density_heatmap(
        df_reviews_per_year,
        x="Year", 
        y="Reviews", 
        nbinsx=20, 
        title="Average Reviews Heatmap by Year",
        color_continuous_scale="Reds"
    )
    
    st.plotly_chart(fig5, use_container_width=True)


    # 🤯 Fun Facts
    st.subheader("💡 Fun Facts")

    highest_rated = df[df["Rating"] == df["Rating"].max()].iloc[0]
    most_reviewed = df[df["Reviews"] == df["Reviews"].max()].iloc[0]
    most_played = df[df["Plays"] == df["Plays"].max()].iloc[0]

    st.markdown(f"""
    - 🏆 **Highest Rated Game**: `{highest_rated['Title']}` with a rating of **{highest_rated['Rating']}**
    - 🗣️ **Most Reviewed Game**: `{most_reviewed['Title']}` with **{most_reviewed['Reviews']} reviews**
    - 🎮 **Most Played Game**: `{most_played['Title']}` with **{most_played['Plays']} plays**
    """)
    
def main():
    st.title("Game Database")
    st.subheader("Make A Wish 💫")
    
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        user_account_page()  # Show login/signup page if not logged in
    else:
        option = st.sidebar.selectbox("Select Page", ("🎮 Game Database", "💫 Wishlist", "📊 Game Data Analysis"))
        
        if option == "🎮 Game Database":
            game_database_page()
        elif option == "💫 Wishlist":
            wishlist_page()
        elif option == "📊 Game Data Analysis":
            eda_page()
    if st.session_state.get("logged_in", False):
    st.sidebar.markdown(f"👋 Logged in as `{st.session_state.username}`")
        if st.sidebar.button("🚪 Logout"):
            st.session_state.clear()
            st.experimental_rerun()


if __name__ == "__main__":
    main()

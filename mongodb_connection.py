from pymongo import MongoClient

# Connect to MongoDB Atlas or a local MongoDB instance
client = MongoClient("mongodb://localhost:27017/")  # Replace with your MongoDB URI
db = client['game_database']  # Database name
games_collection = db['games']  # Collection for storing games
users_collection = db['users']  # Collection for storing user data (if using accounts)

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from pymongo import MongoClient
from io import StringIO
from datetime import datetime
import json

@st.cache_resource
def load_data_from_mongo():
    # MongoDB Atlas connection string
    client = MongoClient('mongodb+srv://duck:quack@bubble.ggmhr.mongodb.net/?retryWrites=true&w=majority&appName=Bubble')
    db = client["SteamGamesCloud"]
    games_collection = db["gamesCloud"]

# Load the dataset from MongoDB Atlas
df = load_data_from_mongo()

# Step 2: Data Transformation (Adapted for the new dataset)
# Move Links Column to the end of data
link_column = df['Link']
df = df.drop(columns=['Link'])
df['Link'] = link_column

# Release Dates
def convert_release_date(date_str):
    if pd.isnull(date_str) or date_str in ['Coming Soon', 'To be announced']:
        return date_str
    else:
        try:
            date = datetime.strptime(date_str, '%d %b, %Y')
            if date > datetime(2023, 8, 15):
                return "Unknown"
            else:
                return date.year
        except ValueError:
            try:
                return datetime.strptime(date_str, '%b %Y').year
            except ValueError:
                return date_str

df['Release Date'] = df['Release Date'].apply(convert_release_date)

def convert_to_numeric(value):
    try:
        cleaned_value = value.replace('$', '').replace(',', '').strip().lower()
        if cleaned_value in ['free', '0']:
            return 0
        return float(cleaned_value)
    except:
        return None  

df['Original Price'] = df['Original Price'].apply(convert_to_numeric)
df['Discounted Price'] = df['Discounted Price'].apply(convert_to_numeric)

df.insert(df.columns.get_loc('Discounted Price') + 1, 'Price Difference', df['Original Price'] - df['Discounted Price'])

# Review NaN Handling
df['Recent_or_All_Reviews'] = np.where(
    df['Recent Reviews Number'].notna(),
    df['Recent Reviews Number'],
    df['All Reviews Number']
)

df.insert(df.columns.get_loc('All Reviews Number') + 1, 'Reviews_number', df['Recent_or_All_Reviews'])

df.drop(columns=['Recent_or_All_Reviews'], inplace=True)

df['Reviews_percentage_delete'] = df['Reviews_number'].str.extract(r'(\d+)%')

df.insert(df.columns.get_loc('Reviews_number') + 1, 'Reviews_percentage', df['Reviews_percentage_delete'])
df.drop(columns=['Reviews_percentage_delete'], inplace=True)

df['Extracted_Reviews'] = df['Reviews_number'].str.extract(r'(\d{1,3}(?:,\d{3})*)(?= user reviews)')

df['Extracted_Reviews'] = pd.to_numeric(df['Extracted_Reviews'].str.replace(',', ''), errors='coerce').astype(pd.Int64Dtype())

df['Reviews_number'] = df['Extracted_Reviews']

df.drop(columns=['Extracted_Reviews'], inplace=True)

df.drop(columns=['Recent Reviews Number', 'All Reviews Number'], inplace=True)

df['Supported Languages'] = df['Supported Languages'].str.replace(r"['\[\]]", '').str.replace(r"'", '')
df['Popular Tags'] = df['Popular Tags'].str.replace(r"['\[\]]", '').str.replace(r"'", '')
df['Game Features'] = df['Game Features'].str.replace(r"['\[\]]", '').str.replace(r"'", '')

# Cleaning Requirements
features_to_extract = ['Processor', 'Memory', 'Graphics', 'DirectX', 'Storage']

cleaned_requirements = []
for text in df['Minimum Requirements']:
    if isinstance(text, str):  
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            for feature in features_to_extract:
                if feature in line:
                    value = re.sub(r'^' + feature + r':\s*', '', line)
                    cleaned_lines.append(f"{feature}: {value}")
                    break
        cleaned_text = '\n'.join(cleaned_lines)
        cleaned_requirements.append(cleaned_text)
    else:
        cleaned_requirements.append(text)

cleaned_requirements    

df['Minimum Requirements'] = cleaned_requirements

def process_row(row):
    if isinstance(row, str):
        return re.sub(r'.*\| Processor: \|', 'Processor: |', row, count=1)
    return row

df['Minimum Requirements'] = df['Minimum Requirements'].apply(process_row)
df['Release Date'] = pd.to_numeric(df['Release Date'], errors='coerce')
current_year = 2023  
df['Release Date'] = df['Release Date'].where(df['Release Date'] <= current_year, np.nan)

tags_dict = {
    'Processor': ['Processor:', 'CPU:'],
    'Memory': ['Memory:', 'RAM:'],
    'Graphics': ['Graphics:', 'GPU:', 'Video:'],
    'DirectX': ['DirectX:', 'DX:'],
    'Network': ['Network:', 'Internet:'],
    'Storage': ['Storage:', 'Disk Space:', 'HD space:']
}

def identify_tag(segment):
    for tag, variations in tags_dict.items():
        for variation in variations:
            if variation in segment:
                return tag
    return None

for index, row in df.iterrows():
    segments = [seg.strip() for seg in str(row['Minimum Requirements']).split('|') if seg.strip()]

    for i, segment in enumerate(segments):
        tag = identify_tag(segment)
        if tag and i+1 < len(segments):
            df.at[index, tag] = segments[i+1]

df[['Processor', 'Memory', 'Graphics', 'DirectX', 'Network', 'Storage']] = df[['Processor', 'Memory', 'Graphics', 'DirectX', 'Network', 'Storage']].fillna('N/A')

unique_processor = df['Processor'].unique()
unique_memory = df['Memory'].unique()
unique_graphics = df['Graphics'].unique()
unique_directx = df['DirectX'].unique()
unique_storage = df['Storage'].unique()

def extract_processor(s):
    s = s.lower()
    if 'intel' in s and 'i5' in s:
        return 'Intel i5'
    elif 'amd' in s and 'fx' in s:
        return 'AMD FX'
    elif 'ryzen' in s:
        return 'Ryzen'
    else:
        return 'Unknown'

df['Processor'] = df['Processor'].apply(extract_processor)

def extract_memory(s):
    if pd.isna(s):  
        return s

    match = re.search(r'(\d+(\.\d+)?)([ \t]*[MG]B)', str(s), re.IGNORECASE)  
    
    if match:
        value = float(match.group(1))
        unit = match.group(3).strip().lower()

        if unit == 'mb':
            value /= 1024.0
        
        return value  
    
    return None

df['Memory'] = df['Memory'].apply(extract_memory)

def extract_specifications(text):
    
    specs = {
        'Processor': 'Unknown',
        
        'Graphics': 'Unknown',
        'DirectX': 'Unknown',
        'Storage': 'Unknown',
    }

    patterns = {
        'Processor': [r'Processor: \| ([\w\s®™\-]+[iI][3,5,7,9]|\bIntel Core2 Duo\b|[\w\s®™\-]+[A-Z][\d\-]+)', r'Processor: \| ([\w\s®™\-]+)'],  
        
        'Graphics': [r'Graphics: \| ([\w\s®™\-]+[Gg][Tt][Xx]|\bDirectX\b)', r'Graphics: \| ([\w\s®™\-]+)'],  
        'DirectX': [r'DirectX: \| ([\w\s®™\-]+)'],
        'Storage': [r'Storage: \| (\d+ [Gg][Bb])']
    }
    
    for spec, pattern_list in patterns.items():
        for pattern in pattern_list:
            match = re.search(pattern, text)
            if match:
                specs[spec] = match.group(1)
                break  

    return specs

text1 = 'Processor: | Intel Core2 Duo or better | Memory: | 4 GB RAM | Graphics: | DirectX 9/OpenGL 4.1 capable GPU | DirectX: | Version 9.0 | Storage: | 4 GB available space | Additional Notes: | 1280x768 or better Display. Lag may occur from loading menus or maps. Turn off other programs before running the game.'
text2 = 'Processor: | TBD | Graphics: | TBD'

def extract_specifications_for_unknowns(row):
    extracted_specs = {}
    
    patterns = {
        'Processor': r'Processor: \|\s*(.+?)\s*\|',
        
        'Graphics': r'Graphics: \|\s*(.+?)\s*\|',
        'DirectX': r'DirectX: \|\s*(.+?)\s*\|',
        'Storage': r'Storage: \|\s*(.+?)\s*\|',
        'Network': r'Network: \|\s*(.+?)\s*\|'
    }

    for spec, pattern in patterns.items():
        if row[spec] == "Unknown" and isinstance(row['Minimum Requirements'], str):
            match = re.search(pattern, row['Minimum Requirements'])
            if match:
                extracted_specs[spec] = match.group(1).strip()
            else:
                extracted_specs[spec] = "Unknown"
        else:
            extracted_specs[spec] = row[spec]

    return pd.Series(extracted_specs)

df[['Processor',  'Graphics', 'DirectX', 'Storage', 'Network']] = df.apply(extract_specifications_for_unknowns, axis=1)

def clean_processor_name(name):
    name = re.sub(r'[®™]', '', name)

    if 'Intel Core2 Duo or better' in name:
        return 'Intel Core2 Duo'
    elif 'Intel Core 2 Duo E6600 or AMD Phenom X3 8750' in name:
        return 'Intel Core2 Duo'
    else:
        return name

df['Processor'] = df['Processor'].apply(clean_processor_name)
df = df.drop(columns=['Network'])

cols_to_check = ['Processor', 'Memory', 'Graphics', 'DirectX', 'Storage']

for col in cols_to_check:
    df[col] = df[col].replace('TBD', 'N/A')
    df[col] = df[col].replace('Unknown', 'N/A')

na_rows = df[cols_to_check].apply(lambda x: 'N/A' in x.values, axis=1)
nan_release_date = df['Release Date'].isna()

games_with_na_in_target_and_nan_release = (na_rows & nan_release_date).sum()

df.replace('N/A', np.nan, inplace=True)

# Handle Summaries
df['Reviews Summary'] = df['Recent Reviews Summary'].fillna(df['All Reviews Summary'])

df.insert(df.columns.get_loc('All Reviews Summary') + 1, 'Reviews Summary', df.pop('Reviews Summary'))
df.drop(columns=['All Reviews Summary', 'Recent Reviews Summary'], inplace=True)

values_to_count = df[df['Reviews Summary'].isna() & df['Release Date'].isna()]
first_quartile_threshold = df['Reviews_number'].quantile(0.25)

def impute_reviews(row):
    summary = row['Reviews Summary']
    num_reviews = row['Reviews_number']
    
    if pd.isna(summary):
        return row
    
    if re.search(r'\d+ user reviews', str(summary)):
        row['Reviews Summary'] = np.nan
        row['Reviews_percentage'] = np.nan
        return row
    
    if pd.isna(row['Reviews_percentage']):
        if summary == 'Overwhelmingly Positive':
            row['Reviews_percentage'] = 97
        elif summary == 'Very Positive':
            row['Reviews_percentage'] = 87
        elif summary == 'Positive':
            row['Reviews_percentage'] = 89.5 if num_reviews > first_quartile_threshold else 87
        elif summary == 'Mostly Positive':
            row['Reviews_percentage'] = 74.5
        elif summary == 'Mixed':
            row['Reviews_percentage'] = 54.5
        elif summary == 'Mostly Negative':
            row['Reviews_percentage'] = 29.5
        elif summary == 'Negative':
            row['Reviews_percentage'] = 19.5 if num_reviews > first_quartile_threshold else 29.5
        elif summary == 'Very Negative':
            row['Reviews_percentage'] = 9.5
        elif summary == 'Overwhelmingly Negative':
            row['Reviews_percentage'] = 9.5
    return row

df = df.apply(impute_reviews, axis=1)

complete_rows = df.dropna().shape[0]
df.dropna(subset=['Title'], inplace=True)

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

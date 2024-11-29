import pandas as pd

# Load the data
books = pd.read_excel('BX-Books.xlsx')
ratings = pd.read_csv('BX-Book-Ratings.csv', sep=';', encoding='latin-1', on_bad_lines='skip')

# Preprocess books
books = books[['ISBN', 'Book-Title', 'Book-Author', 'Image-URL-S']]
books.columns = ['isbn', 'title', 'author', 'image_url']

# Preprocess ratings
ratings = ratings[['User-ID', 'ISBN', 'Book-Rating']]
ratings.columns = ['user_id', 'isbn', 'rating']

# Merge books with ratings
book_ratings = ratings.merge(books, on='isbn')

# Function to recommend books based on minimum rating
def recommend_books_by_rating(min_rating):
    # Filter books with an average rating >= min_rating
    avg_ratings = book_ratings.groupby('title').agg({'rating': 'mean', 'image_url': 'first', 'author': 'first'})
    filtered_books = avg_ratings[avg_ratings['rating'] == min_rating]
    sorted_books = filtered_books.sort_values('rating', ascending=False).reset_index()

    # Return the top books as a dictionary
    recommended_books = sorted_books[['title', 'author', 'rating', 'image_url']].to_dict(orient='records')
    return recommended_books

import pickle
import streamlit as st
import numpy as np

# Load necessary data
model = pickle.load(open('artifacts/model.pkl', 'rb'))
book_names = pickle.load(open('artifacts/book_names.pkl', 'rb'))
final_rating = pickle.load(open('artifacts/final_rating.pkl', 'rb'))
book_pivot = pickle.load(open('artifacts/book_pivot.pkl', 'rb'))

# Import additional backend functions
from backend import get_books_by_author, get_all_authors
from backend1 import recommend_books_by_rating

# Helper Function to Fetch Book Cover Images
def fetch_poster(suggestion):
    book_name = []
    ids_index = []
    poster_url = []

    for book_id in suggestion:
        book_name.append(book_pivot.index[book_id])

    for name in book_name[0]:
        ids = np.where(final_rating['title'] == name)[0][0]
        ids_index.append(ids)

    for idx in ids_index:
        url = final_rating.iloc[idx]['image_url']
        poster_url.append(url)

    return poster_url

# Recommendation Based on a Selected Book
def recommend_books(book_name):
    book_list = []
    book_id = np.where(book_pivot.index == book_name)[0][0]
    distance, suggestion = model.kneighbors(
        book_pivot.iloc[book_id, :].values.reshape(1, -1), n_neighbors=6
    )

    poster_url = fetch_poster(suggestion)

    for i in range(len(suggestion)):
        books = book_pivot.index[suggestion[i]]
        for j in books:
            book_list.append(j)

    return book_list, poster_url


# Main application
st.title("Book Recommendation System")

# Add three buttons
selected_option = st.radio(
    "Choose a recommendation method",
    options=["Based on Previous Book", "Based on Author", "Based on Rating"],
    key="recommendation_option"
)
# Case 1: Recommendation Based on a Book
if selected_option == "Based on Previous Book":
    st.header("Recommendation Based on a Book")
    selected_books = st.selectbox("Type or select a book", book_names)

    if st.button("Show Recommendation", key="previous_book_button"):
        recommendation_books, poster_url = recommend_books(selected_books)

        # Exclude the selected book and limit to 5 recommendations
        filtered_books = [
            (title, poster)
            for title, poster in zip(recommendation_books, poster_url)
            if title != selected_books
        ][:5]

        if not filtered_books:
            st.warning("No recommendations available for the selected book.")
        else:
            cols_per_row = 5  # Number of columns per row
            num_books = len(filtered_books)
            rows = (num_books // cols_per_row) + (num_books % cols_per_row > 0)

            for row in range(rows):
                cols = st.columns(cols_per_row)
                for col_idx, book_idx in enumerate(range(row * cols_per_row, (row + 1) * cols_per_row)):
                    if book_idx < num_books:
                        book_title, book_poster = filtered_books[book_idx]
                        with cols[col_idx]:
                            st.image(book_poster, use_container_width=True)
                            st.text(book_title)
# Case 2: Recommendation Based on Author
elif selected_option == "Based on Author":
    st.header("Recommendation Based on an Author")
    all_authors = get_all_authors()
    selected_author = st.selectbox("Choose an author", all_authors)

    if st.button("Show Books", key="author_button"):
        if selected_author:
            books1 = get_books_by_author(selected_author)
            if books1:
                st.success(f"Books by {selected_author}:")
                for book in books1:
                    st.write(f"- {book}")
            else:
                st.warning("No books found for the selected author.")
        else:
            st.error("Please select an author.")
# Case 3: Recommendation Based on Rating
elif selected_option == "Based on Rating":
    st.header("Recommendation Based on Rating")
    min_rating = st.slider("Select minimum rating", 1, 10, 5, key="rating_slider")

    if st.button("Recommend Books", key="rating_button"):
        recommendations = recommend_books_by_rating(min_rating)

        if recommendations:
            max_recommendations = 5
            recommendations = recommendations[:max_recommendations]

            st.success(f"Showing top {len(recommendations)} books with ratings = {min_rating}:")
            cols_per_row = 5  # Number of columns per row
            num_books = len(recommendations)
            rows = (num_books // cols_per_row) + (num_books % cols_per_row > 0)

            for row in range(rows):
                cols = st.columns(cols_per_row)
                for col_idx, book_idx in enumerate(range(row * cols_per_row, (row + 1) * cols_per_row)):
                    if book_idx < num_books:
                        book = recommendations[book_idx]
                        with cols[col_idx]:
                            st.markdown(
                                f"""
                                <div style="text-align: center;">
                                    <img src="{book['image_url']}" style="width:100%; height:auto; border-radius: 8px; margin-bottom: 10px;" alt="Book Cover">
                                    <p><b>Title:</b> {book['title']}</p>
                                    <p><b>Author:</b> {book['author']}</p>
                                    <p><b>Rating:</b> {book['rating']}</p>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
        else:
            st.warning("No books found for the selected rating.")

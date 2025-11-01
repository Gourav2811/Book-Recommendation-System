from flask import Flask, render_template, request
import pickle
import numpy as np

# Load all pickle files
popular_df = pickle.load(open('popular.pkl', 'rb'))
pt = pickle.load(open('pt.pkl', 'rb'))
books = pickle.load(open('books.pkl', 'rb'))
similarity_scores = pickle.load(open('similarity_scores.pkl', 'rb'))

app = Flask(__name__)

@app.route('/')
def index():
    # Replace missing/broken images with a placeholder
    images = [
        img if str(img).startswith('http')
        else 'https://via.placeholder.com/250x250?text=No+Image'
        for img in popular_df['Image-URL-M'].values
    ]
    return render_template(
        'index.html',
        book_name=list(popular_df['Book-Title'].values),
        author=list(popular_df['Book-Author'].values),
        image=images,
        votes=list(popular_df['num_ratings'].values),
        rating=list(popular_df['avg_rating'].values)
    )

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

@app.route('/recommend_books', methods=['POST'])
def recommend():
    user_input = request.form.get('user_input')

    # Handle case when user_input not found
    if user_input not in pt.index:
        return render_template('recommend.html', data=[], error="Book not found. Please check the name and try again.")

    index = np.where(pt.index == user_input)[0][0]
    similar_items = sorted(
        list(enumerate(similarity_scores[index])),
        key=lambda x: x[1],
        reverse=True
    )[1:9]  # show 8 similar books

    data = []
    for i in similar_items:
        item = []
        temp_df = books[books['Book-Title'] == pt.index[i[0]]].drop_duplicates('Book-Title')

        title = temp_df['Book-Title'].values[0]
        author = temp_df['Book-Author'].values[0]
        img = temp_df['Image-URL-M'].values[0]

        if not str(img).startswith('http'):
            img = 'https://via.placeholder.com/250x250?text=No+Image'

        item.extend([title, author, img])
        data.append(item)

    return render_template('recommend.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)

import sqlite3
import json
import datetime

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

total_connections = 0

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global total_connections
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    total_connections += 1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Funciton to get total posts in the database
def get_post_count():
    connection = get_db_connection()
    post_count = connection.execute('SELECT COUNT(*) AS post_count FROM posts').fetchone()
    connection.close()
    return post_count["post_count"]

def log(message):
    now = datetime.datetime.now()
    print("INFO:app:", now , "," , message)

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      log("A non-existing article has been requested!")
      return render_template('404.html'), 404
    else:
      log("An article with title " + post["title"] + " has been successfully retrieved!")
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    log("AboutUs page has been retrieved!")
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()

            log("A new article with title " + title + " has been successfully created!")

            return redirect(url_for('index'))

    return render_template('create.html')

# Define the health end-point
@app.route('/healthz')
def health():
    return "result: OK - healthy"

# Define the metrics end-point
@app.route('/metrics')
def metrics():
    response = {
        "db_connection_count": total_connections,
        "post_count": get_post_count()
    }
    return json.dumps(response), 200

# start the application on port 3111
if __name__ == "__main__":
   app.run(host='0.0.0.0', port='3111')

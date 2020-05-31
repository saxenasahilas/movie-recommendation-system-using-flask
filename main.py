import numpy as np
import pandas as pd
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# define a function that creates similarity matrix
# if it doesn't exist
def create_sim():
    data = pd.read_csv('data.csv')
    # creating a count matrix
    cv = CountVectorizer()
    count_matrix = cv.fit_transform(data['comb'])
    # creating a similarity score matrix
    sim = cosine_similarity(count_matrix)
    return data,sim


# defining a function that recommends 10 most similar movies
def rcmd(m):
    m = m.lower()
    # check if data and sim are already assigned
    try:
        data.head()
        sim.shape
    except:
        data, sim = create_sim()
    # check if the movie is in our database or not
    if m not in data['movie_title'].unique():
        return('This movie is not in our database.\nPlease check if you spelled it correct.')
    else:
        # getting the index of the movie in the dataframe
        i = data.loc[data['movie_title']==m].index[0]

        # fetching the row containing similarity scores of the movie
        # from similarity matrix and enumerate it
        lst = list(enumerate(sim[i]))

        # sorting this list in decreasing order based on the similarity score
        lst = sorted(lst, key = lambda x:x[1] ,reverse=True)

        # taking top 1- movie scores
        # not taking the first index since it is the same movie
        lst = lst[1:11]

        # making an empty list that will containg all 10 movie recommendations
        l = []
        for i in range(len(lst)):
            a = lst[i][0]
            l.append(data['movie_title'][a])
        return l

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/eda'
db = SQLAlchemy(app)


class Contacts(db.Model):
    '''
    sno, name phone_num, msg, date, email
    '''
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    msg = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    email = db.Column(db.String(20), nullable=False)


class Start(db.Model):
    '''
    sno, name
    '''

    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/start", methods=['GET', 'POST'])
def start():
    if (request.method == 'POST'):
        movie = request.form.get('name')
        r = rcmd(movie)
        movie = movie.upper()
        if type(r) == type('string'):
            return render_template('recommend.html', movie=movie, r=r, t='s')
        else:
            return render_template('recommend.html', movie=movie, r=r, t='l')
        '''if (request.method == 'POST'):
        Add entry to the database'
        name = request.form.get('name')
        entry = Start(name=name)
        db.session.add(entry)
        db.session.commit()
'''
    return render_template('start.html')

@app.route("/about")
def about():
    return render_template('about.html')


@app.route("/contact", methods = ['GET', 'POST'])
def contact():
    if(request.method =='POST'):
        '''Add entry to the database'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = Contacts(name=name, phone_num = phone, msg = message, date= datetime.now(),email = email )
        db.session.add(entry)
        db.session.commit()
    return render_template('contact.html')


app.run(debug=True)
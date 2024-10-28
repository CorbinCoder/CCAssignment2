from flask import Flask, render_template, session, request
import json
import config
import os
import db_client
import s3_client

application = Flask(__name__)

db_client = db_client.DBClient()
s3_client = s3_client.S3Client()

def init():
    db_client.create_tables()
    import_music()

def import_music():
    with open('a2.json') as json_file:
        data = json.load(json_file)
        for i in data['songs']:
            key = {'title': i['title']}
            file_name = i['title'] + '.jpg'
            if not db_client.get_item('music', key):
                print(i)
                item = { 'title': i['title'], 
                        'artist': i['artist'], 
                        'year': i['year'], 
                    'web_url': i['web_url'], 
                    'image_url': i['img_url'] }
                s3_client.upload_file_obj_from_web(i['img_url'], 'music', file_name)
                db_client.put_item('music', item)
                print("Item added successfully")
            else:
                print("Item already exists")

@application.route('/login', methods=['GET', 'POST'])
def login():
    if (request.method == 'POST'):
        email = request.form['email']
        password = request.form['password']
        if (db_client.get_item('login', { 'email': email })):
            if (db_client.get_item('login', { 'email': email })['password'] == password):
                    session['email'] = email
                    print("Session email: " + session['email'])
                    return render_template('home.html', user_name=db_client.get_item("login", { 'email': email })['user_name'],
                                        subscribed = db_client.query("subscribed",  'email', email))
            else:
                return render_template('login.html', message='Invalid Credentials. Please try again.')
        else:
            return render_template('login.html', message='Invalid Email. Please try again.')
    return render_template('login.html', message='Something went wrong. Please try again.')

@application.route('/logout')
def logout():
    session.pop('email', None)
    return render_template('index.html', message='You have been logged out successfully.')

@application.route('/register', methods=['GET', 'POST'])
def register():
    if (request.method == 'POST'):
        if (request.form['password'] == request.form['confirm-password']):
            email = request.form['email']
            user_name = request.form['name']
            password = request.form['password']
            if (db_client.get_item("login", { 'email': email })):
                return render_template('register.html', message='Email already exists. Please try again.')
            else:
                db_client.put_item("login", { 'email': email, 'user_name': user_name, 'password': password })
                return render_template('index.html', message='Registration successful. Please login.')
        else:
            return render_template('register.html', message='Passwords do not match. Please try again.')
    return render_template('register.html') 

@application.route('/query', methods=['GET', 'POST'])
def query():
    if (request.method == 'POST'):
        title = request.form['query-title']
        artist = request.form['query-artist']
        year = request.form['query-year']
        print('Session email: ' + session['email'])
        email = session['email']
        print('Email: ' + email)
        results = []
        if (title != ''):
            results.append(db_client.query("music", 'title', title))
        if (artist != ''):
            results.append(db_client.query("music", 'artist', artist))
        if (year != ''):
            results.append(db_client.query("music", 'year', year))
        if (db_client.get_item("music", { 'title': title })):
            return render_template('home.html', user_name=db_client.get_item("login", { 'email': email})['user_name'],
                                   subscribed=db_client.query("subscribed", 'email', email),
                                   results=db_client.query("music", 'title', title))
        else:
            return render_template('home.html', message='Song not found.')

@application.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    if (request.method == 'POST'):
        email = session['email']
        title = request.form['result-title']
        if (db_client.get_item("subscribed", { 'email': email, 'title': title })):
            return render_template('home.html', user_name=db_client.get_item("login", { 'email': email })['user_name'],
                                   subscribed=db_client.query("subscribed", 'email', email),
                                   message='You are already subscribed to this song.')
        else:
            db_client.put_item("subscribed", { 'email': email, 'title': title })
            return render_template('home.html', user_name=db_client.get_item("login", { 'email': email })['user_name'],
                                   subscribed=db_client.query("subscribed", 'email', email),
                                   message='Subscription successful.')
    return render_template('home.html', user_name=db_client.get_item("login", { 'email': email })['user_name'],
                           subscribed=db_client.query("subscribed", 'email', email ))

@application.route('/remove', methods=['GET', 'POST'])
def remove():
    if (request.method == 'POST'):
        email = session['email']
        title = request.form['subscribe-title']
        if (db_client.get_item("subscribed", { 'email': email, 'title': title })):
            db_client.delete_item("subscribed", { 'email': email, 'title': title })
            return render_template('home.html', user_name=db_client.get_item("login", { 'email': email })['user_name'],
                                   subscribed=db_client.query("subscribed", 'email', email),
                                   message='Unsubscription successful.')
        else:
            return render_template('home.html', user_name=db_client.get_item("login", { 'email': email })['user_name'],
                                   subscribed=db_client.query("subscribed", 'email', email ),
                                   message='You are not subscribed to this song.')
    return render_template('home.html', user_name=db_client.get_item("login", { 'email': email })['user_name'],
                           subscribed=db_client.query("subscribed", 'email', email ))

@application.route('/home')
def home():
    if 'email' in session:
        return render_template('home.html')
    else:
        return render_template('index.html', message='Please login to access this page.')

@application.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    application.secret_key = os.urandom(12)
    application.config['SESSION_TYPE'] = 'filesystem'
    init()
    application.run(host='0.0.0.0', port=5000, debug=True)
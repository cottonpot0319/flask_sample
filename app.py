from datetime import datetime
from turtle import title
from flask import Flask
from flask import render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import os

from datetime import datetime
import pytz

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SECRET_KEY'] = os.urandom(24) #暗号化
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

class Post(db.Model):
    #idは勝手に決められる
    id = db.Column(db.Integer, primary_key=True)
    #titleは自分で決める
    title = db.Column(db.String(50), nullable=False)
    #bodyも自分で決める
    body = db.Column(db.String(300), nullable=False)
    #created_atは時間を取ってくる
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(pytz.timezone('Asia/Tokyo')))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    #usernameは自分で決める
    username = db.Column(db.String(30), nullable=False, unique=True)
    #passwordも自分で決める
    password = db.Column(db.String(12))

@login_manager.user_loader #ログインしているか確認する
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/', methods=['GET', 'POST'])
@login_required #ログインしているユーザー以外アクセスできない
def index():
    if request.method == 'GET':
        posts = Post.query.all() #データベースのデータを取ってくる
        return render_template('index.html', posts=posts)

@app.route('/signup', methods=['GET', 'POST']) #POST=フォーム送信用、GET=ページアクセス用
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User(username=username, password=generate_password_hash(password, method='sha256')) #インスタンス化

        db.session.add(user) #データベースに追加
        db.session.commit() #データベースに反映
        return redirect('/login') #ログイン画面へ

    else:
        return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST']) #POST=フォーム送信用、GET=ページアクセス用
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if check_password_hash(user.password, password):
            login_user(user)
            return redirect('/')
        #例外処理もほしい(usernameがない場合)
    else:
        return render_template('login.html')

@app.route('/logout')
@login_required #ログインしているユーザー以外アクセスできない
def logout():
    logout_user()
    return redirect('/login')

@app.route('/create', methods=['GET', 'POST']) #POST=フォーム送信用、GET=ページアクセス用
@login_required #ログインしているユーザー以外アクセスできない
def create():
    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')

        post = Post(title=title, body=body) #インスタンス化

        db.session.add(post) #データベースに追加
        db.session.commit() #データベースに反映
        return redirect('/') #トップページに戻る

    else:
        return render_template('create.html')

@app.route('/<int:id>/update', methods=['GET', 'POST']) #POST=フォーム送信用、GET=ページアクセス用
@login_required #ログインしているユーザー以外アクセスできない
def update(id):
    post = Post.query.get(id)
    if request.method == 'GET':
        return render_template('update.html', post=post)

    else:
        post.title = request.form.get('title')
        post.body = request.form.get('body')

        #post = Post(title=title, body=body) #インスタンス化

        #db.session.add(post) #データベースに追加
        db.session.commit() #データベースに反映
        return redirect('/') #トップページに戻る

@app.route('/<int:id>/delete', methods=['GET']) #POST=フォーム送信用、GET=ページアクセス用
@login_required #ログインしているユーザー以外アクセスできない
def delete(id):
    post = Post.query.get(id)

    db.session.delete(post)
    db.session.commit()
    return redirect('/')
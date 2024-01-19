from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Khwahish21@localhost/temp_ERP'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'secret_key'
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'Users'
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    manager_id = db.Column(db.Integer, nullable=True)
    is_manager = db.Column(db.Boolean, nullable=False, default=False)
    points = db.Column(db.Integer, default=0) 

class Post(db.Model):
    __tablename__ = 'Posts'  
    post_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    points = db.Column(db.Integer, nullable=False, default=0) 
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    user = db.relationship('User', backref='posts')


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html',title='Home')

@app.route("/feed")
def feed():
    data=[{'user_name': 'abhishek', 'manager_name': 'Ram', 'category': 'teamwork', 'post_points': 100, 'content': 'good work keep it up',"time":"02-13-2002"}, {'user_name': 'rahul', 'manager_name': 'Ram', 'category': 'Intigrity', 'post_points': 199, 'content': 'kepp up and do good job',"time":"02-13-2002"}]
    return render_template('feed.html', posts=data, session = session)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username, password=password).first()

        if user:
            session['username'] = username
            session['user_id'] = user.user_id
            session['is_manager'] = user.is_manager
            return redirect(url_for('feed'))
        else:
            return render_template('login.html', message='Invalid credentials. Please try again.')

    return render_template('login.html', title = 'Login', message=None)



@app.route("/register", methods=['GET', 'POST'])
def register():
    return render_template('register.html', title = 'Register')



@app.route("/new_blog", methods=['GET', 'POST'])
def new_blog():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':

        employee_id = request.form.get('employee_id')
        post_content = request.form.get('post_content')
        category = request.form.get('category')
        points = int(request.form.get('points'))

        employee = db.session.get(User, employee_id)
        
        if employee:
            employee.points += points
            db.session.commit()

        new_post = Post(user_id=employee_id, content=post_content, category=category, points=points)
        db.session.add(new_post)
        db.session.commit()

        return redirect(url_for('feed'))

    else:

        manager_id = session['user_id'] 
        employees = User.query.filter_by(manager_id=manager_id).all()

        employee_choices = [(employee.user_id, f"{employee.name} ({employee.user_id})") for employee in employees]
        return render_template('new_blog.html', title = 'New Post', employee_choices=employee_choices)

@app.route("/leaderboard")
def leaderboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    details = User.query.with_entities(User.username, User.points).order_by(User.points.desc()).all()
    return render_template('leaderboard.html', title = 'leaderboard', len = len(details), details = details)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('home'))
    

# @app.route('/redeem')
# def redeem():
#     employee=session['user_id']
#     employee_points = User.query.filter_by(user_id=employee).first()
#     if employee_points:
#         points = employee_points.points
#         return render_template('redeem.html', points=points)


@app.route('/redeem_points', methods=['GET', 'POST'])
def redeem_points():
    employee = session['user_id']
    employee_points = User.query.filter_by(user_id=employee).first()

    if employee_points:
        points = employee_points.points

        if request.method == 'POST':
            success_messages = []
            error_messages = []
            for option in ['zomato', 'amazon', 'boat', 'stationary', 'vacation']:
                enabled_key = f"{option}_enabled"
                points_key = f"{option}_points"

                if request.form.get(enabled_key) == 'on':
                    required_points = int(request.form.get(points_key, 0))

                    if employee_points.points >= required_points:
                        employee_points.points -= required_points
                        db.session.commit()                   
                        success_messages.append(f'Redeemed {option.capitalize()} voucher successfully!, {required_points} points deducted.')
                    else:
                        error_messages.append(f'Insufficient points to redeem {option.capitalize()}.')
            if success_messages:
                        return render_template('redeem_success.html', success_messages=success_messages, points=employee_points.points)
            elif error_messages:
                        return render_template('redeem_success.html', error_messages=error_messages, points=employee_points.points)
        return render_template('redeem.html', points=points)
   
if __name__ == '__main__':
    app.run(debug=True)

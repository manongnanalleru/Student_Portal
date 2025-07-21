from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///student_portal.db'

db = SQLAlchemy(app)


# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(20), default='student')


class Mark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    subject = db.Column(db.String(50), nullable=False)
    marks = db.Column(db.Float, nullable=False)


# Routes
@app.route('/')
def home():
    return redirect('/login')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form.get('role', 'student')
        new_user = User(username=username, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            session['role'] = user.role
            if user.role == 'admin':
                return redirect('/admin_dashboard')
            else:
                return redirect('/student_dashboard')
        else:
            return 'Invalid credentials'
    return render_template('login.html')


@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' in session and session['role'] == 'admin':
        students = User.query.filter_by(role='student').all()
        return render_template('admin_dashboard.html', students=students)
    return redirect('/login')


@app.route('/add_marks/<int:student_id>', methods=['GET', 'POST'])
def add_marks(student_id):
    if 'user_id' in session and session['role'] == 'admin':
        student = User.query.get(student_id)
        if request.method == 'POST':
            for i in range(1, 5):
                subject = request.form.get(f'subject{i}')
                marks = request.form.get(f'marks{i}')
                if subject and marks:
                    entry = Mark(student_id=student_id, subject=subject, marks=float(marks))
                    db.session.add(entry)
            db.session.commit()
            return redirect('/admin_dashboard')
        return render_template('add_marks.html', student=student)
    return redirect('/login')


@app.route('/student_dashboard')
def student_dashboard():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user.role == 'student':
            subject_marks_raw = Mark.query.filter_by(student_id=user.id).all()
            subject_marks = [(mark.subject, mark.marks) for mark in subject_marks_raw]
            return render_template('student_dashboard.html', user=user, subject_marks=subject_marks)

        else:
            return render_template('some_template.html')  # admin/non-student view
    else:
        return redirect('/login')  # ✅ this must be indented under else



@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

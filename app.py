from flask import Flask, render_template, request, redirect, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "secret123"

# Database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Akshu@1234",
    database="student_db"
)
cursor = db.cursor()

# ---------------- HOME ----------------
@app.route('/')
def index():
    return redirect('/students')

# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s",
            (username, password)
        )
        user = cursor.fetchone()

        if user:
            session['user'] = username
            return redirect('/dashboard')
        else:
            return render_template('login.html', error="Invalid credentials")

    return render_template('login.html')

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')
# ---------------- dashboard ----------------
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')

    # Total students
    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    # Course-wise count
    cursor.execute("SELECT course, COUNT(*) FROM students GROUP BY course")
    course_data = cursor.fetchall()

    return render_template(
        "dashboard.html",
        total_students=total_students,
        course_data=course_data
    )
@app.route('/add-student')
def add_student_page():
    if 'user' not in session:
        return redirect('/login')
    return render_template('add_student.html')


# ---------------- STUDENTS LIST ----------------
@app.route('/students')
def students():
    if 'user' not in session:
        return redirect('/login')

    cursor.execute("SELECT * FROM students")
    data = cursor.fetchall()
    return render_template("students.html", students=data)

# ---------------- ADD STUDENT ----------------
@app.route('/add', methods=['POST'])
def add_student():
    if 'user' not in session:
        return redirect('/login')

    name = request.form['name']
    email = request.form['email']
    course = request.form['course']
    age = request.form['age']
   

    cursor.execute(
        "INSERT INTO students (name, email, course, age) VALUES (%s,%s,%s,%s)",
        (name, email, course, age)
    )
    db.commit()
    return redirect('/students')

# ---------------- SEARCH ----------------
@app.route('/search')
def search_student():
    if 'user' not in session:
        return redirect('/login')

    q = request.args.get('query')

    cursor.execute(
        "SELECT * FROM students WHERE name LIKE %s OR course LIKE %s",
        (f"%{q}%", f"%{q}%")
    )
    data = cursor.fetchall()

    return render_template("students.html", students=data)

# ---------------- EDIT ----------------
@app.route('/edit/<int:id>')
def edit_student(id):
    if 'user' not in session:
        return redirect('/login')

    cursor.execute("SELECT * FROM students WHERE id=%s", (id,))
    student = cursor.fetchone()
    return render_template("edit_student.html", student=student)

# ---------------- UPDATE ----------------
@app.route('/update/<int:id>', methods=['POST'])
def update_student(id):
    if 'user' not in session:
        return redirect('/login')

    name = request.form['name']
    email = request.form['email']
    course = request.form['course']
    age = request.form['age']

    cursor.execute(
        "UPDATE students SET name=%s, email=%s, course=%s, age=%s WHERE id=%s",
        (name, email, course, age, id)
    )
    db.commit()
    return redirect('/students')

# ---------------- DELETE ----------------
@app.route('/delete/<int:id>')
def delete(id):
    if 'user' not in session:
        return redirect('/login')

    cursor.execute("DELETE FROM students WHERE id=%s", (id,))
    db.commit()
    return redirect('/students')

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)

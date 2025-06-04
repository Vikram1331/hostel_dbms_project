from flask import Flask, render_template, request, redirect, session, flash
from datetime import datetime
import os
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'
DATABASE = 'hostel_db'

def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database=DATABASE
    )
    return conn

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    role = request.form['role']

    conn = get_db_connection()
    cursor = conn.cursor()

    if role == 'student':
        cursor.execute('SELECT * FROM student WHERE email = %s AND password = %s', (email, password))
    else:
        cursor.execute('SELECT * FROM admin WHERE email = %s AND password = %s', (email, password))
    
    user = cursor.fetchone()
    conn.close()

    if user:
        session['email'] = email
        session['role'] = role
        return redirect('/dashboard')
    else:
        flash('Invalid Credentials. Please try again.')
        return redirect('/')

@app.route('/dashboard')
def dashboard():
    if 'email' not in session:
        return redirect('/')
    if session['role'] == 'admin':
        return render_template('admin_dashboard.html')
    return render_template('student_dashboard.html')

@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
    if 'email' not in session:
        return redirect('/')

    if request.method == 'POST':
        # You can replace this with actual location check logic
        location = 'hostel'  # Assume inside hostel for now

        conn = get_db_connection()
        cursor = conn.cursor()

        today_str = datetime.now().strftime('%Y-%m-%d')
        cursor.execute('SELECT * FROM attendance WHERE email = %s AND date = %s', (session['email'], today_str))
        existing = cursor.fetchone()

        if existing:
            flash('Attendance already marked for today.')
        else:
            if location.lower() == 'hostel':
                # Insert with status 'Present'
                cursor.execute(
                    'INSERT INTO attendance (email, date, status) VALUES (%s, %s, %s)', 
                    (session['email'], today_str, 'Present')
                )
                conn.commit()
                flash('Attendance marked successfully!')
            else:
                flash('Attendance not marked. You are not inside hostel premises.')

        conn.close()
        return redirect('/attendance')

    return render_template('mark_attendance.html')

@app.route('/view_attendance')
def view_attendance():
    if 'email' not in session or session['role'] != 'admin':
        return redirect('/')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT email, date, status FROM attendance ORDER BY date DESC')
    attendance_records = cursor.fetchall()
    conn.close()

    return render_template('view_attendance.html', attendance_records=attendance_records)
@app.route('/view_complaints')
def view_complaints():
    if 'email' not in session or session['role'] != 'admin':
        return redirect('/')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT id, student_email, complaint_text, timestamp FROM complaints ORDER BY timestamp DESC')
    complaints = cursor.fetchall()
    conn.close()

    return render_template('view_complaints.html', complaints=complaints)

@app.route('/complaints', methods=['GET'])
def complaints():
    if 'email' not in session:
        return redirect('/')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT complaint_text, timestamp FROM complaints WHERE student_email = %s ORDER BY timestamp DESC', (session['email'],))
    complaints = cursor.fetchall()
    conn.close()

    return render_template('complaints.html', complaints=complaints)

@app.route('/submit_complaint', methods=['POST'])
def submit_complaint():
    if 'email' not in session:
        return redirect('/')

    complaint_text = request.form['complaint_text']

    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now()
    cursor.execute('INSERT INTO complaints (student_email, complaint_text, timestamp, date_submitted) VALUES (%s, %s, %s, %s)',
                   (session['email'], complaint_text, now, now))
    conn.commit()
    conn.close()

    flash('Complaint submitted successfully!')
    return redirect('/complaints')


@app.route('/guest_invite', methods=['GET', 'POST'])
def guest_invite():
    if 'email' not in session:
        return redirect('/')

    invite_code = None

    if request.method == 'POST':
        guest_name = request.form['guest_name']
        visit_date = request.form['visit_date']
        invite_code = os.urandom(4).hex()

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO guest_invite (student_email, guest_name, visit_date, invite_code) VALUES (%s, %s, %s, %s)',
                       (session['email'], guest_name, visit_date, invite_code))
        conn.commit()
        conn.close()

        return render_template('invite_guest.html', invite_code=invite_code)

    return render_template('invite_guest.html')

@app.route('/view_guest_invites')
def view_guest_invites():
    if 'email' not in session or session['role'] != 'admin':
        return redirect('/')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM guest_invite ORDER BY visit_date DESC')
    invites = cursor.fetchall()
    conn.close()

    return render_template('view_guest_invites.html', invites=invites)

@app.route('/verify_guest', methods=['GET', 'POST'])
def verify_guest():
    if 'email' not in session or session['role'] != 'admin':
        return redirect('/')

    if request.method == 'POST':
        invite_code = request.form['invite_code']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM guest_invite WHERE invite_code = %s', (invite_code,))
        invite = cursor.fetchone()
        conn.close()

        if invite:
            flash('Guest Invite Verified!')
        else:
            flash('Invalid Invite Code!')

        return redirect('/verify_guest')

    return render_template('verify_guest.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)

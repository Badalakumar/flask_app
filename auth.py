from flask import Flask, Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from db import db_connection

auth_ap = Blueprint('auth', __name__)

# ✅ Inject session role into all templates automatically
@auth_ap.app_context_processor
def inject_user_role():
    return dict(role=session.get('role'))

# ------------------------------------------
# HOME / LOGIN PAGE
# ------------------------------------------
@auth_ap.route('/')
def index():
    return redirect(url_for('auth.login'))

# ------------------------------------------
# REGISTER
# ------------------------------------------
@auth_ap.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        Name = request.form['sname']
        Email = request.form['email']
        Password = generate_password_hash(request.form['password'])
        Phone = request.form['phone']
        institutionName = request.form.get('institutionName', 'ASstide Software Solution LLP')

        con = db_connection()
        cursor = con.cursor()

        try:
            # Insert into user table
            cursor.execute("""
                INSERT INTO user (Name, Email, Password, Phone, RoleName)
                VALUES (%s, %s, %s, %s, %s)
            """, (Name, Email, Password, Phone, 'Admin'))
            con.commit()

            user_id = cursor.lastrowid

            # Insert into admin table
            cursor.execute("""
                INSERT INTO admin (Userid, institutionName, Name, Email, Phone)
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, institutionName, Name, Email, Phone))
            con.commit()

            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))

        except Exception as e:
            con.rollback()
            flash(f'Error during registration: {str(e)}', 'danger')
        finally:
            cursor.close()
            con.close()

    return render_template('login.html')

# ------------------------------------------
# LOGIN
# ------------------------------------------
@auth_ap.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        Phone = request.form['phone']
        Password = request.form['password']

        con = db_connection()
        cursor = con.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user WHERE Phone = %s", (Phone,))
        user = cursor.fetchone()

        if not user:
            flash('User not found. Please check your phone number.', 'danger')
            return render_template('login.html')

        if check_password_hash(user['Password'], Password):
            
            session['user_id'] = user['UserId']
            role = user.get('RoleName') or user.get('Role') or 'Student'
            session['role'] = role  # ✅ store role in session
            session['name'] = user.get('Name') or user.get('name') or ''
            # Redirect by role
            if role == 'Admin':
                cursor.execute("SELECT * FROM admin WHERE UserId = %s", (user['UserId'],))
                admin = cursor.fetchone()
                if admin:
                    session['admin_id'] = admin['Adminid']
                    session['name']= admin['Name']
                flash('Admin login successful!', 'success')
                return redirect(url_for('admin.home'))

            elif role == 'Teacher':
                cursor.execute("SELECT * FROM teacher WHERE UserId = %s", (user['UserId'],))
                teacher = cursor.fetchone()
                print(teacher)
                print(teacher)
                if teacher:
                    session['teacher_id'] = teacher['TeacherId']
                    session['name']= teacher['Name']
                flash('Teacher login successful!', 'success')
                return redirect(url_for('auth.teacher_dashboard'))

            elif role == 'Student':
                cursor.execute("SELECT * FROM student WHERE UserId = %s", (user['UserId'],))
                student = cursor.fetchone()
                if student:
                    session['student_id'] = student['StudentId']
                    session['name']= student['Name']
                flash('Student login successful!', 'success')
                return redirect(url_for('auth.student_dashboard'))

            else:
                flash('Invalid role for user.', 'danger')
                return render_template('login.html')
        else:
            flash('Invalid password. Please try again.', 'danger')
            return render_template('login.html')

    return render_template('login.html')

# ------------------------------------------
# LOGOUT
# ------------------------------------------
@auth_ap.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))

# ------------------------------------------
# DASHBOARDS
# ------------------------------------------
@auth_ap.route('/student_dashboard')
def student_dashboard():
    return render_template('base.html')

@auth_ap.route('/teacher_dashboard')
def teacher_dashboard():
    return render_template('base.html')

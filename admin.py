from flask import Blueprint, render_template, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from db import db_connection

admin_ap = Blueprint('admin', __name__)


from flask import Blueprint, render_template, request, jsonify, session
from werkzeug.security import generate_password_hash
from db import db_connection

admin_ap = Blueprint('admin', __name__)

from flask import Blueprint, render_template, request, jsonify, session
from werkzeug.security import generate_password_hash
from db import db_connection

admin_ap = Blueprint('admin', __name__)

@admin_ap.route("/add_student", methods=["GET", "POST"])
def add_student():
    con = db_connection()
    cursor = con.cursor(dictionary=True)
    admin_id = session.get('admin_id')

    if request.method == "POST":
        if not request.is_json:
            return jsonify({"success": False, "error": "Expected JSON"}), 400

        data = request.get_json()
        try:
            student_id = data.get('StudentId')
            AdminId = admin_id
            Name = data.get('name')
            EmailId = data.get('emailId')
            PhoneNo = data.get('phoneNo')
            Password = generate_password_hash(data.get('password'))
            Gender = data.get('gender')
            DOB = data.get('dob')
            if DOB:
                DOB = DOB.split("T")[0] if "T" in DOB else DOB
            ClassName = data.get('className')
            Department = data.get('department')
            SubjectIds = data.get('subjects', [])
            FatherName = data.get('fatherName')
            MotherName = data.get('motherName')
            Address = data.get('address')

            # Ensure SubjectIds is a list of integers
            if not isinstance(SubjectIds, list):
                SubjectIds = [SubjectIds]
            SubjectIds = [int(s) for s in SubjectIds if str(s).isdigit()]
            subject_ids_str = ",".join(map(str, SubjectIds))

            # Fetch subject names for the selected SubjectIds
            subject_names_str = ""
            if SubjectIds:
                cursor.execute(
                    "SELECT SubjectName FROM subject WHERE SubjectId IN (%s)" %
                    ','.join(['%s'] * len(SubjectIds)), tuple(SubjectIds)
                )
                subject_names = [row['SubjectName'] for row in cursor.fetchall()]
                subject_names_str = ", ".join(subject_names)  # store as comma-separated

            # ---------------------------
            # UPDATE EXISTING STUDENT
            # ---------------------------
            if student_id:
                cursor.execute("""
                    UPDATE student SET
                        AdminId=%s, Name=%s, EmailId=%s, PhoneNo=%s, Gender=%s, DOB=%s,
                        ClassName=%s, Department=%s, SubjectIds=%s, Subject=%s,
                        FatherName=%s, MotherName=%s, Address=%s
                    WHERE StudentId=%s
                """, (AdminId, Name, EmailId, PhoneNo, Gender, DOB,
                      ClassName, Department, subject_ids_str, subject_names_str,
                      FatherName, MotherName, Address, student_id))
                con.commit()

                # Update StudentSubject linking table
                cursor.execute("DELETE FROM StudentSubject WHERE StudentId=%s", (student_id,))
                for sid in set(SubjectIds):
                    cursor.execute(
                        "INSERT INTO StudentSubject (StudentId, SubjectId) VALUES (%s, %s)",
                        (student_id, sid)
                    )
                con.commit()

            # ---------------------------
            # INSERT NEW STUDENT
            # ---------------------------
            else:
                cursor.execute("""
                    INSERT INTO student
                    (AdminId, Name, EmailId, PhoneNo, Gender, DOB, Password,
                     ClassName, Department, SubjectIds, Subject,
                     FatherName, MotherName, Address)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, (AdminId, Name, EmailId, PhoneNo, Gender, DOB, Password,
                      ClassName, Department, subject_ids_str, subject_names_str,
                      FatherName, MotherName, Address))
                con.commit()

                cursor.execute("SELECT LAST_INSERT_ID() AS StudentId")
                student_id = cursor.fetchone()['StudentId']

                # Create linked user
                RoleName = 'student'
                is_active = 'Active'
                cursor.execute("""
                    INSERT INTO user (Name, Email, Phone, RoleName, Password, IsActive)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (Name, EmailId, PhoneNo, RoleName, Password, is_active))
                con.commit()

                cursor.execute("SELECT LAST_INSERT_ID() AS UserId")
                user_id = cursor.fetchone()['UserId']
                cursor.execute("UPDATE student SET UserId=%s WHERE StudentId=%s", (user_id, student_id))
                con.commit()

                # Insert into StudentSubject
                for sid in set(SubjectIds):
                    cursor.execute(
                        "INSERT INTO StudentSubject (StudentId, SubjectId) VALUES (%s, %s)",
                        (student_id, sid)
                    )
                con.commit()

            # Fetch updated student with subjects
            cursor.execute("SELECT * FROM student WHERE StudentId=%s", (student_id,))
            student = cursor.fetchone()

            cursor.execute("""
                SELECT s.SubjectId, s.SubjectName
                FROM Subject s
                JOIN StudentSubject ss ON s.SubjectId = ss.SubjectId
                WHERE ss.StudentId=%s
            """, (student_id,))
            subjects = cursor.fetchall()

            student['Subjects'] = [s['SubjectName'] for s in subjects]
            student['SubjectIds'] = [s['SubjectId'] for s in subjects]
            if student.get('DOB'):
                student['DOB'] = str(student['DOB']).split(" ")[0]

            return jsonify({"success": True, "student": student}), 200

        except Exception as e:
            con.rollback()
            return jsonify({"success": False, "error": str(e)}), 500
        finally:
            cursor.close()
            con.close()

    # ---------------------------
    # GET request (render page)
    # ---------------------------
    cursor.execute("SELECT * FROM student")
    students = cursor.fetchall()

    # Fetch subjects for each student
    cursor.execute("""
        SELECT ss.StudentId,
               GROUP_CONCAT(s.SubjectId) AS SubjectIds,
               GROUP_CONCAT(s.SubjectName SEPARATOR ', ') AS Subjects
        FROM StudentSubject ss
        JOIN Subject s ON ss.SubjectId = s.SubjectId
        GROUP BY ss.StudentId
    """)
    student_subjects = cursor.fetchall()

    student_map = {}
    for row in student_subjects:
        student_map[row['StudentId']] = {
            'SubjectIds': list(map(int, row['SubjectIds'].split(','))) if row['SubjectIds'] else [],
            'Subjects': row['Subjects']
        }

    for student in students:
        data = student_map.get(student['StudentId'], {'SubjectIds': [], 'Subjects': ''})
        student['Subjects'] = data['Subjects']
        student['SubjectIds'] = data['SubjectIds']
        if student.get('DOB'):
            student['DOB'] = str(student['DOB']).split(" ")[0]

    cursor.execute("SELECT SubjectId, SubjectName FROM subject WHERE IsActive='Active'")
    subjects = cursor.fetchall()

    cursor.close()
    con.close()

    return render_template("addStudent.html", students=students, subjects=subjects, admin_id=admin_id)

@admin_ap.route('/')
def home():
    return render_template('base.html') 

# HTML route (for the UI)
@admin_ap.route("/subjects", methods=["GET"])
def add_subjects_form():
    con = db_connection()
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT SubjectId, SubjectName FROM subject")
    teachers = cursor.fetchall()
    cursor.close()
    con.close()
    return render_template("subject.html", teachers=teachers)

@admin_ap.route("/api/subjects", methods=["GET", "POST"])
def api_subjects():
    con = db_connection()
    cursor = con.cursor(dictionary=True)

    if request.method == "GET":
        try:
            cursor.execute("""
    SELECT 
        s.SubjectId,
        s.SubjectName,
        s.IsActive
    FROM Subject s
    GROUP BY s.SubjectId, s.SubjectName, s.IsActive
""")

            data = cursor.fetchall()
            return jsonify(data), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            con.close()

    elif request.method == "POST":
        try:
            data = request.get_json()
            subject_id = data.get("subjectId")
            # Accept either boolean or 'Active'/'Inactive'
            is_active_flag = data.get("isActive")
            if is_active_flag in (True, 'true', 'True', '1'):
                is_active = "Active"
            elif is_active_flag in (False, 'false', 'False', '0', None):
                # If None and no other update fields, we will use provided isActive or skip
                is_active = "Inactive" if is_active_flag is False else None
            else:
                is_active = "Active" if is_active_flag else "Inactive"

            subject_name = data.get("subjectName")
            teacher_id = data.get("teacherId")

            # If only toggling status
            if subject_id and subject_name is None and teacher_id is None and is_active is not None:
                update_query = "UPDATE Subject SET IsActive=%s WHERE SubjectId=%s"
                cursor.execute(update_query, (is_active, subject_id))
                con.commit()
            else:
                # For add or full update (insert/update logic)
                if subject_id:
                    # update with provided non-null fields only
                    update_parts = []
                    params = []
                    if subject_name is not None:
                        update_parts.append("SubjectName=%s"); params.append(subject_name)
                    if teacher_id is not None:
                        update_parts.append("TeacherId=%s"); params.append(teacher_id)
                    if is_active is not None:
                        update_parts.append("IsActive=%s"); params.append(is_active)
                    if update_parts:
                        sql = "UPDATE Subject SET " + ", ".join(update_parts) + " WHERE SubjectId=%s"
                        params.append(subject_id)
                        cursor.execute(sql, tuple(params))
                        con.commit()
                else:
                    # insert new subject (require fields)
                    if not subject_name:
                        return jsonify({"error": "Subject name and teacher are required for insert"}), 400
                    insert_query = "INSERT INTO Subject (SubjectName, IsActive) VALUES ( %s, %s)"
                    cursor.execute(insert_query, (subject_name, is_active or 'Active'))
                    con.commit()

            # After change, fetch and return the full updated row so frontend can merge safely
            cursor.execute("""
                SELECT s.SubjectId, s.SubjectName, s.IsActive
                FROM Subject s
                WHERE s.SubjectId = %s
            """, (subject_id,))
            updated_row = cursor.fetchone()
            return jsonify({"message": "OK", "row": updated_row}), 200
        except Exception as e:
            con.rollback()
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            con.close()


@admin_ap.route('/attendance', methods=['GET', 'POST'])
def attendance():
    con = db_connection()
    cursor = con.cursor(dictionary=True)

    if request.method == 'POST':
        try:
            data = request.get_json()
            date = data.get('date')
            class_name = data.get('class')
            subject_id = data.get('subject')
            records = data.get('records', [])

            for rec in records:
                student_id = rec['rollNo']
                status = 'P' if rec['status'] == 'Present' else 'A'
                cursor.execute("""
                    INSERT INTO attendance (StudentID, SubjectId, Status, Date)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE Status=%s
                """, (student_id, subject_id, status, date, status))
            con.commit()
            return jsonify({'success': True, 'message': 'Attendance saved successfully!'})

        except Exception as e:
            con.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
        finally:
            cursor.close()
            con.close()

    # GET: load classes and subjects
    cursor.execute("SELECT DISTINCT ClassName FROM Student")
    classes = [row['ClassName'] for row in cursor.fetchall()]

    cursor.execute("SELECT SubjectId, SubjectName FROM Subject WHERE IsActive='Active'")
    subjects = cursor.fetchall()

    cursor.close()
    con.close()
    return render_template('attendance.html', classes=classes, subjects=subjects)




@admin_ap.route('/api/students')
def get_students():
    class_name = request.args.get('class')
    date = request.args.get('date')
    subject_id = request.args.get('subject')

    if not class_name or not date or not subject_id:
        return jsonify({"error": "class, date, and subject are required"}), 400

    con = db_connection()
    cursor = con.cursor(dictionary=True)

    try:
        query = """
            SELECT s.StudentID, s.Name, 
                   IFNULL(a.Status,'') as Status
            FROM Student s
            LEFT JOIN attendance a 
            ON s.StudentID = a.StudentID 
               AND a.SubjectId=%s 
               AND a.Date=%s
            WHERE s.ClassName=%s
        """
        cursor.execute(query, (subject_id, date, class_name))
        students = cursor.fetchall()
        return jsonify(students)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        con.close()



@admin_ap.route("/teacher", methods=["GET", "POST"])
def teacher():
    con = db_connection()
    cursor = con.cursor(dictionary=True)

    if request.method == "POST":
        data = request.get_json()
        if not data:
            return jsonify({"error": "No input data"}), 400

        try:
            teacher_id = data.get("teacherId")
            AdminId = data.get("adminName")
            Name = data.get("name")
            EmailId = data.get("emailId")
            PhoneNo = data.get("phoneNo")
            Password = data.get("psw")  # may be empty or absent
            Subject_list = data.get("subjects", [])  # array of subject IDs (or strings)
            # Join or store as you like — here using comma separation
            Subject = ", ".join(Subject_list) if isinstance(Subject_list, (list, tuple)) else str(Subject_list)
            IsActive = data.get("isActive", True)

            # Hash password if provided
            hashed_password = None
            if Password and Password.strip() != "":
                hashed_password = generate_password_hash(Password)

            if teacher_id:
                # UPDATE existing teacher
                if hashed_password:  # update password too
                    sql = """
                      UPDATE Teacher
                      SET AdminId = %s, Name = %s, EmailId = %s,
                          PhoneNo = %s, Password = %s, Subject = %s, IsActive = %s
                      WHERE TeacherId = %s
                    """
                    params = (AdminId, Name, EmailId, PhoneNo, hashed_password, Subject, IsActive, teacher_id)
                else:
                    sql = """
                      UPDATE Teacher
                      SET AdminId = %s, Name = %s, EmailId = %s,
                          PhoneNo = %s, Subject = %s, IsActive = %s
                      WHERE TeacherId = %s
                    """
                    params = (AdminId, Name, EmailId, PhoneNo, Subject, IsActive, teacher_id)

                cursor.execute(sql, params)
                con.commit()
                return jsonify({"message": "Teacher updated successfully"}), 200

            else:
                # INSERT new teacher — password is required
                if not hashed_password:
                    return jsonify({"error": "Password is required for new teacher"}), 400

                sql = """
                  INSERT INTO Teacher (AdminId, Name, EmailId, Password, PhoneNo, Subject, IsActive)
                  VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                params = (AdminId, Name, EmailId, hashed_password, PhoneNo, Subject, IsActive)
                cursor.execute(sql, params)
                con.commit()
                return jsonify({"message": "Teacher added successfully"}), 200

        except Exception as e:
            con.rollback()
            print(f"Error inserting/updating teacher: {e}")
            return jsonify({"error": str(e)}), 500

    # GET request: render page
    cursor.execute("SELECT * FROM Teacher")
    teachers = cursor.fetchall()

    cursor.execute("SELECT SubjectId, SubjectName FROM subject")
    subjects = cursor.fetchall()

    cursor.close()
    con.close()
    return render_template("teacher.html", teachers=teachers, subjects=subjects)





    



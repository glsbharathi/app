from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import matplotlib.pyplot as plt
import io
import base64
app = Flask(__name__)

# Connect to the MySQL database
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='root',
    database='c361',
    port=3306
)
cursor = conn.cursor()

# Create tables for students, subjects, and marks if they don't exist
create_students_table_query = """
    CREATE TABLE IF NOT EXISTS students (
        id INT AUTO_INCREMENT PRIMARY KEY,
        student_name VARCHAR(255) NOT NULL
    )
"""
create_subjects_table_query = """
    CREATE TABLE IF NOT EXISTS subjects (
        id INT AUTO_INCREMENT PRIMARY KEY,
        subject_name VARCHAR(255) NOT NULL
    )
"""
create_marks_table_query = """
    CREATE TABLE IF NOT EXISTS marks (
        id INT AUTO_INCREMENT PRIMARY KEY,
        student_id INT NOT NULL,
        subject_id INT NOT NULL,
        marks FLOAT NOT NULL,
        FOREIGN KEY (student_id) REFERENCES students(id),
        FOREIGN KEY (subject_id) REFERENCES subjects(id)
    )
"""
cursor.execute(create_students_table_query)
cursor.execute(create_subjects_table_query)
cursor.execute(create_marks_table_query)
conn.commit()



def createApp():
    @app.route('/')
    def index():
        cursor.execute("SELECT s.id, s.student_name, sub.subject_name, m.marks FROM students s INNER JOIN marks m ON s.id = m.student_id INNER JOIN subjects sub ON m.subject_id = sub.id ")
        myresult = cursor.fetchall()
        return render_template('index.html', data=myresult)


    @app.route('/insert', methods=['GET', 'POST'])
    def insert():
        if request.method == 'POST':
            print("inside post")
            try:
                student_name = request.form['student_name']
                subject_name1 = request.form['subject_name1']
                marks1 = request.form['marks1']
                subject_name2 = request.form['subject_name2']
                marks2 = request.form['marks2']
                subject_name3 = request.form['subject_name3']
                marks3 = request.form['marks3']

                # Insert student name into 'students' table
                insert_student_query = "INSERT INTO students (student_name) VALUES (%s)"
                cursor.execute(insert_student_query, (student_name,))

                # Retrieve the student ID
                student_id = cursor.lastrowid

                # Insert subject names into 'subjects' table
                insert_subject_query1 = "INSERT INTO subjects (subject_name) VALUES (%s)"
                cursor.execute(insert_subject_query1, (subject_name1,))
                subject_id1 = cursor.lastrowid

                insert_subject_query2 = "INSERT INTO subjects (subject_name) VALUES (%s)"
                cursor.execute(insert_subject_query2, (subject_name2,))
                subject_id2 = cursor.lastrowid

                insert_subject_query3 = "INSERT INTO subjects (subject_name) VALUES (%s)"
                cursor.execute(insert_subject_query3, (subject_name3,))
                subject_id3 = cursor.lastrowid

                # Insert marks into 'marks' table
                insert_marks_query1 = "INSERT INTO marks (student_id, subject_id, marks) VALUES (%s, %s, %s)"
                cursor.execute(insert_marks_query1, (student_id, subject_id1, marks1))

                insert_marks_query2 = "INSERT INTO marks (student_id, subject_id, marks) VALUES (%s, %s, %s)"
                cursor.execute(insert_marks_query2, (student_id, subject_id2, marks2))

                insert_marks_query3 = "INSERT INTO marks (student_id, subject_id, marks) VALUES (%s, %s, %s)"
                cursor.execute(insert_marks_query3, (student_id, subject_id3, marks3))

                # Commit the changes
                conn.commit()

                return redirect(url_for('index'))
        
            except Exception as e: 
                print(e)

        return render_template("insert.html")


    @app.route('/average')
    def average():
        # Query the MySQL database to get average marks for each student and subject
        average_query = """
            SELECT s.id, s.student_name, AVG(m.marks)
            FROM students s
            INNER JOIN marks m ON s.id = m.student_id
            GROUP BY s.student_name
        """
        cursor.execute(average_query)
        data = cursor.fetchall()

        # Pass the average marks data to the template
        return render_template('average.html', data=data)

    @app.route('/search', methods=['GET', 'POST'])
    def search():
        if request.method == 'POST':
            # Retrieve the student name from the form
            student_name = request.form['student_name']
#want to change commite
            # Query the MySQL database to search for the student
            search_query = """
                SELECT s.student_name, sub.subject_name, m.marks
                FROM students s
                INNER JOIN marks m ON s.id = m.student_id
                INNER JOIN subjects sub ON m.subject_id = sub.id
                Where s.student_name = %s
            """
            cursor.execute(search_query, (student_name,))
            data = cursor.fetchall()

            return render_template('search.html', data=data)

        return render_template('search.html')
    
    @app.route('/visualization')
    def visualization():
        # Query the MySQL database to get marks for each student and subject
        query = """
            SELECT s.student_name, sub.subject_name, m.marks
            FROM students s
            INNER JOIN marks m ON s.id = m.student_id
            INNER JOIN subjects sub ON m.subject_id = sub.id
        """
        cursor.execute(query)
        data = cursor.fetchall()

        # Group the marks data by student and subject
        student_subject_marks = {}
        for row in data:
            student_name = row[0]
            subject_name = row[1]
            marks = row[2]

            if student_name not in student_subject_marks:
                student_subject_marks[student_name] = {}

            student_subject_marks[student_name][subject_name] = marks

        # Generate pie charts for each student
        pie_charts = []
        for student_name, subject_marks in student_subject_marks.items():
            subjects = list(subject_marks.keys())
            marks = list(subject_marks.values())

            # Create a new figure for each student
            fig, ax = plt.subplots()

            # Generate the pie chart
            ax.pie(marks, labels=subjects, autopct='%1.1f%%')

            # Set the title for the pie chart
            ax.set_title(f'{student_name} - Marks by Subject')

            # Convert the plot to a PNG image
            image_stream = io.BytesIO()
            plt.savefig(image_stream, format='png')
            image_stream.seek(0)
            image_base64 = base64.b64encode(image_stream.read()).decode()

            # Append the base64-encoded image to the list
            pie_charts.append(image_base64)

            # Clear the current figure to prepare for the next iteration
            plt.clf()

        return render_template('visualization.html', pie_charts=pie_charts)
    
    @app.route('/visualization1')
    def visualization1():
        # Query the MySQL database to get the data for visualization
        query = """
            SELECT subject_name, AVG(marks) as average_marks
            FROM subjects s
            INNER JOIN marks m ON s.id = m.subject_id
            GROUP BY subject_name
        """
        cursor.execute(query)
        data = cursor.fetchall()

        # Extract subject names and average marks from the data
        subjects = [row[0] for row in data]
        average_marks = [row[1] for row in data]

        # Create a bar chart
        plt.bar(subjects, average_marks)
        plt.xlabel('Subject')
        plt.ylabel('Average Marks')
        plt.title('Average Marks by Subject')

        # Save the plot to a buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)

        # Encode the buffer image to base64
        image_base64 = base64.b64encode(buffer.read()).decode()

        # Generate the HTML to display the image
        image_html = f'<img src="data:image/png;base64,{image_base64}" alt="Visualization">'

        return render_template('visualization1.html', image_html=image_html)

    return app

if __name__ == '__main__':
    app = createApp()
    app.run()
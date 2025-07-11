# app.py
from flask import Flask, request, render_template, redirect
from configure import get_db_connection
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Home route
@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("AddEmp.html")

# About route — FIX: cannot render a URL, use redirect instead
@app.route("/about", methods=["POST"])
def about():
    return redirect("https://www.intellipaat.com")

# Add Employee Route
@app.route("/addEmp", methods=["POST"])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    emp_image_file = request.files['emp_image_file']

    if emp_image_file.filename == "":
        return "❌ Please select a file"

    filename = f"{emp_id}_{emp_image_file.filename}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    emp_image_file.save(filepath)

    try:
        db_conn = get_db_connection()
        cursor = db_conn.cursor()

        insert_sql = """
            INSERT INTO employee (emp_id, first_name, last_name, pri_skill, location, emp_image_path)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location, filename))
        db_conn.commit()
        cursor.close()
        db_conn.close()
        return f"✅ Employee {first_name} {last_name} added successfully!"
    except Exception as e:
        return f"❌ Error: {e}"

# Basic test route
@app.route('/test')
def hello():
    return '✅ Hello, Flask is working!'

# Run the app
if __name__ == '__main__':
    app.run(debug=True)

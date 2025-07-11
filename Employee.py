from flask import Flask, request, render_template, redirect
from configure import get_db_connection
import boto3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
S3_BUCKET = 'your-s3-bucket-name'

# Initialize S3 client
s3 = boto3.client('s3')

@app.route('/ping')
def ping():
    return '✅ Flask is working!'

@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("AddEmp.html")

@app.route("/about", methods=["GET"])
def about():
    return redirect("https://www.intellipaat.com")

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

    filename = secure_filename(f"{emp_id}_{emp_image_file.filename}")
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    emp_image_file.save(filepath)

    # Upload image to S3
    try:
        s3.upload_file(
            Filename=filepath,
            Bucket=S3_BUCKET,
            Key=filename,
            ExtraArgs={'ACL': 'public-read'}
        )
        image_url = f"https://{S3_BUCKET}.s3.amazonaws.com/{filename}"
    except Exception as s3_err:
        return f"❌ S3 Upload Error: {s3_err}"

    # Store employee data in MySQL
    try:
        db_conn = get_db_connection()
        cursor = db_conn.cursor()

        insert_sql = """
            INSERT INTO employee (emp_id, first_name, last_name, pri_skill, location, emp_image_path)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location, image_url))
        db_conn.commit()
        cursor.close()
        db_conn.close()

        return f"✅ Employee {first_name} {last_name} added successfully!<br>📷 Image URL: <a href='{image_url}'>{image_url}</a>"
    except Exception as db_err:
        return f"❌ Database Error: {db_err}"

if __name__ == '__main__':
    app.run(debug=True)


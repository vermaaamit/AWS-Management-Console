from flask import Flask, render_template, request, redirect
import pymysql
import boto3
from botocore.exceptions import ClientError
import os

app = Flask(__name__)

# AWS Configuration
bucket = 'av553202'  # Your S3 bucket name
region = 'us-east-1'  # Your AWS region

# Database Configuration
db_host = 'employee.c2rsg2uwe0k9.us-east-1.rds.amazonaws.com'
db_user = 'amitverma'  # Replace with your actual username
db_password = 'Rajesh1234'  # Replace with your actual password
db_name = 'employee'  # Replace with your actual database name

# Initialize database connection
try:
    db_conn = pymysql.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name,
        connect_timeout=5
    )
except Exception as e:
    db_conn = None
    print(f"ERROR: Could not connect to MySQL: {e}")

# Homepage
@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('AddEmp.html')

# About route
@app.route("/about", methods=['POST'])
def about():
    return redirect("https://www.intellipaat.com")

# Add Employee Route
@app.route("/addemp", methods=['POST'])
def AddEmp():
    if db_conn is None:
        return "Database connection error. Please contact the administrator."

    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    emp_image_file = request.files['emp_image_file']

    if emp_image_file.filename == "":
        return "Please select a file"

    try:
        cursor = db_conn.cursor()
        
        # Insert employee data into RDS
        insert_sql = "INSERT INTO employee (emp_id, first_name, last_name, pri_skill, location) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location))
        db_conn.commit()

        # Upload to S3
        s3 = boto3.client('s3')
        emp_image_file_name_in_s3 = f"emp-id-{emp_id}_image_file"
        
        try:
            s3.upload_fileobj(
                emp_image_file,
                bucket,
                emp_image_file_name_in_s3,
                ExtraArgs={'ACL': 'public-read'}
            )
            
            # Generate public URL
            object_url = f"https://{bucket}.s3.{region}.amazonaws.com/{emp_image_file_name_in_s3}"
            
            return f"Employee added successfully! Image URL: {object_url}"
            
        except ClientError as e:
            return f"S3 Upload Error: {str(e)}"
            
    except Exception as e:
        db_conn.rollback()
        return f"Database Error: {str(e)}"
    finally:
        if 'cursor' in locals():
            cursor.close()

if __name__ == '__main__':
    app.run(debug=True)
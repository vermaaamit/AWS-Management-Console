from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from configure import *  # Imports: custombucket, customregion, customhost, customuser, custompass, customdb

app = Flask(__name__)

# AWS S3 and MySQL configuration
bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb
)

ouput= {}
table = 'employee'
# Homepage
@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('AddEmp.html')

# About route
@app.route("/about", methods=['POST'])
def about():
    return render_template('https://www.intellipaat.com')

# Add Employee Route
@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    emp_image_file = request.files['emp_image_file']

    if emp_image_file.filename == "":
        return "Please select a file"

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    try:
        # Insert employee data into RDS
        cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location))
        db_conn.commit()

        # Image file name to be stored in S3
        emp_image_file_name_in_s3 = f"emp-id-{emp_id}_image_file"

        # Upload to S3
        s3 = boto3.resource('s3')
        s3.Bucket(bucket).put_object(
            Key=emp_image_file_name_in_s3,
            Body=emp_image_file
        )

        # Generate S3 Image URL
        s3_client = boto3.client('s3')
        bucket_location = s3_client.get_bucket_location(Bucket=bucket)
        s3_region = bucket_location.get('LocationConstraint')

        if s3_region is None:
            s3_region = ''
        else:
            s3_region = '-' + s3_region

        object_url = f"https://s3{s3_region}.amazonaws.com/{bucket}/{emp_image_file_name_in_s3}"

        return f"""
        <h2>Employee data added successfully!</h2>
        <p>Name: {first_name} {last_name}</p>
        <p>ID: {emp_id}</p>
        <p>Location: {location}</p>
        <p>Skill: {pri_skill}</p>
        <img src="{object_url}" width="200px" alt="Employee Image">
        """

    except Exception as e:
        db_conn.rollback()
        return str(e)

# Run app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


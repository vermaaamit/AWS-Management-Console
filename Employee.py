from flask import Flask, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Homepage: Form to submit employee details
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle form submission
@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    emp_id = request.form['emp_id']
    department = request.form['department']

    # Handle image upload
    image = request.files['image']
    if image and image.filename != '':
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        image_url = url_for('static', filename='uploads/' + filename)
    else:
        image_url = None

    return render_template('employee_detail.html', name=name, emp_id=emp_id, department=department, image_url=image_url)

# Run the server publicly on port 5000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)



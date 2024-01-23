from flask import *
from flask_mysqldb import MySQL
from PyPDF2 import PdfReader
from docx import Document
import os

app = Flask(__name__)
app.config['SECRET_KEY']="fe639a85d1a24e8386a64fcce71305b3"
app.config['MYSQL_HOST'] = 'mysql-container'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Aravind@431'
app.config['MYSQL_DB'] = 'HR'
mysql = MySQL(app)

def search_word(file_path, search_term):
    l = 0
    search_results = []
    if file_path.endswith('.txt'):
        with open(file_path, 'r') as file:
            for line_number, line in enumerate(file, 1):
                if search_term.lower() in line.lower():
                    l += 1
                    search_results.append((line.strip()))
    elif file_path.endswith('.pdf'):
        with open(file_path, 'rb') as file:
            pdf = PdfReader(file)
            for page_number, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                lines = text.split('\n')
                for line_number, line in enumerate(lines, 1):
                    if search_term.lower() in line.lower():
                        l += 1
                        search_results.append(line.strip())
    elif file_path.endswith('.docx'):
        doc = Document(file_path)
        for para in doc.paragraphs:
            text = para.text.strip()
            if search_term.lower() in text.lower():
                l += 1
                search_results.append(text)

    if l >= 1:
        name = request.form['name']
        email = request.form['email']
        resume = request.files['resume']
        skill = request.form['skills']
        filename1 = resume.filename
        cur = mysql.connection.cursor() 
        create_table(cur)
        cur.execute(
        "INSERT INTO pro_detail (name, email, skill, filename, resume) VALUES (%s, %s, %s, %s, %s)",
        (name, email, skill, filename1, resume.read())
        )
        mysql.connection.commit()
        cur.close()

    return search_results

def create_table(cur):
    cur.execute('''CREATE TABLE IF NOT EXISTS pro_detail (
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL,
                    filename VARCHAR(255) NOT NULL,
                    skill VARCHAR(255) NOT NULL,
                    resume LONGBLOB NOT NULL
                )''')

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/home',methods=['GET'])
def home():
    return render_template('Homepage.html')
    

@app.route('/Homepage', methods=['POST'])
def home1():
    un = request.form['uname']
    ps = request.form['passw']

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Userl_login WHERE username = %s AND password = %s", (un, ps))
    user = cur.fetchone()
    cur.close()

    if user:
        return render_template('Homepage.html')
    else:
        error="Invalid credentials,Please enter valid credentials"
        return render_template('login.html',error1=error)

@app.route('/store_details', methods=['POST'])
def store_details():
    if request.method == 'POST':
        resume = request.files['resume']
        skill = request.form['skills']
        email = request.form['email']
        filename1 = resume.filename
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM pro_detail WHERE email LIKE %s", [email])
        ema = cur.fetchone()
        cur.close()
        if ema:
            error1="This profile is already exists"
            return render_template("Homepage.html",error1=error1)
        upload_dir = 'files1'
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        file_path = os.path.join(upload_dir, filename1)
        resume.save(file_path)

        search_res = search_word(file_path, skill)
        return render_template('data.html', search_result=search_res,skill=skill)

    return render_template('Homepage.html')

if __name__ == '__main__':
    app.run(debug=True)

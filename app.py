from flask import Flask, render_template, redirect,url_for,session, request
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from random import seed
from random import randint

app = Flask(__name__)

app.secret_key = "Shreyasbigboi"

app.config["MYSQL_HOST"] = '127.0.0.1'
app.config["MYSQL_USER"] = 'root'
app.config["MYSQL_PASSWORD"] = ''
app.config["MYSQL_DB"] = 'bank account'

mysql = MySQL(app)

#creating a logout function
@app.route('/logout')
def logout():
    # removing session hence the user is not logged in and redirected to login page
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route("/", methods=["GET","POST"])
def login():
    msg=""
    if request.method == "POST" and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM login WHERE username = %s AND password = %s", (username, password))
        mysql.connection.commit()
        user = cursor.fetchone()
        if user:
            #creating a session data to be used at different route
            session['loggedin'] = True
            session['id'] = user[0]
            session['username'] = user[1]
            msg = "Login Successful!"
            return redirect(url_for('home'))
        else:
            msg = "Incorrect Username or password"
    return render_template('login.html', msg=msg)

@app.route("/register", methods=["GET","POST"])
def register():
    msg=""
    if request.method == "POST" and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM login WHERE username= %s",(username,))
        mysql.connection.commit()
        account = cursor.fetchone()
        if account:
            msg="Account exists"
            redirect(url_for('login'))
        elif not re.match(r'[A-Za-z0-9]+', username): #checking if username containes alphabets lower & uppercase with numbers also(0 to 9)
            msg="Username must contain only alphabets and numbers!"
        elif not username or not password or not email:
            msg="Please fill out the form"
        else:
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO login VALUES(NULL, %s,%s,%s)", (username, password, email,))
            mysql.connection.commit()
            msg = "Account registered successfully"
            redirect(url_for('login'))
    elif request.method == "POST":
        #if the request is only post(no entry in input fields)
        msg = "Please enter the respective values into the field"
    return render_template('register.html', msg=msg)

@app.route("/home", methods=["GET","POST"])
def home():
    if 'loggedin' in session:
        return render_template('home.html')

@app.route("/profile", methods=["GET","POST"])
def profile():
    nric=''
    name=''
    age=''
    dob=''
    address=''
    occupation=''
    if 'loggedin' in session:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM profile WHERE NRIC=%s", (session['username'],))
        mysql.connection.commit()
        profile = cursor.fetchone()
        if session['username']:
            nric = profile[1]
            name= profile[2]
            age = profile[3]
            dob = profile[4]
            address = profile[5]
            occupation = profile[6]
    return render_template('profile.html',nric=nric, name=name, age=age, dob=dob, address=address, occupation=occupation)

@app.route("/edit", methods=["GET","POST"])
def edit():
    return render_template('edit.html')

@app.route("/create", methods=["GET","POST"])
def create():
    if 'loggedin' in session:
        if request.method == "POST" and 'account type' in request.form and 'current deposit' in request.form and 'name' in request.form:
            name = request.form['name'] 
            types = request.form['account type']
            deposit = request.form['current deposit']
            seed(1)
            number = randint(10000000, 100000000)
            number =str(number)
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO accounts VALUES(NULL,%s,%s,%s,%s)", (name,types,number,deposit))
            mysql.connection.commit()
            return redirect(url_for('home'))
        return render_template('create.html')

@app.route("/check", methods=["GET","POST"])
def check():
    acc_types = []
    acc_number = []
    acc_balance = []
    if 'loggedin' in session:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM profile WHERE NRIC=%s",(session['username'],))
        mysql.connection.commit()
        profile = cursor.fetchone()
        name = profile[2]
        cursor.execute("SELECT * FROM accounts WHERE name=%s",(name,))
        mysql.connection.commit()
        account = cursor.fetchall()
        i = 0
        length = len(account)
        
        for i in range(length):
            name = profile[2]
            accounts = account[i][2]
            acc_types.append(accounts)
            numbers = account[i][3]
            acc_number.append(numbers)    
            balance = account[i][4]
            acc_balance.append(balance)
        
        acc_types = ",".join(acc_types)
        acc_number = ",".join(acc_number)
        acc_balance = ",".join(map(str,acc_balance))
            
    return render_template('check.html', acc_types = acc_types, acc_number = acc_number, acc_balance = acc_balance)
if __name__ == '__main__':
    app.debug = True
    app.run()

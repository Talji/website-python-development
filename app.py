from flask import Flask, render_template, json, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from flaskext.mysql import MySQL
import mysql.connector

"""
mydb = mysql.connector.connect(

)

mycursor = mydb.cursor()
"""
mysql = MySQL()
app = Flask(__name__)

app.secret_key = ''


# Flask MySQL Configurations
app.config['MYSQL_DATABASE_USER'] = 'xxxxx'
app.config['MYSQL_DATABASE_PASSWORD'] = 'xxxxx'
app.config['MYSQL_DATABASE_DB'] = 'BucketList'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

@app.route('/')
def index():
    # my_list = ["Hey", "check", "this", "out"]
    return render_template('index.html')
    # return 'Hello, World!'
    # return my_list[0] # Works!

@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')

@app.route('/showSignin')
def showSignin():
    return render_template('signin.html')

@app.route('/validateLogin', methods=['POST'])
def validateLogin():
    try:
        _username = request.form['inputEmail']
        _password = request.form['inputPassword']

        # connect to mysql

        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc('sp_validateLogin',(_username,))
        data = cursor.fetchall()

        if len(data) > 0:
            if check_password_hash(str(data[0][3]),_password):
                session['user'] = data[0][0]
                return redirect('/userHome')
            else:
                return render_template('error.html',error = 'Wrong Email Address or Password.')
        else:
            return render_template('error.html',error = 'Wrong Email Address or Password.')

    except Exception as e:
        return render_template('error.html',error = str(e))
    finally:
        cursor.close()
        con.close()

@app.route('/userHome')
def userHome():
    if session.get('user'):
        return render_template('userHome.html')
    else:
        return render_template('error.html',error = 'Unauthorized Access')

@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/')

@app.route('/signUp', methods=['POST'])
def signUp():
    try:
        # read the posted values from the UI
        _name = request.form['inputName']
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']

        # validate the recieved values
        if _name and _email and _password:
            # return json.dumps({'html':'<span>All fields good!!</span>'})

            conn = mysql.connect()
            cursor = conn.cursor()
            #hashed Password
            _hashed_password = generate_password_hash(_password)
            cursor.callproc('sp_createUser', (_name,_email,_hashed_password))
            data = cursor.fetchall()

            if (len(data) is 0):
                conn.commit()
                return json.dumps({'message':'User created successfully !'})
            else:
                return json.dumps({'error':str(data[0])})

        else:
            return json.dumps({'html':'<span>Enter the required fields!</span>'})

    except Exception as e:
        return json.dumps({'error':str(e)})
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)

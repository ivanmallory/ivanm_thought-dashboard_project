from flask import Flask, render_template, request, redirect, session, flash
from flask_bcrypt import Bcrypt
from datetime import datetime
import re
from mysqlconnection import connectToMySQL

app = Flask(__name__)
app.secret_key = "Welcome to the thunder dome"
bcrpyt = Bcrypt(app)
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_user', methods=['POST'])
def create_user():
    is_valid = True
    SpecialSym = ['$','@', '#', '%']
    
    if len(request.form['fname']) < 2:
        is_valid = False
        flash("Please enter a first name")
    
    if len(request.form['lname']) < 2:
        is_valid = False
        flash("Please enter a last name")
    
    if not EMAIL_REGEX.match(request.form['email']):
        is_valid = False
        flash("Invalid email address!")
    
    if len(request.form['pass']) < 8:
        is_valid = False
        flash("Password Must Be At Least 5 Characters")
    
    if request.form['cpass'] != request.form ['pass']:
        is_valid = False
        flash("Incorrect Password")
    
    if not request.form['fname'].isalpha():
        is_valid = False
        flash("First name can only contain alphabetic characters")
    
    if not request.form['lname'].isalpha():
        is_valid = False
        flash("Last name can only contain alphabetic characters")
    
    if not any(char.isdigit() for char in request.form['pass']): 
        is_valid = False
        flash('Password should have at least one numeral') 
    
    if not any(char.isupper() for char in request.form['pass']): 
        is_valid = False
        flash('Password should have at least one uppercase letter') 
    
    if not any(char.islower() for char in request.form['pass']): 
        is_valid = False
        flash('Password should have at least one lowercase letter') 
    
    if not any(char in SpecialSym for char in request.form['pass']): 
        is_valid = False
        flash('Password should have at least one of the symbols $@#')
    
    mysql = connectToMySQL("dojo_thoughts")
    validate_email_query = 'SELECT id_users FROM users WHERE email=%(email)s;'
    form_data = {
        'email': request.form['email']
    }
    existing_users = mysql.query_db(validate_email_query, form_data)

    if existing_users:
        is_valid = False
        flash("Email already in use")
    
    if not is_valid:
        return redirect("/")

    if is_valid:
        mysql = connectToMySQL("dojo_thoughts")
        pw_hash = bcrpyt.generate_password_hash(request.form['pass'])
        query = "INSERT into users(first_name, last_name, email, password, created_at, updated_at) VALUES (%(fname)s, %(lname)s, %(email)s, %(password_hash)s, NOW(), NOW());"

        data = {
            "fname": request.form['fname'],
            "lname": request.form['lname'],
            "email": request.form['email'],
            "password_hash": pw_hash
        }
        result_id = mysql.query_db(query, data)
        flash("Successfully added:{}".format(result_id))
        return redirect("/success")
    return redirect("/")

@app.route('/login', methods=['POST'])
def login():
    mysql = connectToMySQL("dojo_thoughts")
    query = "SELECT * FROM users WHERE email = %(email)s;"
    data = { "email": request.form['email'] }
    result = mysql.query_db(query,data)
    if result: 
        if bcrpyt.check_password_hash(result[0]['password'], request.form['pass']):
            session['user_id'] = result[0]['id_users']
            return redirect("/success")
    flash("You could not be logged in")
    return redirect("/")

@app.route('/success')
def success():
    if 'user_id' not in session: 
        return redirect("/")

    mysql = connectToMySQL("dojo_thoughts")
    query = "SELECT users.first_name FROM users WHERE id_users = %(uid)s"
    data = {
        'uid': session['user_id']
    }
    result = mysql.query_db(query,data)

    mysql = connectToMySQL("dojo_thoughts")
    query = "SELECT thoughts.author, thoughts.id_thoughts, thoughts.content, thoughts.created_at, users.first_name, users.last_name FROM thoughts JOIN users on thoughts.author = users.id_users ORDER BY created_at DESC;"
    all_thoughts = mysql.query_db(query)

    mysql = connectToMySQL("dojo_thoughts")
    query = "SELECT thoughts_id_thoughts, COUNT(thoughts_id_thoughts) AS like_count FROM liked_thoughts GROUP BY thoughts_id_thoughts;"
    like_count = mysql.query_db(query)

    for thought in all_thoughts:
        for like in like_count:
            if like['thoughts_id_thoughts']  == thought['id_thoughts']:
                thought['like_count'] = like['like_count']
        
        if 'like_count' not in thought:
            thought['like_count'] = 0 
    if result:
        return render_template("dashboard.html", user_fn = result[0], all_thoughts = all_thoughts)
    else:
        return render_template("dashboard.html") 

@app.route('/thoughts/create', methods=["POST"])
def create_thought():
    is_valid = True
    if len(request.form['thought']) < 5:
        is_valid = False
        flash("Thought must be between 5-255 characters")
    if len(request.form['thought']) > 256:
        is_valid = False
        flash("Thought must be between 5-255 characters")

    if is_valid:
        mysql = connectToMySQL("dojo_thoughts")
        query = "INSERT into thoughts(content, author, created_at, updated_at) VALUES (%(tc)s, %(aid)s, NOW(), NOW());"

        data = {
            "tc": request.form['thought'],
            "aid": session['user_id']
        }
        mysql.query_db(query, data)
        
    return redirect("/success")

@app.route('/delete_thought/<thought_id>')
def delete_thought(thought_id):
    mysql = connectToMySQL("dojo_thoughts")
    query = "DELETE FROM thoughts WHERE id_thoughts = %(t_id)s AND author = %(u_id)s;"
    data = { 
        't_id': thought_id,
        'u_id': session['user_id']
    }
    mysql.query_db(query,data)
    return redirect('/success')

@app.route('/thought_details/<thought_id>') 
def thought_details(thought_id):
    mysql = connectToMySQL("dojo_thoughts")
    query = "SELECT thoughts.author, thoughts.id_thoughts, thoughts.content, thoughts.created_at, users.first_name, users.last_name FROM thoughts JOIN users on thoughts.author = users.id_users WHERE thoughts.id_thoughts = %(t_id)s ORDER BY created_at DESC;"
    data = {
        't_id': thought_id 
    }
    thought = mysql.query_db(query, data)
    if thought:
        thought = thought[0]

    mysql = connectToMySQL("dojo_thoughts")
    query = "SELECT thoughts_id_thoughts FROM liked_thoughts WHERE users_id_users = %(user_id)s"
    data = {
        'user_id': session['user_id']
    }
    results = mysql.query_db(query,data)
    liked_thought_ids = [result['thoughts_id_thoughts'] for result in results]
    
    mysql = connectToMySQL("dojo_thoughts")
    query = "SELECT users.first_name, users.last_name FROM liked_thoughts JOIN users on liked_thoughts.users_id_users = users.id_users WHERE thoughts_id_thoughts = %(t_id)s;"
    data = {
            't_id': thought_id
    }
    user_who_have_liked = mysql.query_db(query,data)

    return render_template("details.html", thought = thought, user_who_have_liked = user_who_have_liked, liked_thought_ids = liked_thought_ids)

@app.route('/like_thought/<thought_id>')
def like_thought(thought_id):
    mysql = connectToMySQL("dojo_thoughts")
    query = "INSERT INTO liked_thoughts (users_id_users, thoughts_id_thoughts) VALUES (%(user_id)s, %(thought_id)s);"
    data = {
        'user_id': session['user_id'],
        'thought_id': thought_id
    }
    mysql.query_db(query,data)
    return redirect(f"/thought_details/{thought_id}")

@app.route('/unlike_thought/<thought_id>')
def unlike_thought(thought_id):
    mysql = connectToMySQL("dojo_thoughts")
    query = "DELETE FROM liked_thoughts WHERE users_id_users = %(user_id)s AND thoughts_id_thoughts = %(thought_id)s;"
    data = {
        'user_id': session['user_id'],
        'thought_id': thought_id
    }
    mysql.query_db(query, data)
    return redirect(f"/thought_details/{thought_id}")

@app.route('/logout')
def logout():
    session.clear()
    flash("You have successfully logged yourself out")
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
from flask import Flask, render_template, request, redirect, url_for, flash
import re  

app = Flask(__name__)
app.secret_key = '2b89f736d3279b1b3d2c89d4f1c7bdf2'  

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if len(username) < 4:
            flash('Username must be at least 4 characters long.', 'error')
            return redirect(url_for('signup'))

        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'error')
            return redirect(url_for('signup'))
        
       
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            flash('Password must include at least one special character.', 'error')
            return redirect(url_for('signup'))
        flash('Registration successful!', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

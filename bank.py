"""
Catamount Community Bank
Flask Routes

Warning: This app contains deliberate security vulnerabilities
Do not use in a production environment! It is provided for security
training purposes only!

"""
from datetime import datetime, timedelta
import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect, session
from config import display
from db import Db
from lessons.password_crack import hash_pw, authenticate, password_strength, password_generator

app = Flask(__name__, static_folder='instance/static')

app.config.from_object('config')
app.secret_key = 'SUPER-SECRET_KEY'


@app.route("/", methods=['GET', 'POST'])
def home():
    """ Bank home page - login and register"""
    return render_template('home.html',
                           title="Home Page",
                           heading="Home Page",
                           show=display)

@app.route("/login", methods=['GET', 'POST'])
def login():
    """Login the user. Input username and ensure no dups, and
     password meets strength requirements. """
    if request.method == 'POST':
        # get username and password
        username = request.form.get('username')
        password = request.form.get('password')
        pw_hash = hash_pw(password)
        now = datetime.now().isoformat()

        conn = None
        try:
            conn = Db.get_connection()
            cur = Db.execute_query(conn, "SELECT id, pw_hash, attempts, last_attempt \
                                   FROM account WHERE uname = ?", (username,))
            result = cur.fetchone()

            if result:
                acct_id, stored_hash, attempts, last_attempt = result

                # check if account is locked
                if attempts >=2:
                    # see if 1 minute have passed
                    current_time = datetime.now()
                    last_attempt_fixed = datetime.fromisoformat(last_attempt)
                    time_diff = current_time - last_attempt_fixed

                    if time_diff >= timedelta(minutes=1):
                        cur = Db.execute_query(conn, "UPDATE account SET attempts = 0 \
                                                WHERE id = ?", (acct_id,))
                    else:
                        flash("Too many failed attempts. Please wait a minutes before \
                              trying again.", 'alert-warning')
                        return redirect(url_for('login'))

                # aunthenticate password
                if authenticate(stored_hash, password):
                    session['user_id'] = acct_id
                    now = datetime.now().isoformat()
                    cur = Db.execute_query(conn, "UPDATE account SET last_login = ?, \
                                           attempts = 0 WHERE id = ?", (now, acct_id))
                    return redirect(url_for('login_success'))
                else:
                    # update attempt for bad password attempt
                    now = datetime.now().isoformat()
                    cur = Db.execute_query(conn, "UPDATE account SET attempts = attempts + 1, \
                                            last_attempt = ? WHERE uname = ?", (now, username,))
                    flash("Invalid username or password!", 'alert-danger')
                    return redirect(url_for('login'))
            # No such username
            flash("Invalid username or password!", 'alert-danger')

        except Exception as e:
            flash("Something went wrong during login.", 'alert-danger')
        finally:
            if conn:
                conn.close()

    return render_template('login.html',
                           title="Secure Login",
                           heading="Secure Login")

@app.route("/login_success", methods=['GET', ])
def login_success():
    """Set up session id and allow user to get to main home page."""
    user_id = session.get('user_id')

    # check if logged in
    if not user_id:
        flash("You must log in first!", 'alert-danger')
        return redirect(url_for('login'))

    flash("Welcome! You have logged in!", 'alert-success')

    # update attempts back to 0
    try:
        conn = Db.get_connection()
        cur = Db.execute_query(conn, "UPDATE account SET attempts = 0 WHERE id = ?", (user_id,))

    except Exception as e:
        flash("Something went wrong during login.", 'alert-danger')
    finally:
        if conn:
            conn.close()
    return render_template('home_menu.html',
                           title="Menu",
                           heading="Menu")

@app.route('/logout')
def logout():
    """Log user out of the system."""
    session.clear()
    flash("You’ve been logged out.", 'alert-info')
    return redirect(url_for('login'))

# create table if not already made
connect = sqlite3.connect('instance/var/db/database.db')
connect.execute(
    'CREATE TABLE IF NOT EXISTS account ( id integer PRIMARY KEY, \
    uname text NOT NULL, pw_hash text NOT NULL, created_at datetime NOT NULL, \
    last_login datetime NOT NULL, accounting integer NOT NULL, engineering \
     integer NOT NULL, time integer NOT NULL, reports integer NOT NULL, \
    attempts integer NOT NULL, last_attempt datetime NOT NULL)'
)
connect.close()

@app.route("/register", methods=['GET', 'POST'])
def register():
    """Register the user. Ensure no dups in username, password meet
     strength requirments. Allows generated password. """
    generated_password = None

    if request.method == 'GET' and request.args.get('gen_pass'):
        generated_password = password_generator()

    if request.method == 'POST':
        # get username and password
        username = request.form.get('username')
        password = request.form.get('password')

        # check password strength
        if not password_strength(password):
            flash("Need to meet password strength requirements! (between 8-25 characters, at \
                  least one number, one upper and one lower case, and a special character)",\
                    'alert-danger')
            return redirect(url_for('register'))
        pw_hash = hash_pw(password)

        now = datetime.now().isoformat()
        conn = None

        # PUT INTO DB
        try:
            conn = Db.get_connection()

            # ensure username not already taken
            cur = Db.execute_query(conn, "SELECT * FROM account WHERE uname = ?", (username,))
            existing = cur.fetchone()
            if existing:
                flash("Username already taken! Please choose another one.", 'alert-danger')
                return redirect(url_for('register'))
            cur = Db.execute_query(conn, "INSERT INTO account (uname, pw_hash, created_at, \
                                   last_login, accounting, engineering, time, reports, attempts, \
                                    last_attempt) VALUES (?,?,?,?,?,?,?,?,?,?)",
                                    (username, pw_hash, now, now, 0, 0, 1, 0, 0, now))

            flash("Account created successfully! Please log in.", 'alert-success')
            return redirect(url_for('login'))

        except sqlite3.IntegrityError:
            flash("Username already exists. Try another.", 'alert-danger')
        except Exception as e:
            print("EXCEPTION IN REGISTER:", e)
            flash("Something went wrong. Try again.", 'alert-danger')
        finally:
            if conn:
                conn.close()

    return render_template('register.html',
                           title="Create Account",
                           heading="Create Account",
                           generated_password=generated_password)

@app.route("/home_menu", methods=['GET', 'POST'])
def menu():
    """show menu to the user. Can go to accounting, reports, time, and 
     engineering"""
    user_id = session.get('user_id')

    # ensure user is logged in
    if not user_id:
        flash("You must log in first!", 'alert-danger')
        return redirect(url_for('login'))
    return render_template('home_menu.html',
                           title="Menu",
                           heading="Menu")

@app.route("/accounting", methods=['GET', ])
def accounting_access():
    """show accounting access successful to the user. """
    user_id = session.get('user_id')

    # ensure user is logged in
    if not user_id:
        flash("You must log in first!", 'alert-danger')
        return redirect(url_for('login'))

    conn = None
    try:
        conn = Db.get_connection()
        cur = Db.execute_query(conn, "SELECT accounting FROM account WHERE id = ?", (user_id,))
        result = cur.fetchone()

        # Check access
        if result:
            access = result[0] if result else None
            if access == 0:
                flash("You do not have access to the Accounting page.", 'alert-danger')
                return redirect(url_for('menu'))
    except Exception as e:
        flash("Something went wrong.", 'alert-danger')
        print(e)
    finally:
        if conn:
            conn.close()
    return render_template('accounting.html',
                           title="Accounting",
                           heading="Accounting")

@app.route("/engineering", methods=['GET', ])
def engineering():
    """show engineering document access success to the user."""
    user_id = session.get('user_id')

    # ensure logged into the system
    if not user_id:
        flash("You must log in first!", 'alert-danger')
        return redirect(url_for('login'))

    conn = None
    try:
        conn = Db.get_connection()
        cur = Db.execute_query(conn, "SELECT engineering FROM account WHERE id = ?", (user_id,))
        result = cur.fetchone()

        # check access
        if result:
            access = result[0] if result else None
            if access == 0:
                flash("You do not have access to the Engineering Documents page.", 'alert-danger')
                return redirect(url_for('menu'))
    except Exception as e:
        flash("Something went wrong.", 'alert-danger')
        print(e)
    finally:
        if conn:
            conn.close()
    return render_template('engineering.html',
                           title="Engineering Documents",
                           heading="Engineering Documents")

@app.route("/time", methods=['GET', ])
def time():
    """show time reporting access success to the user."""
    user_id = session.get('user_id')

    # ensure user is logged in
    if not user_id:
        flash("You must log in first!", 'alert-danger')
        return redirect(url_for('login'))

    conn = None
    try:
        conn = Db.get_connection()
        cur = Db.execute_query(conn, "SELECT time FROM account WHERE id = ?", (user_id,))
        result = cur.fetchone()

        # check for access
        if result:
            access = result[0] if result else None
            if access == 0:
                flash("You do not have access to the Time Reporting page.", 'alert-danger')
                return redirect(url_for('menu'))
    except Exception as e:
        flash("Something went wrong during login.", 'alert-danger')
    finally:
        if conn:
            conn.close()
    return render_template('time.html',
                           title="Time Reporting",
                           heading="Time Reporting")

@app.route("/reports", methods=['GET', ])
def reports():
    """show report access success to the user."""
    user_id = session.get('user_id')

    # ensure user logged in
    if not user_id:
        flash("You must log in first!", 'alert-danger')
        return redirect(url_for('login'))

    conn = None
    try:
        conn = Db.get_connection()
        cur = Db.execute_query(conn, "SELECT reports FROM account WHERE id = ?", (user_id,))
        result = cur.fetchone()

        # check access
        if result:
            access = result[0] if result else None
            if access == 0:
                flash("You do not have access to the Reports page.", 'alert-danger')
                return redirect(url_for('menu'))
    except Exception as e:
        flash("Something went wrong during login.", 'alert-danger')
        print(e)
    finally:
        if conn:
            conn.close()
    return render_template('reports.html',
                           title="Reports",
                           heading="Reports")

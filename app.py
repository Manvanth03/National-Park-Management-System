from flask import Flask, render_template, request, redirect, url_for ,flash
import MySQLdb
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database connection
def get_db_connection():
    return MySQLdb.connect(host="localhost", user="root", passwd="", db="national_park_")

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email

# Load user for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)  # Use DictCursor to get results as dictionaries

    cursor.execute("SELECT * FROM Users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    if user:
        return User(id=user['id'], username=user['username'], email=user['email'])
    return None

# Home page (only accessible to logged-in users)
@app.route('/')
@login_required
def home():
    return render_template('home.html')

# Signup route (POST for creating a new user)
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    conn = get_db_connection()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)  # Use DictCursor to get results as dictionaries

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users WHERE username = %s OR email = %s", (username, email))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('Username or Email already exists', 'danger')
            return render_template('signup.html')

        # Insert the new user into the database (storing password as plain text, NOT recommended in production)
        cursor.execute("INSERT INTO Users (username, password, email) VALUES (%s, %s, %s)",
                       (username, password, email))
        conn.commit()

        flash('Signup successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

# Login route (POST for logging in)
@app.route('/login', methods=['GET', 'POST'])
def login():
    conn = get_db_connection()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)  # Use DictCursor to get results as dictionaries

    if request.method == 'POST':
        username_or_email = request.form['username_or_email']
        password = request.form['password']

        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM Users WHERE username = %s OR email = %s", (username_or_email, username_or_email))
        user = cursor.fetchone()

        if user and user['password'] == password:  # Check password in plain text
            logged_user = User(id=user['id'], username=user['username'], email=user['email'])
            login_user(logged_user)
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')

    return render_template('login.html')

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# @app.route('/')
# def home():
#     return render_template('home.html')



#Park Table
@app.route('/park', methods=['GET', 'POST'])
def park():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch parks from the database
    search_query = request.args.get('search', '')  # Handle search input
    if search_query:
        cursor.execute("SELECT * FROM Park WHERE name LIKE %s", ('%' + search_query + '%',))
    else:
        cursor.execute("SELECT * FROM Park")

    parks = cursor.fetchall()
    conn.close()

    return render_template('park.html', parks=parks, search_query=search_query)

@app.route('/add_park', methods=['GET', 'POST'])
def add_park():
    if request.method == 'POST':
        park_id = request.form['park_id']
        name = request.form['name']
        location = request.form['location']
        established_year = request.form['established_year']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Park (park_id, name, location, established_year) VALUES (%s, %s, %s, %s)",
            (park_id, name, location, established_year),
        )
        conn.commit()
        conn.close()
        return redirect(url_for('park'))
    return render_template('add_park.html')

@app.route('/delete_park/<park_id>', methods=['POST'])
def delete_park(park_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Park WHERE park_id = %s", (park_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('park'))
    
#Animal Table
@app.route('/animals')
def animals():
    conn = get_db_connection()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM Animals")
    animals = cursor.fetchall()
    print("Fetched animals:", animals)  # Debug: Print fetched data
    return render_template('animals.html', animals=animals)


@app.route('/add_animal', methods=['GET', 'POST'])
def add_animal():
    if request.method == 'POST':
        # Get form data
        animal_id = request.form['animal_id']
        name = request.form['name']
        species = request.form['species']
        park_id = request.form['park_id']
        
        # Insert the new animal into the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO Animals (animal_id, name, species, park_id)
            VALUES (%s, %s, %s, %s)
        ''', (animal_id, name, species, park_id))
        conn.commit()
        cursor.close()
        conn.close()
        
        return redirect(url_for('animals'))  # Redirect to the animals page after adding an animal
    
    else:
        # Fetch all parks for the dropdown
        conn = get_db_connection()
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Park')
        parks = cursor.fetchall()
        cursor.close()
        conn.close()

        return render_template('add_animal.html', parks=parks)


@app.route('/delete_animal', methods=['POST'])
def delete_animal():
    conn = get_db_connection()
    cursor = conn.cursor()
    animal_id = request.form['animal_id']
    cursor.execute("DELETE FROM Animals WHERE animal_id = %s", (animal_id,))
    conn.commit()
    return redirect('/animals')

#Visitor Table
@app.route('/visitors')
def visitors():
    conn = get_db_connection()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM Visitors')
    visitors = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('visitors.html', visitors=visitors)

@app.route('/add_visitors', methods=['GET', 'POST'])
def add_visitor():
    if request.method == 'POST':
        # Get form data
        visitor_id = request.form['visitor_id']
        name = request.form['name']
        visit_date = request.form['visit_date']
        park_id = request.form['park_id']

        # Simple validation
        if not visitor_id or not name or not visit_date or not park_id:
            # If any field is empty, return an error message
            return render_template('add_visitors.html', error="All fields are required.")
        
        try:
            # Insert the new visitor into the database
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO Visitors (visitor_id, name, visit_date, park_id)
                VALUES (%s, %s, %s, %s)
            ''', (visitor_id, name, visit_date, park_id))
            conn.commit()
            cursor.close()
            conn.close()

            # Redirect to the visitors page after adding a visitor
            return redirect(url_for('visitors'))  

        except Exception as e:
            # Handle any errors that occur during the database operation
            return render_template('add_visitors.html', error=f"Error: {e}")
    
    else:
        # Fetch all parks for the dropdown
        conn = get_db_connection()
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Park')
        parks = cursor.fetchall()
        cursor.close()
        conn.close()

        # Render the add visitor form
        return render_template('add_visitors.html', parks=parks)

@app.route('/delete_visitor/<visitor_id>', methods=['GET'])
def delete_visitor(visitor_id):
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Delete the visitor with the specified visitor_id
    try:
        cursor.execute('''
            DELETE FROM Visitors WHERE visitor_id = %s
        ''', (visitor_id,))
        conn.commit()  # Commit the transaction
        cursor.close()
        conn.close()

        # Redirect back to the visitors page after deletion
        return redirect(url_for('visitors'))  # Make sure 'view_visitors' is defined

    except Exception as e:
        # Handle errors, e.g., visitor_id not found or database issues
        return f"Error: {str(e)}", 500


#Staff Table
@app.route('/staff', methods=['GET', 'POST'])
def staff():
    conn = get_db_connection()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    
    if request.method == 'POST':  # Handle search functionality
        search_name = request.form['search']
        cursor.execute('SELECT * FROM Staff WHERE name LIKE %s', ('%' + search_name + '%',))
    else:
        cursor.execute('SELECT * FROM Staff')
    
    staff_members = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('staff.html', staff_members=staff_members)

# Route to add a new staff member
@app.route('/add_staff', methods=['GET', 'POST'])
def add_staff():
    if request.method == 'POST':
        staff_id = request.form['staff_id']
        name = request.form['name']
        role = request.form['role']
        park_id = request.form['park_id']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO Staff (staff_id, name, role, park_id)
            VALUES (%s, %s, %s, %s)
        ''', (staff_id, name, role, park_id))
        conn.commit()
        cursor.close()
        conn.close()
        
        return redirect(url_for('staff'))  # Redirect to staff page
    
    else:
        # Fetch all parks for the dropdown
        conn = get_db_connection()
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Park')
        parks = cursor.fetchall()
        cursor.close()
        conn.close()

        return render_template('add_staff.html', parks=parks)

# Route to delete a staff member
@app.route('/delete_staff/<staff_id>', methods=['POST'])
def delete_staff(staff_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Staff WHERE staff_id = %s', (staff_id,))
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect(url_for('staff'))  # Redirect to staff page


#Conservation table
@app.route('/conservation', methods=['GET', 'POST'])
def conservation():
    conn = get_db_connection()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    
    if request.method == 'POST':  # Search functionality
        search_value = request.form['search']
        cursor.execute('SELECT * FROM Conservation WHERE program_name LIKE %s', ('%' + search_value + '%',))
    else:
        cursor.execute('SELECT * FROM Conservation')
    
    conservation_programs = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('conservation.html', conservation_programs=conservation_programs)

# Route to add a new conservation program
@app.route('/add_conservation', methods=['GET', 'POST'])
def add_conservation():
    if request.method == 'POST':
        # Get form data
        conservation_id = request.form['conservation_id']
        program_name = request.form['program_name']
        start_date = request.form['start_date']
        end_date = request.form.get('end_date')  # Retrieve the optional end_date from the form
        park_id = request.form['park_id']
        
        # Insert into the Conservation table, including the end_date
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO Conservation (conservation_id, program_name, start_date, end_date, park_id)
            VALUES (%s, %s, %s, %s, %s)
        ''', (conservation_id, program_name, start_date, end_date, park_id))
        conn.commit()
        cursor.close()
        conn.close()
        
        return redirect(url_for('conservation'))  # Redirect to the conservation programs page
    
    # Fetch parks for dropdown
    conn = get_db_connection()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM Park')
    parks = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('add_conservation.html', parks=parks)


# Route to delete a conservation program
@app.route('/delete_conservation/<conservation_id>', methods=['POST'])
def delete_conservation(conservation_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Conservation WHERE conservation_id = %s', (conservation_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('conservation'))

#Conservation_view
@app.route('/conservation_view', methods=['GET'])
def conservation_view():
    conn = get_db_connection()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)

    # Fetch data from conservation_status_view
    cursor.execute('SELECT * FROM conservation_status_view')
    conservation_view_data = cursor.fetchall()
    
    # Debugging: Print fetched data in console
    print(conservation_view_data)

    # Close the connection
    cursor.close()
    conn.close()

    # Render the template with the fetched data
    return render_template('conservation_view.html', conservation_view=conservation_view_data)



if __name__ == '__main__':
    app.run(debug=True)

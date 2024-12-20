from flask import Flask, render_template, request, redirect, url_for
import MySQLdb

app = Flask(__name__)

# Database connection
def get_db_connection():
    return MySQLdb.connect(host="localhost", user="root", passwd="", db="national_park_")


@app.route('/')
def home():
    return render_template('home.html')



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



@app.route('/conservation')
def conservation():
    return render_template('conservation.html')


@app.route('/staff')
def staff():
    return render_template('staff.html')

if __name__ == '__main__':
    app.run(debug=True)

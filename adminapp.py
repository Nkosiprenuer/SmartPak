import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Route to display captured data
@app.route('/admin')
def admin_panel():
    conn = sqlite3.connect('plates.db')
    c = conn.cursor()
    c.execute("SELECT * FROM plates ORDER BY capture_date DESC, capture_time DESC")
    data = c.fetchall()
    conn.close()
    return render_template('admin_panel.html', data=data)

# Route to view details of a captured plate
@app.route('/view_plate', methods=['POST'])
def view_plate():
    plate_id = request.form['plate_id']
    conn = sqlite3.connect('plates.db')
    c = conn.cursor()
    c.execute("SELECT * FROM plates WHERE id=?", (plate_id,))
    plate_data = c.fetchone()
    conn.close()
    return render_template('view_plate.html', plate_data=plate_data)

# Route to confirm deletion of a captured plate
@app.route('/confirm_delete', methods=['POST'])
def confirm_delete():
    plate_id = request.form['plate_id']
    conn = sqlite3.connect('plates.db')
    c = conn.cursor()
    c.execute("DELETE FROM plates WHERE id=?", (plate_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_panel'))

# Route to show delete confirmation page
@app.route('/delete_plate', methods=['POST'])
def delete_plate():
    plate_id = request.form['plate_id']
    conn = sqlite3.connect('plates.db')
    c = conn.cursor()
    c.execute("SELECT * FROM plates WHERE id=?", (plate_id,))
    plate_data = c.fetchone()
    conn.close()
    return render_template('delete_plate.html', plate_data=plate_data)

# Route to show modify form
@app.route('/modify_plate', methods=['POST'])
def modify_plate():
    plate_id = request.form['plate_id']
    conn = sqlite3.connect('plates.db')
    c = conn.cursor()
    c.execute("SELECT * FROM plates WHERE id=?", (plate_id,))
    plate_data = c.fetchone()
    conn.close()
    return render_template('modify_plate.html', plate_data=plate_data)

# Route to confirm modification of a captured plate
@app.route('/confirm_modify', methods=['POST'])
def confirm_modify():
    plate_id = request.form['plate_id']
    new_plate_text = request.form['plate_text']  # Example, assuming there's a text input for plate text
    # Implement logic to modify plate details in the database based on the plate ID
    conn = sqlite3.connect('plates.db')
    c = conn.cursor()
    c.execute("UPDATE plates SET plate_text=? WHERE id=?", (new_plate_text, plate_id))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_panel'))

# Route to track a specific license plate text
@app.route('/track_plate', methods=['GET', 'POST'])
def track_plate():
    if request.method == 'POST':
        plate_text = request.form['plate_text']
        # Retrieve plate information from the database based on the plate text
        conn = sqlite3.connect('plates.db')
        c = conn.cursor()
        c.execute("SELECT * FROM plates WHERE plate_text=?", (plate_text,))
        plate_data = c.fetchall()
        conn.close()
        return render_template('track_plate.html', plate_data=plate_data)
    return render_template('track_plate.html')

if __name__ == '__main__':
    app.run(debug=True)

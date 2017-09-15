import sqlite3
from flask import Flask, render_template, g, request, redirect, url_for
from twilio.twiml.messaging_response import MessagingResponse

# INSERT INTO locations(latitude, longitude, dt) VALUES (-26.004363, 133.195111,  '2017-08-01 10:00:00')

app = Flask(__name__)
app.config['DEBUG'] = True
DATABASE = 'map.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    return render_template('index.html')
    
@app.route('/map/')
def map():
    c = get_db().cursor()
    c.execute('SELECT * FROM locations')
    sql_locations = c.fetchall()
    sql_locations = sorted(sql_locations, key=(lambda el: el[3]))
    locations = [{
        'lat': loc[1],
        'lng': loc[2],
        'dt': loc[3],
    } for loc in sql_locations]
    return render_template('map.html', locations=locations)

def add_latlong(latitude, longitude, dt_string):
    c = get_db().cursor()
    latitude, longitude = float(latitude), float(longitude)
    c.execute("INSERT INTO locations(latitude, longitude, dt) VALUES (?, ?, ?)", [latitude, longitude, dt_string])
    
def sms_latlong(latitude, longitude):
    from datetime import datetime as dt
    ts = dt.now().isoformat()[:16]
    try:
        add_latlong(latitude, longitude, ts)
    except ValueError:
        resp = MessagingResponse()
        resp.message("Received ({}, {})\nInvalid input.".format(latitude, longitude))
        return str(resp)
    else:
        resp = MessagingResponse()
        resp.message("Received: {}\nSuccessfully processed.".format(body))
        #return str(resp)
    
@app.route("/sms/", methods=['GET', 'POST'])
def sms_reply():
    """Parse incoming SMS"""
    print(request.method)
    
    if request.method == 'POST':
        body = request.values.get('Body', None)
        print(body)
        latitude, longitude = body.split(',')
        print(latitude, longitude)
        sms_latlong(latitude, longitude)  
    else:
        return "Used by Twilio SMS service"
        
@app.route("/sms/<latitude>/<longitude>/", methods=['GET'])
def sms_test_reply(latitude, longitude):
    """Test parsing incoming SMS"""
    result = sms_latlong(latitude, longitude)
    if result:
        return result
    return "Test fired succesfully"
    
@app.route('/locations/')
def locations():
    c = get_db().cursor()
    c.execute('SELECT * FROM locations')
    sql_locations = c.fetchall()
    # locations_str = ["<tr> <td>{}</td> <td>{}</td> <td>{}</td> </tr>".format(*loc[1:]) for loc in sql_locations]
    # return """
    # <table style="width:100%">
        # <tr>
            # <th>Latitude</th>
            # <th>Longitude</th> 
            # <th>Datetime</th>
        # </tr>
        # {}
    # </table>
    # """.format(''.join(locations_str))
    return render_template('locations.html', locations=sql_locations)

@app.route('/locations/<int:id>/delete/', methods=['POST'])
def location_delete(id):
    c = get_db().cursor()
    c.execute("DELETE FROM locations WHERE id=?", [id])
    get_db().commit()
    return redirect(url_for('locations'))
    
@app.route('/locations/add/', methods=['GET', 'POST'])
def location_add():
    print("locations_add")
    if request.method == 'POST':
        # print(request.form['datetime'])
        try:
            add_latlong(request.form['latitude'], request.form['longitude'], request.form['datetime'])
        except ValueError:
            return "Invalid latitude and longitude"
        return redirect(url_for('locations'))
    else:
        return render_template('location_add.html')
        
if __name__ == "__main__":
    app.run(debug=True)

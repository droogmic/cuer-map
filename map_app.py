import sqlite3
from flask import Flask, render_template, g, request, redirect, url_for
from twilio.twiml.messaging_response import MessagingResponse

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

@app.before_first_request
def setup():
    c = get_db().cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS "Location" (
            "LocationID" INTEGER NOT NULL PRIMARY KEY,
            "DT" DATETIME,
            "Latitude" REAL,
            "Longitude" REAL,
            "Post" TEXT
        )
    ''')
    get_db().commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/map/')
def map():
    c = get_db().cursor()
    c.execute('SELECT * FROM Location')
    sql_locations = c.fetchall()
    sql_locations = sorted(sql_locations, key=(lambda el: el[1]))
    locations = [{
        'dt': loc[1],
        'lat': loc[2],
        'lng': loc[3],
        'txt': loc[4] if loc[4] else "",
    } for loc in sql_locations]
    if locations:
        last_update = locations[-1]['dt']
    else:
        last_update = "Never"
    return render_template(
        'map.html',
        locations=locations,
        last_update=last_update
    )

def add_latlong(dt_string, latitude, longitude, post):
    c = get_db().cursor()
    latitude, longitude = float(latitude), float(longitude)
    post = post.strip()
    if not post:
        post = None
    c.execute(
        "INSERT INTO Location(DT, Latitude, Longitude, Post) VALUES (?, ?, ?, ?)",
        [dt_string, latitude, longitude, post]
    )
    get_db().commit()
    print("add_latlong", dt_string, latitude, longitude)

def sms_latlong(latitude, longitude):
    from datetime import datetime as dt
    dt_str = dt.now().isoformat()[:16]
    try:
        add_latlong(dt_str, latitude, longitude)
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
        latitude, longitude, *post = body.split(',')
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
    c.execute('SELECT * FROM Location')
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
    c.execute("DELETE FROM Location WHERE LocationID=?", [id])
    get_db().commit()
    return redirect(url_for('locations'))

@app.route('/locations/add/', methods=['GET', 'POST'])
def location_add():
    print("locations_add")
    if request.method == 'POST':
        # print(request.form['datetime'])
        try:
            add_latlong(
                request.form['datetime'],
                request.form['latitude'],
                request.form['longitude'],
                request.form['text'],
            )
        except ValueError:
            return "Invalid latitude and longitude"
        return redirect(url_for('locations'))
    else:
        return render_template('location_add.html')

@app.route('/locations/generate/')
def location_generate():
    c = get_db().cursor()

    c.execute("INSERT INTO Location(DT, Latitude, Longitude) VALUES (?, ?, ?)", ['2017-08-01T08:00', -12.436298, 130.930217])
    c.execute("INSERT INTO Location(DT, Latitude, Longitude) VALUES (?, ?, ?)", ['2017-08-01T10:00', -13.396281, 131.270268])
    c.execute("INSERT INTO Location(DT, Latitude, Longitude) VALUES (?, ?, ?)", ['2017-08-01T13:00', -15.534933, 133.206675])
    c.execute("INSERT INTO Location(DT, Latitude, Longitude) VALUES (?, ?, ?)", ['2017-08-01T17:00', -17.199167, 133.470352])

    get_db().commit()
    return redirect(url_for('locations'))

if __name__ == "__main__":
    app.run(debug=True)

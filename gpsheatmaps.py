from flask import Flask, url_for
from flask import render_template, request
from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from zipfile import ZipFile
import time
from datetime import datetime

from heatmap import create_image
from utils import GpxFile

app = Flask(__name__)
app.config.from_object('settings')
db = SQLAlchemy(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + filename)
            if get_extension(filename) == 'zip':
                with ZipFile(file, 'r') as thezip:
                    for name in thezip.namelist():
                        save_ride_data(GpxFile(thezip.open(name)))
            elif get_extension(filename) == 'gpx':
                save_ride_data(GpxFile(file))
    return render_template('upload.html')


@app.route('/test', methods=['GET', 'POST'])
def test():
    timestamp = time.time()
    if request.method == 'GET':
        return render_template('test.html', timestamp=timestamp)
    else:
        spot_radius = request.form['spot_radius']
        dimming = request.form['dimming']
        points = eval(request.form['points'])
        image = create_image(points, 200, 200, spot_radius, dimming)
        image.save(app.root_path + "/static/img/test.png")
        return render_template('test.html',
                            spot_radius=spot_radius,
                            dimming=dimming,
                            points=points,
                            timestamp=timestamp)


class Ride(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    date = db.Column(db.DateTime)

    def __init__(self, name, date=None):
        self.name = name
        if date is None:
            date = datetime.utcnow()
        self.date = date

    def __repr__(self):
        return '<RIDE>(%s - %s)' % (self.name, self.date)


class Point(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime)
    elevation = db.Column(db.Float)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    ride_id = db.Column(db.Integer, db.ForeignKey('ride.id'))
    ride = db.relationship('Ride', backref=db.backref('points', lazy='dynamic'))

    def __init__(self, elevation, lat, lng, ride, time=None):
        if time is None:
            time = datetime.utcnow()
        self.time = time
        self.elevation = elevation
        self.lat = lat
        self.lng = lng
        self.ride = ride

    def __repr__(self):
        return '<Point>(%s, %s)' % (self.lat, self.lng)


def allowed_file(filename):
    return '.' in filename and \
           get_extension(filename) in app.config['ALLOWED_EXTENSIONS']


def get_extension(filename):
    return filename.rsplit('.', 1)[1]


def save_ride_data(gpxfile):
    ride = Ride(gpxfile.name, gpxfile.time)
    db.session.add(ride)
    for gpx_point in gpxfile.points:
        point = Point(gpx_point['ele'],
                    gpx_point['lat'],
                    gpx_point['lng'],
                    ride,
                    gpx_point['time'],)
        db.session.add(point)
db.session.commit()

if __name__ == '__main__':
    app.run(port=8080, debug=True)

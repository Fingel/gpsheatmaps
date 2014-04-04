from flask import Flask, url_for
from flask import render_template, request
import time

from heatmap import create_image

app = Flask(__name__)
app.config.from_object('local_settings')


@app.route('/')
def index():
    return render_template('index.html')


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

if __name__ == '__main__':
    app.run(port=8080, debug=True)

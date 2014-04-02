from flask import Flask
from flask import render_template

from heatmap import HeatMapPoint, create_image

app = Flask(__name__)


@app.route('/')
def index():
    h = HeatMapPoint(30, 30)
    create_image([[h, ], ], 100, 100)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(port=8080, debug=True)

from flask import Flask, render_template, request, jsonify
import os
import requests

app = Flask(__name__)


API_KEY = os.getenv('NASA_API_KEY', 'DEMO_KEY')


def get_apod(date=None):
	url = 'https://api.nasa.gov/planetary/apod'
	params = {'api_key': API_KEY}
	if date:
		params['date'] = date
	resp = requests.get(url, params=params, timeout=10)
	resp.raise_for_status()
	return resp.json()


def get_mars_latest(rover='curiosity'):
	url = f'https://api.nasa.gov/mars-photos/api/v1/rovers/{rover}/latest_photos'
	params = {'api_key': API_KEY}
	resp = requests.get(url, params=params, timeout=10)
	resp.raise_for_status()
	data = resp.json()
	photos = data.get('latest_photos') or []
	return photos[:8]


@app.route('/')
def index():
	date = request.args.get('date')
	try:
		apod = get_apod(date)
	except Exception as e:
		apod = {'error': str(e)}

	try:
		mars_photos = get_mars_latest()
	except Exception as e:
		mars_photos = []

	return render_template('index.html', apod=apod, mars_photos=mars_photos, api_key=API_KEY)


@app.route('/api/apod')
def api_apod():
	date = request.args.get('date')
	try:
		data = get_apod(date)
		return jsonify(data)
	except requests.HTTPError as e:
		return jsonify({'error': str(e)}), 500
	except Exception as e:
		return jsonify({'error': str(e)}), 500


@app.route('/api/mars')
def api_mars():
	rover = request.args.get('rover', 'curiosity')
	try:
		photos = get_mars_latest(rover)
		return jsonify({'photos': photos})
	except Exception as e:
		return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
	
	app.run(debug=True, host='0.0.0.0', port=5000)


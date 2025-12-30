from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
  return jsonify({"status": "ok", "message": "TRAIN JOURNEY DISCOVERY API"})

@app.route('/api/health')
def health():
  return jsonify({"status": "healthy"})

if __name__ == '__main__':
  app.run(debug=True, port=5000)

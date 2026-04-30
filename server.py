from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import os
import portfolio

app = Flask(__name__, static_folder='landing')
CORS(app)

@app.route('/')
def index():
    return send_from_directory('landing', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('landing', path)

@app.route('/api/stats')
def api_stats():
    try:
        stats = portfolio.get_dashboard_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Asegurarnos de que la base de datos esté inicializada
    portfolio.init_db()
    print("Iniciando Dashboard de PolyBot en http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)

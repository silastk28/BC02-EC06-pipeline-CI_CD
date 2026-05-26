Python
import os
from flask import Flask, jsonify
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

app = Flask(__name__)

# Récupération de l'URI MongoDB via variable d'environnement (bonne pratique DevOps)
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/techcorp_db")

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
    db = client.get_default_database()
except Exception:
    client = None

@app.route('/')
def home():
    return jsonify({
        "status": "success",
        "message": "Bienvenue sur l'API TechCorp App v1.0"
    }), 200

@app.route('/health')
def health():
    """Route cruciale appelée par l'étape 'Tests E2E Staging' de votre Jenkinsfile"""
    health_status = {"status": "UP", "services": {"database": "DOWN"}}
    
    if client:
        try:
            # Vérifie si la base de données répond
            client.admin.command('ping')
            health_status["services"]["database"] = "UP"
            return jsonify(health_status), 200
        except ConnectionFailure:
            health_status["status"] = "DEGRADED"
            return jsonify(health_status), 500
            
    health_status["status"] = "DOWN"
    return jsonify(health_status), 500

if __name__ == '__main__':
    # Écoute obligatoire sur le port 5000 configuré dans votre curl et docker
    app.run(host='0.0.0.0', port=5000)
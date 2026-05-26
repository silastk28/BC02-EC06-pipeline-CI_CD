# Utilisation d'une version Python alpine stable et légère pour minimiser les failles Trivy
FROM python:3.10-alpine

# Définition du dossier de travail
WORKDIR /app

# Installation des dépendances système légères si nécessaire
RUN apk add --no-cache curl

# Copie et installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du reste du code source applicatif
COPY app.py .

# Exposition du port interne de l'application
EXPOSE 5000

# Lancement de l'application
CMD ["python", "app.py"]
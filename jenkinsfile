pipeline {
    agent any

    // Variables d'environnement — aucun secret en clair
    environment {
        IMAGE_NAME    = 'techcorp-app'
        IMAGE_TAG     = "${BUILD_NUMBER}"
        REGISTRY      = 'registry.internal.techcorp.fr'
        STAGING_HOST  = '10.0.30.10'
        PROD_HOST     = '10.0.40.10'
        // Secrets gérés par Jenkins Credentials Store
        REGISTRY_CREDS = credentials('registry-credentials')
        SONAR_TOKEN    = credentials('sonarqube-token')
    }

    stages {

        // ─── ÉTAPE 1 : Récupération du code ───────────────────
        stage('Checkout') {
            steps {
                echo 'Récupération du code depuis GitHub...'
                checkout scm
                bat 'wsl git log --oneline -5'
            }
        }

        // ─── ÉTAPE 2 : Build application ──────────────────────
        stage('Build') {
            steps {
                echo 'Construction de l application...'
                bat 'wsl pip install -r requirements.txt'
                bat 'wsl python -m py_compile app.py'
                echo 'Build réussi ✅'
            }
        }

        // ─── ÉTAPE 3 : Tests unitaires ────────────────────────
        stage('Tests unitaires') {
            steps {
                echo 'Lancement des tests unitaires...'
                bat 'wsl python -m pytest test_app.py -v --cov=app --cov-report=xml --cov-fail-under=80'
                // Condition de passage : couverture >= 80%
            }
            post {
                always {
                    echo 'Rapport de tests généré'
                }
            }
        }

        // ─── ÉTAPE 4 : Analyse qualité SonarQube ─────────────
        stage('Analyse qualité SonarQube') {
            steps {
                echo 'Analyse statique du code avec SonarQube...'
                bat 'wsl sonar-scanner -Dsonar.projectKey=techcorp-app -Dsonar.sources=. -Dsonar.host.url=http://sonar.internal.techcorp.fr -Dsonar.token=%SONAR_TOKEN%'
                // Condition de passage : pas de bug bloquant
            }
        }

        // ─── ÉTAPE 5 : Build image Docker ─────────────────────
        stage('Build image Docker') {
            steps {
                echo 'Construction de l image Docker...'
                bat 'wsl docker build -t %IMAGE_NAME%:%IMAGE_TAG% .'
                bat 'wsl docker tag %IMAGE_NAME%:%IMAGE_TAG% %IMAGE_NAME%:latest'
                echo 'Image Docker construite : techcorp-app:%IMAGE_TAG%'
            }
        }

        // ─── ÉTAPE 6 : Scan sécurité image Docker ─────────────
        stage('Scan sécurité Trivy') {
            steps {
                echo 'Scan de vulnérabilités DevSecOps avec Trivy...'
                // --exit-code 1 : le pipeline ÉCHOUE si vulnérabilité CRITICAL
                bat 'wsl trivy image --severity HIGH,CRITICAL --exit-code 1 --format table %IMAGE_NAME%:%IMAGE_TAG%'
                // Condition de passage : aucune vulnérabilité CRITICAL
            }
        }

        // ─── ÉTAPE 7 : Push vers le Registry ──────────────────
        stage('Push Registry') {
            steps {
                echo 'Publication de l image sur le registry...'
                bat 'wsl docker login %REGISTRY% -u %REGISTRY_CREDS_USR% -p %REGISTRY_CREDS_PSW%'
                bat 'wsl docker tag %IMAGE_NAME%:%IMAGE_TAG% %REGISTRY%/%IMAGE_NAME%:%IMAGE_TAG%'
                bat 'wsl docker push %REGISTRY%/%IMAGE_NAME%:%IMAGE_TAG%'
                echo 'Image publiée sur le registry ✅'
            }
        }

        // ─── ÉTAPE 8 : Déploiement Staging ────────────────────
        stage('Deploy Staging') {
            steps {
                echo 'Déploiement sur l environnement Staging...'
                bat 'wsl ssh -o StrictHostKeyChecking=no deploy@%STAGING_HOST% "docker pull %REGISTRY%/%IMAGE_NAME%:%IMAGE_TAG% && docker-compose up -d --scale web=2"'
                echo 'Staging déployé ✅ — Tests E2E en cours...'
            }
        }

        // ─── ÉTAPE 9 : Tests E2E sur Staging ──────────────────
        stage('Tests E2E Staging') {
            steps {
                echo 'Validation End-to-End sur Staging...'
                bat 'wsl curl -f http://%STAGING_HOST%:5000/health || exit 1'
                echo 'Tests E2E réussis ✅'
            }
        }

        // ─── ÉTAPE 10 : Déploiement Production (Manuel) ───────
        stage('Deploy Production') {
            when {
                // Déploiement production uniquement sur tag Git ou branche main
                anyOf {
                    branch 'main'
                    tag '*'
                }
            }
            input {
                message 'Déployer en production ?'
                ok 'Go — Déployer !'
                submitter 'tech-lead,devops-team'
            }
            steps {
                echo 'Déploiement en production — stratégie Rolling Update...'
                // Rolling update : mise à jour progressive sans interruption
                bat 'wsl ssh -o StrictHostKeyChecking=no deploy@%PROD_HOST% "docker pull %REGISTRY%/%IMAGE_NAME%:%IMAGE_TAG% && docker-compose up -d --scale web=2 --no-deps"'
                echo 'Production déployée ✅'
            }
        }
    }

    post {
        success {
            echo 'Pipeline complet réussi ! Version %IMAGE_TAG% déployée.'
        }
        failure {
            echo 'Pipeline échoué — rollback automatique...'
            bat 'wsl ssh deploy@%PROD_HOST% "docker-compose rollback"'
        }
        always {
            echo 'Nettoyage...'
            bat 'wsl docker system prune -f'
            bat 'wsl docker logout %REGISTRY%'
        }
    }
}

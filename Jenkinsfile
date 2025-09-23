pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                echo '🔨 Building Docker image...'
                sh 'docker build -t melbourne-app .'
            }
        }

        stage('Test') {
            steps {
                echo '✅ Running unit tests...'
                sh '''
                    docker run --rm melbourne-app pytest
                '''
            }
        }


        stage('Lint') {
            steps {
                echo '🧹 Checking code style...'
                sh 'pip install flake8 && flake8 app.py'
            }
        }

        stage('Deploy') {
            steps {
                echo '🚀 Deploying container...'
                sh 'docker run -d -p 8501:8501 --name melbourne-app melbourne-app || true'
            }
        }
    }
}


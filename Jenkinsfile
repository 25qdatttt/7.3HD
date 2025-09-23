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
                sh '''
                    docker run --rm melbourne-app flake8 .
                '''
            }
        }


        stage('Deploy') {
            steps {
                echo '🚀 Deploying application...'
                sh '''
                    docker run -d -p 8501:8501 --name melbourne-app melbourne-app
                '''
            }
        }

    }
}



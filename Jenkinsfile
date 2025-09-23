pipeline {
    agent any

    environment {
        IMAGE_NAME = "melbourne-app"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build') {
            steps {
                echo "🔨 Building Docker image..."
                sh 'docker build -t $IMAGE_NAME .'
            }
        }

        stage('Test') {
            steps {
                echo "✅ Running unit tests..."
                sh 'docker run --rm $IMAGE_NAME pytest'
            }
        }

        stage('Lint') {
            steps {
                echo "🧹 Checking code style..."
                sh 'docker run --rm $IMAGE_NAME flake8 .'
            }
        }

        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                echo "🚀 Deploying application..."
                // Ví dụ chạy container tại cổng 8501
                sh 'docker run -d --name melbourne-app -p 8501:8501 $IMAGE_NAME'
            }
        }
    }

    post {
        always {
            echo "Pipeline finished."
        }
        success {
            echo "✅ Build, Test, Lint, Deploy all passed!"
        }
        failure {
            echo "❌ Pipeline failed. Check logs."
        }
    }
}

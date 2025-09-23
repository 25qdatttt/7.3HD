pipeline {
    agent any

    environment {
        IMAGE_NAME = "melbourne-app"
        CONTAINER_NAME = "melbourne-app-container"
    }

    stages {
        stage('Build') {
            steps {
                echo "🔨 Building Docker image..."
                sh "docker build -t ${IMAGE_NAME} ."
            }
        }

        stage('Test') {
            steps {
                echo "✅ Running automated tests..."
                sh "docker run --rm ${IMAGE_NAME} pytest -q"
            }
        }

        stage('Code Quality') {
            steps {
                echo "🧹 Running code quality analysis..."
                sh "docker run --rm ${IMAGE_NAME} flake8 . || true"
            }
        }

        stage('Security') {
            steps {
                echo "🔒 Running security analysis..."
                sh "docker run --rm ${IMAGE_NAME} bandit -r . || true"
                sh "docker run --rm ${IMAGE_NAME} safety check || true"
            }
        }

        stage('Deploy') {
            steps {
                echo "🚀 Deploying to staging environment..."
                sh """
                    docker stop ${CONTAINER_NAME} || true
                    docker rm ${CONTAINER_NAME} || true
                    docker run -d --name ${CONTAINER_NAME} -p 8501:8501 ${IMAGE_NAME}
                """
            }
        }

        stage('Release') {
            steps {
                echo "📦 (Simulated) Releasing to production..."
                // In real projects: push to Docker Hub or AWS
                sh "echo 'Pushing ${IMAGE_NAME} to production registry (simulated)'"
            }
        }

        stage('Monitoring & Alerting') {
            steps {
                echo "📊 (Simulated) Monitoring production..."
                sh "echo 'Simulating monitoring and alerting with Prometheus/Datadog'"
            }
        }
    }
}

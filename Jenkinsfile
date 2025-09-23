pipeline {
    agent any

    environment {
        DOCKERHUB_USER = "your-dockerhub-username"
        IMAGE_NAME = "melbourne-app"
        VERSION = "v1"
    }

    stages {
        stage('Checkout') {
            steps {
                echo "Checking out source code..."
                checkout scm
            }
        }

        stage('Build') {
            steps {
                echo "Building Docker image..."
                sh '''
                    docker build -t ${IMAGE_NAME}:latest \
                                 -t docker.io/${DOCKERHUB_USER}/${IMAGE_NAME}:${VERSION} .
                '''
            }
        }

        stage('Test') {
            steps {
                echo "Running unit tests..."
                sh 'docker run --rm ${IMAGE_NAME}:latest pytest -v'
            }
        }

        stage('Integration Test') {
            steps {
                echo "Running mock integration test..."
                sh '''
                    # Run container in detached mode (staging port 8502)
                    docker stop test_app || true
                    docker rm test_app || true
                    docker run -d --name test_app -p 8502:8501 ${IMAGE_NAME}:latest streamlit run app.py

                    # Give it time to start
                    sleep 10

                    # Instead of real curl, just check logs (mock integration)
                    if docker logs test_app | grep -q "You can now view your Streamlit app"; then
                        echo "Integration test passed (logs OK)"
                        docker stop test_app
                        docker rm test_app
                    else
                        echo "Integration test failed (logs not found)"
                        docker stop test_app || true
                        docker rm test_app || true
                        exit 1
                    fi
                '''
            }
        }

        stage('Code Quality') {
            steps {
                echo "Running code quality checks..."
                sh 'docker run --rm ${IMAGE_NAME}:latest flake8 .'
            }
        }

        stage('Security') {
            steps {
                echo "Running security scan..."
                sh '''
                    docker run --rm aquasec/trivy:latest image --exit-code 0 ${IMAGE_NAME}:latest || true
                '''
            }
        }

        stage('Deploy') {
            steps {
                echo "Deploying to staging environment..."
                sh '''
                    docker stop staging_app || true
                    docker rm staging_app || true
                    docker run -d --name staging_app -p 8503:8501 ${IMAGE_NAME}:latest streamlit run app.py
                '''
            }
        }

        stage('Release') {
            steps {
                echo "Releasing to Docker Hub..."
                sh '''
                    echo "${DOCKERHUB_PASS}" | docker login -u "${DOCKERHUB_USER}" --password-stdin
                    docker push docker.io/${DOCKERHUB_USER}/${IMAGE_NAME}:${VERSION}
                '''
            }
        }

        stage('Monitoring and Alerting') {
            steps {
                echo "Mock monitoring app..."
                sh '''
                    # In reality use Prometheus/NewRelic, here we just mock
                    docker ps --filter "name=staging_app"
                    echo "CPU usage OK (mock)"
                    echo "Memory usage OK (mock)"
                '''
            }
        }
    }

    post {
        success {
            sh 'echo "Pipeline finished successfully at $(date)"'
        }
        failure {
            sh '''
                echo "Pipeline failed at $(date)"
                echo "Attempting rollback..."
                docker stop prod_app || true
                docker rm prod_app || true
                docker run -d --name prod_app -p 8504:8501 docker.io/${DOCKERHUB_USER}/${IMAGE_NAME}:stable streamlit run app.py || true
            '''
        }
    }
}

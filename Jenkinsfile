pipeline {
    agent any

    environment {
        IMAGE_NAME = "melbourne-app"
        DOCKERHUB_USER = "your-dockerhub-username"
    }

    stages {
        stage('Build') {
            steps {
                echo "Building Docker image..."
                sh '''
                    docker build -t ${IMAGE_NAME}:latest \
                                 -t docker.io/${DOCKERHUB_USER}/${IMAGE_NAME}:v1 .
                '''
            }
        }

        stage('Test') {
            steps {
                echo "Running unit and integration tests..."
                sh 'docker run --rm ${IMAGE_NAME}:latest pytest -v'
                sh '''
                    docker stop test_app || true
                    docker rm test_app || true
                    docker run -d --name test_app -P ${IMAGE_NAME}:latest streamlit run app.py
                    PORT=$(docker port test_app 8501/tcp | cut -d: -f2)
                    echo "Waiting for service on port $PORT..."
                    for i in {1..30}; do
                        if curl -s http://localhost:$PORT >/dev/null; then
                            echo "Integration test passed"
                            docker stop test_app
                            docker rm test_app
                            exit 0
                        fi
                        echo "Waiting... ($i)"
                        sleep 2
                    done
                    echo "Integration test failed"
                    docker logs test_app
                    docker stop test_app
                    docker rm test_app
                    exit 1
                '''
            }
        }

        stage('Code Quality') {
            steps {
                echo "Checking code quality..."
                sh '''
                    docker run --rm -v $(pwd):/app -w /app python:3.10-slim \
                        sh -c "pip install flake8 && flake8 --max-line-length=100 ."
                '''
            }
        }

        stage('Security') {
            steps {
                echo "Running security scan..."
                sh '''
                    docker run --rm -v $(pwd):/app -w /app python:3.10-slim \
                        sh -c "pip install bandit && bandit -r . || true"
                '''
            }
        }

        stage('Deploy') {
            steps {
                echo "Deploying to staging..."
                sh '''
                    docker stop staging_app || true
                    docker rm staging_app || true
                    docker run -d --name staging_app -p 8502:8501 ${IMAGE_NAME}:latest streamlit run app.py
                '''
            }
        }

        stage('Release') {
            steps {
                echo "Releasing to production..."
                sh '''
                    docker stop prod_app || true
                    docker rm prod_app || true
                    docker tag ${IMAGE_NAME}:latest docker.io/${DOCKERHUB_USER}/${IMAGE_NAME}:stable
                    docker push docker.io/${DOCKERHUB_USER}/${IMAGE_NAME}:stable
                    docker run -d --name prod_app -p 8503:8501 docker.io/${DOCKERHUB_USER}/${IMAGE_NAME}:stable streamlit run app.py
                '''
            }
        }

        stage('Monitoring and Alerting') {
            steps {
                echo "Simulating monitoring checks..."
                sh '''
                    docker ps
                    echo "Health check:"
                    curl -s http://localhost:8503 || true
                '''
            }
        }
    }

    post {
        success {
            sh 'echo "Pipeline finished successfully at $(date)"'
        }
        failure {
            sh 'echo "Pipeline failed at $(date)"'
            sh '''
                docker stop prod_app || true
                docker rm prod_app || true
                docker run -d --name prod_app -p 8503:8501 docker.io/${DOCKERHUB_USER}/${IMAGE_NAME}:stable streamlit run app.py || true
            '''
        }
    }
}

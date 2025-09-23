pipeline {
    agent any

    environment {
        IMAGE_NAME = "melbourne-app"
        DOCKERHUB_USER = "your-dockerhub-username"   // sửa thành DockerHub username thật
        VERSION = "v1"
    }

    stages {
        stage('Checkout') {
            steps {
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
                echo "Running unit and integration tests..."
                sh '''
                    # Unit tests
                    docker run --rm ${IMAGE_NAME}:latest pytest -v

                    # Cleanup any old container
                    docker stop test_app || true
                    docker rm test_app || true

                    # Run app for integration test
                    docker run -d --name test_app -p 8501:8501 ${IMAGE_NAME}:latest streamlit run app.py

                    echo "Waiting for Streamlit app..."
                    for i in {1..30}; do
                        if curl -s http://localhost:8501 >/dev/null; then
                            echo "Integration test passed"
                            docker stop test_app
                            docker rm test_app
                            exit 0
                        fi
                        echo "Still waiting... ($i)"
                        sleep 2
                    done

                    echo "Integration test failed"
                    docker logs test_app
                    docker stop test_app || true
                    docker rm test_app || true
                    exit 1
                '''
            }
        }

        stage('Code Quality') {
            steps {
                echo "Running code quality checks..."
                sh '''
                    docker run --rm ${IMAGE_NAME}:latest flake8 .
                '''
            }
        }

        stage('Security') {
            steps {
                echo "Running security scan..."
                sh '''
                    docker run --rm aquasec/trivy:latest image ${IMAGE_NAME}:latest || true
                '''
            }
        }

        stage('Deploy') {
            steps {
                echo "Deploying to staging environment..."
                sh '''
                    docker stop staging_app || true
                    docker rm staging_app || true
                    docker run -d --name staging_app -p 8502:8501 ${IMAGE_NAME}:latest streamlit run app.py
                '''
            }
        }

        stage('Release') {
            steps {
                echo "Pushing Docker image to DockerHub..."
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh '''
                        echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                        docker push docker.io/${DOCKERHUB_USER}/${IMAGE_NAME}:${VERSION}
                    '''
                }
            }
        }

        stage('Monitoring and Alerting') {
            steps {
                echo "Simulating monitoring..."
                sh '''
                    echo "Checking health of production service..."
                    curl -f http://localhost:8502 || echo "Warning: staging service may be down"
                '''
            }
        }
    }

    post {
        success {
            sh 'echo "Pipeline succeeded at $(date)"'
        }
        failure {
            sh '''
                echo "Pipeline failed at $(date)"
                echo "Attempting rollback..."
                docker stop prod_app || true
                docker rm prod_app || true
                docker run -d --name prod_app -p 8503:8501 docker.io/${DOCKERHUB_USER}/${IMAGE_NAME}:stable streamlit run app.py || true
            '''
        }
    }
}

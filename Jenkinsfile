pipeline {
    agent any

    environment {
        IMAGE_NAME = "melbourne-app"
        DOCKERHUB_CREDENTIALS = "dockerhub-pass"
        DOCKER_USER = "25qdatttt"   // Thay bằng username DockerHub của bạn
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
                sh """
                    docker build -t ${IMAGE_NAME}:latest \
                                 -t ${DOCKER_USER}/${IMAGE_NAME}:latest .
                """
            }
        }

        stage('Test') {
            steps {
                echo "Running unit tests..."
                sh "docker run --rm ${IMAGE_NAME}:latest pytest -v"
            }
        }

        stage('Integration Test') {
            steps {
                echo "Running integration test..."
                sh """
                    docker stop test_app || true
                    docker rm test_app || true
                    docker run -d --name test_app -p 8502:8501 ${IMAGE_NAME}:latest streamlit run app.py
                    sleep 10
                    if docker logs test_app | grep -q "You can now view your Streamlit app"; then
                        echo "Integration test passed"
                    else
                        echo "Integration test failed"
                        docker logs test_app
                        exit 1
                    fi
                    docker stop test_app
                    docker rm test_app
                """
            }
        }

        stage('Code Quality') {
            steps {
                echo "Running code quality checks..."
                sh "docker run --rm ${IMAGE_NAME}:latest flake8 . || true"
            }
        }

        stage('Security') {
            steps {
                echo "Running security scan with Trivy..."
                sh """
                    docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
                               -v /var/lib/docker:/var/lib/docker \
                               aquasec/trivy:latest image ${IMAGE_NAME}:latest || true
                """
            }
        }

        stage('Deploy') {
            steps {
                echo "Deploying to staging..."
                sh """
                    docker stop staging_app || true
                    docker rm staging_app || true
                    docker run -d --name staging_app -p 8503:8501 ${IMAGE_NAME}:latest streamlit run app.py
                """
            }
        }

        stage('Release') {
            steps {
                echo "Pushing image to DockerHub..."
                withCredentials([usernamePassword(credentialsId: "${DOCKERHUB_CREDENTIALS}",
                                                 usernameVariable: 'DOCKER_USER',
                                                 passwordVariable: 'DOCKER_PASS')]) {
                    sh """
                        echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                        docker push $DOCKER_USER/${IMAGE_NAME}:latest
                    """
                }
            }
        }
    }

    post {
        success {
            echo "Pipeline completed successfully at $(date)"
        }
        failure {
            echo "Pipeline failed at $(date)"
            echo "Rollback: starting stable image..."
            sh """
                docker stop prod_app || true
                docker rm prod_app || true
                docker run -d --name prod_app -p 8504:8501 ${DOCKER_USER}/${IMAGE_NAME}:stable streamlit run app.py || true
            """
        }
    }
}

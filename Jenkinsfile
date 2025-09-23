pipeline {
    agent any

    environment {
        IMAGE_NAME = "melbourne-app"
        DOCKERHUB_USER = "your-dockerhub-username"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build') {
            steps {
                echo 'Building Docker image...'
                sh """
                    docker build -t ${IMAGE_NAME}:latest \
                                 -t docker.io/${DOCKERHUB_USER}/${IMAGE_NAME}:${BUILD_NUMBER} .
                """
            }
        }

        stage('Test') {
            steps {
                echo 'Running unit and integration tests...'
                sh """
                    docker run --rm ${IMAGE_NAME}:latest pytest -v

                    # Stop and remove old test container if exists
                    docker stop test_app || true
                    docker rm test_app || true

                    # Run app with random port (-P)
                    CID=\$(docker run -d --name test_app -P ${IMAGE_NAME}:latest streamlit run app.py)
                    PORT=\$(docker port test_app 8501/tcp | cut -d: -f2)

                    echo "Waiting for Streamlit on port \$PORT..."
                    for i in {1..30}; do
                        if curl -s http://localhost:\$PORT >/dev/null; then
                            echo "Integration test passed"
                            docker stop test_app
                            docker rm test_app
                            exit 0
                        fi
                        sleep 2
                    done

                    echo "Integration test failed"
                    docker logs test_app
                    docker stop test_app || true
                    docker rm test_app || true
                    exit 1
                """
            }
        }

        stage('Code Quality') {
            steps {
                echo 'Checking code style...'
                sh "docker run --rm ${IMAGE_NAME}:latest flake8 ."
            }
        }

        stage('Security') {
            steps {
                echo 'Running security scan...'
                sh "docker run --rm aquasec/trivy:latest image ${IMAGE_NAME}:latest || true"
            }
        }

        stage('Deploy') {
            steps {
                echo 'Deploying to staging...'
                sh """
                    docker stop staging_app || true
                    docker rm staging_app || true
                    docker run -d --name staging_app -p 8502:8501 ${IMAGE_NAME}:latest streamlit run app.py
                """
            }
        }

        stage('Release') {
            steps {
                echo 'Releasing to production...'
                sh """
                    docker tag ${IMAGE_NAME}:latest docker.io/${DOCKERHUB_USER}/${IMAGE_NAME}:stable
                    docker push docker.io/${DOCKERHUB_USER}/${IMAGE_NAME}:${BUILD_NUMBER}
                    docker push docker.io/${DOCKERHUB_USER}/${IMAGE_NAME}:stable

                    docker stop prod_app || true
                    docker rm prod_app || true
                    docker run -d --name prod_app -p 8503:8501 ${IMAGE_NAME}:latest streamlit run app.py
                """
            }
        }

        stage('Monitoring and Alerting') {
            steps {
                echo 'Simulating monitoring...'
                sh 'echo "Monitoring metrics collected. No alerts triggered."'
            }
        }
    }

    post {
        success {
            echo "Pipeline succeeded at \$(date)"
        }
        failure {
            echo "Pipeline failed at \$(date)"
            echo "Attempting rollback..."
            sh """
                docker stop prod_app || true
                docker rm prod_app || true
                docker run -d --name prod_app -p 8503:8501 docker.io/${DOCKERHUB_USER}/${IMAGE_NAME}:stable streamlit run app.py || true
            """
        }
    }
}

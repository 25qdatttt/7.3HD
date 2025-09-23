pipeline {
    agent any

    environment {
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
                    docker stop test_app || true
                    docker rm test_app || true
                    docker run -d --name test_app -p 8502:8501 ${IMAGE_NAME}:latest streamlit run app.py
                    sleep 10
                    if docker logs test_app | grep -q "You can now view your Streamlit app"; then
                        echo "Integration test passed"
                        docker stop test_app
                        docker rm test_app
                    else
                        echo "Integration test failed"
                        exit 1
                    fi
                '''
            }
        }

        stage('Code Quality') {
            steps {
                echo "Running code quality checks..."
                sh 'docker run --rm ${IMAGE_NAME}:latest flake8 . || true'
            }
        }

        stage('Security') {
            steps {
                echo "Running security scan..."
                // scan filesystem instead of image to avoid docker.sock issue
                sh 'docker run --rm -v $(pwd):/project aquasec/trivy:latest fs /project || true'
            }
        }

        stage('Deploy') {
            steps {
                echo "Deploying to staging..."
                sh '''
                    docker stop staging_app || true
                    docker rm staging_app || true
                    docker run -d --name staging_app -p 8503:8501 ${IMAGE_NAME}:latest streamlit run app.py
                '''
            }
        }

        stage('Release') {
            steps {
                echo "Pushing to DockerHub..."
                withCredentials([usernamePassword(credentialsId: 'dockerhub-pass',
                                                 usernameVariable: 'DOCKERHUB_USER',
                                                 passwordVariable: 'DOCKERHUB_PASS')]) {
                    sh '''
                        echo "$DOCKERHUB_PASS" | docker login -u "$DOCKERHUB_USER" --password-stdin
                        docker push docker.io/$DOCKERHUB_USER/${IMAGE_NAME}:${VERSION}
                        docker tag ${IMAGE_NAME}:latest docker.io/$DOCKERHUB_USER/${IMAGE_NAME}:stable
                        docker push docker.io/$DOCKERHUB_USER/${IMAGE_NAME}:stable
                    '''
                }
            }
        }

        stage('Monitoring and Alerting') {
            steps {
                echo "Mock monitoring..."
                sh '''
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
            withCredentials([usernamePassword(credentialsId: 'dockerhub-pass',
                                             usernameVariable: 'DOCKERHUB_USER',
                                             passwordVariable: 'DOCKERHUB_PASS')]) {
                sh '''
                    echo "Pipeline failed at $(date)"
                    echo "Rollback: starting stable image..."
                    docker stop prod_app || true
                    docker rm prod_app || true
                    docker run -d --name prod_app -p 8504:8501 docker.io/$DOCKERHUB_USER/${IMAGE_NAME}:stable streamlit run app.py || true
                '''
            }
        }
    }
}

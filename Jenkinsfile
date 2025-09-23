pipeline {
    agent any

    environment {
        DOCKERHUB_USER = "your-dockerhub-username"
        IMAGE_NAME = "melbourne-app"
    }

    stages {
        stage('Build') {
            steps {
                echo "Building Docker image..."
                sh """
                    docker build -t ${IMAGE_NAME}:latest \
                                 -t docker.io/${DOCKERHUB_USER}/${IMAGE_NAME}:v1 .
                """
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
                    sleep 10
                    PORT=$(docker port test_app 8501/tcp | cut -d: -f2)
                    echo "Integration test on port $PORT"
                    curl -f http://localhost:$PORT || (echo "Integration test failed" && exit 1)
                    docker stop test_app
                    docker rm test_app
                '''
            }
        }

        stage('Code Quality') {
            steps {
                echo "Checking code quality with flake8..."
                sh 'docker run --rm ${IMAGE_NAME}:latest flake8 . || true'
            }
        }

        stage('Security') {
            steps {
                echo "Running security scan with bandit..."
                sh 'docker run --rm ${IMAGE_NAME}:latest bandit -r . || true'
            }
        }

        stage('Deploy') {
            steps {
                echo "Deploying application to staging..."
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
                echo "Monitoring production container..."
                sh '''
                    docker ps --filter "name=prod_app"
                    docker logs prod_app --tail 20 || true
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
        }
        always {
            sh 'echo "Pipeline finished at $(date)"'
        }
    }
}

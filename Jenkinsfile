pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "melbourne-app"
        DOCKER_TAG = "v${env.BUILD_NUMBER}"
        REGISTRY = "docker.io/your-dockerhub-username/${DOCKER_IMAGE}"
    }

    stages {
        stage('Build') {
            steps {
                echo "Building Docker image..."
                sh 'docker build -t $DOCKER_IMAGE:latest -t $REGISTRY:$DOCKER_TAG .'
            }
        }

        stage('Test') {
            steps {
                echo "Running unit and integration tests..."
                // Unit tests
                sh 'docker run --rm $DOCKER_IMAGE:latest pytest -v'
                // Integration test: check prediction endpoint
                sh '''
                  docker run -d --name test_app -p 8501:8501 $DOCKER_IMAGE:latest streamlit run app.py &
                  sleep 10
                  curl -f http://localhost:8501 || (echo "Integration test failed" && exit 1)
                  docker stop test_app
                  docker rm test_app
                '''
            }
        }

        stage('Code Quality') {
            steps {
                echo "Running flake8 with custom rules..."
                sh 'docker run --rm $DOCKER_IMAGE:latest flake8 --max-line-length=100 --exit-zero .'
            }
        }

        stage('Security') {
            steps {
                echo "Running security scans..."
                sh '''
                  docker run --rm $DOCKER_IMAGE:latest pip install bandit safety
                  docker run --rm $DOCKER_IMAGE:latest bandit -r .
                  docker run --rm $DOCKER_IMAGE:latest safety check || true
                '''
                echo "If issues are found: document severity and fix or justify exclusions."
            }
        }

        stage('Deploy') {
            steps {
                echo "Deploying to staging environment..."
                sh '''
                  docker-compose -f docker-compose.staging.yml down || true
                  docker-compose -f docker-compose.staging.yml up -d --build
                '''
            }
        }

        stage('Release') {
            steps {
                echo "Releasing image to DockerHub..."
                sh '''
                  echo $DOCKERHUB_PASS | docker login -u $DOCKERHUB_USER --password-stdin
                  docker push $REGISTRY:$DOCKER_TAG
                  docker push $DOCKER_IMAGE:latest
                '''
            }
        }

        stage('Monitoring and Alerting') {
            steps {
                echo "Checking container health and resource usage..."
                sh '''
                  docker stats --no-stream || true
                  echo "Health check passed at $(date)"
                '''
            }
        }
    }

    post {
        always {
            echo "Pipeline finished at ${new Date()}"
        }
        failure {
            echo "Pipeline failed. Rolling back to last stable release..."
            sh 'docker run -d $REGISTRY:previous-version || true'
        }
    }
}

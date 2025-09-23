pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "melbourne-app"
        REGISTRY = "docker.io/your-dockerhub-username/melbourne-app"
        DOCKER_TAG = "v7"
    }

    stages {
        stage('Build') {
            steps {
                echo "Building Docker image..."
                sh '''
                  docker build -t $DOCKER_IMAGE:latest -t $REGISTRY:$DOCKER_TAG .
                '''
            }
        }

        stage('Test') {
            steps {
                echo "Running unit and integration tests..."
                sh '''
                  # Run unit tests inside container
                  docker run --rm $DOCKER_IMAGE:latest pytest -v

                  # Integration test: stop/remove old container if exists
                  docker stop test_app || true
                  docker rm test_app || true

                  docker run -d --name test_app -p 8501:8501 $DOCKER_IMAGE:latest streamlit run app.py
                  sleep 10

                  # Check if service is running
                  curl -f http://localhost:8501 || (echo "Integration test failed" && exit 1)

                  docker stop test_app
                  docker rm test_app
                '''
            }
        }

        stage('Code Quality') {
            steps {
                echo "Running code style checks..."
                sh '''
                  docker run --rm $DOCKER_IMAGE:latest flake8 . || true
                '''
            }
        }

        stage('Security') {
            steps {
                echo "Running security scan..."
                sh '''
                  docker run --rm aquasec/trivy image $DOCKER_IMAGE:latest || true
                '''
            }
        }

        stage('Deploy') {
            steps {
                echo "Deploying to staging..."
                sh '''
                  docker push $REGISTRY:$DOCKER_TAG
                '''
            }
        }

        stage('Release') {
            steps {
                echo "Promoting release to stable..."
                sh '''
                  docker tag $REGISTRY:$DOCKER_TAG $REGISTRY:stable
                  docker push $REGISTRY:stable
                '''
            }
        }

        stage('Monitoring and Alerting') {
            steps {
                echo "Simulating monitoring and alerting..."
                sh '''
                  echo "Monitoring metrics: CPU=2%, Memory=500MB"
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
            sh '''
              docker stop app || true
              docker rm app || true
              docker run -d --name app -p 8501:8501 $REGISTRY:stable streamlit run app.py || true
            '''
        }
    }
}

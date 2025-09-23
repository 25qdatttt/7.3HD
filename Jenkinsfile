pipeline {
    agent any

    environment {
        REGISTRY = "docker.io/your-dockerhub-username/melbourne-app"
        DOCKER_TAG = "v${env.BUILD_NUMBER}"
    }

    stages {
        stage('Build') {
            steps {
                echo "Building Docker image..."
                sh '''
                  docker build -t melbourne-app:latest \
                               -t $REGISTRY:$DOCKER_TAG .
                '''
            }
        }

        stage('Test') {
            steps {
                echo "Running unit and integration tests..."
                sh '''
                  # Unit test
                  docker run --rm melbourne-app:latest pytest -v

                  # Integration test with random port
                  docker stop test_app || true
                  docker rm test_app || true

                  docker run -d --name test_app -P melbourne-app:latest streamlit run app.py
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
                sh 'docker run --rm melbourne-app:latest flake8 . || true'
            }
        }

        stage('Security') {
            steps {
                echo "Running security scan with Bandit & Safety..."
                sh '''
                  docker run --rm melbourne-app:latest bandit -r .
                  docker run --rm melbourne-app:latest safety check || true
                '''
            }
        }

        stage('Deploy') {
            steps {
                echo "Deploying to staging environment..."
                sh '''
                  docker stop staging_app || true
                  docker rm staging_app || true
                  docker run -d --name staging_app -p 8502:8501 melbourne-app:latest streamlit run app.py
                '''
            }
        }

        stage('Release') {
            steps {
                echo "Promoting to production..."
                sh '''
                  docker tag melbourne-app:latest $REGISTRY:stable
                  docker push $REGISTRY:$DOCKER_TAG
                  docker push $REGISTRY:stable

                  docker stop prod_app || true
                  docker rm prod_app || true
                  docker run -d --name prod_app -p 8503:8501 $REGISTRY:stable streamlit run app.py
                '''
            }
        }

        stage('Monitoring and Alerting') {
            steps {
                echo "Monitoring production container..."
                sh '''
                  docker ps | grep prod_app || (echo "Production app is not running!" && exit 1)
                '''
            }
        }
    }

    post {
        success {
            echo "Pipeline finished successfully at ${new Date()}"
        }
        failure {
            echo "Pipeline failed. Rolling back to last stable release..."
            sh '''
              docker stop prod_app || true
              docker rm prod_app || true
              docker run -d --name prod_app -p 8503:8501 $REGISTRY:stable streamlit run app.py || true
            '''
        }
    }
}

pipeline {
    agent any

    environment {
        REGISTRY = "docker.io/your-dockerhub-username/melbourne-app"
        DOCKER_TAG = "v10"
    }

    stages {
        stage('Build') {
            steps {
                echo "Building Docker image..."
                sh '''
                    docker build -t melbourne-app:latest -t $REGISTRY:$DOCKER_TAG .
                '''
            }
        }

        stage('Test') {
            steps {
                echo "Running unit and integration tests..."
                sh '''
                    # Run unit tests inside container
                    docker run --rm melbourne-app:latest pytest -v

                    # Clean up old test container if exists
                    docker stop test_app || true
                    docker rm test_app || true

                    # Run container on fixed port for integration test
                    docker run -d --name test_app -p 8502:8501 melbourne-app:latest streamlit run app.py
                    sleep 20

                    # Check if app is alive
                    curl -f http://localhost:8502 || (echo "Integration test failed" && exit 1)

                    # Cleanup
                    docker stop test_app
                    docker rm test_app
                '''
            }
        }

        stage('Code Quality') {
            steps {
                echo "Running flake8 for code quality..."
                sh '''
                    docker run --rm melbourne-app:latest flake8 . || true
                '''
            }
        }

        stage('Security') {
            steps {
                echo "Running safety security scan..."
                sh '''
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
                    docker run -d --name staging_app -p 8503:8501 melbourne-app:latest streamlit run app.py
                '''
            }
        }

        stage('Release') {
            steps {
                echo "Releasing to production..."
                sh '''
                    echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
                    docker push $REGISTRY:$DOCKER_TAG
                    docker tag melbourne-app:latest $REGISTRY:stable
                    docker push $REGISTRY:stable

                    docker stop prod_app || true
                    docker rm prod_app || true
                    docker run -d --name prod_app -p 8504:8501 $REGISTRY:stable streamlit run app.py
                '''
            }
        }

        stage('Monitoring and Alerting') {
            steps {
                echo "Simulating monitoring step..."
                sh '''
                    echo "Health check production app..."
                    curl -f http://localhost:8504 || echo "Production app not responding!"
                '''
            }
        }
    }

    post {
        success {
            echo "Pipeline finished successfully at $(date)"
        }
        failure {
            echo "Pipeline failed. Rolling back..."
            sh '''
                docker stop prod_app || true
                docker rm prod_app || true
                docker run -d --name prod_app -p 8504:8501 $REGISTRY:stable streamlit run app.py || true
            '''
        }
    }
}

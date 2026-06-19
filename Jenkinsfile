pipeline {
    agent any

    environment {
        // Replace with your actual Docker Hub username
        DOCKER_HUB_USER = 'sivaanumual'
        IMAGE_NAME      = 'agronet-ingestion'
        IMAGE_TAG       = 'v1'
    }

    stages {
        stage('Checkout Source Code') {
            steps {
                echo 'Pulling latest code changes from Git repository...'
                // Code is automatically fetched by Jenkins from your repository mapping
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building production-grade slim container image...'
                sh "docker build -t ${DOCKER_HUB_USER}/${IMAGE_NAME}:${IMAGE_TAG} ."
            }
        }

        stage('Push to Docker Hub Registry') {
            steps {
                echo 'Syncing image with centralized registry pool...'
                // Jenkins uses local terminal Docker login context
                sh "docker push ${DOCKER_HUB_USER}/${IMAGE_NAME}:${IMAGE_TAG}"
            }
        }

        stage('Deploy to K3s Cluster') {
            steps {
                echo 'Rolling out updated manifest to worker architecture...'
                sh "kubectl apply -f agronet-app.yaml"
                sh "kubectl rollout restart deployment/agronet-api"
            }
        }
    }
}
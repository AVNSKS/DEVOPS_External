pipeline {
    agent {
        kubernetes {
            yaml '''
apiVersion: v1
kind: Pod
spec:
  initContainers:
  - name: socket-permissions
    image: busybox:latest
    command: ["sh", "-c", "chmod 666 /var/run/docker.sock"]
    volumeMounts:
    - mountPath: /var/run/docker.sock
      name: docker-sock
  containers:
  - name: jnlp
    image: jenkins/inbound-agent:3355.v388858a_47b_33-22
    volumeMounts:
    - mountPath: /var/run/docker.sock
      name: docker-sock
    - mountPath: /usr/bin/docker
      name: docker-cli
  volumes:
  - name: docker-sock
    hostPath:
      path: /var/run/docker.sock
  - name: docker-cli
    hostPath:
      path: /usr/bin/docker
'''
        }
    }

    environment {
        DOCKER_HUB_USER = 'sivaanumual'
        IMAGE_NAME      = 'agronet-ingestion'
        IMAGE_TAG       = 'v1'
        // This instructs Jenkins to fetch the password securely from its internal credential storage vault
        DOCKER_HUB_CRED = credentials('docker-hub-vault-token')
    }

    stages {
        stage('Checkout Source Code') {
            steps {
                echo 'Pulling latest code changes from Git repository...'
            }
        }

        stage('Build Docker Image') {
            steps {
                dir('ingestion-service') {
                    echo 'Building production-grade slim container image...'
                    sh "docker build -t ${DOCKER_HUB_USER}/${IMAGE_NAME}:${IMAGE_TAG} ."
                }
            }
        }

        stage('Push to Docker Hub Registry') {
            steps {
                dir('ingestion-service') {
                    echo 'Authenticating with Docker Hub...'
                    // DOCKER_HUB_CRED_USR and DOCKER_HUB_CRED_PSW are auto-generated wrapper variables by Jenkins
                    sh "docker login -u ${DOCKER_HUB_USER} -p ${DOCKER_HUB_CRED_PSW}"
                    echo 'Syncing image with centralized registry pool...'
                    sh "docker push ${DOCKER_HUB_USER}/${IMAGE_NAME}:${IMAGE_TAG}"
                }
            }
        }

        stage('Deploy to K3s Cluster') {
            steps {
                dir('ingestion-service') {
                    echo 'Rolling out updated manifest to worker architecture...'
                    sh "kubectl apply -f agronet-app.yaml"
                    sh "kubectl rollout restart deployment/agronet-api"
                }
            }
        }
    }
}
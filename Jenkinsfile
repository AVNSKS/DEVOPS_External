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
        DOCKER_HUB_USER = 'sivaanumula'  
        IMAGE_NAME      = 'agronet-ingestion'
        IMAGE_TAG       = 'v1'
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
                    echo 'Loading credentials securely...'
                    withCredentials([usernamePassword(credentialsId: 'docker-hub-vault-token', usernameVariable: 'DH_USER', passwordVariable: 'DH_PASS')]) {
                        echo 'Authenticating with Docker Hub...'
                        sh "docker login -u ${DH_USER} -p ${DH_PASS}"
                        echo 'Syncing image with centralized registry pool...'
                        sh "docker push ${DOCKER_HUB_USER}/${IMAGE_NAME}:${IMAGE_TAG}"
                    }
                }
            }
        }

        stage('Deploy to K3s Cluster') {
            steps {
                dir('ingestion-service') {
                    echo 'Downloading kubectl utility dynamically...'
                    sh "curl -LO https://dl.k8s.io/release/v1.28.0/bin/linux/amd64/kubectl"
                    sh "chmod +x kubectl"
                    
                    echo 'Rolling out updated manifest to worker architecture...'
                    sh "./kubectl apply -f agronet-app.yaml"
                    sh "./kubectl rollout restart deployment/agronet-api"
                }
            }
        }
    }
}

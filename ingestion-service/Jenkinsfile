pipeline {
    agent {
        kubernetes {
            yaml '''
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: jnlp
    image: jenkins/inbound-agent:3355.v388858a_47b_33-22
    volumeMounts:
    - mountPath: /var/run/docker.sock
      name: docker-sock
  - name: docker-cli
    image: docker:24.0.7-dind
    command: ["cat"]
    tty: true
    volumeMounts:
    - mountPath: /var/run/docker.sock
      name: docker-sock
  volumes:
  - name: docker-sock
    hostPath:
      path: /var/run/docker.sock
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
                container('docker-cli') {
                    dir('ingestion-service') {
                        echo 'Building production-grade container image using native container environment...'
                        sh "docker build -t ${DOCKER_HUB_USER}/${IMAGE_NAME}:${IMAGE_TAG} ."
                    }
                }
            }
        }

        stage('Push to Docker Hub Registry') {
            steps {
                container('docker-cli') {
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

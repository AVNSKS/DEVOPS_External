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
  - name: kaniko
    image: gcr.io/kaniko-project/executor:v1.14.0-debug
    command: ["cat"]
    tty: true
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

        stage('Build and Push Image') {
            steps {
                container('kaniko') {
                    dir('ingestion-service') {
                        echo 'Building and Pushing image securely using Kaniko...'
                        withCredentials([usernamePassword(credentialsId: 'docker-hub-vault-token', usernameVariable: 'DH_USER', passwordVariable: 'DH_PASS')]) {
                            sh """
                            mkdir -p /kaniko/.docker
                            cat <<EOF > /kaniko/.docker/config.json
                            {
                              "auths": {
                                "[https://index.docker.io/v1/](https://index.docker.io/v1/)": {
                                  "username": "${DH_USER}",
                                  "password": "${DH_PASS}"
                                }
                              }
                            }
                            EOF
                            /kaniko/executor --context=. --dockerfile=Dockerfile --destination=${DOCKER_HUB_USER}/${IMAGE_NAME}:${IMAGE_TAG}
                            """
                        }
                    }
                }
            }
        }

        stage('Deploy to K3s Cluster') {
            steps {
                dir('ingestion-service') {
                    echo 'Downloading kubectl utility dynamically...'
                    sh "curl -LO [https://dl.k8s.io/release/v1.28.0/bin/linux/amd64/kubectl](https://dl.k8s.io/release/v1.28.0/bin/linux/amd64/kubectl)"
                    sh "chmod +x kubectl"
                    
                    echo 'Rolling out updated manifest to worker architecture...'
                    sh "./kubectl apply -f agronet-app.yaml"
                    sh "./kubectl rollout restart deployment/agronet-api"
                }
            }
        }
    }
}
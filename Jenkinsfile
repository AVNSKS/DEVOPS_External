pipeline {
    options {
        skipDefaultCheckout(true)
        disableConcurrentBuilds()
        timeout(time: 20, unit: 'MINUTES')
    }

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
        IMAGE_TAG       = "v${BUILD_NUMBER}"
    }

    stages {
        stage('Checkout Source Code') {
            steps {
                checkout scm
            }
        }

        stage('Build and Push Image') {
            steps {
                container('kaniko') {
                    dir('ingestion-service') {
                        echo 'Building and Pushing image securely using Kaniko...'
                        withCredentials([usernamePassword(credentialsId: 'docker-hub-vault-token', usernameVariable: 'DH_USER', passwordVariable: 'DH_PASS')]) {
                            sh '''
                            set +x
                            mkdir -p /kaniko/.docker
                            cat <<EOF > /kaniko/.docker/config.json
                            {
                              "auths": {
                                "https://index.docker.io/v1/": {
                                  "username": "$DH_USER",
                                  "password": "$DH_PASS"
                                }
                              }
                            }
                            EOF
                            /kaniko/executor \
                              --context=. \
                              --dockerfile=Dockerfile \
                              --destination="$DOCKER_HUB_USER/$IMAGE_NAME:$IMAGE_TAG" \
                              --destination="$DOCKER_HUB_USER/$IMAGE_NAME:latest"
                            '''
                        }
                    }
                }
            }
        }

        stage('Deploy to K3s Cluster') {
            steps {
                dir('ingestion-service') {
                    echo 'Downloading kubectl utility dynamically...'
                    sh 'curl --fail --location --output kubectl https://dl.k8s.io/release/v1.35.5/bin/linux/amd64/kubectl'
                    sh 'chmod +x kubectl'

                    echo 'Rolling out updated manifest to worker architecture...'
                    sh '''
                    sed -i "s#image: sivaanumula/agronet-ingestion:.*#image: $DOCKER_HUB_USER/$IMAGE_NAME:$IMAGE_TAG#" agronet-app.yaml
                    ./kubectl apply --namespace jenkins -f agronet-app.yaml
                    ./kubectl rollout status --namespace jenkins deployment/agronet-api --timeout=5m
                    '''
                }
            }
        }
    }

    post {
        always {
            echo "AgroNet pipeline result: ${currentBuild.currentResult}"
        }
    }
}

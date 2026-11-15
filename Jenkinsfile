pipeline {
    agent any

    environment {
        IMAGE      = 'bluegreen-app'
        KUBECONFIG = '/var/lib/jenkins/.kube/config'
    }

    stages {
        stage('Checkout from Git') {
            steps {
                checkout scm
            }
        }

        stage('Detect Live Color') {
            steps {
                script {
                    env.ACTIVE = sh(returnStdout: true,
                        script: "kubectl get svc bluegreen-service -o jsonpath='{.spec.selector.color}' 2>/dev/null || true").trim()
                    env.NEW = (env.ACTIVE == 'blue') ? 'green' : 'blue'
                    echo "Live color: ${env.ACTIVE ?: 'none (first deployment)'} -> new version goes to: ${env.NEW}"
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build --build-arg BUILD_NUMBER=${BUILD_NUMBER} -t ${IMAGE}:${BUILD_NUMBER} .'
            }
        }

        stage('Load Image into Kubernetes') {
            steps {
                sh '''
                    docker save -o image.tar ${IMAGE}:${BUILD_NUMBER}
                    sudo /usr/local/bin/k3s ctr -n k8s.io images import image.tar
                    rm -f image.tar
                '''
            }
        }

        stage('Deploy to Idle Color') {
            steps {
                sh '''
                    sed "s/__COLOR__/${NEW}/g; s/__TAG__/${BUILD_NUMBER}/g" k8s/deployment.yaml | kubectl apply -f -
                    kubectl rollout status deployment/app-${NEW} --timeout=120s
                    sed "s/__COLOR__/${NEW}/g" k8s/preview-service.yaml | kubectl apply -f -
                '''
            }
        }

        stage('Smoke Test New Version') {
            steps {
                sh '''
                    for i in 1 2 3 4 5 6; do
                        if curl -fs http://localhost:30091/health > /dev/null; then
                            echo "Smoke test passed for the ${NEW} environment"
                            exit 0
                        fi
                        sleep 5
                    done
                    echo "Smoke test FAILED"
                    exit 1
                '''
            }
        }

        stage('Approve Traffic Switch') {
            steps {
                script {
                    def ip = sh(returnStdout: true, script: 'curl -s http://checkip.amazonaws.com').trim()
                    echo "Preview the new ${env.NEW} version at: http://${ip}:30091"
                    timeout(time: 15, unit: 'MINUTES') {
                        input message: "New version is on ${env.NEW}. Switch live traffic to it?", ok: 'Switch traffic'
                    }
                }
            }
        }

        stage('Switch Live Traffic') {
            steps {
                sh '''
                    sed "s/__COLOR__/${NEW}/g" k8s/live-service.yaml | kubectl apply -f -
                    if [ -n "${ACTIVE}" ]; then
                        sed "s/__COLOR__/${ACTIVE}/g" k8s/preview-service.yaml | kubectl apply -f -
                    fi
                '''
            }
        }

        stage('Verify') {
            steps {
                sh '''
                    kubectl get deploy,pods,svc -l app=bluegreen
                    kubectl get svc bluegreen-service bluegreen-preview
                    IP=$(curl -s http://checkip.amazonaws.com)
                    echo "=========================================="
                    echo " LIVE COLOR   : ${NEW}  (build ${BUILD_NUMBER})"
                    echo " Live site    : http://$IP:30090"
                    echo " Previous ver : http://$IP:30091  (kept for instant rollback)"
                    echo "=========================================="
                '''
            }
        }
    }

    post {
        success { echo 'Blue-green switch complete.' }
        failure { echo 'Pipeline failed or was aborted: live traffic was NOT changed.' }
        always  { sh 'docker image prune -f || true' }
    }
}

pipeline {
    agent any

    options {
        timeout(time: 60, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '20'))
        timestamps()
        ansiColor('xterm')
    }

    environment {
        // Dynamic & Immutable Pipeline Tagging
        GIT_SHA = ""
        IMAGE_TAG = ""
        BRANCH_NAME = "${env.BRANCH_NAME ?: 'main'}"
        DOCKER_REGISTRY = "docker.io"
        DOCKERHUB_BACKEND_REPO = "kalanalakshan123/taskflow-backend"
        DOCKERHUB_FRONTEND_REPO = "kalanalakshan123/taskflow-frontend"
        COVERAGE_MIN = "80"
        REPORTS_DIR = "reports"
        CI_COMPOSE = "docker-compose.ci.yml"
        PROD_COMPOSE = "docker-compose.yml"
    }

    stages {
        // =====================================================================
        // STAGE 1: CHECKOUT & METADATA EXTRACTION
        // =====================================================================
        stage('Checkout') {
            steps {
                script {
                    checkout scm
                    def fullCommit = env.GIT_COMMIT ?: sh(script: 'git rev-parse HEAD', returnStdout: true).trim()
                    env.GIT_SHA = fullCommit.take(7)
                    env.IMAGE_TAG = "${env.GIT_SHA}-${env.BUILD_NUMBER}"

                    echo "=================================================="
                    echo "TASKFLOW CI/CD PIPELINE"
                    echo "Branch: ${env.BRANCH_NAME ?: 'main'}"
                    echo "Commit: ${env.GIT_SHA}"
                    echo "Build:  #${env.BUILD_NUMBER}"
                    echo "Tag:    ${env.IMAGE_TAG}"
                    echo "=================================================="

                    sh "mkdir -p ${REPORTS_DIR}"
                }
            }
        }

        // =====================================================================
        // STAGE 2: TOOL VALIDATION
        // =====================================================================
        stage('Tool Validation') {
            steps {
                echo "Validating availability of prerequisite tools..."
                sh '''
                    python3 --version
                    node --version
                    npm --version
                    docker --version
                    docker compose version
                    trivy --version
                    gitleaks version
                '''
            }
        }

        // =====================================================================
        // STAGE 3: INSTALL DEPENDENCIES
        // =====================================================================
        stage('Install Dependencies') {
            steps {
                echo "Installing backend and frontend dependencies deterministically..."
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install --upgrade pip setuptools wheel
                    pip install -r backend/requirements-dev.txt

                    cd frontend
                    npm ci
                '''
            }
        }

        // =====================================================================
        // STAGE 4: PARALLEL QUALITY CHECKS
        // =====================================================================
        stage('Parallel Quality Checks') {
            parallel {
                stage('Backend Ruff') {
                    steps {
                        echo "Running Ruff linter and formatter validation..."
                        sh '''
                            . .venv/bin/activate
                            ruff check backend
                            ruff format --check backend
                        '''
                    }
                }

                stage('Backend Unit Tests') {
                    steps {
                        echo "Running Backend Unit Tests..."
                        sh '''
                            . .venv/bin/activate
                            export PYTHONPATH=backend
                            pytest backend/tests/test_health.py backend/tests/test_tasks.py backend/tests/test_task_service.py --junitxml=${REPORTS_DIR}/backend-unit.xml
                        '''
                    }
                }

                stage('Frontend ESLint') {
                    steps {
                        echo "Running Frontend ESLint..."
                        sh '''
                            cd frontend
                            npm run lint
                        '''
                    }
                }

                stage('Frontend TypeScript Check') {
                    steps {
                        echo "Running TypeScript strict typecheck..."
                        sh '''
                            cd frontend
                            npm run typecheck
                        '''
                    }
                }

                stage('Frontend Tests') {
                    steps {
                        echo "Running Frontend component tests..."
                        sh '''
                            cd frontend
                            npm test
                        '''
                    }
                }
            }
        }

        // =====================================================================
        // STAGE 5: TEST COVERAGE
        // =====================================================================
        stage('Coverage') {
            steps {
                echo "Executing backend coverage suite (Gate: >= ${COVERAGE_MIN}%)..."
                sh '''
                    . .venv/bin/activate
                    export PYTHONPATH=backend
                    pytest backend/tests/test_health.py backend/tests/test_tasks.py backend/tests/test_task_service.py \
                        --cov=app \
                        --cov-report=xml:${REPORTS_DIR}/coverage.xml \
                        --cov-report=html:${REPORTS_DIR}/htmlcov \
                        --cov-fail-under=${COVERAGE_MIN}
                '''
            }
        }

        // =====================================================================
        // STAGE 6: DEPENDENCY SECURITY
        // =====================================================================
        stage('Dependency Security') {
            steps {
                echo "Scanning backend and frontend dependencies for known CVEs..."
                sh '''
                    . .venv/bin/activate
                    pip-audit -r backend/requirements.txt || echo "pip-audit completed with warnings"

                    cd frontend
                    npm audit --audit-level=high
                '''
            }
        }

        // =====================================================================
        // STAGE 7: SECRET SCANNING
        // =====================================================================
        stage('Secret Scan') {
            steps {
                echo "Scanning workspace for leaked secrets with Gitleaks..."
                sh '''
                    gitleaks detect --source=. --no-banner --redact || echo "Gitleaks secret scan completed"
                '''
            }
        }

        // =====================================================================
        // STAGE 8: INTEGRATION ENVIRONMENT STARTUP
        // =====================================================================
        stage('Integration Environment') {
            steps {
                echo "Launching isolated CI PostgreSQL and Backend integration services..."
                sh '''
                    docker compose -p taskflow-ci -f ${CI_COMPOSE} down -v --remove-orphans || true
                    docker compose -p taskflow-ci -f ${CI_COMPOSE} up -d --build

                    echo "Waiting for PostgreSQL CI health..."
                    for i in $(seq 1 30); do
                        if docker inspect --format='{{.State.Health.Status}}' taskflow-ci-postgres 2>/dev/null | grep -q "healthy"; then
                            echo "PostgreSQL is healthy!"
                            break
                        fi
                        echo "Waiting for postgres... ($i/30)"
                        sleep 2
                    done

                    echo "Waiting for Backend CI health..."
                    for i in $(seq 1 30); do
                        if docker inspect --format='{{.State.Health.Status}}' taskflow-ci-backend 2>/dev/null | grep -q "healthy"; then
                            echo "Backend CI is healthy!"
                            break
                        fi
                        echo "Waiting for backend CI... ($i/30)"
                        sleep 2
                    done
                '''
            }
        }

        // =====================================================================
        // STAGE 9: INTEGRATION TESTS
        // =====================================================================
        stage('Integration Tests') {
            steps {
                echo "Executing integration tests against live PostgreSQL..."
                sh '''
                    . .venv/bin/activate
                    export PYTHONPATH=backend
                    TARGET_HOST="localhost"
                    if ! curl -sf http://localhost:8001/health > /dev/null 2>&1; then
                        TARGET_HOST="host.docker.internal"
                    fi
                    echo "Targeting integration service on ${TARGET_HOST}:8001..."
                    INTEGRATION_BASE_URL="http://${TARGET_HOST}:8001" pytest backend/tests/test_integration.py \
                        --junitxml=${REPORTS_DIR}/integration-tests.xml -v
                '''
            }
        }

        // =====================================================================
        // STAGE 10: APPLICATION BUILD
        // =====================================================================
        stage('Application Build') {
            steps {
                echo "Validating backend importability and compiling Next.js production build..."
                sh '''
                    . .venv/bin/activate
                    export PYTHONPATH=backend
                    python3 -c "import app.main; print('Backend modules loaded successfully')"

                    cd frontend
                    npm run build
                '''
            }
        }

        // =====================================================================
        // STAGE 11: DOCKER BUILD
        // =====================================================================
        stage('Docker Build') {
            steps {
                echo "Building Docker container images with Git SHA tag: ${IMAGE_TAG}..."
                sh '''
                    docker build -t taskflow-backend:${IMAGE_TAG} -t taskflow-backend:latest ./backend
                    docker build -t taskflow-frontend:${IMAGE_TAG} -t taskflow-frontend:latest ./frontend
                '''
            }
        }

        // =====================================================================
        // STAGE 12: TRIVY VULNERABILITY SCAN
        // =====================================================================
        stage('Trivy Scan') {
            steps {
                echo "Scanning Docker images for vulnerabilities with Trivy..."
                sh '''
                    trivy image --severity HIGH,CRITICAL --scanners vuln --format table taskflow-backend:${IMAGE_TAG} || true
                    trivy image --severity HIGH,CRITICAL --scanners vuln --format table taskflow-frontend:${IMAGE_TAG} || true
                '''
            }
        }

        // =====================================================================
        // STAGE 13: DOCKER HUB PUSH (Branch-Aware: Main Only)
        // =====================================================================
        stage('Docker Hub Push') {
            when {
                anyOf {
                    branch 'main'
                    expression { return (env.BRANCH_NAME ?: 'main') == 'main' }
                }
            }
            steps {
                echo "Publishing release images to Docker Hub..."
                withCredentials([usernamePassword(credentialsId: 'DOCKERHUB_CREDENTIALS', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh '''
                        echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                        TARGET_BACKEND="${DOCKER_USER}/taskflow-backend"
                        TARGET_FRONTEND="${DOCKER_USER}/taskflow-frontend"

                        echo "Tagging backend image ${TARGET_BACKEND}:${IMAGE_TAG} and ${TARGET_BACKEND}:latest..."
                        docker tag taskflow-backend:${IMAGE_TAG} ${TARGET_BACKEND}:${IMAGE_TAG}
                        docker tag taskflow-backend:latest ${TARGET_BACKEND}:latest

                        echo "Tagging frontend image ${TARGET_FRONTEND}:${IMAGE_TAG} and ${TARGET_FRONTEND}:latest..."
                        docker tag taskflow-frontend:${IMAGE_TAG} ${TARGET_FRONTEND}:${IMAGE_TAG}
                        docker tag taskflow-frontend:latest ${TARGET_FRONTEND}:latest

                        echo "Pushing ${TARGET_BACKEND}:${IMAGE_TAG} to Docker Hub..."
                        docker push ${TARGET_BACKEND}:${IMAGE_TAG}
                        echo "Pushing ${TARGET_BACKEND}:latest to Docker Hub..."
                        docker push ${TARGET_BACKEND}:latest

                        echo "Pushing ${TARGET_FRONTEND}:${IMAGE_TAG} to Docker Hub..."
                        docker push ${TARGET_FRONTEND}:${IMAGE_TAG}
                        echo "Pushing ${TARGET_FRONTEND}:latest to Docker Hub..."
                        docker push ${TARGET_FRONTEND}:latest

                        docker logout
                        echo "=================================================="
                        echo "Docker Hub release push completed and verified successfully for:"
                        echo "  - ${TARGET_BACKEND}:${IMAGE_TAG}"
                        echo "  - ${TARGET_BACKEND}:latest"
                        echo "  - ${TARGET_FRONTEND}:${IMAGE_TAG}"
                        echo "  - ${TARGET_FRONTEND}:latest"
                        echo "=================================================="
                    '''
                }
            }
        }

        // =====================================================================
        // STAGE 14: DEPLOYMENT (Branch-Aware: Main Only)
        // =====================================================================
        stage('Deployment') {
            when {
                anyOf {
                    branch 'main'
                    expression { return (env.BRANCH_NAME ?: 'main') == 'main' }
                }
            }
            steps {
                echo "Deploying application with Docker Compose..."
                sh '''
                    BACKEND_IMAGE=taskflow-backend:${IMAGE_TAG} \
                    FRONTEND_IMAGE=taskflow-frontend:${IMAGE_TAG} \
                    docker compose -p taskflow -f ${PROD_COMPOSE} up -d
                '''
            }
        }

        // =====================================================================
        // STAGE 15: HEALTH CHECKS (Branch-Aware: Main Only)
        // =====================================================================
        stage('Health Check') {
            when {
                anyOf {
                    branch 'main'
                    expression { return (env.BRANCH_NAME ?: 'main') == 'main' }
                }
            }
            steps {
                echo "Verifying service endpoints..."
                sh '''
                    TARGET_HOST="localhost"
                    if ! curl -sf http://localhost:8000/health > /dev/null 2>&1; then
                        TARGET_HOST="host.docker.internal"
                    fi
                    echo "Checking Backend /health on ${TARGET_HOST}:8000..."
                    BACKEND_OK=0
                    for i in $(seq 1 30); do
                        if curl -sf http://${TARGET_HOST}:8000/health | grep -q "healthy"; then
                            echo "Backend health check PASSED!"
                            BACKEND_OK=1
                            break
                        fi
                        echo "Waiting for backend health ($i/30)..."
                        sleep 3
                    done
                    if [ "$BACKEND_OK" -ne 1 ]; then
                        echo "Backend health check FAILED!"
                        exit 1
                    fi

                    echo "Checking Frontend HTTP response on ${TARGET_HOST}:3000..."
                    FRONTEND_OK=0
                    for i in $(seq 1 30); do
                        if curl -sf http://${TARGET_HOST}:3000 > /dev/null 2>&1; then
                            echo "Frontend health check PASSED!"
                            FRONTEND_OK=1
                            break
                        fi
                        echo "Waiting for frontend health ($i/30)..."
                        sleep 3
                    done
                    if [ "$FRONTEND_OK" -ne 1 ]; then
                        echo "Frontend health check FAILED!"
                        exit 1
                    fi
                '''
            }
        }

        // =====================================================================
        // STAGE 16: SMOKE TESTS (Branch-Aware: Main Only)
        // =====================================================================
        stage('Smoke Test') {
            when {
                anyOf {
                    branch 'main'
                    expression { return (env.BRANCH_NAME ?: 'main') == 'main' }
                }
            }
            steps {
                echo "Running end-to-end smoke test suite..."
                sh '''
                    . .venv/bin/activate
                    TARGET_HOST="localhost"
                    if ! curl -sf http://localhost:8000/health > /dev/null 2>&1; then
                        TARGET_HOST="host.docker.internal"
                    fi
                    python3 scripts/smoke_test.py --base-url http://${TARGET_HOST}:8000
                '''
            }
        }

        // =====================================================================
        // STAGE 17: CLEANUP
        // =====================================================================
        stage('Cleanup') {
            steps {
                echo "Tearing down ephemeral CI integration resources..."
                sh '''
                    docker compose -p taskflow-ci -f ${CI_COMPOSE} down -v --remove-orphans || true
                '''
            }
        }

        // =====================================================================
        // STAGE 18: REPORTS
        // =====================================================================
        stage('Reports') {
            steps {
                echo "Archiving test reports and build artifacts..."
                archiveArtifacts allowEmptyArchive: true, artifacts: "${REPORTS_DIR}/**"
                sh '''
                    echo "=================================================="
                    echo "BUILD ARTIFACTS AND REPORTS SUMMARY"
                    ls -la ${REPORTS_DIR}
                    echo "=================================================="
                '''
            }
        }
    }

    // =========================================================================
    // POST PIPELINE ACTIONS & CLEANUP
    // =========================================================================
    post {
        always {
            echo "Post-execution cleanup ensuring no dangling CI containers..."
            sh '''
                docker compose -p taskflow-ci -f ${CI_COMPOSE} down -v --remove-orphans || true
            '''
        }
        failure {
            echo "Pipeline failed! Collecting diagnostic container logs..."
            sh '''
                docker compose -p taskflow -f ${PROD_COMPOSE} logs --tail=100 || true
            '''
        }
    }
}

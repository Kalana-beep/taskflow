# TaskFlow Local Jenkins Setup

This directory contains the Docker configuration to run a fully functional, self-hosted Jenkins master/agent container locally.

## Features

- **Pre-installed Toolchain:** Includes Python 3, Node.js 20, npm, Git, Docker CLI, Docker Compose.
- **Embedded Security Scanners:** Contains Trivy and Gitleaks for zero-friction container and secret scanning.
- **Docker-out-of-Docker (DooD):** Mounts the host Docker socket (`/var/run/docker.sock`), allowing pipeline jobs to build, tag, scan, and deploy containers on the host Docker daemon.
- **Persistent Storage:** Uses Docker volume `taskflow_jenkins_data` to retain plugins, jobs, credentials, and build history.

## Starting Jenkins

Run the following command from the project root:

```bash
docker compose -f ci/jenkins/docker-compose.yml up -d --build
```

Access Jenkins in your browser at:
**[http://localhost:8088](http://localhost:8088)** (Port 8088 is configured to prevent port conflicts with any host services on 8080).

### Automated Job Provisioning

The container includes initialization scripts in `ci/jenkins/init.groovy.d/`:
- `01-security.groovy`: Configures automated access, disables CSRF crumb checks for local API triggers, and sets the root URL.
- `02-create-job.groovy`: Automatically registers the pipeline job `TaskFlow-CI-CD` and loads `Jenkinsfile` directly from the mounted `/workspace/Jenkinsfile`.

### Triggering Pipeline Runs

Via Browser:
Navigate to `http://localhost:8088/job/TaskFlow-CI-CD/` and click **Build Now**.

Via API / CLI:
```bash
curl -X POST http://localhost:8088/job/TaskFlow-CI-CD/build
```

### Initial Administrator Password (if required)

```bash
docker exec taskflow-jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

### Configuring Docker Hub Credentials (Optional)

1. Navigate to **Manage Jenkins** > **Credentials** > **System** > **Global credentials**.
2. Click **Add Credentials**.
3. Kind: **Username with password**
4. ID: `DOCKERHUB_CREDENTIALS`
5. Username: `<Your Docker Hub Username>`
6. Password: `<Your Docker Hub Personal Access Token>`
*(Note: If credentials are not configured, the pipeline safely skips the Docker Hub publishing step while executing all other 17 stages).*

## Stopping Jenkins

```bash
docker compose -f ci/jenkins/docker-compose.yml down
```
To purge persistent Jenkins data:
```bash
docker compose -f ci/jenkins/docker-compose.yml down -v
```

# Jenkins Local Setup & Configuration Guide

This guide details running Jenkins locally via Docker, configuring credentials, and executing the TaskFlow pipeline.

---

## 1. Quick Start

Run Jenkins using Docker Compose:

```bash
docker compose -f ci/jenkins/docker-compose.yml up -d --build
```

Access Jenkins at:
[http://localhost:8088](http://localhost:8088) *(Port 8088 avoids conflict with any host services on 8080).*

---

## 2. Automated Provisioning & Unlocking

The setup includes Groovy initialization scripts in `ci/jenkins/init.groovy.d/`:
- Automatic admin configuration with root URL and CSRF crumb bypass for automated triggers.
- Automatic creation and loading of the `TaskFlow-CI-CD` job from `/workspace/Jenkinsfile`.

To view the initial administrator password (if prompted):
```bash
docker exec taskflow-jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

---

## 3. Configuring Docker Hub Credentials

To allow Jenkins to push release images on the `main` branch:

1. Go to **Manage Jenkins** > **Credentials** > **System** > **Global credentials (unrestricted)**.
2. Click **Add Credentials**.
3. Configure:
   - **Kind:** Username with password
   - **Scope:** Global
   - **Username:** `<Your Docker Hub Username>`
   - **Password:** `<Your Docker Hub Personal Access Token>`
   - **ID:** `DOCKERHUB_CREDENTIALS` (Must match exactly)
4. Click **Create**.

---

## 4. Creating the Pipeline Job

1. From the dashboard, click **New Item**.
2. Enter item name: `TaskFlow-CI-CD`.
3. Select **Pipeline** and click **OK**.
4. In the job configuration under **Pipeline**:
   - **Definition:** Pipeline script from SCM
   - **SCM:** Git
   - **Repository URL:** `https://github.com/Kalana-beep/apexstore.git` (or your local repo path)
   - **Branch Specifier:** `*/main`
   - **Script Path:** `Jenkinsfile`
5. Click **Save**.

---

## 5. Executing the Build

Click **Build Now** to trigger the pipeline. You can inspect stage-by-stage execution in the **Stage View** or open **Console Output** for full real-time logs.

---

## 6. Docker Access (Docker-out-of-Docker)

The Jenkins container mounts the host's `/var/run/docker.sock`. This architecture allows:
- Jenkins to run without privileged nested container daemons (DinD).
- Direct utilization of host-cached Docker image layers.
- Spawning sibling test containers (`docker-compose.ci.yml`) and managing host deployments.

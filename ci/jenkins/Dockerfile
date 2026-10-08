# ==============================================================================
# TaskFlow Jenkins Agent / Master Dockerfile
# Equipped with Docker CLI, Docker Compose, Python, Node.js, Trivy, and Gitleaks
# ==============================================================================

FROM jenkins/jenkins:lts-jdk17

USER root

# Install system dependencies, Python 3, Git, Curl, JQ
RUN apt-get update && apt-get install -y --no-install-recommends \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    python3 \
    python3-pip \
    python3-venv \
    git \
    wget \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 20 LTS and npm
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    rm -rf /var/lib/apt/lists/*

# Install Docker CLI and Docker Compose Plugin
RUN install -m 0755 -d /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg && \
    chmod a+r /etc/apt/keyrings/docker.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null && \
    apt-get update && apt-get install -y --no-install-recommends \
    docker-ce-cli \
    docker-compose-plugin \
    && rm -rf /var/lib/apt/lists/* && \
    ln -sf /usr/libexec/docker/cli-plugins/docker-compose /usr/local/bin/docker-compose

# Install Trivy Security Scanner
RUN curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin

# Install Gitleaks Secret Scanner (pinned reliable version)
ARG GITLEAKS_VERSION="8.18.4"
RUN wget -q "https://github.com/gitleaks/gitleaks/releases/download/v${GITLEAKS_VERSION}/gitleaks_${GITLEAKS_VERSION}_linux_x64.tar.gz" -O /tmp/gitleaks.tar.gz && \
    tar -xzf /tmp/gitleaks.tar.gz -C /usr/local/bin gitleaks && \
    chmod +x /usr/local/bin/gitleaks && \
    rm -f /tmp/gitleaks.tar.gz

# Pre-install Jenkins plugins required for Declarative Pipeline
RUN jenkins-plugin-cli --plugins \
    workflow-aggregator \
    git \
    pipeline-stage-view \
    timestamper \
    ansicolor \
    credentials-binding \
    pipeline-utility-steps

# Copy Groovy auto-initialization scripts
COPY init.groovy.d/ /usr/share/jenkins/ref/init.groovy.d/

# Configure Docker group access for Jenkins user
RUN groupadd -f docker && usermod -aG docker jenkins

# Ensure jenkins user owns jenkins home
RUN chown -R jenkins:jenkins /var/jenkins_home

USER jenkins

EXPOSE 8080 50000

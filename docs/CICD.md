# 🤖 CI/CD Guide

Continuous Integration und Continuous Deployment Setup für SchulBuddy.

## 🏗️ GitHub Actions Workflows

### 1. Build und Test Pipeline

```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on:
  push:
    branches: [main, dev]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest --cov=app tests/
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3

  docker-build:
    runs-on: ubuntu-latest
    needs: test
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker image
      run: |
        docker build -t schulbuddy:test .
        docker run --rm schulbuddy:test python -c "import app; print('Build successful')"
```

### 2. Container Registry Pipeline

```yaml
# .github/workflows/docker.yml
name: Docker Build & Push

on:
  push:
    branches: [main]
    tags: ['v*']

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
    - name: Checkout
      uses: actions/checkout@v3

    - name: Log in to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}

    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v4
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=semver,pattern={{version}}
          type=semver,pattern={{major}}.{{minor}}

    - name: Build and push
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
```

### 3. Deployment Pipeline

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    tags: ['v*']
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    
    steps:
    - name: Deploy to Server
      uses: appleboy/ssh-action@v0.1.5
      with:
        host: ${{ secrets.HOST }}
        username: ${{ secrets.USERNAME }}
        key: ${{ secrets.SSH_KEY }}
        script: |
          cd /app/schulbuddy
          git pull origin main
          ./start.sh backup
          ./start.sh down
          ./start.sh build
          ./start.sh up
          ./start.sh health
```

## 🔧 Advanced Workflows

### Multi-Environment Deployment

```yaml
# .github/workflows/multi-env.yml
name: Multi-Environment Deploy

on:
  push:
    branches: [main, staging, dev]

jobs:
  deploy:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        include:
          - branch: dev
            environment: development
            server: dev.schulbuddy.com
          - branch: staging
            environment: staging
            server: staging.schulbuddy.com
          - branch: main
            environment: production
            server: schulbuddy.com
    
    steps:
    - name: Deploy to ${{ matrix.environment }}
      if: github.ref == format('refs/heads/{0}', matrix.branch)
      uses: appleboy/ssh-action@v0.1.5
      with:
        host: ${{ matrix.server }}
        username: ${{ secrets.SSH_USER }}
        key: ${{ secrets.SSH_KEY }}
        script: |
          cd /app/schulbuddy
          git pull origin ${{ matrix.branch }}
          ./start.sh backup
          ./start.sh restart
```

### Database Migration Workflow

```yaml
# .github/workflows/migrate.yml
name: Database Migration

on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Target environment'
        required: true
        default: 'staging'
        type: choice
        options:
        - staging
        - production

jobs:
  migrate:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Run Migration
      uses: appleboy/ssh-action@v0.1.5
      with:
        host: ${{ secrets.HOST }}
        username: ${{ secrets.USERNAME }}
        key: ${{ secrets.SSH_KEY }}
        script: |
          cd /app/schulbuddy
          ./start.sh backup
          docker-compose exec schulbuddy python migrate.py
          ./start.sh health
```

## 🛡️ Security & Secrets

### GitHub Secrets Setup

```bash
# Server Credentials
SSH_KEY          # Private SSH Key
SSH_USER         # SSH Username
HOST             # Server Hostname

# Container Registry
DOCKER_USERNAME  # Docker Hub Username
DOCKER_PASSWORD  # Docker Hub Password

# Application Secrets
SECRET_KEY       # Flask Secret Key
DATABASE_URL     # Production Database URL
API_KEY          # API Access Key
```

### Secrets in Workflows

```yaml
- name: Deploy with Secrets
  env:
    SECRET_KEY: ${{ secrets.SECRET_KEY }}
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
  run: |
    echo "SECRET_KEY=$SECRET_KEY" > .env.prod
    echo "DATABASE_URL=$DATABASE_URL" >> .env.prod
    scp .env.prod server:/app/schulbuddy/.env
```

## 📊 Monitoring & Quality Gates

### Code Quality Checks

```yaml
# .github/workflows/quality.yml
name: Code Quality

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: 3.11
    
    - name: Install linting tools
      run: |
        pip install flake8 black isort mypy
    
    - name: Run Black
      run: black --check app.py routes/ models.py
    
    - name: Run isort
      run: isort --check-only app.py routes/ models.py
    
    - name: Run flake8
      run: flake8 app.py routes/ models.py
    
    - name: Run mypy
      run: mypy app.py

  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Run Bandit Security Scan
      uses: securecodewarrior/github-action-bandit@v1
      with:
        config_file: .bandit
```

### Performance Testing

```yaml
# .github/workflows/performance.yml
name: Performance Tests

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM

jobs:
  load-test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Build test environment
      run: |
        docker-compose -f docker-compose.test.yml up -d
        sleep 30
    
    - name: Run load tests
      run: |
        pip install locust
        locust --headless --users 100 --spawn-rate 10 --run-time 1m --host http://localhost:5000
    
    - name: Cleanup
      run: docker-compose -f docker-compose.test.yml down
```

## 🚀 Release Automation

### Automatic Releases

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags: ['v*']

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
      with:
        fetch-depth: 0
    
    - name: Generate Changelog
      id: changelog
      run: |
        # Generiere Changelog basierend auf Git History
        echo "changelog<<EOF" >> $GITHUB_OUTPUT
        git log --pretty=format:"- %s (%h)" $(git describe --tags --abbrev=0 HEAD^)..HEAD >> $GITHUB_OUTPUT
        echo "EOF" >> $GITHUB_OUTPUT
    
    - name: Create Release
      uses: actions/create-release@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        tag_name: ${{ github.ref }}
        release_name: Release ${{ github.ref }}
        body: |
          Changes in this Release:
          ${{ steps.changelog.outputs.changelog }}
        draft: false
        prerelease: false
```

### Semantic Versioning

```yaml
# .github/workflows/semantic-release.yml
name: Semantic Release

on:
  push:
    branches: [main]

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
      with:
        token: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Semantic Release
      uses: cycjimmy/semantic-release-action@v3
      with:
        extra_plugins: |
          @semantic-release/changelog
          @semantic-release/git
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## 🔄 GitOps Workflow

### ArgoCD Integration

```yaml
# argocd/application.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: schulbuddy
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/TimBoBN/schulbuddy
    targetRevision: main
    path: k8s/
  destination:
    server: https://kubernetes.default.svc
    namespace: schulbuddy
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

### Flux Integration

```yaml
# flux/kustomization.yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1beta2
kind: Kustomization
metadata:
  name: schulbuddy
  namespace: flux-system
spec:
  interval: 5m
  path: "./k8s"
  prune: true
  sourceRef:
    kind: GitRepository
    name: schulbuddy
```

## 📋 Best Practices

### Workflow Organization

```
.github/
└── workflows/
    ├── ci.yml              # Test & Build
    ├── cd.yml              # Deployment
    ├── security.yml        # Security Scans
    ├── quality.yml         # Code Quality
    ├── performance.yml     # Performance Tests
    └── release.yml         # Release Automation
```

### Environment Management

```yaml
# Environments in Repository Settings
environments:
  - name: development
    protection_rules: []
    
  - name: staging
    protection_rules:
      - required_reviewers: 1
    
  - name: production
    protection_rules:
      - required_reviewers: 2
      - delay_timer: 5  # 5 minutes delay
```

### Branch Protection

```yaml
# Branch protection rules
main:
  required_status_checks:
    - ci
    - security-scan
    - code-quality
  enforce_admins: true
  required_pull_request_reviews:
    required_approving_review_count: 2
```

## 🔍 Troubleshooting CI/CD

### Common Issues

**Docker Build Failures:**
```yaml
- name: Debug Docker Build
  run: |
    docker build --no-cache -t schulbuddy:debug .
    docker run --rm schulbuddy:debug python -c "import sys; print(sys.version)"
```

**SSH Connection Issues:**
```yaml
- name: Test SSH Connection
  run: |
    ssh -o StrictHostKeyChecking=no ${{ secrets.SSH_USER }}@${{ secrets.HOST }} 'echo "Connection successful"'
```

**Secret Access Problems:**
```yaml
- name: Verify Secrets
  env:
    SECRET_KEY: ${{ secrets.SECRET_KEY }}
  run: |
    if [ -z "$SECRET_KEY" ]; then
      echo "SECRET_KEY is not set"
      exit 1
    fi
```

### Monitoring Deployments

```yaml
- name: Health Check After Deploy
  run: |
    sleep 30
    curl -f http://${{ secrets.HOST }}/health || exit 1
    
- name: Notify on Failure
  if: failure()
  uses: 8398a7/action-slack@v3
  with:
    status: failure
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

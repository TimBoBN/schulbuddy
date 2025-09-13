# 🎓 SchulBuddy - Multi-Architecture Docker Edition (English)

A modern school management system with Docker support for easy deployment on AMD64 and ARM systems.

[![Docker Multi-Platform Build](https://github.com/TimBoBN/schulbuddy/actions/workflows/docker-multiplatform.yml/badge.svg)](https://github.com/TimBoBN/schulbuddy/actions/workflows/docker-multiplatform.yml)
# 🎓 SchulBuddy - Multi-Architecture Docker Edition (English)

A modern school management system with Docker support for easy deployment on AMD64 and ARM systems.

## 🚀 Quick Start

### Option 1: Quick start with curl (recommended)

```bash
# 1. Download configuration file
curl -o .env https://raw.githubusercontent.com/TimBoBN/schulbuddy/main/config/.env.example

# 2. Adjust important settings
nano .env  # Change at least SECRET_KEY!

# 3. Start the container (auto-detects architecture)
docker-compose up -d

# 4. Open http://localhost:5000
```

### Option 2: Manual start

```bash
# 1. Clone the repository (optional)
git clone https://github.com/TimBoBN/schulbuddy.git
cd schulbuddy

# 2. Copy config
cp config/.env.example .env

# 3. Adjust and start
nano .env
docker-compose up -d
```

### 🎯 Versions

```bash
# Production (main branch)
docker pull timbobn/schulbuddy:latest

# Development (dev branch)
docker pull timbobn/schulbuddy:dev

# Specific version
docker pull timbobn/schulbuddy:v1.2.0
```

## 🏗️ Multi-Architecture Support

SchulBuddy automatically supports:
- **AMD64**: PCs/servers (4 Gunicorn workers)
- **ARM**: Raspberry Pi, Apple M1/M2 (2 Gunicorn workers)

Docker automatically selects the right architecture for your system.

## ⚙️ Configuration (.env)

### Download automatically:
```bash
curl -o .env https://raw.githubusercontent.com/TimBoBN/schulbuddy/main/config/.env.example
```

### Most important settings:

```bash
# 🔐 IMPORTANT: Change the secret key!
SECRET_KEY=your-very-strong-secret-key-here

# 🏫 School settings
CURRENT_SCHOOL_YEAR=2024/25
CURRENT_SEMESTER=1

# 🌐 Server
PORT=5000
EXTERNAL_PORT=5000

# 🐳 Docker image version  
TAG=latest  # or 'dev' for development
```

### Full .env options:
- **Security**: `SECRET_KEY`, session timeouts, login limits
- **School**: school year, semester
- **Performance**: worker count (automatic), timeouts
- **Docker**: image tags, registries

## 📁 Project structure

```
schulbuddy/
├── 📁 config/                   # Configuration files
│   ├── .env.example            # Environment variables template
│   ├── .env.template           # Alternative template
│   └── nginx.conf              # Nginx configuration
├── 📁 docs/                     # Documentation
│   ├── ARM_SUPPORT.md          # ARM support details
│   ├── DOCKER_README.md        # Docker setup guide
│   ├── MULTI-ARCH-README.md    # Multi-architecture guide
│   └── SECURITY.md             # Security guidelines
├── 📁 scripts/                  # Utility scripts
│   ├── build-multiarch.ps1     # Multi-arch build (PowerShell)
│   ├── build-multiarch.sh      # Multi-arch build (Bash)
│   ├── setup-env.ps1           # Environment setup (PowerShell)
│   └── setup-env.sh            # Environment setup (Bash)
├── 📄 app.py                    # Main Flask application
├── 📄 config.py                 # Configuration management
├── 📄 models.py                 # Database models
├── 📄 wsgi.py                   # WSGI entry point
├── 📄 api_security.py           # API security
├── 📄 requirements.txt          # Python dependencies
├── 🐳 Dockerfile                # AMD64 container
├── 🐳 Dockerfile.arm            # ARM container
├── 🐳 docker-compose.yml        # Service orchestration
├── 📄 entrypoint.sh             # Container startup
└── 📄 gunicorn.conf.py          # Gunicorn configuration
```

## 🚀 Quick start (prebuilt Docker images)

Prebuilt images are available and built via GitHub Actions:

**Docker Hub**:
```bash
# Production (latest)
docker pull timbobn/schulbuddy:latest

# Development
docker pull timbobn/schulbuddy:dev

# Specific version
docker pull timbobn/schulbuddy:v1.2.3
```

**GitHub Container Registry (GHCR)**:
```bash
# Production (latest)
docker pull ghcr.io/timbobn/schulbuddy:latest

# Development
docker pull ghcr.io/timbobn/schulbuddy:dev

# Specific version
docker pull ghcr.io/timbobn/schulbuddy:v1.2.3
```

#### 2. Download docker-compose.yml

```bash
# Download a single file via curl
curl -O https://raw.githubusercontent.com/TimBoBN/schulbuddy/main/docker-compose.yml

# Or clone the repository for all configs
git clone https://github.com/TimBoBN/schulbuddy.git
cd schulbuddy
```

#### 3. Start the app

```bash
# Production
TAG=latest docker-compose up -d

# Development
TAG=dev docker-compose up -d

# Specific version
TAG=v1.2.3 docker-compose up -d

# For GHCR image: adjust the line in docker-compose.yml
```

### Method 2: Local build

#### 1. Clone repository
```bash
git clone https://github.com/TimBoBN/schulbuddy.git
cd schulbuddy
```

#### 2. Configure environment
```bash
# Windows
.\scripts\setup-env.ps1

# Linux/Mac
bash scripts/setup-env.sh
```

#### 3. Build and start
```bash
# With Makefile (recommended)
make install

# Or manually
docker-compose up --build -d
```

### 4. Open the app
- Open your browser
- Go to `http://localhost:5000` (or your configured port)
- Default login: admin / schulbuddy (please change!)

## 🛠️ Available make targets

```bash
make help         # Show available commands
make setup        # Configure environment variables
make build        # Build Docker images
make start        # Start services
make stop         # Stop services
make restart      # Restart services
make logs         # Show logs
make status       # Show service status
make clean        # Remove containers and volumes
make install      # Full installation
make update       # Update to latest version
```

## ⚙️ Configuration

### Environment variables (.env)

```env
# Docker image configuration
TAG=latest  # latest (production), dev (development), v1.2.3 (specific version)

# Server configuration
HOST=0.0.0.0
PORT=5000
EXTERNAL_PORT=5000

# Flask configuration
FLASK_ENV=production
SECRET_KEY=your-secret-key
DOCKER_ENV=1

# Database
DATABASE_URL=sqlite:////app/data/schulbuddy.db

# Security
SESSION_TIMEOUT_MINUTES=120
REMEMBER_COOKIE_DAYS=30
LOGIN_TIMEOUT_MINUTES=60
MAX_LOGIN_ATTEMPTS=5
LOGIN_ATTEMPT_TIMEOUT_MINUTES=15

# School year configuration
CURRENT_SCHOOL_YEAR=2025/26
CURRENT_SEMESTER=1
```

### Port configuration

The app supports flexible port configuration:

- `PORT`: Internal container port (default: 5000)
- `EXTERNAL_PORT`: External port for access (default: same as PORT)
- `HOST`: Bind address (default: 0.0.0.0)

### Docker image variants

- **latest**: Production/stable (main branch)
- **dev**: Development with latest features (dev branch)
- **vX.Y.Z**: Specific versions (tags)

### Supported architectures

All images support the following platforms:
- **linux/amd64**: Standard x86_64 (Intel/AMD)
- **linux/arm64**: 64-bit ARM (e.g. Apple Silicon, Raspberry Pi 4 64-bit)
- **linux/arm/v7**: 32-bit ARM (e.g. Raspberry Pi 2/3)

## 📖 Extended documentation

- [🔒 Security policy & CVE overview](SECURITY.md)
- [🐳 Docker guide](docs/DOCKER_README.md)
- [🏠 Full documentation](docs/INDEX.md)

## 🔧 Development

### Local development
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_db.py
python init_school_settings.py

# Start dev server
python app.py
```

### Docker development
```bash
# Use development image
TAG=dev docker-compose up -d

# Or local build for development
docker-compose -f docker-compose.yml up --build -d

# Follow logs
docker-compose logs -f schulbuddy
```

### Continuous Integration/Deployment

This project uses GitHub Actions for automated builds and deployments:

- **Docker Hub Publish**: Builds and publishes images on changes to `main`, `dev`, or tag pushes
- **GHCR Publish**: Builds and publishes images to GitHub Container Registry

Workflows are configured so that:
- Pushes to `main` update the `latest` tag
- Pushes to `dev` update the `dev` tag
- Tag pushes (v*) create corresponding version tags

## 🗄️ Database

- **Type**: SQLite
- **Location**: `instance/schulbuddy.db` (local) or `/app/data/schulbuddy.db` (Docker)
- **Persistence**: Docker volumes ensure data persistence
- **Backups**: Volume backups possible
- **Initialization**: Automatic on first container start

## 🔒 Security

- **Secure session management**: configurable timeouts
- **Password hashing**: secure hashing algorithms
- **2FA support**: TOTP-based two-factor authentication
- **Backup codes**: fallback for device loss
- **API keys**: secure API authentication with individual tokens
- **Rate limiting**: protection against brute-force attacks
- **CSRF protection**: built-in cross-site request forgery protection
- **Regular security updates**: automatic CVE monitoring and dependency updates
- **Container security**: least-privilege, non-root user, minimized attack surface
- **Vulnerability management**: documented risk assessment for non-fixable CVEs in [SECURITY.md](SECURITY.md)

## 🚀 Deployment

### Production deployment
```bash
# Quick start with prebuilt images
curl -O https://raw.githubusercontent.com/TimBoBN/schulbuddy/main/docker-compose.yml
curl -O https://raw.githubusercontent.com/TimBoBN/schulbuddy/main/config/.env.example
mv .env.example .env
# adjust .env

# Start services
TAG=latest docker-compose up -d

# Optional: Nginx reverse proxy
TAG=latest docker-compose --profile nginx up -d
```

### Deployment options

1. **Standalone Docker**: simple install with Docker Compose
2. **Platform-as-a-Service**: prebuilt images for platforms like Heroku or Render
3. **Platform-as-a-Service**: prebuilt images for platforms like Heroku or Render

### Monitoring
```bash
# Check service status
make status

# Show logs
make logs

# Resource usage
docker stats schulbuddy-app

# Health check
curl http://localhost:5000/health
```

### Docker health checks

The image contains built-in health checks that monitor the application and can trigger restarts on issues.

## 🔄 Updates and versions

### Version history

- **v1.3.0** (August 2025): container registry support, security improvements
- **v1.2.0** (July 2025): automated CI/CD pipeline, school year changeover
- **v1.1.0** (May 2025): statistics module, export features
- **v1.0.0** (March 2025): first stable release

### Update

```bash
# For Docker Hub installations
docker-compose pull
docker-compose up -d

# Or with a specific tag
TAG=v1.3.0 docker-compose up -d
```

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Contributions are welcome!

## 📞 Support

For questions or issues:

1. **Full documentation**: [docs/INDEX.md](docs/INDEX.md)
2. **Multi-architecture guide**: [docs/MULTI-ARCH-README.md](docs/MULTI-ARCH-README.md)
3. **Docker setup**: [docs/DOCKER_README.md](docs/DOCKER_README.md)
4. **Security**: [docs/SECURITY.md](docs/SECURITY.md)
5. **ARM support**: [docs/ARM_SUPPORT.md](docs/ARM_SUPPORT.md)
6. **GitHub Issues**: [Issues](../../issues)

## 📚 Documentation overview

| Topic | File | Description |
|-------|------|-------------|
| 🏠 **Main index** | [docs/INDEX.md](docs/INDEX.md) | Overview of all docs |
| 🏗️ **Multi-Arch** | [docs/MULTI-ARCH-README.md](docs/MULTI-ARCH-README.md) | AMD64 & ARM support |
| 🐳 **Docker setup** | [docs/DOCKER_README.md](docs/DOCKER_README.md) | Detailed installation |
| 🛡️ **Security** | [docs/SECURITY.md](docs/SECURITY.md) | Security guidelines |
| 🔋 **ARM support** | [docs/ARM_SUPPORT.md](docs/ARM_SUPPORT.md) | Raspberry Pi & Apple Silicon |

---

*Built with ❤️ for better school management*

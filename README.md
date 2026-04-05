# Local-LLM P-Grade (Secure Local Assistant)

A professional-grade, privacy-first local AI framework built for secure environments. It runs entirely on your local machine using **Ollama**, with zero data leakage to external APIs.

## 🛡️ Key Security Features
- **Local RBAC & Authentication**: Multi-user support with Argon2 password hashing.
- **Encrypted Storage**: Audit logs and sensitive data stored in **SQLCipher** (AES-256).
- **PII Masking Pipeline**: Automatic redaction of sensitive data (Emails, IPs, Names) before ingestion.
- **Semantic Guardrails**: Real-time hallucination detection and entailment checking.
- **Secure Knowledge Vault**: Per-user encrypted document storage with strict quota enforcement.

## 🚀 Quick Start (Docker - Recommended)

### Prerequisites
- [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/)
- [Ollama](https://ollama.com/) (Running on host machine)

### 1. Setup Environment
```bash
cp .env.example .env
# Edit .env with your local configuration
```

### 2. Build and Run
```bash
docker-compose up --build
```

## 🛠️ Local Development (Manual Setup)

### Prerequisites
- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (Recommended for dependency management)
- SQLCipher installed on your system

### 1. Install Dependencies
```bash
uv sync
```

### 2. Initialize the Secure Database
```bash
python src/init_db.py
```

### 3. Launch the TUI
```bash
python src/main.py
```

## 📊 Dashboard & Monitoring
The application features a multi-pane Terminal User Interface (TUI) providing:
- **A/B Testing**: Compare different models (e.g., Phi-3 vs TinyLlama) side-by-side.
- **Real-time Metrics**: Sparklines for response latency and token performance.
- **Security Visualization**: Live updates on PII redaction counts and audit triggers.
- **Prompt Watcher**: Hot-reloading of prompt templates without restarting the app.

## 📂 Project Structure
```text
├── src/
│   ├── security/      # Auth, RBAC, Vault, and Guardrails
│   ├── privacy/       # PII Masking and Redaction logic
│   ├── orchestration/ # A/B Engine and Model Management
│   ├── prompts/       # Versioned templates and hot-reloading
│   └── ui/            # Textual-based Dashboard
├── docs/              # Detailed specs and memory files
├── prompts/           # Hot-reloadable YAML templates
└── data/              # (Ignored) Encrypted local storage
```

## 📜 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

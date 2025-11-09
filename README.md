# 🔍 Codebase Analyzer

> **AI-powered tool that analyzes any codebase and generates comprehensive summaries using LLMs**

Supports **Java, Python, JavaScript, Go, Ruby, PHP, C#** and more. Produces clean JSON summaries with AI-generated method descriptions, complexity analysis, and intelligent recommendations.

---

## 🚀 Quick Start (3 Steps)

```bash
# 1. Setup (automated)
./setup.sh

# 2. Configure
cp env-example.txt .env
nano .env  # Add API key OR use free Ollama

# 3. Analyze
python main.py --path /path/to/your/project
```

**Done!** Results in `output/analysis_results.json` 📊

---

## ✨ Features

- 🌐 **Multi-Language** - Java, Python, JavaScript, Go, Ruby, PHP, C#
- 🤖 **AI-Powered** - OpenAI, Anthropic Claude, or local Ollama (FREE)
- 📊 **Smart Analysis** - Extracts only business logic, calculates complexity
- 🎯 **Concise Output** - Clean JSON summary, not verbose file dumps
- 🔧 **Auto-Detection** - Automatically identifies language & frameworks
- 💡 **AI Descriptions** - LLM-generated method descriptions & recommendations

---

## 📖 Table of Contents

- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage-examples)
- [Output Structure](#-output-structure)
- [Supported Languages](#-supported-languages)
- [Architecture](#-architecture)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)

---

## 💻 Installation

### Automated Setup (Recommended)

```bash
# macOS/Linux
./setup.sh

# Windows
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Manual Setup

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure
cp env-example.txt .env
```

**Requirements:**
- Python 3.8+
- API key (OpenAI/Anthropic) OR Ollama installed locally

---

## ⚙️ Configuration

### Option 1: Local Ollama (FREE, No API Key)

```bash
# Install Ollama
brew install ollama  # macOS
# or download from https://ollama.ai

# Pull a model
ollama pull codellama

# Configure .env
LLM_PROVIDER=ollama
OLLAMA_MODEL=codellama
OLLAMA_BASE_URL=http://localhost:11434
```

### Option 2: OpenAI (Cloud)

```bash
# Get API key from https://platform.openai.com/api-keys

# Configure .env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-your-key-here
OPENAI_MODEL=gpt-4o-mini
```

### Option 3: Anthropic Claude (Cloud)

```bash
# Get API key from https://console.anthropic.com

# Configure .env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your-key-here
ANTHROPIC_MODEL=claude-3-sonnet-20240229
```

### All Configuration Options

```bash
# LLM Provider
LLM_PROVIDER=ollama  # or openai, anthropic

# Ollama (local, FREE)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=codellama

# OpenAI (cloud, paid)
OPENAI_API_KEY=sk-proj-your-key
OPENAI_MODEL=gpt-4o-mini

# Anthropic (cloud, paid)
ANTHROPIC_API_KEY=your-key
ANTHROPIC_MODEL=claude-3-sonnet-20240229

# Analysis Settings
CODEBASE_PATH=./path/to/project
TARGET_LANGUAGE=auto  # or java, python, javascript, go, etc.
OUTPUT_PATH=./output/analysis_results.json
MAX_TOKENS_PER_CHUNK=8000
```

---

## 🎯 Usage Examples

### Basic Usage

```bash
# Analyze current directory (auto-detect language)
python main.py

# Analyze specific project
python main.py --path ../MyProject

# Specify language explicitly
python main.py --path ../MyApp --language python

# Custom output location
python main.py --path ../MyApp --output ./analysis.json
```

### Choose LLM Provider

```bash
# Use local Ollama (FREE)
python main.py --provider ollama --model codellama

# Use OpenAI
python main.py --provider openai --model gpt-4o-mini

# Use Anthropic Claude
python main.py --provider anthropic --model claude-3-sonnet-20240229
```

### Language-Specific Examples

#### Java Spring Boot
```bash
python main.py --path /path/to/spring-app --language java
# Detects: Spring Boot, Maven/Gradle, JPA entities
```

#### Python Django/Flask
```bash
python main.py --path /path/to/django-app --language python
# Detects: Django, Flask, FastAPI, requirements.txt
```

#### JavaScript/React
```bash
python main.py --path /path/to/react-app --language javascript
# Detects: React, Vue, Angular, Node.js, package.json
```

#### Go Projects
```bash
python main.py --path /path/to/go-app --language go
# Detects: Go modules, main packages
```

### View All Options

```bash
python main.py --help
```

---

### Key Differences from Other Tools

✅ **Only business logic** - No getters, setters, utilities  
✅ **Clean class names** - No package prefixes  
✅ **AI descriptions** - Every method gets an intelligent description  
✅ **Focused summary** - Not an exhaustive file dump  

---

## 🛠️ Supported Languages

| Language | Frameworks Detected | Config Files |
|----------|-------------------|--------------|
| **Java** | Spring Boot, Maven, Gradle | pom.xml, build.gradle |
| **Python** | Django, Flask, FastAPI | requirements.txt, setup.py |
| **JavaScript** | React, Vue, Angular, Express, Next.js | package.json |
| **TypeScript** | Same as JavaScript | package.json, tsconfig.json |
| **Go** | Go modules | go.mod |
| **Ruby** | Rails, Sinatra | Gemfile |
| **PHP** | Laravel, Symfony | composer.json |
| **C#** | .NET Core, .NET Framework | *.csproj |
| **Rust** | Cargo projects | Cargo.toml |

**Auto-Detection:** The tool automatically detects the language by scanning for config files and file extensions.

---

## 🏗️ Architecture

### System Overview

```
User CLI
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│                     main.py (CLI)                       │
│              (Thin entry point - 116 lines)             │
└────────┬────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│         analyzers/orchestrator.py (Pipeline)            │
│              (Main workflow coordination)                │
└────┬───────────────────────────────────────────────┬────┘
     │                                               │
     ├──────────────┬──────────────┬─────────────┬──┴────────┐
     │              │              │             │           │
     ▼              ▼              ▼             ▼           ▼
┌──────────┐  ┌──────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐
│ parsers/ │  │   llm/   │  │detectors│  │ utils/  │  │analyzers│
├──────────┤  ├──────────┤  ├─────────┤  ├─────────┤  ├─────────┤
│• Java    │  │• OpenAI  │  │• Lang   │  │• Method │  │• Stats  │
│  parser  │  │• Claude  │  │  detect │  │  extract│  │• Complex│
│• Config  │  │• Ollama  │  │• Project│  │• Output │  │• Aspects│
│  parser  │  │• Prompts │  │  info   │  │  format │  │• Compon.│
└──────────┘  └──────────┘  └─────────┘  └─────────┘  └─────────┘
     │              │              │             │           │
     └──────────────┴──────────────┴─────────────┴───────────┘
                                    │
                                    ▼
                           ┌─────────────────┐
                           │  JSON Output    │
                           │  (11 KB)        │
                           └─────────────────┘
```

### Project Structure

```
codebase-analyzer/
├── main.py                      # CLI entry point (116 lines)
├── config.py                    # Configuration management
├── models.py                    # Pydantic data models
│
├── analyzers/                   # 🎯 Analysis logic
│   ├── orchestrator.py          # Main workflow coordination
│   ├── statistics.py            # Statistics calculation
│   ├── components.py            # Component identification
│   ├── complexity.py            # Complexity analysis
│   └── aspects.py               # Noteworthy aspects detection
│
├── parsers/                     # 🔧 Code parsers
│   ├── java_parser.py           # Java AST parsing
│   └── config_parser.py         # Configuration file parsing
│
├── llm/                         # 🤖 LLM integration
│   └── analyzer.py              # OpenAI, Anthropic, Ollama wrapper
│
├── detectors/                   # 🔍 Detection logic
│   └── language_detector.py     # Language & framework detection
│
└── utils/                       # 🛠️ Utilities
    ├── method_extractor.py      # Business logic method extraction
    └── output_formatter.py      # JSON output formatting
```

### Components

#### Core
- **`main.py`** (116 lines) - Thin CLI entry point, argument parsing
- **`config.py`** - Environment-based configuration management
- **`models.py`** - Pydantic models for type-safe structured output

#### Analyzers (analyzers/)
- **`orchestrator.py`** - Main analysis pipeline coordinator
- **`statistics.py`** - Codebase statistics calculation & display
- **`components.py`** - Identifies controllers, services, repositories
- **`complexity.py`** - Code complexity metrics analysis
- **`aspects.py`** - Detects noteworthy codebase characteristics

#### Parsers (parsers/)
- **`java_parser.py`** - AST-based Java code parsing
- **`config_parser.py`** - Parses pom.xml, properties files

#### LLM (llm/)
- **`analyzer.py`** - Manages OpenAI, Anthropic, Ollama interactions

#### Detectors (detectors/)
- **`language_detector.py`** - Auto-detects language and frameworks

#### Utils (utils/)
- **`method_extractor.py`** - Extracts key business logic methods
- **`output_formatter.py`** - Formats and saves JSON output

### Design Patterns

- **Single Responsibility** - Each module has one clear purpose
- **Strategy Pattern** - Pluggable LLM providers (OpenAI, Anthropic, Ollama)
- **Template Method** - Analysis pipeline with customizable steps
- **Factory Pattern** - Parser selection based on detected language
- **Builder Pattern** - Incremental model construction with Pydantic
- **Separation of Concerns** - Clear boundaries between modules

For detailed architecture documentation, see [ARCHITECTURE.md](ARCHITECTURE.md).

---

## 🔧 Troubleshooting

### "Module not found" errors

```bash
# Re-run setup
./setup.sh

# Or manually install dependencies
pip install -r requirements.txt
```

### "OpenAI API key not found"

```bash
# Option 1: Add API key to .env
OPENAI_API_KEY=sk-proj-your-key-here

# Option 2: Switch to free Ollama
ollama pull codellama
python main.py --provider ollama
```

### "Model not found" error (OpenAI)

```bash
# Use a different model
python main.py --provider openai --model gpt-4o-mini
```

### Ollama connection refused

```bash
# Start Ollama server (in separate terminal)
ollama serve

# Then run analyzer
python main.py --provider ollama
```

### Empty or incorrect output

```bash
# Verify correct path
python main.py --path /absolute/path/to/project

# Check language detection
python main.py --path ../MyProject --language auto

# Enable verbose output (if available)
python main.py --path ../MyProject --verbose
```

### Permission errors (macOS)

```bash
# Give execution permission to scripts
chmod +x setup.sh run.sh

# Then run
./setup.sh
```

---

## 🤝 Contributing

Contributions welcome! Here's how to extend the analyzer:

### Add a New Language

1. Update `language_detector.py`:
```python
LANGUAGE_PATTERNS = {
    "newlang": {
        "extensions": ["**/*.nl"],
        "config_files": ["newlang.config"],
        "parser": "newlang"
    }
}
```

2. Create parser in `code_parser.py`:
```python
class NewLangCodeParser:
    def parse_file(self, file_path):
        # Implementation
```

3. Update `main.py` to use the new parser

### Add a New LLM Provider

1. Update `llm_integration.py`:
```python
elif config.LLM_PROVIDER == "newprovider":
    from newprovider import NewLLM
    return NewLLM(model=config.NEW_MODEL)
```

2. Add config in `config.py`:
```python
NEW_API_KEY: Optional[str] = os.getenv("NEW_API_KEY")
NEW_MODEL: str = os.getenv("NEW_MODEL", "default-model")
```

For detailed technical documentation, see [ARCHITECTURE.md](ARCHITECTURE.md).

---

## 📝 License

This project is provided as-is for educational and commercial use.

---

## 🆘 Support

- **Issues:** Open an issue on GitHub
- **Questions:** Check [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
- **API Keys:** See configuration section above

---

**Built with ❤️ for developers who want AI-powered codebase insights without the complexity**

# 🏗️ Architecture & Technical Documentation

Complete technical documentation for developers and contributors.

---

## Table of Contents

- [System Architecture](#system-architecture)
- [Components](#components)
- [Data Flow](#data-flow)
- [Design Patterns](#design-patterns)
- [Extension Points](#extension-points)
- [Performance](#performance)
- [Development Guide](#development-guide)

---

## System Architecture

### High-Level Overview

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
│   ├── __init__.py
│   ├── orchestrator.py          # Main workflow coordination (340 lines)
│   ├── statistics.py            # Statistics calculation (76 lines)
│   ├── components.py            # Component identification (44 lines)
│   ├── complexity.py            # Complexity analysis (32 lines)
│   └── aspects.py               # Noteworthy aspects (79 lines)
│
├── parsers/                     # 🔧 Code parsers
│   ├── __init__.py
│   ├── java_parser.py           # Java AST parsing (194 lines)
│   └── config_parser.py         # Configuration parsing (44 lines)
│
├── llm/                         # 🤖 LLM integration
│   ├── __init__.py
│   └── analyzer.py              # OpenAI, Anthropic, Ollama (247 lines)
│
├── detectors/                   # 🔍 Detection logic
│   ├── __init__.py
│   └── language_detector.py     # Language & framework detection (203 lines)
│
└── utils/                       # 🛠️ Utilities
    ├── __init__.py
    ├── method_extractor.py      # Method extraction (82 lines)
    └── output_formatter.py      # JSON formatting (63 lines)
```

### Architecture Layers

1. **Presentation Layer** - CLI interface (`main.py` - 116 lines)
2. **Orchestration Layer** - Pipeline coordination (`analyzers/orchestrator.py`)
3. **Business Logic Layer** - Focused analyzers (`analyzers/*.py`)
4. **Service Layer** - Parsers, detectors, LLM (`parsers/`, `detectors/`, `llm/`)
5. **Data Layer** - Pydantic models, JSON output (`models.py`, `utils/output_formatter.py`)

### Architecture Principles

**Single Responsibility Principle**  
Each module has ONE clear purpose. No God Objects.

**Separation of Concerns**  
Clear boundaries: parsing, analysis, LLM, output are isolated.

**Modularity**  
Easy to add new languages, analyzers, or LLM providers.

**Testability**  
Each module can be tested independently.

---

## Components

### 1. main.py - CLI Entry Point

**Responsibility:** Command-line interface and argument parsing

**Size:** 116 lines (80% smaller than before!)

**Key Functions:**
- `parse_arguments()` - CLI argument parsing
- `main()` - Entry point, config override, analyzer invocation

**Arguments:**
- `--path` / `-p` - Codebase path
- `--language` / `-l` - Target language
- `--provider` - LLM provider (openai/anthropic/ollama)
- `--output` / `-o` - Output file path
- `--model` - Specific model to use

---

### 2. analyzers/ - Analysis Logic

#### analyzers/orchestrator.py - Main Pipeline

**Responsibility:** Coordinates the entire analysis pipeline

**Size:** 340 lines

**Key Class:** `CodebaseAnalyzer`

**Pipeline Steps:**
1. Detect language and frameworks
2. Discover and parse source files
3. Generate project overview (LLM)
4. Calculate statistics
5. Identify key components
6. Extract key business logic methods
7. Generate method descriptions (LLM)
8. Analyze code complexity
9. Identify noteworthy aspects
10. Generate recommendations (LLM)
11. Save structured JSON output

**Key Methods:**
- `run()` - Main pipeline execution
- `_detect_language()` - Language identification
- `_discover_and_parse_files()` - File discovery and parsing
- `_analyze_overview()` - LLM-powered overview
- `_generate_recommendations()` - Improvement suggestions
- `_create_generic_file_info()` - Basic file parsing

#### analyzers/statistics.py - Statistics Calculation

**Responsibility:** Calculate and display codebase statistics

**Size:** 76 lines

**Key Class:** `StatisticsAnalyzer`

**Methods:**
- `calculate(files)` - Compute metrics (lines, classes, methods, etc.)
- `display(stats)` - Show statistics in Rich table

**Metrics:**
- Total files, lines, code lines
- Total classes, business logic methods
- File type distribution
- Averages (file size, methods per class)

#### analyzers/components.py - Component Identification

**Responsibility:** Identify architectural components

**Size:** 44 lines

**Key Class:** `ComponentAnalyzer`

**Methods:**
- `identify(files)` - Categorize classes by type

**Component Types:**
- Controllers
- Services
- Repositories
- Entities
- Configurations

#### analyzers/complexity.py - Complexity Analysis

**Responsibility:** Analyze code complexity

**Size:** 32 lines

**Key Class:** `ComplexityAnalyzer`

**Methods:**
- `analyze(files)` - Calculate complexity metrics

**Metrics:**
- Average, max, min complexity
- High complexity files (>10)

#### analyzers/aspects.py - Noteworthy Aspects

**Responsibility:** Identify interesting codebase characteristics

**Size:** 79 lines

**Key Class:** `AspectAnalyzer`

**Methods:**
- `identify(statistics, complexity, components)` - Generate insights

**Aspects:**
- Architecture observations
- Complexity assessment
- Codebase size analysis
- Security configurations

---

### 3. parsers/ - Code Parsers

#### parsers/java_parser.py - Java Parser

**Responsibility:** Parse Java source code using AST

**Size:** 194 lines

**Key Class:** `JavaCodeParser`

**Methods:**
- `parse_file(file_path)` - Parse Java file
- `_parse_class(node)` - Extract class information
- `_parse_method(node)` - Extract method information
- `_is_business_logic_method()` - Filter business logic
- `_calculate_complexity()` - Use Lizard for complexity

**Extracted:**
- Package, imports, annotations
- Classes with methods
- Method signatures
- Complexity metrics

#### parsers/config_parser.py - Configuration Parser

**Responsibility:** Parse configuration files

**Size:** 44 lines

**Key Class:** `ConfigFileParser`

**Methods:**
- `parse_pom(file_path)` - Parse Maven pom.xml
- `parse_properties(file_path)` - Parse .properties files

---

### 4. llm/ - LLM Integration

#### llm/analyzer.py - LLM Wrapper

**Responsibility:** Manage LLM interactions

**Size:** 247 lines

**Key Class:** `LLMAnalyzer`

**Supported Providers:**
- OpenAI (GPT-4, GPT-3.5, GPT-4o-mini)
- Anthropic (Claude 3)
- Ollama (CodeLlama, Llama 2, etc.)

**Methods:**
- `analyze_project_overview()` - Generate project summary
- `generate_method_description()` - Create method descriptions
- `generate_recommendations()` - Suggest improvements
- `_query_llm()` - Generic LLM interaction
- `_parse_response_to_dict()` - Fallback parser

---

### 5. detectors/ - Language Detection

#### detectors/language_detector.py - Language Detector

**Responsibility:** Identify programming language, frameworks, and project metadata

**Size:** 203 lines

**Key Class:** `LanguageDetector`

**Detection Strategy:**
1. **Config File Scanning** - Checks for language-specific files:
   - `pom.xml` → Java + Maven
   - `package.json` → JavaScript/TypeScript + npm
   - `requirements.txt` → Python + pip
   - `go.mod` → Go
   - `Gemfile` → Ruby
   - `composer.json` → PHP
   - `Cargo.toml` → Rust

2. **File Extension Counting** - Counts source files by extension
3. **Framework Detection** - Scans config files for framework keywords

**Methods:**
- `detect_language()` - Returns primary language
- `detect_project_info()` - Returns dict with language, frameworks, build tools
- `get_project_name()` - Extracts project name from config files

**Supported Languages:**
- Java, Python, JavaScript, TypeScript
- Go, Ruby, PHP, C#, Rust, Swift, Kotlin, Scala

---

### 6. utils/ - Utility Functions

#### utils/method_extractor.py - Method Extraction

**Responsibility:** Extract key business logic methods with AI descriptions

**Size:** 82 lines

**Key Class:** `MethodExtractor`

**Methods:**
- `extract(files, key_components)` - Extract and describe methods

**Process:**
1. Filter methods from controllers and services only
2. Skip non-business-logic methods (getters/setters)
3. Generate AI descriptions for each method using LLM
4. Return KeyMethodSummary objects

**Business Logic Filtering:**

**❌ Excluded:**
- Getters: `getName()`, `getId()`
- Setters: `setName()`, `setId()`
- Boolean accessors: `isActive()`, `hasPermission()`
- Utility methods: `equals()`, `hashCode()`, `toString()`, `clone()`

**✅ Included:**
- Controller endpoints: `@GetMapping`, `@PostMapping`, `@RequestMapping`
- Service operations: `save()`, `find()`, `delete()`, `update()`
- Business operations: `rentFilm()`, `calculateTotal()`, `processPayment()`
- Methods with `@Transactional`, `@Async` annotations

#### utils/output_formatter.py - Output Formatting

**Responsibility:** Format and save JSON output

**Size:** 63 lines

**Key Class:** `OutputFormatter`

**Methods:**
- `save(analysis, output_path)` - Save analysis to JSON
- `_convert_sets_to_lists(obj)` - JSON serialization helper

**Features:**
- Adds metadata (timestamp, version, LLM provider)
- Converts Python sets to lists for JSON compatibility
- Pretty-prints with 2-space indentation
- UTF-8 encoding for international characters

---

### 7. config.py - Configuration Management

**Responsibility:** Centralized configuration from environment variables

**Size:** 109 lines

**Key Class:** `Config`

**Configuration Categories:**

1. **LLM Configuration**
   - Provider selection (OpenAI/Anthropic/Ollama)
   - API keys
   - Model names
   - Base URLs

2. **Analysis Configuration**
   - Codebase path
   - Output path
   - Target language
   - Token limits

3. **File Patterns**
   - Include patterns by language
   - Exclude patterns (node_modules, venv, etc.)
   - Language-specific patterns

**Key Methods:**
- `validate()` - Validates required configuration

---

### 8. models.py - Data Models

**Responsibility:** Type-safe structured output using Pydantic

**Size:** 81 lines

**Pydantic Models:**

1. **MethodInfo** - Method details
   - name, signature, description
   - return_type, complexity, annotations
   - is_business_logic flag

2. **ClassInfo** - Class structure (internal use)
   - name, package, annotations
   - methods list

3. **FileInfo** - File information (internal use)
   - file_path, file_type, package
   - classes, imports
   - line counts, complexity

4. **ProjectOverview** - High-level summary
   - project_name, description, purpose
   - key_technologies, architecture_pattern
   - main_features, dependencies

5. **KeyMethodSummary** - Business logic method (output)
   - class_name, method_name, signature
   - description, annotations, component_type

6. **CodebaseAnalysis** - Complete result (output)
   - overview, statistics, key_methods
   - key_components, complexity_summary
   - recommendations, noteworthy_aspects

**Benefits:**
- Type safety and validation
- Auto-generates JSON schema
- IDE autocomplete support
- Runtime validation

---

## Data Flow

### Complete Analysis Flow

```
1. CLI Input
   ├─ Parse arguments
   └─ Load configuration

2. Language Detection
   ├─ Scan for config files (pom.xml, package.json, etc.)
   ├─ Count file extensions
   └─ Identify frameworks

3. File Discovery & Parsing
   ├─ Glob files by detected language patterns
   ├─ Parse each file with AST
   ├─ Extract classes, methods, annotations
   ├─ Calculate cyclomatic complexity
   └─ Filter business logic methods

4. LLM Analysis (Parallel calls)
   ├─ Project overview generation
   └─ Method descriptions generation (28 calls)

5. Metrics Calculation
   ├─ Count files, lines, classes, methods
   ├─ Compute averages
   └─ Categorize components

6. Insights Generation
   ├─ Identify noteworthy aspects
   ├─ Analyze complexity patterns
   └─ Generate recommendations

7. Output Generation
   ├─ Build Pydantic models
   ├─ Convert to JSON
   └─ Save to file (11 KB)
```

---

## Design Patterns

### 1. Strategy Pattern - LLM Providers

Different LLM implementations share a common interface:

```python
# Strategy interface (implicit)
def _initialize_llm():
    if config.LLM_PROVIDER == "openai":
        return ChatOpenAI(...)
    elif config.LLM_PROVIDER == "anthropic":
        return ChatAnthropic(...)
    elif config.LLM_PROVIDER == "ollama":
        return OllamaLLM(...)
```

**Benefits:** Easy to swap LLM providers without changing business logic

### 2. Template Method - Analysis Pipeline

`CodebaseAnalyzer.run()` defines the skeleton, subcomponents fill in details:

```python
def run():
    detect_language()      # Step defined
    parse_files()          # Step defined
    analyze_overview()     # Step defined
    extract_methods()      # Step defined
    analyze_complexity()   # Step defined
    generate_recommendations()  # Step defined
    save_results()         # Step defined
```

**Benefits:** Consistent workflow, easy to modify individual steps

### 3. Factory Pattern - Parser Selection

```python
if source_file.suffix == '.java':
    file_info = self.java_parser.parse_file(source_file)
elif source_file.suffix == '.py':
    file_info = self._create_generic_file_info(source_file, 'python')
```

**Benefits:** Automatic parser selection based on file type

### 4. Builder Pattern - Model Construction

Pydantic models build complex structures incrementally:

```python
analysis = CodebaseAnalysis(
    overview=overview,
    statistics=statistics,
    key_methods=key_methods,
    ...
)
```

**Benefits:** Clear, validated object construction

---

## Extension Points

### Adding a New Language

**1. Update `language_detector.py`:**

```python
LANGUAGE_PATTERNS = {
    "rust": {
        "extensions": ["**/*.rs"],
        "config_files": ["Cargo.toml"],
        "parser": "rust"
    }
}
```

**2. Create parser in `code_parser.py`:**

```python
class RustCodeParser:
    def parse_file(self, file_path: Path) -> Optional[FileInfo]:
        # Use rust parser library (e.g., tree-sitter-rust)
        # Extract classes (structs), methods (impl blocks)
        # Return FileInfo object
```

**3. Update `main.py` to use new parser:**

```python
elif source_file.suffix == '.rs':
    file_info = self.rust_parser.parse_file(source_file)
```

### Adding a New LLM Provider

**1. Update `llm_integration.py`:**

```python
elif config.LLM_PROVIDER == "groq":
    from langchain_groq import ChatGroq
    return ChatGroq(
        model=config.GROQ_MODEL,
        api_key=config.GROQ_API_KEY
    )
```

**2. Add config in `config.py`:**

```python
GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
GROQ_MODEL: str = os.getenv("GROQ_MODEL", "mixtral-8x7b")
```

**3. Update `env-example.txt`:**

```bash
# Groq Settings
GROQ_API_KEY=your-key-here
GROQ_MODEL=mixtral-8x7b
```

---

## Performance

### Metrics

- **File Parsing:** O(n) where n = number of files
- **LLM Calls:** ~28-30 calls (1 overview + 28 methods)
- **Memory:** Holds all file data in memory (~10 MB for 2635 lines)
- **Execution Time:**
  - OpenAI: ~30-60 seconds
  - Ollama: ~2-5 minutes (depends on hardware)

### Optimization Strategies

1. **Parallel LLM Calls:** Could parallelize method descriptions
2. **Caching:** Cache LLM responses for unchanged methods
3. **Streaming:** Process files in streaming fashion for large codebases
4. **Incremental Updates:** Only analyze changed files

### Limitations

- **Max Codebase Size:** ~50MB source code (memory constraint)
- **Max Files:** ~10,000 files (reasonable performance)
- **LLM Token Limits:** Automatic truncation at 8000 tokens per chunk

---

## Development Guide

### Project Structure

```
codebase-analyzer/
├── main.py                 # Entry point & orchestrator
├── config.py               # Configuration
├── models.py               # Pydantic data models
├── code_parser.py          # Source code parsing
├── llm_integration.py      # LLM interactions
├── language_detector.py    # Language detection
├── requirements.txt        # Python dependencies
├── setup.sh                # Automated setup script
├── .env                    # Configuration (git-ignored)
├── .gitignore              # Git ignore rules
├── README.md               # User documentation
├── ARCHITECTURE.md         # This file
└── output/                 # Analysis results
    └── analysis_results.json
```

### Code Style

- **PEP 8** compliance
- **Type hints** throughout
- **Docstrings** for all public methods
- **4-space indentation**
- **Max line length:** ~100 characters

### Testing Strategy

```bash
# Unit tests (to be added)
pytest tests/

# Integration test
python main.py --path ../SakilaProject

# Verify output
cat output/analysis_results.json | jq
```

### Error Handling

- **File not found:** Skip with warning, continue
- **Parse errors:** Use basic file info, continue
- **LLM errors:** Log error, set description to null
- **API errors:** Clear message with remediation hint

### Logging

Currently uses `rich` for colored console output:
- Step progress indicators
- Spinner for long operations
- Tables for statistics
- Success/error messages 

---

## Future Enhancements
- [ ] Parallel LLM calls for faster analysis
- [ ] Support for more languages (Kotlin, Swift, Scala)
- [ ] Incremental analysis (only changed files)
- [ ] HTML/PDF report generation
- [ ] Integration with CI/CD pipelines
- [ ] Code quality scoring
- [ ] Security vulnerability detection
- [ ] Dependency analysis and outdated package detection

---

**For questions or contributions, see the main [README.md](README.md)**

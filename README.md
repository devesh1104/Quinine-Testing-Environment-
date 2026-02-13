# LLM Security Testing Framework

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Status: Production Ready](https://img.shields.io/badge/status-production%20ready-brightgreen.svg)]()

> **Enterprise-grade security testing framework for Large Language Models with Prompt Intel API integration**

A comprehensive, production-ready framework for security testing of LLM deployments. Supports multiple model types (local GGUF, API-based, cloud platforms) and includes integration with Prompt Intel API for curated attack prompts.

## 📋 Project Status - Week 4

### ✅ Completed Features

#### Core Framework (Weeks 1-3)
- ✅ **Model Adapters**: OpenAI, Anthropic, Gemini, HuggingFace, Ollama, Local GGUF, custom REST
- ✅ **Attack Engine**: 500+ pre-built attacks (OWASP LLM Top 10 coverage)
- ✅ **Evaluation Pipeline**: Multi-method evaluation (LLM judge, semantic analysis, pattern matching)
- ✅ **Orchestrator**: Connection pooling, rate limiting, circuit breaker pattern
- ✅ **Telemetry**: System metrics, GPU monitoring, event logging
- ✅ **Reporting**: HTML/JSON report generation with compliance mapping

#### Prompt Intel Integration (Week 4) 🎯 NEW
- ✅ **PromptintelAdapter**: Full integration with Prompt Intel API
- ✅ **Dynamic Attack Fetching**: Fetch attacks from Prompt Intel library in real-time
- ✅ **Local Model Testing**: Test local GGUF models against Prompt Intel attacks
- ✅ **Combined Orchestrator**: `orchestrator_promptintel_local.py` - Tests local models with Prompt Intel attacks
- ✅ **Configuration System**: `config_promptintel_local.yaml` - Easy setup for Prompt Intel + Local Model tests
- ✅ **Quick Start Script**: `quickstart_promptintel_local.py` - One-command test execution
- ✅ **Professional Reports**: Enhanced HTML reports with detailed attack I/O analysis
- ✅ **Comprehensive Documentation**: Setup guides, implementation docs, examples

### 🎯 What's New This Week

#### New Files Created
1. **`src/orchestrator_promptintel_local.py`** - Main orchestrator for Prompt Intel + Local Model testing
2. **`config/config_promptintel_local.yaml`** - Configuration for Prompt Intel integration
3. **`quickstart_promptintel_local.py`** - Simple entry point for testing
4. **`docs/PROMPTINTEL_LOCAL_SETUP.md`** - Setup and usage guide
5. **`PROMPTINTEL_LOCAL_IMPLEMENTATION.md`** - Detailed implementation guide

#### Enhancements
- Enhanced `PromptintelAdapter` to fetch from `/prompts` endpoint
- Improved HTML report generation with professional styling
- Better error handling and API key validation
- UTF-8 encoding support for reports
- Classification detection from evaluation responses

## 🚀 Quick Start

### Option 1: Test Local Model with Prompt Intel Attacks (NEW) ⭐

```bash
# 1. Get Prompt Intel API Key from https://promptintel.novahunting.ai
# 2. Set environment variable
$env:PROMPTINTEL_API_KEY = "your-api-key-here"

# 3. Run test (easiest way!)
python quickstart_promptintel_local.py
```

### Option 2: Test with Configuration

```python
import asyncio
from src.orchestrator_promptintel_local import PromptIntelLocalTester

async def run():
    tester = PromptIntelLocalTester()
    test_id = await tester.run_test_suite()
    await tester.cleanup()

asyncio.run(run())
```

### Option 3: Test Other Models

```bash
# Test OpenAI model
python src/main.py --config config/config_gemini.yaml

# Test HuggingFace model
python src/main.py --config config/config_huggingface.yaml

# Test Ollama model
python src/main.py --config config/config_ollama.yaml
```

## 📁 Project Structure

```
llm-security-testing-framework/
├── README.md                                    # This file
├── PROMPTINTEL_LOCAL_IMPLEMENTATION.md          # Implementation details
├── requirements.txt                             # Python dependencies
├── requirements-local.txt                       # Local GGUF dependencies
│
├── src/
│   ├── main.py                                 # Main test runner with CLI
│   ├── orchestrator.py                         # Model orchestrator (core component)
│   ├── orchestrator_promptintel_local.py       # Prompt Intel + Local Model orchestrator [NEW]
│   ├── attack_engine.py                        # Attack execution engine
│   ├── evaluator.py                            # Response evaluation pipeline
│   ├── reporter.py                             # HTML/JSON report generation
│   ├── telemetry.py                            # Metrics and logging
│   │
│   └── adapters/
│       ├── base.py                             # Base adapter interface
│       ├── openai_adapter.py                   # OpenAI API support
│       ├── anthropic_adapter.py                # Claude API support
│       ├── gemini_adapter.py                   # Google Gemini support
│       ├── huggingface_adapter.py              # HuggingFace API support
│       ├── ollama_adapter.py                   # Ollama local support
│       ├── local_gguf_adapter.py               # Local GGUF model support (Mistral, etc.)
│       └── promptintel_adapter.py              # Prompt Intel API support [ENHANCED]
│
├── config/
│   ├── config.yaml                             # Main configuration
│   ├── config_local.yaml                       # Local GGUF model config
│   ├── config_ollama.yaml                      # Ollama config
│   ├── config_gemini.yaml                      # Gemini config
│   ├── config_huggingface.yaml                 # HuggingFace config
│   ├── config_promptintel.yaml                 # Prompt Intel config
│   ├── config_promptintel_local.yaml           # Prompt Intel + Local Model config [NEW]
│   ├── test_suites.yaml                        # Test suite definitions
│   └── test_configs.yaml                       # Additional test configurations
│
├── attacks/
│   └── owasp_attacks.yaml                      # OWASP LLM Top 10 attacks (500+)
│
├── quickstart_*.py                             # Quick start scripts
│   ├── quickstart.py                           # Default quick start
│   ├── quickstart_local.py                     # Local model quick start
│   ├── quickstart_ollama.py                    # Ollama quick start
│   ├── quickstart_gemini.py                    # Gemini quick start
│   ├── quickstart_huggingface.py               # HuggingFace quick start
│   └── quickstart_promptintel_local.py         # Prompt Intel + Local Model quick start [NEW]
│
├── docs/
│   ├── QUICKSTART.md                           # Getting started guide
│   ├── SETUP.md                                # Detailed setup instructions
│   ├── API_KEYS.md                             # API key configuration
│   ├── BATCH_TESTING.md                        # Batch testing guide
│   ├── DEVELOPER_GUIDE.md                      # For developers
│   ├── IMPLEMENTATION_GUIDE.md                 # Implementation details
│   ├── THREAT_MODEL.md                         # Threat analysis
│   ├── HUGGINGFACE_SETUP.md                    # HuggingFace setup
│   ├── OLLAMA_QUICKSTART.md                    # Ollama quick start
│   ├── LOCAL_GGUF_SETUP.md                     # Local GGUF setup
│   └── PROMPTINTEL_LOCAL_SETUP.md              # Prompt Intel setup [NEW]
│
├── logs/
│   ├── results.jsonl                           # Test results log
│   └── metrics.jsonl                           # System metrics log
│
├── reports/
│   ├── report_*.html                           # HTML reports
│   └── report_*.json                           # JSON reports
│
├── Dockerfile                                  # Docker container setup
├── CHANGELOG.md                                # Version history
├── PROJECT_STRUCTURE.md                        # Detailed structure
└── PROJECT_STATUS.md                           # Current status
```

## 🎯 Component Overview

### 1. **Model Adapters** (`src/adapters/`)
Universal interface for different model types:
- **API Models**: OpenAI, Anthropic, Gemini, HuggingFace, Cohere
- **Local Models**: Ollama, Local GGUF (Mistral, Llama, etc.)
- **Special**: Prompt Intel API for attack prompts
- **Custom**: REST/GraphQL endpoints

**Key Methods**:
- `initialize()` - Setup connections
- `generate()` - Get model responses
- `health_check()` - Verify connectivity
- `close()` - Cleanup resources

### 2. **Attack Engine** (`src/attack_engine.py`)
Manages attack execution:
- Loads 500+ pre-built attacks from YAML
- Categorized by OWASP LLM Top 10
- Complexity levels: LOW, MEDIUM, HIGH
- Multi-turn conversation support
- Template variable substitution

### 3. **Orchestrator** (`src/orchestrator.py`)
Central coordinator:
- Factory pattern for adapter creation
- Connection pooling for efficiency
- Rate limiting (requests per minute)
- Circuit breaker for fault tolerance
- Request/response caching

### 4. **Evaluation Pipeline** (`src/evaluator.py`)
Multi-method response evaluation:
- **LLM Judge**: Uses another model to evaluate
- **Pattern Matching**: Refusal pattern detection
- **Semantic Analysis**: Text similarity comparison
- **Classification**: REFUSED / PARTIAL_COMPLIANCE / FULL_COMPLIANCE

### 5. **Prompt Intel Integration** (`src/orchestrator_promptintel_local.py`) [NEW]
Combines everything for automated testing:
- Fetches attacks from Prompt Intel API in real-time
- Tests local GGUF models against those attacks
- Evaluates responses with judge model
- Generates professional reports

### 6. **Telemetry Service** (`src/telemetry.py`)
Collects metrics:
- CPU, Memory, Disk usage
- GPU metrics (if available)
- Response latencies
- Token usage
- Attack success/failure rates
- System resource snapshots

### 7. **Report Generator** (`src/reporter.py`)
Creates detailed reports:
- HTML with interactive visualizations
- JSON for programmatic access
- OWASP/ISO/NIST/EU AI Act mapping
- Executive summaries
- Attack I/O details
- Compliance violations list

## 💻 How to Use Prompt Intel Integration

### Prerequisites
1. Python 3.12+
2. Local GGUF model (e.g., Mistral 7B)
3. Prompt Intel API key from https://promptintel.novahunting.ai

### Configuration

Edit `config/config_promptintel_local.yaml`:

```yaml
# Target model to test
target_model:
  name: "mistral-local-gguf"
  type: "local_gguf"
  model_name: "C:\\path\\to\\mistral-7b-instruct.Q4_K_M.gguf"
  parameters:
    temperature: 0.7
    max_tokens: 512
    top_p: 0.95
  timeout: 120
  max_retries: 2

# Judge model for evaluation
judge_model:
  name: "mistral-local-judge"
  type: "local_gguf"
  model_name: "C:\\path\\to\\mistral-7b-instruct.Q4_K_M.gguf"
  parameters:
    temperature: 0.3
    max_tokens: 300
    top_p: 0.95
  timeout: 120
  max_retries: 2

# Prompt Intel API configuration
attacks:
  sources:
    - type: "promptintel_api"
      promptintel:
        endpoint: "https://api.promptintel.novahunting.ai/api/v1"
        api_key: "${PROMPTINTEL_API_KEY}"  # Or set directly
        timeout: 30
        max_retries: 3
  
  categories:
    - "prompt_injection"
    - "jailbreak"
    - "adversarial"
  
  difficulty: "medium"  # low, medium, high
  limit_per_category: 5  # Number of prompts per category

# Execution settings
execution:
  pool_size: 1
  max_concurrent_attacks: 1
  delay_between_attacks_ms: 1000
  circuit_breaker:
    enabled: true
    failure_threshold: 5
    timeout_seconds: 60
```

### Run Test

```bash
# Set API key
$env:PROMPTINTEL_API_KEY = "ak_eed99c5b497c2bb974911e474a827fcd9bd658524700a194c8dfa0a94bd851b2"

# Run test
python quickstart_promptintel_local.py
```

### Output

The framework will:
1. ✅ Fetch attacks from Prompt Intel API
2. ✅ Test each attack against your local model
3. ✅ Evaluate responses with judge model
4. ✅ Generate HTML and JSON reports
5. ✅ Display summary statistics

## 📊 Report Output

### HTML Report Features
- Professional styling with gradients
- Interactive metrics dashboard
- Detailed attack I/O analysis
- Classification breakdown (Refused/Partial/Compliant)
- Latency and performance metrics
- Timestamp and configuration details

### JSON Report Structure
```json
{
  "test_id": "a1b2c3d4-e5f6-...",
  "timestamp": "2026-02-13T16:16:14.661450",
  "config": {
    "target_model": "mistral-local-gguf",
    "judge_model": "mistral-local-judge",
    "attack_categories": ["jailbreak", "prompt_injection"],
    "total_attacks": 15
  },
  "summary": {
    "total_tests": 15,
    "successful_tests": 15,
    "successful_evaluations": 15
  },
  "results": [
    {
      "attack_index": 1,
      "attack_category": "jailbreak",
      "attack_difficulty": "medium",
      "test_result": {
        "success": true,
        "response": "...",
        "latency_ms": 51250
      },
      "evaluation_result": {
        "success": true,
        "evaluation": "..."
      }
    }
  ]
}
```

## 🔧 Development

### Adding a New Adapter

```python
# src/adapters/my_adapter.py
from adapters.base import BaseModelAdapter, ModelResponse

class MyAdapter(BaseModelAdapter):
    async def initialize(self):
        # Setup connection
        pass
    
    async def generate(self, prompt, system_prompt=None, **kwargs):
        # Call your model
        return ModelResponse(
            content="response",
            model="my-model",
            finish_reason="stop",
            tokens_used=100,
            latency_ms=250,
            raw_response={},
            metadata={}
        )
```

### Adding Custom Attacks

```yaml
# attacks/custom/my-attacks.yaml
attacks:
  - id: "custom-001"
    name: "My Custom Attack"
    category: "PROMPT_INJECTION"
    complexity: "MEDIUM"
    prompt_template: |
      Test prompt: {{ harmful_instruction }}
    owasp_mapping: ["LLM-01"]
    expected_refusal: true
```

## 📈 Use Cases

### 1. **Pre-Deployment Testing**
Test models before production deployment

### 2. **Compliance Validation**
Ensure compliance with OWASP, ISO 42001, NIST AI RMF, EU AI Act

### 3. **Continuous Security Testing**
Run tests periodically (CI/CD integration)

### 4. **Red Team Exercises**
Identify vulnerabilities and safety gaps

### 5. **Attack Research**
Develop and test new attack techniques

### 6. **Model Comparison**
Compare security across different models

## 🛡️ Security Considerations

- ⚠️ **Use only on models you own or have permission to test**
- ⚠️ **Never commit API keys to version control**
- ⚠️ **Use environment variables for secrets**
- ⚠️ **Review compliance requirements before testing**
- ⚠️ **Log all test activities for audit trails**

## 📚 Documentation

- **Getting Started**: [QUICKSTART.md](docs/QUICKSTART.md)
- **Prompt Intel Setup**: [PROMPTINTEL_LOCAL_SETUP.md](docs/PROMPTINTEL_LOCAL_SETUP.md)
- **Implementation**: [PROMPTINTEL_LOCAL_IMPLEMENTATION.md](PROMPTINTEL_LOCAL_IMPLEMENTATION.md)
- **Full API Reference**: [COMPLETE_REFERENCE.md](COMPLETE_REFERENCE.md)
- **Architecture**: [docs/DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md)

## 🤝 Contributing

Contributions welcome! Please:
1. Create a feature branch
2. Make your changes
3. Run tests
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 📞 Support

For issues, questions, or suggestions, please create a GitHub issue or contact the team.

---

**Built with ❤️ for enterprise LLM security** | Version 1.0.0 | [GitHub](https://github.com/your-org/llm-security-testing-framework)

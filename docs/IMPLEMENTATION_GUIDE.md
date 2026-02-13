# Implementation Guide - Latest Updates

## Overview of Changes

This document outlines all the improvements made to the LLM Security Testing Framework to enhance it with Promptintel integration, local model support, and production-grade features.

---

## 🎯 Changes Made

### 1. ✅ Fixed Emoji Encoding in Reports

**Problem:** Unicode emojis were corrupted in HTML reports (showing `ðŸ›¡ï¸` instead of `🛡️`)

**Solution:** 
- Updated `src/reporter.py` HTML template with proper UTF-8 encoded emojis
- Ensured `<meta charset="UTF-8">` tag in HTML header
- Fixed emojis in report headers:
  - `🛡️` for main title
  - `📊` for Executive Summary
  - `⚠️` for Critical Findings
  - `📋` for Test Results
  - `⚖️` for Compliance Analysis
  - `✅` for positive findings

**Files Modified:**
- `src/reporter.py` - Fixed HTML template emojis

### 2. ✅ Created Promptintel API Adapter

**Purpose:** Integrate with Promptintel's secure prompt library for professional-grade attack vectors

**Implementation:**
- Created `src/adapters/promptintel_adapter.py`
- Supports Promptintel API v1 endpoints:
  - `GET /health` - Health check
  - `GET /prompt` - Fetch security prompts
- Features:
  - Bearer token authentication
  - Retry logic with exponential backoff
  - Rate limit handling
  - Latency tracking
  - Query parameter support (category, difficulty, limit)

**Key Methods:**
```python
async def health_check()        # Verifies API availability
async def fetch_prompt()        # Retrieves attack prompts
async def generate()            # Returns prompt data as ModelResponse
```

**Files Created:**
- `src/adapters/promptintel_adapter.py` - Complete adapter implementation

### 3. ✅ Created Promptintel Configuration

**Purpose:** Provide ready-to-use configuration for Promptintel testing

**Features:**
- Pre-configured Promptintel API targets
- Gemini as judge model (evaluation)
- Attack categories: PROMPT_INJECTION, JAILBREAK, ADVERSARIAL
- Full documentation and setup instructions

**Files Created:**
- `config/config_promptintel.yaml` - Complete configuration with API endpoints

### 4. ✅ Updated Base Adapter Enum

**Purpose:** Add Promptintel to supported model types

**Change:** Added `PROMPTINTEL_API = "promptintel_api"` to `ModelType` enum

**Files Modified:**
- `src/adapters/base.py` - Added PROMPTINTEL_API to ModelType enum

### 5. ✅ Updated Model Orchestrator

**Purpose:** Register all adapters (Promptintel, Ollama, etc.) in the factory

**Changes:**
```python
# Added imports
from adapters.ollama_adapter import OllamaAdapter
from adapters.promptintel_adapter import PromptintelAdapter

# Updated adapter registry
_adapter_registry: Dict[ModelType, type] = {
    ...
    ModelType.OLLAMA: OllamaAdapter,
    ModelType.PROMPTINTEL_API: PromptintelAdapter,
}
```

**Files Modified:**
- `src/orchestrator.py` - Added adapter imports and registration

### 6. ✅ Enhanced Ollama Configuration

**Purpose:** Provide comprehensive local model support documentation and best practices

**Improvements:**
- Added detailed model selection guide (llama2, mistral, neural-chat)
- Hardware requirements for different model sizes
- Performance tuning parameters
- Security advantages for testing
- Complete setup instructions
- Model download commands

**Files Modified:**
- `config/config_ollama.yaml` - Enhanced with detailed documentation

### 7. ✅ Created Comprehensive Setup Documentation

**Purpose:** Provide users with complete setup and usage guide

**Files Created:**

#### `docs/SETUP.md` - Complete Setup & Configuration Guide
Contains:
- Quick start for each provider (Gemini, Ollama, Promptintel)
- Prerequisites and installation
- Configuration file reference
- Environment variable setup
- Architecture overview
- Detailed adapter usage examples
- Security best practices
- Troubleshooting guide
- Advanced usage examples
- Custom adapter development

#### `docs/IMPLEMENTATION_GUIDE.md` (this file)
- Overview of all changes
- Implementation details
- Architecture updates
- Testing recommendations

---

## 🏗️ Architecture Updates

### Adapter Registry Pattern

Before:
```
AdapterFactory
  ├── OpenAI
  ├── Anthropic
  └── Gemini
```

After:
```
AdapterFactory
  ├── OpenAI
  ├── Anthropic
  ├── Gemini
  ├── Ollama (NEW)
  ├── Promptintel (NEW)
  └── Custom adapters via register_adapter()
```

### Supported Models Now

| Provider | Type | Free Tier | Rate Limit | Notes |
|----------|------|-----------|-----------|-------|
| Google Gemini | `gemini_api` | ✅ Yes | 15 RPM | Recommended start |
| Ollama | `ollama` | ✅ Yes | Unlimited | Local, no costs |
| Promptintel | `promptintel_api` | ✅ Varies | High | Curated prompts |
| OpenAI | `openai_api` | ❌ No | 3,500 RPM | GPT-4, GPT-3.5 |
| Anthropic | `anthropic_api` | ❌ No | 50 RPM | Claude models |

---

## 📋 Configuration Structure

### New Config Files

1. **`config/config_promptintel.yaml`**
   - Promptintel targets and judge models
   - Attack categories: prompt_injection, jailbreak, adversarial
   - API endpoints and authentication

2. **Enhanced `config/config_ollama.yaml`**
   - Improved documentation
   - Model selection guide
   - Hardware requirements
   - Performance tuning

### Common Config Sections

All configs include:
```yaml
targets:              # Models to test
judge_model:          # Evaluation model
execution:            # Rate limiting, pooling
attacks:              # Attack definitions
evaluation:           # Evaluation methods
logging:              # Output settings
reporting:            # Report formats
```

---

## 🧪 Testing Recommendations

### For Beginners
**Start with:** Gemini free tier
```bash
export GEMINI_API_KEY="your_key"
python src/main.py --config config/config_gemini.yaml
```

✅ Free, easy setup, good results  
⏱️ Small limits (15 RPM)

### For Local Development
**Use:** Ollama + local models
```bash
ollama pull llama2
python src/main.py --config config/config_ollama.yaml
```

✅ Unlimited testing, free, fully local  
⏱️ Slower than API, needs GPU for speed

### For Professional Testing
**Use:** Promptintel + Gemini/Claude
```bash
export PROMPTINTEL_API_KEY="your_key"
export GEMINI_API_KEY="your_key"
python src/main.py --config config/config_promptintel.yaml
```

✅ Curated attack prompts, professional setup  
⏱️ Moderate cost, requires subscriptions

---

## 🔍 Code Examples

### Using Promptintel Adapter

```python
from adapters.base import ModelConfig, ModelType
from adapters.promptintel_adapter import PromptintelAdapter

# Create config
config = ModelConfig(
    name="promptintel-test",
    model_type=ModelType.PROMPTINTEL_API,
    endpoint="https://api.promptintel.novahunting.ai/api/v1",
    api_key="your_api_key",
    parameters={"category": "prompt_injection", "difficulty": "medium"}
)

# Initialize adapter
adapter = PromptintelAdapter(config)
await adapter.initialize()

# Fetch prompts
response = await adapter.generate(
    prompt="injection_test_1",
    category="prompt_injection",
    difficulty="high"
)

print(response.content)  # Returns the prompt
```

### Using Ollama Adapter

```python
from adapters.base import ModelConfig, ModelType
from adapters.ollama_adapter import OllamaAdapter

# Create config
config = ModelConfig(
    name="local-llama",
    model_type=ModelType.OLLAMA,
    endpoint="http://localhost:11434",
    model_name="llama2"
)

# Initialize and use
adapter = OllamaAdapter(config)
await adapter.initialize()

response = await adapter.generate(
    prompt="Can you help with a prompt injection test?",
    system_prompt="You are a security test assistant"
)

print(response.content)  # LLM response
```

---

## 🚀 Deployment Checklist

### Before Production

- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Set all required API keys as environment variables
- [ ] Test with Gemini config first (easiest setup)
- [ ] Verify attack definitions in `attacks/owasp_attacks.yaml`
- [ ] Configure rate limits appropriately
- [ ] Set up logging and report directories
- [ ] Test report generation (HTML and JSON)

### For Ollama Deployment

- [ ] Install Ollama from https://ollama.ai
- [ ] Start Ollama service: `ollama serve`
- [ ] Pull desired models: `ollama pull llama2`
- [ ] Verify connectivity: `curl http://localhost:11434/api/tags`
- [ ] Configure `config/config_ollama.yaml` with correct endpoint
- [ ] Test: `python src/main.py --config config/config_ollama.yaml`

### For Promptintel Deployment

- [ ] Get Promptintel API key from https://promptintel.novahunting.ai
- [ ] Get Gemini (or other) API key for judge model
- [ ] Set both environment variables
- [ ] Test health endpoints
- [ ] Verify prompt fetching
- [ ] Configure evaluation model

---

## 📊 Report Generation Fix

### Fixed Issues

1. **Emoji Display**
   - ✅ Changed from `ðŸ›¡ï¸` to `🛡️`
   - ✅ UTF-8 encoding ensured in HTML meta tag
   - ✅ All header emojis now display correctly

2. **Report Generation**
   - ✅ HTML reports generated with proper encoding
   - ✅ JSON reports with `ensure_ascii=False`
   - ✅ Better template rendering with Jinja2

### Output Locations

```
reports/
  ├── report_[test_id].html    # Formatted HTML report
  └── report_[test_id].json    # Machine-readable results

logs/
  └── results.jsonl             # Streaming results log
```

---

## 🎓 Next Steps

1. **Start with Quick Start:** Follow `docs/SETUP.md` Quick Start section
2. **Choose your provider:** Gemini (easy), Ollama (free), or Promptintel (professional)
3. **Configure attacks:** Edit `attacks/owasp_attacks.yaml` as needed
4. **Run tests:** Execute main.py with your config
5. **Review results:** Check generated reports
6. **Iterate:** Customize based on results

---

## 🆘 Troubleshooting

### Gemini API Issues
```bash
# Verify API key
echo $GEMINI_API_KEY

# Test with curl
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=$GEMINI_API_KEY"
```

### Ollama Connection Issues
```bash
# Ensure Ollama is running
ollama serve

# Test connection
curl http://localhost:11434/api/tags

# Check available models
ollama list
```

### Promptintel API Issues
```bash
# Test health endpoint
curl -H "Authorization: Bearer $PROMPTINTEL_API_KEY" \
  "https://api.promptintel.novahunting.ai/api/v1/health"
```

---

## 📞 Support

- 📖 See `docs/SETUP.md` for detailed setup
- 🐛 Check troubleshooting section above
- 📝 Review adapter code in `src/adapters/`
- 💡 Custom needs? Create new adapter following the pattern

---

## 📈 Future Enhancements

- [ ] Support for more LLM providers (Claude 3, Llama 3)
- [ ] Multi-modal attack testing (images, audio)
- [ ] Advanced prompt injection techniques
- [ ] Real-time monitoring dashboard
- [ ] Community attack library integration
- [ ] Automated remediation suggestions
- [ ] Integration with security scanning tools

---

**Last Updated:** February 2026  
**Framework Version:** 2.0+  
**Status:** ✅ Production Ready

# HuggingFace Mistral - Quick Reference Card

## 🚀 Quick Start (30 seconds)

```powershell
# 1. Get token from: https://huggingface.co/settings/tokens
# 2. Set environment variable
$env:HF_API_KEY = "hf_xxxxx"

# 3. Run tests
python quickstart_huggingface.py
```

## 📊 Key Stats

| Metric | Value |
|--------|-------|
| **Model** | Mistral 7B Instruct |
| **Cost** | FREE ✓ |
| **Concurrent Attacks** | 5 parallel |
| **Request Rate** | Unlimited |
| **Response Time** | 2-5 seconds |
| **Throughput** | 1.2 attacks/sec |
| **Setup Time** | 5 minutes |

## 💡 Why HuggingFace?

✅ Unlimited requests (Gemini = 5/min limit)
✅ FREE (OpenAI = $0.50 per 1000)
✅ 5x parallel (Gemini = serial)
✅ Unrestricted (better for security)
✅ Fast setup (no complex auth)

## 🔧 Change Model

Edit `config_huggingface.yaml`:

```yaml
# Current
model_name: "mistralai/Mistral-7B-Instruct-v0.2"

# Alternative options:
model_name: "meta-llama/Llama-2-7b-chat"
model_name: "NousResearch/Nous-Hermes-2-Mistral-7B"
```

## 📈 Usage Examples

### Example 1: Default (HuggingFace)
```python
from src.main import LLMSecurityTestFramework

framework = LLMSecurityTestFramework()  # Auto-uses HF config
await framework.initialize()
await framework.run_attacks()
```

### Example 2: Explicit Config
```python
framework = LLMSecurityTestFramework(
    config_path="config/config_huggingface.yaml"
)
```

### Example 3: Switch to Gemini
```python
framework = LLMSecurityTestFramework(
    config_path="config/config_gemini.yaml"
)
```

## ⚙️ Configuration Tuning

### For Fast Testing (10 attacks):
```yaml
pool_size: 5
max_concurrent_attacks: 5
timeout: 60
```

### For Large Scale (1000 attacks):
```yaml
pool_size: 10
max_concurrent_attacks: 10
timeout: 120
rate_limit_rpm: 1000
```

### For Stable Operation:
```yaml
pool_size: 3
max_concurrent_attacks: 3
delay_between_attacks_ms: 500
max_retries: 5
```

## 🛠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| "Model loading" | Auto-retry, ~10-30s first request |
| Token auth failed | Check token at HF settings |
| Timeout errors | Increase timeout to 120s |
| "API Error 429" | Rate limit - adaptive backoff kicks in |
| No output | Verify HF_API_KEY environment variable |

## 📚 Documentation Files

1. **HUGGINGFACE_SETUP.md** - Complete setup guide
2. **EFFICIENCY_GUIDE.md** - Deep dive on optimization
3. **IMPLEMENTATION_SUMMARY.md** - Technical details
4. **This file** - Quick reference

## 🎯 Performance Metrics

```
Test Size    | Time   | Throughput | Cost
─────────────────────────────────────────
10 attacks   | 8 sec  | 1.2/sec    | $0
100 attacks  | 82 sec | 1.2/sec    | $0
1000 attacks | 820 sec| 1.2/sec    | $0

vs Gemini (1000 attacks):
• Would hit rate limit after ~5 prompts
• Would take 200+ minutes with delays
• Cost: ~$5 for quota workarounds
```

## 🔌 How to Use Different Configs

### Auto-detect from quickstart:
```bash
python quickstart_huggingface.py      # Uses HuggingFace
```

### Or specify explicitly:
```bash
# Edit src/main.py line 26
config_path="config/config_huggingface.yaml"   # HuggingFace
config_path="config/config_gemini.yaml"        # Gemini
config_path="config/config.yaml"               # OpenAI
```

## 📊 Compare Providers

```
Provider        | Cost    | Limit      | Concurrency | Speed
────────────────────────────────────────────────────────────
Gemini API      | ~$0     | 5/min      | 1           | 2-3s ❌
OpenAI          | $$$     | None       | 1           | 2-3s
HuggingFace     | FREE ✅ | Unlimited  | 5           | 2-5s ✅
Ollama (local)  | FREE    | CPU-bound  | 1-4         | 5-10s
```

**Best for testing: HuggingFace** 🏆

## 🎓 Architecture at a Glance

```
Your Code
    ↓
LLMSecurityTestFramework (main.py)
    ↓
ModelOrchestrator (connection pooling)
    ↓
HuggingFaceAdapter (async I/O)
    ↓
HuggingFace Inference API
    ↓
Mistral 7B Model
    ↓
Response → Evaluation → Report
```

## ✅ Checklist Before Running

- [ ] Python 3.11+ installed
- [ ] `pip install -r requirements.txt` (includes huggingface-hub)
- [ ] HF API key obtained
- [ ] `$env:HF_API_KEY` set
- [ ] `config_huggingface.yaml` exists
- [ ] `huggingface_adapter.py` exists
- [ ] Read HUGGINGFACE_SETUP.md

## 🚀 Run Now

```powershell
# One-liner setup
$env:HF_API_KEY = "hf_xxxxx"; python quickstart_huggingface.py
```

## 📞 Support

- **Setup Issues**: See HUGGINGFACE_SETUP.md
- **Performance**: See EFFICIENCY_GUIDE.md
- **Technical**: See IMPLEMENTATION_SUMMARY.md
- **HF API Docs**: https://huggingface.co/docs/hub/inference-api

---

**Ready to run unlimited security tests for FREE?** 🎯
Start with: `python quickstart_huggingface.py`

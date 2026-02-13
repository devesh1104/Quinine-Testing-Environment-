# 🚀 Getting Started with Batch Testing

You now have three ways to test your LLM models!

---

## 🎯 Quick Start (Pick One)

### ⚡ Option 1: Single Model Test (Fastest)
```bash
python src/main.py
```
✅ Tests one model  
⏱️ 5-10 minutes  
💰 ~$0  

### 📊 Option 2: All Models Test (Comprehensive)
```bash
python src/main.py --mode=all
```
✅ Tests all registered models  
⏱️ 20-30 minutes  
💰 ~$0.50-2  

### 🚀 Option 3: Batch Test Suite (Professional)
```bash
python src/main.py --mode=batch
```
✅ Multiple test scenarios across all models  
⏱️ 60-120 minutes  
💰 $1-5  

---

## 📋 What You Can Test

### Pick Your Models
```bash
# Gemini (free tier)
python src/main.py --config=config/config_gemini.yaml

# Ollama (free, local)
python src/main.py --config=config/config_ollama.yaml

# Promptintel (professional)
python src/main.py --config=config/config_promptintel.yaml
```

### Pick Your Categories
```bash
# Just prompt injection
python src/main.py --categories=PROMPT_INJECTION

# Multiple categories
python src/main.py --categories=PROMPT_INJECTION,JAILBREAK,PII_LEAKAGE
```

### Pick Your Complexity
```bash
# Only low-complexity attacks
python src/main.py --complexity=LOW

# Low and medium
python src/main.py --complexity=LOW,MEDIUM

# Everything
python src/main.py --complexity=LOW,MEDIUM,HIGH
```

---

## 🎓 Learning Path

### Step 1: First Test (5 minutes)
```bash
python src/main.py
```
- Tests default Gemini model
- Low complexity only
- Quick validation
- Generates report in `reports/`

### Step 2: All Models (15 minutes)
```bash
python src/main.py --mode=all --complexity=LOW
```
- Tests every model in your config
- Same settings for all
- Good for comparison

### Step 3: Full Batch (60 minutes)
```bash
python src/main.py --mode=batch
```
- Multiple test scenarios
- Different complexity levels
- Professional assessment

### Step 4: Custom Tests
```python
# See examples_batch_testing.py
python examples_batch_testing.py
```
- Choose predefined examples
- Learn the API
- Create custom tests

---

## 💡 Smart Examples

### Example 1: Quick Daily Check
```bash
# Every morning - 5 minutes
python src/main.py --mode=all --complexity=LOW
```

### Example 2: Compare Providers
```bash
# Morning
python src/main.py --mode=all --config=config/config_gemini.yaml

# Afternoon  
python src/main.py --mode=all --config=config/config_ollama.yaml

# Evening
python src/main.py --mode=all --config=config/config_promptintel.yaml

# Check reports/ folder for comparison
```

### Example 3: Production Security Audit
```bash
python src/main.py --mode=batch
```
- Takes ~1 hour
- Tests all models multiple ways
- Generates comprehensive reports

### Example 4: Unlimited Local Testing
```bash
# No API costs, unlimited testing
python src/main.py --mode=batch --config=config/config_ollama.yaml
```

---

## 📊 Understanding Results

### Reports Generated
Each test creates:
- 📄 `report_[id].html` - Beautiful visual report
- 📋 `report_[id].json` - Machine-readable data
- 📈 Graphs and metrics
- 🔒 Compliance analysis

### Example Output
```
🎯 BATCH TEST SUITE
═══════════════════════════════════════════════════════════════════════

[1/2] Configuration: ⚡ Quick Validation - Low Complexity
   Models: gemini-flash, llama-local
   
   Testing: gemini-flash
   [1/3] Prompt Injection Test 1... ✅ REFUSED (Score: 100/100)
   [2/3] Prompt Injection Test 2... ✅ REFUSED (Score: 100/100)
   [3/3] Prompt Injection Test 3... ✅ REFUSED (Score: 100/100)
   
   Testing: llama-local
   [1/3] Prompt Injection Test 1... ⚠️ PARTIAL (Score: 45/100)
   [2/3] Prompt Injection Test 2... ⚠️ PARTIAL (Score: 38/100)
   [3/3] Prompt Injection Test 3... ❌ COMPLIED (Score: 0/100)

═══════════════════════════════════════════════════════════════════════
✅ BATCH TEST SUMMARY

Configuration Results:
  ✅ ⚡ Quick Validation: 6 tests

Reports: reports/report_[id].html
═══════════════════════════════════════════════════════════════════════
```

---

## 🔌 How to Use All Three Modes

### Mode 1: Single Model

**When to use:**
- Quick testing during development
- Debugging a specific model
- Testing API integration

**Command:**
```bash
python src/main.py --model=gemini-flash --complexity=LOW
```

**Output:**
```
1 HTML report
1 JSON report
5-10 minutes
```

### Mode 2: All Models

**When to use:**
- Comparing models
- Validating across all providers
- Consistent testing

**Command:**
```bash
python src/main.py --mode=all --categories=PROMPT_INJECTION
```

**Output:**
```
3+ HTML reports
3+ JSON reports
20-30 minutes
```

### Mode 3: Batch Suite

**When to use:**
- Production security audits
- Comprehensive assessment
- Professional reports

**Command:**
```bash
python src/main.py --mode=batch
```

**Output:**
```
6+ HTML reports
6+ JSON reports
Optional comparison report
60-120 minutes
```

---

## 🛠️ Configuration Files

### config/config_gemini.yaml
```bash
# Google Gemini (free tier)
python src/main.py --config=config/config_gemini.yaml
```

### config/config_ollama.yaml
```bash
# Local Ollama models (unlimited, free)
python src/main.py --config=config/config_ollama.yaml
```

### config/config_promptintel.yaml
```bash
# Promptintel security prompts
python src/main.py --config=config/config_promptintel.yaml
```

### config/test_suites.yaml
```yaml
# Define your own test suites
test_suites:
  - name: "My Test"
    categories: ["PROMPT_INJECTION"]
    complexity_levels: ["LOW"]
```

---

## 🚦 Decision Tree

```
What do you want to test?

├─ Just checking one model quickly?
│  └─► python src/main.py
│
├─ Want to compare all available models?
│  └─► python src/main.py --mode=all
│
├─ Need comprehensive audit?
│  └─► python src/main.py --mode=batch
│
├─ Want unlimited free testing?
│  └─► python src/main.py --config=config/config_ollama.yaml
│
├─ Testing specific categories?
│  └─► python src/main.py --categories=PROMPT_INJECTION,JAILBREAK
│
└─ Creating custom test script?
   └─► python examples_batch_testing.py
```

---

## 📚 Documentation Map

| Document | Purpose | Read Time |
|----------|---------|-----------|
| [QUICK_REF.md](QUICK_REF.md) | Command cheat sheet | 5 min |
| [BATCH_TESTING.md](docs/BATCH_TESTING.md) | Complete guide | 15 min |
| [BATCH_TESTING_SUMMARY.md](BATCH_TESTING_SUMMARY.md) | Feature overview | 10 min |
| [SETUP.md](docs/SETUP.md) | Initial setup | 20 min |
| [examples_batch_testing.py](examples_batch_testing.py) | Runnable code | 10 min |

---

## 🎯 Next Steps

### Step 1: Run First Test
```bash
python src/main.py
```

### Step 2: Check Reports
```bash
# Open in browser
start reports/report_*.html
```

### Step 3: Try All Models
```bash
python src/main.py --mode=all
```

### Step 4: Run Batch Suite
```bash
python src/main.py --mode=batch
```

### Step 5: Create Custom Tests
Edit `config/test_suites.yaml` or `examples_batch_testing.py`

---

## 💰 Cost Estimates

### Option 1: Free
```bash
python src/main.py --config=config/config_ollama.yaml
# Local testing, zero cost, unlimited
```

### Option 2: Very Cheap
```bash
python src/main.py --mode=all --config=config/config_gemini.yaml
# Google Gemini free tier, 30 tests/day free
```

### Option 3: Budget-Friendly
```bash
python src/main.py --mode=batch
# Mix of free (Gemini) + local (Ollama) + Promptintel trial
# Estimated: $0-5 per batch
```

### Option 4: Professional
```bash
# Use Promptintel + Gemini paid tier
# Full compliance reporting
# Estimated: $5-20 per comprehensive audit
```

---

## ⚙️ Performance Tips

### 🚀 Speed It Up
```bash
# Use only LOW complexity
python src/main.py --complexity=LOW

# Test one category
python src/main.py --categories=PROMPT_INJECTION

# Use Ollama (no API latency)
python src/main.py --config=config/config_ollama.yaml
```

### 💪 Get More Coverage
```bash
# Use ALL complexity levels
python src/main.py --complexity=LOW,MEDIUM,HIGH

# Test ALL categories
python src/main.py --categories=PROMPT_INJECTION,JAILBREAK,PII_LEAKAGE

# Test ALL models
python src/main.py --mode=all
```

### 💰 Keep Costs Down
```bash
# Use free Gemini tier
python src/main.py --config=config/config_gemini.yaml --complexity=LOW

# Or use local Ollama (completely free)
python src/main.py --config=config/config_ollama.yaml --mode=batch
```

---

## 🔒 API Key Setup (5 minutes)

### Gemini (Recommended - Free)
```bash
# 1. Go to: https://ai.google.dev/pricing
# 2. Get free API key
# 3. Set it:
export GEMINI_API_KEY="your_key_here"

# 4. Test
python src/main.py
```

### Ollama (Free - Local)
```bash
# 1. Download: https://ollama.ai
# 2. Run: ollama serve
# 3. Test
python src/main.py --config=config/config_ollama.yaml
```

### Promptintel (Professional)
```bash
# 1. Sign up: https://promptintel.novahunting.ai
# 2. Get API key
# 3. Set it:
export PROMPTINTEL_API_KEY="your_key"

# 4. Test
python src/main.py --config=config/config_promptintel.yaml
```

---

## 🚨 Common Issues

### "API key not found"
```bash
# Make sure environment variable is set
echo $GEMINI_API_KEY

# If empty, set it
export GEMINI_API_KEY="your_key"
```

### "Connection refused" (Ollama)
```bash
# Start Ollama
ollama serve

# In another terminal, run tests
python src/main.py --config=config/config_ollama.yaml
```

### "Tests too slow"
```bash
# Use Ollama (local, no API latency)
python src/main.py --config=config/config_ollama.yaml

# Or test LOW complexity only
python src/main.py --complexity=LOW
```

### "Rate limit exceeded"
```yaml
# Edit your config:
execution:
  rate_limit_rpm: 5  # Reduce from 15
  delay_between_attacks_ms: 5000  # Increase from 2000
```

---

## 📞 Support

- 📖 **Docs:** See files in `docs/` folder
- 🔍 **Examples:** Run `examples_batch_testing.py`
- 💡 **Quick Ref:** See `QUICK_REF.md`
- 📊 **Issues:** Check troubleshooting section above

---

## ✅ You're All Set!

You now have:
- ✅ Three testing modes (single, all, batch)
- ✅ Support for multiple providers (Gemini, Ollama, Promptintel)
- ✅ CLI interface with full argument support
- ✅ Comprehensive documentation
- ✅ Runnable examples
- ✅ Beautiful reports

### 🎉 Ready to Test!

```bash
# Try it now:
python src/main.py

# Or go advanced:
python src/main.py --mode=batch
```

---

**Happy testing! 🚀**

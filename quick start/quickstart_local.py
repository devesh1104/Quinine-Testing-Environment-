#!/usr/bin/env python3
"""
Local GGUF Model Quickstart - Mistral 7B
Runs LLM security tests against locally-hosted Mistral model

Prerequisites:
    1. llama-cpp-python installed: pip install llama-cpp-python
    2. GGUF model downloaded (already included in your project)
    3. GPU support (optional but recommended): pip install llama-cpp-python[gpu]

Usage:
    python quickstart_local.py
"""

import asyncio
import sys
import os
from pathlib import Path
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from main import LLMSecurityTestFramework

async def check_dependencies():
    """Check if required dependencies are installed"""
    print("📦 Checking dependencies...")
    
    try:
        import llama_cpp
        print("✅ llama-cpp-python is installed")
        return True
    except ImportError:
        print("❌ llama-cpp-python is required but not installed")
        print()
        print("Install it with one of these commands:")
        print()
        print("Basic (CPU):")
        print("  pip install llama-cpp-python")
        print()
        print("With GPU support (NVIDIA CUDA):")
        print("  pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121")
        print()
        print("With GPU support (Apple Metal):")
        print("  CMAKE_ARGS='-DLLAMA_METAL=on' pip install llama-cpp-python")
        print()
        return False

async def main():
    """Run security tests using local Mistral GGUF model"""
    
    print("=" * 70)
    print("🚀 Local Mistral GGUF - LLM Security Testing Framework")
    print("=" * 70)
    print()
    
    # Check dependencies
    if not await check_dependencies():
        print()
        print("⚠️  Please install llama-cpp-python and try again.")
        return 1
    
    print()
    
    config_path = str(Path(__file__).parent / "config" / "config_local.yaml")
    
    if not Path(config_path).exists():
        print(f"❌ Config file not found: {config_path}")
        return 1
    
    try:
        # Initialize framework with local config
        print("📋 Loading local GGUF configuration...")
        framework = LLMSecurityTestFramework(config_path)
        
        print("🔧 Initializing attack engine...")
        print()
        await framework.initialize()
        
        print()
        print("=" * 70)
        print("🎯 Attack Configuration")
        print("=" * 70)
        print(f"  Provider: Local GGUF (Mistral 7B)")
        print(f"  Model: mistral-7b-instruct-v0.2.Q4_K_M")
        print(f"  Targets: {len(framework.config.get('targets', []))} model(s)")
        print(f"  Max Concurrency: 1 (sequential)")
        print(f"  Cost: FREE (offline, no API calls)")
        print(f"  Speed: Slow-Medium (local inference)")
        print()
        
        print("=" * 70)
        print("🔍 Running Attack Suite...")
        print("=" * 70)
        print()
        print("⏳ Note: First attack will be slow while model loads into memory.")
        print("   Subsequent attacks will be faster.")
        print()
        
        start_time = time.time()
        
        # Run attacks against all configured models
        test_ids = await framework.run_all_models(
            categories=None,  # Use all categories from config
            complexity_levels=None  # Use all complexity levels from config
        )
        
        elapsed = time.time() - start_time
        
        print()
        print("✅ Tests completed successfully!")
        print(f"⏱️  Total time: {elapsed:.1f} seconds")
        print()
        
        for i, test_id in enumerate(test_ids, 1):
            print(f"📄 Test {i} Report ID: {test_id}")
        
        print()
        print("=" * 70)
        print("📊 Reports & Results")
        print("=" * 70)
        print("   📁 HTML Reports: ./reports/report_*.html")
        print("   📁 JSON Reports: ./reports/report_*.json")
        print("   📁 Logs: ./logs/results.jsonl")
        print()
        
        # Clean up resources
        await framework.close()
        
        print("🎉 All set! Open the HTML reports in your browser for detailed results.")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

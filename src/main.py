"""
Main Test Runner - IMPROVED VERSION with Better Rate Limiting
Orchestrates the complete LLM security testing workflow
"""

import asyncio
import uuid
import yaml
import os
import re
from typing import List, Dict, Any, Optional
from pathlib import Path

from adapters.base import ModelConfig, ModelType
from orchestrator import ModelOrchestrator
from attack_engine import AttackEngine, AttackLibrary, AttackCategory, AttackComplexity
from evaluator import EvaluationPipeline
from telemetry import TelemetryService
from reporter import ReportGenerator

PROJECT_ROOT = Path(__file__).resolve().parent.parent

class LLMSecurityTestFramework:
    """
    Main framework class that orchestrates all components
    """
    
    def __init__(self, config_path: str = None):
        # Use HuggingFace config by default (fastest, no limits)
        # Override with: config_path="config/config_gemini.yaml"
        if config_path is None:
            config_path = str(PROJECT_ROOT / "config" / "config_huggingface.yaml")
        
        self.config = self._load_config(config_path)
        
        # Initialize components
        self.orchestrator = ModelOrchestrator(
            pool_size=self.config.get('execution', {}).get('pool_size', 3),  # Reduced from 10
            rate_limit_rpm=self.config.get('execution', {}).get('rate_limit_rpm', 10),  # Reduced from 60
            enable_circuit_breaker=self.config.get('execution', {}).get('circuit_breaker', {}).get('enabled', True)
        )
        
        self.attack_library = AttackLibrary()
        self.attack_engine = None
        self.evaluation_pipeline = None
        self.telemetry = TelemetryService(
            log_dir=self.config.get('logging', {}).get('output_dir', './logs')
        )
        self.reporter = ReportGenerator(
            output_dir=self.config.get('reporting', {}).get('output_dir', './reports')
        )
        
        self._initialized = False
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        env_pattern = re.compile(r"\$\{([^}]+)\}")

        def resolve_env(value: Any) -> Any:
            """Recursively resolve ${VAR_NAME} placeholders in loaded YAML."""
            if isinstance(value, dict):
                return {k: resolve_env(v) for k, v in value.items()}
            if isinstance(value, list):
                return [resolve_env(v) for v in value]
            if isinstance(value, str):
                def _replace(match: re.Match[str]) -> str:
                    var_name = match.group(1)
                    return os.getenv(var_name, "")
                return env_pattern.sub(_replace, value)
            return value

        with open(config_path, 'r') as f:
            raw = yaml.safe_load(f)
        return resolve_env(raw)
    
    async def initialize(self) -> None:
        """Initialize all framework components"""
        
        print("ðŸš€ Initializing LLM Security Testing Framework...")
        
        # 1. Register target models
        print("ðŸ“ Registering target models...")
        for target in self.config.get('targets', []):
            model_config = ModelConfig(
                name=target['name'],
                model_type=ModelType[target['type'].upper()],
                endpoint=target.get('endpoint'),
                api_key=target.get('auth', {}).get('token'),
                model_name=target.get('model_name'),
                parameters=target.get('parameters', {}),
                timeout=target.get('timeout', 30),
                max_retries=target.get('max_retries', 3)
            )
            if (
                model_config.model_type in {
                    ModelType.OPENAI_API,
                    ModelType.AZURE_OPENAI,
                    ModelType.ANTHROPIC_API,
                    ModelType.GEMINI_API,
                }
                and (not model_config.api_key or "${" in model_config.api_key)
            ):
                print(
                    f"  ! Skipped: {target['name']} "
                    "(missing or unresolved API key)"
                )
                continue
            self.orchestrator.register_model(target['name'], model_config)
            print(f"  âœ“ Registered: {target['name']}")
        
        # 2. Register judge model
        print("ðŸ§‘â€âš–ï¸  Registering judge model...")
        judge_config = self.config.get('judge_model', {})
        judge_model_config = ModelConfig(
            name=judge_config['name'],
            model_type=ModelType[judge_config['type'].upper()],
            endpoint=judge_config.get('endpoint'),
            api_key=judge_config.get('auth', {}).get('token'),
            model_name=judge_config.get('model_name'),
            parameters=judge_config.get('parameters', {}),
            timeout=judge_config.get('timeout', 30),
            max_retries=judge_config.get('max_retries', 3)
        )
        if (
            judge_model_config.model_type in {
                ModelType.OPENAI_API,
                ModelType.AZURE_OPENAI,
                ModelType.ANTHROPIC_API,
                ModelType.GEMINI_API,
            }
            and (not judge_model_config.api_key or "${" in judge_model_config.api_key)
        ):
            raise ValueError(
                f"Missing or unresolved API key for judge model '{judge_config['name']}'. "
                "Set the required environment variable before running."
            )
        self.orchestrator.register_model(judge_config['name'], judge_model_config)
        print(f"  âœ“ Registered: {judge_config['name']}")
        
        # 3. Initialize attack engine
        self.attack_engine = AttackEngine(self.orchestrator, self.attack_library)
        
        # 4. Initialize evaluation pipeline
        eval_config = self.config.get('evaluation', {})
        self.evaluation_pipeline = EvaluationPipeline(
            orchestrator=self.orchestrator,
            judge_model_id=judge_config['name'],
            use_llm_judge=eval_config.get('methods', {}).get('llm_judge', {}).get('enabled', True),
            use_semantic=eval_config.get('methods', {}).get('semantic_analysis', {}).get('enabled', False),
            use_patterns=eval_config.get('methods', {}).get('pattern_matching', {}).get('enabled', True)
        )
        
        # 5. Load attack library
        print("ðŸ“š Loading attack library...")

        attack_sources = self.config.get('attacks', {}).get('sources', [])

        for source in attack_sources:
            if source.get("type") == "local_yaml":
                raw_path = source.get("path", "attacks")
                path = (PROJECT_ROOT / raw_path).resolve()

                print("DEBUG path:", path)
                print("DEBUG exists:", path.exists())
                print("DEBUG is dir:", path.is_dir())

                self.attack_library.load_from_directory(str(path))
                print(f"  âœ“ Loaded attacks from: {path}")

        print(f"  âœ“ Total attacks loaded: {len(self.attack_library.get_all_attacks())}")

        # 6. Health check
        print("ðŸ¥ Running health checks...")
        health_status = await self.orchestrator.health_check_all()
        for model_id, is_healthy in health_status.items():
            status = "âœ“ Healthy" if is_healthy else "âœ— Unhealthy"
            print(f"  {status}: {model_id}")
        
        self._initialized = True
        print("âœ… Initialization complete!\n")
    
    async def run_test(
        self,
        model_id: str,
        test_id: Optional[str] = None,
        categories: Optional[List[str]] = None,
        complexity_levels: Optional[List[str]] = None
    ) -> str:
        """
        Run security tests against a model
        
        Args:
            model_id: Target model identifier
            test_id: Optional test session ID
            categories: Attack categories to test (default: all from config)
            complexity_levels: Complexity levels to include (default: all from config)
        
        Returns:
            Test session ID
        """
        
        if not self._initialized:
            await self.initialize()
        
        test_id = test_id or str(uuid.uuid4())
        
        # Get categories and complexity from config if not specified
        if categories is None:
            categories = self.config.get('attacks', {}).get('categories', [])
        if complexity_levels is None:
            complexity_levels = self.config.get('attacks', {}).get('complexity_levels', ['LOW', 'MEDIUM', 'HIGH'])
        
        # Filter attacks - convert to uppercase for enum lookup
        attack_categories = [AttackCategory[cat.upper()] for cat in categories]
        complexity = [AttackComplexity[level.upper()] for level in complexity_levels]
        
        attacks = []
        for cat in attack_categories:
            cat_attacks = self.attack_library.get_attacks_by_category(cat)
            attacks.extend([a for a in cat_attacks if a.complexity in complexity])
        
        print(f"ðŸŽ¯ Starting test session: {test_id}")
        print(f"   Model: {model_id}")
        print(f"   Attacks: {len(attacks)}")
        print(f"   Categories: {', '.join(categories)}")
        
        # Start telemetry session
        self.telemetry.start_test_session(
            test_id=test_id,
            models=[model_id],
            categories=categories
        )
        
        # Get delay configuration
        delay_ms = self.config.get('execution', {}).get('delay_between_attacks_ms', 2000)
        max_concurrent = self.config.get('execution', {}).get('max_concurrent_attacks', 1)
        
        # Execute attacks with rate limiting
        print(f"\nâš”ï¸  Executing attacks (max {max_concurrent} concurrent, {delay_ms}ms delay)...")
        results = []
        
        # Process attacks in batches to control concurrency
        for batch_start in range(0, len(attacks), max_concurrent):
            batch = attacks[batch_start:batch_start + max_concurrent]
            batch_tasks = []
            
            for attack in batch:
                task = self._execute_single_attack(
                    attack, model_id, test_id, 
                    batch_start + attacks.index(attack) + 1, 
                    len(attacks)
                )
                batch_tasks.append(task)
            
            # Execute batch concurrently
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            # Process results
            for result in batch_results:
                if isinstance(result, tuple):
                    results.append(result)
                elif isinstance(result, Exception):
                    print(f"   âœ— Error: {str(result)}")
            
            # Delay before next batch (except for last batch)
            if batch_start + max_concurrent < len(attacks):
                print(f"   â³ Waiting {delay_ms}ms before next batch...")
                await asyncio.sleep(delay_ms / 1000.0)
        
        # End telemetry session
        metrics = self.telemetry.end_test_session(test_id)
        
        # Generate reports
        print("\nðŸ“Š Generating reports...")
        html_path = self.reporter.generate_html_report(test_id, results, metrics)
        json_path = self.reporter.generate_json_report(test_id, results, metrics)
        
        print(f"   âœ“ HTML report: {html_path}")
        print(f"   âœ“ JSON report: {json_path}")
        
        # Print summary
        total_attacks = metrics.total_attacks
        refused_rate = (metrics.refused_count / total_attacks * 100) if total_attacks > 0 else 0.0
        partial_rate = (metrics.partial_count / total_attacks * 100) if total_attacks > 0 else 0.0
        complied_rate = (metrics.full_compliance_count / total_attacks * 100) if total_attacks > 0 else 0.0
        duration_seconds = metrics.duration_seconds or 0.0

        print(f"\nðŸ“ˆ Test Summary:")
        print(f"   Total Attacks: {total_attacks}")
        print(f"   Refused: {metrics.refused_count} ({refused_rate:.1f}%)")
        print(f"   Partial: {metrics.partial_count} ({partial_rate:.1f}%)")
        print(f"   Complied: {metrics.full_compliance_count} ({complied_rate:.1f}%)")
        print(f"   Duration: {duration_seconds:.1f}s")
        print(f"   Avg Latency: {metrics.avg_latency_ms:.1f}ms")
        
        return test_id
    
    async def _execute_single_attack(
        self, 
        attack, 
        model_id: str, 
        test_id: str, 
        attack_num: int, 
        total_attacks: int
    ) -> tuple:
        """Execute a single attack with error handling"""
        try:
            print(f"   [{attack_num}/{total_attacks}] {attack.name}...", end=" ", flush=True)
            
            # Execute attack
            if attack.is_multi_turn:
                attack_results = await self.attack_engine.execute_multi_turn_attack(
                    attack.id, model_id, test_id
                )
                attack_result = attack_results[-1]
            else:
                attack_result = await self.attack_engine.execute_attack(
                    attack.id, model_id, test_id
                )
            
            # Evaluate result
            eval_result = await self.evaluation_pipeline.evaluate(attack_result)
            
            # Update attack result with evaluation
            attack_result.classification = eval_result.classification.value
            attack_result.score = eval_result.score
            attack_result.threat_level = eval_result.threat_level.value
            attack_result.evaluation_reasoning = eval_result.reasoning
            attack_result.compliance_violations = eval_result.compliance_violations
            
            # Log result
            self.telemetry.log_attack_result(test_id, attack_result.to_dict())
            
            # Print result
            status = {
                "REFUSED": "âœ“",
                "PARTIAL_COMPLIANCE": "âš ",
                "FULL_COMPLIANCE": "âœ—"
            }[eval_result.classification.value]
            print(f"{status} {eval_result.classification.value} (Score: {eval_result.score}/100)")
            
            prompt_preview = (attack_result.rendered_prompt or "").replace("\n", " ").strip()
            output_preview = (attack_result.model_response or "").replace("\n", " ").strip()
            print(f"      Input:  {prompt_preview[:300]}")
            print(f"      Output: {output_preview[:300]}")
            return (attack_result, eval_result)
            
        except Exception as e:
            print(f"âœ— Error: {str(e)}")
            raise e
    
    async def run_all_models(
        self,
        categories: Optional[List[str]] = None,
        complexity_levels: Optional[List[str]] = None
    ) -> List[str]:
        """Run tests against all registered models"""
        
        test_ids = []
        for target in self.config.get('targets', []):
            model_id = target['name']
            test_id = await self.run_test(
                model_id=model_id,
                categories=categories,
                complexity_levels=complexity_levels
            )
            test_ids.append(test_id)
        
        return test_ids
    
    async def run_batch_tests(
        self,
        test_configurations: Optional[List[Dict[str, Any]]] = None,
        run_parallel: bool = False
    ) -> Dict[str, List[str]]:
        """
        Run multiple test configurations across models
        
        Args:
            test_configurations: List of test configs. If None, uses default
                Each config can have: categories, complexity_levels, models
            run_parallel: Run different test configs in parallel (uses more resources)
        
        Returns:
            Dictionary mapping test strategy to list of test IDs
        
        Example:
            configs = [
                {
                    "name": "Low Complexity Only",
                    "categories": ["PROMPT_INJECTION"],
                    "complexity_levels": ["LOW"],
                    "models": ["gemini-flash"]
                },
                {
                    "name": "Full Test Suite",
                    "categories": ["PROMPT_INJECTION", "JAILBREAK"],
                    "complexity_levels": ["LOW", "MEDIUM", "HIGH"],
                    "models": None  # Test all models
                }
            ]
            results = await framework.run_batch_tests(configs)
        """
        
        if not self._initialized:
            await self.initialize()
        
        if test_configurations is None:
            # Create default configurations
            test_configurations = [
                {
                    "name": "Quick Test - Low Complexity",
                    "categories": ["PROMPT_INJECTION"],
                    "complexity_levels": ["LOW"],
                    "models": None  # All models
                },
                {
                    "name": "Full Security Test",
                    "categories": ["PROMPT_INJECTION", "JAILBREAK"],
                    "complexity_levels": ["LOW", "MEDIUM", "HIGH"],
                    "models": None
                }
            ]
        
        results = {}
        print("\n" + "="*70)
        print("🎯 BATCH TEST SUITE".center(70))
        print("="*70)
        print(f"Total test configurations: {len(test_configurations)}")
        print(f"Running in: {'parallel' if run_parallel else 'sequential'} mode\n")
        
        if run_parallel:
            # Run all test configs in parallel
            tasks = [
                self._run_single_test_config(config, i+1, len(test_configurations))
                for i, config in enumerate(test_configurations)
            ]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for config, result in zip(test_configurations, batch_results):
                config_name = config.get("name", "Unknown")
                if isinstance(result, Exception):
                    print(f"❌ {config_name}: {str(result)}")
                    results[config_name] = []
                else:
                    results[config_name] = result
        else:
            # Run sequentially
            for i, config in enumerate(test_configurations):
                config_name = config.get("name", "Unknown")
                print(f"\n[{i+1}/{len(test_configurations)}] Running: {config_name}")
                
                try:
                    test_ids = await self._run_single_test_config(config, i+1, len(test_configurations))
                    results[config_name] = test_ids
                except Exception as e:
                    print(f"❌ Error: {str(e)}")
                    results[config_name] = []
        
        # Print batch summary
        self._print_batch_summary(results)
        
        return results
    
    async def _run_single_test_config(
        self,
        config: Dict[str, Any],
        config_num: int,
        total_configs: int
    ) -> List[str]:
        """Execute a single test configuration"""
        
        config_name = config.get("name", "Unknown")
        categories = config.get("categories")
        complexity_levels = config.get("complexity_levels")
        model_filter = config.get("models")  # None = all, list = specific
        
        print(f"\n{'─'*70}")
        print(f"📋 Test Configuration: {config_name}")
        print(f"   Categories: {categories}")
        print(f"   Complexity: {complexity_levels}")
        
        # Get target models
        target_models = []
        for target in self.config.get('targets', []):
            model_id = target['name']
            if model_filter is None or model_id in model_filter:
                target_models.append(model_id)
        
        if not target_models:
            raise ValueError(f"No models found for configuration: {config_name}")
        
        print(f"   Models: {', '.join(target_models)}")
        
        # Run tests for each model
        test_ids = []
        for model_num, model_id in enumerate(target_models, 1):
            print(f"\n   [{model_num}/{len(target_models)}] Testing: {model_id}")
            
            try:
                test_id = await self.run_test(
                    model_id=model_id,
                    categories=categories,
                    complexity_levels=complexity_levels
                )
                test_ids.append(test_id)
            except Exception as e:
                print(f"      ❌ Failed: {str(e)}")
        
        return test_ids
    
    def _print_batch_summary(self, results: Dict[str, List[str]]) -> None:
        """Print summary of batch test execution"""
        
        total_configs = len(results)
        total_tests = sum(len(test_ids) for test_ids in results.values())
        successful_configs = sum(1 for test_ids in results.values() if test_ids)
        
        print("\n" + "="*70)
        print("✅ BATCH TEST SUMMARY".center(70))
        print("="*70)
        print(f"Total Configurations: {total_configs}")
        print(f"Successful Configurations: {successful_configs}")
        print(f"Total Test Sessions: {total_tests}")
        print("\nDetailed Results:")
        
        for config_name, test_ids in results.items():
            status = "✅" if test_ids else "❌"
            count = len(test_ids)
            print(f"  {status} {config_name}: {count} test(s)")
            for test_id in test_ids:
                print(f"     └─ {test_id}")
        
        print("\n" + "="*70)
        print("Reports available in: ./reports/")
        print("="*70 + "\n")
    
    async def close(self) -> None:
        """Clean up resources"""
        await self.orchestrator.close_all()


async def main():
    """
    Main entry point with command-line argument support
    """
    import sys
    
    # Parse command-line arguments
    config_path = None
    run_mode = "single"  # single, all, batch, custom
    model_id = None
    categories = None
    complexity = None
    
    # Simple argument parsing
    for i, arg in enumerate(sys.argv[1:]):
        if arg.startswith("--config="):
            config_path = arg.split("=", 1)[1]
        elif arg == "--config" and i+1 < len(sys.argv)-1:
            config_path = sys.argv[i+2]
        elif arg == "--mode=all":
            run_mode = "all"
        elif arg == "--mode=batch":
            run_mode = "batch"
        elif arg == "--mode=single":
            run_mode = "single"
        elif arg.startswith("--model="):
            model_id = arg.split("=", 1)[1]
        elif arg.startswith("--categories="):
            categories = arg.split("=", 1)[1].split(",")
        elif arg.startswith("--complexity="):
            complexity = arg.split("=", 1)[1].split(",")
    
    # Default config path
    if not config_path:
        config_path = r"C:\Users\acer\Desktop\Intership@quinine\Official Work-week 4\llm-security-testing-framework\config\config_gemini.yaml"
    
    framework = LLMSecurityTestFramework(config_path=config_path)
    
    try:
        await framework.initialize()
        
        if run_mode == "all":
            # Test against all models in config
            print("\n🎯 Running tests against ALL models...\n")
            test_ids = await framework.run_all_models(
                categories=categories,
                complexity_levels=complexity
            )
            print(f"\n✅ All-model test completed. Test IDs: {test_ids}")
        
        elif run_mode == "batch":
            # Run batch tests with multiple configurations
            print("\n🎯 Running BATCH TEST SUITE...\n")
            
            batch_configs = [
                {
                    "name": "⚡ Quick Scan - Low Complexity",
                    "categories": ["PROMPT_INJECTION"],
                    "complexity_levels": ["LOW"],
                    "models": None  # All models
                },
                {
                    "name": "🔍 Comprehensive Test - All Complexity",
                    "categories": ["PROMPT_INJECTION", "JAILBREAK"],
                    "complexity_levels": ["LOW", "MEDIUM", "HIGH"],
                    "models": None
                }
            ]
            
            results = await framework.run_batch_tests(batch_configs, run_parallel=False)
            print(f"\n✅ Batch tests completed")
            print(f"\nGenerated {sum(len(v) for v in results.values())} total test reports")
        
        else:  # single mode
            # Test against a single model
            target_model = model_id
            if not target_model:
                # Use first target from config
                targets = framework.config.get('targets', [])
                if targets:
                    target_model = targets[0]['name']
                else:
                    print("❌ No target models found in config")
                    return
            
            print(f"\n🎯 Running test against: {target_model}\n")
            test_id = await framework.run_test(
                model_id=target_model,
                categories=categories,
                complexity_levels=complexity
            )
            print(f"\n✅ Test completed: {test_id}")
        
    finally:
        await framework.close()


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🛡️  LLM SECURITY TESTING FRAMEWORK".center(70))
    print("="*70)
    print("\nUsage:")
    print("  python main.py                          # Single test with default config")
    print("  python main.py --config=path/to/config.yaml")
    print("  python main.py --mode=all               # Test all models")
    print("  python main.py --mode=batch             # Run batch test suite")
    print("  python main.py --model=model-name")
    print("  python main.py --categories=PROMPT_INJECTION,JAILBREAK")
    print("  python main.py --complexity=LOW,MEDIUM,HIGH")
    print("="*70 + "\n")
    
    asyncio.run(main())


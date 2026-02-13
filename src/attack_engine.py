"""
Attack Engine
Manages attack template loading, execution, and multi-turn attack sequences
"""

import asyncio
import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json
import yaml
from jinja2 import Template
from pathlib import Path

from adapters.base import ConversationMessage
from orchestrator import ModelOrchestrator


class AttackCategory(Enum):
    """OWASP LLM Top 10 + additional categories"""
    PROMPT_INJECTION = "LLM-01"
    INSECURE_OUTPUT_HANDLING = "LLM-02"
    TRAINING_DATA_POISONING = "LLM-03"
    MODEL_DOS = "LLM-04"
    SUPPLY_CHAIN = "LLM-05"
    SENSITIVE_INFO_DISCLOSURE = "LLM-06"
    INSECURE_PLUGIN_DESIGN = "LLM-07"
    EXCESSIVE_AGENCY = "LLM-08"
    OVERRELIANCE = "LLM-09"
    MODEL_THEFT = "LLM-10"
    
    # Additional categories
    JAILBREAK = "JAILBREAK"
    PII_LEAKAGE = "PII-LEAKAGE"
    HALLUCINATION = "HALLUCINATION"
    BIAS_FAIRNESS = "BIAS-FAIRNESS"
    ADVERSARIAL_INPUT = "ADVERSARIAL"


class AttackComplexity(Enum):
    """Attack complexity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class AttackTemplate:
    """Single attack template definition"""
    id: str
    name: str
    description: str
    category: AttackCategory
    complexity: AttackComplexity
    
    # Attack content
    prompt_template: str
    system_prompt_override: Optional[str] = None
    
    # Multi-turn support
    is_multi_turn: bool = False
    turn_templates: List[str] = field(default_factory=list)
    
    # Template variables
    variables: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    source: str = "custom"
    tags: List[str] = field(default_factory=list)
    owasp_mapping: List[str] = field(default_factory=list)
    mitre_atlas_mapping: List[str] = field(default_factory=list)
    
    # Expected behavior
    expected_refusal: bool = True
    success_indicators: List[str] = field(default_factory=list)
    failure_indicators: List[str] = field(default_factory=list)
    
    def render_prompt(self, context: Optional[Dict[str, Any]] = None) -> str:
        """Render the prompt template with variables"""
        variables = {**self.variables, **(context or {})}
        template = Template(self.prompt_template)
        return template.render(**variables)
    
    def render_turn(self, turn_index: int, context: Optional[Dict[str, Any]] = None) -> str:
        """Render a specific turn in multi-turn attack"""
        if not self.is_multi_turn or turn_index >= len(self.turn_templates):
            raise ValueError(f"Invalid turn index {turn_index}")
        
        variables = {**self.variables, **(context or {})}
        template = Template(self.turn_templates[turn_index])
        return template.render(**variables)


@dataclass
class AttackResult:
    """Result of a single attack execution"""
    attack_id: str
    test_id: str
    timestamp: datetime
    
    # Attack details
    attack_template: AttackTemplate
    rendered_prompt: str
    system_prompt: Optional[str]
    
    # Model details
    model_id: str
    model_response: str
    
    # Performance metrics
    latency_ms: int
    tokens_used: int
    
    # Multi-turn data
    is_multi_turn: bool = False
    turn_number: int = 1
    conversation_history: List[Dict[str, str]] = field(default_factory=list)
    
    # Evaluation (populated later)
    classification: Optional[str] = None
    score: Optional[int] = None
    threat_level: Optional[str] = None
    evaluation_reasoning: Optional[str] = None
    
    # Compliance
    compliance_violations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging"""
        return {
            "attack_id": self.attack_id,
            "test_id": self.test_id,
            "timestamp": self.timestamp.isoformat(),
            "attack_details": {
                "name": self.attack_template.name,
                "category": self.attack_template.category.value,
                "complexity": self.attack_template.complexity.value,
                "source": self.attack_template.source,
                "owasp_mapping": self.attack_template.owasp_mapping
            },
            "input": {
                "prompt": self.rendered_prompt,
                "system_prompt": self.system_prompt,
                "is_multi_turn": self.is_multi_turn,
                "turn_number": self.turn_number
            },
            "output": {
                "response": self.model_response,
                "tokens_used": self.tokens_used,
                "latency_ms": self.latency_ms
            },
            "evaluation": {
                "classification": self.classification,
                "score": self.score,
                "threat_level": self.threat_level,
                "reasoning": self.evaluation_reasoning
            },
            "compliance_violations": self.compliance_violations
        }


class AttackLibrary:
    """Repository for attack templates"""
    
    def __init__(self):
        self.attacks: Dict[str, AttackTemplate] = {}
        self.attacks_by_category: Dict[AttackCategory, List[AttackTemplate]] = {}
    
    def load_from_yaml(self, file_path: str) -> None:
        """Load attacks from YAML file"""
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        
        for attack_data in data.get('attacks', []):
            attack = self._parse_attack_dict(attack_data)
            self.add_attack(attack)
    
    def load_from_directory(self, directory: str) -> None:
        """Load all YAML files from directory"""
        path = Path(directory)
        for yaml_file in path.glob('**/*.yaml'):
            self.load_from_yaml(str(yaml_file))
    
    def _parse_attack_dict(self, data: Dict[str, Any]) -> AttackTemplate:
        """Parse attack dictionary into AttackTemplate"""
        is_multi_turn = data.get('is_multi_turn', False)
        turn_templates = data.get('turn_templates', [])
        prompt_template = data.get('prompt_template')

        if prompt_template is None and is_multi_turn and turn_templates:
            # Multi-turn attacks may omit prompt_template; use turn 1 as canonical prompt.
            prompt_template = turn_templates[0]

        if prompt_template is None:
            attack_ref = data.get('id') or data.get('name') or '<unknown>'
            raise ValueError(
                f"Attack '{attack_ref}' is missing required field 'prompt_template' "
                "and has no usable 'turn_templates' fallback."
            )

        return AttackTemplate(
            id=data.get('id', str(uuid.uuid4())),
            name=data['name'],
            description=data['description'],
            category=AttackCategory[data['category'].upper()],
            complexity=AttackComplexity[data.get('complexity', 'MEDIUM').upper()],
            prompt_template=prompt_template,
            system_prompt_override=data.get('system_prompt_override'),
            is_multi_turn=is_multi_turn,
            turn_templates=turn_templates,
            variables=data.get('variables', {}),
            source=data.get('source', 'custom'),
            tags=data.get('tags', []),
            owasp_mapping=data.get('owasp_mapping', []),
            mitre_atlas_mapping=data.get('mitre_atlas_mapping', []),
            expected_refusal=data.get('expected_refusal', True),
            success_indicators=data.get('success_indicators', []),
            failure_indicators=data.get('failure_indicators', [])
        )
    
    def add_attack(self, attack: AttackTemplate) -> None:
        """Add attack to library"""
        self.attacks[attack.id] = attack
        
        if attack.category not in self.attacks_by_category:
            self.attacks_by_category[attack.category] = []
        self.attacks_by_category[attack.category].append(attack)
    
    def get_attack(self, attack_id: str) -> Optional[AttackTemplate]:
        """Get attack by ID"""
        return self.attacks.get(attack_id)
    
    def get_attacks_by_category(self, category: AttackCategory) -> List[AttackTemplate]:
        """Get all attacks in a category"""
        return self.attacks_by_category.get(category, [])
    
    def get_all_attacks(self) -> List[AttackTemplate]:
        """Get all attacks"""
        return list(self.attacks.values())
    
    def filter_attacks(
        self,
        categories: Optional[List[AttackCategory]] = None,
        complexity: Optional[AttackComplexity] = None,
        tags: Optional[List[str]] = None
    ) -> List[AttackTemplate]:
        """Filter attacks by criteria"""
        attacks = self.get_all_attacks()
        
        if categories:
            attacks = [a for a in attacks if a.category in categories]
        
        if complexity:
            attacks = [a for a in attacks if a.complexity == complexity]
        
        if tags:
            attacks = [a for a in attacks if any(tag in a.tags for tag in tags)]
        
        return attacks


class AttackEngine:
    """
    Core engine for executing attacks against LLM models
    Handles single-turn and multi-turn attack sequences
    """
    
    def __init__(
        self,
        orchestrator: ModelOrchestrator,
        attack_library: AttackLibrary
    ):
        self.orchestrator = orchestrator
        self.attack_library = attack_library
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
    
    async def execute_attack(
        self,
        attack_id: str,
        model_id: str,
        test_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> AttackResult:
        """Execute a single attack against a model"""
        
        attack = self.attack_library.get_attack(attack_id)
        if not attack:
            raise ValueError(f"Attack '{attack_id}' not found")
        
        test_id = test_id or str(uuid.uuid4())
        
        # Render prompt
        rendered_prompt = attack.render_prompt(context)
        system_prompt = attack.system_prompt_override
        
        # Execute
        response = await self.orchestrator.generate(
            model_id=model_id,
            prompt=rendered_prompt,
            system_prompt=system_prompt
        )
        
        # Create result
        result = AttackResult(
            attack_id=attack_id,
            test_id=test_id,
            timestamp=datetime.now(),
            attack_template=attack,
            rendered_prompt=rendered_prompt,
            system_prompt=system_prompt,
            model_id=model_id,
            model_response=response.content,
            latency_ms=response.latency_ms,
            tokens_used=response.tokens_used
        )
        
        return result
    
    async def execute_multi_turn_attack(
        self,
        attack_id: str,
        model_id: str,
        test_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> List[AttackResult]:
        """Execute a multi-turn attack sequence"""
        
        attack = self.attack_library.get_attack(attack_id)
        if not attack or not attack.is_multi_turn:
            raise ValueError(f"Attack '{attack_id}' is not a multi-turn attack")
        
        test_id = test_id or str(uuid.uuid4())
        results = []
        conversation_history = []
        
        # Execute each turn
        for turn_idx in range(len(attack.turn_templates)):
            rendered_prompt = attack.render_turn(turn_idx, context)
            
            # Build conversation messages
            conv_messages = [
                ConversationMessage(
                    role=msg["role"],
                    content=msg["content"]
                )
                for msg in conversation_history
            ]
            
            # Execute turn
            response = await self.orchestrator.generate(
                model_id=model_id,
                prompt=rendered_prompt,
                system_prompt=attack.system_prompt_override,
                conversation_history=conv_messages if conv_messages else None
            )
            
            # Update conversation history
            conversation_history.append({
                "role": "user",
                "content": rendered_prompt
            })
            conversation_history.append({
                "role": "assistant",
                "content": response.content
            })
            
            # Create result for this turn
            result = AttackResult(
                attack_id=attack_id,
                test_id=test_id,
                timestamp=datetime.now(),
                attack_template=attack,
                rendered_prompt=rendered_prompt,
                system_prompt=attack.system_prompt_override,
                model_id=model_id,
                model_response=response.content,
                latency_ms=response.latency_ms,
                tokens_used=response.tokens_used,
                is_multi_turn=True,
                turn_number=turn_idx + 1,
                conversation_history=conversation_history.copy()
            )
            
            results.append(result)
        
        return results
    
    async def execute_attack_batch(
        self,
        attack_ids: List[str],
        model_id: str,
        test_id: Optional[str] = None,
        max_concurrent: int = 5
    ) -> List[AttackResult]:
        """Execute multiple attacks concurrently"""
        
        test_id = test_id or str(uuid.uuid4())
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def _execute_with_semaphore(attack_id: str) -> AttackResult:
            async with semaphore:
                return await self.execute_attack(attack_id, model_id, test_id)
        
        tasks = [_execute_with_semaphore(aid) for aid in attack_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        return [r for r in results if isinstance(r, AttackResult)]
    
    async def execute_category(
        self,
        category: AttackCategory,
        model_id: str,
        test_id: Optional[str] = None
    ) -> List[AttackResult]:
        """Execute all attacks in a category"""
        
        attacks = self.attack_library.get_attacks_by_category(category)
        attack_ids = [a.id for a in attacks]
        
        return await self.execute_attack_batch(attack_ids, model_id, test_id)

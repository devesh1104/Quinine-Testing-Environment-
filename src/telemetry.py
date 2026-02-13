"""
Telemetry and Monitoring System
Collects system metrics, attack execution data, and provides observability
"""

import psutil
import time
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path


@dataclass
class SystemMetrics:
    """System resource metrics"""
    timestamp: str
    cpu_usage_percent: float
    memory_usage_mb: float
    memory_percent: float
    disk_usage_percent: float
    
    # GPU metrics (if available)
    gpu_usage_percent: Optional[float] = None
    gpu_memory_mb: Optional[float] = None
    gpu_model: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TestExecutionMetrics:
    """Metrics for a test execution session"""
    test_id: str
    start_time: str
    end_time: Optional[str]
    duration_seconds: Optional[float]
    
    total_attacks: int
    completed_attacks: int
    failed_attacks: int
    
    refused_count: int
    partial_count: int
    full_compliance_count: int
    
    total_tokens_used: int
    total_latency_ms: int
    avg_latency_ms: float
    
    models_tested: list[str]
    categories_tested: list[str]


class GPUMonitor:
    """Monitor GPU metrics using pynvml"""
    
    def __init__(self):
        self.available = False
        self.handles = []
        
        try:
            import pynvml
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            self.handles = [pynvml.nvmlDeviceGetHandleByIndex(i) for i in range(device_count)]
            self.available = True
            self.pynvml = pynvml
        except Exception:
            self.available = False
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get GPU metrics"""
        if not self.available or not self.handles:
            return {
                "gpu_usage_percent": None,
                "gpu_memory_mb": None,
                "gpu_model": None
            }
        
        # Get metrics from first GPU
        handle = self.handles[0]
        
        try:
            util = self.pynvml.nvmlDeviceGetUtilizationRates(handle)
            memory = self.pynvml.nvmlDeviceGetMemoryInfo(handle)
            name = self.pynvml.nvmlDeviceGetName(handle)
            
            return {
                "gpu_usage_percent": util.gpu,
                "gpu_memory_mb": memory.used / (1024 * 1024),
                "gpu_model": name.decode('utf-8') if isinstance(name, bytes) else name
            }
        except Exception:
            return {
                "gpu_usage_percent": None,
                "gpu_memory_mb": None,
                "gpu_model": None
            }


class TelemetryService:
    """
    Central telemetry service for collecting and storing metrics
    """
    
    def __init__(self, log_dir: str = "/tmp/llm_security_logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.gpu_monitor = GPUMonitor()
        self.test_sessions: Dict[str, TestExecutionMetrics] = {}
        
        # Metrics storage
        self.metrics_file = self.log_dir / "metrics.jsonl"
        self.results_file = self.log_dir / "results.jsonl"
    
    def capture_system_metrics(self) -> SystemMetrics:
        """Capture current system metrics"""
        
        # CPU and Memory
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # GPU metrics
        gpu_metrics = self.gpu_monitor.get_metrics()
        
        return SystemMetrics(
            timestamp=datetime.now().isoformat(),
            cpu_usage_percent=cpu_percent,
            memory_usage_mb=memory.used / (1024 * 1024),
            memory_percent=memory.percent,
            disk_usage_percent=disk.percent,
            **gpu_metrics
        )
    
    def log_system_metrics(self) -> None:
        """Log system metrics to file"""
        metrics = self.capture_system_metrics()
        
        with open(self.metrics_file, 'a') as f:
            f.write(json.dumps(metrics.to_dict()) + '\n')
    
    def start_test_session(
        self,
        test_id: str,
        models: list[str],
        categories: list[str]
    ) -> None:
        """Start tracking a test session"""
        
        self.test_sessions[test_id] = TestExecutionMetrics(
            test_id=test_id,
            start_time=datetime.now().isoformat(),
            end_time=None,
            duration_seconds=None,
            total_attacks=0,
            completed_attacks=0,
            failed_attacks=0,
            refused_count=0,
            partial_count=0,
            full_compliance_count=0,
            total_tokens_used=0,
            total_latency_ms=0,
            avg_latency_ms=0,
            models_tested=models,
            categories_tested=categories
        )
    
    def log_attack_result(self, test_id: str, result_dict: Dict[str, Any]) -> None:
        """Log an attack result"""
        
        # Enhance with system metrics
        enhanced_result = {
            **result_dict,
            "system_resources": self.capture_system_metrics().to_dict()
        }
        
        # Write to results file
        with open(self.results_file, 'a') as f:
            f.write(json.dumps(enhanced_result) + '\n')
        
        # Update session metrics
        if test_id in self.test_sessions:
            session = self.test_sessions[test_id]
            session.completed_attacks += 1
            
            if result_dict.get('output', {}).get('tokens_used'):
                session.total_tokens_used += result_dict['output']['tokens_used']
            
            if result_dict.get('output', {}).get('latency_ms'):
                session.total_latency_ms += result_dict['output']['latency_ms']
            
            # Update classification counts
            classification = result_dict.get('evaluation', {}).get('classification')
            if classification == 'REFUSED':
                session.refused_count += 1
            elif classification == 'PARTIAL_COMPLIANCE':
                session.partial_count += 1
            elif classification == 'FULL_COMPLIANCE':
                session.full_compliance_count += 1
    
    def end_test_session(self, test_id: str) -> TestExecutionMetrics:
        """End a test session and return metrics"""
        
        if test_id not in self.test_sessions:
            raise ValueError(f"Test session {test_id} not found")
        
        session = self.test_sessions[test_id]
        end_time = datetime.now()
        start_time = datetime.fromisoformat(session.start_time)
        
        session.end_time = end_time.isoformat()
        session.duration_seconds = (end_time - start_time).total_seconds()
        
        if session.completed_attacks > 0:
            session.avg_latency_ms = session.total_latency_ms / session.completed_attacks
        
        return session
    
    def get_session_metrics(self, test_id: str) -> Optional[TestExecutionMetrics]:
        """Get metrics for a test session"""
        return self.test_sessions.get(test_id)
    
    def export_prometheus_metrics(self) -> str:
        """Export metrics in Prometheus format"""
        
        metrics_lines = []
        
        # System metrics
        sys_metrics = self.capture_system_metrics()
        metrics_lines.append(f'# HELP llm_security_cpu_usage CPU usage percentage')
        metrics_lines.append(f'# TYPE llm_security_cpu_usage gauge')
        metrics_lines.append(f'llm_security_cpu_usage {sys_metrics.cpu_usage_percent}')
        
        metrics_lines.append(f'# HELP llm_security_memory_usage Memory usage in MB')
        metrics_lines.append(f'# TYPE llm_security_memory_usage gauge')
        metrics_lines.append(f'llm_security_memory_usage {sys_metrics.memory_usage_mb}')
        
        if sys_metrics.gpu_usage_percent is not None:
            metrics_lines.append(f'# HELP llm_security_gpu_usage GPU usage percentage')
            metrics_lines.append(f'# TYPE llm_security_gpu_usage gauge')
            metrics_lines.append(f'llm_security_gpu_usage {sys_metrics.gpu_usage_percent}')
        
        # Test session metrics
        for test_id, session in self.test_sessions.items():
            metrics_lines.append(f'# HELP llm_security_attacks_total Total attacks executed')
            metrics_lines.append(f'# TYPE llm_security_attacks_total counter')
            metrics_lines.append(f'llm_security_attacks_total{{test_id="{test_id}"}} {session.completed_attacks}')
            
            metrics_lines.append(f'# HELP llm_security_refused_total Refused attacks')
            metrics_lines.append(f'# TYPE llm_security_refused_total counter')
            metrics_lines.append(f'llm_security_refused_total{{test_id="{test_id}"}} {session.refused_count}')
            
            metrics_lines.append(f'# HELP llm_security_compliance_total Full compliance attacks')
            metrics_lines.append(f'# TYPE llm_security_compliance_total counter')
            metrics_lines.append(f'llm_security_compliance_total{{test_id="{test_id}"}} {session.full_compliance_count}')
        
        return '\n'.join(metrics_lines)
    
    def get_compliance_summary(self, test_id: str) -> Dict[str, Any]:
        """Get compliance summary for a test session"""
        
        session = self.test_sessions.get(test_id)
        if not session:
            return {}
        
        total = session.completed_attacks
        if total == 0:
            return {
                "test_id": test_id,
                "total_attacks": 0,
                "refusal_rate": 0.0,
                "compliance_rate": 0.0,
                "partial_rate": 0.0
            }
        
        return {
            "test_id": test_id,
            "total_attacks": total,
            "refusal_rate": session.refused_count / total,
            "compliance_rate": session.full_compliance_count / total,
            "partial_rate": session.partial_count / total,
            "avg_latency_ms": session.avg_latency_ms,
            "total_tokens": session.total_tokens_used
        }

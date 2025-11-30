"""
Observability Manager - Logging, Tracing, and Metrics
Implements ADK observability concepts for monitoring agents
"""

import logging
import json
import time
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
from collections import defaultdict


class ObservabilityManager:
    """
    Comprehensive observability for agent system.
    Provides logging, tracing, and metrics collection.
    """
    
    def __init__(self, log_dir: str = "logs"):
        """
        Initialize observability manager
        
        Args:
            log_dir: Directory for log files
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
        # Metrics storage
        self.metrics: Dict[str, List] = defaultdict(list)
        
        # Trace storage for request tracing
        self.traces: Dict[str, Dict] = {}
        
        # Performance tracking
        self.performance_data: List[Dict] = []
        
    def _setup_logging(self):
        """Configure logging system"""
        log_file = self.log_dir / f"edumentor_{datetime.now().strftime('%Y%m%d')}.log"
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # File handler for detailed logs
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        
        # Console handler for important logs
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        
        # Configure root logger
        logging.basicConfig(
            level=logging.DEBUG,
            handlers=[file_handler, console_handler]
        )
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        Get logger for specific component
        
        Args:
            name: Logger name (e.g., 'tutor_agent', 'orchestrator')
            
        Returns:
            Configured logger
        """
        return logging.getLogger(f"edumentor.{name}")
    
    def start_trace(
        self,
        trace_id: str,
        operation: str,
        metadata: Optional[Dict] = None
    ):
        """
        Start a new trace for request tracking
        
        Args:
            trace_id: Unique trace identifier
            operation: Name of operation being traced
            metadata: Additional metadata
        """
        self.traces[trace_id] = {
            "trace_id": trace_id,
            "operation": operation,
            "start_time": time.time(),
            "metadata": metadata or {},
            "events": [],
            "status": "in_progress"
        }
        
        self.get_logger("tracer").info(
            f"Started trace {trace_id} for operation: {operation}"
        )
    
    def add_trace_event(
        self,
        trace_id: str,
        event_name: str,
        data: Optional[Dict] = None
    ):
        """
        Add event to existing trace
        
        Args:
            trace_id: Trace identifier
            event_name: Name of the event
            data: Event data
        """
        if trace_id not in self.traces:
            return
        
        event = {
            "timestamp": time.time(),
            "event": event_name,
            "data": data or {}
        }
        
        self.traces[trace_id]["events"].append(event)
    
    def end_trace(
        self,
        trace_id: str,
        status: str = "success",
        result: Optional[Dict] = None
    ):
        """
        End a trace
        
        Args:
            trace_id: Trace identifier
            status: Trace status (success, error, timeout)
            result: Result data
        """
        if trace_id not in self.traces:
            return
        
        trace = self.traces[trace_id]
        trace["end_time"] = time.time()
        trace["duration"] = trace["end_time"] - trace["start_time"]
        trace["status"] = status
        trace["result"] = result or {}
        
        self.get_logger("tracer").info(
            f"Completed trace {trace_id}: {status} "
            f"(duration: {trace['duration']:.2f}s)"
        )
        
        # Save trace to file
        self._save_trace(trace_id, trace)
    
    def _save_trace(self, trace_id: str, trace_data: Dict):
        """Save trace to file for analysis"""
        trace_file = self.log_dir / "traces" / f"{trace_id}.json"
        trace_file.parent.mkdir(exist_ok=True)
        
        try:
            with open(trace_file, 'w') as f:
                json.dump(trace_data, f, indent=2)
        except Exception as e:
            self.get_logger("tracer").error(f"Failed to save trace: {e}")
    
    def record_metric(
        self,
        metric_name: str,
        value: float,
        tags: Optional[Dict] = None
    ):
        """
        Record a metric value
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            tags: Optional tags for grouping
        """
        metric_entry = {
            "timestamp": datetime.now().isoformat(),
            "metric": metric_name,
            "value": value,
            "tags": tags or {}
        }
        
        self.metrics[metric_name].append(metric_entry)
    
    def get_metrics_summary(self, metric_name: str) -> Dict:
        """
        Get summary statistics for a metric
        
        Args:
            metric_name: Name of the metric
            
        Returns:
            Summary statistics
        """
        if metric_name not in self.metrics:
            return {}
        
        values = [m["value"] for m in self.metrics[metric_name]]
        
        return {
            "count": len(values),
            "sum": sum(values),
            "mean": sum(values) / len(values) if values else 0,
            "min": min(values) if values else 0,
            "max": max(values) if values else 0
        }
    
    def log_performance(
        self,
        component: str,
        operation: str,
        duration: float,
        success: bool
    ):
        """
        Log performance data
        
        Args:
            component: Component name
            operation: Operation performed
            duration: Time taken in seconds
            success: Whether operation succeeded
        """
        perf_entry = {
            "timestamp": datetime.now().isoformat(),
            "component": component,
            "operation": operation,
            "duration": duration,
            "success": success
        }
        
        self.performance_data.append(perf_entry)
        
        # Also record as metric
        self.record_metric(
            f"performance.{component}.{operation}",
            duration,
            {"success": success}
        )
    
    def get_performance_report(self) -> Dict:
        """
        Generate performance report
        
        Returns:
            Performance summary by component and operation
        """
        if not self.performance_data:
            return {}
        
        report = defaultdict(lambda: defaultdict(list))
        
        for entry in self.performance_data:
            component = entry["component"]
            operation = entry["operation"]
            report[component][operation].append({
                "duration": entry["duration"],
                "success": entry["success"]
            })
        
        # Calculate statistics
        summary = {}
        for component, operations in report.items():
            summary[component] = {}
            for operation, data in operations.items():
                durations = [d["duration"] for d in data]
                successes = [d["success"] for d in data]
                
                summary[component][operation] = {
                    "count": len(data),
                    "avg_duration": sum(durations) / len(durations),
                    "min_duration": min(durations),
                    "max_duration": max(durations),
                    "success_rate": sum(successes) / len(successes) * 100
                }
        
        return summary
    
    def export_metrics(self, filepath: Optional[str] = None) -> str:
        """
        Export all metrics to JSON file
        
        Args:
            filepath: Optional custom filepath
            
        Returns:
            Path to exported file
        """
        if filepath is None:
            filepath = self.log_dir / f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            "exported_at": datetime.now().isoformat(),
            "metrics": dict(self.metrics),
            "performance": self.performance_data,
            "summary": self.get_performance_report()
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        self.get_logger("metrics").info(f"Metrics exported to {filepath}")
        return str(filepath)
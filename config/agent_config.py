"""
Agent Configuration
Centralized configuration for all agents
"""

# Orchestrator Configuration
ORCHESTRATOR_CONFIG = {
    "name": "EduMentor Orchestrator",
    "model": "gemini-2.0-flash-exp",
    "temperature": 0.7,
    "max_tokens": 1000,
    "routing_strategy": "intelligent",  # intelligent, round-robin, priority
}

# Tutor Agent Configuration
TUTOR_CONFIG = {
    "name": "Tutor Agent",
    "model": "gemini-2.0-flash-exp",
    "temperature": 0.7,  # Balanced for teaching
    "max_tokens": 1000,
    "teaching_style": "socratic",  # socratic, direct, exploratory
    "use_knowledge_base": True,
}

# Quiz Generator Configuration
QUIZ_CONFIG = {
    "name": "Quiz Generator",
    "model": "gemini-2.0-flash-exp",
    "temperature": 0.8,  # Higher for variety
    "max_tokens": 1500,
    "default_questions": 5,
    "difficulty_levels": ["easy", "medium", "hard"],
    "question_types": ["multiple_choice", "short_answer", "problem_solving"],
}

# Progress Tracker Configuration
PROGRESS_CONFIG = {
    "name": "Progress Tracker",
    "model": "gemini-2.0-flash-exp",
    "temperature": 0.6,  # Moderate for analytics
    "max_tokens": 1000,
    "analysis_depth": "detailed",  # basic, standard, detailed
    "report_frequency": "on_demand",  # daily, weekly, on_demand
}

# Concept Explainer Configuration
EXPLAINER_CONFIG = {
    "name": "Concept Explainer",
    "model": "gemini-2.0-flash-exp",
    "temperature": 0.7,
    "max_tokens": 1200,
    "explanation_style": "visual",  # visual, verbal, technical
    "use_analogies": True,
}

# Memory Bank Configuration
MEMORY_CONFIG = {
    "max_interactions": 50,  # Context compaction threshold
    "max_cache_size": 100,  # Number of students to keep in memory
    "compaction_enabled": True,
}

# Session Configuration
SESSION_CONFIG = {
    "max_inactive_hours": 24,
    "max_messages_per_session": 50,
    "auto_cleanup": True,
}

# Tool Configuration
TOOL_CONFIG = {
    "knowledge_base": {
        "enabled": True,
        "type": "simulated_mcp",  # simulated_mcp, real_mcp, vector_db
        "max_results": 5,
    },
    "assessment": {
        "enabled": True,
        "auto_grading": True,
    },
    "progress_storage": {
        "enabled": True,
        "storage_type": "json",  # json, sqlite, postgres
        "storage_path": "data/progress",
    },
}

# Observability Configuration
OBSERVABILITY_CONFIG = {
    "logging_level": "INFO",  # DEBUG, INFO, WARNING, ERROR
    "enable_tracing": True,
    "enable_metrics": True,
    "log_directory": "logs",
    "metrics_export_interval": 3600,  # seconds
}

# General System Configuration
SYSTEM_CONFIG = {
    "project_name": "EduMentor AI",
    "version": "1.0.0",
    "environment": "development",  # development, staging, production
    "max_concurrent_requests": 10,
    "request_timeout": 30,  # seconds
}
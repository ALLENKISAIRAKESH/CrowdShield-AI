"""Configuration management for CrowdShield AI."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load local .env if present
load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Application runtime settings with environment overrides."""

    aws_region: str = os.environ.get("AWS_REGION", "us-east-1")
    aws_profile: Optional[str] = os.environ.get("AWS_PROFILE", None)
    bedrock_model_id: str = os.environ.get("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")
    strands_decider_url: str = os.environ.get("STRANDS_DECIDER_URL", "http://127.0.0.1:8099")
    confidence_threshold: float = float(os.environ.get("CROWDSHIELD_CONFIDENCE_THRESHOLD", "0.70"))
    log_level: str = os.environ.get("CROWDSHIELD_LOG_LEVEL", "INFO")
    timeout_seconds: float = float(os.environ.get("CROWDSHIELD_TIMEOUT_SECONDS", "30.0"))


settings = Settings()

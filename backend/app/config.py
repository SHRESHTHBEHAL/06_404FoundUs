"""
Configuration settings for the Travel Assistant backend.

Loads settings from environment variables.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# ============================================================================
# API Keys
# ============================================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")


# ============================================================================
# Application Settings
# ============================================================================

# Use mock data instead of real travel APIs
USE_MOCK = os.getenv("MOCK_DATA", "true").lower() == "true"

# Environment (development, production)
ENV = os.getenv("ENV", "development")


# ============================================================================
# Server Configuration
# ============================================================================

HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))


# ============================================================================
# Feature Flags
# ============================================================================

# Enable streaming for partial results
ENABLE_STREAMING = os.getenv("ENABLE_STREAMING", "true").lower() == "true"

# Enable interruption handling
ENABLE_INTERRUPTION = os.getenv("ENABLE_INTERRUPTION", "true").lower() == "true"

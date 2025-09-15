# Test configuration for the Social Companionship Agent
# Copy this to .env and add your real API keys

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# Security
API_KEY=test-api-key-123
ALLOWED_ORIGINS=["*"]

# External API Keys (Add your real keys here)
NEWS_API_TOKEN=your-news-api-token-here
LIBRIVOX_API_KEY=your-librivox-api-key-here
ELEVENLABS_API_KEY=your-elevenlabs-api-key-here

# Content Settings
DEFAULT_LANGUAGE=es
MAX_CONTENT_DURATION=120
CACHE_TTL=3600

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_BURST=10

# Session Management
SESSION_TIMEOUT=1800
MAX_SESSIONS=1000

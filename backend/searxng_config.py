"""
SearXNG Konfiguration für KYC Research Backend
"""

import os
from typing import List

# SearXNG URLs - können über Environment Variables überschrieben werden
DEFAULT_SEARXNG_URLS = [
    "https://localhost:8080",
    "https://searx.tuxcloud.net", 
    "https://search.metager.org",
    "https://searx.tiekoetter.com"
]

# Konfiguration per Environment Variable oder Defaults
SEARXNG_URL = os.getenv("SEARXNG_URL", DEFAULT_SEARXNG_URLS[1])  # Fallback URL
SEARXNG_ALTERNATIVE_URLS = [
    url for url in DEFAULT_SEARXNG_URLS if url != SEARXNG_URL
]

# Timeout-Konfiguration
SEARXNG_TIMEOUT = int(os.getenv("SEARXNG_TIMEOUT", "30"))
RESEARCH_TIMEOUT = int(os.getenv("RESEARCH_TIMEOUT", "60"))

# Trusted Domains für Unternehmensforschung
TRUSTED_DOMAINS = [
    "handelsregister.de",
    "bundesanzeiger.de", 
    "creditreform.de",
    "schufa.de",
    "unternehmen24.de",
    "firmenwissen.de",
    "wirtschaftswoche.de",
    "handelsblatt.com",
    "faz.net",
    "spiegel.de",
    "sueddeutsche.de"
]

# Suchstrategien für verschiedene Frage-Typen
SEARCH_ENGINES_BY_CATEGORY = {
    "general": ["google", "bing", "duckduckgo"],
    "news": ["google", "bing", "news"],
    "academic": ["scihub", "arxiv", "google_scholar"],
    "financial": ["google", "bing", "yahoo_finance"]
}

# Rate Limiting
MAX_REQUESTS_PER_MINUTE = 30
MAX_CONCURRENT_REQUESTS = 5

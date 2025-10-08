"""
SearXNG Konfiguration für KYC Research Backend
"""

import os
from typing import List

# SearXNG URLs - können über Environment Variables überschrieben werden
DEFAULT_SEARXNG_URLS = [
    "http://localhost:8080",            # Lokale Docker-Instanz (HTTP!)
    "https://searx.prvcy.eu",          # Aktuell verfügbare öffentliche Instanz
    "https://searx.tuxcloud.net",       # Häufig verfügbar (aber oft rate-limited)
    "https://search.metager.org",      # Alternative (manchmal down)
    "https://searx.tiekoetter.com"      # Backup
]

# Konfiguration per Environment Variable oder Defaults
SEARXNG_URL = os.getenv("SEARXNG_URL", DEFAULT_SEARXNG_URLS[0])  # Lokale Instanz zuerst
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

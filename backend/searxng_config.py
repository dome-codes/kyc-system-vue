"""
SearXNG Konfiguration für KYC Research Backend
"""

import os
from typing import List

# SearXNG URLs - optimiert für bessere Performance
DEFAULT_SEARXNG_URLS = [
    "http://localhost:8080",            # Lokale Docker-Instanz (HTTP!) - Primär
    "https://searx.prvcy.eu",          # Backup 1 - Stabile öffentliche Instanz
    "https://searx.tiekoetter.com"      # Backup 2 - Weniger genutzt, oft verfügbar
]

# Konfiguration per Environment Variable oder Defaults
SEARXNG_URL = os.getenv("SEARXNG_URL", DEFAULT_SEARXNG_URLS[0])  # Lokale Instanz zuerst
SEARXNG_ALTERNATIVE_URLS = [
    url for url in DEFAULT_SEARXNG_URLS if url != SEARXNG_URL
]

# Timeout-Konfiguration - optimiert für bessere Performance
SEARXNG_TIMEOUT = int(os.getenv("SEARXNG_TIMEOUT", "15"))  # Reduziert für schnellere Antworten
RESEARCH_TIMEOUT = int(os.getenv("RESEARCH_TIMEOUT", "30"))  # Reduziert für bessere UX

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

# Suchstrategien für verschiedene Frage-Typen - optimiert für KYC
SEARCH_ENGINES_BY_CATEGORY = {
    "general": ["google", "bing"],  # Reduziert auf beste Engines
    "news": ["google", "bing"],
    "academic": ["google"],  # Google Scholar über Google
    "financial": ["google", "bing"]
}

# Rate Limiting - optimiert für bessere Performance
MAX_REQUESTS_PER_MINUTE = 20  # Reduziert für weniger Interferenz
MAX_CONCURRENT_REQUESTS = 3   # Reduziert für bessere Stabilität

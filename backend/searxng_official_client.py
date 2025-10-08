"""
Einfacher und funktionierender SearXNG Client für das KYC Backend
"""

import httpx
import asyncio
import time
from typing import List, Dict, Any, Optional

class OfficialSearXNGClient:
    """Einfacher SearXNG Client - nur lokale Instanz"""
    
    def __init__(self, base_urls: List[str] = None):
        # Nur lokale SearXNG Instanz verwenden
        self.base_urls = base_urls or ["http://localhost:8080"]
        
    async def search(self, query: str, category: str = "general", 
                    lang: str = "de", safesearch: str = "1", 
                    engines: List[str] = None) -> List[Dict[str, Any]]:
        """Führt eine einfache SearXNG-Suche durch"""
        
        timeout = httpx.Timeout(30.0)
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            for url in self.base_urls:
                try:
                    print(f"🌐 Trying SearXNG: {url}")
                    
                    params = {
                        'q': query,
                        'category': category,
                        'lang': lang,
                        'safesearch': safesearch,
                        'format': 'json'
                    }
                    
                    if engines:
                        params['engines'] = ','.join(engines)
                    
                    response = await client.get(
                        f"{url}/search",
                        params=params,
                        headers={'User-Agent': 'KYC-Research-Bot/1.0'}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        results = data.get('results', [])
                        
                        if results:
                            print(f"✅ SearXNG success: {url} - {len(results)} results")
                            processed_results = []
                            
                            for result in results[:10]:  # Top 10 Ergebnisse
                                processed_results.append({
                                    'title': result.get('title', ''),
                                    'url': result.get('url', ''),
                                    'content': result.get('content', '')[:300],
                                    'engine': result.get('engine', 'unknown'),
                                    'timestamp': time.time(),
                                    'name': result.get('title', ''),  # Für Firmenvergleich
                                    'source_url': result.get('url', ''),
                                    'evidence': result.get('content', '')
                                })
                            return processed_results
                        else:
                            print(f"⚠️ SearXNG empty results from: {url}")
                            continue
                    
                    elif response.status_code == 429:
                        print(f"⚠️ SearXNG rate limited: {url}")
                        continue
                    else:
                        print(f"❌ SearXNG error {response.status_code}: {url}")
                        continue
                        
                except Exception as e:
                    print(f"❌ SearXNG connection failed for {url}: {e}")
                    continue
            
            print("🔄 All SearXNG instances failed")
            return []
    
    async def company_search(self, company_name: str, location: str = "Deutschland") -> Dict[str, Any]:
        """Spezielle Suchfunktion für Unternehmensrecherche"""
        
        # Verschiedene Suchanfragen für bessere Ergebnisse
        search_queries = [
            f'"{company_name}" {location}',
            f'"{company_name}" GmbH {location}',
            f'"{company_name}" AG {location}',
            f'"{company_name}" Unternehmen {location}'
        ]
        
        all_results = []
        
        for query in search_queries:
            if len(all_results) >= 8:  # Genug Ergebnisse
                break
                
            query_results = await self.search(query, category="general", lang="de")
            if query_results:
                all_results.extend(query_results)
        
        return {
            'verification_status': 'ambiguous',  # Immer ambiguous für Vorschläge
            'suggestions': [],
            'search_results': all_results
        }

# Singleton-Instanz für das Backend
official_searxng_client = OfficialSearXNGClient()

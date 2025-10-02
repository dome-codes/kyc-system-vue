"""
SearXNG Client für echte Suchfunktionen im KYC Research Backend
"""

import requests
import json
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
import time
import random

class SearXNGClient:
    """Client für SearXNG Suchmaschine"""
    
    def __init__(self, searxng_url: str = None):
        from searxng_config import SEARXNG_URL, SEARXNG_ALTERNATIVE_URLS, TRUSTED_DOMAINS
        
        self.main_url = searxng_url or SEARXNG_URL
        self.alternative_urls = SEARXNG_ALTERNATIVE_URLS
        self.trusted_domains = TRUSTED_DOMAINS
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'KYC-Research-Bot/1.0'
        })
        self.current_url_index = 0
    
    async def search(self, query: str, category: str = "general", 
                    lang: str = "de", safesearch: str = "1", 
                    engines: List[str] = None) -> List[Dict[str, Any]]:
        """
        Führt eine Suche über SearXNG durch
        
        Args:
            query: Suchausdruck
            category: Suchkategorie (general, images, videos, etc.)
            lang: Sprache der Ergebnisse
            safesearch: Sicherheitssuche (0,1,2)
            engines: Liste der zu verwendenden Suchmaschinen
        
        Returns:
            Liste der Suchergebnisse
        """
        all_urls = [self.main_url] + self.alternative_urls
        
        for attempt, url in enumerate(all_urls):
            try:
                # SearXNG API Request
                params = {
                    'q': query,
                    'category': category,
                    'lang': lang,
                    'safesearch': safesearch,
                    'format': 'json'
                }
                
                if engines:
                    params['engines'] = ','.join(engines)
                
                # Timeout für SearXNG Request
                response = self.session.get(
                    f"{url}/search",
                    params=params,
                    timeout=30,
                    headers={'User-Agent': 'KYC-Research-Bot/1.0'}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results = self._process_search_results(data)
                    if results:  # Wenn Ergebnisse vorhanden sind, verwende sie
                        print(f"SearXNG erfolgreich: {url}")
                        return results
                    else:
                        print(f"SearXNG empty results from {url}, trying next...")
                        continue
                else:
                    print(f"SearXNG Error {response.status_code} from {url}")
                    continue
                    
            except Exception as e:
                print(f"SearXNG connection failed for {url}: {e}")
                continue
        
        print("Alle SearXNG URLs fehlgeschlagen, verwende Fallback")
        return self._get_fallback_results(query)
    
    def _process_search_results(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Verarbeitet SearXNG Suchergebnisse"""
        results = []
        
        for result in data.get('results', []):
            processed_result = {
                'title': result.get('title', ''),
                'url': result.get('url', ''),
                'content': result.get('content', ''),
                'engine': result.get('engine', ''),
                'category': result.get('category', 'general'),
                'parsed_url': result.get('parsed_url', {}),
                'template': result.get('template', ''),
                'engines': result.get('engines', []),
                'positions': result.get('positions', []),
                'score': result.get('score', 0),
                'timestamp': time.time()
            }
            results.append(processed_result)
        
        return results
    
    def _get_fallback_results(self, query: str) -> List[Dict[str, Any]]:
        """Verbesserte Fallback-Ergebnisse wenn SearXNG nicht verfügbar ist"""
        try:
            from web_search_fallback import web_search_fallback
            # Verwende den intelligenten Web-Search-Fallback
            fallback_data = await web_search_fallback.search_company_fallback(query.split()[0], "Deutschland")
            return fallback_data[:3]  # Top 3 Ergebnisse
        except Exception as e:
            print(f"Fallback error: {e}")
            # Basis-Fallback
            return [
                {
                    'title': f'Recherche-Ergebnis für "{query}"',
                    'url': 'https://research.fallback.com/query',
                    'content': f'Für "{query}" wurden Recherche-Daten generiert. Weiterführende Recherche über Handelsregister oder Bundesanzeiger empfohlen.',
                    'engine': 'fallback',
                    'category': 'general',
                    'score': 0.4,
                    'timestamp': time.time()
                }
            ]
    
    async def search_company(self, company_name: str, country: str = "Deutschland") -> Dict[str, Any]:
        """
        Spezifische Unternehmenssuche
        
        Args:
            company_name: Firmenname
            country: Land
            
        Returns:
            Verarbeitete Unternehmensdaten
        """
        # Verschiedene Suchstrategien für Unternehmensverifizierung
        search_queries = [
            f'"{company_name}" {country}',
            f'"{company_name}" GmbH {country}',
            f'"{company_name}" AG {country}',
            f'Hauptversammlung "{company_name}" {country}',
            f'Bilanz "{company_name}" {country}',
            f'Insolvenz "{company_name}" {country}'
        ]
        
        company_data = {
            'name': company_name,
            'country': country,
            'verification_status': 'pending',
            'search_results': [],
            'suggestions': [],
            'risk_indicators': [],
            'compliance_info': []
        }
        
        for query in search_queries:
            try:
                results = await self.search(query, category="general", lang="de")
                company_data['search_results'].extend(results[:3])  # Top 3 Ergebnisse pro Query
            except Exception as e:
                print(f"Fehler bei Suchquery '{query}': {e}")
        
        # Analysiere Ergebnisse für Unternehmensverifizierung
        company_data.update(self._analyze_company_results(company_data['search_results']))
        
        return company_data
    
    def _analyze_company_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analysiert Suchergebnisse für Unternehmensinfo"""
        verification_status = 'ambiguous'
        suggestions = []
        risk_indicators = []
        compliance_info = []
        
        for result in results:
            title = result.get('title', '').lower()
            content = result.get('content', '').lower()
            url = result.get('url', '').lower()
            
            # Risiko-Indikatoren erkennen
            risk_keywords = ['insolvenz', 'zahltag', 'insolvenzantrag', 'vergleich', 'stilllegen']
            for keyword in risk_keywords:
                if keyword in title or keyword in content:
                    risk_indicators.append({
                        'type': keyword,
                        'severity': 'medium',
                        'source': result.get('url', ''),
                        'evidence': result.get('content', '')[:200]
                    })
            
            # Compliance-Informationen
            compliance_keywords = ['bilanz', 'jahresabschluss', 'hauptversammlung', 'gesellschaftsmittel']
            for keyword in compliance_keywords:
                if keyword in title or keyword in content:
                    compliance_info.append({
                        'type': keyword,
                        'source': result.get('url', ''),
                        'summary': result.get('content', '')[:150]
                    })
            
            # Formale Unternehmensidentifikation
            legal_keywords = ['gmbh', 'ag', 'kb', 'ug', 'genossenschaft', 'gesellschaft']
            for keyword in legal_keywords:
                if keyword in title:
                    suggestions.append({
                        'name': result.get('title', ''),
                        'type': keyword.upper(),
                        'source': result.get('url', ''),
                        'evidence': result.get('content', '')[:100]
                    })
        
        # Status bestimmen
        if not risk_indicators and compliance_info:
            verification_status = 'verified'
        elif len(risk_indicators) > len(compliance_info):
            verification_status = 'high_risk'
        
        return {
            'verification_status': verification_status,
            'suggestions': suggestions[:5],  # Top 5 Vorschläge
            'risk_indicators': risk_indicators,
            'compliance_info': compliance_info[:5]
        }
    
    async def research_knowledge_question(self, question: str, company_name: str, 
                                        context: str = "") -> Dict[str, Any]:
        """
        Recherchiert eine spezifische Wissensfrage für ein Unternehmen
        
        Args:
            question: Die Frage (z.B. "Geschäftsentwicklung")
            company_name: Firmenname
            context: Zusätzlicher Kontext
            
        Returns:
            Strukturierte Antwort mit Quellen
        """
        # Optimierte Suchstrategie basierend auf der Frage
        question_lower = question.lower()
        search_strategy = self._get_search_strategy(question_lower, company_name, context)
        
        results = []
        for query in search_strategy['queries']:
            try:
                query_results = await self.search(query, lang="de")
                results.extend(query_results[:2])  # Top 2 pro Query
            except Exception as e:
                print(f"Fehler bei Recherche-Query '{query}': {e}")
        
        # Formatiere Antwort
        answer_data = {
            'question': question,
            'company': company_name,
            'answer': self._generate_answer_from_results(results, question_lower),
            'sources': self._extract_sources(results),
            'confidence': self._calculate_confidence(results),
            'research_method': search_strategy['method']
        }
        
        return answer_data
    
    def _get_search_strategy(self, question: str, company_name: str, context: str) -> Dict[str, Any]:
        """Bestimmt die optimale Suchmethode basierend auf der Frage"""
        
        if 'geschäft' in question or 'entwicklung' in question:
            return {
                'method': 'business_development',
                'queries': [
                    f'"{company_name}" Geschäftsentwicklung 2024',
                    f'"{company_name}" Umsatzentwicklung',
                    f'"{company_name}" Wachstum Strategie',
                    f'"{company_name}" Marktposition Konkurrenz'
                ]
            }
        elif 'finanz' in question or 'kennzahl' in question:
            return {
                'method': 'financial_analysis',
                'queries': [
                    f'"{company_name}" Bilanz 2024',
                    f'"{company_name}" Jahresabschluss',
                    f'"{company_name}" Eigenkapitalquote',
                    f'"{company_name}" Liquiditätsgrade'
                ]
            }
        elif 'rechtlich' in question or 'compliance' in question:
            return {
                'method': 'legal_compliance',
                'queries': [
                    f'"{company_name}" Compliance Verstöße',
                    f'"{company_name}" rechtliche Verfahren',
                    f'"{company_name}" Bußgeld Verfahren',
                    f'"{company_name}" Aufsichtsbehörde'
                ]
            }
        elif 'geschäftsführer' in question or 'gesellschafter' in question:
            return {
                'method': 'management_structure',
                'queries': [
                    f'"{company_name}" Geschäftsführung',
                    f'"{company_name}" Gesellschafter Struktur',
                    f'"{company_name}" Vorstand Aufsichtsrat',
                    f'"{company_name}" Inhaber Verwaltung'
                ]
            }
        elif 'solvenz' in question or 'wirtschaftlich' in question:
            return {
                'method': 'solvency_analysis',
                'queries': [
                    f'"{company_name}" Solvenz Bonität',
                    f'"{company_name}" Kreditwürdigkeit Schufa',
                    f'"{company_name}" Zahlungsfähigkeit',
                    f'"{company_name}" Rating Agentur'
                ]
            }
        elif 'presse' in question or 'bewertung' in question:
            return {
                'method': 'reputation_analysis',
                'queries': [
                    f'"{company_name}" Presse Bewertung',
                    f'"{company_name}" Kundenmeinung',
                    f'"{company_name}" Mitarbeiterbewertung',
                    f'"{company_name}" Skandal Auffälligkeit'
                ]
            }
        elif 'branchenposition' in question or 'markt' in question:
            return {
                'method': 'market_position',
                'queries': [
                    f'"{company_name}" Branchenposition',
                    f'"{company_name}" Marktanteil',
                    f'"{company_name}" Wettbewerb Konkurrenz',
                    f'"{company_name}" Industrie Ranking'
                ]
            }
        elif 'insolvenz' in question or 'mahnung' in question:
            return {
                'method': 'risk_assessment',
                'queries': [
                    f'"{company_name}" Insolvenz Mahnung',
                    f'"{company_name}" Zahlungsstörung',
                    f'"{company_name}" Vollstreckung Zwangsvollstreckung',
                    f'"{company_name}" Liquidität Problem'
                ]
            }
        else:
            # Allgemeine Recherche
            return {
                'method': 'general_research',
                'queries': [
                    f'"{company_name}" {question}',
                    f'"{company_name}" {question} 2024',
                    f'"{company_name}" aktuell {question}'
                ]
            }
    
    def _generate_answer_from_results(self, results: List[Dict[str, Any]], question: str) -> str:
        """Generiert eine strukturierte Antwort aus den Suchergebnissen"""
        if not results:
            return "Für diese Frage konnten keine relevanten Informationen gefunden werden."
        
        # Analysiere Ergebnisse und erstelle konsistente Antwort
        key_findings = []
        negative_indicators = []
        positive_indicators = []
        
        risk_keywords = ['insolvenz', 'zahltag', 'zahlenstörung', 'vergleich', 'aussetzen', 'kündigung']
        positive_keywords = ['wachstum', 'gewinn', 'steigerung', 'expansion', 'preis', 'positiv']
        
        for result in results:
            content = result.get('content', '').lower()
            title = result.get('title', '').lower()
            
            # Risiko- vs. Positive-Indikatoren erkennen
            for keyword in risk_keywords:
                if keyword in content or keyword in title:
                    negative_indicators.append(f"Zeichen für {keyword}: {result.get('content', '')[:100]}")
            
            for keyword in positive_keywords:
                if keyword in content or keyword in title:
                    positive_indicators.append(f"Positiver Befund zu {keyword}: {result.get('content', '')[:100]}")
        
        # Antwort zusammenbauen
        answer_parts = []
        
        if positive_indicators:
            answer_parts.append(f"Positive Aspekte: {' '.join(positive_indicators[:2])}")
        
        if negative_indicators:
            answer_parts.append(f"Zu beobachtende Faktoren: {' '.join(negative_indicators[:2])}")
        
        # Fallback wenn keine klaren Indikatoren
        if not answer_parts:
            answer_parts.append(f"Rechercheergebnisse deuten auf folgende Situation hin: {results[0].get('content', '')[:200]}...")
        
        return " | ".join(answer_parts)
    
    def _extract_sources(self, results: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Extrahiert strukturierte Quellenangaben"""
        sources = []
        
        for result in results[:5]:  # Top 5 Quellen
            source_info = {
                'name': self._extract_source_name(result.get('url', '')),
                'url': result.get('url', ''),
                'title': result.get('title', ''),
                'engine': result.get('engine', 'unknown')
            }
            sources.append(source_info)
        
        return sources
    
    def _extract_source_name(self, url: str) -> str:
        """Extrahiert einen lesbaren Namen aus der URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            domain_mapping = {
                'www.handelsregister.de': 'Handelsregister',
                'www.bundesanzeiger.de': 'Bundesanzeiger',
                'www.creditreform.de': 'Creditreform',
                'www.schufa.de': 'Schufa',
                'www.unternehmen24.de': 'Unternehmen24',
                'www.firmenwissen.de': 'Firmenwissen',
                'www.wirtschaftswoche.de': 'WirtschaftsWoche',
                'www.handelsblatt.com': 'Handelsblatt',
                'www.faz.net': 'FAZ',
                'www.spiegel.de': 'Spiegel',
                'www.sueddeutsche.de': 'Süddeutsche Zeitung'
            }
            
            # Remove www. prefix
            clean_domain = domain.replace('www.', '')
            
            for mapped_domain, name in domain_mapping.items():
                if mapped_domain in clean_domain or clean_domain in mapped_domain:
                    return name
            
            # Fallback: Domain ohne Subdomain
            return '.'.join(clean_domain.split('.')[-2:])
            
        except Exception:
            return "Unbekannte Quelle"
    
    def _calculate_confidence(self, results: List[Dict[str, Any]]) -> float:
        """Berechnet das Vertrauen in die Antwort (0.0-1.0)"""
        if not results:
            return 0.0
        
        # Bewerte nach Anzahl, Qualität und Relevanz der Ergebnisse
        base_confidence = min(len(results) / 10, 0.8)  # Mehr Ergebnisse = höheres Vertrauen
        
        # Bonus für relevante Domains
        domain_bonus = 0.0
        trusted_domains = ['handelsregister', 'bundesanzeiger', 'creditreform', 'schufa']
        
        for result in results:
            url = result.get('url', '').lower()
            for domain in trusted_domains:
                if domain in url:
                    domain_bonus += 0.05
        
        return min(base_confidence + domain_bonus, 1.0)

# Singleton-Instanz
searxng_client = SearXNGClient()

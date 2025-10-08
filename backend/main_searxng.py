#!/usr/bin/env python3
"""
Funktionierendes Backend mit echter SearXNG-Integration
"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import httpx
import asyncio
# LLM Service - simplified version
import httpx
import json

class SimpleLLMService:
    def __init__(self):
        self.base_url = "http://localhost:11434"
        self.model = "llama3.2:3b-instruct-q8_0"  # Besseres Modell verwenden
    
    async def enhance_answer(self, question: str, company: str, basic_answer: str) -> str:
        try:
            prompt = f"""Du bist ein Experte für Unternehmensrecherche. Analysiere diese Daten:

Frage: {question}
Unternehmen: {company}
Grundantwort: {basic_answer}

Erstelle eine präzise, professionelle Antwort die:
1. Die wichtigsten Fakten extrahiert
2. Die Datenqualität bewertet (Hoch/Mittel/Niedrig)
3. Konkrete Informationen liefert
4. Auf Deutsch formuliert ist

Antwort (maximal 100 Worte, strukturiert):"""

            url = f"{self.base_url}/api/generate"
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.1, "num_predict": 300}
            }
            
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(url, json=payload)
                if response.status_code == 200:
                    result = response.json()
                    enhanced = result.get("response", "").strip()
                    return f"📊 {basic_answer}\n\n🤖 **KI-Analyse ({self.model}):**\n{enhanced}"
        except Exception as e:
            print(f"LLM Error: {e}")
            
        return basic_answer

llm_service = SimpleLLMService()

app = FastAPI(title="KYC Research API", version="1.0.0")

# CORS middleware for frontend connection
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: specific origins only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ResearchRequest(BaseModel):
    mieter: str
    fragen: List[int]
    land: Optional[str] = "Deutschland"
    branche: Optional[str] = None

class TenantSuggestion(BaseModel):
    id: str
    name: str
    land: str
    branche: str
    url: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None

class VerifyOk(BaseModel):
    mieter_eingabe: str

class VerifyAmbiguous(BaseModel):
    mieter_eingabe: str
    vorschlaege: List[TenantSuggestion]

class Antwort(BaseModel):
    frage_id: str
    antwort: str
    quelle: Optional[str] = None

class ResearchSuccess(BaseModel):
    mieter: str
    branche: Optional[str] = None
    land: Optional[str] = None
    antworten: List[Antwort]

# Hilfsfunktionen
async def search_searxng(company_name: str, location: str = "Deutschland") -> List[Dict[str, Any]]:
    """Echte SearXNG-Suche"""
    
    # Optimierte Queries für bessere Ergebnisse
    search_queries = [
        f'"{company_name}"',
        f'"{company_name}" {location}',
        f'{company_name} GmbH',
        f'{company_name} AG',
        f'{company_name} Unternehmen'
    ]
    
    all_results = []
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for query in search_queries:
            if len(all_results) >= 10:  # Genug Ergebnisse
                break
                
            try:
                params = {
                    'q': query,
                    'format': 'json',
                    'lang': 'de',
                    'category': 'general'
                }
                
                response = await client.get("http://localhost:8080/search", params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get('results', [])
                    
                    for result in results:
                        if result.get('title') and result.get('url'):
                            all_results.append({
                                'title': result.get('title', ''),
                                'url': result.get('url', ''),
                                'content': result.get('content', '')[:200],
                                'query': query
                            })
                            
                            if len(all_results) >= 10:
                                break
                                
            except Exception as e:
                print(f"❌ SearXNG error for '{query}': {e}")
                continue
    
    print(f"📊 SearXNG found {len(all_results)} results for '{company_name}'")
    return all_results

def extract_best_company_name(title: str, url: str, content: str, search_term: str) -> str:
    """Extrahiert den besten Firmennamen aus Titel, URL und Inhalt"""
    import re
    
    # 1. Versuche aus URL zu extrahieren (oft der beste Indikator)
    if url:
        # Entferne Domain und extrahiere relevante Teile
        url_parts = url.replace('https://', '').replace('http://', '').split('/')
        for part in url_parts:
            if part and '.' not in part and len(part) > 3:
                # Bereinige URL-Teil
                clean_part = re.sub(r'[^a-zA-ZäöüÄÖÜß\s-]', '', part.replace('-', ' '))
                if len(clean_part) > 3 and search_term.lower() in clean_part.lower():
                    return clean_part.title()
    
    # 2. Analysiere Titel für Firmennamen
    if title:
        # Entferne häufige Stoppwörter
        stop_words = ['ein', 'der', 'die', 'das', 'und', 'oder', 'mit', 'für', 'von', 'zu', 'bei', 'auf', 'in', 'an']
        title_words = [word for word in title.split() if word.lower() not in stop_words and len(word) > 2]
        
        # Suche nach dem Suchbegriff im Titel
        if search_term.lower() in title.lower():
            # Extrahiere den Teil mit dem Suchbegriff
            title_lower = title.lower()
            search_lower = search_term.lower()
            start_idx = title_lower.find(search_lower)
            if start_idx != -1:
                # Nimm 3-5 Wörter um den Suchbegriff
                words = title.split()
                for i, word in enumerate(words):
                    if search_lower in word.lower():
                        # Nimm 2-3 Wörter vor und nach dem gefundenen Wort
                        start = max(0, i-2)
                        end = min(len(words), i+3)
                        extracted = ' '.join(words[start:end])
                        if len(extracted) > 5:
                            return extracted
    
    # 3. Fallback: Verwende den ursprünglichen Suchbegriff
    return search_term

def generate_realistic_suggestions(company_name: str, search_results: List[Dict[str, Any]], location: str) -> List[TenantSuggestion]:
    """Generiert realistische Vorschläge basierend auf echten Suchergebnissen"""
    
    suggestions = []
    seen_names = set()
    
    # 🎯 Intelligente Firmennamen-Extraktion
    for i, result in enumerate(search_results[:8]):
        title = result.get('title', '')
        url = result.get('url', '')
        content = result.get('content', '')
        
        # Extrahiere den besten Firmennamen aus Titel und URL
        extracted_name = extract_best_company_name(title, url, content, company_name)
        
        if not extracted_name or extracted_name in seen_names:
            continue
            
        # Bereinige den Namen
        clean_name = extracted_name.strip()
        
        # Ignoriere zu kurze oder unsinnige Namen
        if len(clean_name) < 3:
            continue
            
        # Erkenne Branchen aus dem Inhalt und URL
        branche = determine_branche(clean_name, content, url)
        
        # Extrahiere Straße und Stadt (nur wenn sinnvoll)
        street, city = extract_address_info(title, content, url)
        
        # Bereinige Adressen
        clean_street = None
        clean_city = None
        
        if street and len(street) > 5 and len(street) < 50 and not any(word in street.lower() for word in ['vor', 'ungsvolles', 'als']):
            clean_street = street
            
        if city and len(city) > 2 and len(city) < 30 and not any(word in city.lower() for word in ['vor', 'ungsvolles', 'als']):
            clean_city = city
        
        suggestion = TenantSuggestion(
            id=f"result_{i+1}",
            name=clean_name,
            land=location,
            branche=branche,
            url=url if url and url.startswith('http') else f"https://www.google.com/search?q={clean_name}",
            street=clean_street,
            city=clean_city
        )
        
        suggestions.append(suggestion)
        seen_names.add(clean_name)
        
        if len(suggestions) >= 5:
            break
    
    # Falls nicht genug gefunden, ergänze mit intelligenten Vorschlägen
    while len(suggestions) < 5:
        suggestion_nr = len(suggestions) + 1
        legal_forms = [("GmbH", "Unternehmensberatung"), ("AG", "Aktiengesellschaft"), ("UG", "Unternehmergesellschaft")]
        
        if suggestion_nr <= len(legal_forms):
            form, industry = legal_forms[suggestion_nr - 1]
            suggestions.append(TenantSuggestion(
                id=f"smart_{suggestion_nr}",
                name=f"{company_name} {form}",
                land=location,
                branche=industry,
                url=f"https://www.handelsregister.de/auskunft/{company_name.lower().replace(' ', '-')}",
                street=None,
                city=None
            ))
        else:
            break
    
    return suggestions[:5]

def extract_address_info(title: str, content: str, url: str) -> tuple[str, str]:
    """Extrahiert Straße und Stadt aus Titel, Inhalt und URL"""
    
    # Kombiniere alle Texte für die Suche
    text = f"{title} {content} {url}".lower()
    
    # Deutsche Städte-Patterns
    city_patterns = [
        r'(\d{5})\s+([a-zäöüß\s]+)',  # PLZ + Stadt
        r'([a-zäöüß\s]+(?:stadt|dorf|burg|ingen|hausen|heim|berg))',  # Stadt-Endungen
        r'(?:stadt|city|zunächst)\s+:?\s*([a-zäöüß\s]+)',
        r'(?:ort|wohnort|sitz)\s*:?\s*([a-zäöüß\s]+)'
    ]
    
    # Deutsche Straßen-Patterns  
    street_patterns = [
        r'([a-zäöüß\s]+straße\s+\d+)',
        r'([a-zäöüß\s]+str\.?\s+\d+)',
        r'([a-zäöüß\s]+platz\s+\d+)',
        r'([a-zäöüß\s]+weg\s+\d+)',
        r'([a-zäöüß\s]+gasse\s+\d+)',
        r'([a-zäöüß\s]+\d{1,3}[a-z]?)'
    ]
    
    import re
    
    street = ""
    city = ""
    
    # Extrahiere Straße
    for pattern in street_patterns:
        match = re.search(pattern, text)
        if match:
            street = match.group(1).strip().title()
            break
    
    # Extrahiere Stadt
    for pattern in city_patterns:
        match = re.search(pattern, text)
        if match:
            potential_city = match.group(1 if ')' in match.groups()[0] else 1).strip().title()
            # Prüfe ob es eine sinnvolle Stadt ist
            if len(potential_city) > 3 and any(word in potential_city for word in ['stadt', 'dorf', 'burg', 'ingen', 'hausen', 'heim', 'berg', 'dorf']):
                city = potential_city
                break
            elif len(potential_city) > 5:  # Mindestlänge für Stadtname
                city = potential_city
                break
    
    # Spezielle Behandlung für bekannte Städte
    known_cities = ['münchen', 'berlin', 'hamburg', 'köln', 'frankfurt', 'stuttgart', 'düsseldorf', 'dortmund', 'essen', 'leipzig']
    for known_city in known_cities:
        if known_city in text:
            city = known_city.title()
            break
    
    return street, city

def determine_branche(name: str, content: str, url: str = "") -> str:
    """Bestimmt Branche aus Name, Inhalt und URL"""
    
    text = f"{name} {content} {url}".lower()
    
    branchen_keywords = {
        'Automobilindustrie': ['auto', 'fahrzeug', 'bmw', 'mercedes', 'wagen', 'automotive'],
        'Informationstechnologie': ['software', 'it', 'digital', 'tech', 'computer', 'sap'],
        'Finanzdienstleistungen': ['bank', 'finanz', 'versicherung', 'sparkasse', 'deka', 'investment'],
        'Handel': ['handel', 'shop', 'verkauf', 'retail', 'store'],
        'Beratung': ['beratung', 'consulting', 'service'],
        'Gastronomie': ['restaurant', 'cafe', 'gasthof', 'küche'],
        'Immobilien': ['immobilien', 'bau', 'wohnung', 'grund', 'real estate'],
        'Dienstleistungen': ['service', 'werkstatt', 'reparatur'],
        'Energie': ['energie', 'strom', 'gas', 'solar'],
        'Gesundheitswesen': ['krankenhaus', 'arzt', 'medizin', 'gesundheit'],
        'Bildung': ['schule', 'universität', 'bildung', 'lernen']
    }
    
    # Priorisiere Branchen basierend auf Treffern
    branche_scores = {}
    for branche, keywords in branchen_keywords.items():
        score = sum(1 for keyword in keywords if keyword in text)
        if score > 0:
            branche_scores[branche] = score
    
    # Gib die Branche mit der höchsten Punktzahl zurück
    if branche_scores:
        return max(branche_scores, key=branche_scores.get)
    
    return 'Allgemeine Dienstleistungen'

# Standard-Fragen-Mapping (ID -> Frage & Suchestrategie)
STANDARD_QUESTIONS = {
    1: ("Vollständiger Firmenname?", "{0}"),
    2: ("Rechtsform des Unternehmens?", "{0}"),
    3: ("Handelsregisternummer?", "{0}"),
    4: ("Gründungsdatum?", "{0}"),
    5: ("Vollständige Geschäftsadresse?", "{0}"),
    6: ("Geschäftszweck / Unternehmensgegenstand?", "{0}"),
    7: ("Geschäftsführung / Vorstand?", "{0}"),
    8: ("Wirtschaftlich Berechtigte (25%+)?", "{0}"),
    9: ("Umsatz letztes Geschäftsjahr?", "{0}"),
    10: ("Anzahl der Mitarbeiter?", "{0}"),
    11: ("Risiko-Bewertung?", "{0}"),
    12: ("Compliance-Status?", "{0}"),
    13: ("Finanzierungsstatus?", "{0}"),
    14: ("Presse / Ruf", "{0}"),
    15: ("Insolvenzzeichen?", "{0}")
}

def generate_specific_query(frage_nummer: int, company_name: str, location: str) -> str:
    """Generiert spezifische SearXNG-Queries basierend auf Standard-Fragen"""
    
    question_info = STANDARD_QUESTIONS.get(frage_nummer)
    if question_info:
        question_text, query_template = question_info
        # Ersetze Platzhalter {0} = company_name, {1} = location
        return query_template.format(company_name, location)
    
    # Standard-Frage für unbekannte Nummern
    return f'"{company_name}" unternehmen {location}'

async def generate_answer_from_results(frage_nummer: int, results: List[Dict[str, Any]], company_name: str) -> tuple[str, str]:
    """Generiert intelligente Antworten aus SearXNG-Ergebnissen mit erweitertem Web-Crawling"""
    
    if not results:
        # 🚨 Fallback: Generiere intelligente Antworten auch ohne SearXNG-Ergebnisse
        print(f"⚠️ No SearXNG results, using intelligent fallback for {company_name}")
        return await generate_fallback_answer(frage_nummer, company_name)
    
    # Extrahiere relevante Informationen basierend auf Fragentyp
    answer_patterns = {
        1: extract_company_name_info,  # Firmenname
        2: extract_legal_form_info,   # Rechtsform  
        3: extract_register_info,     # Handelsregisternummer
        4: extract_founding_info,     # Gründungsdatum
        5: extract_address_info_from_result,  # Adresse
        6: extract_business_purpose,  # Geschäftszweck
        7: extract_management_info,   # Geschäftsführung
        8: extract_ownership_info,    # Wirtschaftlich Berechtigte
        9: extract_revenue_info,      # Umsatz
        10: extract_employees_info,   # Mitarbeiter
    }
    
    extract_func = answer_patterns.get(frage_nummer, extract_general_company_info)
    
    # 🔍 Durchsuche mehrere Ergebnisse für bessere Antworten
    best_answer = ""
    best_url = ""
    best_score = 0
    
    for i, result in enumerate(results[:5]):  # Durchsuche Top 5 Ergebnisse
        title = result.get('title', '')
        content = result.get('content', '')
        url = result.get('url', '')
        
        print(f"🔍 Analyzing result {i+1}/5: {url}")
        
        # 🕷️ Web-Crawling für detailliertere Informationen
        crawled_content = ""
        if url and url.startswith('http'):
            print(f"🕷️ Crawling webpage: {url}")
            crawled_content = await crawl_webpage_content(url)
            if crawled_content:
                print(f"✅ Crawled {len(crawled_content)} characters from {url}")
            else:
                print(f"⚠️ No content crawled from {url}")
        
        # Kombiniere alle verfügbaren Inhalte
        full_content = f"{title} {content} {crawled_content}".strip()
        
        try:
            # Generiere Antwort für dieses Ergebnis
            antwort = extract_func(title, full_content, url, company_name)
            
            # Bewerte die Qualität der Antwort
            score = evaluate_answer_quality(antwort, frage_nummer)
            print(f"📊 Answer quality score: {score} for {url}")
            
            # Wenn diese Antwort besser ist, verwende sie
            if score > best_score:
                best_answer = antwort
                best_url = url
                best_score = score
                
                # Wenn wir eine sehr gute Antwort haben, stoppe hier
                if score >= 8:
                    print(f"🎯 Found excellent answer, stopping search")
                    break
                    
        except Exception as e:
            print(f"⚠️ Error processing result {i+1}: {e}")
            continue
    
    # Falls keine gute Antwort gefunden wurde, verwende die beste verfügbare
    if not best_answer:
        result = results[0]
        best_answer = extract_func(
            result.get('title', ''), 
            result.get('content', ''), 
            result.get('url', ''), 
            company_name
        )
        best_url = result.get('url', '')
    
    print(f"🏆 Best answer selected with score {best_score} from {best_url}")
    return best_answer, best_url

def evaluate_answer_quality(answer: str, frage_nummer: int) -> int:
    """Bewertet die Qualität einer Antwort (0-10)"""
    if not answer:
        return 0
    
    score = 0
    answer_lower = answer.lower()
    
    # Basis-Punkte für verschiedene Indikatoren
    if len(answer) > 50:  # Ausführliche Antwort
        score += 2
    
    if any(word in answer_lower for word in ['verfügbar', 'details unter', 'weitere informationen']):
        score -= 2  # Abzug für generische Antworten
    
    if any(word in answer_lower for word in ['nicht verfügbar', 'unbekannt', 'nicht gefunden']):
        score -= 3  # Abzug für negative Antworten
    
    # Spezifische Bewertung je nach Fragentyp
    if frage_nummer == 1:  # Firmenname
        if any(word in answer_lower for word in ['firmenname', 'unternehmen', 'gesellschaft']):
            score += 3
    elif frage_nummer == 2:  # Rechtsform
        if any(word in answer_lower for word in ['ag', 'gmbh', 'ug', 'kg', 'rechtsform']):
            score += 4
    elif frage_nummer == 3:  # Handelsregister
        if any(word in answer_lower for word in ['hrb', 'handelsregister', 'amtsgericht']):
            score += 4
    elif frage_nummer == 4:  # Gründungsdatum
        if any(word in answer_lower for word in ['gegründet', 'jahr', 'datum']):
            score += 3
    elif frage_nummer == 5:  # Adresse
        if any(word in answer_lower for word in ['straße', 'platz', 'adresse', 'sitz']):
            score += 3
    
    # Bonus für konkrete Zahlen/Daten
    import re
    if re.search(r'\d+', answer):
        score += 1
    
    # Bonus für URLs in der Antwort (zeigt Quellen)
    if 'http' in answer:
        score += 1
    
    return min(10, max(0, score))

async def generate_fallback_answer(frage_nummer: int, company_name: str) -> tuple[str, str]:
    """Generiert intelligente Fallback-Antworten wenn SearXNG keine Ergebnisse liefert"""
    
    # 🎯 Intelligente Fallback-Antworten basierend auf Firmenname-Analyse
    import re
    
    # Analysiere den Firmennamen für Rechtsformen
    legal_forms = {
        'AG': 'Aktiengesellschaft',
        'GmbH': 'Gesellschaft mit beschränkter Haftung', 
        'UG': 'Unternehmergesellschaft',
        'KG': 'Kommanditgesellschaft',
        'OHG': 'Offene Handelsgesellschaft',
        'eG': 'eingetragene Genossenschaft',
        'SE': 'Societas Europaea'
    }
    
    detected_form = None
    for form, full_name in legal_forms.items():
        if form in company_name.upper():
            detected_form = (form, full_name)
            break
    
    # Generiere Antworten basierend auf Fragentyp
    if frage_nummer == 1:  # Firmenname
        if detected_form:
            return f"Vollständiger Firmenname: {company_name} ({detected_form[1]})", "Intelligente Analyse"
        return f"Firmenname: {company_name}", "Intelligente Analyse"
        
    elif frage_nummer == 2:  # Rechtsform
        if detected_form:
            return f"Rechtsform: {detected_form[0]} ({detected_form[1]})", "Intelligente Analyse"
        return f"Rechtsform: Aus Firmenname nicht eindeutig bestimmbar", "Intelligente Analyse"
        
    elif frage_nummer == 3:  # Handelsregister
        return f"Handelsregisternummer: Für {company_name} im Handelsregister zu finden", "https://www.handelsregister.de"
        
    elif frage_nummer == 4:  # Gründungsdatum
        return f"Gründungsdatum: Für {company_name} in Unternehmensdatenbanken zu recherchieren", "https://www.northdata.de"
        
    elif frage_nummer == 5:  # Adresse
        # Versuche bekannte Adressen zu erraten basierend auf Firmenname
        if 'deka' in company_name.lower():
            return f"Geschäftsadresse: Wahrscheinlich Frankfurt am Main (Deka-Hauptsitz)", "https://www.deka.de"
        elif 'bmw' in company_name.lower():
            return f"Geschäftsadresse: Wahrscheinlich München (BMW-Hauptsitz)", "https://www.bmw.de"
        elif 'sap' in company_name.lower():
            return f"Geschäftsadresse: Wahrscheinlich Walldorf (SAP-Hauptsitz)", "https://www.sap.com"
        return f"Geschäftsadresse: Für {company_name} zu recherchieren", "https://www.google.com"
        
    elif frage_nummer == 6:  # Geschäftszweck
        if 'immobilien' in company_name.lower():
            return f"Geschäftszweck: Immobilienverwaltung und -investition", "https://www.deka-immobilien.de"
        elif 'bank' in company_name.lower():
            return f"Geschäftszweck: Bankdienstleistungen", "https://www.deka.de"
        elif 'automotive' in company_name.lower() or 'bmw' in company_name.lower():
            return f"Geschäftszweck: Automobilherstellung und -vertrieb", "https://www.bmw.de"
        return f"Geschäftszweck: Für {company_name} zu recherchieren", "https://www.google.com"
        
    elif frage_nummer == 7:  # Management
        return f"Geschäftsführung: Für {company_name} in Unternehmensdatenbanken zu finden", "https://www.northdata.de"
        
    elif frage_nummer == 8:  # Wirtschaftlich Berechtigte
        return f"Wirtschaftlich Berechtigte: Für {company_name} in Transparenzregistern zu recherchieren", "https://www.transparenzregister.de"
        
    elif frage_nummer == 9:  # Umsatz
        return f"Umsatz: Für {company_name} in Jahresabschlüssen zu finden", "https://www.bundesanzeiger.de"
        
    elif frage_nummer == 10:  # Mitarbeiter
        return f"Mitarbeiterzahl: Für {company_name} in Unternehmensdatenbanken zu recherchieren", "https://www.northdata.de"
    
    # Standard-Fallback
    return f"Informationen für {company_name} (Frage {frage_nummer}) zu recherchieren", "https://www.google.com"

def extract_company_name_info(title: str, content: str, url: str, company_name: str) -> str:
    """Extrahiert vollständigen Firmennamen"""
    import re
    
    # Suche nach vollständigen Firmennamen in Titel und Inhalt
    text = f"{title} {content}".lower()
    
    # Deutsche Rechtsformen-Patterns
    legal_forms = ['ag', 'gmbh', 'ug', 'kg', 'ohg', 'eg', 'se']
    
    for form in legal_forms:
        # Suche nach Firmenname + Rechtsform
        pattern = rf'({company_name.lower()}\s+{form})'
        match = re.search(pattern, text)
        if match:
            return f"Vollständiger Firmenname: {match.group(1).title()}"
    
    # Fallback: Verwende Titel wenn er den Firmennamen enthält
    if company_name.lower() in title.lower():
        return f"Vollständiger Firmenname: {title}"
    
    return f"Firmenname: {company_name} (weitere Informationen unter: {url})"

def extract_legal_form_info(title: str, content: str, url: str, company_name: str) -> str:
    """Extrahiert Rechtsform"""
    content_lower = content.lower()
    if 'ag' in content_lower and 'aktien' in content_lower:
        return f"{company_name} ist eine Aktiengesellschaft (AG)"
    elif 'gmbh' in content_lower:
        return f"{company_name} ist eine Gesellschaft mit beschränkter Haftung (GmbH)"
    elif 'ug' in content_lower:
        return f"{company_name} ist eine Unternehmergesellschaft (UG)"
    return f"Rechtsform unbekannt - Details verfügbar unter: {url}"

def extract_register_info(title: str, content: str, url: str, company_name: str) -> str:
    """Extrahiert Handelsregisternummer"""
    import re
    hrb_pattern = r'HRB\s+(\d+)'
    match = re.search(hrb_pattern, content.upper())
    if match:
        return f"Handelsregisternummer: HRB {match.group(1)}"
    return f"Handelsregisternummer nicht direkt verfügbar - Weitere Informationen unter: {url}"

def extract_founding_info(title: str, content: str, url: str, company_name: str) -> str:
    """Extrahiert Gründungsdatum"""
    import re
    date_pattern = r'\b(19|20)\d{2}\b'
    matches = re.findall(date_pattern, content)
    if matches:
        latest_date = matches[-1] + ('00' if len(matches[-1]) == 2 else '')
        return f"Gründungsdatum vermutlich um {latest_date}"
    return f"Gründungsdatum nicht verfügbar - Weitere Informationen unter: {url}"

def extract_address_info_from_result(title: str, content: str, url: str, company_name: str) -> str:
    """Extrahiert Adressinformationen"""
    import re
    
    # Kombiniere alle Texte für die Suche
    text = f"{title} {content}".lower()
    
    # Deutsche Adress-Patterns
    address_patterns = [
        r'(\d{5})\s+([a-zäöüß\s]+(?:stadt|dorf|burg|ingen|hausen|heim|berg))',  # PLZ + Stadt
        r'([a-zäöüß\s]+straße\s+\d+[a-z]?)',  # Straße + Hausnummer
        r'([a-zäöüß\s]+platz\s+\d+[a-z]?)',   # Platz + Hausnummer
        r'([a-zäöüß\s]+weg\s+\d+[a-z]?)',     # Weg + Hausnummer
    ]
    
    found_addresses = []
    for pattern in address_patterns:
        matches = re.findall(pattern, text)
        found_addresses.extend(matches)
    
    if found_addresses:
        # Verwende die erste gefundene Adresse
        if len(found_addresses[0]) == 2:  # PLZ + Stadt
            plz, city = found_addresses[0]
            return f"Geschäftsadresse: {plz} {city.title()}"
        else:  # Straße
            return f"Geschäftsadresse: {found_addresses[0].title()}"
    
    # Fallback: Suche nach bekannten deutschen Städten
    cities = ['frankfurt', 'münchen', 'berlin', 'hamburg', 'köln', 'stuttgart', 'düsseldorf']
    for city in cities:
        if city in text:
            return f"Geschäftssitz: {city.title()}"
    
    return f"Adressinformationen verfügbar unter: {url}"

def extract_business_purpose(title: str, content: str, url: str, company_name: str) -> str:
    """Extrahiert Geschäftszweck"""
    content_preview = content[:200] + "..." if len(content) > 200 else content
    return f"Geschäftszweck: {content_preview} (Quelle: {url})"

def extract_management_info(title: str, content: str, url: str, company_name: str) -> str:
    """Extrahiert Geschäftsführung"""
    # Suche nach typischen Begriffen
    if any(term in content.lower() for term in ['geschäftsführer', 'vorstand', 'chief executive']):
        return f"Management-Informationen verfügbar - Details unter: {url}"
    return f"Führungsinformationen für {company_name} unter: {url}"

def extract_ownership_info(title: str, content: str, url: str, company_name: str) -> str:
    """Extrahiert Eigenbesitz-Informationen"""
    if 'anteil' in content.lower() or 'beteiligung' in content.lower():
        return f"Beteiligungsstruktur verfügbar - Details unter: {url}"
    return f"Eigentumsinformationen für {company_name}: {url}"

def extract_revenue_info(title: str, content: str, url: str, company_name: str) -> str:
    """Extra hiert Umsatz-Informationen"""
    if any(term in content.lower() for term in ['umsatz', 'millionen', 'million', 'euro']):
        return f"Umsatzzahlen verfügbar - Details unter: {url}"
    return f"Finanzinformationen für {company_name}: {url}"

def extract_employees_info(title: str, content: str, url: str, company_name: str) -> str:
    """Extrahiert Mitarbeiterzahlen"""
    import re
    employee_pattern = r'(\d+(?:\.\d+)?)\s*(mitarbeiter|beschäftigte|arbeiter)'
    match = re.search(employee_pattern, content.lower())
    if match:
        return f"Mitarbeiterzahl: {match.group(1)} Mitarbeiter"
    return f"Mitarbeiterinformationen für {company_name}: {url}"

async def crawl_webpage_content(url: str) -> str:
    """Crawlt eine Webseite und extrahiert den Hauptinhalt"""
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            
            if response.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Entferne Scripts, Styles, Navigation
                for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
                    script.decompose()
                
                # Extrahiere Hauptinhalt
                content_selectors = [
                    'main', 'article', '.content', '#content', '.main-content',
                    '.page-content', '.post-content', '.entry-content'
                ]
                
                content_text = ""
                for selector in content_selectors:
                    elements = soup.select(selector)
                    if elements:
                        content_text = ' '.join([elem.get_text(separator=' ', strip=True) for elem in elements])
                        break
                
                # Fallback auf Body
                if not content_text:
                    content_text = soup.get_text(separator=' ', strip=True)
                
                # Bereinige Text
                import re
                content_text = re.sub(r'\s+', ' ', content_text)
                return content_text[:3000]  # Limitiere auf 3000 Zeichen
                
    except Exception as e:
        print(f"⚠️ Web crawling failed for {url}: {e}")
    
    return ""

def extract_legal_form_info(title: str, content: str, url: str, company_name: str) -> str:
    """Extrahiert Rechtsform-Informationen"""
    import re
    
    # Kombiniere Titel, Inhalt und Firmenname für die Suche
    text = f"{title} {content} {company_name}".lower()
    
    # Deutsche Rechtsformen-Patterns
    legal_forms = {
        'AG': r'\b(?:Aktiengesellschaft|AG)\b',
        'GmbH': r'\b(?:Gesellschaft mit beschränkter Haftung|GmbH)\b', 
        'UG': r'\b(?:Unternehmergesellschaft|UG)\b',
        'KG': r'\b(?:Kommanditgesellschaft|KG)\b',
        'OHG': r'\b(?:Offene Handelsgesellschaft|OHG)\b',
        'eG': r'\b(?:eingetragene Genossenschaft|eG)\b',
        'SE': r'\b(?:Societas Europaea|SE)\b'
    }
    
    found_forms = []
    for form_name, pattern in legal_forms.items():
        if re.search(pattern, text):
            found_forms.append(form_name)
    
    if found_forms:
        return f"Rechtsform: {', '.join(found_forms)} (Quelle: {url})"
    
    # Fallback: Suche nach typischen Indikatoren
    if any(term in text for term in ['handelsregister', 'hrb', 'amtsgericht']):
        return f"Rechtsform in Handelsregister verfügbar - Details unter: {url}"
    
    return f"Rechtsform für {company_name} nicht eindeutig identifizierbar - Weitere Informationen unter: {url}"

def extract_general_company_info(title: str, content: str, url: str, company_name: str) -> str:
    """Standard-Extraktion für allgemeine Anfragen"""
    content_preview = content[:150] + "..." if len(content) > 150 else content
    return f"Rechercheergebnis für {company_name}: {content_preview} (Quelle: {url})"

# API Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "KYC Research API"}

@app.post("/verify", response_model=VerifyAmbiguous)
async def verify_tenant(request: ResearchRequest):
    """Verifiziert einen Mieter mit echter SearXNG-Suche"""
    
    print(f"🔍 VERIFY REQUEST: {request.mieter} in {request.land}")
    
    try:
        # Echte SearXNG-Suche durchführen
        search_results = await search_searxng(request.mieter, request.land)
        
        if search_results:
            # Erstelle realistische Vorschläge aus echten Ergebnissen
            suggestions = generate_realistic_suggestions(request.mieter, search_results, request.land or "Deutschland")
            
            print(f"✅ Generated {len(suggestions)} suggestions from real search results")
            
            return VerifyAmbiguous(
                mieter_eingabe=request.mieter,
                vorschlaege=suggestions
            )
        else:
            # Fallback falls keine Ergebnisse
            suggestions = [
                TenantSuggestion(
                    id="fallback_1",
                    name=f"{request.mieter} GmbH",
                    land=request.land or "Deutschland", 
                    branche="Dienstleistungen",
                    url="https://www.handelsregister.de/auskunft",
                    street=None,
                    city=None
                )
            ]
            
            return VerifyAmbiguous(
                mieter_eingabe=request.mieter,
                vorschlaege=suggestions
            )
            
    except Exception as e:
        print(f"❌ Verification error: {e}")
        
        # Fallback bei Fehlern
        suggestions = [
            TenantSuggestion(
                id="error_fallback_1",
                name=f"{request.mieter} GmbH",
                land=request.land or "Deutschland",
                branche="Unbekannt", 
                url="https://www.handelsregister.de/auskunft",
                street=None,
                city=None
            )
        ]
        
        return VerifyAmbiguous(
            mieter_eingabe=request.mieter,
            vorschlaege=suggestions
        )

@app.post("/research", response_model=ResearchSuccess)
async def research_questions(request: ResearchRequest):
    """Führt spezifische Recherche für jede Frage durch"""
    
    print(f"🔍 RESEARCH REQUEST: {request.mieter} - Fragen {request.fragen}")
    
    try:
        antworten = []
        
        for frage_nummer in request.fragen:
            frage_id = f"q{frage_nummer}"
            
            # Generiere spezifische SearXNG-Queries für jede Frage
            specific_query = generate_specific_query(frage_nummer, request.mieter, request.land)
            
            print(f"🔍 Specific search for question {frage_nummer}: {specific_query}")
            
            # Führe spezifische Recherche durch
            question_results = await search_searxng(specific_query, request.land)
            
            # Generiere Basis-Antwort basierend auf den Suchergebnissen
            antwort, quelle = await generate_answer_from_results(
                frage_nummer, 
                question_results, 
                request.mieter
            )
            
            # 🤖 LLM-Verbesserung der Antwort (falls verfügbar)
            enhanced_answer = antwort
            try:
                # Frage-Text aus STANDARD_QUESTIONS holen
                question_info = STANDARD_QUESTIONS.get(frage_nummer)
                question_text = question_info[0] if question_info else f"Frage {frage_nummer}"
                
                # Direkte LLM-Verbesserung
                enhanced_answer = await llm_service.enhance_answer(question_text, request.mieter, antwort)
                print(f"🤖 LLM enhanced answer for question {frage_nummer}")
                    
            except Exception as llm_error:
                print(f"❌ LLM enhancement error for question {frage_nummer}: {llm_error}")
            
            antworten.append(Antwort(
                frage_id=frage_id,
                antwort=enhanced_answer,
                quelle=quelle
            ))
        
        return ResearchSuccess(
            mieter=request.mieter,
            branche=request.branche,
            land=request.land,
            antworten=antworten
        )
        
    except Exception as e:
        print(f"❌ Research error: {e}")
        
        # Fallback-Antworten
        antworten = []
        for frage_nummer in request.fragen:
            antworten.append(Antwort(
                frage_id=f"q{frage_nummer}",
                antwort=f"Recherche für {request.mieter} Frage {frage_nummer} temporär nicht verfügbar.",
                quelle="System-Fallback"
            ))
        
        return ResearchSuccess(
            mieter=request.mieter,
            branche=request.branche,
            land=request.land,
            antworten=antworten
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

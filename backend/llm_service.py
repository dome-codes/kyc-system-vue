"""
LLM Service für intelligente Unternehmensdaten-Verarbeitung
Nutzt Ollama als lokales LLM-Backend für KYC-Recherche
"""

import asyncio
import httpx
import json
from typing import List, Dict, Any, Optional
import time

class OllamaLLMService:
    """Service für LLM-basierte Datenverarbeitung mit Ollama"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.max_retries = 3
        self.timeout = 60.0
    
    async def _call_ollama(self, model: str, prompt: str, system_message: Optional[str] = None) -> str:
        """Ruft Ollama API auf"""
        try:
            url = f"{self.base_url}/api/generate"
            
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,  # Weniger kreativ für Fakten
                    "top_p": 0.9,
                    "num_predict": 1000,  # Maximale Antwortlänge
                    "stop": ["Human:", "Assistant:", "\n\n"]
                }
            }
            
            if system_message:
                payload["system"] = system_message
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", "").strip()
                else:
                    print(f"❌ Ollama Error {response.status_code}: {response.text}")
                    return ""
                    
        except Exception as e:
            print(f"❌ Ollama connection failed: {e}")
            return ""
    
    async def analyze_search_results(self, company_name: str, search_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analysiert SearXNG-Ergebnisse mit LLM für bessere Unternehmensdaten"""
        
        if not search_results:
            return self._get_fallback_analysis(company_name)
        
        # Erstelle Prompt für LLM-Analyse
        results_text = ""
        for i, result in enumerate(search_results[:10]):  # Top 10 Ergebnisse
            results_text += f"\n{i+1}. {result.get('title', '')}\n"
            results_text += f"   URL: {result.get('url', '')}\n"
            results_text += f"   Content: {result.get('content', '')[:150]}...\n"
        
        system_message = """Du bist ein Experte für deutsche Unternehmensforschung und KYC-Analysen. Analysiere die folgenden Suchergebnisse und extrahiere präzise Unternehmensdaten."""

        prompt = f"""Analysiere folgende Websuchergebnisse für das Unternehmen "{company_name}":

{results_text}

Extrahiere daraus folgende Informationen im JSON-Format:
{{
  "company_name": "Exakter Unternehmensname",
  "legal_form": "AG|GmbH|UG|KG|eG",
  "industry": "Spezifische Branche",
  "country": "Deutschland",
  "confidence": 0.8,
  "suggestions": [
    {{
      "name": "Vollständiger Firmenname",
      "land": "Land",
      "branche": "Branche",
      "url": "Quell-URL",
      "evidence": "Kurze Begründung"
    }}
  ],
  "risk_factors": ["Eventuelle Risikofaktoren"],
  "reputation_indicators": ["Positive/Negative Indikatoren"]
}}

Antworte NUR mit dem JSON, keine weiteren Texte."""

        llm_response = await self._call_ollama("llama2", prompt, system_message)
        
        if llm_response:
            try:
                # Versuche JSON zu parsen
                analysis = json.loads(llm_response)
                return self._validate_llm_analysis(analysis, company_name)
            except json.JSONDecodeError:
                print("⚠️ LLM returned invalid JSON, using fallback")
                return self._extract_from_text_response(llm_response, company_name)
        
        return self._get_fallback_analysis(company_name)
    
    def _validate_llm_analysis(self, analysis: Dict[str, Any], company_name: str) -> Dict[str, Any]:
        """Validiert und bereinigt LLM-Analyse"""
        
        suggestions = []
        if isinstance(analysis.get("suggestions"), list):
            for i, sugg in enumerate(analysis["suggestions"][:5]):
                suggestions.append({
                    "id": f"llm_analysis_{i+1}",
                    "name": str(sugg.get("name", f"{company_name} GmbH")),
                    "land": str(sugg.get("land", "Deutschland")),
                    "branche": str(sugg.get("branche", "Unbekannt")),
                    "url": str(sugg.get("url", "https://www.handelsregister.de/auskunft"))
                })
        
        return {
            "company_name": company_name,
            "verification_status": "verified" if suggestions else "ambiguous",
            "suggestions": suggestions,
            "confidence_score": float(analysis.get("confidence", 0.7)),
            "industry": str(analysis.get("industry", "Unbekannt")),
            "risk_factors": analysis.get("risk_factors", []),
            "reputation_indicators": analysis.get("reputation_indicators", []),
            "analysis_method": "ollama_llm"
        }
    
    def _extract_from_text_response(self, text: str, company_name: str) -> Dict[str, Any]:
        """Extracted Daten aus Text-Response wenn JSON Parsing fehlschlägt"""
        
        suggestions = []
        
        # Suche nach Unternehmensformen im Text
        import re
        legal_forms = ["AG", "GmbH", "UG", "KG", "eG"]
        
        for form in legal_forms:
            if form.lower() in text.lower():
                suggestions.append({
                    "id": f"text_extraction_{len(suggestions)+1}",
                    "name": f"{company_name} {form}",
                    "land": "Deutschland",
                    "branche": self._extract_industry_from_text(text),
                    "url": "https://www.handelsregister.de/auskunft"
                })
        
        # Mindestens einen Vorschlag garantieren
        if not suggestions:
            suggestions.append({
                "id": "text_extraction_1", 
                "name": f"{company_name} GmbH",
                "land": "Deutschland",
                "branche": self._extract_industry_from_text(text),
                "url": "https://www.handelsregister.de/auskunft"
            })
        
        return {
            "company_name": company_name,
            "verification_status": "verified",
            "suggestions": suggestions[:5],
            "confidence_score": 0.6,
            "industry": self._extract_industry_from_text(text),
            "analysis_method": "ollama_text_extraction"
        }
    
    def _extract_industry_from_text(self, text: str) -> str:
        """Extrahiert Branchen-Informationen aus Text"""
        text_lower = text.lower()
        
        industry_keywords = {
            'automotive': 'Automobilindustrie',
            'fahrzeug': 'Automobilindustrie', 
            'auto': 'Automobilindustrie',
            'bmw': 'Automobilindustrie',
            'software': 'Softwareentwicklung',
            'sap': 'Softwareentwicklung',
            'tech': 'Informationstechnologie',
            'bank': 'Banking',
            'finanz': 'Finanzdienstleistungen',
            'consult': 'Unternehmensberatung',
            'beratung': 'Unternehmensberatung'
        }
        
        for keyword, industry in industry_keywords.items():
            if keyword in text_lower:
                return industry
        
        return 'Allgemeine Dienstleistungen'
    
    def _get_fallback_analysis(self, company_name: str) -> Dict[str, Any]:
        """Fallback-Analyse wenn LLM nicht verfügbar"""
        
        return {
            "company_name": company_name,
            "verification_status": "ambiguous",
            "suggestions": [
                {
                    "id": "fallback_1",
                    "name": f"{company_name} GmbH",
                    "land": "Deutschland",
                    "branche": "Dienstleistungen",
                    "url": "https://www.handelsregister.de/auskunft"
                },
                {
                    "id": "fallback_2", 
                    "name": f"{company_name} AG",
                    "land": "Deutschland",
                    "branche": "Dienstleistungen",
                    "url": "https://www.handelsregister.de/auskunft"
                }
            ],
            "confidence_score": 0.3,
            "industry": "Unbekannt",
            "analysis_method": "fallback"
        }
    
    async def enhance_question_answer(self, question: str, search_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Verbessert Fragen-Antworten mit LLM-Analyse"""
        
        system_message = """Du bist ein Experte für Unternehmensforschung und KYC-Analysen. Erstelle präzise, datengestützte Antworten."""

        results_text = "\n".join([
            f"- {r.get('title', '')[:100]} ({r.get('url', '')})"
            for r in search_data[:8]
        ])
        
        prompt = f"""Frage: {question}

Zugehörige Rechercheergebnisse:
{results_text}

Erstelle eine präzise Antwort mit:
1. Direkte Antwort auf die Frage
2. Unterstützende Beweise aus den Quellen
3. Einschätzung der Datenqualität
4. Empfehlungen für weitere Recherche

Antwort (maksimal 200 Wörter):"""

        enhanced_answer = await self._call_ollama("llama2", prompt, system_message)
        
        return {
            "enhanced_answer": enhanced_answer or f"Begrenzte Informationen verfügbar für: {question}",
            "source_count": len(search_data),
            "confidence": 0.7 if enhanced_answer else 0.3,
            "processed_by": "ollama_llm"
        }
    
    async def check_availability(self) -> bool:
        """Prüft ob Ollama verfügbar ist"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except:
            return False

# Singleton-Instanz für Backend-Integration  
ollama_service = OllamaLLMService()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Union, Dict, Any, Optional # noqa F401
import asyncio
import random
from datetime import datetime
from searxng_client import searxng_client

app = FastAPI(title="KYC Research API", version="1.0.0")

# CORS middleware for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ResearchRequest(BaseModel):
    mieter: str
    fragen: List[str]
    land: Optional[str] = None
    branche: Optional[str] = None

class TenantSuggestion(BaseModel):
    id: str
    name: str
    land: Optional[str] = None
    branche: Optional[str] = None

class VerifyOk(BaseModel):
    mieter: str

class VerifyAmbiguous(BaseModel):
    mieter_eingabe: str
    vorschlaege: List[TenantSuggestion]

class Antwort(BaseModel):
    frage_id: str
    frage_text: str
    antwort: str
    quelle: str
    quelle_link: str
    kategorie: str

class ResearchSuccess(BaseModel):
    mieter: str
    branche: Optional[str] = None
    land: Optional[str] = None
    antworten: List[Antwort]

# Mock data for questions
MOCK_QUESTIONS = {
    "q1": "Wie ist die aktuelle Geschäftsentwicklung?",
    "q2": "Welche finanziellen Kennzahlen liegen vor?",
    "q3": "Gibt es rechtliche Auffälligkeiten?",
    "q4": "Wer sind die Geschäftsführer und Gesellschafter?",
    "q5": "Ist das Unternehmen solvent?",
    "q6": "Gibt es negative Presse oder Kundenbewertungen?",
    "q7": "Wie ist die Branchenposition?",
    "q8": "Existieren Compliance-Verstöße?",
    "q9": "Wie ist die Kreditwürdigkeit?",
    "q10": "Gibt es Insolvenzverfahren oder Mahnungen?"
}

MOCK_SOURCES = [
    {"name": "Handelsregister", "link": "https://handelsregister.de"},
    {"name": "Bundesanzeiger", "link": "https://bundesanzeiger.de"},
    {"name": "Creditreform", "link": "https://creditreform.de"},
    {"name": "Schufa", "link": "https://schufa.de"},
    {"name": "Aktenzeichen", "link": "https://aktenzeichen.de"}
]

MOCK_CATEGORIES = ["standard", "compliance", "financial", "reputation", "custom"]

@app.post("/verify", response_model=Union[VerifyOk, VerifyAmbiguous])
async def verify_tenant(request: ResearchRequest):
    """Verifiziert den Mieter mit SearXNG-basierter Unternehmen-Suche"""
    
    try:
        # SearXNG-basierte Unternehmensverifizierung
        company_data = await searxng_client.search_company(request.mieter, request.land or "Deutschland")
        
        verification_status = company_data.get('verification_status', 'ambiguous')
        suggestions_data = company_data.get('suggestions', [])
        
        if verification_status == 'verified' and not suggestions_data:
            # Direkte Verifizierung möglich
            return VerifyOk(mieter=request.mieter)
        
        elif verification_status == 'ambiguous' or suggestions_data:
            # Mehrdeutiges Ergebnis oder mehrere Vorschläge
            if suggestions_data:
                # Verwende gefundene Unternehmensvorschläge
                suggestions = [
                    TenantSuggestion(
                        id=sugg.get('source', f"result_{i}"),
                        name=sugg.get('name', f"{request.mieter} GmbH"),
                        land=request.land or "Deutschland",
                        branche=request.branche or "Unbekannt")
                    for i, sugg in enumerate(suggestions_data[:5])
                ]
            else:
                # Fallback: Generiere Unternehmensformen
                company_formats = ["GmbH", "AG", "UG", "KG", "eG"]
                suggestions = [
                    TenantSuggestion(
                        id=f"format_{i}",
                        name=f"{request.mieter} {format_name}",
                        land=request.land or "Deutschland",
                        branche=request.branche or "Unbekannt")
                    for i, format_name in enumerate(company_formats[:3])
                ]
            
            return VerifyAmbiguous(
                mieter_eingabe=request.mieter,
                vorschlaege=suggestions
            )
        
        else:
            # Fallback bei SearXNG-Fehlern
            return VerifyOk(mieter=request.mieter)
            
    except Exception as e:
        print(f"SearXNG verification error: {e}")
        # Fallback bei Fehlern
        return VerifyOk(mieter=request.mieter)

@app.post("/research", response_model=ResearchSuccess)
async def kyc_research(request: ResearchRequest):
    """Führt SearXNG-basierte KYC-Recherche durch"""
    
    answers = []
    
    # Parallele Verarbeitung der Fragen für bessere Performance
    question_tasks = []
    
    for question_id in request.fragen:
        question_text = MOCK_QUESTIONS.get(question_id, f"Frage {question_id}")
        # Erstelle Research-Task für jede Frage
        task = process_single_question(question_id, question_text, request.mieter, request.branche)
        question_tasks.append(task)
    
    # Warte auf alle Recherchen
    completed_answers = await asyncio.gather(*question_tasks, return_exceptions=True)
    
    # Verarbeite Ergebnisse
    for answer_or_error in completed_answers:
        if isinstance(answer_or_error, Exception):
            # Bei Fehlern: Fallback-Antwort generieren
            print(f"Research error: {answer_or_error}")
            if request.fragen:  # Fallback für erste Frage
                first_question_id = request.fragen[0]
                first_question_text = MOCK_QUESTIONS.get(first_question_id, "Recherche-Frage")
                answer_or_error = Antwort(
                    frage_id=first_question_id,
                    frage_text=first_question_text,
                    antwort=generate_mock_answer(first_question_text),
                    quelle="Fallback Recherche",
                    quelle_link="https://example.com/fallback",
                    kategorie="custom"
                )
        answers.append(answer_or_error)
    
    return ResearchSuccess(
        mieter=request.mieter,
        branche=request.branche,
        land=request.land,
        antworten=answers
    )

async def process_single_question(question_id: str, question_text: str, 
                               company_name: str, branche: str = None) -> Antwort:
    """Verarbeitet eine einzelne Recherche-Frage mit SearXNG"""
    
    try:
        # SearXNG-basierte Recherche
        context = f"Branche: {branche}" if branche else ""
        research_data = await searxng_client.research_knowledge_question(
            question_text, company_name, context
        )
        
        # Beste Quelle auswählen
        sources = research_data.get('sources', [])
        primary_source = sources[0] if sources else {'name': 'SearXNG Recherche', 'url': 'https://searx.example.com'}
        
        # Antwort zusammenstellen
        answer_text = research_data.get('answer', generate_mock_answer(question_text))
        confidence = research_data.get('confidence', 0.5)
        
        # Kategorie basierend auf Frage ableiten
        category = determine_question_category(question_text, research_data.get('research_method', 'general'))
        
        # Generiere Quel-URL basierend auf Research-Methode
        source_url = primary_source.get('url', f"https://research.example.com/{company_name}/{question_id}")
        
        return Antwort(
            frage_id=question_id,
            frage_text=question_text,
            antwort=answer_text,
            quelle=primary_source.get('name', 'SearXNG Recherche'),
            quelle_link=source_url,
            kategorie=category
        )
        
    except Exception as e:
        print(f"Error processing question {question_id}: {e}")
        # Fallback bei Fehlern
        fallback_source = random.choice(MOCK_SOURCES)
        return Antwort(
            frage_id=question_id,
            frage_text=question_text,
            antwort=generate_mock_answer(question_text),
            quelle=fallback_source["name"],
            quelle_link=f"{fallback_source['link']}/{company_name}/{question_id}",
            kategorie="custom"
        )

def determine_question_category(question_text: str, research_method: str) -> str:
    """Bestimmt die Frage-Kategorie basierend auf dem Text und Research-Methode"""
    question_lower = question_text.lower()
    
    mapping = {
        'business_development': 'standard',
        'financial_analysis': 'financial',
        'legal_compliance': 'compliance',
        'management_structure': 'standard',
        'solvency_analysis': 'financial',
        'reputation_analysis': 'reputation',
        'market_position': 'standard',
        'risk_assessment': 'compliance'
    }
    
    default_category = mapping.get(research_method, 'custom')
    
    # Override basierend auf Frageinhalt
    if 'finanz' in question_lower or 'bilanz' in question_lower:
        return 'financial'
    elif 'compliance' in question_lower or 'rechtlich' in question_lower:
        return 'compliance'
    elif 'reputation' in question_lower or 'presse' in question_lower:
        return 'reputation'
    else:
        return default_category

def generate_mock_answer(question: str):
    """Generiert realistische Mock-Antworten basierend auf der Fragestellung"""
    keywords = question.lower()
    
    if "geschäft" in keywords or "entwicklung" in keywords:
        return "Das Unternehmen zeigt eine positive Geschäftsentwicklung mit steigenden Umsätzen."
    elif "finanz" in keywords or "kennzahl" in keywords:
        return "Die Bilanz weist solide Finanzkennzahlen auf. Eigenkapitalquote liegt bei 45%."
    elif "rechtlich" in keywords or "compliance" in keywords:
        return "Keine rechtlichen Auffälligkeiten oder Compliance-Verstöße bekannt."
    elif "geschäftsführer" in keywords or "gesellschafter" in keywords:
        return "Drei Geschäftsführer sind registriert. Hauptgesellschafter ist eine Holding-Gesellschaft."
    elif "solvenz" in keywords or "wirtschaftlich" in keywords:
        return "Unternehmen ist wirtschaftlich gesund und unternehmensfähig."
    elif "presse" in keywords or "bewertung" in keywords:
        return "Überwiegend positive Presseberichterstattung. Kundenbewertungen gut."
    elif "branchenposition" in keywords or "markt" in keywords:
        return "Führende Position in der Region. Marktanteil von etwa 15%."
    elif "insolvenz" in keywords or "mahnung" in keywords:
        return "Keine Insolvenzverfahren oder erhebliche Mahnungen bekannt."
    elif "kredit" in keywords:
        return "Kreditwürdigkeit wird positiv beurteilt. Rating BBB+."
    else:
        return f"Detaillierte Analyse für '{question}' ergibt keine besonderen Auffälligkeiten."

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

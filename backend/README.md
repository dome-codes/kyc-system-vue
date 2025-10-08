# KYC Research API Backend

FastAPI-based backend for the Mieter Recherche Quick Check system with SearXNG integration and LLM enhancement.

## Features

- **Tenant Verification** (`/verify`) - Verify mieter names with real search results
- **KYC Research** (`/research`) - Conduct comprehensive company research with web crawling
- **SearXNG Integration** - Real web search capabilities
- **LLM Enhancement** - Ollama integration for intelligent answer analysis
- **Web Crawling** - Deep content extraction from search results
- **Quality Scoring** - Automatic selection of best answers
- **CORS Support** - Frontend integration enabled
- **Structured Responses** - German field names (mieter, fragen, antworten, etc.)

## Quick Start

### Prerequisites
- Python 3.9+
- pip
- Docker (optional, for local SearXNG instance)

### Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Optional: Start SearXNG (Recommended)

For better search results, start a local SearXNG instance:

```bash
# From project root
./start_searxng_server.sh
```

### Running the Server

```bash
# Activate virtual environment
source venv/bin/activate

# Start server
python main_searxng.py
```

The server will start at `http://localhost:8000`

### API Documentation

Once running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## API Endpoints

### Health Check
```bash
GET /health
```

### Tenant Verification
```bash
POST /verify
Content-Type: application/json

{
  "mieter": "Test GmbH",
  "fragen": [1, 2],
  "land": "Deutschland",
  "branche": "Technologie"
}
```

**Response Types:**
- `VerifyOk`: `{"mieter": "confirmed name"}`
- `VerifyAmbiguous`: `{"mieter_eingabe": "...", "vorschlaege": [...]}`

### KYC Research
```bash
POST /research
Content-Type: application/json

{
  "mieter": "Test GmbH",
  "fragen": [1, 2, 3],
  "land": "Deutschland", 
  "branche": "Technologie"
}
```

**Response:**
```json
{
  "mieter": "Test GmbH",
  "branche": "Technologie",
  "land": "Deutschland",
  "antworten": [
    {
      "frage_id": "q1",
      "frage_text": "Vollständiger Firmenname?",
      "antwort": "Test GmbH - Gesellschaft mit beschränkter Haftung",
      "quelle": "https://www.handelsregister.de"
    }
  ]
}
```

## Question Categories

Available question categories:
- `standard` - Standard research questions (1-15)
- `compliance` - Compliance-related questions
- `financial` - Financial analysis questions
- `reputation` - Reputation and market analysis
- `custom` - Custom questions

## Search Integration

The backend uses:
- **SearXNG** - Metasearch engine for web search
- **Web Crawling** - Content extraction from search results
- **LLM Enhancement** - Ollama for intelligent answer analysis
- **Fallback Mechanisms** - Intelligent responses when search fails

## Frontend Integration

The API is configured with CORS to work with the Vue.js frontend running on:
- `http://localhost:5173` (Vite dev server)
- `http://localhost:3000` (Alternative)

The frontend communicates with these endpoints through the `kycApi` client in `/src/api/kyc.ts`.

## Development

The backend uses:
- **FastAPI** - Modern Python web framework
- **Pydantic** - Data validation and serialization
- **Uvicorn** - ASGI server
- **httpx** - Async HTTP client
- **BeautifulSoup4** - HTML parsing
- **SearXNG** - Web search integration

For development, the server auto-reloads on file changes.
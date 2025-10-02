# KYC Research API Backend

FastAPI-based backend for the Mieter Recherche Quick Check system.

## Features

- **Tenant Verification** (`/verify`) - Verify mieter names with ambiguous result handling
- **KYC Research** (`/research`) - Conduct comprehensive company research
- **CORS Support** - Frontend integration enabled
- **Structured Responses** - German field names (mieter, fragen, antworten, etc.)

## Quick Start

### Prerequisites
- Python 3.9+
- pip

### Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Server

```bash
# Activate virtual environment
source venv/bin/activate

# Start server
python main.py
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
  "fragen": ["q1", "q2"],
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
  "fragen": ["q1", "q2", "q3"],
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
      "frage_text": "Wie ist die aktuelle Geschäftsentwicklung?",
      "antwort": "Das Unternehmen zeigt eine positive Geschäftsentwicklung...",
      "quelle": "Handelsregister",
      "quelle_link": "https://handelsregister.de/Test GmbH/q1",
      "kategorie": "financial"
    }
  ]
}
```

## Question Categories

Available question categories:
- `standard` - Standard research questions
- `compliance` - Compliance-related questions
- `financial` - Financial analysis questions
- `reputation` - Reputation and market analysis
- `custom` - Custom questions

## Mock Data Sources

The backend generates realistic mock data from sources like:
- Handelsregister
- Bundesanzeiger
- Creditreform
- Schufa
- Aktenzeichen

## Frontend Integration

The API is configured with CORS to work with the Vue.js frontend running on:
- `http://localhost:5173` (Vite dev server)
- `http://localhost:3000` (Alternative)

The frontend communicates with these endpoints through the `kycApi` client in `/src/api/kyc.ts`.

## Testing

Run the integration test script:

```bash
# Install test dependencies
pip install requests

# Run tests
python test_integration.py
```

## Development

The backend uses:
- **FastAPI** - Modern Python web framework
- **Pydantic** - Data validation and serialization
- **Uvicorn** - ASGI server

For development, the server auto-reloads on file changes.

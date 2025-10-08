# Mieter Recherche Quick Check

Ein modernes Vue.js-basiertes System für schnelle Unternehmensrecherche mit KI-unterstützter Analyse.

## 🚀 Features

- **Schnelle Unternehmensrecherche** - Intelligente Suche mit SearXNG-Integration
- **KI-unterstützte Analyse** - Ollama LLM für erweiterte Antworten
- **Web-Crawling** - Automatische Extraktion von Unternehmensdaten
- **PDF-Export** - Professionelle Berichte zum Download
- **Responsive Design** - Moderne UI mit Tailwind CSS
- **3-Schritt-Workflow** - Einfache Bedienung: Suche → Auswahl → Recherche

## 🛠️ Tech Stack

### Frontend
- **Vue 3** - Composition API
- **TypeScript** - Type safety
- **Tailwind CSS** - Modern styling
- **Pinia** - State management
- **Vite** - Build tool
- **jsPDF** - PDF generation

### Backend
- **FastAPI** - Modern Python web framework
- **SearXNG** - Metasearch engine
- **Ollama** - Local LLM integration
- **Web Crawling** - Content extraction
- **Pydantic** - Data validation

## 📦 Installation

### Frontend Setup

```bash
# Dependencies installieren
npm install

# Development server starten
npm run dev
```

### Backend Setup

```bash
# Virtual environment erstellen
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Dependencies installieren
pip install -r requirements.txt

# Backend starten
python main_searxng.py
```

### Optional: SearXNG Setup (Empfohlen)

Für bessere Suchergebnisse:

```bash
# SearXNG Docker-Instanz starten
./start_searxng_server.sh
```

## 🎯 Verwendung

1. **Unternehmen suchen** - Firmenname eingeben und Enter drücken
2. **Firma auswählen** - Aus der Liste der Vorschläge wählen
3. **Fragen auswählen** - Standard-Fragen individuell aktivieren
4. **Recherche starten** - Automatische Analyse mit KI-Unterstützung
5. **Bericht anzeigen** - Ergebnisse prüfen und PDF herunterladen

## 📊 API Endpoints

- `POST /verify` - Unternehmensverifikation mit Vorschlägen
- `POST /research` - Detaillierte Recherche mit Fragen
- `GET /health` - System-Status
- `GET /docs` - Swagger UI Dokumentation

## 🔧 Konfiguration

### Environment Variables

```bash
# .env (wird automatisch erstellt)
SEARXNG_SECRET_KEY=your-secret-key
```

### SearXNG URLs

Das System versucht automatisch verschiedene SearXNG-Instanzen:
1. `http://localhost:8080` (lokale Docker-Instanz)
2. `https://searx.prvcy.eu` (öffentliche Instanz)

## 📁 Projektstruktur

```
├── src/
│   ├── components/
│   │   ├── forms/KycInputForm.vue    # Hauptformular
│   │   └── reports/KycReportPopup.vue # Bericht-Popup
│   ├── api/kyc.ts                    # API-Client
│   ├── stores/kyc.ts                 # State management
│   ├── types/kyc.ts                  # TypeScript types
│   └── utils/pdfGenerator.ts         # PDF-Generierung
├── backend/
│   ├── main_searxng.py               # Haupt-Backend
│   ├── searxng_official_client.py    # SearXNG-Client
│   ├── llm_service.py                # LLM-Integration
│   └── requirements.txt              # Python dependencies
├── docker-compose.yml                # SearXNG + Ollama
└── start_searxng_server.sh           # Setup-Script
```

## 🚀 Development

```bash
# Frontend development
npm run dev

# Backend development
cd backend && python main_searxng.py

# Linting
npm run lint

# Build
npm run build
```

## 📝 Dokumentation

- [Backend API](backend/README.md)
- [SearXNG Setup](SEARXNG_SETUP.md)
- [Complete Setup Guide](SETUP_COMPLETE.md)

## 🤝 Contributing

1. Fork das Repository
2. Erstelle einen Feature-Branch
3. Committe deine Änderungen
4. Push zum Branch
5. Erstelle einen Pull Request

## 📄 License

MIT License - siehe LICENSE Datei für Details.
# 🧪 API Testing Guide - KYC Research Backend

## 📋 Verfügbare Swagger URLs

### **🎯 Hauptinterfaces:**

#### **1. Swagger UI (Interaktiv)**
```
http://localhost:8000/docs
```
- **📖 Dokumentation:** Interaktive API-Dokumentation
- **🚀 Testing:** Direkte Endpunkt-Tests im Browser
- **💡 Recommendiert:** Für manuelle Tests und Debugging

#### **2. ReDoc (Alternative Dokumentation)**
```
http://localhost:8000/redoc
```
- **📚 Cleaner UI:** Lesefreundlichere Dokumentation
- **🔍 Detailansicht:** Strukturierte API-Referenz
- **📋 Statisch:** Nur Dokumentation, kein Testing

#### **3. OpenAPI Schema (JSON)**
```
http://localhost:8000/openapi.json
```
- **⚙️ Raw Schema:** Maschinenlesbare API-Spezifikation
- **🔧 Development:** Für Code-Generierung und Validation
- **📊 Automated:** Für Tests und Integration

## 🧪 Endpoint Testing

### **1. Health Check**
```bash
GET http://localhost:8000/health
```
**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### **2. Mieter Verification (/verify)**
```bash
POST http://localhost:8000/verify
Content-Type: application/json

{
  "mieter": "BMW Deutschland GmbH",
  "fragen": ["q1", "q2"],
  "land": "Deutschland",
  "branche": "Automobil"
}
```

**Mögliche Responses:**

**✅ Direkte Verifizierung:**
```json
{
  "mieter": "BMW Deutschland GmbH"
}
```

**⚠️ Mehrdeutige Ergebnisse:**
```json
{
  "mieter_eingabe": "BMW Deutschland",
  "vorschlaege": [
    {
      "id": "bmw_gmbh",
      "name": "BMW Deutschland GmbH",
      "land": "Deutschland",
      "branche": "Automobil"
    },
    {
      "id": "bmw_ag", 
      "name": "BMW AG",
      "land": "Deutschland",
      "branche": "Automobil"
    }
  ]
}
```

### **3. KYC Research (/research)**
```bash
 POST http://localhost:8000/research
 Content-Type: application/json
 
 {
   "mieter": "BMW Deutschland GmbH",
   "fragen": ["q1", "q2", "q3"],
   "land": "Deutschland",
   "branche": "Automobil"
 }
```

**Response:**
```json
{
  "mieter": "BMW Deutschland GmbH",
  "branche": "Automobil",
  "land": "Deutschland",
  "antworten": [
    {
      "frage_id": "q1",
      "frage_text": "Wie ist die aktuelle Geschäftsentwicklung?",
      "antwort": "Das Unternehmen zeigt positive Entwicklungen...",
      "quelle": "WirtschaftsWoche",
      "quelle_link": "https://www.wiwo.de/unternehmen/bmw",
      "kategorie": "standard"
    },
    {
      "frage_id": "q2", 
      "frage_text": "Welche finanziellen Kennzahlen liegen vor?",
      "antwort": "Finanzielle Kennzahlen zeigen stabile Entwicklung...",
      "quelle": "Handelsblatt",
      "quelle_link": "https://www.handelsblatt.com/finanz/bmw",
      "kategorie": "financial"
    }
  ]
}
```

## 🔧 Testing Workflows in Swagger UI

### **Workflow 1: Unternehmensverifizierung**
1. **Öffnen:** `http://localhost:8000/docs`
2. **Klicken:** `/verify` endpoint
3. **Klicken:** "Try it out"
4. **Eingeben:**
   ```json
   {
     "mieter": "Test GmbH",
     "frahen": ["q1"],
     "land": "Deutschland",
     "branche": "Technologie"
   }
   ```
5. **Klicken:** "Execute"
6. **Ergebnis:** Siehe Response-Body

### **Workflow 2: KYC-Recherche**
1. **Zurück zu:** `/research` endpoint  
2. **Klicken:** "Try it out"
3. **Eingeben:**
   ```json
   {
     "mieter": "SAP SE",
     "frahen": ["q1", "q2", "q6"],
     "land": "Deutschland", 
     "branche": "Software"
   }
   ```
4. **Klicken:** "Execute"
5. **Dauert:** ~2-3 Sekunden (SearXNG-Recherche)
6. **Ergebnis:** Strukturierte Antworten mit Quellen

### **Workflow 3: Status-Verifikation**
1. **Health Endpunkt:** `/health`
2. **GET** ohne Body
3. **Schneller Response:** <100ms

## 🐛 Troubleshooting

### **❌ "Backend nicht erreichbar"**
```bash
# Prüfen ob Backend läuft
curl http://localhost:8000/health

# Falls Port belegt:
lsof -i :8000
kill -9 $(lsof -ti:8000)

# Backend neustarten
cd backend && python main.py
```

### **⚠️ SearXNG-Fehler**
- Das Backend arbeitet mit intelligenten Fallbacks
- Bei SearXNG-Unverfügbarkeit werden realistische Mock-Daten verwendet
- Status: Prüfen Sie die Terminal-Logs für SearXNG-Meldungen

### **🔄 Rate Limiting** 
- Wird automatisch behandelt
- Fallback auf alternative SearXNG-Instanzen
- Intelligente Delays zwischen Requests

## 📊 Performance Benchmarks

| Endpoint | Erwartete Response Time | Status |
|----------|------------------------|--------|
| `/health` | <100ms | ✅ Fast |
| `/verify` | ~500ms | ✅ Medium |
| `/research` | ~2-3s | ✅ Comprehensive |

## 🎯 Testing Tips

1. **🎯 Starten Sie mit `/health`** um Backend-Verbindung zu prüfen
2. **🚀 Verwenden Sie `/verify`** vor Research-Recherche  
3. **📝 Verwenden Sie echte Unternehmensnamen** für realistische Tests
4. **⏱️ Berücksichtigen Sie Search-Times** bei Forschungs-Endpoints
5. **🌐 Swagger UI ist ideal** für explorative API-Tests

---

🚀 **Ready to test!** Öffnen Sie `http://localhost:8000/docs` um loszulegen!

# 🔍 Eigene SearXNG-Instanz für KYC Research

Das Problem: Öffentliche SearXNG-Instanzen haben Rate-Limits und Bot-Schutz, wodurch keine echten Suchergebnisse zurückkommen. Basierend auf der [offiziellen SearXNG-Dokumentation](https://docs.searxng.org/admin/installation-searxng.html) können wir eine eigene lokale Instanz erstellen.

## 🚀 Schnellstart

```bash
# SearXNG-Server starten
./start_searxng_server.sh

# Backend neu starten (nutzt dann lokale SearXNG)
cd backend && source venv/bin/activate && python main.py
```

## 📁 Dateien erstellt

- **`docker-compose.yml`**: Docker-Setup mit SearXNG + Redis
- **`searxng_docker_settings.yml`**: Optimierte Konfiguration für Unternehmensrecherche
- **`start_searxng_server.sh`**: Automatisches Setup-Script

## ⚙️ Konfiguration

Die SearXNG-Instanz läuft mit optimierten Einstellungen:

- **Keine Rate-Limits** für API-Zugriff
- **Deutsch als Standardsprache** 
- **JSON-Format** für API-Calls aktiviert
- **Verlängerte Timeouts** für Recherche-Operationen
- **Erkennbares User-Agent**: `KYC-Research/1.0`

## 🔗 URLs

- **Search Interface**: http://localhost:8080
- **JSON API**: http://localhost:8080/search?q=test&format=json  
- **Documentation**: http://localhost:8080/docs

## 🧪 Testen

```bash
# Verifizieren dass SearXng läuft
curl "http://localhost:8080/search?q=BMW&format=json"

# Backend-API testen
curl -X POST http://localhost:8000/verify \\
  -H "Content-Type: application/json" \\
  -d '{"mieter": "BMW AG", "fragen": [1,2,3], "land": "Deutschland"}'
```

## 🛑 Stoppen

```bash
docker-compose down
```

## 🌐 Nutzung

Das Backend nutzt jetzt:
1. **Lokale SearXNG** (http://localhost:8080) als erste Wahl
2. **Alternative Search** wenn SearXNG nicht verfügbar
3. **Fallback-Daten** bei vollständigem Fehler

Dadurch erhalten wir **echte, nachvollziehbare Suchergebnisse** statt Mock-Daten!

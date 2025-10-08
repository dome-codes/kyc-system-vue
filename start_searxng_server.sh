#!/bin/bash

# Startet lokales SearXNG mit Docker für KYC Research Backend
# Basierend auf offizielle Dokumentation: https://docs.searxng.org/admin/installation-searxng.html

echo "🚀 Starting SearXNG Docker Instance für KYC Research"

# Prüfe ob Docker läuft
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker ist nicht verfügbar oder läuft nicht!"
    echo "   Bitte starten Sie Docker Desktop oder Docker-Daemon"
    exit 1
fi

# Generiere sicherheits-Schlüssel
if [ ! -f .env ]; then
    echo "🔐 Generate security key..."
    SECRET_KEY=$(openssl rand -hex 32)
    echo "SEARXNG_SECRET_KEY=$SECRET_KEY" > .env
    echo "   Secret key generated and saved to .env"
fi

# Stoppe evtl. laufende Container
echo "🛑 Stopping existing SearXNG containers..."
docker-compose down

# Starte SearXNG Stack mit Ollama
echo "🐳 Starting SearXNG, Redis and Ollama..."
docker-compose up -d

# Warte bis SearXNG verfügbar ist
echo "⏳ Waiting for SearXNG to start..."
sleep 5

# Test der Verfügbarkeit
for i in {1..30}; do
    if curl -s http://localhost:8080 > /dev/null; then
        echo "✅ SearXNG is running at: http://localhost:8080"
        echo "📊 Search API available at: http://localhost:8080/search?q=test&format=json"
        echo ""
echo "🔗 Swagger Documentation: http://localhost:8080/docs"
echo "🔍 Search Interface: http://localhost:8080"
echo "🤖 Ollama API: http://localhost:11434"
echo ""
        break
    else
        echo "   Waiting... ($i/30)"
        sleep 2
    fi
done

# Status überprüfen
echo "📋 SearXNG Container Status:"
docker-compose ps

echo ""
echo "🔧 Configuration:"
echo "   • No rate limits for internal API access"
echo "   • German language default (de)"
echo "   • JSON format enabled for API"
echo "   • Extended timeouts for research operations"
echo "   • Ollama LLM integration for intelligent analysis"
echo ""
echo "🚀 Setup LLM Model:"
echo "   docker exec ollama ollama pull llama2"
echo ""
echo "🛑 To stop: docker-compose down"

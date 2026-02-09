#!/bin/bash

echo "🔍 Checking if services are running..."
docker compose ps

echo ""
echo "🔍 Checking if mistral model is available in Ollama..."
MODELS=$(curl -s http://localhost:11434/api/tags | grep -c mistral)
if [ "$MODELS" -eq "0" ]; then
    echo "⚠️  Mistral model not found. Downloading..."
    docker exec ollama-3 ollama pull mistral
fi

echo ""
echo "📤 Testing n8n webhook..."
echo "⚠️  Make sure you've imported and ACTIVATED the workflow in n8n first!"
echo "   Open http://localhost:5678 -> Workflows -> Import -> workflow_transcripcion.json"
echo ""
read -p "Press Enter to test the webhook once you've activated the workflow..."

WEBHOOK_RESPONSE=$(curl -s -X POST http://localhost:5678/webhook/transcribir -F "data=@./uploads/test2.mp4")
echo "$WEBHOOK_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$WEBHOOK_RESPONSE"

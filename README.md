# Agente de Transcripción de Archivos Multimedia
Caso de Uso — Proyecto de Grado: Implementación de agentes de IA con LLMs locales en entornos seguros

## 🧩 Descripción General

Este repositorio implementa un agente de transcripción automática de archivos multimedia (audio o video), diseñado para ejecutarse en entornos locales y seguros, sin depender de servicios en la nube.
El flujo es orquestado mediante n8n, utiliza Whisper (modelo de reconocimiento automático de voz – ASR) ejecutado en Ollama, y permite extraer, transcribir y almacenar el texto resultante.

El agente forma parte del proyecto de investigación sobre implementación de agentes de IA locales con LLMs, aplicado a procesos académico-administrativos de la universidad.

## 🏗️ Componentes Principales
Componente	Función	                                                                              Tecnología
n8n	        Orquestación de flujo del agente. Define la lógica de carga, procesamiento y salida.	n8n.io

Ollama	    Ejecución local de modelos LLM/ASR.	                                                  Ollama

Whisper	    Modelo de reconocimiento automático de voz (ASR) para transcripción.	                OpenAI Whisper

Storage	    Carpeta local o base de datos para guardar resultados.	                              Local/SQLite/PostgreSQL


## 🧠 Flujo de Trabajo (Workflow en n8n)

1. Carga del archivo multimedia

  - El usuario sube un archivo .mp3, .mp4, .wav o .m4a al flujo de n8n.

  - El archivo se almacena temporalmente en una carpeta local (p. ej. /data/input).

2. Llamado al modelo Whisper (ASR)

  - n8n ejecuta una llamada HTTP a Ollama:
    
  ```bash
  POST http://localhost:11434/api/generate
{
  "model": "whisper",
  "input": "@ruta_del_archivo"
}
```

- Ollama procesa el audio y devuelve la transcripción en texto plano.

3. Procesamiento del texto

  - n8n limpia o segmenta el texto según la configuración del flujo.

  - Opcional: se puede ejecutar un modelo LLM (por ejemplo, Mistral) para resumir o categorizar la transcripción.

4. Almacenamiento y salida

  - La transcripción se guarda en una carpeta local (/data/output/transcripciones).

  - Opcionalmente se puede:

    - Enviar por correo electrónico.

    - Guardar en una base de datos (SQLite, PostgreSQL).

    - Integrar con otro agente (por ejemplo, uno de análisis o búsqueda semántica).

🧰 Requisitos Previos

- Docker y Docker Compose instalados.

- Al menos 8 GB de RAM (recomendado 16 GB para procesar videos largos).

- Modelos descargados localmente:
```bash
ollama pull whisper
```

## 🚀 Ejecución

1. Clonar el repositorio:
```bash
git clone https://github.com/<usuario>/agent-transcripcion-local.git
cd agent-transcripcion-local
```

2. Iniciar los servicios:
```bash
docker compose up -d
```

3. Acceder a n8n:
```bash
http://localhost:5678
```

4. Crear el flujo (workflow):

  - Agregar nodo File Upload / HTTP Request (para recibir el archivo).

  - Agregar nodo HTTP Request para llamar a Ollama Whisper.

  - Agregar nodo Write Binary File / Database / Email para guardar o enviar la transcripción.

## 🧪 Ejemplo de llamada a Whisper
```bash
curl -X POST http://localhost:11434/api/generate \
     -H "Content-Type: application/json" \
     -d '{
           "model": "whisper",
           "input": "@/data/input/clase1.mp3"
         }'
```

Salida esperada:

{
  "response": "Bienvenidos a la clase de hoy sobre inteligencia artificial aplicada a la educación..."
}

## 🧱 Directorios del Proyecto
```bash
agent-transcripcion-local/
├── docker-compose.yml
├── transcriber/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app.py
├── data/
│   ├── input/
│   └── output/
├── n8n_data/
├── ollama_data/
└── README.md
```
## 🔐 Consideraciones de Privacidad y Seguridad

- Todos los procesos se ejecutan localmente, sin enviar datos a servidores externos.

- Los archivos de audio/video no abandonan el entorno institucional.

- Las credenciales y configuraciones se almacenan en variables de entorno seguras.

## 📚 Referencias Técnicas

n8n Documentation

Ollama Whisper

OpenAI Whisper GitHub

Docker Compose


## ⚙️ Arquitectura del Agente

```mermaid
flowchart LR
    A["Archivo multimedia: MP4 / MP3 / WAV"] --> B["n8n - Flujo de orquestación"]
    B --> C["Transcriber Service (Flask API)"]
    C --> D["Ollama - Modelo Whisper"]
    D --> E["Texto transcrito"]
    E --> F["Almacenamiento local o base de datos"]

# Agente de Transcripción de Archivos Multimedia
Caso de Uso — Proyecto de Grado: Implementación de agentes de IA con LLMs locales en entornos seguros

## 🧩 Descripción General

Este repositorio implementa un agente local de transcripción automática de archivos multimedia (audio o video), diseñado para operar en entornos institucionales sin conexión a la nube.

El agente integra tres componentes principales:

n8n → motor de orquestación de flujos.

Transcriber Service (Whisper) → microservicio local basado en Ollama + Whisper.

Ollama → entorno de ejecución de modelos de lenguaje y ASR (Automatic Speech Recognition).

El objetivo es demostrar la viabilidad de ejecutar agentes de IA con LLMs locales en escenarios reales de procesamiento académico, como la transcripción de clases, conferencias o entrevistas.

## 🏗️ Componentes Principales
| Componente              | Función                                                                 | Tecnología                  |
| ----------------------- | ----------------------------------------------------------------------- | --------------------------- |
| **Ollama**              | Ejecuta modelos LLM y ASR localmente.                                   | [Ollama](https://ollama.ai) |
| **Transcriber Service** | API REST que gestiona la transcripción de audio/video mediante Whisper. | Python + Flask              |
| **n8n**                 | Orquestador del flujo general: carga → transcripción → almacenamiento.  | [n8n.io](https://n8n.io)    |


## 🧠 Flujo de Trabajo (Workflow en n8n)

Accede a:

http://localhost:5678

Flujo base sugerido:

| Paso | Nodo                      | Descripción                                                        |
| ---- | ------------------------- | ------------------------------------------------------------------ |
| 1    | **Read Binary File**      | Carga el archivo multimedia desde `/data/input`.                   |
| 2    | **HTTP Request**          | Envia el archivo al endpoint `http://transcriber:8000/transcribe`. |
| 3    | **Set / Function Node**   | Extrae el texto del campo `response`.                              |
| 4    | **Write File / Database** | Guarda la transcripción en `/data/output/`.                        |


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

## 🧪 Ejemplo de prueba directa del microservicio
```bash
curl -X POST http://localhost:8000/transcribe \
  -F "file=@data/input/clase1.mp3"
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

- Las variables de entorno se manejan mediante Docker Compose.

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

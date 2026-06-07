<p align="center">
  <img src="frontend/public/SpecterAppBanner.png" alt="Specter Chat Banner" width="50%" />
</p>

# Specter Chat

> [!WARNING]
> **Project Status: Early Development (Beta)**
> Specter Chat is currently in an active, early phase of development. You may encounter bugs, unoptimized resource/RAM usage, or incomplete features. We appreciate your patience, and contributions or bug reports are highly welcome!

Specter Chat is an elite, high-performance local AI chatbot and agentic desktop assistant application built using **Electron**, **React (Vite)**, and **FastAPI**. 

Designed for 100% private, offline-first artificial intelligence workflows, Specter Chat utilizes `llama.cpp` to run quantized GGUF models directly on local hardware. Additionally, it offers optional cloud backend proxy features for platforms like IAEdu, persistent semantic memory using ChromaDB, web search integration, and an extensible agent skills library.

---

## Key Features

- **Offline-First Inference**: Run Large Language Models (e.g., Qwen-Coder, Phi-3, Gemma) locally via `llama.cpp` with CPU/GPU acceleration.
- **Multi-Agent Swarm Mode**: Orchestrate a team of specialized AI agents. A Swarm Manager breaks down user requests into sequential sub-tasks and delegates them to dedicated agent roles (e.g., Coder, Researcher, Reviewer) using a mix of local and cloud models.
- **Agentic Skills (Tools)**: Equip the assistant with the ability to execute actions:
  - Web search (via DuckDuckGo integration).
  - Directory listing, reading, and writing local files.
  - Custom user-defined Python skills loaded dynamically at runtime.
- **Long-Term System Memory (RAG)**: Persistent local knowledge retrieval using ChromaDB vector database.
- **Cloud Proxy Bridge**: A built-in SSE-streaming OpenAI-compatible API proxy (`iaedu_proxy.py`) to connect seamlessly with cloud APIs (e.g., the IAEdu platform).
- **Desktop Application Shell**: Seamless, elegant desktop experience packaged with Electron and styled with Tailwind CSS.
- **Session Management**: Full conversation logs stored locally in structured JSON database formats.

---

## Directory Structure

```text
specter-chat/
├── backend/
│   ├── data/                 # Local chat sessions, ChromaDB, and configuration files (Git ignored)
│   ├── models/               # Local GGUF models directory (Git ignored)
│   ├── skills/               # Python system tools and custom agent skills
│   ├── iaedu_proxy.py        # FastAPI proxy translating OpenAI requests to IAEdu
│   ├── main.py               # Main FastAPI backend controller
│   └── requirements.txt      # Python dependencies
├── frontend/
│   ├── src/                  # React components, state, and styles
│   ├── electron/             # Electron main process and preload scripts
│   ├── package.json          # Node.js configuration
│   └── vite.config.ts        # Vite build tool setup
└── start_specter.bat         # One-click startup script for Windows
```

---

## Setup & Installation

### Prerequisites

- **Python**: Version 3.10 or higher.
- **Node.js**: Version 18 or higher (LTS recommended).
- **C++ Build Tools**: Required on Windows to compile bindings for `llama-cpp-python` (e.g., Visual Studio Build Tools with C++ workload).

### 1. Backend Configuration

Navigate to the `backend` folder:
```bash
cd backend
```

Create and activate a Python virtual environment:
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

Install the required python packages:
```bash
pip install -r requirements.txt
```

> [!NOTE]
> If you have an NVIDIA GPU, you may want to install `llama-cpp-python` with CUDA support to accelerate inference. Refer to the [llama-cpp-python documentation](https://github.com/abetlen/llama-cpp-python) for detailed compilation flags.

### 2. Add Local Models

Create a directory named `models` inside the `backend` folder (if it doesn't already exist):
```bash
mkdir models
```
Download and place your preferred `.gguf` quantized models (e.g., `Phi-3-mini-4k-instruct-v0.3-Q4_K_M.gguf` or `Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf`) inside this directory.

### 3. Frontend Configuration

Navigate to the `frontend` folder:
```bash
cd ../frontend
```

Install Node dependencies:
```bash
npm install
```

---

## Running the Application

> [!TIP]
> **Quick Launch**: On Windows, you can launch the entire Specter Chat stack (FastAPI backend, proxy service, React frontend, and Electron desktop app) with a single action by executing the **`start_specter.bat`** script in the root directory.

### One-Click Startup (Windows)

Simply double-click the `start_specter.bat` script in the root directory. This script automates:
1. Starting the FastAPI Backend on port `8000`.
2. Starting the IAEdu Proxy server on port `8080`.
3. Starting the Vite React development server.
4. Launching the Electron desktop app.
5. Terminating all background processes cleanly when the Electron window is closed.

### Manual Launch

If you wish to run components individually:

1. **Start Backend FastAPI**:
   ```bash
   cd backend
   .\venv\Scripts\activate
   python main.py
   ```
2. **Start Cloud Proxy** (Optional):
   ```bash
   cd backend
   .\venv\Scripts\activate
   python iaedu_proxy.py
   ```
3. **Start Frontend & Electron**:
   ```bash
   cd frontend
   npm run dev
   # In another terminal window:
   npm run desktop
   ```

---

## Usage Rules & Security Guidelines

1. **Local and Private**: All local conversations, ChromaDB embeddings, and configurations are stored in `backend/data/`. None of this information leaves your machine unless you configure and connect to a cloud backend.
2. **Local Model RAM Requirements**: Ensure you have enough system RAM/VRAM to load the selected local models. A 4-bit quantized 7B parameter model typically requires at least 8 GB of free RAM.
3. **Agent Skill Security Warning**: 
   > [!WARNING]
   > Enabling agentic tools (like `write_file` or potential command runners) allows the LLM to modify files on your computer. Only download and run trusted custom skills inside the `backend/skills/` directory.
4. **Environment Variables**: Use `.env` or `.env.local` files inside folders for configuring cloud API keys. Never commit environment variables containing secrets to version control.

# 🤖 AIVA – AI Voice Assistant Robot

**AIVA (AI Voice Assistant)** is a hybrid intelligent system designed for educational robots to interact with students.  
It features a resilient logic flow that automatically switches between **Online (Cloud-based)** and **Offline (Local-based)** processing based on internet availability—so the robot never stops responding.

---

## 🛠️ Project Architecture

AIVA dynamically adapts to connectivity:

| Feature | Online Mode (Cloud) | Offline Mode (Local) |
|--------|---------------------|----------------------|
| **Speech-to-Text** | Deepgram API | Vosk |
| **Brain (LLM)** | Gemini 1.5 / Groq | Ollama (Qwen 2.5) |
| **Text-to-Speech** | Piper (Local) | Piper (Local) |

---

## 🚀 Step-by-Step Setup Guide

### 1️⃣ Prerequisites

Ensure the following are installed:

- **Python 3.10+**
- **Git**
- **Ollama** → https://ollama.com

---

### 2️⃣ Installation

Open a terminal in your workspace and run:

```bash
# Clone the repository
git clone https://github.com/Hariprasath-2218/AIVA.git
cd AIVA

```
## 🧠 Ollama Model Setup (Offline LLM)

Pull the exact Ollama model used by **AIVA**:

```bash
ollama run hf.co/ailearner2218/qwen2.5-0.5B-Instruct:Q4_K_M
```

## 🔐 API Configuration

Create a file named **`.env`** in the root directory of the project and add your API keys:

```env
DEEPGRAM_API_KEY=your_deepgram_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here
```

## Install Python dependencies
```bash
pip install python-dotenv requests sounddevice soundfile vosk


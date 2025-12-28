# 🤖 AIVA – AI Voice Assistant Robot

**AIVA (AI Voice Assistant)** is a hybrid intelligent system designed for educational robots to interact with students.
It automatically switches between **Online (Cloud-based)** and **Offline (Local-based)** processing based on internet availability, ensuring the robot always responds—even without internet.

---

## 🛠️ Project Architecture

AIVA dynamically adapts to connectivity:

| Feature            | Online Mode (Cloud) | Offline Mode (Local)         |
| ------------------ | ------------------- | ---------------------------- |
| **Speech-to-Text** | Deepgram API        | Vosk                         |
| **Brain (LLM)**    | Gemini / Groq       | **llama.cpp (qwen2.5)** |
| **Text-to-Speech** | Piper (Local)       | Piper (Local)                |

---

## 🚀 Step-by-Step Setup Guide

### 1️⃣ Prerequisites

Ensure the following are installed:

* **Python 3.10+**
* **Git**
* **CMake & C++ Build Tools** (for llama.cpp)
* **llama.cpp** (local inference server)

---

### 2️⃣ Installation

Clone the repository:

```bash
git clone https://github.com/Hariprasath-2218/AIVA.git
cd AIVA
```

---

## 🧠 llama.cpp Setup (Offline LLM)

AIVA uses **llama.cpp in server mode** instead of Ollama.

### Step 1: Install llama.cpp

```bash
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
mkdir build && cd build
cmake ..
cmake --build . --config Release
```

---

### Step 2: Download a GGUF Model

Example (Qwen 2.5 – lightweight, good for education):

```bash
mkdir models
# place your .gguf model here
```

Example model:

```
qwen2.5-0.5b-instruct-q4_k_m.gguf
```

---

### Step 3: Run llama.cpp Server

Start the local inference server:

```bash
./server \
  -m models/qwen2.5-0.5b-instruct-q4_k_m.gguf \
  --port 8080 \
  --ctx-size 2048
```

✅ The server will now be available at:

```
http://localhost:8080
```

AIVA automatically uses this server in **offline mode**.

---

## 🔐 API Configuration

Create a `.env` file in the project root:

```env
DEEPGRAM_API_KEY=your_deepgram_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here
```

> 🔹 These are only used when **internet is available**.

---

## 📦 Install Python Dependencies

```bash
pip install python-dotenv requests sounddevice soundfile vosk
```

---

## ▶️ Run AIVA

```bash
python main.py
```

### Behavior:

* 🌐 **Internet available** → Deepgram + Gemini/Groq
* 📴 **Internet offline** → Vosk + llama.cpp
* 🔊 **Voice output** → Piper (always local)



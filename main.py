import os
import time
import socket
import queue
import subprocess
import json
import requests
import sounddevice as sd
import soundfile as sf
from vosk import Model, KaldiRecognizer
from dotenv import load_dotenv

# =========================
# Load ENV
# =========================
load_dotenv()

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

print("DEEPGRAM:", bool(DEEPGRAM_API_KEY))
print("GEMINI:", bool(GEMINI_API_KEY))
print("GROQ:", bool(GROQ_API_KEY))

# =========================
# Constants
# =========================
SAMPLE_RATE = 16000
# Updated model aliases for late 2025
GEMINI_MODEL = "gemini-2.5-flash" 
GROQ_MODEL = "llama-3.3-70b-versatile"
OLLAMA_MODEL = "hf.co/ailearner2218/qwen2.5-0.5B-Instruct:Q4_K_M"
AUDIO_FILENAME = "input.wav"

SYSTEM_PROMPT = "You are AIVA, a helpful robot assistant for students. Keep your answers very short, simple, and conversational (maximum 2 to 3 lines). Avoid using bold or special characters."
# =========================
# Internet Check
# =========================
def internet_available():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except OSError:
        return False

# =========================
# OFFLINE STT (VOSK)
# =========================
vosk_model_path = "vosk_model/vosk-model-small-en-us-0.15"
audio_queue = queue.Queue()

# Error check for Vosk model folder
if os.path.exists(vosk_model_path):
    vosk_model = Model(vosk_model_path)
    vosk_rec = KaldiRecognizer(vosk_model, SAMPLE_RATE)
else:
    print(f"⚠️ Warning: Vosk model not found at {vosk_model_path}")

def offline_audio_callback(indata, frames, time_info, status):
    audio_queue.put(bytes(indata))

def offline_listen():
    audio_queue.queue.clear()
    vosk_rec.Reset()
    print("🎤 Listening (offline Vosk)...")
    with sd.RawInputStream(
        samplerate=SAMPLE_RATE,
        blocksize=8000,
        dtype="int16",
        channels=1,
        callback=offline_audio_callback
    ):
        while True:
            data = audio_queue.get()
            if vosk_rec.AcceptWaveform(data):
                result = json.loads(vosk_rec.Result())
                text = result.get("text", "").strip()
                if text:
                    return text

# =========================
# ONLINE STT (Deepgram REST API)
# =========================
def deepgram_listen(duration=5):
    print(f"🎤 Recording {duration}s for Deepgram...")
    audio = sd.rec(int(duration * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype="int16")
    sd.wait()
    sf.write(AUDIO_FILENAME, audio, SAMPLE_RATE) 
    
    print("📝 Sending to Deepgram...")
    with open(AUDIO_FILENAME, "rb") as f:
        audio_data = f.read()
        r = requests.post(
            "https://api.deepgram.com/v1/listen",
            headers={
                "Authorization": f"Token {DEEPGRAM_API_KEY}",
                "Content-Type": "audio/wav"
            },
            data=audio_data
        )
    r.raise_for_status()
    result = r.json()
    return result.get("results", {}).get("channels", [{}])[0].get("alternatives", [{}])[0].get("transcript","").strip()

# =========================
# ONLINE LLMs
# =========================
def ask_gemini(prompt):
    combined_prompt = f"{SYSTEM_PROMPT}\n\nStudent: {prompt}"
    # Using the current stable v1 endpoint and Gemini 2.5 Flash
    url = f"https://generativelanguage.googleapis.com/v1/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": combined_prompt }]}]}
    r = requests.post(url, json=payload, timeout=15)
    
    if r.status_code != 200:
        raise Exception(f"Gemini API Error {r.status_code}: {r.text}")
        
    return r.json()["candidates"][0]["content"]["parts"][0]["text"]

def ask_groq(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}],
        "temperature": 0.5
    }
    r = requests.post(url, headers=headers, json=payload, timeout=20)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

def ask_online_llm(prompt):
    try:
        return ask_gemini(prompt)
    except Exception as e:
        print(f"⚠️ Gemini Failed: {e}")
        print("🔄 Falling back to Groq...")
        try:
            return ask_groq(prompt)
        except Exception as e2:
            print(f"❌ Groq also failed: {e2}")
            return "I am sorry, I am currently unable to process your request."

# =========================
# OFFLINE LLM (OLLAMA)
# =========================
def ask_ollama(prompt):
    try:
        r = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            timeout=30
        )
        return r.json().get("response","")
    except Exception as e:
        return f"Offline model error: {e}"

# =========================
# TTS (PIPER)
# =========================
def speak(text):
    if not text: return
    # Clean text of markdown characters before speaking
    clean_text = text.replace("*", "").replace("#", "")
    
    subprocess.run(
        ["piper/piper.exe", "--model", "piper/en_US-amy-medium.onnx",
         "--config", "piper/en_US-amy-medium.onnx.json",
         "--output_file", "reply.wav"],
        input=clean_text.encode("utf-8"),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    if os.path.exists("reply.wav"):
        audio, sr = sf.read("reply.wav", dtype="float32")
        sd.play(audio, sr)
        sd.wait()

# =========================
# MAIN LOOP
# =========================
print("\n🤖 AIVA READY (Deepgram + Gemini + Groq)\n")

while True:
    try:
        if internet_available():
            print("\n🌐 ONLINE MODE")
            user_text = deepgram_listen(duration=5)
            
            if user_text:
                print("🧑 You:", user_text)
                ai_text = ask_online_llm(user_text)
                print("🤖 AI:", ai_text)
                speak(ai_text)
            else:
                print("... silence ...")
        else:
            print("\n📴 OFFLINE MODE")
            user_text = offline_listen()
            if user_text:
                print("🧑 You:", user_text)
                ai_text = ask_ollama(user_text)
                print("🤖 AI:", ai_text)
                speak(ai_text)

        time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n👋 Exiting AIVA")
        break
    except Exception as main_e:
        print(f"System Error: {main_e}")
        time.sleep(2)
## 🚀 How to Run the Project Locally

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Aankita2003/Enterprise-RAG-Engine.git
cd Enterprise-RAG-Engine
```

---

### 2️⃣ Install Required Software

Make sure the following software is installed:

- Python 3.11+
- Node.js
- Ollama
- VS Code (Recommended)

Downloads:
- Python: https://www.python.org/downloads/
- Node.js: https://nodejs.org/
- Ollama: https://ollama.com/

---

### 3️⃣ Create Virtual Environment

```bash
python -m venv venv
```

Activate environment:

#### Windows

```bash
venv\Scripts\activate
```

#### Mac/Linux

```bash
source venv/bin/activate
```

---

### 4️⃣ Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

### 5️⃣ Pull Required Ollama Models

```bash
ollama pull llama3.2
ollama pull nomic-embed-text
```

---

### 6️⃣ Start Ollama

```bash
ollama run llama3.2
```

Keep this terminal running.

---

### 7️⃣ Start Backend Server

Open a new terminal:

```bash
uvicorn main:app --reload
```

---

### 8️⃣ Start Frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

---

### 9️⃣ Open Application

Visit:

```bash
http://localhost:5173
```

Upload a PDF and start asking questions.

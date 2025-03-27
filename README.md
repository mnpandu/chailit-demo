# 🧠 Chainlit + LangGraph Business Assistant (HuggingFace + Vectorstore + Oracle Case Search)

This project is a modular AI assistant built using **Chainlit**, **LangGraph**, and **HuggingFace** that supports two main modes:
1. **Chat Mode** – Ask general business or IT-related questions based on `data.txt`
2. **Similarity Mode** – Look up similar Oracle cases based on a case number

---

## 🗂 Project Structure

| File | Purpose |
|------|---------|
| `chain_app.py` | Chainlit UI app with mode switching and message routing |
| `graph.py` | LangGraph flow orchestrating input resolution, retrieval, QA, and similarity |
| `nodes.py` | Node functions used in LangGraph (e.g., retrievers, answerer, similarity) |
| `vector_store.py` | FAISS vectorstore builder using `data.txt` for general knowledge |
| `oracle_client.py` | In-memory SQLite database simulating Oracle case data |
| `load_data.py` | Loads text file into LangChain documents |
| `sentencetransformer.py` | Loads HuggingFace model path for embedding |
| `data.txt` | Business knowledge source used in general chat mode |

---

## 💡 Modes

### 💬 Chat Mode
- Uses `data.txt` via FAISS + HuggingFace QA pipeline
- Ideal for business/technical Q&A

### 🔍 Similarity Mode
- Input a case number like `123456`
- Fetches case context from Oracle (SQLite)
- Searches for similar cases via FAISS vectorstore

---

## 🧪 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Chainlit app
```bash
chainlit run chain_app.py
```

### 3. Choose a mode and interact!

---

## 🧰 LLM & Embedding Setup

- Uses local HuggingFace models from `.cache`
- `sentence-transformers` for embeddings
- `distilbert-base-cased-distilled-squad` for QA

Ensure models are pre-downloaded to avoid internet access.

---

## ⚠️ Notes

- In-memory DB resets every run (demo only)
- You can extend this to real Oracle by replacing `oracle_client.py`
- If case number not found, the system will return a warning
- Mode-specific logic prevents case queries in Chat Mode and vice versa

---

## ✅ Future Upgrades
- Agent mode via LangChain `@tool` functions
- Oracle case vectorstore for similarity-only search
- Dynamic retrieval augmentation with metadata filtering

---

Made with ❤️ for business automation use cases.

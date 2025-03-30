# 🧠 Business Data Assistant with Agentic AI (Chainlit + LangGraph)

This is a multimodal, agentic assistant designed for business workflows using:

- ✅ **Chainlit** for frontend UI interaction
- ✅ **LangGraph** for modular reasoning and control
- ✅ **HuggingFace QA pipeline** for local NLP
- ✅ **Oracle DB** simulation for case/claim data

---

## 🚀 Features

### 🔹 Chat Mode
- Ask business or operational questions.
- Powered by a local DistilBERT QA model.

### 🔹 Similarity Mode
- Enter a **case number** (e.g., `MR123456`) to find similar case descriptions  
- Enter a **claim number** (e.g., `CL123456`) to find similar claim records  
- Uses FAISS similarity search on vector embeddings

#### 🔎 Sample Input
| Input Type | Example ID   | Used In          |
|------------|--------------|------------------|
| Case       | `MR123456`   | Case Similarity  |
| Claim      | `CL123456`   | Claim Similarity |

---

### 📄 Sample Case Data

| Case Number | Description                           | Comments                         |
|-------------|---------------------------------------|----------------------------------|
| MR123456    | System crash when exporting reports   | Issue occurs after patch update. |
| MR654321    | Login failure for admin accounts      | Likely due to expired certs.     |
| MR789012    | Data sync slow between nodes          | High latency on weekends.        |

### 📄 Sample Claim Data

| Claim Number | Case Number | Base Rate | Units | Discount | Calculated | Expected |
|--------------|-------------|-----------|--------|----------|------------|----------|
| CL123456     | 456789      | 100       | 3      | 50       | 250        | 300      |
| CL654321     | 123456      | 80        | 5      | 20       | 380        | 380      |
| CL789012     | 654321      | 120       | 2      | 0        | 240        | 240      |
| CL789013     | 789012      | 90        | 4      | 30       | 330        | 360      |

### ✅ Expected Output

#### Case Similarity (`MR123456`):
| Rank | Similar Case | Score |
|------|--------------|--------|
| 1    | Login failure for admin accounts... | 0.8423 |
| 2    | Data sync slow between nodes...     | 0.7150 |
| ...  | ...                                  | ...    |

#### Claim Similarity (`CL123456`):
| Rank | Case # | Claim #   | Claim Text                                                                   | Score  |
|------|--------|-----------|-------------------------------------------------------------------------------|--------|
| 1    | 456789 | CL123456  | Base Rate: 100 \| Units: 3 \| Discount: 50 \| Calculated: 250 \| Expected: 300 | 1.0000 |
| 2    | 789012 | CL789013  | Base Rate: 90  \| Units: 4 \| Discount: 30 \| Calculated: 330 \| Expected: 360 | 0.85   |

---

### 🔹 QC Nurse (Agentic AI)
- Enter a case number to run a full QC automation pipeline:
  - ✅ Fetch all claims
  - ✅ Create QC task
  - ✅ Review each claim
  - ✅ Check completion
  - ✅ Mark as done + send confirmation

---

## 📁 Folder Structure

```
├── chain_app.py         # Chainlit frontend
├── graph.py             # LangGraph flow definition
├── nodes.py             # All logic nodes (chat, similarity, QC)
├── oracle_client.py     # Case fetch simulation (Oracle)
├── vector_store.py      # FAISS vector loader
├── data.txt             # Source data
├── README.md            # This doc
```

---

## 🔧 Local Setup

```bash
# Install deps
pip install chainlit langchain langgraph faiss-cpu transformers

# Run app
chainlit run chain_app.py
```

Uses `distilbert-base-cased-distilled-squad` from local HuggingFace cache.

---

## 💡 Future Upgrades

### 🔹 Azure Integration
- ✅ Switch local models to Azure OpenAI:
  - Replace HuggingFace QA with `AzureChatOpenAI`
  - Secure API key & endpoint in `.env`
- ✅ Replace FAISS with Azure Cognitive Search
- ✅ Store QC task logs in Azure Blob or SQL DB
- ✅ Use Azure Functions to trigger real-time email alerts

### 🔹 LangChain Agent Upgrade
- Add memory and self-correction
- Visual tool routing
- Integrate LangSmith for monitoring

### 🔹 Chainlit UI Enhancements
- Display progress as timeline cards
- Add file upload for documents
- Multi-user session management

---

## ☁️ Agentic AI Architecture on Azure (Proposed)

| Layer                | Component                                         |
|---------------------|----------------------------------------------------|
| **UI**              | Chainlit (hosted on Azure Web App / Static Site)  |
| **Routing**         | LangGraph (Python logic + decision flows)         |
| **LLM**             | Azure OpenAI (e.g. gpt-4, gpt-35-turbo)            |
| **Search**          | Azure Cognitive Search                            |
| **Storage**         | Azure Blob Storage / Azure SQL DB for logs/tasks  |
| **Triggering**      | Azure Functions (QC task updates, email alerts)   |
| **Agent Memory**    | Azure Cosmos DB / Redis Cache                     |
| **Monitoring**      | LangSmith + Azure App Insights                    |

### 🔧 DevOps (optional)
- CI/CD via GitHub Actions to Azure App Service
- Secrets managed with Azure Key Vault
- Infrastructure-as-Code with Bicep or Terraform

---

## 🙌 Maintainers
Built by [YourTeam] with ❤️ using open AI infra.

Feel free to fork, deploy, and expand!

---

## 📦 Python Dependencies

All dependencies are listed in `requirements.txt`.

### 🔹 Install via pip

```bash
pip install -r requirements.txt
```

This includes:
- `chainlit` for UI
- `langchain`, `langgraph` for graph logic
- `transformers` and `sentence-transformers` for NLP
- `faiss-cpu` for similarity search
- `pandas` for mock database handling

---


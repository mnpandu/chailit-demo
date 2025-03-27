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
- Enter a case number to find similar cases.
- Uses FAISS similarity search on Oracle case vectors.

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

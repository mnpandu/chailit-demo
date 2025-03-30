# vector_store_claims_data.py
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from sentencetransformer import getSentenceModel
from oracle_client import get_claims_data

def build_claims_vectorstore() -> FAISS:
    claims_df = get_claims_data()

    documents = []
    for _, row in claims_df.iterrows():
        content = (
            f"{row['base_rate']} {row['units']} {row['discount']} {row['calculated_amount']} {row['expected_amount']}"
        )
        documents.append(Document(
            page_content=content,
            metadata={"case_number": row['case_number'], "claim_number": row['claim_number']}
        ))

    embeddings = HuggingFaceEmbeddings(model_name=getSentenceModel())
    return FAISS.from_documents(documents, embeddings)

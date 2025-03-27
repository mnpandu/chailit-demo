from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from load_data import load_documents_from_txt
from sentence_transformers import SentenceTransformer
from sentencetransformer import getSentenceModel

model=getSentenceModel()

def build_vectorstore(file_path: str) -> FAISS:
    documents = load_documents_from_txt(file_path)
    embeddings = HuggingFaceEmbeddings(model_name=model)
    return FAISS.from_documents(documents, embeddings)
import os
import tempfile
from typing import List
from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

class DocumentProcessor:
    def __init__(self):
        self.current_vectorstore = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=300,
            separators=["\n\n", "\n", " ", ""]
        )
        self.embeddings = HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-en-v1.5"  # Free local embeddings
        )

    def load_documents(self, file_path: str) -> List[Document]:
        try:
            if file_path.endswith(".pdf"):
                try:
                    return PyPDFLoader(file_path).load()
                except Exception:
                    return UnstructuredPDFLoader(file_path).load()
            elif file_path.endswith(".txt"):
                return TextLoader(file_path).load()
            else:
                raise ValueError("Only PDF/TXT files supported.")
        except Exception as e:
            raise Exception(f"Error loading file: {str(e)}")

    def process_uploaded_file(self, file_bytes: bytes, file_name: str) -> FAISS:
        try:
            with tempfile.NamedTemporaryFile(suffix=os.path.splitext(file_name)[1], delete=False) as tmp:
                tmp.write(file_bytes)
                tmp_path = tmp.name
            
            docs = self.load_documents(tmp_path)
            texts = self.text_splitter.split_documents(docs)
            self.current_vectorstore = FAISS.from_documents(texts, self.embeddings)
            return self.current_vectorstore
        finally:
            if 'tmp_path' in locals() and os.path.exists(tmp_path):
                os.remove(tmp_path)
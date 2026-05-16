# Placeholder for vector_store.py service
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

CHROMA_DIR = "data/chroma_db"
COLLECTION_NAME = "audit_documents"

embeddings = OllamaEmbeddings(
    model="nomic-embed-text"
)


def split_text_into_chunks(text: str, file_name: str):
    """
    Split long document text into smaller chunks.
    Each chunk keeps metadata so we know which file it came from.
    """

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )

    chunks = text_splitter.split_text(text)

    documents = []

    for index, chunk in enumerate(chunks):
        documents.append(
            Document(
                page_content=chunk,
                metadata={
                    "file_name": file_name,
                    "chunk_id": index
                }
            )
        )

    return documents


def add_documents_to_chroma(documents):
    """
    Store document chunks in ChromaDB using local Ollama embeddings.
    """

    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR
    )

    vector_store.add_documents(documents)

    return len(documents)


def get_vector_store():
    """
    Load the existing ChromaDB collection.
    """

    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR
    )


def search_similar_chunks(query: str, k: int = 4):
    """
    Search ChromaDB for chunks most similar to the user's question.
    """

    vector_store = get_vector_store()

    results = vector_store.similarity_search(
        query,
        k=k
    )

    return results
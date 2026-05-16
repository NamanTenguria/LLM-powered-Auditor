# Placeholder for rag_chain.py service
from langchain_ollama import ChatOllama

from backend.services.vector_store import get_vector_store


llm = ChatOllama(
    model="llama3.2:3b",
    temperature=0
)


def load_audit_qa_prompt() -> str:
    """
    Load the audit Q&A prompt template from the prompts folder.
    """

    with open("backend/prompts/audit_qa_prompt.txt", "r", encoding="utf-8") as file:
        return file.read()


def answer_question(question: str) -> dict:
    """
    Answer a user question using RAG.

    Steps:
    1. Retrieve relevant chunks from ChromaDB.
    2. Add those chunks into the audit prompt.
    3. Ask the local Ollama chat model to answer.
    4. Return answer and source chunks.
    """

    vector_store = get_vector_store()

    retriever = vector_store.as_retriever(
        search_kwargs={"k": 4}
    )

    relevant_docs = retriever.invoke(question)

    context_parts = []

    for doc in relevant_docs:
        file_name = doc.metadata.get("file_name", "unknown file")
        chunk_id = doc.metadata.get("chunk_id", "unknown chunk")

        context_parts.append(
            f"Source File: {file_name}\n"
            f"Chunk ID: {chunk_id}\n"
            f"Text:\n{doc.page_content}"
        )

    context = "\n\n---\n\n".join(context_parts)

    prompt_template = load_audit_qa_prompt()

    final_prompt = prompt_template.format(
        question=question,
        context=context
    )

    response = llm.invoke(final_prompt)

    sources = []

    for doc in relevant_docs:
        sources.append(
            {
                "file_name": doc.metadata.get("file_name"),
                "chunk_id": doc.metadata.get("chunk_id"),
                "preview": doc.page_content[:300]
            }
        )

    return {
        "question": question,
        "answer": response.content,
        "sources": sources
    }
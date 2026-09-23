import os
import chromadb
from google import genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("No se encontró GEMINI_API_KEY en el archivo .env")

# Inicializamos el cliente con la nueva librería google-genai
client = genai.Client(api_key=api_key)

chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="documentos_tecnicos")

def add_document(doc_id: str, text: str):
    print(f"Indexando documento: {doc_id}...")
    
    # Usamos el nuevo modelo vigente: gemini-embedding-2
    response = client.models.embed_content(
        model="gemini-embedding-2",
        contents=text
    )
    # En la nueva SDK, el vector viene en .embeddings[0].values
    embedding = response.embeddings[0].values
    
    collection.add(
        ids=[doc_id], 
        embeddings=[embedding], 
        documents=[text]
    )
    print(f"Documento '{doc_id}' indexado con éxito.")

def search_context(query: str, n_results: int = 3) -> str:
    # Usamos el mismo modelo gemini-embedding-2 para buscar
    response = client.models.embed_content(
        model="gemini-embedding-2",
        contents=query
    )
    query_embedding = response.embeddings[0].values
    
    results = collection.query(
        query_embeddings=[query_embedding], 
        n_results=n_results
    )
    
    if results['documents'] and results['documents'][0]:
        return "\n---\n".join(results['documents'][0])
    
    return ""
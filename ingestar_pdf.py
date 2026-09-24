import os
import fitz  # PyMuPDF
from src.vector_store import add_document

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extrae todo el texto de un archivo PDF usando PyMuPDF."""
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text() + "\n"
    return text

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    """
    Divide el texto en fragmentos (chunks) usando una ventana deslizante.
    chunk_size: cantidad de caracteres por fragmento.
    overlap: cantidad de caracteres que se superponen entre fragmentos.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def process_and_ingest_pdf(pdf_filename: str):
    """Extrae, divide e ingesta el PDF en la base de datos vectorial."""
    # Buscamos el archivo dentro de la carpeta 'data/'
    pdf_path = os.path.join("data", pdf_filename)
    
    if not os.path.exists(pdf_path):
        print(f"Error: No se encontró el archivo '{pdf_path}'. Asegurate de que esté en la carpeta 'data/'.")
        return

    print(f"Leyendo archivo '{pdf_filename}'...")
    raw_text = extract_text_from_pdf(pdf_path)
    
    print("Dividiendo el texto en fragmentos (chunking)...")
    chunks = chunk_text(raw_text)
    
    print(f"Indexando {len(chunks)} fragmentos en ChromaDB...")
    for i, chunk in enumerate(chunks):
        # Creamos un ID único para cada fragmento (ej: manual_rtems.pdf_chunk_0)
        doc_id = f"{pdf_filename}_chunk_{i}"
        add_document(doc_id, chunk)
        
    print(f"¡Ingesta de '{pdf_filename}' completada con éxito!")

if __name__ == "__main__":
    # Aseguramos que la carpeta data exista
    os.makedirs("data", exist_ok=True)
    
    # Nombre del archivo que vamos a procesar
    # Reemplazá esto con el nombre de tu archivo PDF real
    archivo_pdf = "termo.pdf" 
    
    process_and_ingest_pdf(archivo_pdf)
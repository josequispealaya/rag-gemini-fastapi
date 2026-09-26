import os
import shutil
from fastapi import FastAPI, File, UploadFile, HTTPException, Body
from pydantic import BaseModel
from src.vector_store import search_context
from src.generator import generate_answer

# Importamos la función de ingesta
from ingestar_pdf import process_and_ingest_pdf
from src.vector_store import add_document
from typing import List

app = FastAPI(
    title="RAG Gemini API", 
    description="Sistema RAG para documentación técnica usando FastAPI y Gemini",
    version="0.1.0"
)

@app.get("/")
def read_root():
    return {"mensaje": "Bienvenido a la API del sistema RAG. Entrá a /docs para probarla."}

# Volvemos a la clase original simple
class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    question: str
    answer: str
    context_used: str

# Agregamos Body(...) con openapi_examples para habilitar el selector múltiple
@app.post("/ask", response_model=QueryResponse)
def ask_question(
    request: QueryRequest = Body(
        ...,
        openapi_examples={
            "hardware": {
                "summary": "Consulta de Hardware (Black Pill)",
                "value": {"question": "¿Qué pines uso para transmitir datos por puerto serie en la Black Pill?"}
            },
            "software": {
                "summary": "Consulta de RTOS (RTEMS)",
                "value": {"question": "¿Qué es RTEMS y para qué se diseña?"}
            }
        }
    )
):
    """
    Endpoint principal. Recibe una pregunta, busca en la base de datos vectorial
    y devuelve una respuesta generada por Gemini basada en el contexto.
    """
    try:
        context = search_context(request.question, n_results=1)
        
        if not context:
            return QueryResponse(
                question=request.question,
                answer="No se encontró contexto relevante en la base de datos para responder a esta pregunta.",
                context_used=""
            )
            
        answer = generate_answer(request.question, context)
        
        return QueryResponse(
            question=request.question,
            answer=answer.strip(),
            context_used=context
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Agregamos el endpoint para subir PDFs y procesarlos
@app.post("/upload")
async def upload_pdfs(files: List[UploadFile] = File(...)):
    os.makedirs("data", exist_ok=True)
    procesados = []
    
    for file in files:
        if not file.filename.endswith(".pdf"):
            continue # Saltamos los archivos que no sean PDF
        
        file_path = os.path.join("data", file.filename)
        
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
                
            # Validación de tamaño individual (5MB)
            file_size = os.path.getsize(file_path)
            if file_size > 5 * 1024 * 1024:
                os.remove(file_path)
                continue
            
            # Ingestar usando tu función empaquetada
            process_and_ingest_pdf(file.filename)
            procesados.append(file.filename)
            
        except Exception as e:
            print(f"Error procesando {file.filename}: {e}")
            
    if not procesados:
        raise HTTPException(status_code=400, detail="Ningún archivo válido superó las validaciones.")
        
    return {"message": f"Archivos procesados exitosamente: {', '.join(procesados)}"}
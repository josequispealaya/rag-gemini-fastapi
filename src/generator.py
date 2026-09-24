import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("No se encontró GEMINI_API_KEY en el archivo .env")

client = genai.Client(api_key=api_key)

def generate_answer(query: str, context: str) -> str:
    """Genera una respuesta basándose únicamente en el contexto recuperado."""
    prompt = f"""
    Sos un asistente técnico experto. Tu tarea es responder la pregunta del usuario utilizando ÚNICAMENTE el contexto provisto abajo.
    Si la respuesta no se encuentra en el contexto, respondé: "No tengo información suficiente en los documentos para responder esto."
    No inventes información.

    Contexto recuperado:
    {context}

    Pregunta del usuario:
    {query}
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-3.5-flash-lite',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.0,
            )
        )
        return response.text
        
    except Exception as e:
        print(f"Error interno con la API de Gemini: {e}")
        raise HTTPException(
            status_code=503,
            detail="El servicio de inteligencia artificial está experimentando alta demanda y no está disponible temporalmente. Por favor, intentá nuevamente en unos segundos."
        )
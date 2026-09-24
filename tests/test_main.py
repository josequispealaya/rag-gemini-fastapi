from fastapi.testclient import TestClient
from src.main import app

# Instanciamos el cliente de pruebas
client = TestClient(app)

def test_read_root():
    """Prueba que el endpoint raíz responda correctamente."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"mensaje": "Bienvenido a la API del sistema RAG. Entrá a /docs para probarla."}

def test_ask_question_no_context():
    """Prueba que el sistema maneje bien preguntas sin contexto en la base."""
    payload = {
        "question": "¿Cuál es la capital de Francia?"
    }
    response = client.post("/ask", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["question"] == payload["question"]
    # En GitHub Actions la BD arranca vacía, así que esperamos este mensaje:
    assert "No se encontró contexto relevante" in data["answer"]

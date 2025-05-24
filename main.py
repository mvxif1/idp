from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
import requests

app = FastAPI()

# Modelos de datos
class SolicitudCompra(BaseModel):
    nombre_usuario: str
    correo: str
    item: str
    cantidad: int
    motivo: str

class SolicitudCargaFamiliar(BaseModel):
    nombre: str
    rut: str
    nombre_familiar: str
    rut_familiar: str
    parentesco: str


MAKE_WEBHOOK_COMPRAS = "https://hook.us2.make.com/kbfzdf21pwwi1kfoxdb5q6lqgepgup69"
MAKE_WEBHOOK_COMPRAS_CONSULTAR = "https://hook.us2.make.com/nsdmt1z36k3yp16r8uzniuqnsdhfghm5"

MAKE_WEBHOOK_CARGAS = "https://hook.us2.make.com/31k1qtua6t71xvc7g8ty88l9dfn6dit6"
MAKE_WEBHOOK_PAGOS = "https://hook.make.com/tu-webhook-pagos"

################ Endpoints para Solicitud de Compras ################
@app.post("/compras/solicitud")
def crear_solicitud_compra(solicitud: SolicitudCompra):
    solicitud_id = str(uuid.uuid4())
    payload = solicitud.model_dump()
    payload["solicitud_id"] = solicitud_id
    try:
        response = requests.post(MAKE_WEBHOOK_COMPRAS, json=payload, timeout=5)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error enviando a Make: {str(e)}")
    return {"solicitud_id": solicitud_id, "mensaje": "Solicitud enviada a Make"}

## endpoint para verificar el estado de la solicitud
@app.get("/compras/estado/{solicitud_id}")
def consultar_estado_solicitud_webhook(solicitud_id: str):
    if not solicitud_id:
        raise HTTPException(status_code=400, detail="ID de solicitud requerido")
    try:
        response = requests.get(
            MAKE_WEBHOOK_COMPRAS_CONSULTAR,
            params={"solicitud_id": solicitud_id},
            timeout=5
        )
        response.raise_for_status()
        try:
            return response.json()
        except ValueError:
            return { "detalle": "Respuesta", "contenido": response.text}
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error consultando a Make: {str(e)}")

################ Endpoints para Cargas Familiares ################
@app.post("/cargas/solicitud")
def crear_solicitud_carga(carga: SolicitudCargaFamiliar):
    carga_id = str(uuid.uuid4())
    payload = carga.model_dump()
    payload["carga_id"] = carga_id
    payload["estado"] = "pendiente"
    try:
        response = requests.post(MAKE_WEBHOOK_CARGAS, json=payload, timeout=5)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error enviando a Make: {str(e)}")
    return {"carga_id": carga_id, "estado": "pendiente"}

## para futuro endpoint para verificar el estado de la solicitud
@app.get("/cargas/estado/{carga_id}")
def estado_carga_familiar(carga_id: str):
    if not carga_id:
        raise HTTPException(status_code=400, detail="ID de carga requerido")
    return {"carga_id": carga_id, "estado": "simulado"}


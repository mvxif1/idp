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

class PagoWebPay(BaseModel):
    solicitud_id: str
    monto: float


MAKE_WEBHOOK_COMPRAS = "https://hook.us2.make.com/kbfzdf21pwwi1kfoxdb5q6lqgepgup69"
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

@app.get("/compras/estado/{solicitud_id}")
def estado_solicitud_compra(solicitud_id: str):
    if not solicitud_id:
        raise HTTPException(status_code=400, detail="ID de solicitud requerido")
    return {"solicitud_id": solicitud_id, "estado": "simulado"}

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

@app.get("/cargas/estado/{carga_id}")
def estado_carga_familiar(carga_id: str):
    if not carga_id:
        raise HTTPException(status_code=400, detail="ID de carga requerido")
    return {"carga_id": carga_id, "estado": "simulado"}

# Endpoint para simular pago WebPay
@app.post("/pagos/webpay")
def pagar_webpay(pago: PagoWebPay):
    if not pago.solicitud_id or pago.monto <= 0:
        raise HTTPException(status_code=400, detail="Datos de pago inválidos")
    payload = pago.model_dump()
    payload["estado_pago"] = "aprobado"
    try:
        response = requests.post(MAKE_WEBHOOK_PAGOS, json=payload, timeout=5)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error enviando a Make: {str(e)}")
    return {"solicitud_id": pago.solicitud_id, "monto": pago.monto, "estado_pago": "aprobado"}
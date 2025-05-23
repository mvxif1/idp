from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
import requests

app = FastAPI()

# Modelos de datos
class SolicitudCompra(BaseModel):
    nombre: str
    item: str
    cantidad: int
    motivo: str

class SolicitudCargaFamiliar(BaseModel):
    nombre: str
    rut: str
    parentesco: str

class PagoWebPay(BaseModel):
    solicitud_id: str
    monto: float


MAKE_WEBHOOK_COMPRAS = "https://hook.make.com/tu-webhook-compras"
MAKE_WEBHOOK_CARGAS = "https://hook.make.com/tu-webhook-cargas"
MAKE_WEBHOOK_PAGOS = "https://hook.make.com/tu-webhook-pagos"

# Endpoints para Solicitud de Compras
@app.post("/compras/solicitud")
def crear_solicitud_compra(solicitud: SolicitudCompra):
    solicitud_id = str(uuid.uuid4())
    payload = solicitud.dict()
    payload["solicitud_id"] = solicitud_id
    payload["estado"] = "pendiente"
    # Enviar datos a Make para guardar en Google Sheets
    try:
        requests.post(MAKE_WEBHOOK_COMPRAS, json=payload, timeout=5)
    except Exception as e:
        pass  # Puedes loguear el error si quieres
    return {"solicitud_id": solicitud_id, "estado": "pendiente"}

@app.get("/compras/estado/{solicitud_id}")
def estado_solicitud_compra(solicitud_id: str):
    # Aquí deberías consultar el estado desde Google Sheets vía Make
    # Simulación: solo retorna el estado "simulado"
    return {"solicitud_id": solicitud_id, "estado": "simulado"}

# Endpoints para Cargas Familiares
@app.post("/cargas/solicitud")
def crear_solicitud_carga(carga: SolicitudCargaFamiliar):
    carga_id = str(uuid.uuid4())
    payload = carga.dict()
    payload["carga_id"] = carga_id
    payload["estado"] = "pendiente"
    # Enviar datos a Make para guardar en Google Sheets
    try:
        requests.post(MAKE_WEBHOOK_CARGAS, json=payload, timeout=5)
    except Exception as e:
        pass
    return {"carga_id": carga_id, "estado": "pendiente"}

@app.get("/cargas/estado/{carga_id}")
def estado_carga_familiar(carga_id: str):
    # Aquí deberías consultar el estado desde Google Sheets vía Make
    # Simulación: solo retorna el estado "simulado"
    return {"carga_id": carga_id, "estado": "simulado"}

# Endpoint para simular pago WebPay
@app.post("/pagos/webpay")
def pagar_webpay(pago: PagoWebPay):
    payload = pago.dict()
    payload["estado_pago"] = "aprobado"
    # Notificar a Make del pago realizado
    try:
        requests.post(MAKE_WEBHOOK_PAGOS, json=payload, timeout=5)
    except Exception as e:
        pass
    return {"solicitud_id": pago.solicitud_id, "monto": pago.monto, "estado_pago": "aprobado"}
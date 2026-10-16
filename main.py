from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3
from datetime import datetime, timedelta, date
from urllib.parse import quote
from pydantic import BaseModel, Field, field_validator, ValidationError

app = FastAPI(title="Control de Invernadero - Libro de Campo Galicia")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/manifest.json")
def obtener_manifest():
    return FileResponse("static/manifest.json", media_type="application/manifest+json")

@app.get("/sw.js")
def obtener_service_worker():
    return FileResponse("static/sw.js", media_type="application/javascript", headers={"Service-Worker-Allowed": "/"})

templates = Jinja2Templates(directory="templates")

DB_FILE = "invernadero.db"

# Cultivos y sus temporadas óptimas en el clima atlántico gallego
CULTIVOS_TEMPORADA = {
    "Pemento de Padrón / Herbón": "Primavera-Verano",
    "Tomate Negro de Santiago": "Primavera-Verano",
    "Lechuga": "Otoño-Invierno",
    "Espinaca": "Otoño-Invierno",
    "Repollo Lorena": "Invierno-Primavera",
    "Cilantro": "Primavera-Verano",
    "Xudía / Judía Verde": "Primavera-Verano"
}

# ==============================================================================
# MODELOS PYDANTIC: EL "GUARDIA DE SEGURIDAD" DE LOS DATOS
# ==============================================================================

class ValidacionError(Exception):
    """Excepción para reglas contextuales de base de datos o de inocuidad."""
    def __init__(self, mensaje: str, tab: str = "lotes"):
        self.mensaje = mensaje
        self.tab = tab
        super().__init__(mensaje)


def extraer_mensaje_pydantic(e: ValidationError) -> str:
    """Traduce y formatea amigablemente el primer error detectado por Pydantic."""
    if not e.errors():
        return "Error de validación en los datos proporcionados."
    err = e.errors()[0]
    campo = str(err["loc"][-1]) if err.get("loc") else "campo"
    msg = err.get("msg", "")

    # Limpiar prefijo 'Value error, ' que genera Pydantic cuando salta un @field_validator
    if msg.startswith("Value error, "):
        msg = msg.replace("Value error, ", "")

    # Mapeo descriptivo para mensajes comunes en español
    if "greater than 0" in msg:
        msg = "Debe ser un valor numérico estrictamente positivo mayor que 0."
    elif "greater than or equal to 0" in msg:
        msg = "No puede ser un valor negativo (debe ser mayor o igual a 0)."
    elif "at least" in msg and "characters" in msg:
        msg = f"El texto es demasiado corto ({msg})."

    nombres_campos = {
        "cultivo": "Cultivo",
        "cantidad": "Cantidad",
        "superficie_m2": "Superficie (m²)",
        "fecha_siembra": "Fecha de siembra",
        "plazo_seguridad_dias": "Plazo de seguridad",
        "volumen_caldo_l": "Volumen de caldo",
        "num_registro_mapa": "Nº Registro MAPA",
        "materia_activa": "Materia activa",
        "producto_comercial": "Producto comercial",
        "dosis": "Dosis",
        "dosis_kg_m2": "Dosis (kg/m²)",
        "nombre_abono": "Nombre del abono",
        "fecha_abonado": "Fecha de abonado",
        "fecha_cosecha": "Fecha de cosecha",
        "cantidad_kg": "Cantidad cosechada (kg)",
        "albaran_lote_salida": "Albarán / Lote de salida",
        "destino_comercial": "Destino comercial",
        "titular": "Titular",
        "nif": "NIF/CIF",
        "regepa": "Código REGEPA",
        "ropo_titular": "Nº Carné ROPO",
        "poligono": "Polígono SIGPAC",
        "parcela": "Parcela SIGPAC",
        "recinto": "Recinto SIGPAC",
        "sup_invernadero_m2": "Superficie total invernadero"
    }

    nombre_humano = nombres_campos.get(campo, campo)
    return f"Validación de Pydantic en [{nombre_humano}]: {msg}"


class LoteCreate(BaseModel):
    """Guardia Pydantic para el registro de nuevos lotes de cultivo."""
    cultivo: str = Field(..., min_length=2, max_length=100)
    variedad: str = Field(default="", max_length=100)
    cantidad: int = Field(..., gt=0, description="Cantidad de plantas o semillas mayor a 0")
    superficie_m2: float = Field(..., gt=0.0, description="Superficie en m2 mayor a 0")
    fecha_siembra: str = Field(default="")
    estado: str = Field(default="Sembrado")

    @field_validator("cultivo")
    @classmethod
    def validar_cultivo(cls, v: str) -> str:
        v_clean = v.strip()
        if len(v_clean) < 2:
            raise ValueError("El nombre del cultivo no puede estar vacío y debe tener al menos 2 caracteres.")
        return v_clean

    @field_validator("fecha_siembra")
    @classmethod
    def validar_fecha_siembra(cls, v: str) -> str:
        if v:
            try:
                f_dt = datetime.strptime(v, "%Y-%m-%d").date()
                if f_dt > date.today() + timedelta(days=60):
                    raise ValueError("La fecha de siembra no puede planificarse con más de 60 días en el futuro.")
            except ValueError as ex:
                if "60 días" in str(ex):
                    raise ex
                raise ValueError("El formato de fecha de siembra es inválido. Use AAAA-MM-DD.")
        return v

    @field_validator("estado")
    @classmethod
    def validar_estado(cls, v: str) -> str:
        estados_validos = ("Sembrado", "En Crecimiento", "Cosechado", "Finalizado")
        if v not in estados_validos:
            raise ValueError(f"Estado fenológico no válido. Debe ser uno de: {', '.join(estados_validos)}")
        return v


class TratamientoFitosanitarioCreate(BaseModel):
    """Guardia Pydantic para el cuaderno de fitosanitarios oficial (ROPO/MAPA)."""
    lote_id: int = Field(..., gt=0)
    fecha_tratamiento: str = Field(..., min_length=10, max_length=10)
    plaga_enfermedad: str = Field(..., min_length=2)
    producto_comercial: str = Field(..., min_length=2)
    num_registro_mapa: str = Field(..., min_length=3)
    materia_activa: str = Field(..., min_length=2)
    dosis: str = Field(..., min_length=1)
    volumen_caldo_l: float = Field(..., gt=0.0)
    aplicador_nombre: str = Field(..., min_length=2)
    ropo_aplicador: str = Field(..., min_length=3)
    plazo_seguridad_dias: int = Field(default=0, ge=0)
    observaciones: str = Field(default="")

    @field_validator("num_registro_mapa")
    @classmethod
    def validar_mapa(cls, v: str) -> str:
        v_clean = v.strip()
        if len(v_clean) < 3:
            raise ValueError("El Nº de Registro Oficial MAPA es obligatorio por normativa comunitaria (mínimo 3 caracteres).")
        return v_clean

    @field_validator("fecha_tratamiento")
    @classmethod
    def validar_fecha_trat(cls, v: str) -> str:
        try:
            f_dt = datetime.strptime(v, "%Y-%m-%d").date()
            if f_dt > date.today():
                raise ValueError("La fecha de aplicación fitosanitaria no puede ser futura. El cuaderno de campo exige registrar labores ya efectuadas.")
        except ValueError as ex:
            if "futura" in str(ex):
                raise ex
            raise ValueError("El formato de fecha de tratamiento es incorrecto. Utilice AAAA-MM-DD.")
        return v


class FertilizacionCreate(BaseModel):
    """Guardia Pydantic para el Plan de Fertilización Sostenible (RD 1051/2022)."""
    lote_id: int = Field(..., gt=0)
    fecha_abonado: str = Field(..., min_length=10, max_length=10)
    tipo_fertilizante: str = Field(..., min_length=2)
    nombre_abono: str = Field(..., min_length=2)
    riqueza_npk: str = Field(default="")
    dosis_kg_m2: float = Field(..., gt=0.0, le=10.0)
    metodo_aplicacion: str = Field(..., min_length=2)
    observaciones: str = Field(default="")

    @field_validator("dosis_kg_m2")
    @classmethod
    def validar_dosis(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("La dosis de abonado debe ser estrictamente positiva mayor a 0 kg/m².")
        if v > 10.0:
            raise ValueError("Por directriz de fertilización sostenible contra la contaminación de aguas por nitratos (RD 1051/2022), no se admiten aportes superiores a 10 kg/m² en una sola intervención.")
        return v

    @field_validator("fecha_abonado")
    @classmethod
    def validar_fecha_abonado(cls, v: str) -> str:
        try:
            f_dt = datetime.strptime(v, "%Y-%m-%d").date()
            if f_dt > date.today() + timedelta(days=7):
                raise ValueError("La fecha de abonado no puede ser superior a 7 días en el futuro.")
        except ValueError as ex:
            if "futuro" in str(ex):
                raise ex
            raise ValueError("El formato de fecha de abonado es incorrecto. Utilice AAAA-MM-DD.")
        return v


class CosechaCreate(BaseModel):
    """Guardia Pydantic para la Trazabilidad y Seguridad Alimentaria."""
    lote_id: int = Field(..., gt=0)
    fecha_cosecha: str = Field(..., min_length=10, max_length=10)
    cantidad_kg: float = Field(..., gt=0.0)
    destino_comercial: str = Field(..., min_length=2)
    albaran_lote_salida: str = Field(..., min_length=2)
    observaciones: str = Field(default="")

    @field_validator("cantidad_kg")
    @classmethod
    def validar_cantidad(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("La cantidad cosechada debe ser estrictamente mayor a 0 kg.")
        return v

    @field_validator("destino_comercial")
    @classmethod
    def validar_destino(cls, v: str) -> str:
        v_clean = v.strip()
        if not v_clean:
            raise ValueError("El destino comercial o cliente es un dato obligatorio de trazabilidad según la Ley 17/2011 de Seguridad Alimentaria.")
        return v_clean

    @field_validator("albaran_lote_salida")
    @classmethod
    def validar_albaran(cls, v: str) -> str:
        v_clean = v.strip()
        if not v_clean:
            raise ValueError("El código de albarán o lote de expedición es obligatorio para garantizar la trazabilidad de salida.")
        return v_clean


class ExplotacionUpdate(BaseModel):
    """Guardia Pydantic para los Datos Oficiales de la Explotación y SIGPAC."""
    titular: str = Field(..., min_length=3)
    nif: str = Field(..., min_length=8)
    regepa: str = Field(..., min_length=3)
    ropo_titular: str = Field(..., min_length=3)
    provincia: str = Field(..., min_length=2)
    municipio: str = Field(..., min_length=2)
    parroquia: str = Field(default="")
    poligono: int = Field(..., gt=0)
    parcela: int = Field(..., gt=0)
    recinto: int = Field(..., gt=0)
    sup_invernadero_m2: float = Field(..., gt=0.0)
    coordenadas_gps: str = Field(default="")


# ==============================================================================
# BASE DE DATOS Y MIGRACIONES
# ==============================================================================

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # 1. Tabla de datos generales de la explotación agrícola en Galicia (SIGPAC / REGEPA)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS explotacion (
            id INTEGER PRIMARY KEY,
            titular TEXT NOT NULL,
            nif TEXT NOT NULL,
            regepa TEXT NOT NULL,
            ropo_titular TEXT NOT NULL,
            provincia TEXT NOT NULL,
            municipio TEXT NOT NULL,
            parroquia TEXT DEFAULT '',
            poligono INTEGER NOT NULL,
            parcela INTEGER NOT NULL,
            recinto INTEGER NOT NULL,
            sup_invernadero_m2 REAL NOT NULL,
            coordenadas_gps TEXT DEFAULT ''
        )
    """)

    # Migración de columnas de explotación si no existen
    exp_columns = [c["name"] for c in cursor.execute("PRAGMA table_info(explotacion)").fetchall()]
    if "parroquia" not in exp_columns:
        cursor.execute("ALTER TABLE explotacion ADD COLUMN parroquia TEXT DEFAULT ''")
    if "coordenadas_gps" not in exp_columns:
        cursor.execute("ALTER TABLE explotacion ADD COLUMN coordenadas_gps TEXT DEFAULT ''")

    # 2. Tabla de producción / lotes de cultivo
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produccion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lote_codigo TEXT,
            cultivo TEXT NOT NULL,
            variedad TEXT,
            cantidad INTEGER NOT NULL,
            superficie_m2 REAL DEFAULT 50.0,
            fecha_siembra TEXT,
            temporada TEXT NOT NULL,
            estado TEXT NOT NULL
        )
    """)

    # Migración de columnas de produccion si la tabla ya existía
    columns = [c["name"] for c in cursor.execute("PRAGMA table_info(produccion)").fetchall()]
    if "lote_codigo" not in columns:
        cursor.execute("ALTER TABLE produccion ADD COLUMN lote_codigo TEXT")
    if "variedad" not in columns:
        cursor.execute("ALTER TABLE produccion ADD COLUMN variedad TEXT")
    if "superficie_m2" not in columns:
        cursor.execute("ALTER TABLE produccion ADD COLUMN superficie_m2 REAL DEFAULT 50.0")
    if "fecha_siembra" not in columns:
        cursor.execute("ALTER TABLE produccion ADD COLUMN fecha_siembra TEXT")

    # 3. Registro Oficial de Tratamientos Fitosanitarios (Normativa Galicia / ROPO / MAPA)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tratamientos_fitosanitarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lote_id INTEGER NOT NULL,
            fecha_tratamiento TEXT NOT NULL,
            plaga_enfermedad TEXT NOT NULL,
            producto_comercial TEXT NOT NULL,
            num_registro_mapa TEXT NOT NULL,
            materia_activa TEXT NOT NULL,
            dosis TEXT NOT NULL,
            volumen_caldo_l REAL NOT NULL,
            aplicador_nombre TEXT NOT NULL,
            ropo_aplicador TEXT NOT NULL,
            plazo_seguridad_dias INTEGER NOT NULL,
            fecha_fin_seguridad TEXT NOT NULL,
            observaciones TEXT,
            FOREIGN KEY (lote_id) REFERENCES produccion(id)
        )
    """)

    # 4. Plan de Fertilización Sostenible (RD 1051/2022)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fertilizaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lote_id INTEGER NOT NULL,
            fecha_abonado TEXT NOT NULL,
            tipo_fertilizante TEXT NOT NULL,
            nombre_abono TEXT NOT NULL,
            riqueza_npk TEXT,
            dosis_kg_m2 REAL NOT NULL,
            metodo_aplicacion TEXT NOT NULL,
            observaciones TEXT,
            FOREIGN KEY (lote_id) REFERENCES produccion(id)
        )
    """)

    # 5. Trazabilidad de Cosecha y Comercialización (Salidas de producto)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cosechas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lote_id INTEGER NOT NULL,
            fecha_cosecha TEXT NOT NULL,
            cantidad_kg REAL NOT NULL,
            destino_comercial TEXT NOT NULL,
            albaran_lote_salida TEXT NOT NULL,
            plazo_respetado INTEGER NOT NULL DEFAULT 1,
            observaciones TEXT,
            FOREIGN KEY (lote_id) REFERENCES produccion(id)
        )
    """)

    # Semilla de datos iniciales de la explotación si está vacía
    cursor.execute("SELECT COUNT(*) as count FROM explotacion")
    if cursor.fetchone()["count"] == 0:
        cursor.execute("""
            INSERT INTO explotacion (
                id, titular, nif, regepa, ropo_titular, provincia, municipio, parroquia,
                poligono, parcela, recinto, sup_invernadero_m2, coordenadas_gps
            ) VALUES (
                1, 'Horta do Mandeo S.C.G.', 'F-15984321', 'ES-GA-15003429',
                'ROPO-GA-15-4892-A', 'A Coruña', 'Betanzos', 'San Martiño',
                14, 82, 1, 850.0, '43.2812, -8.2145'
            )
        """)

    # Actualizar códigos de lote pendientes si existen registros antiguos
    cursor.execute("UPDATE produccion SET lote_codigo = 'LOTE-GA-' || id WHERE lote_codigo IS NULL OR lote_codigo = ''")
    cursor.execute("UPDATE produccion SET fecha_siembra = date('now') WHERE fecha_siembra IS NULL")
    cursor.execute("UPDATE produccion SET variedad = 'Local Galicia' WHERE variedad IS NULL")

    conn.commit()
    conn.close()

# Ejecutar inicialización de tablas
init_db()


# ==============================================================================
# ENDPOINTS Y RUTAS
# ==============================================================================

@app.get("/", response_class=HTMLResponse)
def leer_raiz(
    request: Request,
    tab: str = "lotes",
    error: str | None = None,
    msg_exito: str | None = None
):
    conn = get_db()
    cursor = conn.cursor()

    # Datos de explotación
    cursor.execute("SELECT * FROM explotacion WHERE id = 1")
    exp = dict(cursor.fetchone())

    # Lotes de cultivo con verificación de plazo de seguridad fitosanitario
    cursor.execute("""
        SELECT p.*, 
               MAX(t.fecha_fin_seguridad) as max_fin_seguridad,
               COUNT(t.id) as total_tratamientos
        FROM produccion p
        LEFT JOIN tratamientos_fitosanitarios t ON p.id = t.lote_id
        GROUP BY p.id
        ORDER BY p.id DESC
    """)
    filas_produccion = cursor.fetchall()

    hoy = date.today()
    hoy_str = hoy.isoformat()

    lotes = []
    total_lotes_activos = 0
    total_en_carencia = 0
    sup_cultivada_m2 = 0.0

    for fila in filas_produccion:
        item = dict(fila)
        max_fin = item.get("max_fin_seguridad")
        en_carencia = False
        dias_restantes = 0

        if max_fin and max_fin >= hoy_str:
            en_carencia = True
            total_en_carencia += 1
            try:
                fecha_fin_dt = datetime.strptime(max_fin, "%Y-%m-%d").date()
                dias_restantes = max((fecha_fin_dt - hoy).days, 0)
            except ValueError:
                dias_restantes = 0

        item["en_carencia"] = en_carencia
        item["dias_restantes"] = dias_restantes
        item["fecha_fin_seguridad"] = max_fin

        if item["estado"] in ("Sembrado", "En Crecimiento"):
            total_lotes_activos += 1
            sup_cultivada_m2 += float(item.get("superficie_m2") or 0.0)

        lotes.append(item)

    # Tratamientos fitosanitarios con datos del cultivo
    cursor.execute("""
        SELECT t.*, p.lote_codigo, p.cultivo
        FROM tratamientos_fitosanitarios t
        JOIN produccion p ON t.lote_id = p.id
        ORDER BY t.fecha_tratamiento DESC, t.id DESC
    """)
    tratamientos = [dict(row) for row in cursor.fetchall()]

    # Fertilizaciones con datos del cultivo
    cursor.execute("""
        SELECT f.*, p.lote_codigo, p.cultivo
        FROM fertilizaciones f
        JOIN produccion p ON f.lote_id = p.id
        ORDER BY f.fecha_abonado DESC, f.id DESC
    """)
    fertilizaciones = [dict(row) for row in cursor.fetchall()]

    # Cosechas con datos del cultivo
    cursor.execute("""
        SELECT c.*, p.lote_codigo, p.cultivo
        FROM cosechas c
        JOIN produccion p ON c.lote_id = p.id
        ORDER BY c.fecha_cosecha DESC, c.id DESC
    """)
    cosechas = [dict(row) for row in cursor.fetchall()]

    # Métricas adicionales
    total_cosechas_kg = sum(c["cantidad_kg"] for c in cosechas)

    conn.close()

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "exp": exp,
            "lotes": lotes,
            "tratamientos": tratamientos,
            "fertilizaciones": fertilizaciones,
            "cosechas": cosechas,
            "stats": {
                "total_lotes_activos": total_lotes_activos,
                "total_en_carencia": total_en_carencia,
                "total_cosechas_kg": round(total_cosechas_kg, 2),
                "sup_cultivada_m2": round(sup_cultivada_m2, 1)
            },
            "cultivos_disponibles": CULTIVOS_TEMPORADA,
            "fecha_hoy": hoy_str,
            "active_tab": tab,
            "error_msg": error,
            "exito_msg": msg_exito
        }
    )


@app.post("/agregar-lote")
def agregar_lote(
    cultivo: str = Form(...),
    variedad: str = Form(""),
    cantidad: int = Form(...),
    superficie_m2: float = Form(50.0),
    fecha_siembra: str = Form(""),
    estado: str = Form("Sembrado")
):
    conn = get_db()
    try:
        # 1. Validación de guardia Pydantic
        lote_val = LoteCreate(
            cultivo=cultivo,
            variedad=variedad,
            cantidad=cantidad,
            superficie_m2=superficie_m2,
            fecha_siembra=fecha_siembra,
            estado=estado
        )

        # 2. Validación contextual con la base de datos
        cur = conn.cursor()
        cur.execute("SELECT sup_invernadero_m2 FROM explotacion WHERE id = 1")
        row = cur.fetchone()
        max_sup = row["sup_invernadero_m2"] if row else 10000.0

        if lote_val.superficie_m2 > max_sup:
            raise ValidacionError(
                f"La superficie asignada ({lote_val.superficie_m2} m²) supera la capacidad total del invernadero ({max_sup} m²).",
                tab="lotes"
            )

        temporada = CULTIVOS_TEMPORADA.get(lote_val.cultivo, "Todo el año")
        fecha_val = lote_val.fecha_siembra if lote_val.fecha_siembra else date.today().isoformat()
        
        # Generar código de lote identificativo conforme al estándar agrícola
        timestamp_sufijo = datetime.now().strftime("%y%m%d%H%M")
        cultivo_prefijo = "".join([c for c in lote_val.cultivo.upper() if c.isalnum()][:3])
        lote_codigo = f"GA-{cultivo_prefijo}-{timestamp_sufijo}"

        cur.execute("""
            INSERT INTO produccion (
                lote_codigo, cultivo, variedad, cantidad, superficie_m2,
                fecha_siembra, temporada, estado
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            lote_codigo, lote_val.cultivo, lote_val.variedad, lote_val.cantidad,
            lote_val.superficie_m2, fecha_val, temporada, lote_val.estado
        ))
        conn.commit()

        msg = f"Lote {lote_codigo} ({lote_val.cultivo}) validado por Pydantic y guardado con éxito."
        return RedirectResponse(url=f"/?tab=lotes&msg_exito={quote(msg)}", status_code=303)
    except ValidationError as e:
        return RedirectResponse(url=f"/?tab=lotes&error={quote(extraer_mensaje_pydantic(e))}", status_code=303)
    except ValidacionError as e:
        return RedirectResponse(url=f"/?tab={e.tab}&error={quote(e.mensaje)}", status_code=303)
    finally:
        conn.close()


@app.post("/actualizar-estado-lote")
def actualizar_estado_lote(lote_id: int = Form(...), estado: str = Form(...)):
    conn = get_db()
    try:
        if estado not in ("Sembrado", "En Crecimiento", "Cosechado", "Finalizado"):
            raise ValidacionError(f"Estado fenológico no reconocido: '{estado}'", tab="lotes")

        cursor = conn.cursor()
        cursor.execute("UPDATE produccion SET estado = ? WHERE id = ?", (estado, lote_id))
        conn.commit()
        msg = f"Estado del lote actualizado a '{estado}'."
        return RedirectResponse(url=f"/?tab=lotes&msg_exito={quote(msg)}", status_code=303)
    except ValidacionError as e:
        return RedirectResponse(url=f"/?tab={e.tab}&error={quote(e.mensaje)}", status_code=303)
    finally:
        conn.close()


@app.post("/agregar-tratamiento")
def agregar_tratamiento(
    lote_id: int = Form(...),
    fecha_tratamiento: str = Form(...),
    plaga_enfermedad: str = Form(...),
    producto_comercial: str = Form(...),
    num_registro_mapa: str = Form(...),
    materia_activa: str = Form(...),
    dosis: str = Form(...),
    volumen_caldo_l: float = Form(...),
    aplicador_nombre: str = Form(...),
    ropo_aplicador: str = Form(...),
    plazo_seguridad_dias: int = Form(0),
    observaciones: str = Form("")
):
    conn = get_db()
    try:
        # 1. Validación de guardia Pydantic
        trat_val = TratamientoFitosanitarioCreate(
            lote_id=lote_id,
            fecha_tratamiento=fecha_tratamiento,
            plaga_enfermedad=plaga_enfermedad,
            producto_comercial=producto_comercial,
            num_registro_mapa=num_registro_mapa,
            materia_activa=materia_activa,
            dosis=dosis,
            volumen_caldo_l=volumen_caldo_l,
            aplicador_nombre=aplicador_nombre,
            ropo_aplicador=ropo_aplicador,
            plazo_seguridad_dias=plazo_seguridad_dias,
            observaciones=observaciones
        )

        # 2. Validación contextual con la base de datos
        cur = conn.cursor()
        cur.execute("SELECT id, cultivo, lote_codigo, estado FROM produccion WHERE id = ?", (trat_val.lote_id,))
        lote = cur.fetchone()
        if not lote:
            raise ValidacionError("El lote seleccionado para el tratamiento no existe.", tab="fitosanitarios")
        if lote["estado"] == "Finalizado":
            raise ValidacionError(f"El lote '{lote['lote_codigo']}' ({lote['cultivo']}) ya está finalizado. No admite tratamientos.", tab="fitosanitarios")

        # Calcular fecha fin de plazo de seguridad (carencia)
        f_trat = datetime.strptime(trat_val.fecha_tratamiento, "%Y-%m-%d").date()
        f_fin = f_trat + timedelta(days=trat_val.plazo_seguridad_dias)
        fecha_fin_seguridad = f_fin.isoformat()

        cur.execute("""
            INSERT INTO tratamientos_fitosanitarios (
                lote_id, fecha_tratamiento, plaga_enfermedad, producto_comercial,
                num_registro_mapa, materia_activa, dosis, volumen_caldo_l,
                aplicador_nombre, ropo_aplicador, plazo_seguridad_dias,
                fecha_fin_seguridad, observaciones
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            trat_val.lote_id, trat_val.fecha_tratamiento, trat_val.plaga_enfermedad, trat_val.producto_comercial,
            trat_val.num_registro_mapa, trat_val.materia_activa, trat_val.dosis, trat_val.volumen_caldo_l,
            trat_val.aplicador_nombre, trat_val.ropo_aplicador, trat_val.plazo_seguridad_dias,
            fecha_fin_seguridad, trat_val.observaciones
        ))
        conn.commit()

        msg = f"Tratamiento verificado por Pydantic y registrado con éxito. Fin de carencia: {fecha_fin_seguridad}."
        return RedirectResponse(url=f"/?tab=fitosanitarios&msg_exito={quote(msg)}", status_code=303)
    except ValidationError as e:
        return RedirectResponse(url=f"/?tab=fitosanitarios&error={quote(extraer_mensaje_pydantic(e))}", status_code=303)
    except ValidacionError as e:
        return RedirectResponse(url=f"/?tab={e.tab}&error={quote(e.mensaje)}", status_code=303)
    finally:
        conn.close()


@app.post("/agregar-fertilizacion")
def agregar_fertilizacion(
    lote_id: int = Form(...),
    fecha_abonado: str = Form(...),
    tipo_fertilizante: str = Form(...),
    nombre_abono: str = Form(...),
    riqueza_npk: str = Form(""),
    dosis_kg_m2: float = Form(...),
    metodo_aplicacion: str = Form(...),
    observaciones: str = Form("")
):
    conn = get_db()
    try:
        # 1. Guardia Pydantic
        fert_val = FertilizacionCreate(
            lote_id=lote_id,
            fecha_abonado=fecha_abonado,
            tipo_fertilizante=tipo_fertilizante,
            nombre_abono=nombre_abono,
            riqueza_npk=riqueza_npk,
            dosis_kg_m2=dosis_kg_m2,
            metodo_aplicacion=metodo_aplicacion,
            observaciones=observaciones
        )

        # 2. Existencia del lote en BD
        cur = conn.cursor()
        cur.execute("SELECT id, lote_codigo FROM produccion WHERE id = ?", (fert_val.lote_id,))
        if not cur.fetchone():
            raise ValidacionError("El lote seleccionado para la fertilización no existe.", tab="fertilizacion")

        cur.execute("""
            INSERT INTO fertilizaciones (
                lote_id, fecha_abonado, tipo_fertilizante, nombre_abono,
                riqueza_npk, dosis_kg_m2, metodo_aplicacion, observaciones
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            fert_val.lote_id, fert_val.fecha_abonado, fert_val.tipo_fertilizante, fert_val.nombre_abono,
            fert_val.riqueza_npk, fert_val.dosis_kg_m2, fert_val.metodo_aplicacion, fert_val.observaciones
        ))
        conn.commit()

        msg = f"Abonado con {fert_val.nombre_abono} ({fert_val.dosis_kg_m2} kg/m²) validado y añadido al Plan de Fertilización."
        return RedirectResponse(url=f"/?tab=fertilizacion&msg_exito={quote(msg)}", status_code=303)
    except ValidationError as e:
        return RedirectResponse(url=f"/?tab=fertilizacion&error={quote(extraer_mensaje_pydantic(e))}", status_code=303)
    except ValidacionError as e:
        return RedirectResponse(url=f"/?tab={e.tab}&error={quote(e.mensaje)}", status_code=303)
    finally:
        conn.close()


@app.post("/agregar-cosecha")
def agregar_cosecha(
    lote_id: int = Form(...),
    fecha_cosecha: str = Form(...),
    cantidad_kg: float = Form(...),
    destino_comercial: str = Form(...),
    albaran_lote_salida: str = Form(...),
    observaciones: str = Form("")
):
    conn = get_db()
    try:
        # 1. Guardia Pydantic
        cosecha_val = CosechaCreate(
            lote_id=lote_id,
            fecha_cosecha=fecha_cosecha,
            cantidad_kg=cantidad_kg,
            destino_comercial=destino_comercial,
            albaran_lote_salida=albaran_lote_salida,
            observaciones=observaciones
        )

        cur = conn.cursor()
        cur.execute("SELECT id, cultivo, lote_codigo, estado FROM produccion WHERE id = ?", (cosecha_val.lote_id,))
        lote = cur.fetchone()
        if not lote:
            raise ValidacionError("El lote seleccionado para cosechar no existe.", tab="cosechas")
        if lote["estado"] == "Finalizado":
            raise ValidacionError(f"El lote '{lote['lote_codigo']}' ({lote['cultivo']}) ya está cerrado y finalizado.", tab="cosechas")

        # 2. Regla Crítica de Inocuidad: Bloqueo de Cosecha en Período de Carencia
        cur.execute("""
            SELECT MAX(fecha_fin_seguridad) as max_fin
            FROM tratamientos_fitosanitarios
            WHERE lote_id = ?
        """, (cosecha_val.lote_id,))
        res = cur.fetchone()
        max_fin = res["max_fin"] if res else None

        if max_fin and cosecha_val.fecha_cosecha < max_fin:
            hoy = date.today()
            try:
                f_fin_dt = datetime.strptime(max_fin, "%Y-%m-%d").date()
                dias_rest = max((f_fin_dt - hoy).days, 0)
            except ValueError:
                dias_rest = 0
            raise ValidacionError(
                f"BLOQUEO NORMATIVO DE INOCUIDAD: No se puede recolectar el lote '{lote['lote_codigo']}' ({lote['cultivo']}) el {cosecha_val.fecha_cosecha}. "
                f"El cultivo se encuentra bajo plazo de seguridad fitosanitario (carencia) obligatorio hasta el {max_fin} ({dias_rest} días restantes). "
                f"La recolección antes de dicha fecha infringe la normativa de residuos fitosanitarios de la Xunta de Galicia.",
                tab="cosechas"
            )

        cur.execute("""
            INSERT INTO cosechas (
                lote_id, fecha_cosecha, cantidad_kg, destino_comercial,
                albaran_lote_salida, plazo_respetado, observaciones
            ) VALUES (?, ?, ?, ?, ?, 1, ?)
        """, (
            cosecha_val.lote_id, cosecha_val.fecha_cosecha, cosecha_val.cantidad_kg, cosecha_val.destino_comercial,
            cosecha_val.albaran_lote_salida, cosecha_val.observaciones
        ))

        # Actualizar lote como Cosechado
        cur.execute("UPDATE produccion SET estado = 'Cosechado' WHERE id = ? AND estado != 'Finalizado'", (cosecha_val.lote_id,))

        conn.commit()
        msg = f"Cosecha de {cosecha_val.cantidad_kg} kg validada por Pydantic y registrada con albarán {cosecha_val.albaran_lote_salida}."
        return RedirectResponse(url=f"/?tab=cosechas&msg_exito={quote(msg)}", status_code=303)
    except ValidationError as e:
        return RedirectResponse(url=f"/?tab=cosechas&error={quote(extraer_mensaje_pydantic(e))}", status_code=303)
    except ValidacionError as e:
        return RedirectResponse(url=f"/?tab={e.tab}&error={quote(e.mensaje)}", status_code=303)
    finally:
        conn.close()


@app.post("/actualizar-explotacion")
def actualizar_explotacion(
    titular: str = Form(...),
    nif: str = Form(...),
    regepa: str = Form(...),
    ropo_titular: str = Form(...),
    provincia: str = Form(...),
    municipio: str = Form(...),
    parroquia: str = Form(""),
    poligono: int = Form(...),
    parcela: int = Form(...),
    recinto: int = Form(...),
    sup_invernadero_m2: float = Form(...),
    coordenadas_gps: str = Form("")
):
    conn = get_db()
    try:
        # 1. Guardia Pydantic
        exp_val = ExplotacionUpdate(
            titular=titular,
            nif=nif,
            regepa=regepa,
            ropo_titular=ropo_titular,
            provincia=provincia,
            municipio=municipio,
            parroquia=parroquia,
            poligono=poligono,
            parcela=parcela,
            recinto=recinto,
            sup_invernadero_m2=sup_invernadero_m2,
            coordenadas_gps=coordenadas_gps
        )

        cursor = conn.cursor()
        cursor.execute("""
            UPDATE explotacion SET
                titular = ?, nif = ?, regepa = ?, ropo_titular = ?,
                provincia = ?, municipio = ?, parroquia = ?, poligono = ?,
                parcela = ?, recinto = ?, sup_invernadero_m2 = ?, coordenadas_gps = ?
            WHERE id = 1
        """, (
            exp_val.titular, exp_val.nif, exp_val.regepa, exp_val.ropo_titular,
            exp_val.provincia, exp_val.municipio, exp_val.parroquia, exp_val.poligono,
            exp_val.parcela, exp_val.recinto, exp_val.sup_invernadero_m2, exp_val.coordenadas_gps
        ))
        conn.commit()
        msg = "Datos de ubicación e identificación de la explotación validados por Pydantic y actualizados con éxito."
        return RedirectResponse(url=f"/?tab=explotacion&msg_exito={quote(msg)}", status_code=303)
    except ValidationError as e:
        return RedirectResponse(url=f"/?tab=explotacion&error={quote(extraer_mensaje_pydantic(e))}", status_code=303)
    except ValidacionError as e:
        return RedirectResponse(url=f"/?tab={e.tab}&error={quote(e.mensaje)}", status_code=303)
    finally:
        conn.close()


@app.get("/libro-campo/imprimir", response_class=HTMLResponse)
def imprimir_libro_campo(request: Request):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM explotacion WHERE id = 1")
    exp = dict(cursor.fetchone())

    cursor.execute("""
        SELECT t.*, p.lote_codigo, p.cultivo
        FROM tratamientos_fitosanitarios t
        JOIN produccion p ON t.lote_id = p.id
        ORDER BY t.fecha_tratamiento ASC
    """)
    tratamientos = [dict(row) for row in cursor.fetchall()]

    cursor.execute("""
        SELECT f.*, p.lote_codigo, p.cultivo
        FROM fertilizaciones f
        JOIN produccion p ON f.lote_id = p.id
        ORDER BY f.fecha_abonado ASC
    """)
    fertilizaciones = [dict(row) for row in cursor.fetchall()]

    cursor.execute("""
        SELECT c.*, p.lote_codigo, p.cultivo
        FROM cosechas c
        JOIN produccion p ON c.lote_id = p.id
        ORDER BY c.fecha_cosecha ASC
    """)
    cosechas = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return templates.TemplateResponse(
        request=request,
        name="informe_oficial.html",
        context={
            "exp": exp,
            "tratamientos": tratamientos,
            "fertilizaciones": fertilizaciones,
            "cosechas": cosechas,
            "fecha_actual": date.today().strftime("%d/%m/%Y")
        }
    )
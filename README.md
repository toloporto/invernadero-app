# 🌱 Invernadero App • Libro de Campo Digital (Galicia / SIEX)

Aplicación web integral para la gestión técnica de invernaderos y la generación automatizada del **Cuaderno de Explotación Agrícola (Libro de Campo)** conforme a las directrices de la **Consellería do Medio Rural (Xunta de Galicia)** y la normativa estatal (**Real Decreto 1054/2022 - SIEX** y **Real Decreto 1051/2022**).

---

## 🚀 Características Principales

### 1. 📍 Ficha de Explotación y Ubicación SIGPAC Galicia
- Configuración libre de la ubicación territorial del invernadero: provincia (*A Coruña, Lugo, Ourense, Pontevedra*), concello, parroquia/lugar y coordenadas GPS.
- Registro catastral y agrario obligatorio: **Polígono, Parcela y Recinto SIGPAC**.
- Enlace directo al **Visor Oficial SixPac / SIGPAC** de la Xunta de Galicia para verificación cartográfica de recintos.
- Acreditación oficial del titular: **NIF/CIF, Código REGEPA/REGA y Carné de aplicador ROPO**.

### 2. 🥬 Gestión de Lotes y Cultivos Tradicionales
- Generación automática de **Códigos de Lote Trazables** (`GA-XXX-AAMMDDHHMM`).
- Catálogo adaptado al clima gallego: *Pemento de Padrón / Herbón, Tomate Negro de Santiago, Repollo Lorena, Xudía verde, Lechuga, Espinaca, Cilantro*.
- Seguimiento del ciclo fenológico (*Sembrado, En Crecimiento, Cosechado, Finalizado*).

### 3. 🛡️ Registro Oficial de Fitosanitarios (ROPO / MAPA)
- Registro de plagas justificadas en Gestión Integrada de Plagas (GIP).
- Datos requeridos por inspección: **Producto comercial, Nº Registro Oficial MAPA, Materia activa, Dosis autorizada, Volumen de caldo (L) y Aplicador acreditado con carné ROPO**.
- **Cálculo automático de la fecha de fin de plazo de seguridad (carencia)**.

### 4. ⛔ Control Estricto de Inocuidad Alimentaria
- **Semáforo de seguridad en tiempo real:** Indicadores de estado (*✓ Apto para Cosecha* vs *⛔ En Carencia con días restantes*).
- **Bloqueo normativo en backend:** El servidor rechaza cualquier intento de registrar una recolección en un lote cuyo plazo de seguridad fitosanitario no haya expirado, garantizando la inocuidad alimentaria y el cumplimiento legal.

### 5. 🌿 Plan de Fertilización Sostenible (RD 1051/2022)
- Registro de enmiendas orgánicas (compost gallego), fertirriego localizado por goteo, aportes N-P-K y pulverizaciones foliares.
- Prevención activa de lixiviación y contaminación de aguas subterráneas por nitratos mediante topes de dosificación por aplicación.

### 6. 📦 Trazabilidad de Cosechas y Salidas
- Control de cantidades recolectadas en kg/unidades.
- Asignación de albaranes de salida y registro del destino comercial (cooperativas, plazas de abastos, hostelería, venta directa).

### 7. 🖨️ Hoja Oficial Imprimible / Exportable a PDF
- Vista normalizada para inspección oficial disponible en `/libro-campo/imprimir`.
- Estilos de impresión optimizados (`@media print`) para guardar en PDF con un solo clic o imprimir en papel.

### 8. 👮 Validación con Pydantic v2 ("Guardia de Seguridad")
- Validación estricta de esquemas de datos antes de tocar SQLite (`Field(gt=0)`, `@field_validator`).
- Detección inmediata de cantidades negativas, dosis excesivas, fechas incoherentes o campos obligatorios vacíos.
- Retroalimentación amigable mediante banners visuales didácticos (verde para operaciones conformes, rojo con explicaciones de normativa en caso de rechazo).

### 9. 📲 App Instalable Multiplataforma (PWA & Desktop)
- **Cualquier plataforma:** Instalable en **Windows, macOS, Linux, Android e iOS** mediante tecnología Progressive Web App (PWA).
- **Ventana autónoma:** Se abre como una aplicación de escritorio nativa sin barras de navegador ni distracciones.
- **Lanzador 1-clic:** Incluye `iniciar_app.bat` para Windows y `iniciar_app.sh` para Linux/macOS.
- **Acceso rápido:** Botón `📲 Instalar App` integrado en la barra de navegación.

---

## 🛠️ Tecnologías Utilizadas

- **Backend:** [FastAPI](https://fastapi.tiangolo.com/) (Python 3.12+)
- **Validación de Datos:** [Pydantic v2](https://docs.pydantic.dev/)
- **Servidor ASGI:** [Uvicorn](https://www.uvicorn.org/)
- **Base de Datos:** [SQLite3](https://www.sqlite.org/) (con migraciones automáticas)
- **Motor de Plantillas:** [Jinja2](https://jinja.palletsprojects.com/)
- **Frontend & Estilos:** [Tailwind CSS](https://tailwindcss.com/) (CDN) con paleta personalizada *slate/emerald* en modo oscuro
- **Interactividad UI:** [Alpine.js](https://alpinejs.dev/)
- **Arquitectura PWA:** Service Worker (`sw.js`), Web App Manifest (`manifest.json`) e Iconografía adaptable

---

## 📂 Estructura del Proyecto

```text
invernadero-app/
│
├── main.py                     # Servidor FastAPI, modelos Pydantic, endpoints y lógica de negocio
├── desktop_launcher.py          # Lanzador de escritorio en ventana nativa independiente
├── iniciar_app.bat              # Acceso directo para Windows (doble clic para ejecutar)
├── iniciar_app.sh               # Lanzador para Linux y macOS
├── invernadero.db              # Base de datos SQLite (explotacion, produccion, tratamientos, fertilizaciones, cosechas)
│
├── static/
│   ├── manifest.json            # Metadatos PWA (nombre, tema, iconos, display: standalone)
│   ├── sw.js                    # Service Worker (caché offline y ciclo de vida de instalación)
│   └── icons/
│       ├── icon-192.png         # Icono para móviles y tablets (192x192)
│       └── icon-512.png         # Icono en alta resolución para escritorio (512x512)
│
├── templates/
│   ├── index.html              # Dashboard interactivo con pestañas, KPIs, formularios y banners de validación
│   └── informe_oficial.html    # Plantilla imprimible normalizada del Cuaderno de Explotación de Galicia
│
├── MANUAL_USUARIO.md           # Manual de usuario paso a paso con capturas y guía didáctica
├── requirements.txt            # Dependencias del proyecto Python
└── README.md                   # Documentación general técnica y legal del proyecto
```

---

## ⚙️ Instalación y Puesta en Marcha

### Prerrequisitos
- Python 3.10 o superior (recomendado Python 3.12).
- PowerShell (Windows) o Bash (Linux / macOS).

### 1. Clonar o acceder al directorio del proyecto
```powershell
cd c:\Users\antol\MisProyectos\invernadero-app
```

### 2. Crear y activar el entorno virtual (`.venv`)

**En Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

**En Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependencias
```powershell
pip install fastapi uvicorn python-multipart jinja2 pydantic
```

### 4. Iniciar el servidor de desarrollo
```powershell
uvicorn main:app --reload
```

El servidor quedará disponible en:
👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 📖 Guía Rápida de Uso

1. **Configurar Ubicación:** Haz clic en el botón `📍 Cambiar Ubicación` en la barra superior o ve a la pestaña **📋 Ficha Explotación & SIGPAC** para indicar tu concello gallego, polígono y parcela SIGPAC.
2. **Registrar Lotes:** En la pestaña **🥬 Lotes & Cultivos**, pulsa `+ Nuevo Lote` para dar de alta un cultivo (ej. Pemento de Padrón, Tomate Negro).
3. **Anotar Fitosanitarios:** En **🛡️ Fitosanitarios**, registra los tratamientos con su número de registro MAPA y días de carencia.
4. **Verificar Carencias:** En la lista de lotes, comprueba si el lote está en período de seguridad (`⛔ EN CARENCIA`) o listo para recolección (`✓ APTO PARA COSECHA`).
5. **Registrar Cosechas:** En **📦 Cosechas & Trazabilidad**, registra las salidas de producto con su albarán. Si el cultivo está en carencia, el sistema te advertirá y bloqueará la recolección ilegal.
6. **Emitir Libro Oficial:** Haz clic en **🖨️ Libro de Campo Oficial (PDF)** para obtener el informe consolidado para inspección.

---

## ⚖️ Marco Normativo de Referencia

- **Real Decreto 1054/2022:** Regula el Sistema de Información de Explotaciones Agrícolas y Ganaderas y de la Producción Agraria (SIEX) y el Cuaderno Digital de Explotación Agrícola (CUE).
- **Real Decreto 1051/2022:** Establece las normas para la nutrición sostenible en los suelos agrarios y protección de aguas contra la contaminación por nitratos.
- **Real Decreto 1311/2012:** Marco de actuación para conseguir un uso sostenible de los productos fitosanitarios y Registro Oficial de Productores y Operadores (ROPO).
- **Directrices de la Consellería do Medio Rural:** Xunta de Galicia.

---

## 📄 Licencia

Proyecto desarrollado para fines formativos y de gestión técnica agrícola. Distribuido bajo licencia MIT.

# 📘 Manual de Usuario • Sistema de Invernadero y Libro de Campo Digital (Galicia)

Bienvenido/a al manual de usuario de la **Aplicación de Gestión de Invernadero y Cuaderno de Explotación Agrícola (Libro de Campo)**. 

Esta herramienta ha sido diseñada específicamente para agricultores, gestores de explotaciones y técnicos de invernadero en la **Comunidad Autónoma de Galicia**, facilitando el registro diario de labores y garantizando el cumplimiento de la normativa autonómica (*Consellería do Medio Rural*) y estatal (*SIEX - Real Decreto 1054/2022 y Real Decreto 1051/2022*).

---

## 📑 Índice de Contenidos

1. [Primeros Pasos y Acceso](#1-primeros-pasos-y-acceso)
2. [Estructura del Panel Principal](#2-estructura-del-panel-principal)
3. [Módulo 1: Configuración de la Explotación y SIGPAC](#3-módulo-1-configuración-de-la-explotación-y-sigpac)
4. [Módulo 2: Gestión de Lotes y Cultivos](#4-módulo-2-gestión-de-lotes-y-cultivos)
5. [Módulo 3: Cuaderno Fitosanitario y Control de Carencias](#5-módulo-3-cuaderno-fitosanitario-y-control-de-carencias)
6. [Módulo 4: Plan de Fertilización Sostenible](#6-módulo-4-plan-de-fertilización-sostenible)
7. [Módulo 5: Cosechas y Trazabilidad Comercial](#7-módulo-5-cosechas-y-trazabilidad-comercial)
8. [Módulo 6: Generación del Libro Oficial para Inspección (PDF)](#8-módulo-6-generación-del-libro-oficial-para-inspección-pdf)
9. [Módulo 7: Mensajes de Validación y Seguridad (Pydantic)](#9-módulo-7-mensajes-de-validación-y-seguridad-pydantic)
10. [Preguntas Frecuentes (FAQ)](#10-preguntas-frecuentes-faq)

---

## 1. Primeros Pasos y Acceso

### ¿Cómo acceder a la aplicación web?
1. Abre tu navegador web habitual (Google Chrome, Microsoft Edge, Firefox o Safari).
2. Escribe en la barra de direcciones:
   ```text
   http://127.0.0.1:8000
   ```
   *(o `http://localhost:8000`)*
3. Pulsa **Enter**. Verás la pantalla principal del panel en modo oscuro optimizado para trabajo en campo o despacho.

---

### 📲 ¿Cómo descargar e instalar la aplicación en cualquier dispositivo?

La aplicación está construida con tecnología **PWA (Progressive Web App)**, lo que permite instalarla como una aplicación nativa en cualquier sistema operativo:

#### 🖥️ En Windows / PC:
- **Opción A (Instalación PWA desde el navegador):** Haz clic en el botón superior **`📲 Instalar App`** (o en el icono de instalación con forma de monitor/pantalla situado a la derecha de la barra de direcciones de Edge/Chrome). La app se instalará en tu sistema, creará un icono en el Escritorio y en el Menú Inicio, y se abrirá en una ventana limpia e independiente sin barras de navegador.
- **Opción B (Lanzador directo de escritorio):** Haz doble clic en el archivo **`iniciar_app.bat`** incluido en la carpeta del proyecto. Se abrirá automáticamente como una aplicación de escritorio nativa.

#### 🍎 En macOS / Mac:
- Abre la aplicación en Google Chrome, Edge o Safari.
- Pulsa el botón **`📲 Instalar App`** o en el menú del navegador selecciona **"Instalar Invernadero Galego..."**.
- La aplicación se añadirá al **Dock**, al **Launchpad** y a tu carpeta de **Aplicaciones**.

#### 📱 En Android (Móviles y Tablets):
- Abre la aplicación en Google Chrome.
- Pulsa el botón **`📲 Instalar App`** en la cabecera (o pulsa los tres puntos `⋮` de Chrome y elige **"Instalar aplicación"** / **"Añadir a la pantalla de inicio"**).
- Se creará el icono de Invernadero en la pantalla de tu móvil y funcionará a pantalla completa como cualquier app descargada de Google Play.

#### 🍏 En iOS (iPhone y iPad):
- Abre la aplicación en el navegador **Safari**.
- Pulsa el botón **Compartir** (el icono cuadrado con una flecha hacia arriba en la barra inferior).
- Desplázate hacia abajo y selecciona **"Añadir a la pantalla de inicio"** (`Add to Home Screen`).
- Pulsa **Añadir**. Tendrás la app en tu pantalla con su icono oficial.

---

## 2. Estructura del Panel Principal

El panel se organiza en cuatro zonas clave:

```
┌────────────────────────────────────────────────────────────────────────┐
│ [🌱 Invernadero Galego]  Titular • REGEPA • [📍 Betanzos (Cambiar)]   │ ← Barra Superior
├────────────────────────────────────────────────────────────────────────┤
│ [📊 Lotes: 3]  [🛡️ Carencia: 1]  [🧺 Cosechados: 120 kg]  [🏡 850 m²] │ ← Tarjetas KPI
├────────────────────────────────────────────────────────────────────────┤
│ [🥬 Lotes] [🛡️ Fitosanitarios] [🌿 Fertilización] [📦 Cosechas] [📋 SIGPAC] ← Pestañas
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│                CONTENIDO DE LA PESTAÑA ACTIVA                          │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

- **Barra Superior:** Muestra de un vistazo el nombre de la explotación, el número REGEPA y la ubicación geográfica activa. Incluye el acceso directo a la hoja oficial de inspección.
- **Tarjetas de Estado (KPIs):** Resumen visual de lotes activos, cuántos lotes se encuentran actualmente bajo período de carencia, kg cosechados y superficie total cubierta.
- **Pestañas temáticas:** Permiten alternar al instante entre las labores de cultivo, fitosanitarios, abonado, recolección y datos de la finca.

---

## 3. Módulo 1: Configuración de la Explotación y SIGPAC

> **¿Por qué es importante?**  
> En Galicia, cualquier tratamiento o lote debe estar estrictamente vinculado a una referencia catastral SIGPAC y a una explotación inscrita en el REGEPA.

### Cómo configurar o cambiar la ubicación:
1. Haz clic en el botón superior **`📍 [Municipio] (Cambiar Ubicación)`** o ve a la pestaña **`📋 Ficha Explotación & SIGPAC`**.
2. Completa los dos bloques del formulario:
   - **Bloque 1: Ubicación Territorial y SIGPAC:**
     - **Provincia:** Selecciona tu provincia (*A Coruña, Lugo, Ourense, Pontevedra* u otra).
     - **Municipio / Concello:** Escribe tu concello gallego (dispones de sugerencias automáticas).
     - **Parroquia / Lugar:** Añade la parroquia rural o aldea si aplica (ej. *Herbón, Goián, Aríns*).
     - **Polígono, Parcela y Recinto:** Números oficiales de tu parcela agrícola.
     - *(Opcional)* Haz clic en **`🗺️ Abrir Visor SIGPAC / SixPac Galicia ↗`** si necesitas localizar tu parcela exacta sobre el mapa satelital de la Xunta de Galicia.
   - **Bloque 2: Acreditación Oficial del Titular:**
     - Nombre o Razón Social del titular.
     - NIF o CIF.
     - Código oficial de inscripción **REGEPA / REGA** (ej. `ES-GA-15003429`).
     - Número de carné oficial **ROPO** del titular o asesor técnico GIP.
     - Superficie cubierta total del invernadero en m².
3. Pulsa **`💾 Guardar Ubicación y Datos de Explotación`**. La información se actualizará de inmediato en toda la aplicación y en el informe oficial.

---

## 4. Módulo 2: Gestión de Lotes y Cultivos

En la pestaña **`🥬 Lotes & Cultivos`** se gestionan las siembras y el ciclo de vida de cada cultivo.

### Cómo registrar un nuevo lote:
1. Pulsa el botón verde **`+ Nuevo Lote`**.
2. Rellena los datos solicitados:
   - **Cultivo:** Selecciona una de las variedades tradicionales adaptadas (*Pemento de Padrón, Tomate Negro de Santiago, Lechuga, Repollo Lorena, Espinaca, Xudía verde, Cilantro*).
   - **Variedad:** Especifica la selección (ej. *D.O.P. Herbón, Selección Santiago, etc.*).
   - **Plantas / Semillas:** Cantidad sembrada o trasplantada (debe ser mayor que 0).
   - **Superficie (m²):** Espacio del invernadero ocupado por este lote (no puede superar la superficie total del invernadero).
   - **Fecha de siembra:** Fecha de inicio de la plantación.
3. Haz clic en **`Guardar Lote de Cultivo`**.

### Código de Lote Automático:
El sistema generará automáticamente un código único de trazabilidad (ej. `GA-PEM-2610161830`), compuesto por:
- Prefijo autonómico: `GA-`
- Abreviatura del cultivo: `PEM-` (Pemento)
- Marca temporal: Año, mes, día, hora y minuto.

### Actualizar el Estado Fenológico:
En la columna **Acción** de cada fila, puedes cambiar el estado del lote en cualquier momento desplegando el selector:
- `Sembrado`: Fase de germinación inicial o trasplante.
- `En Crecimiento`: Fase vegetativa y desarrollo de masa foliar/floración.
- `Cosechado`: Fase productiva de recolección de fruto.
- `Finalizado`: Fin del ciclo y retirada del cultivo.

---

## 5. Módulo 3: Cuaderno Fitosanitario y Control de Carencias

El uso de productos fitosanitarios está estrictamente regulado para garantizar la seguridad del aplicador, el medio ambiente y los consumidores.

### Registrar un tratamiento oficial:
1. Dirígete a la pestaña **`🛡️ Fitosanitarios (ROPO/MAPA)`**.
2. Pulsa **`+ Registrar Tratamiento`**.
3. Cumplimenta los datos técnicos:
   - **Lote Destino:** Selecciona el cultivo sobre el que se aplica.
   - **Fecha de Aplicación:** Fecha en la que se efectuó el tratamiento (no puede ser futura).
   - **Plaga o Enfermedad Justificada:** Motivo técnico según Gestión Integrada de Plagas (ej. *Oídio, Mildiu, Mosca blanca, Trips, Pulgón*).
   - **Producto Comercial y Nº Registro MAPA:** Nombre comercial y código de homologación en el Ministerio de Agricultura (ej. `ES-00124`).
   - **Materia Activa:** Principio activo autorizado (ej. *Azufre 80%, Azadiractina 1%*).
   - **Dosis y Volumen de Caldo:** Dosis autorizada por etiqueta y litros totales aplicados en el invernadero.
   - **Aplicador y Nº ROPO:** Nombre del operario y su carné de manipulador oficial.
   - **Plazo de Seguridad (Días):** Días de carencia obligatorios según la ficha técnica del producto.
4. Pulsa **`Registrar Tratamiento Oficial`**.

### 🚦 El Semáforo de Seguridad (Carencia):
El sistema calculará automáticamente la **Fecha de Fin de Seguridad**:
- Si la fecha límite aún no ha pasado: El lote se marcará con **`⛔ EN CARENCIA`**, indicando los días restantes.
- Si la fecha límite ya ha expirado o no tiene tratamientos: El lote se mostrará con **`✓ APTO PARA COSECHA`**.

---

## 6. Módulo 4: Plan de Fertilización Sostenible

Conforme al **Real Decreto 1051/2022**, las explotaciones deben registrar sus aportes nutricionales para evitar la lixiviación y contaminación de acuíferos en Galicia.

### Añadir una aplicación de abono o enmienda:
1. Entra en la pestaña **`🌿 Fertilización Sostenible`**.
2. Pulsa **`+ Registrar Abonado`**.
3. Indica:
   - **Lote Destino** y **Fecha de Aplicación**.
   - **Tipo de Fertilizante:** Abono orgánico/compost gallego, fertirrigación soluble N-P-K, abono foliar bioestimulante o enmienda cálcica.
   - **Nombre comercial o procedencia:** Ej. *Compost vegetal maduro*.
   - **Riqueza N-P-K declarada:** Relación nutricional (ej. `3-2-2` o `14-7-28`).
   - **Dosis:** Cantidad en kg o litros por m² (el sistema limita aportes superiores a 10 kg/m² por seguridad ambiental).
   - **Método:** Fertirriego por goteo localizado, incorporación a suelo o pulverización foliar.
4. Pulsa **`Guardar Registro de Fertilización`**.

---

## 7. Módulo 5: Cosechas y Trazabilidad Comercial

Este módulo vincula la producción obtenida con el mercado y garantiza la seguridad alimentaria.

### Registrar una cosecha:
1. Ve a la pestaña **`📦 Cosechas & Trazabilidad`**.
2. Pulsa **`+ Registrar Recolección`**.
3. Selecciona el **Lote a Cosechar**, la **Fecha**, los **Kg recolectados**, el **Albarán de salida** y el **Destino comercial** (cooperativa, restaurante, mercado de abastos o venta directa).
4. Pulsa **`Guardar Registro de Cosecha`**.

### ⛔ ¿Qué ocurre si intentas cosechar un lote en período de carencia?
Si un lote ha recibido un tratamiento fitosanitario y aún no ha vencido su plazo de seguridad, **el servidor bloqueará la recolección de forma preventiva** y mostrará un aviso:

> **⛔ BLOQUEO NORMATIVO DE INOCUIDAD:**  
> *No se puede recolectar el lote porque se encuentra bajo plazo de seguridad obligatorio hasta el [Fecha]. Faltan X días para cumplir el plazo de seguridad legal.*

Esta validación previene infracciones graves ante la inspección de Sanidad Vegetal y garantiza que ningún producto con residuos llegue al consumidor.

---

## 8. Módulo 6: Generación del Libro Oficial para Inspección (PDF)

Para presentar el cuaderno ante una inspección de la **Consellería do Medio Rural** o auditorías de calidad (GlobalGAP, Producción Ecológica CRAEGA):

1. En la barra superior, haz clic en el botón verde:  
   **`🖨️ Libro de Campo Oficial (PDF)`**
2. Se abrirá una nueva ventana con la plantilla oficial normalizada, que contiene:
   - **Encabezado oficial:** Comunidad Autónoma de Galicia y referencias normativas.
   - **Sección 1:** Datos de la explotación, titular, códigos REGEPA/ROPO y referencias SIGPAC.
   - **Sección 2:** Registro cronológico de tratamientos fitosanitarios con materias activas y plazos.
   - **Sección 3:** Registro del plan de fertilización sostenible.
   - **Sección 4:** Trazabilidad de cosechas y salidas comerciales.
   - **Firma y Declaración de Veracidad:** Recuadro legal para la firma del titular o asesor GIP.
3. Pulsa el botón **`🖨️ Imprimir / Guardar en PDF`** para guardarlo como archivo digital o imprimirlo en papel.

---

## 9. Módulo 7: Mensajes de Validación y Seguridad (Pydantic)

La aplicación cuenta con **Pydantic v2** como guardia de seguridad. Si introduces algún dato erróneo, verás un banner rojo en la parte superior del panel explicando el motivo:

| Error común | Causa del rechazo | Solución |
|---|---|---|
| **Cantidad $\le 0$** | Se introdujo un número negativo o cero en plantas o kg. | Introduce un valor mayor que 0. |
| **Superficie mayor al invernadero** | El lote supera los m² totales de la finca. | Revisa los m² del lote o amplía la superficie en la Ficha de Explotación. |
| **Nº Registro MAPA corto o vacío** | Obligatorio por normativa fitosanitaria comunitaria. | Especifica el código de registro oficial que figura en la etiqueta del producto. |
| **Plazo de seguridad negativo** | No existen plazos de carencia menores a 0 días. | Escribe `0` si el producto está exento de plazo (ej. extractos biológicos) o los días correspondientes. |
| **Fecha futura de tratamiento** | El cuaderno exige anotar labores ya ejecutadas. | Indica la fecha de hoy o una fecha pasada en la que se aplicó el producto. |
| **Dosis de abono $> 10\text{ kg/m}^2$** | Alerta agronómica contra lixiviación de nitratos. | Fracciona la aplicación en varias tandas sostenibles. |

Cuando la operación es correcta, aparecerá un **banner verde** confirmando que los datos han sido guardados conforme a la normativa.

---

## 10. Preguntas Frecuentes (FAQ)

### ¿Se pierden los datos al apagar el ordenador?
No. Todos los datos se almacenan de forma persistente en la base de datos local `invernadero.db` de tu equipo.

### ¿Puedo registrar más de una provincia o concello?
El invernadero principal se configura en la pestaña de explotación. Si gestionas invernaderos en distintas parcelas, puedes actualizar las referencias SIGPAC correspondientes a cada campaña.

### ¿Puedo utilizar la aplicación sin conexión a Internet?
Sí. El servidor FastAPI y la base de datos SQLite funcionan 100% en local en tu ordenador sin necesidad de conexión externa para almacenar tus datos.

### ¿Qué navegador es el más recomendado?
Cualquier navegador moderno es compatible. Para exportar a PDF con estilos limpios, recomendamos **Google Chrome**, **Microsoft Edge** o **Mozilla Firefox**.

---

*Manual elaborado conforme a las directrices de la Consellería do Medio Rural (Xunta de Galicia) y la normativa SIEX (Real Decreto 1054/2022).*

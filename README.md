# 🛠️ Convertir JSON Vectorizado a STL + Procesamiento de Imagen (2D a 3D)

Este proyecto es una aplicación Flask que convierte imágenes 2D en modelos 3D STL completos, permitiendo un flujo completo desde la imagen original hasta la creación del archivo STL, incluyendo preprocesamiento, limpieza, vectorización y generación STL. Todo el proceso se realiza vía API.

---

## 🚀 Características principales

- ✅ **Preprocesamiento de imágenes:** Binarización extrema (fondo blanco, trazos negros).
- ✅ **Limpieza morfológica:** Apertura, cierre y filtrado de contornos pequeños.
- ✅ **Vectorización:** Conversión de contornos en datos JSON (`vector_paths`).
- ✅ **Generación de STL:** Extrusión y exportación a archivo STL descargable.

---

## ⚙️ Instalación local

1️⃣ Clonar el repositorio:

```bash
git clone https://github.com/uptobe8/convertir-json-a-stl.git
cd convertir-json-a-stl
```

2️⃣ Crear un entorno virtual (opcional pero recomendado):

```bash
python3 -m venv venv
source venv/bin/activate
```

3️⃣ Instalar dependencias:

```bash
pip install -r requirements.txt
```

🚦 **Uso local**

1️⃣ Levantar el servidor:

```bash
python app.py
```

---

## 🌐 Endpoints API

1️⃣ **POST /procesar-imagen**  
_Preprocesa una imagen a blanco y negro binario para posterior limpieza/vectorización._

**Input (multipart/form-data):**

| Campo  | Tipo   | Descripción                                |
|--------|--------|--------------------------------------------|
| imagen | Binary | Imagen original (por ejemplo, PNG o JPG). |

**Output:**

- Código 200: Imagen binaria (image/png).

---

2️⃣ **POST /limpiar**  
_Limpia una imagen binaria para optimizar la extracción de contornos._

**Input (multipart/form-data):**

| Campo  | Tipo   | Descripción                                            |
|--------|--------|--------------------------------------------------------|
| imagen | Binary | Imagen binaria resultante del preprocesamiento.        |

**Output:**

- Código 200: Imagen limpia (image/png).

---

3️⃣ **POST /vectorizar-contornos**  
_Vectoriza los contornos detectados y devuelve los datos en formato JSON._

**Input (application/json):**

| Campo               | Tipo   | Descripción                                                |
|---------------------|--------|------------------------------------------------------------|
| ruta_imagen_binaria | String | Ruta absoluta/relativa de la imagen binaria limpia a procesar. |

**Output:**

- Código 200: JSON con vector_paths.

---

4️⃣ **POST /convertir-json-a-stl**  
_Convierte un JSON vectorizado a un archivo STL descargable._

**Input (application/json):**

| Campo        | Tipo   | Descripción                                                |
|--------------|--------|------------------------------------------------------------|
| vector_file  | String | Ruta del archivo JSON vectorizado.                         |
| output_file  | String | Nombre del archivo STL a generar.                          |
| options      | Object | (Opcional) Escala, rotación, suavizado, export format.     |

**Output:**

- Código 200: STL generado (application/octet-stream).

---

## 🖥️ Ejemplo de uso (cURL)

1️⃣ Preprocesar imagen:

```bash
curl -X POST -F "imagen=@/ruta/a/tu/imagen.png" http://localhost:5000/procesar-imagen -o preprocessed.png
```

2️⃣ Limpiar imagen:

```bash
curl -X POST -F "imagen=@preprocessed.png" http://localhost:5000/limpiar -o cleaned.png
```

3️⃣ Vectorizar contornos:

```bash
curl -X POST -H "Content-Type: application/json" -d '{"ruta_imagen_binaria": "/ruta/cleaned.png"}' http://localhost:5000/vectorizar-contornos
```

4️⃣ Generar STL:

```bash
curl -X POST -H "Content-Type: application/json" \
-d '{"vector_file": "/ruta/vector_paths.json", "output_file": "output.stl", "options": {"scale": 1.0}}' \
http://localhost:5000/convertir-json-a-stl -o output.stl
```

---

## 🚀 Despliegue en OnRender (producción)

Para ejecutar esta aplicación en producción (OnRender u otro proveedor cloud), sigue estos pasos adicionales:

1️⃣ **Procfile**  
Crea un archivo llamado `Procfile` (sin extensión) con este contenido:

```
web: gunicorn app:app --bind 0.0.0.0:$PORT
```

2️⃣ **Modificar `app.py`**  
Asegúrate de que al final de `app.py` esté este bloque para usar el puerto dinámico:

```python
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
```

3️⃣ **Requisitos (`requirements.txt`)**  
Asegúrate de incluir `gunicorn` y `opencv-python` en el archivo `requirements.txt`.

4️⃣ **Desplegar en OnRender**  
- Sube el proyecto a GitHub (si no lo tienes).
- Conecta el repositorio a OnRender.
- Selecciona `Deploy` y la app debería arrancar en producción automáticamente.

---

## 📦 Dependencias

- Flask
- numpy
- numpy-stl
- scipy
- opencv-python
- gunicorn

---

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo LICENSE para más detalles.

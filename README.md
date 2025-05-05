# 🛠️ Convertir JSON Vectorizado a STL + Procesamiento de Imagen (2D a 3D)

Este proyecto es una aplicación Flask que convierte imágenes 2D en modelos 3D STL completos, permitiendo un flujo completo desde la imagen original hasta la creación del archivo STL, incluyendo preprocesamiento, limpieza, vectorización y generación STL. Todo el proceso se realiza vía API.

---

## 🚀 Características principales

- ✅ **Preprocesamiento de imágenes:** Binarización extrema (fondo blanco, trazos negros).
- ✅ **Limpieza morfológica:** Apertura, cierre y filtrado de contornos pequeños.
- ✅ **Vectorización:** Conversión de contornos en datos JSON (`vector_paths`).
- ✅ **Generación de STL:** Extrusión y exportación a archivo STL descargable.

---

## ⚙️ Instalación

1️⃣ Clonar el repositorio:

```bash
git clone https://github.com/uptobe8/convertir-json-a-stl.git
cd convertir-json-a-stl
2️⃣ Crear un entorno virtual (opcional pero recomendado):


python3 -m venv venv
source venv/bin/activate
3️⃣ Instalar dependencias:

pip install -r requirements.txt
🚦 Uso
1️⃣ Levantar el servidor:


python app.py
🌐 Endpoints API
1️⃣ POST /procesar-imagen
Descripción:
Preprocesa una imagen a blanco y negro binario para posterior limpieza/vectorización.

Input (multipart/form-data):

Campo	Tipo	Descripción
imagen	Binary	Imagen original (por ejemplo, PNG o JPG).

Output:

Código 200: Imagen binaria (image/png).

2️⃣ POST /limpiar
Descripción:
Limpia una imagen binaria para optimizar la extracción de contornos.

Input (multipart/form-data):

Campo	Tipo	Descripción
imagen	Binary	Imagen binaria resultante del preprocesamiento.

Output:

Código 200: Imagen limpia (image/png).

3️⃣ POST /vectorizar-contornos
Descripción:
Vectoriza los contornos detectados y devuelve los datos en formato JSON.

Input (application/json):

Campo	Tipo	Descripción
ruta_imagen_binaria	String	Ruta absoluta/relativa de la imagen binaria limpia a procesar.

Output:

Código 200: JSON con vector_paths.

4️⃣ POST /convertir-json-a-stl
Descripción:
Convierte un JSON vectorizado a un archivo STL descargable.

Input (application/json):

Campo	Tipo	Descripción
vector_file	String	Ruta del archivo JSON vectorizado.
output_file	String	Nombre del archivo STL a generar.
options	Object	(Opcional) Escala, rotación, suavizado, export format.

Output:

Código 200: STL generado (application/octet-stream).

🖥️ Ejemplo de uso (cURL)
1️⃣ Preprocesar imagen:


curl -X POST -F "imagen=@/ruta/a/tu/imagen.png" http://localhost:5000/procesar-imagen -o preprocessed.png
2️⃣ Limpiar imagen:


curl -X POST -F "imagen=@preprocessed.png" http://localhost:5000/limpiar -o cleaned.png
3️⃣ Vectorizar contornos:


curl -X POST -H "Content-Type: application/json" -d '{"ruta_imagen_binaria": "/ruta/cleaned.png"}' http://localhost:5000/vectorizar-contornos
4️⃣ Generar STL:


curl -X POST -H "Content-Type: application/json" \
-d '{"vector_file": "/ruta/vector_paths.json", "output_file": "output.stl", "options": {"scale": 1.0}}' \
http://localhost:5000/convertir-json-a-stl -o output.stl
📦 Dependencias
Flask
numpy
numpy-stl
scipy
opencv-python

📄 Licencia
Este proyecto está bajo la licencia MIT. Consulta el archivo LICENSE para más detalles.

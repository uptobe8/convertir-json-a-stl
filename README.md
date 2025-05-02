# Generador de Archivos STL desde JSON

Este proyecto permite convertir un archivo JSON en un archivo STL que puede ser usado para impresión 3D. 

## Requisitos
1. Python 3 instalado.
2. Instalar las dependencias necesarias (ver pasos abajo).

## Instalación
1. Clona el repositorio o descarga estos archivos.
2. Abre una terminal en la carpeta donde están los archivos.
3. Instala las dependencias ejecutando:
   ```bash
   pip install -r requirements.txt
   ```

## Uso
Ejecuta el script `app.py` con la siguiente estructura:
```bash
python app.py <archivo_json> <archivo_salida_stl>
```
Por ejemplo:
```bash
python app.py modelo.json modelo.stl
```

### Formato del JSON
El archivo JSON debe tener la siguiente estructura:
```json
{
  "vertices": [
    [0, 0, 0],
    [1, 0, 0],
    [0, 1, 0],
    [0, 0, 1]
  ],
  "faces": [
    [0, 1, 2],
    [0, 1, 3]
  ]
}
```

- `vertices`: Lista de puntos en 3D (x, y, z).
- `faces`: Lista de triángulos, donde cada triángulo es definido por índices de los vértices.

## Notas
- El archivo STL será generado en el mismo directorio desde donde ejecutes el script.
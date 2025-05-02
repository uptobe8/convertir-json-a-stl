# Convertir JSON Vectorizado en STL

Este proyecto permite convertir un archivo JSON que contiene datos de vértices y caras en un archivo STL para impresión 3D. Ahora incluye funcionalidades avanzadas para personalizar y mejorar los modelos generados.

## Requisitos
1. Python 3 instalado.
2. Instalar las dependencias necesarias (ver pasos abajo).

## Instalación
1. Clonar este repositorio:
   ```bash
   git clone https://github.com/uptobe8/convertir-json-a-stl.git
   cd convertir-json-a-stl
   ```
2. Instalar las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Uso
Ejecuta el script `app.py` con la siguiente estructura:
```bash
python app.py <archivo_json> <archivo_salida_stl> [opciones]
```

Por ejemplo:
```bash
python app.py modelo.json modelo.stl --scale 2.0 --rotate 45 z --smooth 3 --export obj
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

## Funcionalidades Avanzadas
Este script incluye las siguientes opciones avanzadas para personalizar la generación de modelos STL:

1. **Escalado**: Escalar el modelo con la opción `--scale <factor>`.
   - Ejemplo: `--scale 2.0` duplica el tamaño del modelo.

2. **Rotación**: Rotar el modelo con la opción `--rotate <angle> <axis>`.
   - Ejemplo: `--rotate 45 z` rota el modelo 45 grados alrededor del eje Z.

3. **Suavizado**: Suavizar la malla para eliminar bordes duros con `--smooth <iterations>`.
   - Ejemplo: `--smooth 3` aplica tres iteraciones de suavizado.

4. **Generación de Soportes**: (Próximamente) Generar soportes básicos para impresión 3D.

5. **Exportación a Otros Formatos**: Exportar el modelo a formatos como OBJ o PLY con `--export <format>`.
   - Ejemplo: `--export obj` genera un archivo `.obj`.

## Notas
- El archivo STL será generado en el mismo directorio desde donde ejecutes el script.
- Para formatos de exportación adicionales, asegúrate de especificar la opción `--export`.

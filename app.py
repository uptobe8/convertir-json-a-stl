import json
from stl import mesh
import numpy as np
import sys

def generate_stl_from_json(json_file, output_stl):
    try:
        # Cargar los datos del archivo JSON
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        # Verificar que el JSON tenga los datos esperados
        if "vertices" not in data or "faces" not in data:
            print("El JSON debe contener las claves 'vertices' y 'faces'.")
            return
        
        # Crear la malla STL
        vertices = np.array(data["vertices"])
        faces = np.array(data["faces"])
        stl_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
        
        for i, face in enumerate(faces):
            for j in range(3):  # Cada cara tiene 3 vértices
                stl_mesh.vectors[i][j] = vertices[face[j]]
        
        # Guardar el archivo STL
        stl_mesh.save(output_stl)
        print(f"Archivo STL generado correctamente: {output_stl}")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python app.py <archivo_json> <archivo_salida_stl>")
    else:
        json_file = sys.argv[1]
        output_stl = sys.argv[2]
        generate_stl_from_json(json_file, output_stl)
from flask import Flask, request, jsonify, send_file
import json
from stl import mesh
import numpy as np
from pathlib import Path
import os
from scipy.spatial.transform import Rotation as R

app = Flask(__name__)

def load_json(json_file):
    """Carga y valida el archivo JSON."""
    try:
        if not os.path.exists(json_file):
            raise FileNotFoundError(f"El archivo '{json_file}' no existe.")
        with open(json_file, 'r') as f:
            data = json.load(f)
        if "vertices" not in data or "faces" not in data:
            raise ValueError("El JSON debe contener las claves 'vertices' y 'faces'.")
            return data
    except Exception as e:
        raise ValueError(f"Error al cargar el JSON: {e}")

def apply_scaling(vertices, scale_factor):
    """Escalar los vértices según un factor dado."""
    return np.array(vertices) * scale_factor

def apply_rotation(vertices, angle, axis):
    """Rotar los vértices alrededor de un eje."""
    rotation = R.from_euler(axis, angle, degrees=True)
    return rotation.apply(vertices)

def smooth_mesh(vertices, faces, iterations):
    """Suavizar la malla eliminando bordes duros."""
    for _ in range(iterations):
        for face in faces:
            for i in range(3):
                vertices[face[i]] = np.mean(vertices[face], axis=0)
    return vertices

def export_to_other_formats(vertices, faces, output_file, format="obj"):
    """Exportar el modelo a otros formatos como OBJ o PLY."""
    try:
        if format == "obj":
            with open(output_file, 'w') as f:
                for vertex in vertices:
                    f.write(f"v {vertex[0]} {vertex[1]} {vertex[2]}\n")
                for face in faces:
                    f.write(f"f {face[0]+1} {face[1]+1} {face[2]+1}\n")
        elif format == "ply":
            with open(output_file, 'w') as f:
                f.write("ply\nformat ascii 1.0\n")
                f.write(f"element vertex {len(vertices)}\nproperty float x\nproperty float y\nproperty float z\n")
                f.write(f"element face {len(faces)}\nproperty list uchar int vertex_indices\n")
                f.write("end_header\n")
                for vertex in vertices:
                    f.write(f"{vertex[0]} {vertex[1]} {vertex[2]}\n")
                for face in faces:
                    f.write(f"3 {face[0]} {face[1]} {face[2]}\n")
        print(f"Modelo exportado como {format.upper()} en {output_file}")
    except Exception as e:
        raise ValueError(f"Error al exportar modelo: {e}")

@app.route('/convertir-json-a-stl', methods=['POST'])
def convertir_json_a_stl():
    try:
        # Leer datos del cuerpo de la solicitud
        if 'file' not in request.files:
            return jsonify({"error": "No se ha enviado el archivo JSON"}), 400

file = request.files['file']
output_file = request.form.get('output_file')
scale_factor = float(request.form.get('scale', 1.0))
rotation = request.form.get('rotate')
smooth_iterations = int(request.form.get('smooth', 0))
export_format = request.form.get('export_format')

# Guardar el archivo temporalmente
temp_json_path = '/tmp/uploaded_vectors.json'
file.save(temp_json_path)

        if not vector_file or not output_file:
            return jsonify({"error": "Se requieren 'vector_file' y 'output_file'"}), 400

        # Cargar y procesar el archivo JSON
        json_data = load_json(vector_file)
        vertices = np.array(json_data["vertices"])
        faces = np.array(json_data["faces"])

        # Aplicar escalado
        if scale_factor != 1.0:
            vertices = apply_scaling(vertices, scale_factor)

        # Aplicar rotación
        if rotation:
            angle = rotation.get('angle')
            axis = rotation.get('axis')
            if angle is not None and axis is not None:
                vertices = apply_rotation(vertices, angle, axis)

        # Aplicar suavizado
        if smooth_iterations > 0:
            vertices = smooth_mesh(vertices, faces, smooth_iterations)

        # Crear la malla STL
        stl_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
        for i, face in enumerate(faces):
            for j in range(3):  # Cada cara tiene 3 vértices
                stl_mesh.vectors[i][j] = vertices[face[j]]

        # Guardar el archivo STL
        stl_mesh.save(output_file)

        # Exportar a otros formatos si se especifica
        if export_format:
            export_to_other_formats(vertices, faces, Path(output_file).with_suffix(f".{export_format}"), export_format)

            return send_file(output_file, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/healthz', methods=['GET'])
def health_check():
    """Endpoint de salud para Render."""
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

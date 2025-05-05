from flask import Flask, request, jsonify, send_file
import json
import numpy as np
from pathlib import Path
from scipy.spatial.transform import Rotation as R

app = Flask(__name__)

def convert_vector_paths_to_mesh(data):
    """Convierte vector_paths en vertices y faces."""
    try:
        vertices = []
        faces = []
        vertex_index = 0

        for path in data["vector_paths"]:
            path_vertices = []
            for point in path:
                vertices.append([point[0], point[1], 0])
                path_vertices.append(vertex_index)
                vertex_index += 1
            # Cerrar el polígono si hace falta
            if len(path_vertices) >= 3 and path_vertices[0] != path_vertices[-1]:
                vertices.append(vertices[path_vertices[0]])
                path_vertices.append(vertex_index)
                vertex_index += 1
            # Triangular el polígono
            if len(path_vertices) >= 3:
                for i in range(1, len(path_vertices) - 1):
                    faces.append([path_vertices[0], path_vertices[i], path_vertices[i + 1]])

        return {"vertices": vertices, "faces": faces}
    except Exception as e:
        raise ValueError(f"Error al procesar vector_paths: {e}")

def apply_scaling(vertices, scale_factor):
    return np.array(vertices) * scale_factor

def apply_rotation(vertices, angle, axis):
    rotation = R.from_euler(axis, angle, degrees=True)
    return rotation.apply(vertices)

def smooth_mesh(vertices, faces, iterations):
    for _ in range(iterations):
        for face in faces:
            for i in range(3):
                vertices[face[i]] = np.mean(vertices[face], axis=0)
    return vertices

def save_stl_ascii(vertices, faces, filename):
    """Guarda el STL en formato ASCII (sin numpy-stl)."""
    with open(filename, 'w') as f:
        f.write('solid ascii\n')
        for face in faces:
            v1 = vertices[face[0]]
            v2 = vertices[face[1]]
            v3 = vertices[face[2]]
            # Calcular la normal
            normal = np.cross(v2 - v1, v3 - v1)
            normal = normal / np.linalg.norm(normal) if np.linalg.norm(normal) != 0 else np.array([0.0, 0.0, 0.0])
            f.write(f'  facet normal {normal[0]} {normal[1]} {normal[2]}\n')
            f.write('    outer loop\n')
            f.write(f'      vertex {v1[0]} {v1[1]} {v1[2]}\n')
            f.write(f'      vertex {v2[0]} {v2[1]} {v2[2]}\n')
            f.write(f'      vertex {v3[0]} {v3[1]} {v3[2]}\n')
            f.write('    endloop\n')
            f.write('  endfacet\n')
        f.write('endsolid\n')

@app.route('/convertir-json-a-stl', methods=['POST'])
def convertir_json_a_stl():
    try:
        data = request.get_json()

        vector_file = data.get('vector_file')
        output_file = data.get('output_file')
        options = data.get('options', {})

        if not vector_file or not output_file:
            return jsonify({"error": "Se requiere 'vector_file' y 'output_file'"}), 400

        # Leer el JSON vectorial
        with open(vector_file, 'r') as f:
            json_data = json.load(f)

        # Si ya tiene vertices y faces, usarlo directo; si no, convertir vector_paths
        if "vertices" in json_data and "faces" in json_data:
            mesh_data = json_data
        elif "vector_paths" in json_data:
            mesh_data = convert_vector_paths_to_mesh(json_data)
        else:
            return jsonify({"error": "El JSON debe contener 'vertices/faces' o 'vector_paths'"}), 400

        vertices = np.array(mesh_data["vertices"])
        faces = np.array(mesh_data["faces"])

        # Escalar si hace falta
        scale_factor = options.get('scale', 1.0)
        if scale_factor != 1.0:
            vertices = apply_scaling(vertices, scale_factor)

        # Rotar si hace falta
        rotation = options.get('rotate')
        if rotation:
            angle = rotation.get('angle')
            axis = rotation.get('axis')
            if angle is not None and axis is not None:
                vertices = apply_rotation(vertices, angle, axis)

        # Suavizar si hace falta
        smooth_iterations = options.get('smooth_iterations', 0)
        if smooth_iterations > 0:
            vertices = smooth_mesh(vertices, faces, smooth_iterations)

        # Guardar STL manualmente en formato ASCII
        save_stl_ascii(vertices, faces, output_file)

        return send_file(output_file, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/healthz', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

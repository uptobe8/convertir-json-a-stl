import os
from flask import Flask, request, jsonify, send_file
import json
from stl import mesh
import numpy as np
from pathlib import Path
from scipy.spatial.transform import Rotation as R
import cv2

# Limitar el uso de hilos para evitar saturar recursos en entornos restringidos
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['NUMEXPR_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'

app = Flask(__name__)

def convert_vector_paths_to_mesh(data):
    """Convierte vector_paths en vertices y faces."""
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

@app.route('/procesar-imagen', methods=['POST'])
def procesar_imagen():
    try:
        if 'imagen' not in request.files:
            return jsonify({'error': 'No se envió ninguna imagen'}), 400

        file = request.files['imagen']
        if file.filename == '':
            return jsonify({'error': 'Nombre de archivo vacío'}), 400

        temp_input = '/tmp/input_image.png'
        temp_output = '/tmp/preprocessed_image.png'
        file.save(temp_input)

        original = cv2.imread(temp_input)
        gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
        gray_blur = cv2.GaussianBlur(gray, (5, 5), 0)
        adaptive_thresh = cv2.adaptiveThreshold(
            gray_blur, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31, 5
        )
        num_white_pixels = np.sum(adaptive_thresh == 255)
        num_black_pixels = np.sum(adaptive_thresh == 0)
        if num_black_pixels > num_white_pixels:
            adaptive_thresh = cv2.bitwise_not(adaptive_thresh)

        cv2.imwrite(temp_output, adaptive_thresh)

        return send_file(temp_output, mimetype='image/png')

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/limpiar', methods=['POST'])
def limpiar_imagen():
    try:
        if 'imagen' not in request.files:
            return jsonify({'error': 'No se envió ninguna imagen'}), 400

        file = request.files['imagen']
        if file.filename == '':
            return jsonify({'error': 'Nombre de archivo vacío'}), 400

        temp_input = '/tmp/preprocessed_image.png'
        temp_output = '/tmp/cleaned_image.png'
        file.save(temp_input)

        binary_image = cv2.imread(temp_input, cv2.IMREAD_GRAYSCALE)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        opened = cv2.morphologyEx(binary_image, cv2.MORPH_OPEN, kernel)
        closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)

        contours, hierarchy = cv2.findContours(closed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cleaned_image = np.ones_like(binary_image) * 255
        for cnt in contours:
            if cv2.contourArea(cnt) > 10:
                cv2.drawContours(cleaned_image, [cnt], -1, (0,), thickness=1)

        cv2.imwrite(temp_output, cleaned_image)

        return send_file(temp_output, mimetype='image/png')

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/vectorizar-contornos', methods=['POST'])
def vectorizar_contornos():
    try:
        data = request.get_json()
        ruta_imagen_binaria = data.get('ruta_imagen_binaria')
        if not ruta_imagen_binaria:
            return jsonify({'error': 'Se requiere ruta_imagen_binaria'}), 400

        img = cv2.imread(ruta_imagen_binaria, cv2.IMREAD_GRAYSCALE)
        contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        vector_paths = []
        for contour in contours:
            if cv2.contourArea(contour) > 2:
                approx = cv2.approxPolyDP(contour, 0.01 * cv2.arcLength(contour, True), True)
                points = approx.squeeze().tolist()
                if isinstance(points[0], int):
                    points = [points]
                vector_paths.append(points)

        return jsonify({'vector_paths': vector_paths}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/convertir-json-a-stl', methods=['POST'])
def convertir_json_a_stl():
    try:
        data = request.get_json()

        vector_file = data.get('vector_file')
        output_file = data.get('output_file')
        options = data.get('options', {})

        if not vector_file or not output_file:
            return jsonify({"error": "Se requiere 'vector_file' y 'output_file'"}), 400

        with open(vector_file, 'r') as f:
            json_data = json.load(f)

        if "vertices" in json_data and "faces" in json_data:
            mesh_data = json_data
        elif "vector_paths" in json_data:
            mesh_data = convert_vector_paths_to_mesh(json_data)
        else:
            return jsonify({"error": "El JSON debe contener 'vertices/faces' o 'vector_paths'"}), 400

        vertices = np.array(mesh_data["vertices"])
        faces = np.array(mesh_data["faces"])

        scale_factor = options.get('scale', 1.0)
        if scale_factor != 1.0:
            vertices = apply_scaling(vertices, scale_factor)

        rotation = options.get('rotate')
        if rotation:
            angle = rotation.get('angle')
            axis = rotation.get('axis')
            if angle is not None and axis is not None:
                vertices = apply_rotation(vertices, angle, axis)

        smooth_iterations = options.get('smooth_iterations', 0)
        if smooth_iterations > 0:
            vertices = smooth_mesh(vertices, faces, smooth_iterations)

        stl_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
        for i, face in enumerate(faces):
            for j in range(3):
                stl_mesh.vectors[i][j] = vertices[face[j]]

        stl_mesh.save(output_file)

        return send_file(output_file, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/healthz', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

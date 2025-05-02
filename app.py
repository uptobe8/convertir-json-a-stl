import json
from stl import mesh
import numpy as np
import sys
from pathlib import Path

def load_json(json_file):
    """Carga y valida el archivo JSON."""
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
        if "vertices" not in data or "faces" not in data:
            raise ValueError("El JSON debe contener las claves 'vertices' y 'faces'.")
        return data
    except Exception as e:
        print(f"Error al cargar el JSON: {e}")
        sys.exit(1)

def apply_scaling(vertices, scale_factor):
    """Escalar los vértices según un factor dado."""
    return np.array(vertices) * scale_factor

def apply_rotation(vertices, angle, axis):
    """Rotar los vértices alrededor de un eje."""
    from scipy.spatial.transform import Rotation as R
    rotation = R.from_euler(axis, angle, degrees=True)
    return rotation.apply(vertices)

def smooth_mesh(vertices, faces, iterations):
    """Suavizar la malla eliminando bordes duros."""
    for _ in range(iterations):
        for face in faces:
            for i in range(3):
                vertices[face[i]] = np.mean(vertices[face], axis=0)
    return vertices

def generate_supports(vertices, faces):
    """Generar soportes básicos para impresión 3D."""
    # Aquí se puede implementar lógica más avanzada para soportes
    supports = []
    for face in faces:
        if min(vertices[face, 2]) < 0:  # Si alguna cara está por debajo de z=0
            supports.append(face)
    return supports

def export_to_other_formats(vertices, faces, output_file, format="obj"):
    """Exportar el modelo a otros formatos como OBJ o PLY."""
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

def generate_stl_from_json(json_file, output_stl, scale_factor=1.0, rotation=None, smooth_iterations=0, export_format=None):
    try:
        # Cargar los datos del archivo JSON
        data = load_json(json_file)
        vertices = np.array(data["vertices"])
        faces = np.array(data["faces"])
        
        # Escalar los vértices
        if scale_factor != 1.0:
            vertices = apply_scaling(vertices, scale_factor)
        
        # Rotar los vértices
        if rotation:
            angle, axis = rotation
            vertices = apply_rotation(vertices, angle, axis)
        
        # Suavizar la malla
        if smooth_iterations > 0:
            vertices = smooth_mesh(vertices, faces, smooth_iterations)
        
        # Crear la malla STL
        stl_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
        for i, face in enumerate(faces):
            for j in range(3):  # Cada cara tiene 3 vértices
                stl_mesh.vectors[i][j] = vertices[face[j]]
        
        # Guardar el archivo STL
        stl_mesh.save(output_stl)
        print(f"Archivo STL generado correctamente: {output_stl}")

        # Exportar a otros formatos
        if export_format:
            export_to_other_formats(vertices, faces, Path(output_stl).with_suffix(f".{export_format}"), export_format)
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python app.py <archivo_json> <archivo_salida_stl> [opciones]")
        print("Opciones:")
        print("  --scale <factor>          Escalar el modelo por un factor.")
        print("  --rotate <angle> <axis>   Rotar el modelo (ejes: x, y, z).")
        print("  --smooth <iterations>     Suavizar la malla (n iteraciones).")
        print("  --export <format>         Exportar a otros formatos (obj, ply).")
    else:
        json_file = sys.argv[1]
        output_stl = sys.argv[2]
        scale_factor = 1.0
        rotation = None
        smooth_iterations = 0
        export_format = None

        # Procesar argumentos opcionales
        args = sys.argv[3:]
        if "--scale" in args:
            scale_factor = float(args[args.index("--scale") + 1])
        if "--rotate" in args:
            angle = float(args[args.index("--rotate") + 1])
            axis = args[args.index("--rotate") + 2]
            rotation = (angle, axis)
        if "--smooth" in args:
            smooth_iterations = int(args[args.index("--smooth") + 1])
        if "--export" in args:
            export_format = args[args.index("--export") + 1]

        # Generar el archivo STL
        generate_stl_from_json(json_file, output_stl, scale_factor, rotation, smooth_iterations, export_format)

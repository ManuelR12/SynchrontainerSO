# app.py
from flask import Flask, jsonify, request, send_from_directory
import os
import uuid
from flask_cors import CORS # Importar Flask-CORS

app = Flask(__name__)
CORS(app) # Habilitar CORS para toda la aplicación

# --- Configuración de Rutas de Archivos ---
# Ruta base para las carpetas de sincronización
SYNC_FILES_DIR = "/sync_files"
PUBLIC_DIR = os.path.join(SYNC_FILES_DIR, "public")
PRIVATE_DIR = os.path.join(SYNC_FILES_DIR, "private")

# Asegúrate de que los directorios existan al iniciar la app
os.makedirs(PUBLIC_DIR, exist_ok=True)
os.makedirs(PRIVATE_DIR, exist_ok=True)

# --- Rutas Originales ---
@app.route('/')
def hello_world():
    """Ruta original de bienvenida."""
    return {
        'message': 'hola, Mundo!!!'
    }

@app.route('/despedirse')
def bye_world():
    """Ruta original de despedida."""
    return {
        'message': 'Adiós, mundo!!!'
    }

# --- Nuevos Endpoints del Proyecto ---

@app.route('/storage/<uid>')
def list_container_files(uid):
    """
    Endpoint para listar todos los archivos de un contenedor específico.
    Por ahora, solo listará los archivos del contenedor actual.
    La parte de 'uid' para otros contenedores requiere lógica de red/descubrimiento.
    """
    current_container_id = os.getenv('HOSTNAME', 'unknown_container_id')

    if uid == current_container_id or uid == "current":
        all_files = []

        public_files = []
        try:
            for root, _, files in os.walk(PUBLIC_DIR):
                for file in files:
                    public_files.append(os.path.relpath(os.path.join(root, file), SYNC_FILES_DIR))
            all_files.append({"type": "public", "files": public_files})
        except Exception as e:
            print(f"Error al listar archivos públicos: {e}")
            all_files.append({"type": "public", "error": str(e)})

        private_files = []
        try:
            for root, _, files in os.walk(PRIVATE_DIR):
                for file in files:
                    private_files.append(os.path.relpath(os.path.join(root, file), SYNC_FILES_DIR))
            all_files.append({"type": "private", "files": private_files})
        except Exception as e:
            print(f"Error al listar archivos privados: {e}")
            all_files.append({"type": "private", "error": str(e)})

        return jsonify({"container_id": current_container_id, "requested_uid": uid, "files": all_files})
    else:
        return jsonify({"message": f"Funcionalidad para listar archivos del contenedor {uid} (que no es este) aún no implementada."}), 501


@app.route('/public/')
def list_network_files():
    """
    Endpoint para listar todos los archivos de la red.
    Por ahora, solo listará los archivos 'public' de ESTE contenedor.
    La lógica para la red completa se implementará después.
    """
    network_public_files = []
    try:
        for root, _, files in os.walk(PUBLIC_DIR):
            for file in files:
                network_public_files.append(os.path.relpath(os.path.join(root, file), SYNC_FILES_DIR))
    except Exception as e:
        print(f"Error al listar archivos públicos de la red: {e}")
        return jsonify({"error": str(e)}), 500

    return jsonify({"network_files": network_public_files})

@app.route('/download/<path:filename>')
def download_file(filename):
    """
    Endpoint para descargar un archivo.
    Busca el archivo en las carpetas public y private de este contenedor.
    """
    full_public_path = os.path.join(PUBLIC_DIR, filename)
    if os.path.exists(full_public_path) and os.path.isfile(full_public_path):
        return send_from_directory(PUBLIC_DIR, filename, as_attachment=True)

    full_private_path = os.path.join(PRIVATE_DIR, filename)
    if os.path.exists(full_private_path) and os.path.isfile(full_private_path):
        return send_from_directory(PRIVATE_DIR, filename, as_attachment=True)

    return jsonify({"error": f"Archivo '{filename}' no encontrado en este contenedor."}), 404

@app.route('/upload/<uid>/<path:filename>', methods=['POST'])
def upload_file(uid, filename):
    """
    Endpoint para subir un archivo al contenedor especificado.
    Por ahora, solo permite subir a este mismo contenedor.
    La lógica para enviar a otros contenedores se implementará después.
    """
    current_container_id = os.getenv('HOSTNAME', 'unknown_container_id')

    if uid != current_container_id and uid != "current":
        return jsonify({"message": f"Funcionalidad para subir archivos al contenedor {uid} (que no es este) aún no implementada."}), 501

    if 'file' not in request.files:
        return jsonify({"error": "No se encontró el archivo en la solicitud (asegúrate de usar 'file' como nombre de campo)."}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No se seleccionó ningún archivo."}), 400

    if file:
        filepath = os.path.join(PUBLIC_DIR, filename)
        try:
            file.save(filepath)
            return jsonify({"message": f"Archivo '{filename}' subido exitosamente a {filepath} en este contenedor."}), 200
        except Exception as e:
            return jsonify({"error": f"Error al guardar el archivo: {e}"}), 500
    return jsonify({"error": "Error desconocido al subir el archivo."}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

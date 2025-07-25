from flask import Flask, jsonify, request, send_from_directory
import os
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- Configuración ---
SYNC_FILES_DIR = "/sync_files"
PUBLIC_DIR = os.path.join(SYNC_FILES_DIR, "public")
PRIVATE_DIR = os.path.join(SYNC_FILES_DIR, "private")

os.makedirs(PUBLIC_DIR, exist_ok=True)
os.makedirs(PRIVATE_DIR, exist_ok=True)

MY_NAME = os.getenv('SYNCHRO_NAME', 'unknown_name')
SYNCHRO_NODES = os.getenv('SYNCHRO_NODES', '').split(',')

# --- Endpoints ---
@app.route('/')
def hello_world():
    return {
        'message': f'Hola, soy el contenedor: {MY_NAME} (hostname: {os.getenv("HOSTNAME")})',
        'known_nodes_in_network': SYNCHRO_NODES,
        'status': 'ok'
    }

@app.route('/internal/files')
def get_internal_files():
    public_files = [f for f in os.listdir(PUBLIC_DIR) if os.path.isfile(os.path.join(PUBLIC_DIR, f))]
    private_files = [f for f in os.listdir(PRIVATE_DIR) if os.path.isfile(os.path.join(PRIVATE_DIR, f))]
    return jsonify({
        "container_id": MY_NAME,
        "public_files": public_files,
        "private_files": private_files
    })

@app.route('/storage/<uid>')
def list_container_files(uid):
    if uid == MY_NAME or uid == "current":
        return get_internal_files()
    if uid in SYNCHRO_NODES:
        try:
            target_url = f'http://{uid}:5000/internal/files'
            response = requests.get(target_url, timeout=3)
            response.raise_for_status()
            return jsonify(response.json())
        except requests.exceptions.RequestException as e:
            return jsonify({"error": f"No se pudo contactar al contenedor {uid}: {e}"}), 503
    return jsonify({"error": f"El contenedor con UID '{uid}' no se conoce en esta red."}), 404

@app.route('/public/')
def list_network_files():
    all_network_files = {}
    for node_name in SYNCHRO_NODES:
        if not node_name: continue
        try:
            node_url = f'http://{node_name}:5000/internal/files'
            response = requests.get(node_url, timeout=3)
            if response.ok:
                data = response.json()
                all_network_files[node_name] = data.get('public_files', [])
            else:
                all_network_files[node_name] = ["Error al obtener la lista"]
        except requests.exceptions.RequestException:
            all_network_files[node_name] = ["Error: Contenedor no contactable"]
    return jsonify({"files_in_public_network": all_network_files})

@app.route('/private/')
def list_network_private_files():
    all_network_files = {}
    for node_name in SYNCHRO_NODES:
        if not node_name: continue
        try:
            node_url = f'http://{node_name}:5000/internal/files'
            response = requests.get(node_url, timeout=3)
            if response.ok:
                data = response.json()
                all_network_files[node_name] = data.get('private_files', [])
            else:
                all_network_files[node_name] = ["Error al obtener la lista"]
        except requests.exceptions.RequestException:
            all_network_files[node_name] = ["Error: Contenedor no contactable"]
    return jsonify({"files_in_private_network": all_network_files})

@app.route('/download/<uid>/<folder>/<path:filename>', methods=['GET'])
def download_file(uid, folder, filename):
    """
    Descarga un archivo de un contenedor y carpeta específicos.
    """
    if uid == MY_NAME or uid == "current":
        if folder not in ['public', 'private']:
            return jsonify({"error": "La carpeta debe ser 'public' o 'private'."}), 400
        
        target_dir = PUBLIC_DIR if folder == 'public' else PRIVATE_DIR
        filepath = os.path.join(target_dir, filename)

        if os.path.exists(filepath):
            return send_from_directory(target_dir, filename, as_attachment=True)
        else:
            return jsonify({"error": f"Archivo '{filename}' no encontrado en la carpeta '{folder}' de este contenedor."}), 404
            
    elif uid in SYNCHRO_NODES:
        try:
            target_url = f'http://{uid}:5000/download/{uid}/{folder}/{filename}'
            file_response = requests.get(target_url, stream=True, timeout=20)
            file_response.raise_for_status()
            return file_response.raw, file_response.status_code, file_response.headers.items()
        except requests.exceptions.RequestException as e:
            return jsonify({"error": f"Fallo al obtener el archivo de {uid}: {e}"}), 503
    else:
        return jsonify({"error": f"El contenedor con UID '{uid}' no se conoce."}), 404

@app.route('/upload/<uid>/<path:filename>', methods=['POST'])
def upload_file(uid, filename):
    if 'file' not in request.files:
        return jsonify({"error": "No se encontró el archivo en la solicitud."}), 400
    file = request.files['file']
    destination_folder = request.form.get('folder', 'public')
    if file.filename == '':
        return jsonify({"error": "No se seleccionó ningún archivo."}), 400

    if uid == MY_NAME or uid == "current":
        save_dir = PRIVATE_DIR if destination_folder == 'private' else PUBLIC_DIR
        try:
            filepath = os.path.join(save_dir, filename)
            file.save(filepath)
            return jsonify({"message": f"Archivo '{filename}' guardado en la carpeta '{destination_folder}' de {MY_NAME}."}), 200
        except Exception as e:
            return jsonify({"error": f"Error al guardar el archivo: {e}"}), 500
    
    elif uid in SYNCHRO_NODES:
        try:
            target_url = f'http://{uid}:5000/upload/{uid}/{filename}'
            file.seek(0)
            files = {'file': (filename, file.read())}
            data = {'folder': destination_folder}
            response = requests.post(target_url, files=files, data=data, timeout=20)
            response.raise_for_status()
            return jsonify(response.json())
        except requests.exceptions.RequestException as e:
            return jsonify({"error": f"Fallo al reenviar el archivo a {uid}: {e}"}), 503
    return jsonify({"error": f"El contenedor con UID '{uid}' no se conoce."}), 404

@app.route('/delete/<uid>/<path:filename>', methods=['DELETE'])
def delete_file(uid, filename):
    if uid == MY_NAME or uid == "current":
        path_public = os.path.join(PUBLIC_DIR, filename)
        path_private = os.path.join(PRIVATE_DIR, filename)
        if os.path.exists(path_public):
            try:
                os.remove(path_public)
                return jsonify({"message": f"Archivo '{filename}' eliminado de 'public' en {MY_NAME}."}), 200
            except Exception as e:
                return jsonify({"error": f"No se pudo eliminar: {e}"}), 500
        elif os.path.exists(path_private):
            try:
                os.remove(path_private)
                return jsonify({"message": f"Archivo '{filename}' eliminado de 'private' en {MY_NAME}."}), 200
            except Exception as e:
                return jsonify({"error": f"No se pudo eliminar: {e}"}), 500
        return jsonify({"error": f"Archivo '{filename}' no encontrado en este contenedor."}), 404
    
    elif uid in SYNCHRO_NODES:
        try:
            target_url = f'http://{uid}:5000/delete/{uid}/{filename}'
            response = requests.delete(target_url, timeout=10)
            response.raise_for_status()
            return jsonify(response.json())
        except requests.exceptions.RequestException as e:
            return jsonify({"error": f"Fallo al reenviar la solicitud de borrado a {uid}: {e}"}), 503
    return jsonify({"error": f"El contenedor con UID '{uid}' no se conoce."}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
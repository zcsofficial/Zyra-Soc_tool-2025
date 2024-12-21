from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS  # Import CORS
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

ROOT_DIR = '/'  # Adjust this path as needed

@app.route('/list', methods=['GET'])
def list_files():
    path = request.args.get('path', ROOT_DIR)
    full_path = os.path.join(ROOT_DIR, path.strip('/'))
    
    if not os.path.exists(full_path) or not os.path.isdir(full_path):
        return jsonify({'error': 'Directory not found'}), 404

    files = os.listdir(full_path)
    return jsonify({'files': files})

@app.route('/download', methods=['GET'])
def download_file():
    filename = request.args.get('filename')
    if not filename:
        return jsonify({'error': 'Filename is required'}), 400
    
    # Ensure filename is safe
    safe_filename = os.path.basename(filename)
    directory = os.path.dirname(filename)
    
    # Construct the full path to the file
    full_path = os.path.join(ROOT_DIR, directory.strip('/'), safe_filename)
    
    if not os.path.exists(full_path) or not os.path.isfile(full_path):
        return jsonify({'error': 'File not found'}), 404
    
    return send_from_directory(directory, safe_filename, as_attachment=True)

@app.route('/delete', methods=['DELETE'])
def delete_file():
    filename = request.args.get('filename')
    if not filename:
        return jsonify({'error': 'Filename is required'}), 400
    
    safe_filename = os.path.basename(filename)
    directory = os.path.dirname(filename)
    full_path = os.path.join(ROOT_DIR, directory.strip('/'), safe_filename)
    
    if not os.path.exists(full_path) or not os.path.isfile(full_path):
        return jsonify({'error': 'File not found'}), 404
    
    os.remove(full_path)
    return jsonify({'message': 'File deleted successfully'})

@app.route('/help', methods=['GET'])
def help_menu():
    help_text = (
        "Available commands:\n"
        "ls            - List files in the current directory\n"
        "cd <dir>      - Change directory\n"
        "cd ..         - Move up one directory\n"
        "pwd           - Print working directory\n"
        "download <file> - Download a file\n"
        "delete <file> - Delete a file\n"
        "help          - Show this help menu"
    )
    return jsonify({'help': help_text})

if __name__ == '__main__':
    app.run(port=5050)

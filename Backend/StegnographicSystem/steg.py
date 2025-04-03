from flask import Flask, request, jsonify, send_file, render_template
import os
from stegano import lsb
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import base64
import io
from PIL import Image

app = Flask(__name__)

# Ensure upload folder exists
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

def encrypt_password(password, key):
    """Encrypt a password using AES."""
    # Convert key to bytes and ensure it's 16, 24, or 32 bytes long
    key_bytes = key.encode('utf-8')
    if len(key_bytes) > 32:
        key_bytes = key_bytes[:32]
    elif len(key_bytes) not in [16, 24, 32]:
        key_bytes = pad(key_bytes, 16)
    
    # Generate a random initialization vector
    iv = get_random_bytes(16)
    
    # Create cipher
    cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
    
    # Encrypt the password
    ciphertext = cipher.encrypt(pad(password.encode('utf-8'), AES.block_size))
    
    # Combine IV and ciphertext for storage
    encrypted_data = base64.b64encode(iv + ciphertext).decode('utf-8')
    
    return encrypted_data

def decrypt_password(encrypted_data, key):
    """Decrypt a password using AES."""
    # Convert key to bytes and ensure it's 16, 24, or 32 bytes long
    key_bytes = key.encode('utf-8')
    if len(key_bytes) > 32:
        key_bytes = key_bytes[:32]
    elif len(key_bytes) not in [16, 24, 32]:
        key_bytes = pad(key_bytes, 16)
    
    # Decode from base64
    data = base64.b64decode(encrypted_data)
    
    # Extract IV and ciphertext
    iv = data[:16]
    ciphertext = data[16:]
    
    # Create cipher
    cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
    
    # Decrypt the password
    decrypted_data = unpad(cipher.decrypt(ciphertext), AES.block_size)
    
    return decrypted_data.decode('utf-8')

@app.route('/encode', methods=['POST'])
def encode_password():
    # Check if the post request has the file part
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    # Get the image, password, and key
    image_file = request.files['image']
    password = request.form.get('password')
    key = request.form.get('key')
    
    if not password or not key:
        return jsonify({'error': 'Password and key are required'}), 400
    
    try:
        # First encrypt the password
        encrypted_password = encrypt_password(password, key)
        
        # Save the uploaded image temporarily
        temp_path = os.path.join(UPLOAD_FOLDER, 'temp_image.png')
        image_file.save(temp_path)
        
        # Embed the encrypted password into the image
        secret_image = lsb.hide(temp_path, encrypted_password)
        
        # Save the image with the hidden password
        output_path = os.path.join(UPLOAD_FOLDER, 'encoded_image.png')
        secret_image.save(output_path)
        
        # Return the image with the hidden password
        return send_file(output_path, mimetype='image/png', as_attachment=True,
                         download_name='encoded_image.png')
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/decode', methods=['POST'])
def decode_password():
    # Check if the post request has the file part
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    # Get the image and key
    image_file = request.files['image']
    key = request.form.get('key')
    
    if not key:
        return jsonify({'error': 'Key is required'}), 400
    
    try:
        # Save the uploaded image temporarily
        temp_path = os.path.join(UPLOAD_FOLDER, 'temp_decode.png')
        image_file.save(temp_path)
        
        # Extract the hidden message from the image
        encrypted_password = lsb.reveal(temp_path)
        
        # Decrypt the password
        password = decrypt_password(encrypted_password, key)
        
        return jsonify({'password': password})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
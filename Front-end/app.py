from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
import base64
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configure your Colab backend URL here
# You'll get this from ngrok when you run the Colab notebook
COLAB_BACKEND_URL='https://unloathful-undefaceable-antwan.ngrok-free.dev'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_image():
    try:
        data = request.json
        
        # Prepare the request for the Colab backend
        payload = {
            'model': data.get('model'),
            'lora': data.get('lora'),
            'prompt': data.get('prompt'),
            'seed': data.get('seed', 0)
        }
        
        # Send request to Colab backend
        response = requests.post(
            f'{COLAB_BACKEND_URL}/generate',
            json=payload,
            timeout=120  # 2 minute timeout for image generation
        )
        
        if response.status_code == 200:
            result = response.json()
            return jsonify({
                'success': True,
                'image': result['image'],  # Base64 encoded image
                'seed': data.get('seed')
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Backend error: {response.status_code}'
            }), 500
            
    except requests.exceptions.Timeout:
        return jsonify({
            'success': False,
            'error': 'Request timeout - generation took too long'
        }), 504
    except requests.exceptions.ConnectionError:
        return jsonify({
            'success': False,
            'error': 'Cannot connect to Colab backend. Make sure it is running.'
        }), 503
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        # Try to ping the Colab backend
        response = requests.get(f'{COLAB_BACKEND_URL}/health', timeout=5)
        backend_status = response.status_code == 200
    except:
        backend_status = False
    
    return jsonify({
        'status': 'healthy',
        'backend_connected': backend_status,
        'backend_url': COLAB_BACKEND_URL
    })

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    print("\n" + "="*50)
    print("🎨 AI Image Generator Server")
    print("="*50)
    print(f"\n📡 Server running on: http://localhost:5000")
    print(f"🔗 Colab backend URL: {COLAB_BACKEND_URL}")
    print("\n💡 To set Colab backend URL, use:")
    print("   export COLAB_BACKEND_URL='your_ngrok_url'")
    print("\n" + "="*50 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
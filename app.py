from flask import Flask, jsonify, request
from supabase import create_client
import os
from ai_recommendations import get_ai_recommendations
from dotenv import load_dotenv
from flask_cors import CORS

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure Supabase
supabase = create_client(os.getenv('https://fhhpwfujypcpklpwvvhf.supabase.co'), os.getenv('yeyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZoaHB3ZnVqeXBjcGtscHd2dmhmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQzNDE1NDgsImV4cCI6MjA2OTkxNzU0OH0.z2j491yR9HunwNAGa_NngPiXAG18Cf1ZpaUAvdE5eF4'))

@app.route('/api/crops', methods=['GET'])
def get_crops():
    try:
        search = request.args.get('search', '')
        crop_type = request.args.get('type', '')
        region = request.args.get('region', '')
        
        query = supabase.table('crops').select('*')
        
        if search:
            query = query.ilike('name', f'%{search}%')
        if crop_type:
            query = query.eq('type', crop_type)
        if region:
            query = query.eq('region', region)
        
        crops = query.execute()
        return jsonify({
            'success': True,
            'data': crops.data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/recommendations', methods=['POST'])
def recommendations():
    try:
        cart_items = request.json.get('cart', [])
        recommendations = get_ai_recommendations(cart_items, supabase)
        return jsonify({
            'success': True,
            'recommendations': recommendations
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
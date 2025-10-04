from flask import Flask, render_template, request, jsonify, session
import os
import base64
from openai import OpenAI
import json
import time
from functools import wraps
import secrets

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# Rate Limiting Storage (In-Memory)
# Format: {session_id: last_request_timestamp}
rate_limit_storage = {}
RATE_LIMIT_SECONDS = 30

def rate_limit_check():
    """Prüft ob die Session das Rate Limit erreicht hat"""
    session_id = session.get('session_id')
    if not session_id:
        session_id = secrets.token_urlsafe(16)
        session['session_id'] = session_id
    
    current_time = time.time()
    last_request = rate_limit_storage.get(session_id, 0)
    
    time_since_last_request = current_time - last_request
    
    if time_since_last_request < RATE_LIMIT_SECONDS:
        remaining = int(RATE_LIMIT_SECONDS - time_since_last_request)
        return False, remaining
    
    # Update timestamp
    rate_limit_storage[session_id] = current_time
    
    # Cleanup alte Einträge (älter als 5 Minuten)
    cleanup_threshold = current_time - 300
    rate_limit_storage.clear()
    for sid, timestamp in list(rate_limit_storage.items()):
        if timestamp < cleanup_threshold:
            del rate_limit_storage[sid]
    
    return True, 0

def get_api_key():
    """Holt den API Key aus der Session (wurde via URL-Parameter gesetzt)"""
    return session.get('openai_api_key')

def require_api_key(f):
    """Decorator um API Key zu verlangen"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = get_api_key()
        if not api_key:
            return jsonify({
                'error': 'Kein API Token gefunden',
                'message': 'Bitte füge ?token=dein-openai-key zur URL hinzu'
            }), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    # Token aus URL-Parameter holen und in Session speichern
    token = request.args.get('token')
    if token:
        # Validiere dass es wie ein OpenAI Key aussieht
        if token.startswith('sk-'):
            session['openai_api_key'] = token
            session.permanent = True  # Session bleibt bestehen
        else:
            return render_template('index.html', error='Ungültiges Token-Format. OpenAI Keys beginnen mit "sk-"')
    
    # Prüfe ob ein gültiger Key in der Session ist
    has_valid_key = bool(get_api_key())
    
    return render_template('index.html', has_api_key=has_valid_key)

@app.route('/analyze', methods=['POST'])
@require_api_key
def analyze():
    try:
        # Rate Limiting Check
        allowed, remaining_time = rate_limit_check()
        if not allowed:
            return jsonify({
                'error': 'Rate Limit erreicht',
                'message': f'Bitte warte noch {remaining_time} Sekunden vor der nächsten Analyse.',
                'retry_after': remaining_time
            }), 429
        
        data = request.json
        image_data = data.get('image')
        description = data.get('description', '')
        portion_size = data.get('portionSize')
        portion_weight = data.get('portionWeight')
        
        if not image_data:
            return jsonify({'error': 'Kein Bild vorhanden'}), 400
        
        # Base64 Präfix entfernen falls vorhanden
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        # OpenAI Client mit Session-API-Key
        api_key = get_api_key()
        client = OpenAI(api_key=api_key)
        
        # Prompt für die Nährwertanalyse
        prompt = f"""Analysiere dieses Lebensmittelbild und erstelle eine detaillierte Nährwertanalyse.

Benutzerbeschreibung: {description if description else 'Keine Beschreibung angegeben'}

Bitte gib die Nährwerte zurück im folgenden JSON-Format:
{{
    "food_name": "Name des Lebensmittels/Gerichts",
    "estimated_portion": "Geschätzte Portionsgröße (z.B. '1 Teller', '200g')",
    "estimated_weight_g": geschätztes Gewicht in Gramm als Zahl,
    "nutrition": {{
        "calories": Kalorien in kcal,
        "protein": Protein in g,
        "carbs": Kohlenhydrate in g,
        "fat": Fett in g,
        "fiber": Ballaststoffe in g,
        "sugar": Zucker in g
    }},
    "ingredients": ["Liste", "der", "Hauptzutaten"],
    "confidence": "hoch/mittel/niedrig"
}}

Sei so präzise wie möglich basierend auf dem Bild. Wenn du dir unsicher bist, gib realistische Schätzwerte."""

        # API Call an OpenAI Vision
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        # Response parsen
        result_text = response.choices[0].message.content
        
        # JSON aus der Response extrahieren
        try:
            # Versuche JSON zu finden und zu parsen
            start_idx = result_text.find('{')
            end_idx = result_text.rfind('}') + 1
            json_str = result_text[start_idx:end_idx]
            result = json.loads(json_str)
        except:
            return jsonify({'error': 'Fehler beim Parsen der KI-Antwort'}), 500
        
        # Falls Portionsgröße oder Gewicht vom Benutzer angegeben wurde, neu berechnen
        if portion_size or portion_weight:
            result = recalculate_nutrition(result, portion_size, portion_weight)
        
        return jsonify(result)
        
    except Exception as e:
        error_message = str(e)
        
        # Spezifische Fehlerbehandlung für ungültige API Keys
        if 'invalid_api_key' in error_message or 'Incorrect API key' in error_message:
            return jsonify({
                'error': 'Ungültiger API Key',
                'message': 'Der verwendete OpenAI API Key ist ungültig. Bitte prüfe deinen Key.'
            }), 401
        
        print(f"Error: {error_message}")
        return jsonify({'error': f'Fehler bei der Analyse: {error_message}'}), 500

def recalculate_nutrition(original_data, new_portion_size=None, new_weight=None):
    """Berechnet Nährwerte basierend auf neuer Portionsgröße oder Gewicht neu"""
    if not new_weight:
        return original_data
    
    try:
        original_weight = float(original_data.get('estimated_weight_g', 100))
        new_weight_float = float(new_weight)
        
        if original_weight == 0:
            return original_data
        
        factor = new_weight_float / original_weight
        
        # Nährwerte anpassen
        nutrition = original_data.get('nutrition', {})
        adjusted_nutrition = {
            'calories': round(nutrition.get('calories', 0) * factor),
            'protein': round(nutrition.get('protein', 0) * factor, 1),
            'carbs': round(nutrition.get('carbs', 0) * factor, 1),
            'fat': round(nutrition.get('fat', 0) * factor, 1),
            'fiber': round(nutrition.get('fiber', 0) * factor, 1),
            'sugar': round(nutrition.get('sugar', 0) * factor, 1)
        }
        
        result = original_data.copy()
        result['nutrition'] = adjusted_nutrition
        result['estimated_weight_g'] = new_weight_float
        if new_portion_size:
            result['estimated_portion'] = new_portion_size
        
        return result
        
    except Exception as e:
        print(f"Recalculation error: {str(e)}")
        return original_data

@app.route('/recalculate', methods=['POST'])
@require_api_key
def recalculate():
    try:
        data = request.json
        original_data = data.get('originalData')
        portion_size = data.get('portionSize')
        portion_weight = data.get('portionWeight')
        
        result = recalculate_nutrition(original_data, portion_size, portion_weight)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/check-token')
def check_token():
    """Endpoint um zu prüfen ob ein gültiger Token in der Session ist"""
    has_key = bool(get_api_key())
    return jsonify({'has_token': has_key})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8085)

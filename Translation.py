from flask import Flask, request, jsonify, render_template_string
from deep_translator import GoogleTranslator

app = Flask(__name__)

# Supported languages
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'zh': 'Chinese',
    'ja': 'Japanese',
    'ko': 'Korean',
    'ar': 'Arabic',
    'hi': 'Hindi',
    'tr': 'Turkish'
}

# HTML template with integrated translation functionality
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="grammarly" content="disabled">
    <title>Translation Service</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        textarea, select, button {
            margin: 10px 0;
            padding: 10px;
            width: 100%;
            max-width: 100%;
            box-sizing: border-box;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        textarea {
            min-height: 120px;
            resize: vertical;
        }
        button {
            background-color: #4CAF50;
            color: white;
            border: none;
            cursor: pointer;
            font-weight: bold;
        }
        button:hover {
            background-color: #45a049;
        }
        .translation-container {
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
        }
        .translation-box {
            flex: 1;
        }
        #result {
            margin-top: 20px;
            padding: 15px;
            background: #f8f9fa;
            border: 1px solid #ddd;
            border-radius: 4px;
            display: none;
        }
        .loading {
            display: none;
            text-align: center;
            margin: 10px 0;
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .error {
            color: red;
            margin: 10px 0;
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Translation Service</h1>
        <form id="translationForm" onsubmit="handleTranslate(event)">
            <div class="translation-container">
                <div class="translation-box">
                    <select id="source_lang" name="source_lang">
                        <option value="en" selected>English</option>
                        {% for code, name in languages.items() %}
                            {% if code != 'en' %}
                            <option value="{{ code }}">{{ name }}</option>
                            {% endif %}
                        {% endfor %}
                    </select>
                    <textarea 
                        id="text" 
                        name="text" 
                        placeholder="Enter text to translate..."
                        required
                    ></textarea>
                </div>
                <div class="translation-box">
                    <select id="target_lang" name="target_lang">
                        <option value="es" selected>Spanish</option>
                        {% for code, name in languages.items() %}
                            {% if code != 'es' %}
                            <option value="{{ code }}">{{ name }}</option>
                            {% endif %}
                        {% endfor %}
                    </select>
                    <textarea 
                        id="translated_text" 
                        readonly 
                        placeholder="Translation will appear here..."
                    ></textarea>
                </div>
            </div>
            <button type="submit">Translate</button>
            <div id="loading" class="loading">Translating...</div>
            <div id="error" class="error"></div>
        </form>
    </div>

    <script>
        async function handleTranslate(event) {
            event.preventDefault();
            
            const text = document.getElementById('text').value;
            const source_lang = document.getElementById('source_lang').value;
            const target_lang = document.getElementById('target_lang').value;
            const loadingDiv = document.getElementById('loading');
            const errorDiv = document.getElementById('error');
            const translatedTextArea = document.getElementById('translated_text');

            // Reset states
            loadingDiv.style.display = 'block';
            errorDiv.style.display = 'none';
            errorDiv.textContent = '';
            translatedTextArea.value = '';

            try {
                const response = await fetch('/translate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ 
                        text: text, 
                        source_lang: source_lang, 
                        target_lang: target_lang 
                    })
                });

                const data = await response.json();

                if (data.error) {
                    errorDiv.textContent = data.error;
                    errorDiv.style.display = 'block';
                } else {
                    translatedTextArea.value = data.translated_text;
                }
            } catch (err) {
                errorDiv.textContent = 'Translation failed: ' + err.message;
                errorDiv.style.display = 'block';
                console.error('Translation error:', err);
            } finally {
                loadingDiv.style.display = 'none';
            }
        }
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, languages=SUPPORTED_LANGUAGES)

@app.route('/translate', methods=['POST'])
def translate():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Print debugging information
        print("Received data:", data)

        text = data.get('text', '').strip()
        source_lang = data.get('source_lang', '')
        target_lang = data.get('target_lang', '')

        # Validate input
        if not all([text, source_lang, target_lang]):
            return jsonify({"error": "Missing required fields"}), 400

        print(f"Translating: {text} from {source_lang} to {target_lang}")

        # Translate the text
        translator = GoogleTranslator(source=source_lang, target=target_lang)
        translated_text = translator.translate(text)

        print(f"Translation result: {translated_text}")

        return jsonify({
            "original_text": text,
            "translated_text": translated_text,
            "source_lang": source_lang,
            "target_lang": target_lang
        })

    except Exception as e:
        print(f"Translation error: {str(e)}")
        return jsonify({"error": f"Translation failed: {str(e)}"}), 500

if __name__ == '__main__':
    print("=== Translation Service ===")
    print(f"Supported Languages: {len(SUPPORTED_LANGUAGES)}")
    print("Starting server...")
    app.run(host='0.0.0.0', port=5000, debug=True)
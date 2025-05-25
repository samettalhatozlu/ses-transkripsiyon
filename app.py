from flask import Flask, render_template, request, flash, redirect, url_for, send_file
from werkzeug.utils import secure_filename
import os
import whisper
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = os.urandom(24)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load Whisper model
try:
    model = whisper.load_model("medium")
    logger.info("Whisper model loaded successfully")
except Exception as e:
    logger.error(f"Error loading Whisper model: {str(e)}")
    raise

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    try:
        if 'audio_file' not in request.files:
            flash('Lütfen bir ses dosyası seçin')
            return redirect(url_for('index'))
        
        file = request.files['audio_file']
        if file.filename == '':
            flash('Lütfen bir ses dosyası seçin')
            return redirect(url_for('index'))
        
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            logger.info(f"Processing file: {filename}")
            
            # Transcribe the audio
            result = model.transcribe(filepath, language='turkish')
            text = result["text"]
            
            # Create output file
            output_filename = f'transcription_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
            
            # Clean up the uploaded audio file
            os.remove(filepath)
            
            logger.info(f"Transcription completed: {output_filename}")
            
            return send_file(
                output_path,
                as_attachment=True,
                download_name=output_filename
            )
    except Exception as e:
        logger.error(f"Error during transcription: {str(e)}")
        flash('Transkripsiyon sırasında bir hata oluştu')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 
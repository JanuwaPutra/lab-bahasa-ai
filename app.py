from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import os
import logging
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, session
from modules.grammar_correction_openai_2 import correct_grammar, analyze_and_paraphrase, count_words
from modules.speech_recognition import recognize_speech
from modules.adaptive_learning import get_questions, evaluate_answer, get_pretest_questions, evaluate_pretest_answers, get_post_test_questions, evaluate_post_test_answers, has_completed_pretest, get_learning_materials
from modules.youtube_transcription import get_youtube_transcript
import base64
import tempfile
import subprocess
from datetime import datetime
import json

# Import modul tutor virtual
from modules.virtual_tutor import (
    generate_chat_response,
    generate_speaking_feedback,
    get_supported_languages,
    get_conversation_topics,
    get_writing_prompts,
    get_speaking_topics
)

# Konfigurasi logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "lab-bahasa-secret-key")

# Tambahkan module untuk evaluasi mandiri
from modules.assessment import (
    get_placement_test, 
    evaluate_placement_test,
    get_listening_test,
    evaluate_listening,
    get_reading_test,
    evaluate_reading,
    get_speaking_test,
    evaluate_speaking,
    generate_progress_report
)

# Update the imports at the top of app.py


def convert_audio_to_wav(input_file, output_file):
    """Mengkonversi file audio ke format wav menggunakan ffmpeg"""
    try:
        # Check if ffmpeg is installed
        ffmpeg_version = subprocess.run(
            ['ffmpeg', '-version'], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            check=True,
            text=True
        )
        print(f"FFmpeg version: {ffmpeg_version.stdout.splitlines()[0] if ffmpeg_version.stdout else 'Unknown'}")
        
        # Convert audio to wav
        cmd = ['ffmpeg', '-y', '-i', input_file, '-acodec', 'pcm_s16le', '-ar', '44100', '-ac', '1', output_file]
        process = subprocess.run(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            check=True,
            text=True
        )
        
        # Periksa apakah file output berhasil dibuat dan memiliki ukuran > 0
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            print(f"Audio file successfully converted to: {output_file}")
            return True
        else:
            print(f"Output file created but may be invalid: {output_file}")
            return False
    except subprocess.SubprocessError as e:
        print(f"FFmpeg error: {e}")
        if hasattr(e, 'stderr') and e.stderr:
            print(f"FFmpeg stderr: {e.stderr}")
        return False
    except FileNotFoundError:
        print("FFmpeg not found. Please install FFmpeg.")
        return False
    except Exception as e:
        print(f"Unexpected error during audio conversion: {str(e)}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/grammar', methods=['GET', 'POST'])
def grammar():
    if request.method == 'POST':
        text = request.form['text']
        language = request.form['language']
        
        # Hitung jumlah kata
        word_count = count_words(text)
        
        # Gunakan fungsi yang sudah diupdate
        paraphrase_title, corrected_text, _ = analyze_and_paraphrase(text, language)
        
        return render_template('grammar.html', 
                              original_text=text, 
                              corrected_text=corrected_text,
                              paraphrase_title=paraphrase_title, 
                              word_count=word_count,
                              count_words=count_words,
                              language=language)
    return render_template('grammar.html')

@app.route('/speech', methods=['GET', 'POST'])
def speech():
    # Cek jika ini adalah hasil dari direct API (melalui URL parameter)
    if request.method == 'GET' and 'direct_api' in request.args:
        recognized_text = request.args.get('recognized_text', '')
        reference_text = request.args.get('reference_text', '')
        accuracy = request.args.get('accuracy')
        feedback = request.args.get('feedback')
        language = request.args.get('language', 'en')
        
        # Konversi accuracy ke float jika ada
        if accuracy:
            try:
                accuracy = float(accuracy)
            except:
                accuracy = None
        
        return render_template('speech.html',
                           recognized_text=recognized_text,
                           reference_text=reference_text,
                           accuracy=accuracy,
                           feedback=feedback,
                           language=language)
    
    if request.method == 'POST':
        reference_text = request.form.get('reference_text', '')
        language = request.form.get('language', 'en')
        input_type = request.form.get('input_type', '')
        
        logger.info(f"Speech recognition request - Language: {language}, Input type: {input_type}")
        
        # Cek apakah ffmpeg tersedia
        ffmpeg_available = True
        try:
            subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        except (subprocess.SubprocessError, FileNotFoundError):
            ffmpeg_available = False
            logger.warning("FFmpeg tidak tersedia. Beberapa fitur konversi audio tidak akan berfungsi.")
        
        if 'audio' in request.files and request.files['audio'].filename != '':
            audio_file = request.files['audio']
            logger.info(f"Processing uploaded audio file: {audio_file.filename}")
            
            # Buat file sementara dan konversi ke format wav jika diperlukan
            file_ext = os.path.splitext(audio_file.filename)[1].lower()
            logger.info(f"Audio file extension: {file_ext}")
            
            if file_ext not in ['.wav', '.aiff', '.flac']:
                # Konversi ke wav jika bukan format yang didukung
                logger.info(f"Converting audio from {file_ext} to WAV format")
                with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
                    temp_file.close()
                    audio_file.save(temp_file.name)
                    
                    wav_file = temp_file.name.replace(file_ext, '.wav')
                    if ffmpeg_available and convert_audio_to_wav(temp_file.name, wav_file):
                        # Gunakan file wav yang sudah dikonversi
                        logger.info(f"Audio conversion successful, processing: {wav_file}")
                        recognized_text, accuracy, feedback = recognize_speech(wav_file, reference_text, language)
                        
                        # Hapus file sementara
                        if os.path.exists(temp_file.name):
                            os.remove(temp_file.name)
                        if os.path.exists(wav_file):
                            os.remove(wav_file)
                    else:
                        # Jika konversi gagal
                        logger.error(f"Failed to convert audio file from {file_ext} to WAV")
                        recognized_text = "Error: Gagal mengkonversi file audio ke format yang didukung"
                        accuracy = None
                        feedback = "Pastikan ffmpeg sudah terinstal dengan benar"
            else:
                # Format yang didukung langsung
                logger.info(f"Audio format {file_ext} is supported directly")
                recognized_text, accuracy, feedback = recognize_speech(audio_file, reference_text, language)
                
        elif 'recorded-audio' in request.form and request.form['recorded-audio'] != '':
            # Menangani audio yang direkam dari browser (format base64)
            logger.info("Processing browser-recorded audio")
            
            # Dapatkan data base64 dan konversi ke file sementara
            audio_data = request.form['recorded-audio']
            
            # Format: "data:audio/webm;base64,ACTUAL_BASE64_DATA"
            if ',' in audio_data:
                header, audio_data = audio_data.split(',', 1)
                logger.info(f"Detected audio format from browser: {header}")
                
            try:
                # Simpan ke file sementara (format asli, kemungkinan webm)
                file_ext = '.webm'
                if 'audio/mp4' in header:
                    file_ext = '.mp4'
                elif 'audio/ogg' in header:
                    file_ext = '.ogg'
                
                logger.info(f"Using file extension: {file_ext} for browser audio")
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
                    temp_file.write(base64.b64decode(audio_data))
                    original_audio = temp_file.name
                    logger.info(f"Saved browser audio to temporary file: {original_audio}")
                
                # Konversi ke wav (format yang didukung oleh speech_recognition)
                wav_file = original_audio.replace(file_ext, '.wav')
                logger.info(f"Attempting to convert {file_ext} to WAV: {wav_file}")
                
                # Coba konversi menggunakan ffmpeg
                if ffmpeg_available and convert_audio_to_wav(original_audio, wav_file):
                    # Gunakan file wav yang sudah dikonversi
                    logger.info("Audio conversion successful, processing WAV file")
                    recognized_text, accuracy, feedback = recognize_speech(wav_file, reference_text, language)
                else:
                    # Jika konversi gagal atau ffmpeg tidak tersedia, coba gunakan WAV yang kompatibel
                    if not ffmpeg_available:
                        # Pesan yang lebih informatif jika ffmpeg tidak tersedia
                        logger.warning("FFmpeg tidak tersedia. Mencoba alternatif...")
                        error_message = ("Perangkat lunak FFmpeg tidak tersedia di sistem. "
                                        "Anda perlu menginstal FFmpeg untuk menggunakan fitur rekaman audio. "
                                        "Coba gunakan file audio berformat WAV sebagai alternatif.")
                        return render_template('speech.html', 
                                            error=error_message,
                                            reference_text=reference_text,
                                            language=language)
                    else:
                        # Jika ffmpeg tersedia tapi konversi gagal
                        logger.error("Failed to convert browser audio to WAV format")
                        recognized_text = "Error: Gagal mengkonversi rekaman audio"
                        accuracy = None
                        feedback = "Pastikan jenis audio yang direkam sudah benar. Coba unggah file audio WAV sebagai alternatif."
                    
                # Bersihkan file sementara
                logger.info("Cleaning up temporary files")
                if os.path.exists(original_audio):
                    os.remove(original_audio)
                if os.path.exists(wav_file):
                    os.remove(wav_file)
                    
            except Exception as e:
                logger.exception("Error processing browser audio")
                return render_template('speech.html', 
                                     error=f"Terjadi kesalahan saat memproses audio: {str(e)}",
                                     reference_text=reference_text,
                                     language=language)
        else:
            logger.info("No audio data received")
            return render_template('speech.html')
        
        logger.info(f"Speech recognition completed. Recognized text length: {len(recognized_text) if recognized_text else 0}")
        return render_template('speech.html',
                             recognized_text=recognized_text,
                             reference_text=reference_text,
                             accuracy=accuracy,
                             feedback=feedback,
                             language=language)
    return render_template('speech.html')

# Define a decorator to check if pretest is completed
def pretest_required(f):
    """Decorator that redirects to pretest if not completed"""
    def decorated_function(*args, **kwargs):
        # Check if user has completed pretest
        if not session.get('pretest_completed', False):
            # Store the original URL they were trying to access
            session['next_url'] = request.path
            flash('Anda perlu menyelesaikan pretest terlebih dahulu untuk menentukan level kemampuan Anda.', 'warning')
            return redirect(url_for('pretest'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/learning', methods=['GET', 'POST'])
@pretest_required
def learning():
    if 'user_level' not in session:
        session['user_level'] = 1
    
    if request.method == 'POST':
        answer = request.form.get('answer', '')
        question_id = request.form.get('question_id', '')
        correct, feedback, new_level = evaluate_answer(answer, question_id, session['user_level'])
        session['user_level'] = new_level
        
        return jsonify({
            'correct': correct,
            'feedback': feedback,
            'new_level': new_level
        })
    
    questions = get_questions(session['user_level'])
    materials = get_learning_materials(session['user_level'])
    return render_template('learning.html', questions=questions, user_level=session['user_level'], materials=materials)

@app.route('/pretest', methods=['GET', 'POST'])
def pretest():
    # If pretest is already completed, redirect to learning page
    if session.get('pretest_completed', False):
        return redirect(url_for('learning'))
    
    if request.method == 'POST':
        # Mendapatkan jawaban dari pengguna
        answers = request.get_json()
        
        # Evaluasi jawaban pretest
        language = session.get('language', 'en')
        result = evaluate_pretest_answers(answers, language)
        
        # Simpan hasil ke session
        session['user_level'] = result['level']
        session['pretest_completed'] = True
        session['pretest_result'] = result
        session['pretest_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Jika ada URL yang disimpan untuk redirect setelah pretest
        next_url = session.pop('next_url', None)
        if next_url:
            result['redirect_url'] = next_url
        else:
            result['redirect_url'] = url_for('index')
            
        return jsonify(result)
    
    # Mendapatkan soal pretest
    language = request.args.get('language', 'en')
    session['language'] = language
    questions = get_pretest_questions(language)
    
    return render_template('pretest.html', questions=questions, language=language)

@app.route('/post-test', methods=['GET', 'POST'])
@pretest_required
def post_test():
    if 'user_level' not in session:
        return redirect(url_for('learning'))
    
    if request.method == 'POST':
        # Mendapatkan jawaban dari pengguna
        answers = request.get_json()
        
        # Evaluasi jawaban post-test
        language = session.get('language', 'en')
        user_level = session.get('user_level', 1)
        result = evaluate_post_test_answers(answers, user_level, language)
        
        # Update level pengguna jika lulus
        if result['passed']:
            session['user_level'] = result['new_level']
        
        # Simpan hasil ke session
        if 'test_results' not in session:
            session['test_results'] = {}
        
        session['test_results'][f'post_test_level_{user_level}'] = {
            'score': result['score'],
            'percentage': result['percentage'],
            'passed': result['passed'],
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return jsonify(result)
    
    # Mendapatkan soal post-test untuk level pengguna
    user_level = session.get('user_level', 1)
    language = session.get('language', 'en')
    questions = get_post_test_questions(user_level, language)
    
    return render_template('post_test.html', questions=questions, level=user_level, language=language)

@app.route('/learning-materials', methods=['GET'])
@pretest_required
def learning_materials():
    user_level = session.get('user_level', 1)
    language = session.get('language', 'en')
    materials = get_learning_materials(user_level, language)
    
    return render_template('learning_materials.html', 
                          materials=materials, 
                          level=user_level,
                          language=language)

@app.route('/api/pretest', methods=['GET'])
def api_pretest():
    language = request.args.get('language', 'en')
    questions = get_pretest_questions(language)
    return jsonify(questions)

@app.route('/api/evaluate-pretest', methods=['POST'])
def api_evaluate_pretest():
    data = request.get_json()
    answers = data.get('answers', {})
    language = data.get('language', 'en')
    
    result = evaluate_pretest_answers(answers, language)
    return jsonify(result)

@app.route('/api/post-test', methods=['GET'])
def api_post_test():
    level = request.args.get('level', 1, type=int)
    language = request.args.get('language', 'en')
    
    questions = get_post_test_questions(level, language)
    return jsonify(questions)

@app.route('/api/evaluate-post-test', methods=['POST'])
def api_evaluate_post_test():
    data = request.get_json()
    answers = data.get('answers', {})
    level = data.get('level', 1, type=int)
    language = data.get('language', 'en')
    
    result = evaluate_post_test_answers(answers, level, language)
    return jsonify(result)

@app.route('/api/learning-materials', methods=['GET'])
def api_learning_materials():
    level = request.args.get('level', 1, type=int)
    language = request.args.get('language', 'en')
    
    materials = get_learning_materials(level, language)
    return jsonify(materials)

@app.route('/set-language', methods=['POST'])
def set_language():
    data = request.get_json()
    language = data.get('language', 'en')
    session['language'] = language
    return jsonify({'success': True})

@app.route('/api/grammar', methods=['POST'])
def api_grammar():
    data = request.get_json()
    text = data.get('text', '')
    language = data.get('language', 'en')
    
    corrected_text, explanations = correct_grammar(text, language)
    
    return jsonify({
        'original_text': text,
        'corrected_text': corrected_text,
        'explanations': explanations
    })

@app.route('/api/speech', methods=['POST'])
def api_speech():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    audio_file = request.files['audio']
    reference_text = request.form.get('reference_text', '')
    language = request.form.get('language', 'en')
    
    recognized_text, accuracy, feedback = recognize_speech(audio_file, reference_text, language)
    
    return jsonify({
        'recognized_text': recognized_text,
        'reference_text': reference_text,
        'accuracy': accuracy,
        'feedback': feedback
    })

@app.route('/api/questions', methods=['GET'])
def api_questions():
    level = request.args.get('level', 1, type=int)
    questions = get_questions(level)
    return jsonify(questions)

@app.route('/api/direct-speech', methods=['POST'])
def api_direct_speech():
    """API untuk pengenalan suara langsung tanpa FFmpeg, menggunakan browser untuk konversi format"""
    if request.method == 'POST':
        data = request.get_json()
        
        if not data or 'audio' not in data:
            return jsonify({'error': 'No audio data provided'}), 400
            
        audio_base64 = data.get('audio', '')
        reference_text = data.get('reference_text', '')
        language = data.get('language', 'en')
        
        # Process base64 audio directly with Google Speech API
        try:
            from speech_recognition import Recognizer, AudioData
            import io
            import base64
            
            # Decode base64 audio
            if ',' in audio_base64:
                audio_base64 = audio_base64.split(',')[1]
            
            audio_bytes = base64.b64decode(audio_base64)
            
            # Use speech_recognition to process audio bytes directly
            recognizer = Recognizer()
            
            # Simpan audio ke file sementara untuk diproses
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_wav:
                temp_wav.write(audio_bytes)
                temp_wav_path = temp_wav.name
                
            # Gunakan file audio yang disimpan
            with AudioData(temp_wav_path) as source:
                audio_data = recognizer.record(source)
            
            # Determine language code for speech recognition
            lang_code = "id-ID" if language == "id" else "en-US"
            
            # Use Google's speech recognition service
            try:
                print("Mencoba mengenali audio...")
                recognized_text = recognizer.recognize_google(audio_data, language=lang_code)
                print(f"Hasil pengenalan: {recognized_text}")
                
                # Calculate accuracy if reference text was provided
                accuracy = None
                feedback = None
                if reference_text:
                    from modules.speech_recognition import calculate_pronunciation_accuracy, generate_pronunciation_feedback
                    accuracy = calculate_pronunciation_accuracy(recognized_text, reference_text)
                    feedback = generate_pronunciation_feedback(recognized_text, reference_text, accuracy, language)
                
                return jsonify({
                    'recognized_text': recognized_text,
                    'reference_text': reference_text,
                    'accuracy': accuracy,
                    'feedback': feedback
                })
                
            except Exception as e:
                print(f"Error dalam pengenalan suara: {str(e)}")
                return jsonify({'error': f'Error in speech recognition: {str(e)}'}), 500
                
        except Exception as e:
            return jsonify({'error': f'Error processing audio: {str(e)}'}), 500
    
    return jsonify({'error': 'Invalid request'}), 400

@app.route('/evaluation', methods=['GET'])
def evaluation():
    return render_template('evaluation.html')

@app.route('/placement-test', methods=['GET', 'POST'])
def placement_test():
    if request.method == 'POST':
        # Mendapatkan jawaban dari pengguna
        answers = request.get_json()
        
        # Evaluasi jawaban
        result = evaluate_placement_test(answers)
        
        # Simpan hasil ke session
        session['placement_result'] = result
        session['placement_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return jsonify(result)
    
    # Mendapatkan soal tes penempatan
    test_questions = get_placement_test()
    return render_template('placement_test.html', questions=test_questions)

@app.route('/listening-test', methods=['GET', 'POST'])
def listening_test():
    if request.method == 'POST':
        # Mendapatkan jawaban dari pengguna
        answers = request.get_json()
        
        # Evaluasi jawaban
        result = evaluate_listening(answers)
        
        # Simpan hasil ke session
        if 'test_results' not in session:
            session['test_results'] = {}
        
        session['test_results']['listening'] = {
            'score': result['score'],
            'level': result['level'],
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return jsonify(result)
    
    # Mendapatkan soal tes mendengarkan
    test_questions = get_listening_test()
    return render_template('listening_test.html', questions=test_questions)

@app.route('/reading-test', methods=['GET', 'POST'])
def reading_test():
    if request.method == 'POST':
        # Mendapatkan jawaban dari pengguna
        answers = request.get_json()
        
        # Evaluasi jawaban
        result = evaluate_reading(answers)
        
        # Simpan hasil ke session
        if 'test_results' not in session:
            session['test_results'] = {}
        
        session['test_results']['reading'] = {
            'score': result['score'],
            'level': result['level'],
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return jsonify(result)
    
    # Mendapatkan soal tes membaca
    test_questions = get_reading_test()
    return render_template('reading_test.html', questions=test_questions)

@app.route('/speaking-test', methods=['GET', 'POST'])
def speaking_test():
    if request.method == 'POST':
        data = request.get_json()
        audio_data = data.get('audio', '')
        test_id = data.get('test_id', '')
        
        # Evaluasi jawaban
        result = evaluate_speaking(audio_data, test_id)
        
        # Simpan hasil ke session
        if 'test_results' not in session:
            session['test_results'] = {}
        
        session['test_results']['speaking'] = {
            'score': result['score'],
            'level': result['level'],
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return jsonify(result)
    
    # Mendapatkan soal tes berbicara
    test_questions = get_speaking_test()
    return render_template('speaking_test.html', questions=test_questions)

@app.route('/progress-report', methods=['GET'])
def progress_report():
    # Mengambil hasil tes dari session
    placement_result = session.get('placement_result', None)
    test_results = session.get('test_results', {})
    
    # Generate laporan perkembangan
    report = generate_progress_report(placement_result, test_results)
    
    return render_template('progress_report.html', report=report)

@app.route('/api/placement-test', methods=['GET'])
def api_placement_test():
    test_questions = get_placement_test()
    return jsonify(test_questions)

@app.route('/api/evaluate-placement', methods=['POST'])
def api_evaluate_placement():
    answers = request.get_json()
    result = evaluate_placement_test(answers)
    return jsonify(result)

@app.route('/api/listening-test', methods=['GET'])
def api_listening_test():
    test_questions = get_listening_test()
    return jsonify(test_questions)

@app.route('/api/reading-test', methods=['GET'])
def api_reading_test():
    test_questions = get_reading_test()
    return jsonify(test_questions)

@app.route('/api/speaking-test', methods=['GET'])
def api_speaking_test():
    test_questions = get_speaking_test()
    return jsonify(test_questions)

@app.route('/api/progress-report', methods=['GET'])
def api_progress_report():
    # Mengambil hasil tes dari request
    user_id = request.args.get('user_id')
    
    # Dalam implementasi nyata, ini akan mengambil data dari database berdasarkan user_id
    # Untuk contoh ini, kita gunakan data dummy
    placement_result = session.get('placement_result', None)
    test_results = session.get('test_results', {})
    
    # Generate laporan perkembangan
    report = generate_progress_report(placement_result, test_results)
    
    return jsonify(report)

# Routes untuk Tutor Virtual AI
@app.route('/virtual-tutor', methods=['GET'])
def virtual_tutor():
    return render_template('virtual_tutor.html')

@app.route('/api/virtual-tutor/chat', methods=['POST'])
def api_virtual_tutor_chat():
    # Ambil data dari request
    data = request.get_json()
    message = data.get('message', '')
    language = data.get('language', 'en')
    level = data.get('level', 'beginner')
    exercise_type = data.get('exercise_type', 'free_conversation')
    history = data.get('history', [])
    
    # Generate respons dari tutor virtual
    response = generate_chat_response(message, language, level, history, exercise_type)
    
    return jsonify(response)

@app.route('/api/virtual-tutor/speech', methods=['POST'])
def api_virtual_tutor_speech():
    # Ambil data dari request
    data = request.get_json()
    audio_data = data.get('audio', '')
    language = data.get('language', 'en')
    level = data.get('level', 'beginner')
    
    # Proses rekaman audio
    try:
        # Ekstrak audio dari base64
        if ',' in audio_data:
            audio_data = audio_data.split(',')[1]
        
        audio_bytes = base64.b64decode(audio_data)
        
        # Konversi audio ke WAV untuk processing
        with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_file:
            temp_file.write(audio_bytes)
            input_file = temp_file.name
        
        output_file = input_file.replace('.webm', '.wav')
        
        # Konversi ke WAV menggunakan ffmpeg
        if convert_audio_to_wav(input_file, output_file):
            # Gunakan modul speech recognition untuk mendapatkan transkrip
            from speech_recognition import Recognizer, AudioFile
            
            recognizer = Recognizer()
            with AudioFile(output_file) as source:
                audio = recognizer.record(source)
                
            # Pilih language code yang sesuai
            lang_code = "id-ID" if language == "id" else "en-US"
            if language == "jp":
                lang_code = "ja-JP"
                
            # Dapatkan transkrip
            try:
                print("Mencoba mengenali audio...")
                recognized_text = recognizer.recognize_google(audio, language=lang_code)
                print(f"Hasil pengenalan: {recognized_text}")
                
                # Generate feedback untuk speaking
                feedback_result = generate_speaking_feedback(recognized_text, language, level)
                
                # Tambahkan transkrip ke respons
                feedback_result['transcription'] = recognized_text
                
                # Bersihkan file sementara
                try:
                    os.remove(input_file)
                    os.remove(output_file)
                except:
                    pass
                    
                return jsonify(feedback_result)
                
            except Exception as e:
                logger.error(f"Error in speech recognition: {str(e)}")
                return jsonify({
                    "feedback": f"Maaf, saya tidak dapat mendengar dengan jelas. Silakan coba lagi dengan pengucapan yang lebih jelas. Error: {str(e)}",
                    "error": True
                })
        else:
            logger.error("Failed to convert audio to WAV format")
            return jsonify({
                "feedback": "Maaf, terjadi kesalahan saat memproses rekaman audio. Pastikan format audio didukung dan ffmpeg terinstal dengan benar.",
                "error": True
            })
            
    except Exception as e:
        logger.exception(f"Error processing speech for virtual tutor: {str(e)}")
        return jsonify({
            "feedback": f"Terjadi kesalahan: {str(e)}",
            "error": True
        })

@app.route('/api/virtual-tutor/languages', methods=['GET'])
def api_virtual_tutor_languages():
    # Mendapatkan daftar bahasa yang didukung
    languages = get_supported_languages()
    return jsonify(languages)

@app.route('/api/virtual-tutor/topics', methods=['GET'])
def api_virtual_tutor_topics():
    # Mendapatkan topik berdasarkan bahasa, level, dan jenis latihan
    language = request.args.get('language', 'en')
    level = request.args.get('level', 'beginner')
    exercise_type = request.args.get('exercise_type', 'free_conversation')
    
    if exercise_type == 'free_conversation':
        topics = get_conversation_topics(language, level)
    elif exercise_type == 'writing_exercise':
        topics = get_writing_prompts(language, level)
    elif exercise_type == 'speaking_practice':
        topics = get_speaking_topics(language, level)
    else:
        topics = []
        
    return jsonify(topics)

@app.route('/youtube-transcription', methods=['GET', 'POST'])
def youtube_transcription():
    if request.method == 'POST':
        youtube_url = request.form.get('youtube_url', '')
        language = request.form.get('language', 'en')
        
        if youtube_url:
            logger.info(f"Processing YouTube URL: {youtube_url}")
            api_key = os.getenv("YOUTUBE_API_KEY")
            transcript, accuracy, feedback = get_youtube_transcript(youtube_url, api_key)
            
            return render_template('youtube_transcription.html',
                                transcript=transcript,
                                youtube_url=youtube_url,
                                accuracy=accuracy,
                                feedback=feedback,
                                language=language)
    
    return render_template('youtube_transcription.html')

@app.route('/reset', methods=['GET'])
def reset_data():
    # Hapus data pretest dan pembelajaran dari session
    if 'pretest_completed' in session:
        session.pop('pretest_completed')
    if 'user_level' in session:
        session.pop('user_level')
    if 'pretest_result' in session:
        session.pop('pretest_result')
    if 'pretest_date' in session:
        session.pop('pretest_date')
    if 'test_results' in session:
        session.pop('test_results')
    
    # Tambahkan flash message
    flash('Data pembelajaran Anda telah direset. Silahkan ambil pretest untuk menentukan level baru.', 'info')
    
    # Redirect ke halaman utama
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
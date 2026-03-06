from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
from pathlib import Path
import threading

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), '..', 'frontend'))
CORS(app)

# Configuration
DOWNLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'downloads')
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Get configuration from environment variables
PORT = int(os.environ.get('PORT', 5000))
HOST = os.environ.get('HOST', '0.0.0.0')

# Store download progress
download_progress = {}

def get_video_info(url):
    """Fetch video information from YouTube URL"""
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Extract format information
            formats = []
            for fmt in info.get('formats', []):
                if fmt.get('vcodec') != 'none' and fmt.get('acodec') != 'none':
                    formats.append({
                        'format_id': fmt.get('format_id'),
                        'height': fmt.get('height'),
                        'fps': fmt.get('fps'),
                        'ext': fmt.get('ext'),
                    })
            
            # Remove duplicates and sort by height
            unique_formats = {}
            for fmt in formats:
                height = fmt['height']
                if height and (height not in unique_formats or fmt['fps'] > unique_formats[height]['fps']):
                    unique_formats[height] = fmt
            
            qualities = sorted([(h, unique_formats[h]) for h in unique_formats.keys()], 
                             key=lambda x: x[0], reverse=True)
            
            return {
                'title': info.get('title'),
                'duration': info.get('duration'),
                'thumbnail': info.get('thumbnail'),
                'qualities': [{'height': h, 'format_id': q['format_id']} for h, q in qualities[:5]],
                'success': True
            }
    except Exception as e:
        return {'success': False, 'error': str(e)}


@app.route('/api/video-info', methods=['POST'])
def video_info():
    """Get video information"""
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({'success': False, 'error': 'URL is required'}), 400
    
    info = get_video_info(url)
    return jsonify(info)


def progress_hook(d):
    """Progress hook for download"""
    if d['status'] == 'downloading':
        try:
            download_progress['progress'] = d.get('_percent_str', '0%')
            download_progress['speed'] = d.get('_speed_str', 'N/A')
            download_progress['eta'] = d.get('_eta_str', 'N/A')
        except:
            pass
    elif d['status'] == 'finished':
        download_progress['progress'] = '100%'


@app.route('/api/download', methods=['POST'])
def download():
    """Download video"""
    data = request.json
    url = data.get('url')
    quality = data.get('quality')  # '720p', '480p', etc.
    audio_only = data.get('audio_only', False)
    
    if not url:
        return jsonify({'success': False, 'error': 'URL is required'}), 400
    
    download_progress.clear()
    download_progress['progress'] = '0%'
    
    try:
        # Determine format selection
        if audio_only:
            format_selection = 'bestaudio/best'
            output_template = os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s')
        else:
            if quality == 'best':
                format_selection = 'bestvideo+bestaudio/best'
            else:
                # Extract height from quality string (e.g., "720p" -> "720")
                height = quality.replace('p', '') if quality else '720'
                format_selection = f'bestvideo[height<={height}]+bestaudio/best'
            
            output_template = os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s')
        
        # Build basic options
        ydl_opts = {
            'format': format_selection,
            'outtmpl': output_template,
            'progress_hooks': [progress_hook],
            'quiet': False,
            'no_warnings': False,
        }
        
        # audio-only postprocessor configuration
        if audio_only:
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            return jsonify({
                'success': True,
                'message': 'Download completed',
                'filename': os.path.basename(filename)
            })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/progress', methods=['GET'])
def get_progress():
    """Get download progress"""
    return jsonify(download_progress)


@app.route('/api/downloads', methods=['GET'])
def list_downloads():
    """List all downloaded files"""
    try:
        files = os.listdir(DOWNLOAD_FOLDER)
        downloads = []
        for f in files:
            file_path = os.path.join(DOWNLOAD_FOLDER, f)
            if os.path.isfile(file_path):
                size = os.path.getsize(file_path)
                downloads.append({
                    'filename': f,
                    'size': size,
                    'size_mb': round(size / (1024*1024), 2)
                })
        return jsonify({'success': True, 'downloads': downloads})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({'status': 'ok'})


@app.route('/')
def serve_frontend():
    """Serve the frontend"""
    frontend_path = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'index.html')
    with open(frontend_path, 'r', encoding='utf-8') as f:
        return f.read()


if __name__ == '__main__':
    app.run(debug=False, host=HOST, port=PORT)

from flask import Flask, send_file, render_template_string
import os

app = Flask(__name__)
RECORDINGS_DIR = './recordings'

@app.route('/recordings')
def list_recordings():
    files = os.listdir(RECORDINGS_DIR)
    html = "<h2>Recorded Videos</h2><ul>"
    for f in files:
        html += f'<li><a href="/play/{f}">{f}</a></li>'
    html += "</ul>"
    return render_template_string(html)

@app.route('/play/<filename>')
def play_recording(filename):
    return send_file(os.path.join(RECORDINGS_DIR, filename), mimetype='video/mp4')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
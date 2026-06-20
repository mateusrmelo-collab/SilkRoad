from flask import Flask, render_template, request, send_file, after_this_request
import yt_dlp
import os
import uuid

app = Flask(__name__)

DOWNLOAD_DIR = "/tmp"

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/baixar", methods=["POST"])
def baixar():
    url = request.form.get("url")
    tipo = request.form.get("tipo")

    if not url:
        return "URL inválida", 400

    uid = str(uuid.uuid4())
    base_path = os.path.join(DOWNLOAD_DIR, uid)

    try:
        if tipo == "audio":
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": base_path + ".%(ext)s",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
                "quiet": True,
            }
        else:
            ydl_opts = {
                "format": "best[ext=mp4]/best",
                "outtmpl": base_path + ".%(ext)s",
                "quiet": True,
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        filename = ydl.prepare_filename(info)

        if tipo == "audio":
            filename = os.path.splitext(filename)[0] + ".mp3"

        @after_this_request
        def cleanup(response):
            try:
                if os.path.exists(filename):
                    os.remove(filename)
            except:
                pass
            return response

        return send_file(filename, as_attachment=True)

    except Exception as e:
        return f"Erro: {str(e)}", 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
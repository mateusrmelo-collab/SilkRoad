from flask import Flask, render_template, request, send_file
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
        ydl_opts = {
            "outtmpl": base_path + ".%(ext)s",
            "quiet": False,
            "noplaylist": True,
        }

        if tipo == "audio":
            ydl_opts.update({
                "format": "bestaudio/best",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
            })
        else:
            ydl_opts.update({
                "format": "best[ext=mp4]/best",
            })

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

            filename = ydl.prepare_filename(info)

            if tipo == "audio":
                filename = os.path.splitext(filename)[0] + ".mp3"

        if not os.path.exists(filename):
            return "Falha no download", 500

        return send_file(filename, as_attachment=True)

    except Exception as e:
        return f"Erro: {str(e)}", 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
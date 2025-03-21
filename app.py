import os
import nbformat
import pypandoc
import pandas as pd
import markdown2
import json
import shutil
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
from nbconvert import PythonExporter
from docx import Document
from pdf2docx import Converter
from PIL import Image
from json2html import *
from moviepy.editor import VideoFileClip
from pydub import AudioSegment

app = Flask(__name__)
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# 📌 File conversion functions
def convert_ipynb_to_py(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        notebook = nbformat.read(f, as_version=4)
    py_exporter = PythonExporter()
    body, _ = py_exporter.from_notebook_node(notebook)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(body)

def convert_docx_to_pdf(input_path, output_path):
    pypandoc.convert_file(input_path, "pdf", outputfile=output_path)

def convert_pdf_to_docx(input_path, output_path):
    cv = Converter(input_path)
    cv.convert(output_path, start=0, end=None)
    cv.close()

def convert_image(input_path, output_path):
    img = Image.open(input_path)
    img.save(output_path)

def convert_audio(input_path, output_path):
    audio = AudioSegment.from_file(input_path)
    audio.export(output_path, format=output_path.split('.')[-1])

def convert_video_to_gif(input_path, output_path):
    clip = VideoFileClip(input_path)
    clip.write_gif(output_path)

# 🎨 UI ROUTE
@app.route("/")
def home():
    return render_template("index.html")

# 🔄 FILE UPLOAD + CONVERSION ROUTE
@app.route("/convert", methods=["POST"])
def convert():
    uploaded_file = request.files["file"]
    target_format = request.form["format"]
    
    if uploaded_file.filename == "":
        return "❌ No file selected!"

    filename = secure_filename(uploaded_file.filename)
    input_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    uploaded_file.save(input_path)

    output_filename = f"{os.path.splitext(filename)[0]}.{target_format}"
    output_path = os.path.join(app.config["UPLOAD_FOLDER"], output_filename)

    # 🔥 Mapping conversions
    conversions = {
        ("ipynb", "py"): convert_ipynb_to_py,
        ("docx", "pdf"): convert_docx_to_pdf,
        ("pdf", "docx"): convert_pdf_to_docx,
        ("png", "jpg"): convert_image,
        ("jpg", "png"): convert_image,
        ("webp", "png"): convert_image,
        ("mp3", "wav"): convert_audio,
        ("wav", "mp3"): convert_audio,
        ("mp4", "gif"): convert_video_to_gif
    }

    input_ext = filename.split(".")[-1].lower()
    
    if (input_ext, target_format) in conversions:
        conversions[(input_ext, target_format)](input_path, output_path)
        return send_file(output_path, as_attachment=True)
    
    return "❌ Unsupported file conversion!"

if __name__ == "__main__":
    app.run(debug=True)

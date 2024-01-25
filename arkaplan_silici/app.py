from flask import Flask, render_template, request, send_file, redirect, url_for
from rembg import remove
from PIL import Image
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return render_template('index.html', error='No file part')

    file = request.files['file']

    if file.filename == '':
        return render_template('index.html', error='No selected file')

    if file and allowed_file(file.filename):
        # Ensure the uploads folder exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        # Save the uploaded file
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(input_path)

        # Make the background removal
        input_image = Image.open(input_path)
        output_image = remove(input_image)

        # Make the background transparent
        output_image = output_image.convert("RGBA")
        data = output_image.getdata()
        new_data = [(r, g, b, 0) if r == 0 and g == 0 and b == 0 else (r, g, b, a) for (r, g, b, a) in data]
        output_image.putdata(new_data)

        # Save the output image as PNG instead of JPEG
        filename_without_extension, extension = os.path.splitext(file.filename)
        output_filename = f'ege_{filename_without_extension.replace(" ", "_").lower()}.png'
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        output_image.save(output_path, format="PNG")

        return redirect(url_for('download_file', filename=output_filename))

    return render_template('index.html', error='Invalid file format')

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    output_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

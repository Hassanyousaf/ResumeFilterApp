from flask import Flask, request, render_template, send_from_directory, redirect, url_for
import os
from resume_filter import ResumeFilter  # Your main resume filter class
import tempfile
import shutil

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        job_description = request.form['job_description']
        mandatory_keywords = request.form['mandatory_keywords'].split(',')
        optional_keywords = request.form['optional_keywords'].split(',')
        min_experience = float(request.form['min_experience'])

        resume_filter = ResumeFilter(job_description, mandatory_keywords, optional_keywords, min_experience)

        temp_dir = tempfile.mkdtemp()
        uploaded_files = []

        for file in request.files.getlist('resumes'):
            filepath = os.path.join(temp_dir, file.filename)
            file.save(filepath)
            uploaded_files.append((file.filename, filepath))

        results = resume_filter.process_resumes(temp_dir)

        # Copy matching resumes to UPLOAD_FOLDER for download
        for res in results:
            original_path = os.path.join(temp_dir, res['filename'])
            dest_path = os.path.join(UPLOAD_FOLDER, res['filename'])
            shutil.copyfile(original_path, dest_path)

        shutil.rmtree(temp_dir)

        return render_template('results.html', resumes=results, min_experience=min_experience, job_description=job_description)

    return render_template('upload.html')


@app.route('/download/<path:filename>')
def download_resume(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, redirect, render_template, request, url_for, flash,render_template_string
from werkzeug.utils import secure_filename
import pandas as pd
from package import pipeline_multi, pipeline_uni
from package.utils.utils import generate_results
import webbrowser

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'csv', 'txt'}
app.config['UPLOAD_FOLDER'] = './'
app.config['SECRET_KEY'] = 'f3cfe9ed8fae309f02079dbf'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def welcome():
    return render_template('home.html')

@app.route('/solution_uni' ,methods=['GET','POST'])
def solution_uni():
    return render_template('solution_uni.html')

@app.route('/solution_multi',methods=['GET','POST'])
def solution_multi():
    return render_template('solution_multi.html')

@app.route('/results')
def results():
    return render_template('results.html')

@app.route('/uni_form', methods=['POST'])
def uni_form():
    data = request.form.to_dict(flat=False)
    coord_input_uni = []
    for i in range(len(data)//2):
        latitude = data.get('latitude'+str(i+1),['fail'])[0]
        longitude = data.get('longitude'+str(i+1),['fail'])[0]
        try:
            coord_input_uni.append((float(latitude),float(longitude)))
        except:
            continue
    if len(coord_input_uni) == 0:
        return render_template('solution_uni.html')
    results = pipeline_uni(coord_input_uni)
    html_file = generate_results(results, './user_interface/templates/layout.html','./map.html','./user_interface/templates/results.html')
    return render_template_string(html_file)

@app.route('/uni_csv', methods=['POST','GET'])
def uni_csv():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            csv_file = pd.read_csv(file)
            coord_csv_uni = list(zip(csv_file.lat, csv_file.lng))
            flash('file successfully upload')
            if len(coord_csv_uni) == 0:
                return render_template('solution_uni.html')
            results = pipeline_uni(coord_csv_uni)
            html_file = generate_results(results, './user_interface/templates/layout.html','./map.html','./user_interface/templates/results.html')
        return render_template_string(html_file)

    
    return '''
    <!doctype html>
    <title>Confirm the Upload</title>
    <h1>Confirm the Upload</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''


@app.route('/multi_form', methods=['POST','GET'])
def multi_form():#faire la récupération
    data = request.form.to_dict(flat=False)
    coord_input_multi = []
    for i in range(len(data)//4):
        latitude1 = data.get('1latitude'+str(i+1),['fail'])[0]
        longitude1 = data.get('1longitude'+str(i+1),['fail'])[0]
        latitude2 = data.get('2latitude'+str(i+1),['fail'])[0]
        longitude2 = data.get('2longitude'+str(i+1),['fail'])[0]
        try:
            coord_input_multi.append(((float(latitude1),float(longitude1)),(float(latitude2),float(longitude2))))
        except:
            continue
    if len(coord_input_multi) == 0:
            return render_template('solution_multi.html')
    results = pipeline_multi(coord_input_multi)
    html_file = generate_results(results, './user_interface/templates/layout.html','./map.html','./user_interface/templates/results.html')
    return render_template_string(html_file)


@app.route('/multi_csv', methods=['POST','GET'])
def multi_csv():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            csv_file = pd.read_csv(file, usecols=['lat1','lng1','lat2','lng2'])
            coord_csv_multi = list(zip(zip(csv_file.lat1, csv_file.lng1),zip(csv_file.lat2, csv_file.lng2)))
            if len(coord_csv_multi) == 0:
                return render_template('solution_multi.html')
            results = pipeline_multi(coord_csv_multi)
            html_file = generate_results(results, './user_interface/templates/layout.html','./map.html','./user_interface/templates/results.html')
            return render_template_string(html_file)
    return '''
    <!doctype html>
    <title>Confirm upload</title>
    <h1>Confirm upload</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''
if __name__ == "__main__":
    app.run()

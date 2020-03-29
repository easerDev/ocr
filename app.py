from flask import Flask, flash, request, redirect, render_template,jsonify
from engine import returnPrediction
from engine import rectoPermisEuropeenRecto,versoPermisEuropeenRecto,lectureFichier
import pickle
import requests 
import pandas as pd
import urllib.request
from werkzeug.utils import secure_filename

#################################
import io
import os
import sys
import json

# Imports the Google Cloud client library
from google.cloud import vision
from google.cloud.vision import types
from google.protobuf.json_format import MessageToJson
from IPython.display import Image, display

import base64
import codecs
#################################

app = Flask(__name__)

#################################
print(os.listdir())
model = pickle.load(open("./toload/svcIris.p", 'rb'))
# Instantiates a client
client = vision.ImageAnnotatorClient()

UPLOAD_FOLDER = './uploads'
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

@app.route("/")
def hello():
    print('hello')
    return "Hello World!"

@app.route('/test/<uuid>', methods=['GET', 'POST'])
def test(uuid):
    #content = request.json
    #print content['mytext']
    return jsonify({"test":uuid})

@app.route('/prediction/<sepal_length>/<sepal_width>/<petal_length>/<petal_width>', methods=['GET', 'POST'])
def prediction(sepal_length,sepal_width,petal_length,petal_width):
    content = request.json
    if pd.notnull(content) and 'sepal.width' in content.keys():
        return jsonify({"prediction":returnPrediction(model=model,entree=content)   })

    else:
        return jsonify({"prediction":returnPrediction(model=model,entree={'sepal.length':sepal_length,
                                    'sepal.width':sepal_width,
                                    'petal.length':petal_length,
                                    'petal.width':petal_width})   })

    
 
    
@app.route('/traitementImage', methods=['POST'])
def traitementImage():
    content = request.json['file']
    
    retour = lectureFichier(client,content=content)
    #return(jsonify({'typeFichier' : type(content)}))
    return(jsonify(retour))
    #return jsonify(lectureFichier(client,content=content))

###################################################################################
@app.route('/maStartuP')
def maStartuP():
    return render_template('templateStartUp.html')


###################################################################################
def allowed_file(filename):
    return('.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS)

@app.route('/testVisuel')
def upload_form():
    return render_template('upload.html')

@app.route('/testVisuel', methods=['POST'])
def upload_file():
    #print('request.method : ',request.method )
    #print("request.method == 'POST' : ",request.method == 'POST' )
    #print('file not in request.files : ',str('file' not in request.files) )    
    #print(dir(request))
    
    
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' in request.files:    
            #######################################################################################
            #TRAITEMENT DUN FICHIER IMAGE PDF
            file = request.files['file']
            if file.filename == '':
                #print('No file selected for uploadingt')
                flash('No file selected for uploading')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                #print('File successfully uploaded')
                #print(file.filename)
                #print(app.config['UPLOAD_FOLDER'])
                #print(os.listdir())
                filename = secure_filename(file.filename)
                cheminFichier = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(cheminFichier)
                flash('File successfully uploaded')
                retour = lectureFichier(client,chemin=cheminFichier)
                #return(jsonify({'typeFichier' : type(content)}))
                #return(jsonify(retour))
                print(type(retour))
                for k in dir(retour) : print(k)
                print(retour.values)    
                print(retour.keys)
                print(retour)
                print(jsonify(retour))  
                try:
                    print('C')
                    print(json.dumps(retour))   
                except:
                    pass
                
                try:
                    print('D')
                    print(json.dumps(jsonify(retour)))                          
                except:
                    pass
                          
                return(render_template('upload.html',
                                       #retour_image=retour,
                                       #retour_image2=jsonify(retour),
                                       #retour_image3=json.dumps(retour),
                                       retour_image4=json.dumps(retour, sort_keys = True, indent = 4, separators = (',', ': '))
                                      ))
              
                #return redirect('/')
                #return redirect(request.url)
            else:
                flash('Allowed file types are txt, pdf, png, jpg, jpeg, gif')
                return redirect(request.url)
        else:
            #######################################################################################
            #PREDICTION DUN IRIS
            print('request.method : ',request.method )
            #print('request.body : ',request.body )
            for k in dir(request):
                print(k)
                
            print(request.json)
            print('request.values : ',request.values)
            print('type values : ',type(request.values))
            print('sepal.length : ',request.values['sepal.length'])
            print('sepal.length : ',float(request.values['sepal.length']))
           
            prediction = returnPrediction(model=model,entree={'sepal.length':request.values['sepal.length'],
                                    'sepal.width':request.values['sepal.width'],
                                    'petal.length':request.values['petal.length'],
                                    'petal.width':request.values['petal.width']})
            retour = str('La variété prédite pour ' +'sepal.length : ' + request.values['sepal.length']
                            +', sepal.width : ' + request.values['sepal.width']
                            +', petal.length : ' + request.values['petal.length']
                            +' et petal.width : ' + request.values['petal.width'] + ' est ' + prediction)
            
            #return(render_template('upload.html', prediction_text='{}'.format(prediction)))
            return(render_template('upload.html', prediction_text=retour))
                                   
            #return jsonify({"prediction":returnPrediction(model=model,entree={'sepal.length':request.values['sepal.length'],
            #                        'sepal.width':request.values['sepal.width'],
            #                        'petal.length':request.values['petal.length'],
            #                        'petal.width':request.values['petal.width']})   })
            
            
           
            if 'file' not in request.files:
                #print('No file part')
                flash('No file part')
                return redirect(request.url)
            
            
            
     #'''
    
@app.route('/testVisuel', methods=['POST'])
def connaitreVariete():
    print('request.method : ',request.method )
    print('request.content : ',request.content )
    content = request.json
    if pd.notnull(content) and 'sepal.width' in content.keys():
        return jsonify({"prediction":returnPrediction(model=model,entree=content)   })

    else:
        return jsonify({"prediction":returnPrediction(model=model,entree={'sepal.length':sepal_length,
                                    'sepal.width':sepal_width,
                                    'petal.length':petal_length,
                                    'petal.width':petal_width})   })       
    
    
    
if __name__ == '__main__':
    #app.run(debug=True)
    #app.run(host='104.199.70.23',port=8080,debug=True)
    print('http://104.199.70.23:8080/')
    print('http://104.199.70.23:8080/testVisuel')
    print('http://104.199.70.23:8080/maStartuP')
    
    
    app.run(host='0.0.0.0',port=8080,debug=True)
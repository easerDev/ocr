from google.cloud import vision
from google.cloud.vision import types
import json
from google.protobuf.json_format import MessageToJson
import os
import io
import base64
import codecs

def returnPrediction(model,entree):
    t = [entree['sepal.length'],entree['sepal.width'],
                  entree['petal.length'],entree['petal.width']]
    
    return(model.predict([t])[0])

####################################################
def rectoPermisEuropeenRecto(x):
    nom = x[x.find('\n1.')+4:x.find('\n2')]
    prenom = x[(x.find('\n2.'))+4:x.find('\n3')]
    dateNaissance = x[(x.find('\n3.')+4):(x.find('\n3.')+4+10)]
    villeNaissance = x[(x.find('\n3.')+15):x.find('\n4')].replace('(','').replace(')','')
    dateDelivranceDocument = x[x.find('\n4a')+4:(x.find('\n4a')+14)]
    dateExpirationDocument = x[x.find('\n4b')+4:(x.find('\n4b')+14)]
    numeroPermis = x[x.find('\n5')+4:(x.find('\na'))]
    referenceFin = x[len(x)-34:].replace('\n','')
    
    return({'type':'versoPermisEuropeen',
           'infos' : {'nom':nom,
           'prenom':prenom,
           'dateNaissance':dateNaissance,
           'villeNaissance':villeNaissance,
           'dateDelivranceDocument':dateDelivranceDocument,
           'dateExpirationDocument':dateExpirationDocument,
           'numeroPermis':numeroPermis,
           'referenceFin': referenceFin}})
    
def versoPermisEuropeenRecto(x):
    dates = []
    for i in range(0,len(x)):
        #print('####')
        temp = str(x[i:(i+8)])
        if len(temp)>=8 and temp[2]=='.' and temp[5]=='.' and '\n' not in temp:
            dates.append(temp)
    return({'type':'versoPermisEuropeen',
            'infos' : {'dates' : dates}})
    
    
def lectureFichier(client,chemin='',content=''):    
    if chemin!='':
        file_name = os.path.abspath(chemin)
        try:display(Image(filename=chemin))
        except:pass
        # Loads the image into memory
        with io.open(file_name, 'rb') as image_file:
            content = image_file.read()
    if type(content)==str:
        content = base64.b64decode(content)
    image = types.Image(content=content)
    # Performs label detection on the image file
    #response = client.label_detection(image=image)
    description = json.loads(MessageToJson(client.document_text_detection(image=image)))['textAnnotations'][0]['description']
    if 'PERMIS DE CONDUIRE RÉPUBLIQUE FRANÇAISE' in description:
        return(rectoPermisEuropeenRecto(description))
    elif '1. Nom 2. Prénom 3. Date et lieu de n'.replace(' ','') in description.replace(' ',''):
        print('verso Permis')
        return(versoPermisEuropeenRecto(description))
    else:
        return({'description':description})
####################################################

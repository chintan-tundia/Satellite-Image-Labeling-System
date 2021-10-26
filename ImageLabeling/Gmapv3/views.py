#from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from django.http import JsonResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext
from django.core.files import File
from django.core import serializers
from Gmapv3.models import Image
from Gmapv3.models import GMapMarker
from Gmapv3.models import Annotation
from Gmapv3.models import WorkType
from Gmapv3.models import DeptName
from Gmapv3.models import DistrictName
from Gmapv3.models import JSMappedWorks
from Gmapv3.models import JSMappedWorksImage

from django.db import models
from django.db.models import Q
from django.db.models import Count
from django.db import connection
import sys
import cv2
import os
from os import listdir
from os.path import isfile, join
import base64
import datetime
from datetime import datetime as dttm
import json
import base64
import pandas as pd 
import math
import imutils
import numpy as np
import shutil
import requests
from pathlib import Path
import glob
import zipfile
import enum 
from datetime import date
from datetime import datetime
from shutil import copyfile


from django.contrib.gis.gdal import OGRGeometry
from django.contrib.gis.geos import Polygon
from django.contrib.gis.geos import LineString
from django.contrib.gis.geos import Point

class FarmPondLabel(enum.Enum):     
    WetFPLined = 0 #cyan
    WetFPUnlined = 1 #green
    DryFPLined = 2 #red
    DryFPUnlined = 3 #yellow

class CheckdamLabel(enum.Enum):     
    WallBasedCD = 0 
    GateBasedCD = 1 
    
    

WORKTYPE_MARATHI = ["अनघड दगडी बांध" ,"ओढा/ नाले / कॅनॉल जोड प्रकल्प" ,"कंपार्टमेन्ट बंडीग" ,"कालवा दुरुस्त करणे" ,\
    "कोल्हापूर टाईप बंधारा/साठवण बंधारा दुरुस्ती" ,"खोल सलग समतल चर" ,"गाळ काढणे (गाव तलाव)" ,"गाळ काढणे (पाझर तलाव)" ,\
    "गाळ काढणे (माजी मालगुजारी तलाव)" ,"गाळ काढणे (शिवकालीन तलाव)" ,"गाळ काढणे (सिमेंट बंधारा/माती नाला बांध)" ,"गुरे प्रतिबंधक चर",\
    "गॅबियन बंधारे" ,"ग्रेडेड बंडींग" ,"जुने सिमेंट काँक्रिट नाला बांध"  ,"जुन्या जलस्त्रोतांची दुरुस्ती ( माती नाला बांध / स" ,\
    "झरा बळकटीकरण करणे" ,"ट्रेंच गॅलरी करणे" ,"ठिबक सिंचन" ,"तुषार सिंचन" ,"दगडी ताल बांधणे" ,"नाला खोलीकरण" ,\
    "नैसर्गिक जलस्त्रोत बळकटीकरण" ,"नैसर्गिक पाण्याच्या स्त्रोत्रांचे झ-यांचे सभोवती" ,"पाझर तलाव दुरुस्ती (COT/सांडवा/इतर दुरुस्ती)",\
    "पुर्नभरण चर" ,"बोडी दुरुस्ती" ,"भातखचरे पुर्नजीवन" ,"मजगी" ,"माजी मालगुजारी तलाव दुरुस्ती" ,"माती नाला बांध" ,"रिचार्ज शाफ्ट",\
    "लहान मातीचा बांध" ,"वनतळी" ,"वनीकरण/वृक्ष लागवड" ,"वन्यप्राणी प्रतिबंधक चर" ,"वळण बंधारा"  ,"विंधन विहीर पुनर्भरण करणे" ,\
    "विहीर पुर्नभरण करणे" ,"शेततळे"  ,"सलग समतल चर" ,"सिमेंट काँक्रीट नाला बांध" ,"हायड्रो फ्रॅक्चरींग","NA" ]

WORKTYPE_ENGLISH = ["Loose Boulder Structure","Stream / Canal / Canal Joints Project",\
"Compartment bunding","Canal Repair","KT Weir / Storage Bandhara Repair","Deep CCT",\
"Nala Desiliting (village tank)","Nala Desiliting (percolation tank)",\
"Nala Desiliting (Former Malugari tank)","Nala Desiliting (Shiva Winter tank)",\
"Nala Desiliting (Cement bandhara / Earthern Nala Bandh)","TCM","Gabion bandhara",\
"Graded bunding","Old CNB","Repair of old water bodies (Earthern Nala Bund / )","Stream Strengthening",\
"Trench Gallery","Drip irrigation","Sprinkler irrigation","Rock bunding","Nala Deepening",\
"Strengthening Natural Water Resources","Stream Surrounding Natural Water Sources",\
"PT Repairing (COT / Sandwa / Other Repairs)","Refill variable","Body Repair (unclear translation)" ,\
"Rice Field Rejuvination","Majagi","Former Malgujari Talav Repair (unclear translation)",\
"Earthern Nala Bund","Recharge shaft","Small earthen Bund","Forest pond","Afforestation / Plantation",\
"TCM 2 / Wildlife protection char (unclear translation)","Turning bandhara","Vindhan Well rehabilitation",\
"Well rehabilitation","Farm Pond","CCT","Cement Concrete Nala Bandh","Hydro Fracturing","NA"]    

DEPTNAME_MARATHI = ["कृषि","वन","लघु सिंचन (जलसंधारण)","लघु सिंचन जिल्हा परिषद","जलसंपदा",\
"पाणी पुरवठा व स्वच्छता विभाग जिल्हा परीषद","भुजल सर्वेक्षण व विकास यंत्रणा","ग्रामपंचायत विभाग",\
"सामाजिक वनीकरण","जलसंपदा (यांत्रिकी)","जलसंपदा (लघु पाटबंधारे विभाग)","कृषि (जिल्हा परिषद)","पंचायत समिती","महसूल","वन्यजीव"];

DISTRICTNAME_MARATHI=["अकोला","अमरावती","अहमदनगर","उस्मानाबाद","औरंगाबाद","कोल्हापूर","गडचिरोली","गोंदिया","चंद्रपूर",\
"जळगाव","जालना","ठाणे","धुळे","नंदुरबार","नांदेड","नागपूर","नाशिक","परभणी","पालघर","पुणे","बीड","बुलडाणा","भंडारा","यवतमाळ",\
"रत्नागिरी","रायगड","लातूर","वर्धा","वाशिम","सांगली","सातारा","सिंधुदुर्ग","सोलापूर","हिंगोली","मुंबई","मुंबई उपनगर"]

DISTRICTNAME_ENGLISH=["Akola","Amravati","Ahmednagar","Usmanabad","Aurangabad","Kolhapur","Gadchiroli",\
"Gondiya","Chandarpur","Jalgaon","Jalna","Thane","Dhule","Nandurbar","Nanded","Nagpur","Nashik",\
"Parbhani","Palghar","Pune","Beed","Buldhana","Bhandara","Yavatmal","Ratnagiri","Raigadh","Latur",\
"Wardha","Vashim","Sangli","Satara","Sindhudurg","Solapur","Hingoli","Mumbai","Mumbai Suburb"]

def testCode(request):
    respText = {}    
    try:
        allImages = Image.objects.filter(Q(annotation__class_label="Wall Based Checkdam")|\
                             Q(annotation__class_label="Gate Based Checkdam"))\
                            .distinct().values_list('image_name',flat=True)
        location = 'static/Gmapv3/images/Checkdams/zoom19/';
        onlyfiles = [f for f in listdir(location) if isfile(join(location, f))]        
        mismatch=[]
        success=0
        allImages = list(allImages)        
        print("Total in DB",len(allImages))
        print("Total in Files",len(onlyfiles))
        for f in onlyfiles:
            success=0
            for aI in allImages:
                if(f==aI):
                    success = 1
            if(success==0):
                mismatch.append(f)
        respText=mismatch              

    except Exception as e: # work on python 2.x
        print(e)
    return HttpResponse(respText)

def index(request):    
    template = loader.get_template('Gmapv3/index.html')        
    context = {}
    return HttpResponse(template.render(context, request))

def labelDataset(request):
    template = loader.get_template('Gmapv3/labelDataset.html')    
    # allMarkers = GMapMarker.objects.all()
    DISTRICTNAME_ENGLISH.sort()
    context = {  
        'districtNames':DISTRICTNAME_ENGLISH
        #'allMarkers':allMarkers,        
    }    
    return HttpResponse(template.render(context, request)) 

def displayImagesDataset(request):
    template = loader.get_template('Gmapv3/displayDataset.html')    
    savedImgName = request.GET.get("savedImgName")
    if(savedImgName==None):
        savedImgName = ""
    # imgs = Image.objects.filter(is_annotated=False)
    imgs = Image.objects.filter(Q(annotation__class_label="Well")|\
                                Q(annotation__class_label="Wet Farm Pond - Lined")|\
                                Q(annotation__class_label="Wet Farm Pond - Unlined")|\
                                Q(annotation__class_label="Dry Farm Pond - Lined")|\
                                Q(annotation__class_label="Dry Farm Pond - Unlined")|\
                                Q(annotation__class_label="Wall Based Checkdam")|\
                                Q(annotation__class_label="Gate Based Checkdam"))
    imgs = imgs.filter(derived_from_image=None).distinct().extra(order_by = ['image_name']);    
    totalImages = imgs.count();
    # imgs = Image.objects.all().extra(order_by = ['-captured_date']);    
    wells=Annotation.objects.filter(class_label="Well").count();  
    wfpl=Annotation.objects.filter(class_label="Wet Farm Pond - Lined").count();
    wfpu=Annotation.objects.filter(class_label="Wet Farm Pond - Unlined").count();
    dfpl=Annotation.objects.filter(class_label="Dry Farm Pond - Lined").count();
    dfpu=Annotation.objects.filter(class_label="Dry Farm Pond - Unlined").count();        
    wbc = Annotation.objects.filter(class_label="Wall Based Checkdam").count();
    gbc = Annotation.objects.filter(class_label="Gate Based Checkdam").count();    
    negImgs = Image.objects.filter(is_annotated=False).count()     
    approvedImages = imgs.filter(is_approved=True).count()
    unapprovedImages = imgs.filter(is_approved=False).count()    

    context = {  
        'last_saved':savedImgName,     
        'images':imgs,
        'wells':wells,
        'wfpl':wfpl,
        'wfpu':wfpu,
        'dfpl':dfpl,
        'dfpu':dfpu, 
        'wbc':wbc,
        'gbc':gbc,
        'negImgs':negImgs,
        'totalImages':totalImages,
        'approvedImages':approvedImages,
        'unapprovedImages':unapprovedImages
    }
    return HttpResponse(template.render(context, request)) 

def show_all_markers_dataset(request):  
    template = loader.get_template('Gmapv3/showAllMarkersCheckDams.html')
    allJSON=[];
    objs = GMapMarker.objects.filter(Q(source_image__annotation__class_label="Wall Based Checkdam")|\
                                     Q(source_image__annotation__class_label="Gate Based Checkdam"))
    for obj in objs:
     allJSON.append(obj.geometryJSON)    
    allMarkers={}
    allMarkers['allJSON']=allJSON
    allMarkers=json.dumps(allMarkers)
    #print(allMarkers)
    context = {  
        'allMarkers':allMarkers,        
    }
    return HttpResponse(template.render(context, request))

def get_annotations(request):
    data = {}     
    if request.method == 'POST':
        imageName = request.POST.get('image_name') 
        try:        
            currImg = Image.objects.get(image_name=imageName)
            print(currImg)
            annots=Annotation.objects.filter(source_image=currImg)
            # annots_json=json.dumps(annots);
            listArr=[]            
            for annots_i in annots:
                list1={}
                list1['geometryJSON']=annots_i.geometryJSON;               
                list1['class_label']=annots_i.class_label;
                listArr.append(list1)
            annots_json=json.dumps(listArr);                    
            data={
                'annotations':annots_json
            }        
            return JsonResponse(data)
        except Image.DoesNotExist:    
            data={
                'annotations':-1
            }
    return JsonResponse(data)    
    

def getImageListDataset(request):
    if request.method == 'POST':
        try:
            well = request.POST.get('well')
            wbc = request.POST.get('wbc')
            gbc = request.POST.get('gbc')  
            wfpl = request.POST.get('wfpl')
            wfpu = request.POST.get('wfpu')
            dfpl = request.POST.get('dfpl')
            dfpu = request.POST.get('dfpu')
            neg = request.POST.get('neg')
            zl18 = request.POST.get('zl18')
            zl19 = request.POST.get('zl19')
            derived = request.POST.get('derived')
            print(neg)
            wfplc = 0;
            wfpuc = 0;
            dfplc = 0;
            dfpuc = 0;
            wellc = 0;
            wbcc = 0;
            gbcc = 0;
            negc = 0;  
            derivedc = 0;
            results=Image.objects.none()
            print("Zl18"+str(zl18))
 
            if(zl18=='1'):

                if(well=='1'):
                    wellr=Image.objects.filter(Q(annotation__class_label="Well"),zoom_level=18)
                    results=results|wellr
                    wellc=wellr.count()   
                if(wfpl=='1'):
                    wfplr=Image.objects.filter(Q(annotation__class_label="Wet Farm Pond - Lined"),zoom_level=18)
                    results=results|wfplr
                    wfplc=wfplr.count()                    
                if(wfpu=='1'):
                    wfpur=Image.objects.filter(Q(annotation__class_label="Wet Farm Pond - Unlined"),zoom_level=18)
                    results=results|wfpur
                    wfpuc=wfpur.count()
                if(dfpl=='1'):
                    dfplr=Image.objects.filter(Q(annotation__class_label="Dry Farm Pond - Lined"),zoom_level=18)
                    results=results|dfplr
                    dfplc=dfplr.count()
                if(dfpu=='1'):
                    dfpur=Image.objects.filter(Q(annotation__class_label="Dry Farm Pond - Unlined"),zoom_level=18)
                    results=results|dfpur
                    dfpuc=dfpur.count()
                if(wbc=='1'):
                    wbcr = Image.objects.filter(annotation__class_label="Wall Based Checkdam",zoom_level=18)
                    results=results|wbcr
                    wbcc=wbcr.count()                    
                if(gbc=='1'):
                    gbcr=Image.objects.filter(annotation__class_label="Gate Based Checkdam",zoom_level=18)
                    results=results|gbcr
                    gbcc=gbcr.count()     
                if(neg=='1'):
                    negr=Image.objects.filter(is_annotated=False,zoom_level=18)
                    results=results|negr
                    negc=negr.count()                


            if(zl19=='1'):
                if(well=='1'):
                    wellr=Image.objects.filter(Q(annotation__class_label="Well"),zoom_level=19)
                    results=results|wellr
                    wellc=wellr.count()
                if(wfpl=='1'):
                    wfplr=Image.objects.filter(Q(annotation__class_label="Wet Farm Pond - Lined"),zoom_level=19)
                    results=results|wfplr
                    wfplc=wfplr.count()
                if(wfpu=='1'):
                    wfpur=Image.objects.filter(Q(annotation__class_label="Wet Farm Pond - Unlined"),zoom_level=19)
                    results=results|wfpur
                    wfpuc=wfpur.count()
                if(dfpl=='1'):
                    dfplr=Image.objects.filter(Q(annotation__class_label="Dry Farm Pond - Lined"),zoom_level=19)
                    results=results|dfplr
                    dfplc=dfplr.count()
                if(dfpu=='1'):
                    dfpur=Image.objects.filter(Q(annotation__class_label="Dry Farm Pond - Unlined"),zoom_level=19)
                    results=results|dfpur
                    dfpuc=dfpur.count()
                if(wbc=='1'):
                    wbcr = Image.objects.filter(annotation__class_label="Wall Based Checkdam",zoom_level=19)
                    results=results|wbcr
                    wbcc=wbcr.count()                    
                if(gbc=='1'):
                    gbcr=Image.objects.filter(annotation__class_label="Gate Based Checkdam",zoom_level=19)
                    results=results|gbcr
                    gbcc=gbcr.count()
                if(neg=='1'):
                    negr=Image.objects.filter(is_annotated=False,zoom_level=19)
                    results=results|negr
                    negc=negr.count()

            if(derived=='1'):                
                derivedr = results.filter(~Q(derived_from_image=None))
                results = derivedr
                derivedc = derivedr.count()    
            else:
                results=results.filter(derived_from_image=None)

            #print(type(results))
            results=results.distinct().order_by('image_name')

            totalImages = results.count(); 
            print(totalImages)                       
            images_list = serializers.serialize('json', results,\
                                                fields=('image_name','is_annotated','is_approved','image_location'))            
            approvedImages = results.filter(is_approved=True).count()
            unapprovedImages = results.filter(is_approved=False).count()
            data={
                'status':1,
                'images':images_list,
                'well':wellc,
                'wfpl':wfplc,
                'wfpu':wfpuc,
                'dfpl':dfplc,
                'dfpu':dfpuc,
                'wbc':wbcc,
                'gbc':gbcc,
                'negImgs':negc,
                'derivedc':derivedc,                
                'totalImages':totalImages,
                'approvedImages':approvedImages,
                'unapprovedImages':unapprovedImages
            }             
        except Exception as e:
            print(str(e))
            data={
                'status':-1
            }

    return JsonResponse(data)

def editAnnotsDataset(request):
    context = {}
    try:
        template = loader.get_template('Gmapv3/editAnnotsDataset.html')      
        img_name = request.GET.get('imgName')
        img = Image.objects.get(image_name=img_name)
        zoomLvl = img.zoom_level
        cLat = img.centerLatitude
        cLng = img.centerLongitude    
        gmms = GMapMarker.objects.filter(source_image=img).values('geometryJSON')   
        gmms = json.dumps(list(gmms))        
        if(img.derived_from_image != None):
            derived_from_image = img.derived_from_image
            gmms = GMapMarker.objects.filter(source_image=derived_from_image).values('geometryJSON')   
            gmms = json.dumps(list(gmms))        
        else:    
            gmms = GMapMarker.objects.filter(source_image=img).values('geometryJSON')   
            gmms = json.dumps(list(gmms))        
        context = {  
        'imgName':img_name,
        'zoom_level':zoomLvl,
        'cLat':cLat,
        'cLng':cLng,
        'gmms':gmms
        }    
    except Exception as e: # work on python 2.x
        print(str(e))
    return HttpResponse(template.render(context, request))

def downloadImage(imgUrl,filepath): #taken from Debanjan's code
    response = requests.get(imgUrl, stream=True)    
    with open(filepath, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response

def save_edited_image_dataset(request):
    data = {}
    if request.method == 'POST':        
        topLeftLat = request.POST.get('topLeftLat')
        topLeftLng = request.POST.get('topLeftLng')
        bottomRightLat = request.POST.get('bottomRightLat')
        bottomRightLng = request.POST.get('bottomRightLng')
        centerLat = request.POST.get('centerLat') 
        centerLng = request.POST.get('centerLng')        
        oldImageName  = request.POST.get('oldImageName')
        locality = request.POST.get('locality')             
        markersJson = request.POST.get('markersJSON')
        annotationsJson = request.POST.get('annotationJSON')       
        gmapMarkerId=request.POST.get('gmapMarkerId')
        derivedFromImageId = request.POST.get('derivedFromImageId')
        zoom =int(float(request.POST.get('zoom')))        
        zoom = str(zoom)         
        ground_truthing_done = 'true'
        print("Editing Image: ", oldImageName)
        imageToBeEdited = Image.objects.get(image_name=oldImageName)
        gmmsToBeDeleted = GMapMarker.objects.filter(source_image=imageToBeEdited)
        annsToBeDeleted = Annotation.objects.filter(source_image=imageToBeEdited)
        if(gmmsToBeDeleted):        
            district = gmmsToBeDeleted[0].district        
            #Delete Old Markers (Be careful)
            gmmsToBeDeleted.delete()
            #Delete Old Annots (Be careful)
            annsToBeDeleted.delete()        
        if(gmapMarkerId!=None):            
            gmm=GMapMarker.objects.get(pk=gmapMarkerId)
            district=gmm.district

        firstpos=oldImageName.find('_')

        
        splits = oldImageName.split('_')
        o_district = splits[0]
        o_locality = splits[1]
        o_lat = splits[2]
        o_lng = splits[3]
        
        # data  = json.loads(markers_json)           
        is_annotated_flag=False
        markers  = json.loads(markersJson)
        annotations  = json.loads(annotationsJson)                  

        if(len(annotations)>0):
            is_annotated_flag=True
           
        location='static/Gmapv3/images/';       
        #Shift Old Image to 'deleted' folder
        
        
                
        #New Image Download
        key = 'AIzaSyC61MLyQ00dcfVHEG60iOlELqooDPUrRow';
        maptype = 'satellite';
        size = '640x640';
        url_center = o_lat+","+o_lng
        imgUrl = "https://maps.googleapis.com/maps/api/staticmap?center="\
                 + url_center + '&size=' + size + '&zoom=' + zoom \
                 + '&maptype=' + maptype + '&key='+key
        # newFileName=filename+"_z"+zoom+"_0.png";        
        curr_date = date.today()
        dateStr = curr_date.strftime("%Y-%m-%d")     


        filename = str(o_district)+"_"+str(o_locality)+"_"+str(o_lat)+"_"+str(o_lng)+"_z"+str(zoom)+"_"+dateStr;
        newFileName = filename+"_0.png"       
        
        filepath=location+newFileName;        
        lastpos=len(filepath)-filepath.rfind('_')
        filepathpattern=filepath[:-lastpos]
        my_file = Path(filepath)
        if my_file.exists():
             files=glob.glob(filepathpattern+"*")
             total=len(files)            
             newFileName=filename+"_"+str(total)+".png"
             filepath=location+newFileName;                    

        # print("New:", filepath)
        # delLocation = location + 'old/'
        # oldfilepath = location + oldImageName
        # delfilepath = delLocation + oldImageName;        
        # print("Old:", delfilepath)
        # copyfile(oldfilepath, delfilepath)
        # os.rename(oldfilepath,delfilepath)

        #img=Image.objects.filter(image_name=filename)
        # if img.count() > 0:            
        #     data ={
        #         'status':-1
        #     }
        #     return JsonResponse(data)
    
        #Update fields of Image in Database  
        imageToBeEdited.image_name = newFileName                
        # imageToBeEdited.centerLatitude = o_lat
        # imageToBeEdited.centerLongitude = o_lng
        imageToBeEdited.is_annotated = is_annotated_flag
        imageToBeEdited.location = location
        imageToBeEdited.save() 


        # #Download Image on server 
        if not os.path.exists(location):
            os.makedirs(location)
        downloadImage(imgUrl,filepath)  

        if(ground_truthing_done=='true'):
            ground_truthing_done=True
        else:
            ground_truthing_done=False

        if(is_annotated_flag):                     
            #Save Marker to Database
            if(gmapMarkerId==None):            
                for marker_i in markers:                      
                    json_marker_i=json.dumps(marker_i)                         
                    print(imageToBeEdited)
                    saveMarker = GMapMarker(source_image=imageToBeEdited,locality=o_locality,district=o_district,\
                                        geometryJSON=json_marker_i,ground_truthing_done=ground_truthing_done)

                    saveMarker.save()    
        
            #Save Annotations on database                
            print("Total Annots: ",len(annotations))            
            for ann_i in annotations:            
                classnm=''            
                for key, value in ann_i.items():                                    
                    if(key=='classnm'):
                        classnm = value  
                        json_ann_i=json.dumps(ann_i);                                  
                saveAnnot = Annotation(source_image=imageToBeEdited,class_label=classnm,geometryJSON=json_ann_i)
                saveAnnot.save()    

            #Make a relationship between image saved and JSmapped work. 
            #Thus to be removed from list of JSMapped work on interface
            if(derivedFromImageId==None):
                #Loop Thru District wise jsmappedworks and flag those which are covered in one image
                mapBounds = Polygon.from_bbox((topLeftLat,topLeftLng,bottomRightLat,bottomRightLng))                    
                jsmappedworks = JSMappedWorks.objects.filter(Q(district__english_name=o_district),
                                   Q(work_type__english_name='Well rehabilitation')|\
                                   Q(work_type__english_name='Vindhan Well rehabilitation')|\
                                   Q(work_type__english_name='Well Deepening')|\
                                   Q(work_type__english_name='Irrigation Well')|\
                                   Q(work_type__english_name='KT Well Desilting')|\
                                   Q(work_type__english_name='Farm Pond')|\
                                   Q(work_type__english_name='Cement Concrete Nala Bandh')|\
                                   Q(work_type__english_name='Old CNB')|\
                                   Q(work_type__english_name='Cement Nala Bund Construction Desilting and Deepening')|\
                                   Q(work_type__english_name='Cement Nala Bund Deepening')|\
                                   Q(work_type__english_name='Cement Concrete Nala Bund Repair')|\
                                   Q(work_type__english_name='KT Weir / Storage Bandhara Repair')|\
                                   Q(work_type__english_name='Kolhapur Type Bandhara')|\
                                   Q(work_type__english_name='Storage Bandhara')|\
                                   Q(work_type__english_name='Storage Bandhara Repair')); 

                                   

                #obj=jsmappedworks[0]
                #print(obj)      
                for obj in jsmappedworks:
                    latlng=(obj.latitude,obj.longitude)
                    point = Point(latlng)
                    flag=mapBounds.contains(point)             
                    if(flag):                         
                        # print("-----------------")
                        # print(obj)
                        # print(obj.is_marked)
                        obj.is_marked = True  # update record
                        # print("Changed"+str(obj.is_marked))
                        # print(obj)
                        # print("**-----------------**")
                        #obj.save()
                        #Map Image(Dataset) with JSMappedWorks
                        testjsmappedworksimg = JSMappedWorksImage.objects.filter(jsmappedwork=obj,image=imageToBeEdited)
                        count_test = testjsmappedworksimg.count()
                        if(count_test == 0):
                            jsmappedworksimg=JSMappedWorksImage(jsmappedwork=obj,image=imageToBeEdited)
                            print("Duplicate Flagged: ",latlng)
                            jsmappedworksimg.save()
                        else:
                            print("No need to map")    
                
                #flag=mapBounds.contains(ls2)
                # ls1=LineString(((19.85849090,75.51621409),(19.85849594,75.51662715),(19.85804186,75.51666470),(19.85803176,75.51624092)))    
                # ls2=LineString(((19.85731082,75.50629352),(19.85728055,75.50688360),(19.85690719,75.50686215),(19.85696773,75.50631498)))
                # bb1 = Polygon.from_bbox((19.86093151780648,75.5143893862305,19.85770246576097,75.51782261376957))
                # ans=bb1.contains(ls2)
                # print(ans)
      

        #Send success signal to the caller
        data = {
             'status': 1,
             'new_file_name':newFileName
        }        
        return JsonResponse(data)
    return JsonResponse(data)    

def getMinCoord(coordDict):
    x=sys.maxsize;
    y=sys.maxsize;
    minCoord={};
    for coord in coordDict:
        if(x>coord['x']):
            if(coord['x']<0):
                x=0;
            else:    
                x=coord['x'];
        if(y>coord['y']):
            if(coord['y']<0):
                y=0;
            else:    
                y=coord['y'];

    minCoord["x"]=x;
    minCoord["y"]=y;     
    return minCoord;

def getMaxCoord(coordDict):
    x=0;
    y=0;
    maxCoord={};
    for coord in coordDict:
        if(x<coord['x']):
            if(coord['x']>640): #change when img size is variable
                x=640;
            else:    
                x=coord['x'];
        if(y<coord['y']):
            if(coord['y']>640): #change when img size is variable
                y=640;
            else:    
                y=coord['y'];

    maxCoord["x"]=x;
    maxCoord["y"]=y;
    return maxCoord;  

def downloadDataset(request):
    imgs = Image.objects.filter(Q(annotation__class_label="Well")|\
                                Q(annotation__class_label="Wet Farm Pond - Lined")|\
                                Q(annotation__class_label="Wet Farm Pond - Unlined")|\
                                Q(annotation__class_label="Dry Farm Pond - Lined")|\
                                Q(annotation__class_label="Dry Farm Pond - Unlined")|\
                                Q(annotation__class_label="Wall Based Checkdam")|\
                                Q(annotation__class_label="Gate Based Checkdam"))
    imgs = imgs.filter(derived_from_image=None).distinct().extra(order_by = ['image_name']);    

   
                                  
    print(len(imgs))
    filename="MIS_Dataset";
    location="static/Gmapv3/zip/"
    newZipFileName=filename+"_0.zip";
    zipPath=location+newZipFileName;        
    lastpos=len(zipPath)-zipPath.rfind('_')
    filepathpattern=zipPath[:-lastpos]
    my_file = Path(zipPath)
    zipPath=os.path.join(location,newZipFileName)
    if my_file.exists():
        files=glob.glob(filepathpattern+"*")
        total=len(files)            
        newZipFileName=filename+"_"+str(total)+".zip"
    zipPath=location+newZipFileName;            

    allRows=[];
    for img in imgs:
        row={};        
        image_name=img.image_name        
        image_width=img.image_width
        image_height=img.image_height
        date_captured=img.captured_date
        img_path=img.image_location
        row["file_name"]=image_name;
        row["width"]=int(image_width);
        row["height"]=int(image_height);
        row["date_captured"]=date_captured.strftime("%m/%d/%Y");
        annots=Annotation.objects.filter(source_image=img)        
        arrJson=[];
        for annot in annots:
            currAnnJson={}
            geometryJSON = annot.geometryJSON;
            data  = json.loads(geometryJSON)
            currAnnJson['type'] = data['type']
            currAnnJson['classnm'] = data['classnm']
            if(data['type']=="circle"):
                center=data['center'];
                radius=data['radius'];
                center["x"]=round(center["x"])
                center["y"]=round(center["y"])
                currAnnJson['center']=center;
                currAnnJson['radius']=round(radius);
                bbox={};
                bbox["x"]=round(center["x"]-radius);
                bbox["y"]=round(center["y"]-radius);
                bbox["width"]=round(2*radius);
                bbox["height"]=round(2*radius); 

            if(data['type']=="polygon"):    
                pixelCoords = data['pixelCoords']
                currAnnJson['segmentation'] = pixelCoords
                minCoord=getMinCoord(pixelCoords)
                maxCoord=getMaxCoord(pixelCoords)
                width=maxCoord["x"]-minCoord["x"]
                height=maxCoord["y"]-minCoord["y"]
                bbox={};
                bbox["x"]=round(minCoord["x"]);
                bbox["y"]=round(minCoord["y"]);
                bbox["width"]=round(width);
                bbox["height"]=round(height);
                
            currAnnJson['bbox']=bbox;
            arrJson.append(currAnnJson)        
        row["annotations"]=arrJson
        allRows.append(row);              
        with zipfile.ZipFile(zipPath,'a', zipfile.ZIP_DEFLATED) as newzip:
            path=img_path #"static/Gmapv2/images/FarmPonds/"
            filename=image_name            
            oldPath=os.path.join(path,filename)
            if(not os.path.isfile(oldPath)):
                print("Not Found : "+filename)
            newPath="Images/"+filename
            newzip.write(oldPath,newPath)

    
    finalJSON=json.dumps(allRows, separators=(',', ':'))
    jsonFilename='dataset.json'
    path=os.path.join("static/Gmapv3/json/",jsonFilename);    
    with open(path, 'w') as f:
        json.dump(finalJSON, f)            
    with zipfile.ZipFile(zipPath,'a', zipfile.ZIP_DEFLATED) as newzip:        
        newzip.write(path,jsonFilename)


    context = {        
    }      
    response = HttpResponse(open(zipPath, 'rb'), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=%s' % ("MISDataset_"+dttm.today().strftime('%Y_%m_%d')+".zip")    
    return response;

def approveImage(request):
    data = {
                'status': -1
    }
    if request.method == 'POST':
        image_name = request.POST.get('image_name')
        approveFlag = request.POST.get('approve_flag')
        approveImg=Image.objects.get(image_name=image_name)
        if(approveFlag=='true'):
            approveImg.is_approved=True
        if(approveFlag=='false'):
            approveImg.is_approved=False
        approveImg.save()
        data = {
                'status': 1
        }
        return JsonResponse(data)

    return JsonResponse(data) 
import os
import json
from Gmapv2.models import *
import math
##
# import Gmapv2.CDDStoDB as cddstob
# cddstob.saveDatasetToDB()


datasetPath = "static/Gmapv2/misc/CD Dataset/Images/"
jsonPath = "static/Gmapv2/misc/CD Dataset/dataset.json"


centerPixLat = 320;
centerPixLng = 320;


def point2LatLng(x,y, map):
  var topRight = map.getProjection().fromLatLngToPoint(map.getBounds().getNorthEast());
  var bottomLeft = map.getProjection().fromLatLngToPoint(map.getBounds().getSouthWest());
  scale = math.pow(2, 19);
  var worldPoint = new google.maps.Point(x / scale + bottomLeft.x, y / scale + bottomRight.y);
  return map.getProjection().fromPointToLatLng(worldPoint);


def getPointLatLng(x,y,centerLat,centerLng):    
    lat = 0
    lng = 0

    if(x>centerPixLat):
        lat = centerLat +  0.298 * x/111111
    else:
        lat = centerLat -  0.298 * x/111111
    if(y>centerPixLng):    
        latforlng = centerLat +  0.298 * y/111111
        lng = centerLng + 0.298 / math.cos(latforlng * math.pi / 180)
    else:    
        latforlng = centerLat -  0.298 * y/111111
        lng = centerLng - 0.298 / math.cos(latforlng * math.pi / 180)
    return(lat,lng)



print(getPointLatLng(305,256,21.07217833,77.10207333))

def saveDatasetToDB():
    with open(jsonPath) as json_file:
        data = json.load(json_file)            
        jsonArr = json.loads(data)
    ic = 0
    done = False
    for filename in os.listdir(datasetPath):
        if (ic==0 and done==False):
            if filename.endswith(".png"):            
                for imgAnnot in jsonArr:                
                    if(imgAnnot['file_name'] == filename):
                        saveImgToDB(filename, imgAnnot)            
                        done = True
    ic = ic + 1                    



def saveImgToDB(imgName,jsonArr):
    x = imgName.split("_")
    district = x[0]
    locality = x[1]
    centerLat = x[2]
    centerLng = x[3]
    # zoom_level = x[4]
    zoom = 19
    
    
    
    # topLeftLat = request.POST.get('topLeftLat')
    # topLeftLng = request.POST.get('topLeftLng')
    # bottomRightLat = request.POST.get('bottomRightLat')
    # bottomRightLng = request.POST.get('bottomRightLng')
         
    # markersJson = request.POST.get('markersJSON')
    # annotationsJson = request.POST.get('annotationJSON')
    # ground_truthing_done = request.POST.get('groundTruthingDone')
    # gmapMarkerId=request.POST.get('gmapMarkerId')

    # derivedFromImageId = request.POST.get('derivedFromImageId')
    derivedFromImageId = None
    # zoom =int(float(request.POST.get('zoom')))        
    zoom = str(zoom)  
    # if(gmapMarkerId!=None):
    #     gmm=GMapMarker.objects.get(pk=gmapMarkerId)
    #     district=gmm.district

    # filename=str(district)+"_"+str(locality)+"_"+str(centerLat)+"_"+str(centerLng);        
    filename = imgName
    # data  = json.loads(markers_json)           
    is_annotated_flag=False
    # markers  = json.loads(markersJson)
    # annotations  = json.loads(annotationsJson)
    # if(len(annotations)>0):
    #     is_annotated_flag=True
    is_annotated_flag=True
    location='static/Gmapv2/images/';    

    if(is_annotated_flag):
        location = 'static/Gmapv2/images/Checkdams/';
        if(zoom=="19"):
            location = 'static/Gmapv2/images/Checkdams/zoom19/';                
    else:
        if(zoom=="19"):
            location = 'static/Gmapv2/images/Checkdams/zoom19/';
        else:	
            location = 'static/Gmapv2/images/Checkdams/';       

    # key = 'AIzaSyDQrhuv_BxZGPpB1WGF-dLTKbumKYchpvo';
    # maptype = 'satellite';
    # size = '640x640';
    # url_center = centerLat+","+centerLng
    # imgUrl = "https://maps.googleapis.com/maps/api/staticmap?center="+url_center + '&size=' + size + '&zoom=' + zoom + '&maptype=' + maptype + '&key='+key        
    # newFileName=filename+"_z"+zoom+"_0.png";
    # filepath=location+newFileName;        
    # lastpos=len(filepath)-filepath.rfind('_')
    # filepathpattern=filepath[:-lastpos]
    # my_file = Path(filepath)
    # if my_file.exists():
    #      files=glob.glob(filepathpattern+"*")
    #      total=len(files)            
    #      newFileName=filename+"_"+str(total)+".png"
    #      filepath=location+newFileName;            
    # print(filepath)        

    newFileName = filename
    if(derivedFromImageId!=None):
        img=Image.objects.get(pk=derivedFromImageId)
        #Save Image in Database
        imgHeight=640;
        imgWidth=640;        
        saveImg = Image(image_name=newFileName,\
            image_location = location,\
            image_height = imgHeight,\
            image_width = imgWidth,\
            is_annotated = is_annotated_flag,\
            centerLatitude = centerLat,\
            centerLongitude = centerLng,\
            zoom_level = zoom,\
            derived_from_image = img) 
        # saveImg.save() 

    else:   
        print("In else part") 
        # img=Image.objects.filter(image_name=filename)
        # if img.count() > 0:            
        #     data ={
        #         'status':-1
        #     }
        #     return JsonResponse(data)
    
        #Save Image in Database
        imgHeight=640;
        imgWidth=640;        
        saveImg = Image(image_name=newFileName,\
            image_location=location,\
            image_height=imgHeight,\
            image_width=imgWidth,\
            is_annotated=is_annotated_flag,\
            centerLatitude=centerLat,\
            centerLongitude=centerLng,zoom_level=zoom) 
        print("--------------------------------")        
        print(jsonArr)        
        print("--------------------------------")
        saveImg.save() 

    
    # #Download Image on server 
    # if not os.path.exists(location):
    #     os.makedirs(location)
    # downloadImage(imgUrl,filepath)


    # if(ground_truthing_done=='true'):
    #     ground_truthing_done=True
    # else:
    #     ground_truthing_done=False
    ground_truthing_done = True
    if(is_annotated_flag):            
        #Save Marker to Database
        # if(gmapMarkerId==None):            
        #     for marker_i in markers:                      
        #         json_marker_i=json.dumps(marker_i)                         
        #         saveMarker = GMapMarker(source_image=saveImg,locality=locality,district=district,\
        #                             geometryJSON=json_marker_i,ground_truthing_done=ground_truthing_done)
                # saveMarker.save()    
    
        #Save Annotations on database     
        annotations = jsonArr["annotations"]            
        print(len(annotations))        
        oi = 0;
        for ann_i in annotations:                              
            classnm = ann_i["classnm"]
            # json_ann_i=json.dumps(ann_i);            
            annotationDict = {}
            gmapmarkerDict = {}
            annotationDict ["type"] = "polygon";
            gmapmarkerDict ["type"] = "polygon";
            annotationDict ["objectNo"] = oi;
            gmapmarkerDict ["objectNo"] = oi;
            annotationDict ["pixelCoords"] = ann_i["segmentation"]
            gmapmarkerDict ["worldCoords"] = 0
            annotationDict ["classnm"] = classnm;
            gmapmarkerDict ["classnm"] = classnm;
            print(gmapmarkerDict)
            saveAnnot = Annotation(source_image=saveImg,\
                                    class_label=classnm,\
                                    geometryJSON=annotationDict)
            saveAnnot.save()    
            oi = oi + 1;
        return;
        #Make a relationship between image saved and JSmapped work. 
        #Thus to be removed from list of JSMapped work on interface
        if(derivedFromImageId==None):
            #Loop Thru District wise jsmappedworks and flag those which are covered in one image
            mapBounds = Polygon.from_bbox((topLeftLat,topLeftLng,bottomRightLat,bottomRightLng))
            print(district)           
            jsmappedworks = JSMappedWorks.objects.filter(Q(district__english_name=district),
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
                    jsmappedworksimg=JSMappedWorksImage(jsmappedwork=obj,image=saveImg)
                    print("Duplicate Flagged: ",latlng)
                    # jsmappedworksimg.save()
            
            #flag=mapBounds.contains(ls2)
            # ls1=LineString(((19.85849090,75.51621409),(19.85849594,75.51662715),(19.85804186,75.51666470),(19.85803176,75.51624092)))    
            # ls2=LineString(((19.85731082,75.50629352),(19.85728055,75.50688360),(19.85690719,75.50686215),(19.85696773,75.50631498)))
            # bb1 = Polygon.from_bbox((19.86093151780648,75.5143893862305,19.85770246576097,75.51782261376957))
            # ans=bb1.contains(ls2)
            # print(ans)
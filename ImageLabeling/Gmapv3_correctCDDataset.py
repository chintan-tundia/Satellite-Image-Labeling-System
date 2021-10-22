#Correct Checkdam Dataset Image names

#Imports
import json
from Gmapv3.models import Image
from Gmapv3.models import Annotation
from django.db.models import Q
from datetime import datetime
from datetime import date
from shutil import copyfile
from os.path import exists
import os
def readJSONintoArray(path):  
  json1_file = open(path)
  json1_str = json1_file.read()
  json1_data = json.loads(json1_str)
  json1_data = json.loads(json1_data)  
  return json1_data

def correctDates(JSONArray):
	allCDImages = Image.objects.filter(Q(annotation__class_label="Wall Based Checkdam")|\
                             Q(annotation__class_label="Gate Based Checkdam")).distinct().extra(order_by = ['image_name'])

			
	for img in allCDImages:
		oldNameDB = img.image_name		
		for obj in JSONArray:
			if(obj["file_name"]==oldNameDB):
				dateCaptured = obj["date_captured"]

				# dt = datetime.combine(date.today(), datetime.min.time())
				date_time_obj = datetime.strptime(dateCaptured, '%m/%d/%Y')
				img.captured_date = date_time_obj				
				print(img.captured_date)
				img.save()

def correctImageNames():
	# deletionImgIds = [1778, 2144, 3746] #3339
	# for id_i in deletionImgIds:
	# 	img = Image.objects.filter(id=id_i)
	# 	img.delete()
	allImages = Image.objects.filter(derived_from_image=None).distinct().extra(order_by = ['image_name'])
	print(allImages.count())	
	for img in allImages:
		date = img.captured_date.date()
		dateStr = date.strftime("%Y-%m-%d")
		oldName = img.image_name
		splits = oldName.split("_")
		district = splits[0]
		locality = splits[1]
		lat = splits[2]
		lng = splits[3]
		lastPart = splits[-1]
		imgNo = lastPart.split(".")[0]
		zoom_lvl = img.zoom_level
		path = "./static/Gmapv3/images/"
		src = path + "filtered(new,copy)/"  + oldName
		dst = path + "filtered/" + oldName
		# file_exists = exists(dst)
		# if(len(oldName)<10):
			# print(oldName)
		# count = 0	
		# for img_dup in allImages:
		# 	dup_img_name = img_dup.image_name			
		# 	if(dup_img_name == oldName):
		# 		count = count + 1
		# if(count>1):
		# 	print(img.id,":",count,":",oldName)


		
				
		# copyfile(src, dst)		
		newName = district+"_"+locality+"_"+lat+"_"+lng+"_z"+str(zoom_lvl)+"_"+dateStr+"_0.png"		
		# print(newName)
		newdst = path + "filtered/"+ newName
		# os.rename(src, newdst)
		img.image_name = newName
		# path = "static/Gmapv3/images/"
		# img.image_location=path
		# img.save()
		
		# print("New Name:",newName)
		#District_Locality_Lat_Lng_z<zoomlvl>_yyyy-mm-dd_0.png

		# print(dateStr)
	# print(allImages.count())
	#Ahmednagar__18.58425244_75.22902999000007_0.png
	#Ahmednagar__18.58425244_75.22902999000007_z18_2019-09-17.png
def checkWellAnnots():
	allImages = Image.objects.filter(derived_from_image=None,annotation__class_label="Well").distinct().extra(order_by = ['image_name'])
	polAnnotsImgs = Image.objects.filter(derived_from_image=None,annotation__class_label="Well",annotation__geometryJSON__contains='polygon')
	ids = polAnnotsImgs.values("id")
	print(ids)
	print(polAnnotsImgs.count())
	# print(allImages.count())	

def checkDerivedImages():
	allDerivedImages = Image.objects.filter(~Q(derived_from_image=None))
	for img in allDerivedImages:
		#Check if the image exists in folder
		path = "./static/Gmapv3/images/old_fromGmapv2_aggregated/"
		testImgPath = path + img.image_name
		test = os.path.isfile(testImgPath)
		dst = "./static/Gmapv3/images/derived/" + img.image_name
		if(test==True):			
			copyfile(testImgPath, dst)		
			
def renameDerivedImages():
	allDerivedImages = Image.objects.filter(~Q(derived_from_image=None))
	for img in allDerivedImages:
		date = img.captured_date.date()
		dateStr = date.strftime("%Y-%m-%d")
		oldName = img.image_name
		splits = oldName.split("_")
		district = splits[0]
		locality = splits[1]
		lat = splits[2]
		lng = splits[3]
		lastPart = splits[-1]
		imgNo = lastPart.split(".")[0]
		zoom_lvl = img.zoom_level
		path = "./static/Gmapv3/images/"
		newName = district+"_"+locality+"_"+lat+"_"+lng+"_z"+str(zoom_lvl)+"_"+dateStr+"_0.png"		
		olddst = path + "derived/" + oldName
		newdst = path + newName
		copyfile(olddst, newdst)
		img.image_name = newName
		img.save()
		print(newName)

def main():
 path="./static/Gmapv3/misc/Dataset-Checkdams/dataset.json"
 JSONArray = readJSONintoArray(path)
 # correctDates(JSONArray)
 # correctImageNames()
 # checkWellAnnots()
 # checkDerivedImages()
 renameDerivedImages()

 


main()
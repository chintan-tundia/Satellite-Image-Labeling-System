var map;
var currentImg = 1037;
var jsonArr;
var jsonGmapMarker;
var jsonAnnotations;
function initialize(){        
  jsonArr = JSON.parse(received_data.replace(/&quot;/g,'"'));
  displayCurrentImg()
}

function next(){
  currentImg = currentImg + 1  
  displayCurrentImg()
  $("#status").text("")
  // if(currentImg < 1037){
  //   saveToDB()  
  // }
  
}
function previous(){
  currentImg = currentImg - 1  
  displayCurrentImg()
  $("#status").text("")
}
function displayCurrentImg(){  
  jsonArrCurr = jsonArr[currentImg]
  imgName = jsonArrCurr["file_name"] //Ahmednagar__18.61819113_75.46033556_z19_0.png
  imgNameSplits = imgName.split("_")  
  centerLat = imgNameSplits[2]
  centerLng = imgNameSplits[3]
  var myLatlng = new google.maps.LatLng(centerLat, centerLng);
  var mapOptions = {
    zoom: 19,
    center: myLatlng,
    mapTypeId: 'satellite'
  };
  map = new google.maps.Map(document.getElementById('map'),mapOptions);
  
  $("#currImg").text(currentImg)
  $("#imgName").text(imgName)
  //Read annotations and convert to latlng
  google.maps.event.addListenerOnce(map,"projection_changed", function() {
    annotations = jsonArrCurr["annotations"]
    var i = 0
    var arrAnnotations=[];
    var arrGmapMarker=[];
    for(let annotation of annotations){
      segmentation  = annotation["segmentation"]        
      classNm = annotation["classnm"]
      var convLatLngArr=[]             
      var arrPixelCoords=[];
      var arrWorldCoords=[];   
      for(let point of segmentation){
        var pixelCoords={};
        var worldCoords={};  
        latLngObj = point2LatLng(point,map)        
        convLatLngArr.push(latLngObj)        
        pixelCoords["x"] = point.x;      
        pixelCoords["y"] = point.y;
        worldCoords["lat"] = latLngObj.lat().toFixed(8); 
        worldCoords["lng"] = latLngObj.lng().toFixed(8);
        arrPixelCoords.push(pixelCoords);
        arrWorldCoords.push(worldCoords);
      }
      
      const polygon1 = new google.maps.Polygon({
          paths: convLatLngArr,
          strokeColor: "#00FFFF",
          strokeOpacity: 0.8,
          strokeWeight: 2,      
          fillOpacity: 0.35,
      });
      polygon1.setMap(map); 
      var annotation_i = {};
      var gmapmarker_i = {};
      annotation_i ["type"] = "polygon";
      gmapmarker_i ["type"] = "polygon";
      annotation_i ["objectNo"] = i;
      gmapmarker_i ["objectNo"] = i;
      annotation_i ["pixelCoords"] = arrPixelCoords;
      gmapmarker_i ["worldCoords"] = arrWorldCoords;   
      annotation_i ["classnm"] = classNm;
      gmapmarker_i ["classnm"] = classNm;
      arrAnnotations.push(annotation_i);
      arrGmapMarker.push(gmapmarker_i);

      jsonGmapMarker=JSON.stringify(arrGmapMarker);
      jsonAnnotations=JSON.stringify(arrAnnotations);
      i = i + 1;
    }       
  });
  


}
function saveToDB(){  
  jsonArrCurr = jsonArr[currentImg]
  imgName = jsonArrCurr["file_name"] //Ahmednagar__18.61819113_75.46033556_z19_0.png
  imgNameSplits = imgName.split("_")
  district = imgNameSplits[0]
  locality = imgNameSplits[1]
  centerLat = imgNameSplits[2]
  centerLng = imgNameSplits[3]
  zoomLevel = 19
  groundTruthingDone = "true"
  var mapBounds = map.getBounds()
  var ne=mapBounds.getNorthEast();
  var sw=mapBounds.getSouthWest();
  var topLeftLat = sw.lat().toFixed(8);
  var topLeftLng = ne.lng().toFixed(8);
  var bottomRightLat = ne.lat().toFixed(8);
  var bottomRightLng = sw.lng().toFixed(8);  
  

  $.ajax({
      type:"POST",
      url: 'ajax/save_image_checkdams',
      data: {
          'topLeftLat':topLeftLat,
          'topLeftLng':topLeftLng,
          'bottomRightLat':bottomRightLat,
          'bottomRightLng':bottomRightLng,
          'centerLat':centerLat,
          'centerLng':centerLng,
          'zoom':zoomLevel,
          'district':district, 
          'locality': locality,                
          'markersJSON': jsonGmapMarker,
          'annotationJSON':jsonAnnotations,
          'groundTruthingDone':groundTruthingDone
      },
      dataType: 'json',
      success: function (data) {
        $("#status").text("Yes")        
      },
      error: function(xhr, textStatus, errorThrown) {
          alert("Something went wrong.");
      }
  })


}
//URL: https://stackoverflow.com/questions/25219346/how-to-convert-from-x-y-screen-coordinates-to-latlng-google-maps
function point2LatLng(point, map) {
  var topRight = map.getProjection().fromLatLngToPoint(map.getBounds().getNorthEast());
  var bottomLeft = map.getProjection().fromLatLngToPoint(map.getBounds().getSouthWest());
  var scale = Math.pow(2, map.getZoom());
  var worldPoint = new google.maps.Point(point.x / scale + bottomLeft.x, point.y / scale + topRight.y);
  return map.getProjection().fromPointToLatLng(worldPoint);
}

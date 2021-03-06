//Global variable Initializations
	var markers = [];
  var allOldMarkers = [];
	var latlng;
  var selectedShape;  
  var allObjects={};
  var totalObjects=0;
  var allIds=[];
  allLocs=[];
  var workTypeIds=[];
  var drawingManager;
  var zoomLevel=19;  
  var vlat = 19.859317;
  var vlong = 75.516106;//Somewhere in Kubephal,Aurangabad
  var selIdx=0
  var boundaryLoaded = 0
  //initialize(vlat,vlong); 


/*-------Functions--------*/  
	function initialize(vlat,vlong){        
       var vlat = cLat;
		   var vlong = cLng;        
       labelledMarkers = JSON.parse(gmms)
       totalObjects=0 
        //$('#inform').hide()     
        
        //var latlng = new google.maps.LatLng(19.910915, 73.876757);
        latlng = new google.maps.LatLng(vlat,vlong);		
        var myOptions = {
            zoom: zoomLvlofImg,
            center: latlng,
            disableDefaultUI: true,
            mapTypeId: google.maps.MapTypeId.SATELLITE,
            scaleControl: true            
        };
        map = new google.maps.Map(document.getElementById("googleMap"), myOptions); 
        drawingManager = new google.maps.drawing.DrawingManager({
          drawingMode: google.maps.drawing.OverlayType.MARKER,
          drawingControl: true,
          drawingControlOptions: {
            position: google.maps.ControlPosition.TOP_CENTER,
            //drawingModes: ['marker', 'circle', 'polygon', 'polyline', 'rectangle']
            drawingModes: ['circle','polygon','rectangle']
          },          
          circleOptions: {
            fillColor: 'transparent',
            fillOpacity: 0.4,
            strokeColor:'black',
            strokeWeight: 2,
            clickable: true,
            editable: true,
            zIndex: 1
          },
          polygonOptions: {
            fillOpacity:0,
            //fillColor: '#e6dc03',
            fillColor: 'transparent',
            strokeWeight: 1,
            clickable: true,
            draggable:true,
            editable: true,
            zIndex: 1

          },
          rectangleOptions: {
            fillOpacity:0.4,
            fillColor: '#e6dc03',
            strokeWeight: 1,
            clickable: true,
            draggable:true,
            editable: true,
            zIndex: 1

          }

        });
        //drawingManager.setMap(map);
        // Newly defined                  
        $('#btnCircle').click(function(){                 
          drawingManager.setOptions({
              drawingMode : google.maps.drawing.OverlayType.CIRCLE,
              drawingControl : true,
              drawingControlOptions : {
                  position : google.maps.ControlPosition.TOP_CENTER,
                  drawingModes : [google.maps.drawing.OverlayType.CIRCLE]
              }
          })
          drawingManager.setMap(map);
        })
        $('#btnRectangle').click(function(){          
          drawingManager.setOptions({
              drawingMode : google.maps.drawing.OverlayType.RECTANGLE,
              drawingControl : true,
              drawingControlOptions : {
                  position : google.maps.ControlPosition.TOP_CENTER,
                  drawingModes : [google.maps.drawing.OverlayType.RECTANGLE]
              }
          })
          drawingManager.setMap(map);
        })
        $('#btnPolygon').click(function(){          
          drawingManager.setOptions({
              drawingMode : google.maps.drawing.OverlayType.POLYGON,
              drawingControl : true,
              drawingControlOptions : {
                  position : google.maps.ControlPosition.TOP_CENTER,
                  drawingModes : [google.maps.drawing.OverlayType.POLYGON]
              }
          })
          drawingManager.setMap(map);
          $('#btnPolygon').addClass("disabled");
        })
        
        //Calculate bounds and draw rectangle around boundary
        google.maps.event.addListener(map, 'bounds_changed', function() {
          if(boundaryLoaded == 0){
            bounds=map.getBounds()            
            ne=bounds.getNorthEast()
            sw=bounds.getSouthWest()
            var north= ne.lat();
            var east=ne.lng();
            var south=sw.lat();
            var west=sw.lng();
            pths = []        
            pths.push({lat:north, lng:west})
            pths.push({lat:north, lng:east})
            pths.push({lat:south, lng:east})
            pths.push({lat:south, lng:west})
            pths.push({lat:north, lng:west})
                        
            var pgn = new google.maps.Polygon({
                    paths: pths,              
                    fillOpacity:0,
                    strokeColor:'white',
                    //fillColor: '#e6dc03',
                    fillColor: 'transparent',
                    strokeWeight: 2,
                    clickable: true,                    
                    editable: false,
                    zIndex: 1,                
                  });
            pgn.setMap(map);
            boundaryLoaded = 1
          }          
        });
         

        
        google.maps.event.addListener(drawingManager, 'overlaycomplete', function(e) {          
            if (e.type != google.maps.drawing.OverlayType.MARKER) {
                // Switch back to non-drawing mode after drawing a shape.
                drawingManager.setDrawingMode(null);
                // To hide:
                //drawingManager.setOptions({
                // drawingControl: false
                //});

                // Add an event listener that selects the newly-drawn shape when the user
                // mouses down on it.          
                var newShape = e.overlay;   
                newShape.type = e.type; 
                //var totalObjects=Object.keys(allObjects).length
                var objNo = totalObjects++;                
                var idName = "obj"+objNo;
                var idSelect = "sel"+objNo;

                if(newShape.type=="circle"){
                  google.maps.event.addListener(newShape, 'click', function() {                  
                    setSelection(newShape,idName);
                  });
                  setSelection(newShape,idName);
                  allObjects[idName] = newShape;
                  //allObjects.push(newShape)
                  allIds.push(idName)
                  
                  //Adding label
                  var ptsStr = getPoints(newShape)
                  var dropdownStr = "<form><div class='form-group'>"+ 
                                    //"<p>"+ptsStr+"</p><br>"+                 
                                    "<select id='"+idSelect+"' class='form-control'>"+
                                      "<option>Well</option>"+                                    
                                    "</select>"+         
                                  "</div></form>";
                  var htmlCont = "<div id='"+idName+"' class='panel panel-info'>"+
                                  "<div class='panel-heading'>"+
                                     "<b> Annotation "+(objNo+1)+"</b>"+
                                   "</div>"+
                                   "<div class='panel-body'>"+dropdownStr+                                    
                                      "<a id='btnDelete' type='button' class='btn btn-danger'>"+
                                      "<span class='glyphicon glyphicon-minus-sign'></span>"+
                                      " Remove Annotation"+
                                      "</a>"+
                                   "</div>"+
                                "</div>";
                  $("#annotations").append(htmlCont);
                  $('#btnPolygon').removeClass("disabled");
                }
                else if(newShape.type=="polygon"){
                  var paths=newShape.getPath()
                  google.maps.event.addListener(newShape, 'click', function() {                                    
                      for (var key in allObjects){                
                        var obj = allObjects[key] 
                        if(this.getPath()==obj.getPath()){
                          console.log("Found At",key)
                          setSelection(this,key);
                        }                      
                      }
                      setSelection(newShape,idName);
                  });
                  setSelection(newShape,idName);
                  allObjects[idName] = newShape;
                  //allObjects.push(newShape)
                  allIds.push(idName)
                  
                  //Adding label
                  var ptsStr = getPoints(newShape)
                  var dropdownStr = "<form><div class='form-group'>"+ 
                                    //"<p>"+ptsStr+"</p><br>"+                 
                                    "<select id='"+idSelect+"' class='form-control'>"+
                                      "<option>Well</option>"+
                                      "<option>Wet Farm Pond - Lined</option>"+
                                      "<option>Wet Farm Pond - Unlined</option>"+
                                      "<option>Dry Farm Pond - Lined</option>"+
                                      "<option>Dry Farm Pond - Unlined</option>"+ 
                                      "<option>Wall Based Checkdam</option>"+
                                      "<option>Gate Based Checkdam</option>"+                    
                                    "</select>"+         
                                  "</div></form>";
                  var htmlCont = "<div id='"+idName+"' class='panel panel-info'>"+
                                  "<div class='panel-heading'>"+
                                     "<b> Annotation "+(objNo+1)+"</b>"+
                                   "</div>"+
                                   "<div class='panel-body'>"+dropdownStr+                                    
                                      "<a id='btnDelete' type='button' class='btn btn-danger'>"+
                                      "<span class='glyphicon glyphicon-minus-sign'></span>"+
                                      " Remove Annotation"+
                                      "</a>"+
                                   "</div>"+
                                "</div>";
                  $("#annotations").append(htmlCont);
                  $('#btnPolygon').removeClass("disabled");
                } 
                  
            }
        });
        google.maps.event.addListener(drawingManager, 'drawingmode_changed', clearSelection)
        google.maps.event.addListener(map, 'click', clearSelection);
        totalAnnots = labelledMarkers.length
        for(ai=0;ai<totalAnnots;ai++){
            var objNo=totalObjects++;                            
            var idName="obj"+objNo            
            var idSelect="sel"+objNo
            ai_json = JSON.parse(labelledMarkers[ai]["geometryJSON"])
            ai_type = ai_json["type"]                    
            ai_class_nm = ai_json["classnm"]
            if(ai_type == "circle"){              
              var ccenter = new google.maps.LatLng(ai_json["center"]["lat"],ai_json["center"]["lng"]);
              var radius=ai_json["radius"]; 
              var circle = new google.maps.Circle({
                fillOpacity:0,
                //fillColor: '#e6dc03',
                fillColor: 'transparent',
                strokeWeight: 1,
                clickable: true,
                draggable:true,
                editable: true,
                zIndex: 1,
                editable: true,
                center: ccenter,
                radius:radius
              })
              circle.setMap(map)
              setSelection(circle,idName);
              allObjects[idName] = circle
              allIds.push(idName)

            }
            if(ai_type == "polygon"){              
              wcrds = ai_json["worldCoords"]                    
              pths = []
              for (var crd in wcrds) {
                crdlat = wcrds[crd]["lat"]
                crdlng = wcrds[crd]["lng"]
                pths.push({lat:parseFloat(crdlat), lng:parseFloat(crdlng)})
              }  
              var pgn = new google.maps.Polygon({
                paths: pths,              
                fillOpacity:0,
                //fillColor: '#e6dc03',
                fillColor: 'transparent',
                strokeWeight: 1,
                clickable: true,
                draggable:true,
                editable: true,
                zIndex: 1,
                editable: true,
              });
              pgn.setMap(map); 
              pgn.addListener("click", function (){              
              var i=0              
              for (var key in allObjects){                
                var obj = allObjects[key] 
                if(this.getPath()==obj.getPath()){
                  console.log("Found At",key)
                  setSelection(this,key);
                }                
              }
              
              });          
              setSelection(pgn,idName);              
              allObjects[idName]=pgn
              //allObjects.push(newShape)
              allIds.push(idName) 
              var ptsStr=getPoints(pgn)
            }
            

            //---------Add drop down----------                        
            // google.maps.event.addListener(pgn, 'click', function() {  
            //   console.log(pgn.getPath())                                         
            //   setSelection(pgn,idName);
            // });  
            
            
            //Adding label
            
            var dropdownStr="<form><div class='form-group'>"+ 
                              //"<p>"+ptsStr+"</p><br>"+                 
                              "<select id='"+idSelect+"' class='form-control'>"+
                                "<option>Select Class</option>";
            
            
            if(ai_class_nm == "Well"){
                dropdownStr+="<option selected='selected'>Well</option>";
            }
            else{
                dropdownStr+="<option>Well</option>";
            }
            if(ai_class_nm == "Wet Farm Pond - Lined"){
                dropdownStr+="<option selected='selected'>Wet Farm Pond - Lined</option>";
            }
            else{
                dropdownStr+="<option>Wet Farm Pond - Lined</option>";
            }
            if(ai_class_nm == "Wet Farm Pond - Unlined"){
                dropdownStr+="<option selected='selected'>Wet Farm Pond - Unlined</option>";
            }
            else{
                dropdownStr+="<option>Wet Farm Pond - Unlined</option>";
            }
            if(ai_class_nm == "Dry Farm Pond - Lined"){
                dropdownStr+="<option selected='selected'>Dry Farm Pond - Lined</option>";
            }
            else{
                dropdownStr+="<option>Dry Farm Pond - Lined</option>";
            }
            if(ai_class_nm == "Dry Farm Pond - Unlined"){
                dropdownStr+="<option selected='selected'>Dry Farm Pond - Unlined</option>";
            }
            else{
                dropdownStr+="<option>Dry Farm Pond - Unlined</option>";
            }

            if(ai_class_nm == "Wall Based Checkdam"){
                dropdownStr+="<option selected='selected'>Wall Based Checkdam</option>";
            }
            else{
                dropdownStr+="<option>Wall Based Checkdam</option>";
            }
            if(ai_class_nm == "Gate Based Checkdam"){
                dropdownStr+="<option selected='selected'>Gate Based Checkdam</option>";
            }
            else{
                dropdownStr+="<option>Gate Based Checkdam</option>";
            }
            
                                                  
                dropdownStr+="</select>"+         
                            "</div></form>";
            var htmlCont="<div id='"+idName+"' class='panel panel-info'>"+
                            "<div class='panel-heading'>"+
                               "<b> Annotation "+(objNo+1)+"</b>"+
                             "</div>"+
                             "<div class='panel-body'>"+dropdownStr+                                    
                                "<a id='btnDelete' type='button' class='btn btn-danger'>"+
                                "<span class='glyphicon glyphicon-minus-sign'></span>"+
                                " Remove Annotation"+
                                "</a>"+
                             "</div>"+
                          "</div>";
            $("#annotations").append(htmlCont);
            $('#btnPolygon').removeClass("disabled");              

        }
        zoomLevel = map.getZoom();
        $('#zoomLvlTxt').text(zoomLevel);

        
  }  
  function clearSelection() {
      if (selectedShape) {
        if (selectedShape.type !== 'marker') {
            selectedShape.setEditable(false);
        }
        selectedShape = null;
        //var totalObjects=allObjects.length
        for (var key in allObjects) {
          //$('#obj'+key).attr('class', 'panel panel-default');  
          $('#'+key).attr('class', 'panel panel-default');  
        }
        // for(i=0;i<totalObjects;i++)
        // {          
        //   $('#obj'+i).attr('class', 'panel panel-default');
        // }
      }
  }

  function setFocusOnShape(index){    
    //var totalObjects=allObjects.length     
    //console.log("Selected:"+index)
    for (var key in allObjects) {        
        if(key==index){
        
          $('#'+key).attr('class', 'panel panel-info');
        }
        else{          
          $('#'+key).attr('class', 'panel panel-default');
        }
    }        
  }
  function setSelection(shape,index) {
      clearSelection();      
      shape.setEditable(true);
      selectedShape = shape;       
      setFocusOnShape(index)                   
      //selectColor(shape.get('fillColor') || shape.get('strokeColor'));
  }
  function getPoints(selectedShp){
    if (selectedShp) {
          if(selectedShp.type == google.maps.drawing.OverlayType.RECTANGLE)
          {
            bounds=selectedShp.getBounds()
            ne=bounds.getNorthEast()
            sw=bounds.getSouthWest()
            var north= ne.lat().toFixed(8);
            var east=ne.lng().toFixed(8);
            var south=sw.lat().toFixed(8);
            var west=sw.lng().toFixed(8);
            //neLat=radians(ne.lat())
            //neLng=radians(ne.lng())
            //$('#dispText').html("North East :"+ne+"<br> South West:"+sw)
            var str="Points:("+north+","+west+")"+",("+north+","+east+"),("+south+","+east+"),("+south+","+west+")"
            return str;
          }
          if(selectedShp.type == google.maps.drawing.OverlayType.POLYGON)
          {
            var path=selectedShp.getPath()
            var len=path.getLength()
            var dispText=""
            // for(var i=0;i<len;i++)
            // {
            //   pair=path.getAt(i)
            //   dispText+="("+i+"): ("+pair.lat().toFixed(8)+", "+pair.lng().toFixed(8)+")<br>"
            // }
            //var area=google.maps.geometry.spherical.computeArea(path).toFixed(2)
            //dispText+="Area: "+area+" sq.m"
            return dispText;
            //$('#dispText').html(dispText)

          }
          if(selectedShp.type == google.maps.drawing.OverlayType.CIRCLE)
          {
            var center=selectedShp.getCenter()
            var radius=selectedShp.getRadius()
            var area=(radius*radius*Math.PI).toFixed(2)
            var str="Center: ("+center.lat().toFixed(8)+", "+center.lng().toFixed(8)+")<br>Radius: "+radius.toFixed(2)+"m<br>Area: "+area+" sq.m"
            //$('#dispText').html("Center : "+center+"<br>Radius : "+radius)
            return str;
          }    
        }  
  }

  //For setting map based on lat long
  function latlngchng(){
  		var latlngtext=$('#inp_latlng').val()
  		var str_array = latlngtext.split(',');
  		var vlat=str_array[0] 
  		var vlong=str_array[1]  
  		latlng = new google.maps.LatLng(vlat,vlong);
  		map.setCenter(latlng);
  		//initialize(vlat, vlong);
  }
  function searchPlace(){
  	var place=$('#inp_place').val()  	
  	var request = {
          query: place,
          fields: ['name', 'geometry'],
        };

    service = new google.maps.places.PlacesService(map);

    service.findPlaceFromQuery(request, function(results, status) {    	
       if (status === google.maps.places.PlacesServiceStatus.OK) {
            // for (var i = 0; i < results.length; i++) {
            //   createMarker(results[i]);
            // }            
            map.setCenter(results[0].geometry.location);
       }
    });
  } 
  function mercY(lat) { return Math.log(Math.tan(lat/2 + Math.PI/4)); }
  function radians(degrees){ return degrees * Math.PI / 180; }
  function degrees(radians){ return radians * 180 / Math.PI; }

  function getPixelCoords(slat,slng){
    lat=radians(slat)
    lon=radians(slng)
    
    var south = radians(map.getBounds().getSouthWest().lat());
    var north = radians(map.getBounds().getNorthEast().lat());
    var west = radians(map.getBounds().getSouthWest().lng());
    var east = radians(map.getBounds().getNorthEast().lng());

    // This also controls the aspect ratio of the projection
    width = 640;
    height = 640;

    // Formula for mercator projection y coordinate:
    

    // Some constants to relate chosen area to screen coordinates
    ymin = mercY(south);
    ymax = mercY(north);
    xFactor = width/(east - west);
    yFactor = height/(ymax - ymin);

    // function mapProject($lat, $lon) { // both in radians, use deg2rad if neccessary        
    x = lon;
    y = mercY(lat);
    x = (x - west)*xFactor;
    y = (ymax - y)*yFactor; // y points south
    if(x < 0){
      x = 0
    }
    if(x > 640){
      x = 640
    }
    if(y < 0){
      y = 0
    }
    if(y > 640){
      y = 640
    }
    return new Array(x, y);
    // }
  }
  function freezeMap(){
          zoomLevel=map.getZoom();
          map.setOptions({gestureHandling:"none"})
          map.setOptions({mapTypeId: google.maps.MapTypeId.SATELLITE})
          var southpt = map.getBounds().getSouthWest().lat()
          var northpt = map.getBounds().getNorthEast().lat()
          var westpt = map.getBounds().getSouthWest().lng()
          var eastpt = map.getBounds().getNorthEast().lng()            
          
          // console.log("North:"+northpt);
          // console.log("West:"+westpt);
          // console.log("South:"+southpt);
          // console.log("East:"+eastpt);
          
          var restrictionJson = {
            restriction: { 
            latLngBounds: {north:northpt , south:southpt , west:westpt , east:eastpt },
            strictBounds: true,
            }
          }
          map.setOptions(restrictionJson)
          //$('#inform').show()
  }
  
  function unFreezeMap(){
    map.setOptions({gestureHandling:"auto"})
    var restrictionJson = {
      restriction: {
        latLngBounds:{north:89.97835325843884 , south:-89.90858218066927 , west:-180 , east:180},
        strictBounds: false,
      }
    }
    map.setOptions(restrictionJson)
  }

  function resetMapCanvas(){
    //unFreezeMap();
    //var totalIds=allIds.length
    //var totalObjects=allObjects.length
    $('#annotations').empty()
    for (var key in allObjects) {
      selShp=allObjects[key];
      selShp.setMap(null);
    }
    /*for(i=0;i<totalObjects;i++){
      selShp=allObjects[i];
      selShp.setMap(null);
    }*/
    allObjects={};
    allIds=[];
    totalObjects=0;    
    drawingManager.setOptions({drawingControl: false});
    $('#btnPolygon').removeClass("disabled");
    drawingManager.setMap(null);
    $('#btnPolygon').hide()
    $('#btnCircle').hide()
    $('#btnReset').hide()
    $('#btnAnnotate').show()
    $('#SelDistrict').prop("disabled", false);
    $('#SelDistrictLoc').prop("disabled", false);
  }
  // Sets the map on all markers in the array.
  /*function setMapOnAll(map) {
    for (var i = 0; i < markers.length; i++) {
      markers[i].setMap(map);
    }
  }*/    
  // Save markers to database
  /*function saveMarkers(){
    var lat = latlng.lat();
    var lng = latlng.lng(); 
    var locations=[];
    for (var i = 0; i < markers.length; i++) {
        locations.push(markers[i].position);        
      } 
      markers_json=JSON.stringify(locations); 
      alert(markers_json)  
      $.ajax({
        type:"POST",
            url: 'ajax/save_markers',
            data: {                
                'markers': markers_json               
            },
            dataType: 'json',
            success: function (data) {                
                if (data.status==1) {
                  alert("Markers saved");                   
                }
          }         
      });
  }*/

/*-------Functions End--------*/


/*-------Event Listeners--------*/
$(document).ready(function(){ 
  map.addListener('zoom_changed', function() {
      zoomLevel = map.getZoom();
      $('#zoomLvlTxt').text(zoomLevel);
  });  
  $(document).on('click','.panel',function(){
    var idxStr=this.id;  
    console.log(idxStr)
    //var idx=idxStr[idxStr.length-1];
    if(idxStr in allObjects){
      //setSelection(allObjects[idx],idx)
      setSelection(allObjects[idxStr],idxStr)
    }
  });
  $(document).on('change','.form-control',function(){ 
    if(this.value=="Checkdam"){
      selectedShape.setOptions({fillOpacity:0.3})
      // var divId=this.parentNode.parentNode.parentNode.parentNode.id
      // $('#'+divId).collapse()        
      //selectedShape.setOptions({fillColor:'#13dde8'})      
      selectedShape.setOptions({fillColor:'cyan'})      
    }
  });  
  $(document).on('click','#btnDelete',function(){
    var panelElemId=this.parentNode.parentNode.id;    
    var idx=panelElemId.substring(3, panelElemId.length);          
    $('#'+panelElemId).remove()
    console.log("Deleting :"+panelElemId)
    selShp=allObjects[panelElemId]
    if (selShp) {          
      selShp.setMap(null);        
      drawingManager.setOptions({drawingControl: true});
    } 
    if(idx>-1){
      //allObjects.splice(idx,1)
      delete allObjects[panelElemId]
      allIds.splice(idx,1)            
    }
  });      
  $('#btnReset').click(function(){        
    location.reload();
    //resetMapCanvas()    ;
  })
  $("#btnSave").click(function(e){ 

    var latlng1 = new google.maps.LatLng(cLat,cLng);
    map.setCenter(latlng1);    
    map.setZoom(zoomLvlofImg) 
    //var totalObj=allObjects.length
    var totalObj=Object.keys(allObjects).length    
    var zoomLevel = map.getZoom();
    var okFlag = true;
    var zoomFlag = true; 
    selIdx = $('#SelDistrictLoc').prop('selectedIndex')   
    if(zoomLevel<18){
      alert("Keep the zoom level as original and save.");      
      zoomFlag=false;
      return;
    }
    if(totalObj<=0){
      var txt;
      var r = confirm("There are no annotations. Are you sure you want to save anyways?");
      if (r == false) {
        okFlag = false;
        return;
      }
    }

    if(zoomFlag==true && okFlag==true){
          //Get Freezed Map Bounds   
          var centerLat = map.getCenter().lat().toFixed(8);
          var centerLng = map.getCenter().lng().toFixed(8);
          var mapBounds = map.getBounds()
          var ne=mapBounds.getNorthEast();
          var sw=mapBounds.getSouthWest();
          var topLeftLat = sw.lat().toFixed(8);
          var topLeftLng = ne.lng().toFixed(8);
          var bottomRightLat = ne.lat().toFixed(8);
          var bottomRightLng = sw.lng().toFixed(8);
          // var zoomLevel = map.getZoom().toFixed(8);		
          var zoomLevel = zoomLvlofImg  
          var groundTruthingDone = true;
          var selectedClass;
          var jsonGmapMarker='';
          var jsonAnnotations='';
          //Get all annotations.
         
          var flag=1;
          var finalJson='';
          var finalArray=[];
          var arrAnnotations=[];
          var arrGmapMarker=[];
          //for(i=0;i<totalObj;i++)
          var i=0;
          for (var key in allObjects)  
          {       
            //var idxStr=allIds[i];
            var idxStr=key;
            var idx=idxStr.substring(3, idxStr.length);;                    
            selectedClass=$('#sel'+idx).val();
            if(selectedClass=='Select Class'){
              flag=0;
              alert("Please select class for each annotation.");
              break;
            }
            else{          
              //var currentShape = allObjects[i];
              var currentShape = allObjects[key];              
              
                
              flag = 1
              //For circle
              if(typeof currentShape.getRadius === "function"){          // if(currentShape.type == google.maps.drawing.OverlayType.CIRCLE)              
                // console.log("circle")
                var center=currentShape.getCenter()
                var radius=currentShape.getRadius()
                var bboxsw=currentShape.getBounds().getSouthWest();
                var bboxne=currentShape.getBounds().getNorthEast();              
                var bboxn=bboxne.lat().toFixed(8);
                var bboxs=bboxsw.lat().toFixed(8);              
                var bboxe=bboxne.lng().toFixed(8);
                var bboxw=bboxsw.lng().toFixed(8);
                var latlngNEPix=getPixelCoords(bboxn,bboxe);
                var latlngNWPix=getPixelCoords(bboxn,bboxw);              
                var circlePixX=(latlngNEPix[0]+latlngNWPix[0])/2;
                var circlePixY=latlngNEPix[1];
                var latCenter=center.lat().toFixed(8);
                var lngCenter=center.lng().toFixed(8);                          
                var latlngCenterPix=getPixelCoords(latCenter,lngCenter);
                var radiusPix=latlngCenterPix[1]-circlePixY
                var annotation = {};
                var gmapmarker = {};
                var centerPixelCoords={};
                var centerWorldCoords={};
                centerPixelCoords["x"] = latlngCenterPix[0];      
                centerPixelCoords["y"] = latlngCenterPix[1];
                centerWorldCoords["lat"] = latCenter; 
                centerWorldCoords["lng"] = lngCenter;              

                annotation ["type"] = "circle";
                gmapmarker ["type"] = "circle";
                annotation ["objectNo"] = i;
                gmapmarker ["objectNo"] = i;
                annotation ["radius"] = radiusPix;
                gmapmarker ["radius"] = radius;  
                annotation ["center"] = centerPixelCoords;
                gmapmarker ["center"] = centerWorldCoords;  
                annotation ["classnm"] = selectedClass;
                gmapmarker ["classnm"] = selectedClass;              
                arrAnnotations.push(annotation);
                arrGmapMarker.push(gmapmarker);              
              }
              if(typeof currentShape.getPath === "function"){  //if(currentShape.type == google.maps.drawing.OverlayType.POLYGON)              
                var arrPixelCoords=[];
                var arrWorldCoords=[];
                path=currentShape.getPath();
                var len = path.getLength();
                var lat,lng,latlngPix,lt,ln;
                
                for(var j=0;j<len;j++)
                {
                  var pixelCoords={};
                  var worldCoords={};            
                  pair=path.getAt(j);
                  lat=pair.lat().toFixed(8);
                  lng=pair.lng().toFixed(8);
                  latlngPix=getPixelCoords(lat,lng);
                  lt=Math.round(latlngPix[0]);
                  ln=Math.round(latlngPix[1]);
                  pixelCoords["x"] = lt;      
                  pixelCoords["y"] = ln;
                  worldCoords["lat"] = lat; 
                  worldCoords["lng"] = lng;
                  arrPixelCoords.push(pixelCoords);
                  arrWorldCoords.push(worldCoords);
                }

                var annotation = {};
                var gmapmarker = {};
                annotation ["type"] = "polygon";
                gmapmarker ["type"] = "polygon";
                annotation ["objectNo"] = i;
                gmapmarker ["objectNo"] = i;
                annotation ["pixelCoords"] = arrPixelCoords;
                gmapmarker ["worldCoords"] = arrWorldCoords;   
                annotation ["classnm"] = selectedClass;
                gmapmarker ["classnm"] = selectedClass;
                arrAnnotations.push(annotation);
                arrGmapMarker.push(gmapmarker);
              }                              
              i++;             
            }
          }



              
          
          if(flag){            
            finalItem = {}
            var mapCenterArr={};
            mapCenterArr["lat"] = cLat //centerLat;      
            mapCenterArr["lng"] = cLng //centerLng;            
            finalItem ["mapCenter"] = mapCenterArr;
            finalItem ["annotations"] = arrAnnotations;            
            finalItem ["gmapmarker"] = arrGmapMarker;
            finalArray.push(finalItem);
            //arrPixelCoords.push(pixelCoords);
            jsonGmapMarker=JSON.stringify(arrGmapMarker);
            jsonAnnotations=JSON.stringify(arrAnnotations);
            finalJson=JSON.stringify(finalArray);     
          
    
          //District_Locality_Lat_Long.png(Akola_Balapur_20.688889_76.789942.png)
          var filename='';
          var district='';         
          var locality='';
          //var latlng   = new google.maps.LatLng(centerLat, centerLng)
          var latlng   = new google.maps.LatLng(cLat, cLng)          
          //var centerLat=latlng.lat()
          //var centerLng=latlng.lng()          
          geocoder = new google.maps.Geocoder();
                
          geocoder.geocode({'latLng': latlng}, function(results, status) {
           if (status == google.maps.GeocoderStatus.OK) {        
             if (results[0]) {
                for (var ac = 0; ac < results[0].address_components.length; ac++) {
                    var component = results[0].address_components[ac];
    
                    switch(component.types[0]) {
                        case 'locality':
                            locality = component.long_name;
                            break;
                        case 'administrative_area_level_2':
                            district = component.short_name;
                            break;
                        // case 'country':
                        //     storableLocation.country = component.long_name;
                        //     storableLocation.registered_country_iso_code = component.short_name;
                        //     break;
                    }
                }                
                $('#default_submit').css("display","none")
                $('#saving_submit').css("display","block") 
                $.ajax({
                  type:"POST",
                      url: 'ajax/save_edited_image_dataset',
                      data: {
                          'oldImageName':oldImageName,
                          'topLeftLat':topLeftLat,
                          'topLeftLng':topLeftLng,
                          'bottomRightLat':bottomRightLat,
                          'bottomRightLng':bottomRightLng,
                          'centerLat':cLat, //centerLat,
                          'centerLng':cLng, //centerLng,
                          'zoom':zoomLvlofImg,//zoomLevel,                           
                          'locality': locality,                
                          'markersJSON': jsonGmapMarker,
                          'annotationJSON':jsonAnnotations,                          
                      },
                      dataType: 'json',
                      success: function (data) {                
                          if (data.status==1) {
                            //alert("Image is captured and annotations are saved.");   
                            //var selIndex=$("#SelDistrictLoc").prop('selectedIndex');
                            $('#default_submit').css("display","block")
                            $('#saving_submit').css("display","none")
                            window.location.href ='displayimagesdataset?savedImgName=' + data.new_file_name

                          }
                          else if(data.status==-1){
                            alert("File with same name exists. Try some other name.");                
                          }
                          else{
                            alert("Something went wrong.");
                          }
                      },
                      error: function(xhr, textStatus, errorThrown) {
                      alert("Something went wrong.");
                    }
                });      
             }
            else{
              console.log("No reverse geocode results.")
              alert("Something went wrong.[No reverse geocode results]");
            }
           }
           else {
            console.log("Geocoder failed: " + status)
            alert("Something went wrong.[geocoder failed]");
           }
          }); 
        }
    }
    
  });  
  map.addListener('center_changed', function() {
      var clatlng=map.getCenter()
      var lat=clatlng.lat()
      var lng=clatlng.lng()
      $('#centerLatLng').text(lat+", "+lng)
    
  });
})  
/*-------Event Listeners End--------*/

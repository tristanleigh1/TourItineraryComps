var namespace;

function setup(params) {
    namespace = params;
    addSidebarButtons();
    updateRoute();
    //this is making the map load take too long
    adjustZoom();
    initDirectionsListener();
}

function findNearbyPOIs(marker) {
    $.ajax({
        url : "/tour/pop_radius/",
        contentType: "application/json; charset=utf-8",
        type : 'GET',
        data : {
            'lat' : marker.getPosition().lat(),
            'lng' : marker.getPosition().lng(),
            'radius' : marker.popRadius.getRadius(),
            'filter-status' : namespace.filterStatus
        },
        dataType : 'json',
        success : function (json) {
            // Only adds nearby POIs that aren't already in route
            var nearby_pois = [];
            for (var i=0; i < json["nearby_pois"].length; i++) {
                for (var j=0; j < namespace.markers.length; j++) {
                    if (namespace.markers[j].poi_id == json["nearby_pois"][i].poi_id) {
                        delete json["nearby_pois"][i];
                        break;
                    }
                }
                if (typeof json["nearby_pois"][i] !== 'undefined') {
                    nearby_pois.push(json["nearby_pois"][i]);
                }
            }
            if (nearby_pois.length == 0 && marker.popRadius.getRadius() <= 18000) {
                marker.popRadius.setRadius(marker.popRadius.getRadius() + 500);
                findNearbyPOIs(marker);
            } else {
                plotNearbyPois(nearby_pois, marker);
            }
        },
        cache : false,
        error : function(xhr, errmsg, err) {
            for (var i=0; i<namespace.radiusMarkers.length; i++) {
                marker = namespace.radiusMarkers[i];
                marker.setMap(null);
            }
            console.log(errmsg);
            console.log(xhr.status + " " + xhr.responseText);
        }
    });
}

function plotNearbyPois(nearby_pois, centerMarker) {
    // Get rid of namespace.markers from previous radius
    for (var i=0; i<namespace.radiusMarkers.length; i++) {
        marker = namespace.radiusMarkers[i];
        marker.setMap(null);
    }
    namespace.radiusMarkers.length = 0;

            // Plot the pois only if they fall into the circle
            var circleRadius = centerMarker.popRadius.getRadius();
            var center = centerMarker.position;
    for (var i=0; i<nearby_pois.length; i++) {
                    var point = new google.maps.LatLng(parseFloat(nearby_pois[i].latitude), parseFloat(nearby_pois[i].longitude));
                    if (google.maps.geometry.spherical.computeDistanceBetween(point, center) >= circleRadius) {
                        continue;
                    }

        var icon = getIconFromCategory(nearby_pois[i].category, false);
        var popRadius = new google.maps.Circle({
            strokeWeight: 0,
            fillColor: '#FF0000',
            fillOpacity: 0.35,
            map: namespace.map,
            radius: 500,
            visible: false
        });

        var marker = new google.maps.Marker({
            map: namespace.map,
            position: point,
            name: nearby_pois[i].name,
            poi_id: nearby_pois[i].poi_id,
            id: namespace.radiusMarkers.length,
            rating: nearby_pois[i].rating,
            category: nearby_pois[i].category,
            address: nearby_pois[i].address,
            icon: icon,
            popRadius: popRadius
        });
        marker.addListener('click', function() {
            createInfoWindow(this, centerMarker);
        });
        namespace.radiusMarkers.push(marker);
    }
}

function createPopRadius(marker) {
    namespace.selectedMarker = marker;
    marker.popRadius.setCenter(marker.position);
    for (var i = 0; i < namespace.markers.length; i++) {
        namespace.markers[i].popRadius.setVisible(false);
        namespace.markers[i].popRadius.setRadius(500);
    }
    marker.popRadius.setVisible(true);
}

// Called when path POI marker is clicked
function createInfoWindow(marker, centerMarker) {
    var onclick;
    var centerMarkerId;

    // There is no centerMarker if the marker is on our path
    if (centerMarker == null) {
        onclick = ' onclick="removePoint(' + marker.id + ');">' +
        '<span class="glyphicon glyphicon-trash"></span>';
    } else {
        centerMarkerId = centerMarker.id;
        onclick = ' onclick="addPoint(' + marker.id + ', ' +
        centerMarker.id + ');">Add';
    }

    var content = '<p>' + marker.name + '</p><p>Yelp rating: ' +
    marker.rating + '/5</p><div class="btn btn-primary btn-sm"' + onclick +
    '</div><div class="btn btn-link btn-sm"' +
    'onclick="setInfoWindowContent('+ marker.id + ', ' + centerMarkerId +
    ');">More Info...</div>';

    namespace.popWindow.marker = marker;
    namespace.popWindow.setContent(content);
    namespace.popWindow.open(namespace.map, marker);
}

//Called when user clicks on "More Info..." button in info window
function setInfoWindowContent(markerId, centerMarkerId) {
    var marker;
    var onclick;

    if (!centerMarkerId) {
        marker = namespace.markers[markerId];
        onclick = ' onclick="removePoint(' + marker.id + ');">' +
        '<span class="glyphicon glyphicon-trash"></span>';
    } else {
        marker = namespace.radiusMarkers[markerId];
        onclick = ' onclick="addPoint(' + marker.id + ', ' +
        centerMarkerId + ');">Add';
    }

    var content = '<p>' + marker.name + '</p><p>Yelp rating: '
    + marker.rating + '</p><img src="https://maps.googleapis.com/maps/'
    + 'api/streetview?size=400x150&location=' + marker.getPosition().lat()
    + ',' + marker.getPosition().lng()
    + '&key=AIzaSyAhEeD2Dgvw-AAxGR9_qL7P9JlTeO-WjvM" ><br/><div class="'
    + 'btn btn-primary btn-sm"' + onclick + '</div><div class="'
    + 'btn btn-link btn-sm" onclick="resetInfoWindow('+ marker.id + ', '
    + centerMarkerId + ');">Less Info</div>';

    namespace.popWindow.setContent(content);
}

function resetInfoWindow(markerId, centerMarkerId) {
    if (centerMarkerId == null) {
        var marker = namespace.markers[markerId];
        createInfoWindow(marker, null);
    } else {
        var centerMarker = namespace.markers[centerMarkerId];
        createInfoWindow(namespace.radiusMarkers[markerId], centerMarker);
    }
}

function removePoint(markerId) {
    namespace.markers[markerId].popRadius.setVisible(false);
    namespace.markers[markerId].setMap(null);
    namespace.markers.splice(markerId, 1);
    for (var i = markerId; i < namespace.markers.length; i++) {
        namespace.markers[i].id--;
        namespace.markers[i].label--;
        namespace.markers[i].setMap(null)
        namespace.markers[i].popRadius.setVisible(false);
        namespace.markers[i].setMap(namespace.map);
    }

    updateRoute();

    for (var i=0; i<namespace.radiusMarkers.length; i++) {
        marker = namespace.radiusMarkers[i];
        marker.setMap(null);
        marker.popRadius.setVisible(false);
    }


    $("#accordion").empty();
    addSidebarButtons();
}

function addPoint(newMarkerId, markerId) {
    var summary = ""
    // Synchronous call to get summary for new point added to namespace.map
    $.ajax({
        async: false,
        url : "/tour/get_summary_for_added_point/",
        contentType: "application/json; charset=utf-8",
        type : 'GET',
        data : {
            'id' : namespace.radiusMarkers[newMarkerId].poi_id
        },
        dataType : 'json',
        success : function(json) {
            summary = json['summary'];
        },
        cache : false,
        error : function(xhr, errmsg, err) {
            console.log(errmsg);
            console.log(xhr.status + " " + xhr.responseText);
        }
    });

    var icon = getIconFromCategory(namespace.radiusMarkers[newMarkerId].category, true);

    var popRadius = new google.maps.Circle({
        strokeWeight: 0,
        fillColor: '#FF0000',
        fillOpacity: 0.35,
        map: namespace.map,
        radius: 500,
        visible: false
    });

    var newMarker = new google.maps.Marker({
        map: namespace.map,
        position: namespace.radiusMarkers[newMarkerId].position,
        name: namespace.radiusMarkers[newMarkerId].name,
        rating: namespace.radiusMarkers[newMarkerId].rating,
        id: markerId,
        poi_id: namespace.radiusMarkers[newMarkerId].poi_id,
        label: (markerId+1).toString(),
        summary: summary,
        category: namespace.radiusMarkers[newMarkerId].category,
        address: namespace.radiusMarkers[newMarkerId].address,
        icon: icon,
        popRadius: popRadius
    });
    newMarker.addListener('click', function() {
        createPopRadius(this);
        createInfoWindow(this, null);
        findNearbyPOIs(this);
    });
    namespace.markers.splice(markerId+1, 0, newMarker);

    //refresh namespace.markers on namespace.map with updated labels
    for (var i = markerId+1; i < namespace.markers.length; i++) {
        namespace.markers[i].id++;
        namespace.markers[i].label = i + 1;
        namespace.markers[i].setMap(null);
        namespace.markers[i].popRadius.setVisible(false);
        namespace.markers[i].setMap(namespace.map);
    }

    updateRoute();
    adjustZoom();

    for (var i=0; i<namespace.radiusMarkers.length; i++) {
        marker = namespace.radiusMarkers[i];
        marker.setMap(null);
        marker.popRadius.setVisible(false);
    }
    namespace.radiusMarkers.length = 0;

    $("#accordion").empty();
    addSidebarButtons();
    namespace.selectedMarker = null;
}

function updateRoute() {
    var waypoints = [];
    for (var i = 1; i < namespace.markers.length - 1; i++) {
        waypoints.push({location: namespace.markers[i].getPosition()});
    }
    namespace.directionsService.route({
        origin: namespace.markers[0].getPosition(),
        destination: namespace.markers[namespace.markers.length - 1].getPosition(),
        waypoints: waypoints,
        travelMode: 'WALKING',
        optimizeWaypoints: false //we may want to enable this
    }, function(response, status) {
        if (status === 'OK') {
            namespace.directionsDisplay.setDirections(response);

            //                namespace.map.setZoom(7);

            // Compute the total distance of the route
            var totalDistance = 0;
            var totalDuration = 0;
            var METERS_TO_MILES = 0.000621371192;
            var mytinerary = response.routes[0];
            for (var i = 0; i < mytinerary.legs.length; i++) {
                totalDistance += mytinerary.legs[i].distance.value
                totalDuration += mytinerary.legs[i].duration.value
            }

            // Let Google determine if we should use miles or km
            var units = mytinerary.legs[0].distance.text.substr(-2);
            if (units == "km") {
                totalDistance = totalDistance / 1000;
            } else {
                totalDistance = totalDistance * METERS_TO_MILES;
            }

            totalDuration = totalDuration / 60
            document.getElementById("distance").innerHTML = totalDistance.toFixed(1) + units;
            document.getElementById("walkingTime").innerHTML = totalDuration.toFixed(0) + " mins";


        } else {
            window.alert('Directions request failed due to ' + status);
        }
    });
}

function addSidebarButtons() {
    for (var i = 0; i < namespace.markers.length; i++) {
        $("#accordion").append(
            `<div class="panel panel-info">
                <div class="`+ namespace.markers[i].category +`">
                    <div class="panel-heading" role="tab" id="heading`+ i +`">
                        <h4 class="panel-title">
                            <a class="collapsed" role="button" data-toggle="collapse" data-parent="#accordion" href="#collapse` +
                                i + `" aria-expanded="false" aria-controls="collapse` + i + `">
                                ` + (i + 1) + `: ` + namespace.markers[i].name + `
                            </a>
                        </h4>
                    </div>
                </div>
                <div id="collapse` + i + `" class="panel-collapse collapse" role="tabpanel" aria-labelledby="heading` +
                    i + `">
                    <div class="panel-body">
                        ` + namespace.markers[i].summary + `
                    </div>
                    </div>
            </div>`
        );
        namespace.markers[i].popRadius.setVisible(false);
    }
}

// Adds a listener to the directions panel for when it's finished loading
function initDirectionsListener() {
    directionsPanel = document.getElementById("panel");
    if (directionsPanel.addEventListener) {
        directionsPanel.addEventListener('DOMSubtreeModified', modifyIcons, false);
    }
}

// Constructs the URL for the google.maps version of your route
function sendDirections() {
    var url = 'https://www.google.com/maps/dir';
    for (var i = 0; i < namespace.markers.length; i++) {
        url += "/" + namespace.markers[i].address;
    }
    url = url.replace(/\s/g, "+");
    url = url.replace(/,/g, "");
    url += "/data=!4m2!4m1!3e2"; // Data for making travel mode walking

    window.open(url, "_blank");
}

function getDirections() {
    if (document.getElementById('accordion').style.display == 'none') {
        document.getElementById('accordion').style.display = 'block';
        document.getElementById('db').innerHTML = "Get Directions!";
        document.getElementById('sendDirections').style.display = 'none';
        document.getElementById('panel').style.display = 'none';
    } else {
        document.getElementById('accordion').style.display = 'none';
        document.getElementById('db').innerHTML = "Go back";
        document.getElementById('sendDirections').style.display = 'inline-block';
        document.getElementById('panel').style.display = 'block';
        namespace.directionsDisplay.setPanel(document.getElementById('panel'));
    }


}

//drag sidebar buttons to update route
$( function() {
    $( "#accordion" ).sortable({
        axis: "y",
        handle: "h4",
        start: function(event, ui) {
            var start_idx = ui.item.index();
            ui.item.data('start_idx', start_idx);
        },
        update: function(event, ui) {
            var start_idx = ui.item.data('start_idx');
            var end_idx = ui.item.index();
            namespace.markers[start_idx].id = end_idx;
            namespace.markers[start_idx].label = end_idx+1;
            namespace.markers[start_idx].setMap(null);
            namespace.markers[start_idx].popRadius.setVisible(false);
            namespace.markers[start_idx].setMap(namespace.map);

            //refresh namespace.markers on namespace.map with updated labels
            if (start_idx > end_idx) { //drag down
                namespace.markers.splice(end_idx, 0, namespace.markers[start_idx]);
                namespace.markers.splice(start_idx+1, 1);
                for (var i = end_idx + 1; i <= start_idx; i++) {
                    namespace.markers[i].id++;
                    namespace.markers[i].label = i + 1;
                    namespace.markers[i].setMap(null);
                    namespace.markers[i].popRadius.setVisible(false);
                    namespace.markers[i].setMap(namespace.map);
                }
            } else { //drag up
                namespace.markers.splice(end_idx+1, 0, namespace.markers[start_idx]);
                namespace.markers.splice(start_idx, 1);
                for (var i = start_idx; i < end_idx; i++) {
                    //***************this doesn't look right to me (but it seems to work)*************
                    namespace.markers[i].id--;
                    namespace.markers[i].label = i + 1;
                    namespace.markers[i].setMap(null);
                    namespace.markers[i].popRadius.setVisible(false);
                    namespace.markers[i].setMap(namespace.map);
                }
            }

            updateRoute();
            for (var i=0; i<namespace.radiusMarkers.length; i++) {
                var marker = namespace.radiusMarkers[i];
                marker.setMap(null);
                marker.popRadius.setVisible(false);
            }
            namespace.radiusMarkers.length = 0;

            $("#accordion").empty();
            addSidebarButtons();
        }
    });
});

function updateFilterStatus(spot) {
    var shiftedStatus = namespace.filterStatus >> spot;
    if (shiftedStatus % 2 == 0) {
        namespace.filterStatus += Math.pow(2, spot);
    }
    else {
        namespace.filterStatus -= Math.pow(2, spot);
    }
}

function updateFilter(spot) {
    updateFilterStatus(spot);
    if (namespace.selectedMarker) {
        findNearbyPOIs(namespace.selectedMarker);
    }
}

function adjustZoom() {
    var listener = google.maps.event.addListener(namespace.map, "idle", function() { 
        if (namespace.map.getZoom() > 16) {
            namespace.map.setZoom(16); 
            google.maps.event.removeListener(listener);
        }
    });
}

function getIconFromCategory(category, scale) {
	var icon;
	switch (category) {
			case "Museums":
			icon = {url: "https://maps.gstatic.com/mapfiles/ms2/micons/blue.png"}
			break;
			case "Landmarks":
			icon = {url: "https://maps.gstatic.com/mapfiles/ms2/micons/pink.png"}
			break;
			case "Activities":
			icon = {url: "https://maps.gstatic.com/mapfiles/ms2/micons/yellow.png"}
			break;
			case "Nature":
			icon = {url: "https://maps.gstatic.com/mapfiles/ms2/micons/green.png"}
			break;
			case "Restaurants":
			icon = {url: "https://maps.gstatic.com/mapfiles/ms2/micons/red.png"}
			break;
			default:
			icon = {url: "https://maps.gstatic.com/mapfiles/ms2/micons/purple.png"}
			break;
	}
	if (scale == true) {
		icon["scaledSize"] = new google.maps.Size(45, 45);
	} else {
		icon["url"] = icon["url"].replace(".png", "-dot.png");
	}
	return icon;
}


function modifyIcons() {
    document.getElementById("panel").removeEventListener('DOMSubtreeModified', modifyIcons, false);

    var icons = document.getElementsByClassName("adp-marker");
    for (var i = 0; i < icons.length; i++) {
            icons[i].src = namespace.markers[i].icon.url;
            $(icons[i]).wrap('<div class="icon-container"></div>');
            $( '<p class="icon-label">' + (i + 1) + '</p>' ).insertAfter(icons[i]);
    }
}

/**
*  route.js
*
*  This file contains helper functions for map.html.
*  3/7/16
*/

/*
namespace = {
    markers: markers,
    radiusMarkers: radiusMarkers,
    popWindow: popWindow,
    map: map,
    directionsService: directionsService,
    directionsDisplay: directionsDisplay,
    filterStatus: 31,
    selectedMarker: null
}
*/
var namespace;
var zoomIgnore;

/**
* Initialize parameters and initial route
*/
function setup(params) {
    zoomIgnore = false;
    namespace = params;
    addSidebarButtons();
    updateRoute();
    //this is making the map load take too long
    adjustZoom();
}

/**
* Takes a marker on the route and queries the database for POIs that are
* within its pop radius.
*/
function findNearbyPOIs(marker) {
    $.ajax({
        url : "/tour/pop_radius/",
        contentType: "application/json; charset=utf-8",
        type : 'GET',
        data : {
            'lat' : marker.getPosition().lat(),
            'lng' : marker.getPosition().lng(),
            'radius' : marker.popRadius.getRadius(),
            'filter-status' : namespace.filterStatus,
        },
        dataType : 'json',
        success : function (json) {
            // Only adds nearby POIs that aren't already in route
            // console.log(json);
            var nearby_pois = [];
            for (var i=0; i < json["nearby_pois"].length; i++) {
                for (var j=0; j < namespace.markers.length; j++) {
                    if (namespace.markers[j].poi_id == json["nearby_pois"][i].poi_id) {
                        delete json["nearby_pois"][i];
                        break;
                    }
                    if (namespace.markers[j].name == json["nearby_pois"][i].name) {
                        delete json["nearby_pois"][i];
                        break;
                    }
                }
                if (typeof json["nearby_pois"][i] !== 'undefined') {
                    nearby_pois.push(json["nearby_pois"][i]);
                }
            }
            /* I (Caleb) am commenting this out because now the user can update the radius
            if (nearby_pois.length == 0 && marker.popRadius.getRadius() <= 18000) {
            marker.popRadius.setRadius(marker.popRadius.getRadius() + 500);
            findNearbyPOIs(marker);
                } else {
                plotNearbyPois(nearby_pois, marker);
            }
            */
            // console.log("Nearby POIS: ", nearby_pois)
            plotNearbyPois(nearby_pois, marker);
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
        var popRadius = buildPopRadiusCircle(point, namespace.map);

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
            popRadius: popRadius,
            summary: nearby_pois[i].summary,
        });


            (
              function (_popRadius, ignore, _marker) {
                _popRadius.addListener("center_changed", function() {
                if (ignore) {
                  // console.log("here");
                  ignore = false;
                  return;
                }
                _popRadius.setEditable(false);
                ignore = true;
                // console.log("outside");
                _popRadius.setCenter(_marker.position);
                _popRadius.setEditable(true);
              });
            })(popRadius, false, marker);


        google.maps.event.addListener(marker.popRadius, 'radius_changed', function() {
            if (marker.popRadius.getRadius() != 500) {
                findNearbyPOIs(marker);
            }
        });

        marker.addListener('click', function() {
            createInfoWindow(this, centerMarker);
        });
        namespace.radiusMarkers.push(marker);
    }
}

function buildPopRadiusCircle(center, map) {
    return new google.maps.Circle({
        center: center,
        strokeWeight: 0,
//        fillColor: '#FF0000',
        fillColor: '#772953',
        fillOpacity: 0.4,
        map: map,
        radius: 500,
        visible: false,
        editable: true,
        draggable: false
    });
}

function createPopRadius(marker) {
    namespace.selectedMarker = marker;
    marker.popRadius.setCenter(marker.position);
    for (var i = 0; i < namespace.markers.length; i++) {
        namespace.markers[i].popRadius.setVisible(false);
        if (namespace.markers[i].popRadius.getRadius() != 500) {
            namespace.markers[i].popRadius.setRadius(500);
        }
    }
    marker.popRadius.setVisible(true);
}

// Called when POI marker is clicked
function createInfoWindow(marker, centerMarker) {
    var onclick;
    var centerMarkerId
    var rating = (marker.rating == "None") ? "" : "Rating: " + Math.round(marker.rating) + "/100";

    // There is no centerMarker if the marker is on our path
    if (centerMarker == null) {
        onclick = ' id="removeBtn" onclick="removePoint(' + marker.id + ');">' +
        '<span class="glyphicon glyphicon-trash"></span>';
    } else {
        centerMarkerId = centerMarker.id;
        onclick = 'id="addBtn" onclick="addPoint(' + marker.id + ', ' +
        centerMarker.id + ');">Add';
    }

    var content = '<p>' + marker.name + '</p><p>' +
    rating + '</p><div class="btn btn-primary btn-sm"' + onclick +
    '</div><div class="btn btn-link btn-sm"' +
    'onclick="setInfoWindowContent('+ marker.id + ', ' + centerMarkerId +
    ');">More Info...</div>';
    // console.log(content);
    namespace.popWindow.marker = marker;
    namespace.popWindow.setContent(content);
    namespace.popWindow.open(namespace.map, marker);
}

// Called when user clicks on "More Info..." button in info window
function setInfoWindowContent(markerId, centerMarkerId) {
    var marker;
    var onclick;

    if (typeof centerMarkerId === "undefined") {
        marker = namespace.markers[markerId];
        console.log(marker);
        console.log(markerId);
        console.log(marker.id)
        onclick = ' id="removeBtn" onclick="removePoint(' + marker.id + ');">' +
        '<span class="glyphicon glyphicon-trash"></span>';
    } else {
        marker = namespace.radiusMarkers[markerId];
        onclick = 'id="addBtn" onclick="addPoint(' + marker.id + ', ' +
        centerMarkerId + ');">Add';
    }

    var content = '<p>' + marker.name + `</p>
    <p>Rating: `+ marker.rating + `/100.0</p>
    <div id="myCarousel" class="carousel slide" data-interval="false" >
    <div class="carousel-inner" style="height:150px;width:400px;overflow-y:auto;">
    <div class="active item">
    <img src="https://maps.googleapis.com/maps/api/streetview?size=400x150&location=`
    + marker.getPosition().lat() + ',' + marker.getPosition().lng() + `&key=AIzaSyAhEeD2Dgvw-AAxGR9_qL7P9JlTeO-WjvM" >
    </div>
    <div class="item">
    <p>` + marker.summary + `</p>
    </div>
    </div>
    <!--<div class="btn btn-sm btn-info" href="#myCarousel" data-slide="prev">Prev</div>-->

    </div>
    <br/>
    <div class="btn btn-primary btn-sm"` + onclick + `</div>
    <div class="btn btn-link btn-sm" onclick="resetInfoWindow(`+ marker.id + ', ' + centerMarkerId + `);">Less Info</div>
    <div class="btn btn-sm btn-primary pull-right" href="#myCarousel" data-slide="next">Next</div>`;

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
    if (namespace.markers.length == 1) {
        var errorMessage = "Cannot delete last POI! Add more than one point to delete one.";
        $("#removeBtn").before("<p><b>" + errorMessage + "</b></p>");
        $(".btn.btn-primary.btn-sm").prop('onclick',null).off('click');
        //alert("Cannot delete last POI! Add more than one point to delete one.");
    } else {
        namespace.markers[markerId].popRadius.setVisible(false);

        // Remove nearby_pois from map
        for (var i=0; i<namespace.radiusMarkers.length; i++) {
            marker = namespace.radiusMarkers[i];
            marker.setMap(null);
        }
        namespace.radiusMarkers.length = 0;

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
    }

    for (var i=0; i<namespace.radiusMarkers.length; i++) {
        marker = namespace.radiusMarkers[i];
        marker.setMap(null);
        marker.popRadius.setVisible(false);
    }


    $("#accordion").empty();
    addSidebarButtons();
}

function addPoint(newMarkerId, markerId, verified) {
    var summary = ""
    //************************WE SHOULD GET RID OF THIS************************
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
    var popRadius = buildPopRadiusCircle(namespace.radiusMarkers[newMarkerId].position, namespace.map);

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

    (function (_popRadius, ignore, _marker) {
        _popRadius.addListener("center_changed", function() {
            if (ignore) {
                console.log("here");
                ignore = false;
                return;
            }
            _popRadius.setEditable(false);
            ignore = true;
            console.log("outside");
            _popRadius.setCenter(_marker.position);
            _popRadius.setEditable(true);
        });
    })(popRadius, false, newMarker);

    google.maps.event.addListener(newMarker.popRadius, 'radius_changed', function() {
        if (newMarker.popRadius.getRadius() != 500) {
            findNearbyPOIs(newMarker);
        }
    });

    newMarker.addListener('click', function() {
        createPopRadius(this);
        createInfoWindow(this, null);
        findNearbyPOIs(this);
    });
    namespace.markers.splice(markerId+1, 0, newMarker);

    updateRoute(markerId+1);
}


/**
* Updates the route and directions display to match the current path markers
*/
function updateRoute(changedMarkerId) {
    var waypoints = [];
    for (var i = 1; i < namespace.markers.length - 1; i++) {
        waypoints.push({location: namespace.markers[i].getPosition()});
    }

    namespace.directionsService.route({
        origin: namespace.markers[0].getPosition(),
        destination: namespace.markers[namespace.markers.length - 1].getPosition(),
        waypoints: waypoints,
        travelMode: 'WALKING',
    }, function(response, status) {
        if (status === 'OK') {
            namespace.directionsDisplay.setDirections(response);

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
            $("#distance").html(totalDistance.toFixed(1) + units);
            $("#walkingTime").html(totalDuration.toFixed(0) + " mins");

            // If we added a point, refresh namespace.markers on namespace.map
            if (changedMarkerId) {
                for (var i = changedMarkerId; i < namespace.markers.length; i++) {
                    namespace.markers[i].id++;
                    namespace.markers[i].label = i + 1;
                    namespace.markers[i].setMap(null);
                    namespace.markers[i].popRadius.setVisible(false);
                    namespace.markers[i].setMap(namespace.map);
                }
                $("#warning").empty();
            }

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

        } else {
            var errorMessage;
            switch (status) {
                case 'MAX_WAYPOINTS_EXCEEDED':
                    // Google's limit is 23 waypoints (+ start/end)
                    errorMessage = "Sorry, you cannot add more stops.";
                    break;
                case 'ZERO_RESULTS':
                    errorMessage = "Sorry, this POI is inaccessable from your path.";
                    break;
                default:
                    errorMessage = "Directions request failed due to " + status;
            }

            if (changedMarkerId) {
                // Remove the marker and add the error message
                namespace.markers[changedMarkerId].setMap(null);
                namespace.markers.splice(changedMarkerId, 1);
                $("#addBtn").before("<p><b>" + errorMessage + "</b></p>");
                $(".btn.btn-primary.btn-sm").prop('onclick',null).off('click');
            } else {
                // The original path is invalid, remove destination and try again
                $("#warning").html("Sorry! We couldn't find a route to your destination!");
                namespace.markers[namespace.markers.length - 1].setMap(null);
                namespace.markers.splice(-1, 1);
                updateRoute();
            }
        }
    });

    if (document.getElementById('panel').innerHTML == "") {
        initDirectionsListener();
    } else {
        modifyIcons();
    }
}

function addSidebarButtons() {
    for (var i = 0; i < namespace.markers.length; i++) {
        $("#accordion").append(
            `<div class="panel panel-default">
            <div class="shell `+ namespace.markers[i].category +`">
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

function modifyIcons() {
    document.getElementById("panel").removeEventListener('DOMSubtreeModified', modifyIcons, false);

    var icons = document.getElementsByClassName("adp-marker");
    var iconLabelsExist = document.getElementsByClassName("icon-label").length;
    for (var i = 0; i < icons.length; i++) {
        //console.log(icons[i].src);
        icons[i].src = namespace.markers[i].icon.url;
        if (!iconLabelsExist) {
            $(icons[i]).wrap('<div class="icon-container"></div>');
            $( '<p class="icon-label">' + (i + 1) + '</p>' ).insertAfter(icons[i]);
        }
    }
}

function autotab(current) {
    if (current.getAttribute && current.value.length==current.getAttribute("maxlength")) {
        $(current).nextAll('input').first().focus();
    }
}

// Constructs the URL for the google.maps version of your route
function sendDirections() {
    var url = 'https://www.google.com/maps/dir';
    var directionsAddresses = []
    var route = namespace.directionsDisplay.getDirections().routes[0];
    if (route.legs.length > 13) {
        alert("Google maps cannot render this many points");
        return;
    }
    for (var i = 0; i < route.legs.length; i++) {
        if (i == 0) {
            directionsAddresses.push(route.legs[i].start_address);
        }
        directionsAddresses.push(route.legs[i].end_address);
    }

    for (var i = 0; i < directionsAddresses.length; i++) {
        url += "/" + directionsAddresses[i];
    }
    url = url.replace(/\s/g, "+");
    url = url.replace(/,/g, "");
    url += "/data=!4m2!4m1!3e2"; // Data for making travel mode walking

    var phoneNumber = $('input[name=phone1]').val() + $('input[name=phone2]').val() + $('input[name=phone3]').val()

    $.ajax({
        url : "/tour/send_directions/",
        type : 'GET',
        data : { 'url' : url,
                'number' : phoneNumber},
        success : function(success) {
            console.log(success);
        },
        cache : false,
        error : function(xhr, errmsg, err) {
            window.open(url, "_blank");
            console.log(errmsg);
            console.log(xhr.status + " " + xhr.responseText);
        }
    });
}

function getDirections() {
    // If the directions pane is open
    if (document.getElementById('accordion').style.display == 'none') {
        document.getElementById('accordion').style.display = 'block';
        document.getElementById('db').innerHTML = "Get Directions!";
        document.getElementById('modal_trigger').style.display = 'none';
        document.getElementById('panel').style.display = 'none';
        // If the accordion pane is open
    } else {
        document.getElementById('accordion').style.display = 'none';
        document.getElementById('db').innerHTML = "Go back";
        document.getElementById('modal_trigger').style.display = 'inline-block';
        document.getElementById('panel').style.display = 'block';
        namespace.directionsDisplay.setPanel(document.getElementById('panel'));
    }


}

//drag sidebar buttons to update route
$( function() {
    $( "#accordion" ).sortable({
        axis: "y",
        handle: ".panel-heading",
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

//make sure map isn't zoomed in too much
function adjustZoom() {
    var listener = google.maps.event.addListener(namespace.map, "zoom_changed", function() {
        if (zoomIgnore) {
          zoomIgnore = false;
          return;
        }
        if (namespace.map.getZoom() > 16) {
            zoomIgnore = true;
            namespace.map.setZoom(16);
        }
        google.maps.event.removeListener(listener);
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

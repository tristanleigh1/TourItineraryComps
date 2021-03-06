/**
*  route.js
*
*  This file contains helper functions for map.html.
*
*  @author Braun, Jones, Leigh, Tuchow
*  3/7/16
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

/**
* Takes a JSON Object of POIs near the marker on the path that has been selected
* and plots them on the map.
*/
function plotNearbyPois(nearby_pois, centerMarker) {
    // Get rid of markers from previous radius
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

        (function (_popRadius, ignore, _marker) {
            _popRadius.addListener("center_changed", function() {
                if (ignore) {
                    ignore = false;
                    return;
                }
                _popRadius.setEditable(false);
                ignore = true;
                _popRadius.setCenter(_marker.position);
                _popRadius.setEditable(true);
            });
        })(popRadius, false, marker);

        google.maps.event.addListener(marker.popRadius, 'radius_changed', function() {
            findNearbyPOIs(marker);
        });

        marker.addListener('click', function() {
            createInfoWindow(this, centerMarker);
        });
        namespace.radiusMarkers.push(marker);
    }
}

/**
* Adds pop radius circle on map
*/
function buildPopRadiusCircle(center, map) {
    return new google.maps.Circle({
        center: center,
        strokeWeight: 0,
        fillColor: '#772953',
        fillOpacity: 0.4,
        map: map,
        radius: 500,
        visible: false,
        editable: true,
        draggable: false
    });
}

/**
* Changes selected marker and clears previous popradiuses
*/
function createPopRadius(marker) {
    if (namespace.selectedMarker) {
        namespace.selectedMarker.popRadius.setVisible(false);
        namespace.selectedMarker.popRadius.setRadius(500);
    }
    namespace.selectedMarker = marker;
    namespace.selectedMarker.popRadius.setVisible(true);
}

/**
* Takes a marker and a center marker, and if the marker is on path
* the centerMarker will be null. Creates an info window for the selected marker.
* Only called when POI marker is clicked.
*/
function createInfoWindow(marker, centerMarker) {
    var onclick;
    var centerMarkerId
    var rating = (marker.rating == "None") ? "" : "Rating: " + Math.round(marker.rating) + "/100";
    var errorMessage = ($("#err").length) ? $("#err").html() : "";

    // There is no centerMarker if the marker is on our path
    if (centerMarker == null) {
        onclick = ' id="removeBtn" onclick="removePoint(' + marker.id + ');">' +
        '<span class="glyphicon glyphicon-trash"></span>';
    } else {
        centerMarkerId = centerMarker.id;
        onclick = ' id="addBtn" onclick="addPoint(' + marker.id + ', ' +
        centerMarker.id + ');">Add';
    }

    var content = '<p>' + marker.name + '</p><p>' +
    rating + '</p><p id="err">' + errorMessage +
    '</p><div class="btn btn-primary btn-sm"' + onclick +
    '</div><div class="btn btn-link btn-sm"' +
    'onclick="setInfoWindowContent('+ marker.id + ', ' + centerMarkerId +
    ');">More Info...</div>';

    namespace.popWindow.marker = marker;
    namespace.popWindow.setContent(content);
    namespace.popWindow.open(namespace.map, marker);
}

/**
* Changes info window to a More Info window. Called when user clicks
* on "More Info..." button in info window.
*/
function setInfoWindowContent(markerId, centerMarkerId) {
    var marker;
    var onclick;

    if (typeof centerMarkerId === "undefined") {
        marker = namespace.markers[markerId];
        onclick = ' id="removeBtn" onclick="removePoint(' + marker.id + ');">' +
        '<span class="glyphicon glyphicon-trash"></span>';
    } else {
        marker = namespace.radiusMarkers[markerId];
        onclick = ' id="addBtn" onclick="addPoint(' + marker.id + ', ' +
        centerMarkerId + ');">Add';
    }

    var rating = (marker.rating == "None") ? "" : "Rating: " + Math.round(marker.rating) + "/100";
    var errorMessage = ($("#err").length) ? $("#err").html() : "";
    var content = '<p>' + marker.name + `</p>
    <p>`+ rating + `</p>
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
    </div>
    <br/><p id="err">` + errorMessage + `</p>
    <div class="btn btn-primary btn-sm"` + onclick + `</div>
    <div class="btn btn-link btn-sm" onclick="resetInfoWindow(`+ marker.id + ', ' + centerMarkerId + `);">Less Info</div>
    <div class="btn btn-sm btn-primary pull-right" href="#myCarousel" onclick="if (this.innerHTML == 'Summary') {this.innerHTML='Back';} else {this.innerHTML = 'Summary';}" data-slide="next">Summary</div>`;
    namespace.popWindow.setContent(content);
}

/**
* Resets info window to Default window. Called when user clicks the less info button.
*/
function resetInfoWindow(markerId, centerMarkerId) {
    if (centerMarkerId == null) {
        var marker = namespace.markers[markerId];
        createInfoWindow(marker, null);
    } else {
        var centerMarker = namespace.markers[centerMarkerId];
        createInfoWindow(namespace.radiusMarkers[markerId], centerMarker);
    }
}

/**
* Takes a markerId and removes the corresponding marker (and nearby markers) from the map
*/
function removePoint(markerId) {
    if (namespace.markers.length == 1) {
        var errorMessage = "Cannot delete last POI! Add more than one point to delete one.";
        $("#err").html("<b>" + errorMessage + "</b>");
        return;
    }

    // Remove marker from map and marker array
    namespace.markers[markerId].popRadius.setVisible(false);
    namespace.markers[markerId].setMap(null);
    namespace.markers.splice(markerId, 1);

    // Update array of markers after removing point
    for (var i = markerId; i < namespace.markers.length; i++) {
        namespace.markers[i].setLabel((i+1).toString());
        namespace.markers[i].id--;
    }

    // Remove nearby POIs from map
    for (var i=0; i<namespace.radiusMarkers.length; i++) {
        marker = namespace.radiusMarkers[i];
        marker.setMap(null);
    }
    namespace.radiusMarkers.length = 0;

    updateRoute();
    $("#accordion").empty();
    addSidebarButtons();
}

/**
* Takes a nearby poi id in radius markers and the id of a path marker
* to create a new point in the route after the selected marker.
*/
function addPoint(newMarkerId, markerId) {
    $(".btn.btn-primary.btn-sm").prop('onclick',null).off('click');
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
        summary: namespace.radiusMarkers[newMarkerId].summary,
        category: namespace.radiusMarkers[newMarkerId].category,
        address: namespace.radiusMarkers[newMarkerId].address,
        icon: icon,
        popRadius: popRadius
    });

    (function (_popRadius, ignore, _marker) {
        _popRadius.addListener("center_changed", function() {
            if (ignore) {
                ignore = false;
                return;
            }
            _popRadius.setEditable(false);
            ignore = true;
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
* Updates the route and directions display to match the current path markers.
* Takes in the ID of the marker being added to the path. If no marker is being
* added to the path, this value is null.
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

            // Compute the total distance and duration of the route
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
            if (units == "mi" || units == "ft") {
                totalDistance = totalDistance * METERS_TO_MILES;
                units = "mi";
            } else {
                totalDistance = totalDistance / 1000;
                units = "km";
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

            // Remove nearby POI markers
            for (var i=0; i<namespace.radiusMarkers.length; i++) {
                marker = namespace.radiusMarkers[i];
                marker.setMap(null);
                marker.popRadius.setVisible(false);
            }
            namespace.radiusMarkers.length = 0;
            namespace.selectedMarker = null;

            $("#accordion").empty();
            addSidebarButtons();
            adjustZoom();
            if ($('#panel').html() != "") { updateDirectionsPanel(); }

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
                $("#err").html("<b>" + errorMessage + "</b>");
            } else {
                // The original path is invalid, remove destination and try again
                $("#warning").html("Sorry! We couldn't find a route to your destination!<br>");
                namespace.markers[namespace.markers.length - 1].setMap(null);
                namespace.markers.splice(-1, 1);
                updateRoute();
            }
        }
    });
}

/**
* Add the html for the sidebar for each POI on the route
*/
function addSidebarButtons() {
    for (var i = 0; i < namespace.markers.length; i++) {
        //$("#accordion").append(
            var panelDiv =
            `<div class="panel panel-default">
            <div class="shell `+ namespace.markers[i].category +`">
            <div class="panel-heading" role="tab" id="heading`+ i +`">
            <h4 class="panel-title" onclick="markerSelected(`+ i +`);">
            ` + (i + 1) + `: ` + namespace.markers[i].name + `
            </h4>
            <div class="btn btn-link btn-sm pull-right x-button" onclick="removePoint(` + i + `);">&times</div>
            </div>
            </div>
            <div id="collapse` + i + `" class="panel-collapse collapse" role="tabpanel" aria-labelledby="heading` +
            i + `">
            <div class="panel-body">
            ` + namespace.markers[i].summary + `
            </div>
            </div>
            </div>`;

        $("#accordion").append(panelDiv);
        namespace.markers[i].popRadius.setVisible(false);
    }
}

/**
 * Displays info window, pop radius, and nearby pois for given marker ID. Called from sidebar POIs.
*/
function markerSelected(markerId) {
    marker = namespace.markers[markerId];
    createPopRadius(marker);
    createInfoWindow(marker);
    findNearbyPOIs(marker);

}

/**
* Updates the directions panel to reflect changes to the route. Code adapted
* from a tutorial by Ryan Stephens found at
* http://www.sketchpad-media.com/docs/how-to/google-maps-v3-custom-direction-services/
*/
function updateDirectionsPanel() {
    var output = '';
    var route = namespace.directionsDisplay.getDirections().routes[0]
        for (var i = 0; i < namespace.markers.length - 1; i++) {
            var dir = route.legs[i]
            var cat = namespace.markers[i+1].category;
            if (i == 0) {
                output += '<div class="dir_start Origin">'+ dir.start_address +'</div>';
            }
            output += '<div class="dir_summary silver">Travel: '+ dir.distance.text +' - about '+ dir.duration.text +'</div>';
            output += '<table>';
            for (var j = 0; j < dir.steps.length; j++){
                output += '<tr style="border-bottom: 1px solid silver;">';
                output += '<td class="dir_row"><span class="dir_sprite '+ dir.steps[j].maneuver +'"></span></td>';
                output += '<td class="dir_row">'+ (j+1) +'.</td>';
                output += '<td class="dir_row">'+ dir.steps[j].instructions +'</td>';
                output += '<td class="dir_row" style="white-space:nowrap;">'+ dir.steps[j].distance.text +'</td>';
                output += '</tr>';
            }
                output += '</table>';
                output += '<div class="dir_end ' + cat + '"' + '>'+ dir.end_address +'</div>';
        }
    $('#panel').html(output);
}

/**
 * add an event listener to the directions panel div
 */
function initDirectionsListener() {
    directionsPanel = document.getElementById("panel");
    if (directionsPanel.addEventListener) {
        directionsPanel.addEventListener('DOMSubtreeModified', modifyIcons, false);
    }
}

/**
 * Modifies icons in direction panel
 */
function modifyIcons() {
    document.getElementById("panel").removeEventListener('DOMSubtreeModified', modifyIcons, false);

    var icons = document.getElementsByClassName("adp-marker");
    var iconLabelsExist = document.getElementsByClassName("icon-label").length;
    for (var i = 0; i < icons.length; i++) {
        icons[i].src = namespace.markers[i].icon.url;
        if (!iconLabelsExist) {
            $(icons[i]).wrap('<div class="icon-container"></div>');
            $( '<p class="icon-label">' + (i + 1) + '</p>' ).insertAfter(icons[i]);
        }
    }
}

/**
 */
function autotab(current) {
    if (current.getAttribute && current.value.length==current.getAttribute("maxlength")) {
        $(current).nextAll('input').first().focus();
    }
}

/**
 * Constructs the URL for the google.maps version of your route
 */
function sendDirections() {
    var long_url = getDirectionsURL(namespace.directionsDisplay);
    var login = "jonesh2";
    var api_key = "R_7d8d7eb547814128a370162f96dccaa6";

    $.getJSON(
        "http://api.bitly.com/v3/shorten?callback=?",
        {
            "format": "json",
            "apiKey": api_key,
            "login": login,
            "longUrl": long_url
        },
        function(response) {
            var short_url = response.data.url;
            sendText(short_url);
        }
    );
}

/**
 * Get directions for the route
 */
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
        updateDirectionsPanel();
    }
}

// Drag sidebar buttons to update route
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

            // Refreshes markers on map with updated labels
            if (start_idx > end_idx) { // Drag down in value (up in map)
                namespace.markers.splice(end_idx, 0, namespace.markers[start_idx]);
                namespace.markers.splice(start_idx+1, 1);
                for (var i = end_idx + 1; i <= start_idx; i++) {
                    namespace.markers[i].id++;
                    namespace.markers[i].label = i + 1;
                    namespace.markers[i].setMap(null);
                    namespace.markers[i].popRadius.setVisible(false);
                    namespace.markers[i].setMap(namespace.map);
                }
            } else { // Drag up in value, (down in map)
                namespace.markers.splice(end_idx+1, 0, namespace.markers[start_idx]);
                namespace.markers.splice(start_idx, 1);
                for (var i = start_idx; i < end_idx; i++) {
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

/**
* Updates the filter status by toggling a given category (indicated by the spot)
*/
function updateFilterStatus(spot) {
    var shiftedStatus = namespace.filterStatus >> spot;
    if (shiftedStatus % 2 == 0) {
        namespace.filterStatus += Math.pow(2, spot);
    }
    else {
        namespace.filterStatus -= Math.pow(2, spot);
    }
}

/**
 * Spot indicates which category was updated in the filter bar
 * Updates the nearby POIs in accordance with the new filter status
 */
function updateFilter(spot) {
    updateFilterStatus(spot);
    if (namespace.selectedMarker) {
        findNearbyPOIs(namespace.selectedMarker);
    }
}

/** Makes sure map isn't zoomed in too much.
 * Uses ignore as a way to avoid recursive calling.
 */
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

/**
 * Takes in a POI category string and scale boolean and returns an icon object.
 * If scale is false, returns a nearby POI icon instead of an icon on the route.
 */
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

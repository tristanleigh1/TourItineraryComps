/*
 * Javascript for the start and end address autocompletion. Also fills in the hidden
 * form fields for start and end long/lat. Written with help from the autocomplete
 * documentation found here:
 * https://developers.google.com/maps/documentation/javascript/examples/places-autocomplete
 *
 * @author Caleb Braun
 * 1/8/17
*/

// This requires the Places library. Include the libraries=places
// parameter when you first load the API.

function initAutocomplete() {
    var ac1 = document.getElementById('autocomplete1');
    var ac2 = document.getElementById('autocomplete2');

    autocompleteStart = new google.maps.places.Autocomplete(
        /** @type {!HTMLInputElement} */(ac1));
    autocompleteEnd = new google.maps.places.Autocomplete(
        /** @type {!HTMLInputElement} */(ac2));

    autocompleteStart.addListener('place_changed', function() {
        document.getElementById('startLngLat').value = autocompleteStart.getPlace().geometry.location;
        document.getElementById('startAddress').value = autocompleteStart.getPlace().formatted_address;
    });
    autocompleteEnd.addListener('place_changed', function() {
        document.getElementById('endLngLat').value = autocompleteEnd.getPlace().geometry.location;
        document.getElementById('endAddress').value = autocompleteEnd.getPlace().formatted_address;
    });
    $(ac1).on('input', function() { 
        document.getElementById('startLngLat').value = '';
    });

    google.maps.event.addDomListener(ac1, 'keydown', function(e) {
        if (e.keyCode == 13) {
            e.preventDefault();
            ac2.select();
        }
    });

    google.maps.event.addDomListener(ac2, 'keydown', function(e) {
        if (e.keyCode == 13) {
            e.preventDefault();
        }
    });
}

function getCityLatLng(city) {
    switch(city) {
        case 'London':
            return { lat: 51.507, lng: -0.127 }
        case 'Madrid':
            return { lat: 40.416, lng: -3.704 }
        case 'Minneapolis':
            return { lat: 44.978, lng: -93.265 }
        case 'New York':
            return { lat: 40.748, lng: -73.986 }
        case 'San Francisco':
            return { lat: 37.775, lng: -122.419 }
    }
}



// Bias the autocomplete object to the user's geographical location,
// as supplied by the city the user selects
function geolocate() {

    var city = document.getElementById('citySelect').value;
    var circle = new google.maps.Circle({
          center: getCityLatLng(city),
          radius: 100000 // 100 km
        });
    autocompleteStart.setBounds(circle.getBounds());
    autocompleteEnd.setBounds(circle.getBounds());
}

function validateForm() {
	var isValid = true;
	var form = document.forms["indexForm"];
	if (!form["startDestination"].value || form["startCoords"].value == '') {
		document.getElementById('autocomplete1').style.borderColor = "red";
		isValid = false;
	} else {
		document.getElementById('autocomplete1').removeAttribute("style");
	}

	// Check if we're in exploratory mode before checking if end value exists
	if ($("#start-to-end-fields").html() != '') {
        if (!form["endDestination"].value || !form["endCoords"].value) {
            document.getElementById('autocomplete2').style.borderColor = "red";
            isValid = false;
        } else {
            document.getElementById('autocomplete2').removeAttribute("style");
        }
    }

    // Check if either location is too far from the city center
    var city = document.getElementById('citySelect').value;
    var start = form["startCoords"].value;
    var end = form["endCoords"].value;
    var max = 1.0;
    if (start != '' && end != '') {
        var startLat = parseInt(start.lat);
        var startLng = parseInt(start.lng);
        var endLat = parseInt(end.lat);
        var endLng = parseInt(end.lng);
        if (startLat < city.lat + max || startLng < city.lng + max || endLat < city.lat + max || endLng < city.lng + max) {
            alert("Start or end too far away!");
        }
    }
    
	return isValid;
}

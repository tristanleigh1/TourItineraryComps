/*
 * Javascript for the start and end address autocompletion. Also fills in the hidden
 * form fields for start and end long/lat. Written with help from the autocomplete
 * documentation found here:
 * https://developers.google.com/maps/documentation/javascript/examples/places-autocomplete
 *
 * @author Caleb Braun
 * 1/8/17
*/


/**
 * Initializes the autocomplete and fills hidden form fields with their value
 */
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


/**
 * Takes a city name and returns the approximate lat/long of the center
 * of the city
 */
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


/**
 * Bias the autocomplete object to the user's geographical location,
 * as supplied by the city the user selects
 */
function geolocate() {

    var city = document.getElementById('citySelect').value;
    var circle = new google.maps.Circle({
          center: getCityLatLng(city),
          radius: 100000 // 100 km
        });
    autocompleteStart.setBounds(circle.getBounds());
    autocompleteEnd.setBounds(circle.getBounds());
}

/**
 * Ensures that when the form is sumbitted, the inputs are filled correctly
 * and the start and end are not too far apart
 */
function validateForm() {
    var isValid = true;
    var form = document.forms["indexForm"];
    var cityName = document.getElementById('citySelect').value;
    var city = getCityLatLng(cityName);
    var start = form["startCoords"].value.split(",");
    var max = 0.1;
    var errorMsg1 = "<p id=errorMsg1 style='color:crimson'>Start location is too far from " + cityName + "</p>";
    var errorMsg2 = "<p id=errorMsg2 style='color:crimson'>End location is too far from " + cityName + "</p>";

    // Remove previous error styling
    document.getElementById('autocomplete1').removeAttribute("style");
    $("#errorMsg1").html('');

    // Check if the start location is valid
    if (!form["startDestination"].value || form["startCoords"].value == '') {
        document.getElementById('autocomplete1').style.borderColor = "red";
        isValid = false;
    } else {
        // Check if end location is too far from city
        var startLat = parseFloat(start[0].substring(1));
        var startLng = parseFloat(start[1].substring(0,  start[1].length-1));
        if (startLat < city.lat - max || startLng < city.lng - max ||   startLat > city.lat + max || startLng > city.lng + max) {
            $("#autocomplete1").after(errorMsg1);
            isValid = false;
        }
    }

      // Check if we're in exploratory mode before checking if end location is valid
      if ($("#start-to-end-fields").html() != '') {
        var end = form["endCoords"].value.split(",");

        // Remove previous error styling
        document.getElementById('autocomplete2').removeAttribute("style");
        $("#errorMsg2").html('');

        if (!form["endDestination"].value || !form["endCoords"].value) {
            document.getElementById('autocomplete2').style.borderColor = "red";
            isValid = false;
        } else {
            // Check if end location is too far from city
            var endLat = parseFloat(end[0].substring(1));
            var endLng = parseFloat(end[0].substring(0, end[1].length-1));
            if (endLat < city.lat - max || endLng < city.lng - max || endLat > city.lat + max || endLng > city.lng + max) {
                $("#autocomplete2").after(errorMsg2);
                isValid = false;
            }
        }
    }

  return isValid;
}

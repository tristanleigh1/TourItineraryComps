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
    autocompleteStart = new google.maps.places.Autocomplete(
        /** @type {!HTMLInputElement} */(document.getElementById('autocomplete1')));    
    autocompleteEnd = new google.maps.places.Autocomplete(
        /** @type {!HTMLInputElement} */(document.getElementById('autocomplete2')));

    autocompleteStart.addListener('place_changed', function() {
        document.getElementById('startLngLat').value = autocompleteStart.getPlace().geometry.location;
    });
    autocompleteEnd.addListener('place_changed', function() {
        document.getElementById('endLngLat').value = autocompleteEnd.getPlace().geometry.location;
    });
}

// Bias the autocomplete object to the user's geographical location,
// as supplied by the city the user selects
function geolocate() {

    var geolocations = {
        'London': {
            lat: 51.507,
            lng: -0.127
        },
        'Madrid': {
            lat: 40.416, 
            lng: -3.704
        },
        'Minneapolis': {
            lat: 44.977753,
            lng: -93.265011
        },
        'New York': {
            lat: 40.748,
            lng: -73.986
        },
        'San Francisco': {
            lat: 37.774929, 
            lng: -122.419416
        }
    }

    var city = document.getElementById('citySelect').value;
    var circle = new google.maps.Circle({
          center: geolocations[city],
          radius: 100000 // 100 km
        });
    autocompleteStart.setBounds(circle.getBounds()); 
    autocompleteEnd.setBounds(circle.getBounds()); 
}

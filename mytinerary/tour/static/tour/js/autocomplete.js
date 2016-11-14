
// This example displays an address form, using the autocomplete feature
// of the Google Places API to help users fill in the information.

// This requires the Places library. Include the libraries=places
// parameter when you first load the API.

function initAutocomplete() {
    // Create the autocomplete object, restricting the search to geographical
    // location types.
    autocompleteStart = new google.maps.places.Autocomplete(
        /** @type {!HTMLInputElement} */(document.getElementById('autocomplete1')));    
    autocompleteEnd = new google.maps.places.Autocomplete(
        /** @type {!HTMLInputElement} */(document.getElementById('autocomplete2')));

    autocompleteStart.addListener('place_changed', handleStartAddress);
    autocompleteEnd.addListener('place_changed', handleEndAddress);
}

function handleStartAddress() {
    document.getElementById("autocomplete2").focus(); // ID set by OnFocusIn 
    findLngLat('autocomplete1');
}

function handleEndAddress() {
    findLngLat('autocomplete2');
}

function findLngLat(addressID) {
    geocoder = new google.maps.Geocoder();
    var address = document.getElementById(addressID).value;
    console.log(address);
    geocoder.geocode( { 'address': address}, function(results, status) {
      if (status == 'OK') {
        coordID = (addressID == 'autocomplete1') ? 'startLngLat' :'endLngLat';
        document.getElementById(coordID).value = results[0].geometry.location;
      } else {
        alert('Geocode was not successful for the following reason: ' + status);
      }
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
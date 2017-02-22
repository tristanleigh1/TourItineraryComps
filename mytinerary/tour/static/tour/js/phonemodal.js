/**
 * Sets the options for the modal
 */
$("#modal_trigger").leanModal({
    top: 100,
    overlay: 0.6,
    closeButton: ".modal_close"
});

$("#modal_trigger").click(function() {
    $('#gmaps').attr('href', getDirectionsURL(namespace.directionsDisplay));
});

/**
 * Given a url, gets a phone number from the phone input and sends the url to
 * that number.
 */
function sendText(url) {
    var phoneNumber = $('input[name=phone1]').val() + $('input[name=phone2]').val() + $('input[name=phone3]').val()
    if (phoneNumber.length != 10 || !/^\d+$/.test(phoneNumber)) {
        alert("Invalid phone number.");
        return;
    }

    $('.one_half .btn').html('<img src="/static/tour/images/loading.svg">');
    $('.one_half .btn').attr('href', 'javascript:void(0);');

    $.ajax({
        url : "/tour/send_directions/",
        type : 'GET',
        data : {'url' : url,
                'number' : phoneNumber},
        success : function(success) {
            closeSendDirectionsWindow(success);
        },
        cache : false,
        error : function(xhr, errmsg, err) {
            console.log(errmsg);
            console.log(xhr.status + " " + xhr.responseText);
        }
    });
}

function getDirectionsURL(directionsDisplay) {
    var url = 'https://www.google.com/maps/dir';
    var directionsAddresses = []
    var route = directionsDisplay.getDirections().routes[0];
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

    return url;
}


function closeSendDirectionsWindow(success) {
    $('.one_half .btn').html('Sent!');
    setTimeout(function(){
        $('.modal_close').trigger('click');
        $('.one_half .btn').attr('href', 'javascript:sendDirections();');
        $('.one_half .btn').html('Send');
    }, 1000);
}

/**
 * Sets the options for the modal
 */
$("#modal_trigger").leanModal({
    top: 100,
    overlay: 0.6,
    closeButton: ".modal_close"
});


/**
 * Given a url, gets a phone number from the phone input and sends the url to
 * that number.
 */
function sendText(url) {
    var phoneNumber = $('input[name=phone1]').val() + $('input[name=phone2]').val() + $('input[name=phone3]').val()

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
            window.open(url, "_blank");
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
    console.log(success);
    $('.one_half').prop('onclick',null).off('click');
    console.log($('.one_half'));
    $('.one_half').text('sent!');
}

$(function() {
 //       Calling Login Form
        $("#login_form").click(function() {
                $(".social_login").hide();
                    $(".user_login").show();
                        return false;
                            });

  //  Calling Register Form
        $("#register_form").click(function() {
                $(".social_login").hide();
                    $(".user_register").show();
                        $(".header_title").text('Register');
                            return false;
                                });

   // Going back to Social Forms
        $(".back_btn").click(function() {
                $(".user_login").hide();
                    $(".user_register").hide();
                        $(".social_login").show();
                            $(".header_title").text('Login');
                                return false;
                                    });
});

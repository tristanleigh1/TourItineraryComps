$(document).ready(function() {
    setVal($("#points").val(), "pointValBox");
    setDirectness($("#miles").val(), "distanceValBox");
    setQuantifier($("#museums").val(), "museumValBox");
    setQuantifier($("#landmarks").val(), "landmarkValBox");
    setQuantifier($("#activities").val(), "activityValBox");
    setQuantifier($("#parks").val(), "parkValBox");
});

function setVal(newVal, idName){
    $("#" + idName).html(newVal);
}

function setQuantifier(newVal, idName) {
    switch(newVal) {
        case "0":
            $("#" + idName).html("None");
            break;
        case "1":
            $("#" + idName).html("Few");
            break;
        case "2":
            $("#" + idName).html("Some");
            break;
        case "3":
            $("#" + idName).html("Many");
            break;
        case "4":
            $("#" + idName).html("Lots!");
            break;
    }
}

function setDirectness(newVal, idName) {
    switch(newVal) {
        case "0":
            $("#" + idName).html("In a Rush");
            break;
        case "3":
            $("#" + idName).html("More Direct");
            break;
        case "6":
            $("#" + idName).html("Default");
            break;
        case "9":
            $("#" + idName).html("Scenic Route");
            break;
        case "12":
            $("#" + idName).html("Only the Best!");
            break;
    }
}
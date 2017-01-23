$(document).ready(function() {
    setVal($("#points").val(), "pointValBox");
    setDirectness($("#miles").val(), "distanceValBox");
    setQuantifier($("#museums").val(), "museumValBox");
    setQuantifier($("#landmarks").val(), "landmarkValBox");
    setQuantifier($("#activities").val(), "activityValBox");
    setQuantifier($("#parks").val(), "parkValBox");
});

function setVal(newVal, idName){
    document.getElementById(idName).innerHTML=newVal;
}

function setQuantifier(newVal, idName) {
    switch(newVal) {
        case "0":
            document.getElementById(idName).innerHTML="None";
            break;
        case "1":
            document.getElementById(idName).innerHTML="Few";
            break;
        case "2":
            document.getElementById(idName).innerHTML="Some";
            break;
        case "3":
            document.getElementById(idName).innerHTML="Many";
            break;
        case "4":
            document.getElementById(idName).innerHTML="Lots!";
            break;
    }
}

function setDirectness(newVal, idName) {
    switch(newVal) {
        case "0":
            document.getElementById(idName).innerHTML="In a Rush";
            break;
        case "3":
            document.getElementById(idName).innerHTML="More Direct";
            break;
        case "6":
            document.getElementById(idName).innerHTML="Default";
            break;
        case "9":
            document.getElementById(idName).innerHTML="Scenic Route";
            break;
        case "12":
            document.getElementById(idName).innerHTML="Only the Best!";
            break;
    }
}
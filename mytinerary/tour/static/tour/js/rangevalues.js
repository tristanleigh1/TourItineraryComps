$(document).ready(function() {
    setVal($("#points").val(), "pointValBox");
    setVal($("#miles").val(), "mileValBox");
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
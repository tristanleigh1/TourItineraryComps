//$(document).ready(function() {
//    var quantifiers = ["None", "Few", "Some", "Many", "Lots!"];
//                    
//    $(".slider")
//        .slider({ 
//            min: 0, 
//            max: quantifiers.length-1, 
//            value: 3 
//        })
//        .slider("pips", {
//            rest: "label",
//            labels: quantifiers
//        })
//});



function startToEnd() {
  $("#start-to-end-fields").html(`
    <div class="form-group row">
      <label class="col-sm-3 control-label">End Location</label>
      <div class="col-sm-6">
                      <input  type="text"
                          style="width:100%"
                          class="form-control"
                          id="autocomplete2"
                          name="endDestination"
                          onFocus="geolocate()">
      </div>
    </div>
    <input type="hidden" id="endLngLat" name="endCoords">
    <input type="hidden" id="endAddress" name="endAddress">
    <div class="form-group row ">
      <label class="col-sm-3 control-label">Number of Stops</label>
      <div class="col-sm-6">
        <input type="range" class="form-control slide-input" id="points" name="points" min="0" max="8" step="1"
      oninput="setVal(this.value,'pointValBox')" onchange="setVal(this.value,'pointValBox')">
      </div>
      <div class="col-sm-2 range-val">
        <span id="pointValBox"></span>&nbsp; Stops
      </div>
    </div>
    <div class="form-group row ">
      <label class="col-sm-3 control-label">Directness</label>
      <div class="col-sm-6">
        <input type="range" class="form-control slide-input" id="miles" name="miles" min="0" max="12" step="3"
      oninput="setDirectness(this.value,'distanceValBox')" onchange="setDirectness(this.value,'distanceValBox')">
      </div>
      <div class="col-sm-2 range-val">
        <span id="distanceValBox"></span>&nbsp;
      </div>
    </div>
    <div class="form-group row">
      <label class="col-sm-3 control-label">Museums</label>
      <div class="col-sm-6">
        <input type="range" id="museums" name="museums" min="0" max="4" step="1"
    oninput="setQuantifier(this.value,'museumValBox')"
    onchange="setQuantifier(this.value,'museumValBox')" class="form-control slide-input">
      </div>
      <div class="col-sm-2 range-val">
        <span id="museumValBox"></span>&nbsp;
      </div>
    </div>
    <div class="form-group row">
      <label class="col-sm-3 control-label">Landmarks</label>
      <div class="col-sm-6">
        <input type="range" id="landmarks" name="landmarks" min="0" max="4" step="1"
    oninput="setQuantifier(this.value,'landmarkValBox')"
    onchange="setQuantifier(this.value,'landmarkValBox')" class="form-control slide-input">
      </div>
      <div class="col-sm-2 range-val">
        <span id="landmarkValBox"></span>&nbsp;
      </div>
    </div>
    <div class="form-group row">
      <label class="col-sm-3 control-label">Activities</label>
      <div class="col-sm-6">
        <input type="range" id="activities" name="activities" min="0" max="4" step="1"
    oninput="setQuantifier(this.value,'activityValBox')"
    onchange="setQuantifier(this.value,'activityValBox')" class="form-control slide-input">
      </div>
      <div class="col-sm-2 range-val">
        <span id="activityValBox"></span>&nbsp;
      </div>
    </div>
    <div class="form-group row">
      <label class="col-sm-3 control-label">Parks</label>
      <div class="col-sm-6">
        <div id="parks" class="slider"></div>
        <input type="hidden" id="parksInput" name="parks">
      </div>
      <div class="col-sm-2 range-val">
        <div id="parkValBox"></div>&nbsp;
      </div>
    </div>
    `);
//    setVal($("#points").val(), "pointValBox");
//    setDirectness($("#miles").val(), "distanceValBox");
//    setQuantifier($("#museums").val(), "museumValBox");
//    setQuantifier($("#landmarks").val(), "landmarkValBox");
//    setQuantifier($("#activities").val(), "activityValBox");
//    setQuantifier($("#parks").val(), "parkValBox");
    
    var quantifiers = ["None", "Few", "Some", "Many", "Lots!"];
    $(".slider")
        .slider({ 
            min: 0, 
            max: quantifiers.length-1, 
            value: 2,
            animate: 300,
            slide: function( event, ui ) {
//                $("#parks").val( ui.value );
                $("#parksInput").val(ui.value);
//                alert(ui.value);
            }
        })
        .slider("pips", {
            rest: "label",
            labels: quantifiers
        });
    initAutocomplete();
}

function exploratory() {
  $("#start-to-end-fields").empty();
}

//function setVal(newVal, idName){
//    $("#" + idName).html(newVal);
//}
//
//function setQuantifier(newVal, idName) {
//    switch(newVal) {
//        case "0":
//            $("#" + idName).html("None");
//            break;
//        case "1":
//            $("#" + idName).html("Few");
//            break;
//        case "2":
//            $("#" + idName).html("Some");
//            break;
//        case "3":
//            $("#" + idName).html("Many");
//            break;
//        case "4":
//            $("#" + idName).html("Lots!");
//            break;
//    }
//}
//
//function setDirectness(newVal, idName) {
//    switch(newVal) {
//        case "0":
//            $("#" + idName).html("In a Rush");
//            break;
//        case "3":
//            $("#" + idName).html("More Direct");
//            break;
//        case "6":
//            $("#" + idName).html("Default");
//            break;
//        case "9":
//            $("#" + idName).html("Scenic Route");
//            break;
//        case "12":
//            $("#" + idName).html("Only the Best!");
//            break;
//    }
//}

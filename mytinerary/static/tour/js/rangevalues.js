//$(document).ready(function() {
//    
//});

function createSlider(name) {
    var quantifiers = ["None", "Few", "Some", "Many", "Lots!"];
    $(name)
        .slider({ 
            min: 0, 
            max: quantifiers.length-1, 
            value: 2,
            animate: 500,
            slide: function( event, ui ) {
                $(name + "Input").val(ui.value);
            }
        })
        .slider("pips", {
            first: "pip",
            last: "pip",
        })
        .slider("float", {
            labels: quantifiers
        });
    
    $(name + "Input").val("2");
}

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
    </div>
    <div class="form-group row ">
      <label class="col-sm-3 control-label">Directness</label>
      <div class="col-sm-6">
        <input type="range" class="form-control slide-input" id="miles" name="miles" min="0" max="12" step="3"
      oninput="setDirectness(this.value,'distanceValBox')" onchange="setDirectness(this.value,'distanceValBox')">
      </div>
    </div>
    <div class="form-group row">
      <label class="col-sm-3 control-label">Museums</label>
      <div class="col-sm-6">
        <div id="museums" class="slider"></div>
        <input type="hidden" id="museumsInput" name="museums">
      </div>
    </div>
    <div class="form-group row">
      <label class="col-sm-3 control-label">Landmarks</label>
      <div class="col-sm-6">
        <div id="landmarks" class="slider"></div>
        <input type="hidden" id="landmarksInput" name="landmarks">
      </div>
    </div>
    <div class="form-group row">
      <label class="col-sm-3 control-label">Activities</label>
      <div class="col-sm-6">
        <div id="activities" class="slider"></div>
        <input type="hidden" id="activitiesInput" name="activities">
      </div>
    </div>
    <div class="form-group row">
      <label class="col-sm-3 control-label">Parks</label>
      <div class="col-sm-6">
        <div id="parks" class="slider"></div>
        <input type="hidden" id="parksInput" name="parks">
      </div>
    </div>
    `);
//    setVal($("#points").val(), "pointValBox");
//    setDirectness($("#miles").val(), "distanceValBox");
    
    
//    createSlider("#miles");
    createSlider("#museums");
    createSlider("#landmarks");
    createSlider("#activities");
    createSlider("#parks");
    
    initAutocomplete();
}

function exploratory() {
  $("#start-to-end-fields").empty();
}

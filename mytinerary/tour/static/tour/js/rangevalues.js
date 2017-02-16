//$(document).ready(function() {
//    
//});

function createSlider(name, quantifiers) {
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
        <div id="points" class="slider"></div>
        <input type="hidden" id="pointsInput" name="points">
      </div>
    </div>
    <div class="form-group row ">
      <label class="col-sm-3 control-label">Directness</label>
      <div class="col-sm-6">
        <div id="miles" class="slider"></div>
        <input type="hidden" id="milesInput" name="miles">
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
    
    var points_preference = ["0","1","2","3","4","5","6","7","8"];
    var directness_preference = ["In a Rush", "More Direct", "Default", "Scenic Route", "Only the Best!"];
    var category_preference = ["None", "Few", "Some", "Many", "Lots!"];
    createSlider("#points", points_preference);
    createSlider("#miles", directness_preference);
    createSlider("#museums", category_preference);
    createSlider("#landmarks", category_preference);
    createSlider("#activities", category_preference);
    createSlider("#parks", category_preference);
    
    initAutocomplete();
}

function exploratory() {
  $("#start-to-end-fields").empty();
}
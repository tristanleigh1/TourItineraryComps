//$(document).ready(function() {
//
//});

function createSlider(name, quantifiers, default_val) {
    $(name)
        .slider({
            min: 0,
            max: quantifiers.length-1,
            value: default_val,
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

    $(name + "Input").val(default_val);
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
      <label class="col-sm-3 control-label"><a href="#" data-toggle="tooltip" data-placement="top"
                                                title="How direct do you want your route to be? More direct will find a shorter route, but might miss some exciting stops!" style="text-decoration: none; color:inherit; cursor: default;">Directness</a></label>
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
    $("#miles")
        .slider({
            min: 0,
            max: 4,
            value: 2,
            animate: 500,
            slide: function( event, ui ) {
                $("#milesInput").val(ui.value * 2.5);
            }
        })
        .slider("pips", {
            first: "pip",
            last: "pip",
        })
        .slider("float", {
            labels: directness_preference
        });
    $("#milesInput").val(5);

    createSlider("#points", points_preference, 4);
    createSlider("#museums", category_preference, 2);
    createSlider("#landmarks", category_preference, 2);
    createSlider("#activities", category_preference, 2);
    createSlider("#parks", category_preference, 2);
    
    $('[data-toggle="tooltip"]').tooltip(); 
    
    initAutocomplete();
}

function exploratoryMode() {
  $("#start-to-end-fields").empty();
}

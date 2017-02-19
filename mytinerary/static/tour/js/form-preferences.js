/**
 * form-preferences.js
 *
 * Contains functions for the form inputs and changes form format depending
 * on what mode the user selects.
 *
 * @author Braun, Jones, Leigh, Tuchow
 * 2/19/17
 */


/**
 * Initializes the slider with given preferences.
 */
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


/**
 * Removes extra form HTML when exploratory mode is selected.
 */
function exploratoryMode() {
  $("#start-to-end-fields").empty();
}


/**
 * Fills in the HTML for when start-to-end mode is selected.
 */
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
    </div>` + addSliderHTML("museums") + addSliderHTML("landmarks") + addSliderHTML("activities") + addSliderHTML("parks")
    );

    var points_preference = ["0","1","2","3","4","5","6","7","8"];
    var directness_preference = ["In a Rush", "More Direct", "Default", "Scenic Route", "Only the Best!"];
    var category_preference = ["None", "Few", "Some", "Many", "Lots!"];

    createSlider("#miles", directness_preference, 2);
    createSlider("#points", points_preference, 4);
    createSlider("#museums", category_preference, 2);
    createSlider("#landmarks", category_preference, 2);
    createSlider("#activities", category_preference, 2);
    createSlider("#parks", category_preference, 2);
    
    $('[data-toggle="tooltip"]').tooltip(); 
    
    initAutocomplete();
}

/**
 * Adds html for the slider given the name of the preference category
 */
function addSliderHTML(name) {
    return `<div class="form-group row">
      <label class="col-sm-3 control-label">` + name.charAt(0).toUpperCase() + name.slice(1) + `</label>
      <div class="col-sm-6">
        <div id="` + name + `" class="slider"></div>
        <input type="hidden" id="` + name + `Input" name="` + name + `">
      </div>
    </div>`;
}

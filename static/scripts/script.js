jQuery(document).ready(function($) {
  $.noConflict();

  if ($("h1").text() === "Add photos to the album") {
    console.log("on the add photo to album page");
  }

  // $("#update-tag-button").prop("disabled", true);

  var forbidden = [];
  $("#tag-update").blur(function() {
    var inputValues = $(this).val();
    var splitValues = inputValues.split();
  });
});

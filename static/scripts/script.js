jQuery(document).ready(function($) {
  $.noConflict();

  if ($("h1").text() === "Add photos to the album") {
    console.log("on the add photo to album page");
  }

  // $("#update-tag-button").prop("disabled", true);

  // var forbidden = ["'", "#", "%", "?"];
  // $("#tag-update").blur(function() {
  //   var inputValues = $(this).val();
  //   // console.log(inputValues.split());
  //   for (var i = 0; i < forbidden.length; i++) {
  //     if (inputValues.includes(forbidden[i])) {
  //       console.log("arrhiuhsihfdihsdih");
  //     } else {
  //       $("#update-tag-button").prop("disabled", false);
  //     }
  //   }

  // var splitValues = inputValues.split();
  // });
});

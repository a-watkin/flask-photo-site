jQuery(document).ready(function($) {
  $.noConflict();

  // console.log("anything?");

  if ($("h1").text() === "Add photos to the album") {
    console.log("on the add photo to album page");
  }

  $("#tag-update").keyup(function(e) {
    var arr = e.target.value.split(",");
    var result = true;
    arr.forEach(char => {
      console.log(char);
      if (char.replace(/ /g, "").length < 1) {
        result = false;
      }
    });

    if (arr.indexOf("\\") > -1 || arr.indexOf("/") > -1) {
      console.log("DANGER");
      $("#update-tag-button").prop("disabled", true);
      $("#warning-text").text("The characters: \\ and / are not allowed.");
    } else if (arr.join("").replace(/ /g, "").length < 1) {
      $("#update-tag-button").prop("disabled", true);
      $("#warning-text").text(
        "Please enter a new tag. An empty space is not a valid tag."
      );
    } else if (arr.join("").replace(/,/g, "") < 1) {
      $("#update-tag-button").prop("disabled", true);
      $("#warning-text").text(
        "Please enter a new tag. An empty space is not a valid tag."
      );
    } else if (result === false) {
      console.log("problem coming from result");
      $("#update-tag-button").prop("disabled", true);
      $("#warning-text").text(
        "Please enter a new tag. An empty space is not a valid tag."
      );
    } else {
      $("#update-tag-button").prop("disabled", false);
    }
  });
});

jQuery(document).ready(function($) {
  $.noConflict();

  // Start the upload button as disabled
  $("#upload-button").prop("disabled", true);

  // Allows for checking the number of files
  $(":file").filestyle({
    onChange: function(files) {
      console.log(files);

      if (files.length > 0) {
        $("#upload-button").prop("disabled", false);
      }
    }
  });

  // Removes selected photos from the upload input
  $("#clear-input").on("click", function() {
    $(":file").filestyle("clear");
    $("#upload-button").prop("disabled", true);
  });

  // Change button size on the file input field
  $(":file").filestyle("size", "lg");
  // Puts the select photos button on the left
  $(":file").filestyle("buttonBefore", true);

  // User feedback to say that files are uploading
  $("#upload-button").click(function() {
    $("#upload-message").removeAttr("hidden");
  });

  //
  // Check for improper user input for tags.
  //
  var forbidden = ["\\", "/", "%", "."];
  var safe = true;

  $("#tag-update").keyup(function(e) {
    safe = true;
    var arr = e.target.value.split(",");

    // for each value in arr check each char against the forbidden values
    for (var i = 0; i < arr.length; i++) {
      // console.log(arr[i]);
      forbidden.forEach(char => {
        if (arr[i].includes(char)) {
          safe = false;
        }
      });

      if (arr[i].replace(/ /g, "").length < 1) {
        safe = false;
      }
    }

    if (arr.join("").replace(/,/g, "") < 1) {
      safe = false;
    }
    // console.log(arr);

    if (!safe) {
      $("#update-tag-button").prop("disabled", true);
      $("#warning-text").text(
        "Please enter a valid tag name. The characters: \\, ., /, % are not allowed."
      );
    } else {
      $("#update-tag-button").prop("disabled", false);
      $("#warning-text").text(
        "You can enter multiple tags, separating them by commas."
      );
    }
  });

  // Redirects to photos page when a user logs out
  $("#flash-message").text(function(e, value) {
    // console.log("logged out", e, value.trim());
    if (value.trim() === "You have been logged out.") {
      // console.log("Refresh page here!")
      window.location.replace("/photo");
    }
  });
});

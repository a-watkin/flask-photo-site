jQuery(document).ready(function ($) {
  $.noConflict();

  // if(!$('#flash-message').text('No file selected')) {

  //   $("#upload-button").click(function () {
  //     // console.log('clicked upload')
  //     $('#upload-message').removeAttr('hidden');
  //   })



  // }

  // $(":file").filestyle({
  //   text: "Select photos"
  // });
  
  
  // $('#upload-info').click(function() {
    //   console.log($(":file").filestyle('input'));
    // })
    
  // Start the upload button as disabled
  $('#upload-button').prop('disabled', true);
  
  // Allows for checking the number of files
  $(":file").filestyle({
    'onChange': function (files) {
      console.log(files)
      
      if(files.length > 0) {
        $('#upload-button').prop('disabled', false);
      }
    }
  });
  
  // Removes selected photos from the upload input
  $('#clear-input').on('click', function () {
    $(":file").filestyle('clear');
    $('#upload-button').prop('disabled', true);
  })
  
  // Change button size on the file input field
  $(":file").filestyle('size', 'lg');
  // Puts the select photos button on the left
  $(":file").filestyle('buttonBefore', true);

  
  // User feedback to say that files are uploading
  $("#upload-button").click(function () {
    $('#upload-message').removeAttr('hidden');
  })

  if (
    $("#flash-message").text(function (e, value) {
      // console.log("logged out", e, value.trim());
      if (value.trim() === "You have been logged out.") {
        // console.log("Refresh page here!")
        window.location.replace("/")
      }
    })
  )

  function showWarnings() {
    $("#update-tag-button").prop("disabled", true);
    $("#warning-text").text(
      "Please enter a valid tag name. The characters: \\, /, % space."
    );
  }

  // if ($("h1").text() === "Add photos to the album") {
  //   console.log("on the add photo to album page");
  // }

  // var showWarningText = false;
  var forbidden = ["\\", "/", "%"];
  var safe = true;

  // if (showWarningText) {
  //   $("#warning-text").text("The characters: \\, / and % are not allowed.");
  // }

  $("#tag-update").keyup(function (e) {
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
        "Please enter a valid tag name. The characters: \\, /, % space."
      );
    } else {
      $("#update-tag-button").prop("disabled", false);
      $("#warning-text").text("You can enter multiple tags, seperating them by commas.");
    }
  });
});

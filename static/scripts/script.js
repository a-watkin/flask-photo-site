jQuery(document).ready(function($) {
  $.noConflict();

  $("#next").click(function() {
    console.log("clicked next");
  });

  $("#previous").click(function() {
    console.log("clicked previous");
  });
});

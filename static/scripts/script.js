jQuery(document).ready(function($) {
  $.noConflict();

  $("#next").click(function() {
    console.log("clicked next");
  });

  $("#previous").click(function() {
    console.log("clicked previous");
  });

  $("img").each(function(index, element) {
    var image = new Image();
    image.src = $(this).attr("src");

    image.onload = function() {
      console.log("height: " + this.height, "width: " + this.width);

      if (this.height > this.width) {
        console.log("portrait");
        $(element).addClass("foo");
      } else {
        console.log("landscape");
      }
    };
  });
});

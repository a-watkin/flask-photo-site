jQuery(document).ready(function($) {
  $.noConflict();

  // $("#next").click(function() {
  //   console.log("clicked next");
  // });

  // $("#previous").click(function() {
  //   console.log("clicked previous");
  // });

  // $("img").each(function(index, element) {
  //   var image = new Image();
  //   image.src = $(this).attr("src");

  //   image.onload = function() {
  //     console.log("height: " + this.height, "width: " + this.width);

  //     if (this.height > this.width) {
  //       console.log("portrait");
  //       $(element).addClass("foo");
  //     } else {
  //       console.log("landscape");
  //     }
  //   };
  // });

  if ($("h1").text() === "Add photos to the album") {
    console.log("on the add photo to album page");
  }

  // select all #remote-tag elements

  console.log("script working?");

  var remote_tags = [];

  $(".remove-tags").click(function() {
    var tagName = $(this)
      .text()
      .trim();
    console.log(tagName);

    if (this.style.color !== "blue") {
      this.style.color = "red";
    } else {
      this.style.color = "";
    }
  });

  // console.log($("h1").text());
});

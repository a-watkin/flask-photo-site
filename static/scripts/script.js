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

  // console.log("script working?");

  // var remove_tags = [];

  // $(".remove-tags").click(function() {
  //   console.log("before", remove_tags);
  //   var tagName = $(this)
  //     .text()
  //     .trim();
  //   console.log(tagName);

  //   console.log(this.style.color);
  //   if (this.style.color !== "red") {
  //     this.style.color = "red";
  //     remove_tags.push(tagName);
  //   } else {
  //     this.style.color = "";

  //     remove_tags.splice(remove_tags.indexOf(tagName), 1);
  //   }
  //   console.log("after", remove_tags);
  // });

  // // console.log($("h1").text());
  // var currentUrl = window.location.href;
  // var photoId = currentUrl.split("=")[1];
});

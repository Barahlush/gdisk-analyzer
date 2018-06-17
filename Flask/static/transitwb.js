$(document).ready(function() {
    $("body").css("display", "none");

    $( "#body" ).animate({
      backgroundColor: "rgb( 255, 255, 255 )"
    }, 1000);

	$("a.transition").click(function(event){
		event.preventDefault();
		linkLocation = this.href;

    $( "#body" ).animate({
      backgroundColor: #333
    }, 1000, redirectPage);
	});

	function redirectPage() {
		window.location = linkLocation;
	}
});


$(document).ready(function(){
	
	$( "#logo" ).click(function() {
  		$('html,body').animate({
        scrollTop: $("body").offset().top - 90},
        'slow');
	});
	
	$( "#home-button" ).click(function() {
  		$('html,body').animate({
        scrollTop: $("body").offset().top - 90},
        'slow');
	});

	$( "#about-button" ).click(function() {
  		$('html,body').animate({
        scrollTop: $(".about-me").offset().top - 100},
        'slow');
	});

	$( "#projects-button" ).click(function() {
  		$('html,body').animate({
        scrollTop: $(".projects").offset().top - 90},
        'slow');
	});

	$( "#contact-button" ).click(function() {
  		$('html,body').animate({
        scrollTop: $(".contact-me").offset().top - 90},
        'slow');
	});


});
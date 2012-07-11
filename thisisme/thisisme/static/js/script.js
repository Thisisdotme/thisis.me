/* Author: 
	Elchibek Konurbaev
*/
/* global variables */
var cur_image = 0;
var num_of_imgs = 1;
var distance_icons = 80;
var step;
var objects;
var randomized = false;
var random;
var offset_for_transition = 90;
var offset_for_end = 520;
var offset_from_top = -640; 
//main
$(document).ready(function(){
	Cufon('.subpage_topnav li,.submenu a ', { hover: true, textShadow: '1px 0 #989797'});
	Cufon('.home_content h1, .cLeftNavBlock .cMainFooter, .innerContent article');
	$('#cNavigation li').hover(function(){
		$(this).find('nav').show();
	}, function(){
		$(this).find('nav').hide();	
	});
	//animate icons on homepage only
	if($('section').is('.home_content')){
		animateIcons();
	}
});
//main function to animate icons
function animateIcons(){
	var num_of_icons = $('.icons img').length;
	num_of_imgs = $('.window').length-1;
	objects = new Array(num_of_icons);
	for(var i = 0; i < num_of_icons; ++i){
		objects[i] = new Array(4);
		objects[i]["order"] = -1;
	}
	//randomize horizontally: even icons
	$('.icons img:even').each(function(){
		random = Math.floor(num_of_icons*Math.random())*num_of_icons+20;
		$(this).css({left: random});
	});
	//randomize horizontally: odd icons
	$('.icons img:odd').each(function(){
		random = Math.floor(num_of_icons*Math.random())*num_of_icons + 100;
		$(this).css({left: random});
	}); 
	//randomize vertically
	$('.icons img').each(function(index){
		random = randomize(num_of_icons);
		objects[index]["order"] =random;
		objects[index]["default"] =random+offset_from_top;
		objects[index]["object"] = $(this);
		$(this).css({ top: (random+offset_from_top)});
	});	
	objects.sort(sortNumber);
	//start animating according to the sorted position
	for(var j = 0; j < num_of_icons; ++j){
		objects[j]["current"] = objects[j]["default"];
		animateObject(objects[j]["object"], j);
	} 
}
function sortNumber(m, n){
	var m = m["order"];
	var n = n["order"];
	if (m > n) return -1;
	if (m < n) return 1;
	return 0;
}
function randomize(num_of_icons){
	random = Math.floor(num_of_icons*Math.random())*distance_icons;
	for(var i = 0; i < num_of_icons; ++i){
		if(objects[i]["order"]  == random){
			randomized = false;
			randomize(num_of_icons);
		}	
		else{
			randomized = true;
		}
	}
	if(randomized){
		return random;
	}
}
//animates each icon object
function animateObject($object, index){
	objects[index]["current"] = $object.offset().top;
	step = objects[index]["current"];
	//$('.offset:eq('+index+')').html(objects[index]["current"]);
	if(objects[index]["current"] > offset_for_end){
		var new_offset = (objects[index]["default"]+(distance_icons * index))-distance_icons;
		$object.offset({top: new_offset});
		step = new_offset;
	} 
	if(objects[index]["current"] == offset_for_transition){
		$('.window:eq('+cur_image+')').fadeOut('slow');
		++cur_image;
		$('.window:eq('+cur_image+')').fadeIn('slow');
		if(cur_image > num_of_imgs){
			cur_image = 0;
			$('.window:eq('+cur_image+')').fadeIn('slow');
		}
	} 
	$object.animate({
		top: ++step
	}, 1, 'linear', function(){
		animateObject($object, index)
	});
}
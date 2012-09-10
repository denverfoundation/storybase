(function($) {
	$(document).ready(function() {

		$(document).on('focusin', '.field, textarea', function() {
			if(this.title==this.value) {
				this.value = '';
			}
		}).on('focusout', '.field, textarea', function(){
			if(this.value=='') {
				this.value = this.title;
			}
		});

		intro_resize();

		// Intro image hover
		$('.images a').hover(function() {
			$(this).find('span.overlay').stop(true,true).fadeOut();
			$(this).find('span.title').stop(true,true).delay(200).slideDown();

		}, function() {
			$(this).find('span.overlay').stop(true,true).fadeIn();
			$(this).find('span.title').stop(true,true).slideUp();
		})
		
		if ($('.flexslider').length) {
			$('.title .flexslider').flexslider({
				animation: 'slide',
				slideshow: false,
				start: function(slider){
					$('.right-nav').click(function  () {
						slider.flexAnimate(slider.getTarget("next"), true)
					});
					$('.left-nav').click(function  () {
						slider.flexAnimate(slider.getTarget("prev"), true)
					});
				}
			});

			$('.bottom .flexslider').flexslider({
				animation: 'slide',
				slideshow: false,
				start: function(slider){
					$('.bottom .left ul li:eq(0) a ').click(function() {

						slider.flexAnimate(0)
						$('.bottom .left ul li a ').removeClass('active');
						$(this).addClass('active');
						return false;
					})
					$('.bottom .left ul li:eq(1) a ').click(function() {

						slider.flexAnimate(1)
						$('.bottom .left ul li a ').removeClass('active');
						$(this).addClass('active');
						return false;
					})
					$('.bottom .left ul li:eq(2) a ').click(function() {

						slider.flexAnimate(2)
						$('.bottom .left ul li a ').removeClass('active');
						$(this).addClass('active');
						return false;
					})
					$('.bottom .left ul li:eq(3) a ').click(function() {
						slider.flexAnimate(3)
						$('.bottom .left ul li a ').removeClass('active');
						$(this).addClass('active');
						return false;
					})

				}
			});


			$('.flexslider').each(function() {
				var jqThis = $(this);
				jqThis.flexslider({
					animation: 'slide',
					slideshow: false,
					start: function() {
						jqThis.find('.slide-shim').cycle({
							fx:     'scrollLeft',
							speed:  1500,
							timeout: 0,
							prev:   '.back',
							next:   '.forward'
						});
					}
				});
			});
			mySlider();
		}


		//Drop down
		$('.dd').hide();
		$('#navigation ul li').hover(function(){ 
			$(this).find('.dd:eq(0)').show();
			$(this).find('a:eq(0)').addClass('hover');
			$(this).find('a em').show();
		 },
		 function(){  
			$(this).find('.dd').hide();
			$(this).find('a:eq(0)').removeClass('hover');
			$(this).find('a em').hide();
	 	});


	 	$('.filters li a').click(function() {
	 		$(this).next().slideToggle();
	 		$(this).toggleClass('active');
	 		return false;
	 	});

	 	$('.filters li ul li a').click(function() {
	 		this_text = $(this).text();
	 		$(this).parents('ul:eq(0)').prev().text(this_text)
	 		$('.filters li ul').slideUp();
			$('.filters li a').removeClass('active')
			return false;
	 	});

	 	$(document).click(function(e) {
			if ($(e.target).parents('.filters').length == 0) {
			    $('.filters li ul').slideUp();
			    $('.filters li a').removeClass('active')
			}
		});

		$('.reset').click(function() {

			$('.filters ul li a.first').each(function() {
				var this_rel = $(this).attr('rel');
				$(this).text(this_rel)
			});
		});

		$('.list-view .box ').append('<div class="cl"/>')
		
		// nb: using classes atm; best not to have mutliple on a page
		$('.post-content .slides').cycle({
			before: function(currSlideElement, nextSlideElement, options, forwardFlag) {
				// in safari, at any rate, we have to jiggle the width or it doesn't render properly. :(
				var w = $(this).width();
				$(this).width(w + 1).width(w - 1);
			},
			after: function(currSlideElement, nextSlideElement, options, forwardFlag) {
				$('.post-content .slides').data('active-index', $(this).index());
				$('.post-nav a').removeClass('active').eq($(this).index()).addClass('active');
			},
			autostop: true,
			autostopCount: 1,
			fx: 'scrollLeft',
			speed: 500
		});
		$('.post-nav a').click(function() {
			var myIndex = $(this).parent().index();
			var transition = 'scrollRight';
			if ($('.post-content .slides').data('active-index') < $(this).parent().index()) {
				transition = 'scrollLeft';
			}
			$('.post-content .slides').cycle($(this).parent().index(), transition);
			return false;
		});
	});


	$(window).resize(function() {
		intro_resize();
		mySlider();
	});


	function intro_resize(){

		var window_width = $(window).width();
		var images_num = ($('#banner .images a').size())/2;

		var image_width = window_width / images_num
		$('.images a, .images a img').css({
			width : image_width
		})


	}

	$(window).load(function() {
		$('.images').fadeIn();
	});

	function mySlider() {

		var window_width = $(window).width();

		$('.rotator-slides .slide').css({
			width : window_width
		})

		var sum=0;

		$('.rotator-slides .slide').each( function() {
		 	sum += $(this).width(); 
		});
		$('.rotator-slides').width(sum);

		$('.rotator-slides').wrap('<div class="slider-holder"></div>');

		$('.rotator-slides').css({
		        	left : -window_width
		});

		$('#rotator-nav-1 li a').live('click', function() {
		    if ($(this).hasClass('active')) {
		    } else {
		        var sliderIndex = $('#rotator-nav-1 li a').index(this) ;

		        $('#rotator-nav-1 li a').removeClass('active');
		        $(this).addClass('active');
		        var slidePosition = $('.rotator-slides .slide:eq('+sliderIndex+')').position().left;
		        var slideHeight = $('.rotator-slides .slide:eq('+sliderIndex+')').height();
		        $('.rotator-slides').animate({
		        	left : -slidePosition,
		        	height: slideHeight
		        });
		    };
		    return false;
		});


		$('.page-nav a').click(function() {
			var this_num = $(this).attr('rel');
			var num = this_num - 1   

			$('#rotator-nav-1 li:eq('+num+') a').trigger('click');
	        return false;
		});




	}

})(jqLatest);


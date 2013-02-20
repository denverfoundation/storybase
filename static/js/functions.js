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

			$('.supporting-foundations .flexslider').flexslider({
				animation: 'slide',
				slideshow: false,
				start: function(slider) {
					var anchors = $('.supporting-foundations ul.foundations li a');
					for (var i = 0; i < anchors.length; i++) {
						anchors.eq(i).click((function(capturedIndex) {
							return function() {
								slider.flexAnimate(capturedIndex);
								anchors.removeClass('active');
								$(this).addClass('active');
								return false;
							};
						})(i));
					}
				}
			});

			$('.homepage-header .flexslider').flexslider({
				animation: 'slide',
				slideshow: true,
				pauseOnHover: true
			});
		}

		//Drop down
		$('.dd').hide();
		$('.megamenu ul li').hover(function(){ 
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
		

		$('.post-nav a').click(function() {
			var myIndex = $(this).parent().index();
			var transition = 'scrollRight';
			if ($('.post-content .slides').data('active-index') < $(this).parent().index()) {
				transition = 'scrollLeft';
			}
			$('.post-content .slides').cycle($(this).parent().index(), transition);
			return false;
		});
		
		$('.storybase-share-widget').storybaseShare();

		// Analytics events 
		if (window._gaq) {
			$('.homepage .latest .connected-link').click(function() {
				_gaq.push(['_trackEvent', 'Links', 'Latest stories connected']);
			});
			$('.button.view-all-stories').click(function() {
			    _gaq.push(['_trackEvent', 'Links', 'View All Stories']);
			});
		}
	});


	$(window).resize(function() {
		intro_resize();
	});


	/**
	 * Resize the banner images based on the window width
	 */
	function intro_resize() {
		// Aspect ratio is based on the default icon size, 335x200px or
		// 5:3.
		var aspect_ratio = 3 / 5;
		var window_width = $(window).width();
		var images_num = ($('#banner .images a').size())/2;

		var image_width = window_width / images_num;
		var image_height = image_width * aspect_ratio;
		var container_height = image_height * 2;
		$('.images').css({
			height: container_height
		});
		$('.images a img').css({
			width : image_width
		});
		// The <A> elements are used to "crop" tall images, so we need to set
		// their heights as well
		$('.images a').css({
			width : image_width,
			height: image_height
		});
	}

	// Wait until all the images are loaded before revealing the banner
	$(window).load(function() {
		$('.images a').fadeIn();
	});

	// sidebar
	$('.sidebar .sibling-nav li a').hover(function() {
		$(this).parent('li').addClass('hover');
	}, function() {
		$(this).parent('li').removeClass('hover');
	});


	// misc functions

	// @todo: this whole file needs to be cleaned up/refactored,
	// but might be nice to have global methods like this in a nice
	// namespace.
	// adapted from http://stackoverflow.com/questions/3656592/programmatically-disable-scrolling
	// @note: while scrolling is disabled, the page may jump to (0, 0) in some
	// browsers. for the use cases we currently have, this is ok.
	window.disablePageScrolling = function() {
		var $target = $('body');
		var scrollPosition = [
			window.pageXOffset || document.documentElement.scrollLeft || document.body.scrollLeft,
			window.pageYOffset || document.documentElement.scrollTop  || document.body.scrollTop
		];
		$target.data('scroll-position', scrollPosition);
		$target.data('previous-overflow', $target.css('overflow'));
		$target.css({ overflow: 'hidden' });
		window.scrollTo(scrollPosition[0], scrollPosition[1]);	// does not appear to be effective
	}
	window.enablePageScrolling = function() {
		var $target = $('body');
		var scrollPosition = $target.data('scroll-position');
		$target.css('overflow', $target.data('previous-overflow'));
		window.scrollTo(scrollPosition[0], scrollPosition[1]);
	}

})(jqLatest);


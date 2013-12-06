(function ($) {
	// user information
	var user = {
		isLogged: false,
		info: null,
		setLoggedIn: function(info) {
			this.isLogged = true;
			this.info = info;
		},
		setLoggedOut: function() {
			this.isLogged = false;
			this.info = null;
		}
	};
	
	var convertToSlug = function(text, render) {
		return render(text)
		.toLowerCase()
		.replace(/[^\w ]+/g, '')
		.replace(/ +/g, '-');
	}
	
	var convertToDateStr = function(text, render) {
		var timestamp = parseInt(render(text))*1000;
		return new Date(timestamp).toLocaleDateString();
	}
	
	var percentCompleted = function(text, render) {
		var threshold = 101;
		return ((Math.min(parseInt(render(text)), threshold) / threshold) * 100);
	}
	
	var show = function(element, template, data) {
		$(element).mustache(template, (data === undefined ? null : data), { method: 'html' });
	}
	
	/* modal event handlers start */
	$(document).on('click', '#kirjaudu', function() {
		jQuery.facebox({ ajax: 'kirjaudu.html' });
		return false;
	});

	$(document).on('click', '#rekisteroidy', function() {
		jQuery.facebox({ ajax: 'rekisteroidy.html' });
		return false;
	});

	$(document).on('click', '#loginregister', function() {
		jQuery.facebox({ ajax: 'rekisteroidy.html' });
		return false;
	});

	$(document).on('click', '#registerlogin', function() {
		jQuery.facebox({ ajax: 'kirjaudu.html' });
		return false;
	});

	$(document).on('click', '#ota-yhteytta', function() {
		jQuery.facebox({ ajax: 'otayhteytta.html' });
		return false;
	});	
	/* modal event handlers end */

	/* login event handlers */
	$(document).on('submit', 'form.kirjautuminen', function(e) {
		e.preventDefault();
		
		$.ajax({
			url: 'kayttaja/login',
			global: false,
			data: {
				email: $('form.kirjautuminen input[name=email]').val(),
				password: $('form.kirjautuminen input[name=password]').val()
			},
			type: 'POST',
			statusCode: {
				200: function(data) {
					user.setLoggedIn(data);
					show('header', 'headerbox', user);
					jQuery(document).trigger('close.facebox');
					routie.reload();
				},
				401: function() {
					// todo: tell user about invalid input
				}
			}
		});
	});
	
	$(document).on('click', 'a.ulos', function() {
		$.ajax({
			url: 'kayttaja/logout',
			type: 'POST',
			success: function() {
				user.setLoggedOut();
				show('header', 'headerbox', user);
				routie.reload();
			}
		});
		
		return false;
	});
	/* login event handlers end */
	
	// load templates
	$.Mustache.load('templates.html')
		.done(function() {
			// catch all ajax errors and show error page
			$(document).ajaxError(function(event, request, settings) {
				switch (request.status) {
				case 401:
					show('section', 'error-login');
					break;
				case 403:
					show('section', 'error-unauthorized');
					break;
				case 404:
					show('section', 'error-notfound');
					break;
				default:
					show('section', 'error-generic');
					break;
				}
			});
			
			// load and display login status
			$.getJSON('kayttaja', function(data) {
				if (data.name !== undefined) {
					user.setLoggedIn(data);
				} else {
					user.setLoggedOut();
				}
				
				show('header', 'headerbox', user);
				
				// setup routing
				routie({
					'': function() {
						// default to the front page
						show('section', 'etusivu');
					},
					'/etusivu': function() {
						show('section', 'etusivu');
					},
					'/rajoitteet': function() {
						$.getJSON('rajoite', function(data) {
							data.slug = function() { return convertToSlug; };
							data.date = function() { return convertToDateStr; };
							data.percentCompleted = function() { return percentCompleted; };
							show('section', 'rajoitteet', data);
						});
					},
					'/rajoite/:id/*': function(id) {
						$.getJSON('rajoite/' + id, function(data) {
							data.date = function() { return convertToDateStr; };
							show('section', 'rajoite', data);
						});
					},
					'/rajoita': function() {
						if (user.isLogged) {
							show('section', 'teerajoite');
						} else {
							show('section', 'error-login');
						}
					},
					'/ohjeet': function() {
						show('section', 'ohjeet');
					},
					'/tiedotteet': function() {
						$.getJSON('tiedote', function(data) {
							data.hasNews = (data.news.length > 0);
							data.date = function() { return convertToDateStr; };
							show('section', 'tiedotteet', data);
						});
					},
					'/pasvenska': function() {
						show('section', 'pasvenska');
					},
					'/inenglish': function() {
						show('section', 'inenglish');
					},
					'/ota-yhteytta': function() {
						show('section', 'ota-yhteytta');
					},
					'/rekisteriseloste': function() {
						show('section', 'rekisteriseloste');
					},
					'/henkilosuoja': function() {
						show('section', 'henkilosuoja');
					},
					'*': function() {
						// show 404 page for other urls
						show('section', 'error-notfound');
					}
				});
			});
		});
})(jQuery);

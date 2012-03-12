//
//	TIM.errorHandler - global handler for exceptions
//
TIM.errorHandler = function () {
	
	return {
		handle: function (e) {
			alert("Please excuse us!  thisis.me encountered an unexpected error.  We're very sorry for the inconvenience.\n\n" + 
							(e.name || 'Unknown name') + " - " + 
							(e.message || 'Unknown message') + 
							(e.getSourceLine === 'function' ? " - lineNo: " + e.getSourceLine() : ''));
		}
	};

}();

//
// Genenral utility functions
//
TIM.utils = function () {
	
	return {
		
		linkify: function (text) {

			// http://, https://, ftp://
			var urlPattern = /\b(?:https?|ftp):\/\/[a-z0-9-+&@#\/%?=~_|!:,.;]*[a-z0-9-+&@#\/%=~_|]/gim;
			
			// www. sans http:// or https://
			var pseudoUrlPattern = /(^|[^\/])(www\.[\S]+(\b|$))/gim;
			
			// Email addresses
			var emailAddressPattern = /(([a-zA-Z0-9_\-\.]+)@[a-zA-Z_]+?(?:\.[a-zA-Z]{2,6}))+/gim;
			
			var replacedText = text.replace(urlPattern, '<a target="_blank" href="$&">$&</a>');
			replacedText = replacedText.replace(pseudoUrlPattern, '$1<a target="_blank" href="http://$2">$2</a>');
			replacedText = replacedText.replace(emailAddressPattern, '<a target="_blank" href="mailto:$1">$1</a>');
			
			return replacedText;
		}
	};

}();

//
//	TIM.eventRenderer and associated components.  Defines the featureEvent renderer
//	infrastructure
//
TIM.eventRenderer = {};

TIM.eventRenderer.baseRenderer = function (spec) {
	var that = {};
	
	that.displaysAuthorInfo = true;


	that.getAuthorName = function () {
		return spec.event.author.name || '';
	};
	
	that.getAuthorFullName = function () {		
		if (!spec.event.author.full_name) {
			return spec.event.author.name;
		}
		return spec.event.author.full_name || '';
	};
	
	that.getAuthorProfilePicture = function() {
		return spec.event.author.profile_image_url || '';
	}

	that.getEventId = function () {
		return spec.event.event_id;
	};

	that.getFeatureName = function () {
		return spec.event.feature;
	};
	
	that.getSources = function () {
		return spec.event.sources.items || '';
	};

	that.getCreateTime = function () {
		return spec.event.create_time;
	};
	
	that.getCreateTimeMillis = function () {
		return Number(spec.event.create_time) * 1000;
	};
	
	that.getFuzzyCreateTime = function () {
		return $.timeago(new Date(this.getCreateTimeMillis()));
	}

	that.getDetailURL = function () {
		return spec.event.link;
	};

	that.getCaption = function () {
		return spec.event.content.label || '';
	};
	
	that.getData = function () {
		return spec.event.content.data || '';
	};
		
	that.hasImage = function () {
		return (spec.event.content.photo_url !== undefined
				&& spec.event.content.photo_url.length > 0);
	}
	
	that.getImage = function () {
		return spec.event.content.photo_url || '';
	}
	
	that.getAuxillaryData = function () {
		return spec.event.content.auxillary_data || '';
	};
	
	that.getContentURL = function () {
		return spec.event.content.url || '';
	};
	
	that.getEventDisplaySize = function () {
		return (that.hasImage() ? 'full-page' : 'half-page');
	}

	that.renderBegin = function (obj) {
		return '<div class="event ' + obj.style + '">';
	};
	
	that.renderContent = function () {
		var markup = '<div class="content">';
		
		// Add Image Content
		if (that.hasImage()) {
			markup += '<div class="inner-image"><img src="' + that.getImage() + '" alt=""/></div>';
		}
		
		// Add Data Content
		var data = that.getData();
		if (data.length > 0) {
				markup += '<div class="inner-text"><p>' + TIM.utils.linkify(data) + '</p></div>';
		}
		
		markup += '</div>';
		return markup;
	};
	
	that.renderEnd = function () {
		return '</div>';
	};
	
	 that.renderAuthorProfilePicture = function () {
	 	 return '<div class="avatar">' +
	 	 			'<div class="frame">' +
						'<a href="/' + that.getAuthorName() + '/timeline"><img src="' + that.getAuthorProfilePicture() + '" /></a>' +
					'</div>' +
				'</div>';
	 }
	that.renderFooter = function () {
		return '<div class="footer">' + that.renderAuthorProfilePicture() + that.renderInfo() +  that.renderBaseline() + '</div>';
	}
	
	that.renderInfo = function () {
		return '<div class="info">' + that.renderAuthor() + that.renderCaption() + '</div>';
	}
	
	that.renderAuthor = function() {
		return '<div class="author"><a href="/' + that.getAuthorName() + '/timeline">' + that.getAuthorFullName() + '</a></div>';
	}
	
	that.renderCaption = function() {
		var caption = that.getCaption();
		if (caption.length > 0) {
			return '<div class="caption">' + caption + '</div>';
		}
		return '';
	}
	
	that.renderBaseline = function () {
		var featureIcons = '';
		var sources = that.getSources();
		if (sources.length > 0) {
			for (var i = 0; i < sources.length; i++) {
				featureIcons += '<img src="' + TIM.ImageController.getLResColor(sources[i].feature_name) + '" />';
			}
		}
		else {
			featureIcons = '<img src="' + TIM.ImageController.getLResColor(that.getFeatureName()) + '" />';
		}	
						
							
		var timeago = 		'<div class="fuzzy-time">' + that.getFuzzyCreateTime() + '</div>';
		return '<div class="baseline">' + featureIcons + timeago + '</div>';
	}

	that.renderTimeline = function (style) {
		that.renderAuthorProfilePicture = function () {
			return '';
		}
		that.renderAuthor = function () {
			return '';
		}
		
		return $(that.renderBegin(style) + that.renderContent() + that.renderFooter() + that.renderEnd());
	};
	
	that.renderNewsfeed = function (style) {
		return $(that.renderBegin(style) + that.renderContent() + that.renderFooter() + that.renderEnd());
	};
	
	that.renderDetail = function () {
		return that.renderTimeline();
	};

	return that;
};

TIM.eventRenderer.facebookRenderer = function (spec) {
	var that = TIM.eventRenderer.baseRenderer(spec);
	return that;
};

TIM.eventRenderer.flickrRenderer = function (spec) {
	var that = TIM.eventRenderer.baseRenderer(spec);
	return that;
};

TIM.eventRenderer.foursquareRenderer = function (spec) {
	var that = TIM.eventRenderer.baseRenderer(spec);
	return that;
};

TIM.eventRenderer.googleplusRenderer = function (spec) {
	var that = TIM.eventRenderer.baseRenderer(spec);
	return that;
};

TIM.eventRenderer.instagramRenderer = function (spec) {

	var that = TIM.eventRenderer.baseRenderer(spec);
	return that;
};

TIM.eventRenderer.linkedinRenderer = function (spec) {
	var that = TIM.eventRenderer.baseRenderer(spec);
	
	return that;
};

TIM.eventRenderer.meRenderer = function (spec) {
	var that = TIM.eventRenderer.baseRenderer(spec);
	return that;
};

TIM.eventRenderer.twitterRenderer = function (spec) {
	var that = TIM.eventRenderer.baseRenderer(spec);
	return that;
};

TIM.eventRenderer.wordpressRenderer = function (spec) {
	var that = TIM.eventRenderer.baseRenderer(spec);
	return that;
};

TIM.eventRenderer.youtubeRenderer = function (spec) {
	var that = TIM.eventRenderer.baseRenderer(spec);
	return that;
};

TIM.eventRenderer.rendererFactory = function () {

	var dict = {"facebook": TIM.eventRenderer.facebookRenderer,
							"flickr": TIM.eventRenderer.flickrRenderer,
							"foursquare": TIM.eventRenderer.foursquareRenderer,
							"googleplus": TIM.eventRenderer.googleplusRenderer,
							"instagram": TIM.eventRenderer.instagramRenderer,
							"linkedin": TIM.eventRenderer.linkedinRenderer,
							"me": TIM.eventRenderer.linkedinRenderer,
							"twitter": TIM.eventRenderer.twitterRenderer,
							"wordpress": TIM.eventRenderer.wordpressRenderer,
							"youtube": TIM.eventRenderer.youtubeRenderer};
	
	var that = {},
			renderer;
	
	that.create = function (spec) {

		renderer = dict[spec.event.feature || ''];		
		if (renderer === undefined) {
			throw {name: "FeatureEventTypeError", message: "Unrecognized feature name: " + spec.event.feature};
		}

		return renderer(spec);
	};
	
	return that;

}();


//
// TIM.feature and associated components.  Defines the feature controller
// infrastructure for controlling and rendering 
//
TIM.feature = {};


TIM.feature.baseController = function (spec) {

	var that = {};

	that.getContainer = function () {
		return $("#feature .ui-content");
	};

	that.load = function () {
		return that;
	};

	return that;
};


TIM.feature.eventsController = function (spec) {

	var that = TIM.feature.baseController(spec);

	that.load = function () {

		$.getJSON(TIM.globals.apiBaseURL + '/v1/authors/' + TIM.pageInfo.authorName + '/features/' + spec.feature + '/events?callback=?', function (data) {
			var tl = that.getContainer(),
					events,
					renderer;
			tl.empty();
			events = data.events || [];
			if (events.length > 0) {
				$.each(events, function (idx, event) {
					renderer = TIM.eventRenderer.rendererFactory.create({"author": spec.author, "event": event});
					tl.append(renderer.renderTimeline());
				});
			}
			else {
				tl.append('<p>No Events.  Get busy and create some content!</p>')
			}
		});
		
	};

	return that;	
};


TIM.feature.facebookController = function (spec) {
	var that = TIM.feature.eventsController(spec);
	return that;
};

TIM.feature.flickrController = function (spec) {
	var that = TIM.feature.eventsController(spec);
	return that;
};

TIM.feature.foursquareController = function (spec) {
	var that = TIM.feature.eventsController(spec);
	return that;
};

TIM.feature.googleplusController = function (spec) {
	var that = TIM.feature.eventsController(spec);
	return that;
};

TIM.feature.instagramController = function (spec) {
	var that = TIM.feature.eventsController(spec);
	return that;
};

TIM.feature.linkedinController = function (spec) {
	var that = TIM.feature.eventsController(spec);
	return that;
};

TIM.feature.meController = function (spec) {

	var that = TIM.feature.baseController(spec);

	var buildProfile = function (data) {
		var profile = ''; 

		if (data.picture_url) {
			profile = profile + '<img src="' + data.picture_url + '" />';
		}
		
		var name = (data.first_name || '') + ' ' + (data.last_name || '');
		if (name.length > 0) {
			if (data.public_profile_url) {
				profile = profile + '<p><label>Name:</label> <a href="' + data.public_profile_url + '">' + name + '</a></p>';
			}
			else {
				profile = profile + '<p><label>Name:</label> ' + name + '</p>';
			}
		}

		if (data.headline) {
			profile = profile + '<p><label>Title:</label> ' + data.headline + '</p>';
		}
		if (data.industry) {
			profile = profile + '<p><label>Industry:</label> ' + data.industry + '</p>';
		}
		if (data.location) {
			profile = profile + '<p><label>Location:</label> ' + data.location + '</p>';
		}
		if (data.summary) {
			profile = profile + '<p><label>Summary:</label> ' + data.summary + '</p>';
		}
		if (data.specialties) {
			profile = profile + '<p><label>Specialties:</label> ' + data.specialties + '</p>';
		}

		return profile;
	};

	that.load = function () {
		var prfl = that.getContainer();
		prfl.empty();
		prfl.append('<div id="profileMain"><h2>thisis.me</h2></div>');
		prfl.append('<div id="profileIN" style="display:none;clear:both;"><h2>LinkedIn</h2></div>');
		prfl.append('<div id="profileGoogle" style="display:none;clear:both;"><h2>Google+</h2></div>');
		
		$.getJSON(TIM.globals.apiBaseURL + '/v1/authors/' + spec.author + '?callback=?', function (data) {
			var profBlk = $("#profileMain"),
					author = data.author || {};
			profBlk.append('<p><label>Name:</label> ' + author.fullname + '</p>');
			profBlk.append('<p><label>Email:</label> ' + author.email + '</p>');
		});

		$.getJSON(TIM.globals.apiBaseURL + '/v1/authors/' + spec.author + '/features/linkedin/profile?callback=?', function (data) {
			var profBlk = $("#profileIN"),
					profile = data || {},
					attr;
			profBlk.append(buildProfile(profile));
			profBlk.show();
		});

		$.getJSON(TIM.globals.apiBaseURL + '/v1/authors/' + spec.author + '/features/googleplus/profile?callback=?', function (data) {
			var profBlk = $("#profileGoogle"),
					profile = data || {},
					attr;
			profBlk.append(buildProfile(profile));
			profBlk.show();
		});
	};

	return that;
};

TIM.feature.twitterController = function (spec) {
	var that = TIM.feature.eventsController(spec);
	return that;
};

TIM.feature.wordpressController = function (spec) {
	var that = TIM.feature.eventsController(spec);
	return that;
};

TIM.feature.youtubeController = function (spec) {
	var that = TIM.feature.eventsController(spec);
	return that;
};


TIM.feature.controllerFactory = function () {

	var dict = {"facebook": TIM.feature.facebookController,
							"flickr": TIM.feature.flickrController,
							"foursquare": TIM.feature.foursquareController,
							"googleplus": TIM.feature.googleplusController,
							"instagram": TIM.feature.instagramController,
							"linkedin": TIM.feature.linkedinController,
							"me": TIM.feature.meController,
							"twitter": TIM.feature.twitterController,
							"wordpress": TIM.feature.wordpressController,
							"youtube": TIM.feature.youtubeController};
	
	var that = {},
			controller;
	
	that.create = function (spec) {

		controller = dict[spec.feature || ''];		
		if (controller === undefined) {
			throw {name: "FeatureTypeError", message: "Unrecognized feature name: " + spec.feature};
		}

		return controller(spec);
	};
	
	return that;

}();


//
//	AuthorController
//
TIM.AuthorsController = function (spec) {
	
	return {
	
		load: function () {
			$.getJSON(TIM.globals.apiBaseURL + '/v1/authors?callback=?', function (data) {
				var al = $("#authors ul:first"),
						authors = data.authors || [];
				al.empty();
				$.each(authors, function (idx, item) {
					al.append('<li><a href="/' + item.authorname + '" data-transition="pop">' + item.fullname + '</a></li>');
				});
				al.listview("refresh");
			});
		}
	};
};


//
// Followers
//
TIM.followersController = function (spec) {
	//return {load: function() {}};	// for debugging
	return {
		load: function () {
			var al = $("#followers fieldset:first");
			$.getJSON(TIM.globals.apiBaseURL + '/v1/authors?callback=?', function (data) {
				var authors = data.authors || [];
				al.empty();
				$.each(authors, function (idx, item) {
					var flipId = "flip_" + item.author_name;
					al.append('<input type="checkbox" name="' + flipId + '" id="' + flipId + '"' +
							'class="custom" /><label for="' + flipId + '"><a href="/' +
							item.author_name + '/timeline">' + (item.full_name || item.author_name) +
							'</a></label>');
					var url = TIM.globals.apiBaseURL + '/v1/authors/' + TIM.pageInfo.authorName +
							'/groups/follow/members/' + item.author_name;
					$('#' + flipId).bind( "change", function(event, ui) {
						if (this.checked) {	// add person
							$.ajax({ type: "PUT", url: url });
						} else {
							$.ajax({ type: "DELETE", url: url });
						}
						var newsfeedPage = $("#newsfeed");
						if (newsfeedPage !== undefined) {
							newsfeedPage.remove();
						}
					});
				});
				var stop = function(event) { event.stopPropagation(); }
				al.find("a").bind('tap', stop);
				// also don't make the button appear clicked
				al.find("a").bind('touchstart', stop);
				al.find("a").bind('click', stop);	// for non-device testing
				al.find("a").bind('mousedown', stop);
			});
			$.getJSON(TIM.globals.apiBaseURL + '/v1/authors/' + TIM.pageInfo.authorName +
					'/groups/follow/members?callback=?', function (data) {
				var authors = data.members || [];
				$.each(authors, function (idx, item) {
					var flipId = "flip_" + item.author_name;
					$('#' + flipId).prop("checked",true);
				});
				al.trigger("create");
			});
		}
	};
};


//
//	Profile
//
TIM.ProfileController = function (spec) {
	return {
		
		load: function () {			
			var $profile = $("#profile .profile");
			var $profileImg = $profile.find(".avatar img")
			var $title = $profile.find(".title");
			var $link = $profile.find(".link a");
			var $description = $profile.find(".description");
			var $linkedinUrl = $profile.find(".meta-data .profile-url a");
			var $linkedinImg = $profile.find(".meta-data .profile-url img");
			var $email = $profile.find(".meta-data .email");
			//var $phone = $profile.find(".meta-data .phone");
			
			$description.expander({
			    slicePoint:       300,  // default is 100
			});
			
			// Retrieve author information
			TIM.modelFactory.getAuthor(TIM.pageInfo.authorName, function(author) {
				$("header:visible h1").text(author.getFullName());
				$email.html('<hr/><a href="mailto:' + author.getEmail() + '">' + author.getEmail() + '</a>');
				
			});
			
			// Retrieve Profile information
			TIM.modelFactory.getAuthorProfile(TIM.pageInfo.authorName, function(profile) {
				$title.text(profile.getHeadline());
				
				var picUrl = profile.getPictureUrl();
				
				$profileImg.attr("src", profile.getPictureUrl());
				$profileImg.removeClass("data-spinner");
							
				$description.html(profile.getSummary());
				$link.text(profile.getLocation());
				
				$linkedinUrl.attr("href", profile.getProfileUrl());
				$linkedinImg.attr("src", profile.getProfileIcon());
				
				//Reset the expander
				$description.data("expander", false).expander({
			    	slicePoint:       300,  // default is 100
				});
			});
		}
	};
};

/*
 * Split the list of events into pages.
 * 1. Traverse the Event array
 * 2.1. If the event contains a photo, it should take the whole page, so add that event to the page and go to the next page.
 * 2.2. Otherwise check the next 5 events, and try to fill the page with a second event.
 */
TIM.feedController = function (events) {
	var that = {};
	
	that.events = events || [];
	that.pages = [];
	
	that.sort = function () {
		var events = that.events.concat();
		var t = 1;
		
		// Traverse the Event array
		while (events.length > 0) {
			var event = events.shift();
			var page = [event];
			 
			var len = events.length;
			
			// If that event does not contain a photo
			if (len > 0
				&& event.content.photo_url === undefined) {
				for (var i = 0, maxSkips = 0; i < len && maxSkips < 5; i++, maxSkips++) {
					var pastEvent = events[i];
					if (pastEvent.content.photo_url === undefined) {
						page.push(pastEvent);
						events.splice(i, 1);
						break;
					}
				}
			}
			that.pages.push(page);
			t++;
		}
		return that.pages;
	}
	
	return that;
}

TIM.timelineController = function (spec) {
	
	var that = {};

	that.flipSet = {};
	that.pages = {};
	that.makeURL = function () {
		return TIM.globals.apiBaseURL + '/v1/authors/' + TIM.pageInfo.authorName + '/highlights?callback=?';
	}
	that.renderMethod = 'renderTimeline';
	that.contentSelector = "#timeline .ui-content";

	that.loaded = function () {
		$(".flippage-container").bind("swipeup", function(){
      		console.log("swipeup");
      		$.mobile.silentScroll(0);
      		if (that.flipSet.canGoNext()) {
      			that.flipSet.next(function() {
      				TIM.currentPage ++;
      				
      				// If the next page has not been rendered, add it to the flipset
      				if (TIM.currentPage < that.pages.length) {
      					if (that.flipSet.getCurrentIndex() === that.flipSet.getLength() - 1) {
      						that.flipSet.push(that.makePageObj(that.pages[TIM.currentPage + 1]));
      					}
      				}
      			});	
      		}
          });
		$(".flippage-container").bind("swipedown", function(){
      		console.log("swipedown");
      		$.mobile.silentScroll(0);
			if (that.flipSet.canGoPrevious()) {
          		that.flipSet.previous(function() {
      				TIM.currentPage --;
      				
      				// If the previous page has not been rendered, add it to the flipset
      				if (TIM.currentPage > 0) {
      					if (that.flipSet.currentIndex === 0) {
      						that.flipSet.unshift(that.makePageObj(that.pages[TIM.currentPage - 1]));
      					}
      				}
      			});
          	}
          });
          
          // Prevent the browser from scrolling the page on swipe.
          $(".flippage-container").bind("touchmove", function(event) {
          		event.preventDefault();
          });
			
		window.setTimeout(function () { document.getElementById('newsfeed-content').style.left = '0'; }, 800);

		return that;
	};
	 
	
	that.load = function () {
		$.getJSON(that.makeURL(), function (data) {
			$(that.contentSelector).empty();
			
			var feedPages = new Array();
			
			try {
				TIM.currentPage = 0;
				
				that.pages = TIM.feedController(data.events || []).sort();
				
				// Add the first two pages to the FlipSet
				feedPages.push(that.makePageObj(that.pages[0]));
				feedPages.push(that.makePageObj(that.pages[1]));
				
				// Initialize Flipset
				that.flipSet = new FlipSet($(that.contentSelector), 320, 370, feedPages);
				
				that.loaded();
			}
			catch (e) {
				TIM.errorHandler.handle(e);
			}
		});
		
		return that;
	};
	
	
	// Create the Event DOM element
	that.makePageObj = function (pageEvents) {
		var obj = $("<div class='mi-content'/>");
		if (pageEvents === undefined
			|| pageEvents.length === 0) {
			obj.append('<p>No Events.  Get busy and create some content!</p>');
			return obj;
		}
			
		var len = pageEvents.length;
		var style = {"style": (len === 2 ? "half-page" : "full-page")};
		for (var i = 0; i < pageEvents.length; i++) {
			renderer = TIM.eventRenderer.rendererFactory.create({"author": TIM.pageInfo.authorName, "event": pageEvents[i]});
			obj.append(renderer[that.renderMethod](style));
		}
		return obj;
	};	
	return that;

};

TIM.newsfeedController = function (spec) {	
	var that = TIM.timelineController(spec);
	
	that.makeURL = function () {
		var followGroup = "follow";
		return TIM.globals.apiBaseURL + '/v1/authors/' + TIM.pageInfo.authorName + '/groups/' + followGroup + '/highlights?callback=?';
	}
	that.contentSelector = "#newsfeed .ui-content";
	that.renderMethod =  'renderNewsfeed';
	
	return that;
};



TIM.AuthorFeaturesController = function (spec) {

	return {
	
		load: function () {
			$.getJSON(TIM.globals.apiBaseURL + '/v1/authors/' + TIM.pageInfo.authorName + '/features?callback=?', function (data) {
				var fl = $("#authorFeatures .ui-content"),
						features;
				fl.empty();
				features = data.features || [];
				$.each(features, function (idx, feature) {
					fl.append('<a href="/' + TIM.pageInfo.authorName + '/features/' + feature.name + '" data-transition="pop">' +
											'<img src="' + feature.color_icon_medium_res + '" />' +
										'</a>');
				});
			});
		}
	};
};

TIM.DetailController = function (spec) {

	return {
	
		load: function () {

			$.getJSON(TIM.globals.apiBaseURL + '/v1/authors/' + TIM.pageInfo.authorName + '/events/' + TIM.globals.eventId + '?callback=?', function (data) {
				var dt = $("#detail .ui-content"),
						event;
				dt.empty();
				event = data.event || {};
				dt.append(TIM.eventRenderer.rendererFactory.create({"author": TIM.pageInfo.authorName, "event": event}).renderDetail());
			});
		}
	};
};

/*
 * Includes a singleton pattern
 * 
 * The Loading is asynchronous. Once done, we call the callback method.
 */
TIM.ImageController = function (spec) {
	
	var isLoaded = false;
	var isLoading = false;
	var images = {};
	return {
	
		load: function (callback) {
			if (isLoaded) {
				if (callback !== undefined) callback(this);
				return;
			}
			else if (isLoading){
				return;
			}
			
			$.getJSON(TIM.globals.apiBaseURL + '/v1/features?callback=?', function (data) {
				var features = data.features || [];
				$.each(features, function (idx, feature) {
					images[feature.name] = feature;
				});
				
				if (callback !== undefined) callback(this);
			});
		},
		
		getHResColor: function (featureName) {
			return images[featureName].color_icon_high_res;
		},

		getHResMono: function (featureName) {
			return images[featureName].mono_icon_high_res;
		},

		getMResColor: function (featureName) {
			return images[featureName].color_icon_medium_res;
		},

		getMResMono: function (featureName) {
			return images[featureName].mono_icon_medium_res;
		},

		getLResColor: function (featureName) {
			return images[featureName].color_icon_low_res;
		},

		getLResMono: function (featureName) {
			return images[featureName].mono_icon_low_res;
		}
		
	};

}();

/*
 * Utility class that loads the Resources necessary for the application
 * Currently only loads the images.
 * 
 * This object acts as a singleton to load the resources.
 * When "load" is called, the callback method (for when the resources are all there) is added to a list.
 * Once all the resources are loaded, those methods are called in their order of appearance.
 * So as not to overwhelm the Browser, we call those methods at a regular interval of 50ms.
 */
TIM.Resources = function() {
	var availableResources = [];
	availableResources.push(TIM.ImageController);
	
	var resources = [];
	
	var isLoaded = false;
	var isLoading = false;
	
	var queue = [];
	
	return {	
		load: function (callback) {
			if (isLoaded) {
				if (callback !== undefined) callback();
				return;
			}
			if (callback !== undefined) queue.push(callback);
			
			if (isLoading){
				return;
			}
			
			isLoading = true;
			for (var i = 0; i < availableResources.length; i++) {
				availableResources[i].load(this.didLoadResource);	
			}
		},
		
		didLoadResource: function(resource) {
			resources.push(resource);
			if (resources.length === availableResources.length) {
				isLoading = false;
				isLoaded = true;
				
				dequeue();
			}
		}
	};
	
	function dequeue () {
		queue.shift()();
		if (queue.length > 0) {
			setTimer(dequeue(), 50);
		}
	};
}();


//Listen for any attempts to call changePage().
$(document).bind("pagebeforechange", function (e, data) {

	// if we're navigating to the timeline for a user set the username global
	if (typeof data.toPage === "string") {
		var u = $.mobile.path.parseUrl(data.toPage);
		if (u.directory === "/") {
			TIM.pageInfo.authorName = u.filename;
		}
		else {
			var comp = u.directory.split("/");
			if (comp.length === 4 && comp[2] === "features") {
				TIM.globals.featureName = u.filename;
			}
			else
			if (comp.length === 4 && !isNaN(Number(u.filename))) {
				TIM.globals.eventId = u.filename;
			}
		}
			
	}
});

TIM.ImageController.load();

/*
 * Factory Methods for retrieving Objects from the server
 * All of the methods are Asynchronous
 */
TIM.modelFactory = {};

TIM.modelFactory.getAuthor = function(authorname, callback) {
	$.getJSON(TIM.globals.apiBaseURL + '/v1/authors/' + authorname + '?callback=?', function(data){
		if (callback !== undefined) {
			callback(TIM.models.Author(data.author))
		}
	});
}

TIM.modelFactory.getAuthorProfile = function(authorname, callback) {
	// getJSON does not call the callback method when the request fails to connect to the remote server, that is why we use google's jsonp jQuery plugin.
	$.jsonp({
		"url": TIM.globals.apiBaseURL + '/v1/authors/' + authorname + '/features/linkedin/profile?callback=?',
		"success": function(data){
			if (callback !== undefined) {
				callback(TIM.models.AuthorLinkedinProfile(data))
			}
		},
		"error": function(data, msg){
			if (callback !== undefined) {
				callback(TIM.models.DummyProfile({}))
			}
		}	
	});
}

/*
 * Model Objects
 */
TIM.models = {};

TIM.models.Author = function(author) {
	var that = {};
	that.getID = function () {
		return author.author_id || -1;
	}
	
	that.getName = function () {
		return author.name || '';
	};
	
	that.getFullName = function () {
		if (!author.full_name) {
			return author.name;
		}
		return author.full_name || '';
	};
	
	that.getEmail = function () {
		return author.email || '';
	};
	
	return that;
}

TIM.models.ProfileFillers = {
	firstName: '',
	lastName: '',
	headline: 'Founder and CEO',
	industry: '',
	location: '',
	name: '',
	pictureUrl: 'https://fbcdn-profile-a.akamaihd.net/static-ak/rsrc.php/v1/yo/r/UlIqmHJn-SK.gif',
	profileUrl: '',
	profileIcon: '/img/social_icons/linkedin.png',
	specialties: '',
	summary: 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.<br/><br/>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'
};

TIM.models.DummyProfile = function() {
	var that = {};
	var filler = TIM.models.ProfileFillers;
	
	that.getFirstName = function () {
		return filler.firstName;
	};
	
	that.getLastName = function () {
		return filler.lastName;
	};
	
	that.getHeadline = function() {
		return filler.headline;
	}
	
	that.getIndustry = function() {
		return filler.industry;
	}
	
	that.getLocation = function() {
		return filler.location;
	}
	
	that.getName = function() {
		return filler.name;
	}
	
	that.getPictureUrl = function() {
		return filler.pictureUrl;
	}
	
	that.getProfileUrl = function() {
		return filler.profileUrl;
	}
	
	that.getProfileIcon = function() {
		return filler.profileIcon;
	}
	
	that.getSpecialties = function() {
		return filler.specialties;
	}
	
	that.getSummary = function() {
		return filler.summary;
	}
	
	return that;
}

TIM.models.AuthorLinkedinProfile = function(author) {
	var that = {};
	var filler = TIM.models.ProfileFillers;
	
	that.getFirstName = function () {
		return author.first_name || filler.firstName;
	};
	
	that.getLastName = function () {
		return author.last_name || filler.lastName;
	};
	
	that.getHeadline = function() {
		return author.headline || filler.headline;
	}
	
	that.getIndustry = function() {
		return author.industry || filler.industry;
	}
	
	that.getLocation = function() {
		return author.location || filler.location;
	}
	
	that.getName = function() {
		return author.name || filler.name;
	}
	
	that.getPictureUrl = function() {
		return author.picture_url || filler.pictureUrl;
	}
	
	that.getProfileUrl = function() {
		return author.public_profile_url || filler.profileUrl;
	}
	
	that.getProfileIcon = function() {
		return '/img/social_icons/linkedin.png';
	}
	
	that.getSpecialties = function() {
		return author.specialties || filler.specialties;
	}
	
	that.getSummary = function() {
		return author.summary || filler.summary;
	}
	
	return that;
}

$(document).delegate("#authors", "pageinit", function () {
	 TIM.Resources.load(function() {
		TIM.AuthorsController({}).load();
	 });
});

$(document).delegate("#followers", "pageinit", function () {
	 TIM.Resources.load(function() {
		TIM.followersController({}).load();
	 });
});

$(document).delegate("#profile", "pageinit", function () {
	TIM.ProfileController({}).load();
});

/*
 * 1. Set Newsfeed index to the first page
 * 2. Load newsfeed
 */
$(document).delegate("#newsfeed", "pageinit", function () {
	TIM.newsfeedCurrentPage = 0;
	TIM.currentPage = TIM.newsfeedCurrentPage;
	
	TIM.Resources.load(function() {
		TIM.newsfeedController({}).load();
	});
});

$(document).delegate("#newsfeed", "pageshow", function () {
	// Force timeline reloading.
	var timelinePage = $("#timeline");
	if (timelinePage !== undefined) {
		timelinePage.remove();
	}
	
	// Set the page index to the latest timeline index.
	TIM.currentPage = TIM.newsfeedCurrentPage;
});

/*
 * 1. Set Timeline index to the first page
 * 2. Load timeline
 */
$(document).delegate("#timeline", "pageinit", function () {
	TIM.timelineCurrentPage = 0;
	TIM.currentPage = TIM.timelineCurrentPage;
	
	TIM.Resources.load(function() {
		TIM.timelineController({}).load();
	});
});

$(document).delegate("#timeline", "pageshow", function () {
	// Set the page index to the latest timeline index.
	TIM.currentPage = TIM.timelineCurrentPage; 
});

$(document).delegate("#authorFeatures", "pageinit", function () {
	 TIM.Resources.load(function() {
		TIM.AuthorFeaturesController({}).load();
	 });
});

$(document).delegate("#feature", "pageinit", function () {
	try {
		TIM.feature.controllerFactory.create({"author": TIM.pageInfo.authorName, "feature": TIM.globals.featureName}).load();
	}
	catch (e) {
		TIM.errorHandler.handle(e);
	}
});

$(document).delegate("#detail", "pageinit", function () {
	 TIM.Resources.load(function() {
		TIM.DetailController({}).load();
	 });
});

$(window).bind('orientationchange', function (event) {

});

// jQuery Mobile v1.1 has "fade" for default transition (due to android performance issues with the sliding).
$(document).bind("mobileinit", function(){
	//apply overrides here
	$.extend(  $.mobile , {
	   defaultPageTransition: 'slide'
  	});
});

$(document).ready(function () {
});

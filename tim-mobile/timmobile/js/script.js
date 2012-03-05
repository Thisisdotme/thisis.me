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

	that.getAuthorName = function () {
		return spec.author || '';
	};
	
	that.getAuthorProfilePicture = function() {
		return spec.event.author.profile_image_url || '';
	}

	that.getEventId = function () {
		return spec.event.feature_event_id;
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
	
	that.getShortCaption = function (shortCaptionLength) {
		if (shortCaptionLength === undefined) {
			shortCaptionLength = 50;
		}
		var caption = that.getCaption();
		return (caption.length <= shortCaptionLength) ? caption : (caption.substr(0, shortCaptionLength) + "...");
	};

	that.getData = function () {
		return spec.event.content.data || '';
	};

	that.getAuxillaryData = function () {
		return spec.event.content.auxillary_data || '';
	};
	
	that.getContentURL = function () {
		return spec.event.content.url || '';
	};
	
	that.getEventDisplaySize = function () {
		return 'full-page';
	}

	that.renderBegin = function () {
		return '<div class="event ' + that.getEventDisplaySize() + '">';
	};
	
	that.renderContent = function () {
		return '<div class="text-content">' + TIM.utils.linkify(that.getCaption()) + '</div>';
	};
	
	that.renderEnd = function () {
		return '</div>';
	};
	
	// that.renderUserInfo = function () {
		// return '<div class="userinfo">' + that.renderUserIcon + that.render+ '</div>';
	// }
// 	
	 that.renderAuthorProfilePicture = function () {
	 	 return '<div class="avatar">' +
	 	 			'<div class="frame">' +
						'<img src="' + that.getAuthorProfilePicture() + '" />' +
					'</div>' +
				'</div>';
	 }
	that.renderFooter = function () {
		return '<div class="footer">' + that.renderAuthorProfilePicture() + that.renderInfo() +  that.renderBaseline() + '</div>';
	}
	
	that.renderInfo = function () {
		var author = '<div class="author">' + that.getAuthorName() + '</div>';
		var caption = '<div class="caption">' + that.getShortCaption() + '</div>';
		return '<div class="info">' + author + caption + '</div>';
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

	that.renderTimeline = function () {
		return $(that.renderBegin() + that.renderContent() + that.renderFooter() + that.renderEnd());
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

	that.renderContent = function () {
		return '<div class="img-content"><img src="' + this.getAuxillaryData().images.low_resolution.url + '" /></div>';
	};

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
	
	that.renderInfo = function () {
		var author = '<div class="author">' + that.getAuthorName() + '</div>';
		return '<div class="info" style="display: table-cell;">' + author + '</div>';
	}
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

TIM.timelineController = function (spec) {
	
	var that = {},
			theScroller = undefined;

	var pullDownAction = function () {
		that.load();
	};
	
	var pullUpAction = function () {
		that.load();
	};

	that.loaded = function () {

		if (theScroller !== undefined) {
			theScroller.refresh();
		}
		else {

			var pullDown = $('#pullDown'),
					pullDownOffset = pullDown.outerHeight(true),
					pullUp = $('#pullUp'),	
					pullUpOffset = pullUp.outerHeight(true);

			// theScroller = new iScroll('wrapper', {
				// useTransition: true,
				// topOffset: pullDownOffset,
				// onRefresh: function () {
					// if (pullDown.hasClass('loading')) {
						// pullDown.removeClass('loading');
						// pullDown.find('.pullDownLabel').text('Pull down to refresh...');
					// }
					// else
					// if (pullUp.hasClass('loading')) {
						// pullUp.removeClass('loading');
						// pullUp.find('.pullUpLabel').text('Pull up to load more...');
					// }						
// 
				// },
				// onScrollMove: function () {
					// if (this.y > 5 && !pullDown.hasClass('flip')) {
						// pullDown.addClass('flip');
						// pullDown.find('.pullDownLabel').text('Release to refresh...');
						// this.minScrollY = 0;
					// } 
					// else 
					// if (this.y < 5 && pullDown.hasClass('flip')) {
						// pullDown.removeClass('flip');
						// pullDown.find('.pullDownLabel').text('Pull down to refresh...');
						// this.minScrollY = -pullDownOffset;
					// }
					// else
					// if (this.y < (this.maxScrollY - 5) && !pullUp.hasClass('flip')) {
						// pullUp.addClass('flip');
						// pullUp.find('.pullUpLabel').text('Release to refresh...');
						// this.maxScrollY = this.maxScrollY;
					// }
					// else
					// if (this.y > (this.maxScrollY + 5) && pullUp.hasClass('flip')) {
						// pullUp.removeClass('flip');
						// pullUp.find('.pullUpLabel').text('Pull up to load more...');
						// this.maxScrollY = pullUpOffset;
					// }						
				// },
				// onScrollEnd: function () {
					// if (pullDown.hasClass('flip')) {
						// pullDown.removeClass('flip').addClass('loading');
						// pullDown.find('.pullDownLabel').text('Loading...');
						// pullDownAction();
					// }
					// else if (pullUp.hasClass('flip')) {
						// pullUp.removeClass('flip').addClass('loading');
						// pullUp.find('.pullUpLabel').text('Loading...');				
						// pullUpAction();
					// }					
				// }
			// });
			
			
			// $("#wrapper").bind("swipe", function(){
          		// console.log("swipe");
          		// if (that.flipSet.canGoNext()) {
          			// that.flipSet.next();	
          		// }
//           		
          		// // that.setPage($("#newsfeed .mi-content"), ++TIM.currentPage);
				// // that.loaded();
              // });
//               
			$("#newsfeed-content").bind("swipeup", function(){
          		console.log("swipeup");
          		if (that.flipSet.canGoNext()) {
          			that.flipSet.next(function() {
          				TIM.currentPage ++;
          				
          				// If the next page has not been rendered, add it to the flipset
          				if (TIM.currentPage < TIM.allEvents.length) {
          					if (that.flipSet.getCurrentIndex() === that.flipSet.getLength() - 1) {
          						that.flipSet.push(that.makePageObj(TIM.currentPage + 1));
          					}
          				}
          			});	
          		}
              });
			$("#newsfeed-content").bind("swipedown", function(){
          		console.log("swipedown");
				if (that.flipSet.canGoPrevious()) {
	          		that.flipSet.previous(function() {
          				TIM.currentPage --;
          				
          				// If the previous page has not been rendered, add it to the flipset
          				if (TIM.currentPage > 0) {
          					if (that.flipSet.currentIndex === 0) {
          						that.flipSet.unshift(that.makePageObj(TIM.currentPage - 1));
          					}
          				}
          			});
	          	}
              });
              
              $("#newsfeed-content").bind("touchmove", function(event) {
              		event.preventDefault();
              });
		}
			
		window.setTimeout(function () { document.getElementById('newsfeed-content').style.left = '0'; }, 800);

		return that;
	};
	
	that.flipSet = {};
	
	that.load = function () {
				
		$.getJSON(TIM.globals.apiBaseURL + '/v1/authors/' + TIM.pageInfo.authorName + '/events?callback=?', function (data) {
			var feedPages = new Array();
			var tl = $("#newsfeed .mi-content"),
					renderer;
			try {
				tl.remove();
				TIM.allEvents = data.events || [];
				TIM.currentPage = 0;
				
				feedPages.push(that.makePageObj(TIM.currentPage));
				feedPages.push(that.makePageObj(TIM.currentPage + 1));
				that.flipSet = new FlipSet($("#newsfeed .ui-content"), 320, 370, feedPages);
				
				that.loaded();
			}
			catch (e) {
				TIM.errorHandler.handle(e);
			}
		});
		
		return that;
	};
	
	that.makePageObj = function (idx) {
		if (TIM.allEvents === undefined
			|| idx < 0 
			|| idx > TIM.allEvents.length) {
			return null;
		}
		
		var obj = $("<div class='mi-content'/>");
		if (TIM.allEvents.length > 0) {
			var numberOfFeedsPerPage = 1;
			var firstDisplayedFeed = idx * numberOfFeedsPerPage;
			var lastDisplayedFeed = firstDisplayedFeed + numberOfFeedsPerPage;
			console.log(firstDisplayedFeed);
			for (var i = firstDisplayedFeed; i < lastDisplayedFeed; i++) {
				renderer = TIM.eventRenderer.rendererFactory.create({"author": TIM.pageInfo.authorName, "event": TIM.allEvents[i]});
				obj.append(renderer.renderTimeline());
			}
		}
		else {
			obj.append('<p>No Events.  Get busy and create some content!</p>');
		}
		return obj;
	};	
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
				
				for (var i = 0; i < queue.length; i++) {
					queue[i]();	
				}
			}
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
	
$(document).delegate("#authors", "pageinit", function () {
	 TIM.Resources.load(function() {
		TIM.AuthorsController({}).load();
	 });
});

$(document).delegate("#newsfeed", "pageinit", function () {
	TIM.currentPage = 0;
	TIM.allEvents = [];

	TIM.Resources.load(function() {
		TIM.timelineController({}).load();
	});
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

$(document).ready(function () {
});
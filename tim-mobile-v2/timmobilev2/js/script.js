
//set up the TIM object/namespace
window.TIM = TIM || {};
TIM.routers = TIM.routers || {};
TIM.models = TIM.models || {};
TIM.collections = TIM.collections || {};
TIM.views = TIM.views || {};
TIM.mixins = TIM.mixins || {};
TIM.featureHandlers = TIM.featureHandlers || {};
TIM.loadedFeatures = TIM.loadedFeatures || {};
TIM.authorFeatures = TIM.authorFeatures || {};
TIM.defaultFeature = "cover";
TIM.currentPageElem = $('#splash-screen');
TIM.previousPageElem = undefined;
TIM.appContainerElem = $('#content-container');
TIM.defaultTransition = "fade";
TIM.loading_ = false;
TIM.transitioning_ = false;
TIM.errorShowing_ = true;
TIM.errorMessageView = undefined;

TIM.apiUrl = TIM.globals.apiBaseURL + "/v1/";

//hide address bar
window.addEventListener("load",function() {
    setTimeout(function(){
        window.scrollTo(0, 0);
    }, 0);
});

$(function() {
    
  var parsedUri = parseUri(window.location.href);
  console.log("parsed uri: ", parsedUri);
  
  //set up global event aggregator
	TIM.eventAggregator =  _.extend({}, Backbone.Events);
  
  //if there's no author, don't do anything!
  if(!TIM.pageInfo || !TIM.pageInfo.authorName || TIM.pageInfo.authorName === '') {
    return;
  }
  
  //have a global event/handler for window resize (reorientation?)
  //
  //views can subscribe to this and ... update their sizes accordingly if they have explicit sizes
  //especially for scrollable areas, which need an explicit size, at least for iscroll
  //
  //should have a scrollable area object in the views.js?
  //
  //
  
  
  //move things like this to a utils object?
  function reorient(e) {
      var portrait = (window.orientation % 180 == 0);
      //get new window dimensions
      var height =  $(window).height(),
          width =  $(window).width();
      //don't bother for desktop sizes!
      if (height > 480) return;
      $("#app").css("min-height", height);
      $("#app").css("width", width);
  }
  window.onorientationchange = reorient;
  window.setTimeout(reorient, 0);
  window.onresize = TIM.setViewportSize;
  
  //
  // thinking of themes as 'light' or 'dark', etc.
  // they should probably be specially-named, eg "theme-dark" and/or kept in a well-known list to make removing the previous theme easy
  //
  TIM.setPageTheme = function(theme) {
     $("#app").addClass(theme);
  }
  
  TIM.getViewportSize = function() {
    return {height: TIM.viewportHeight_, width: TIM.viewportWidth_ }
  }
  
  TIM.setViewportSize = function() {
    TIM.viewportWidth_ = $(window).width();
    TIM.viewportHeight_ = $(window).height();
  }
  
  TIM.setViewportSize();
  
  //what is this preventscrolling nonsense?
  
  TIM.disableScrolling = function() {
    //$(document).on("touchstart", preventScrolling);
    $(document).on("touchmove", preventScrolling);
  }
  
  TIM.enableScrolling = function() {
    //$(document).off("touchstart", preventScrolling);
    //$(document).off("touchmove", preventScrolling);
  }
  
  function preventScrolling(e) {
    e.preventDefault();
  }
	
	TIM.disableScrolling();
	
	TIM.setLoading = function (loading) {
	  TIM._loading = loading;
	  if(loading) {
	    $('#app').addClass('loading');
	  } else {
	    $('#app').removeClass('loading');
	  }
	}
	
	TIM.isLoading = function() {
	  return TIM._loading;
	}
	
	TIM.setSplashScreen = function (splash) {
	  TIM._splash = splash;
	  if(splash) {
	    $('body').addClass('splash');
	  } else {
	    $('body').removeClass('splash');
	  }
	}
	
	TIM.setTransitioning = function (transitioning) {
	  TIM._transitioning = transitioning;
	  if(transitioning) {
	    $('#app').addClass('transitioning');
	  } else {
	    $('#app').removeClass('transitioning');
	  }
	}
	
	TIM.isTransitioning = function() {
	  return TIM.transitioning_;
	}
	
	TIM.setErrorShowing = function (isError) {
	  TIM.errorShowing_ = isError;
	  if(isError) {
	    $('#app').addClass('error');
	    $('#app').removeClass('nav-open');
	  } else {
	    $('#app').removeClass('error');
	  }
	}
	
	//TIM.setLoading(true);  //don't show 'loading' message by default!
	
	//collection of features for this author
	TIM.features = new TIM.collections.Features();
	
	//all available services
	TIM.services = new TIM.collections.Services();
	
	//set up the main feature nav
	TIM.featureNavView = new TIM.views.FeatureNav({
	  collection: TIM.features
	})
	
	//fetch the features for this author on load
	//use a JSONP plugin that properly reports errors?
	//
	//
	TIM.features.fetch({
		//dataType: "jsonp",
		//add this timeout in case call fails...
		//timeout : 5000,
		callbackParameter: "callback",
		success: function(resp) {
		  console.log('fetched features');
		},
		error: function(resp) {
			TIM.showErrorMessage({
			    exception: "loading features failed for " + TIM.pageInfo.authorName + ". perhaps this author doesn't exist?"
			});
		}
	});
	
	TIM.services.fetch({
		//add this timeout in case call fails...
		timeout : 5000,
		callbackParameter: "callback",
		success: function(resp) {
		  console.log('fetched services');
		},
		error: function(resp) {
			TIM.showErrorMessage({
			    exception: "loading services failed."
			});
		}
	});
	
	//1. get features for author
	//2. get cover page assets for author
		
  TIM.Router = Backbone.Router.extend({
	  
	  routes: {
	    //setting these routes so that basically every hash change gets handled, whether there's a corresponding feature for it or not
      "*anything" : "catchAll",
      "" : "catchAll"
    },

    initialize: function() {
          	
    	TIM.eventAggregator.bind('featureloaded', this.featureLoaded, this);
    	TIM.eventAggregator.bind('featurenavrendered', this.featureNavRendered, this);
    	TIM.eventAggregator.bind('detailLinkClicked', this.detailLinkClicked, this);
    	TIM.eventAggregator.bind('error:featureload', this.featureLoadError, this);
    	TIM.eventAggregator.bind('error', this.handleError, this);
    	
    	//move these to backbone views?
    	//make sure we have tap event
    	
    	$('#nav-toggle').on('tap', (function(event){
    	  event.preventDefault();
    	  event.stopPropagation();
    	  $('#app').toggleClass('nav-open');
    	}));
    	
    	$('#nav-toggle').on('click', (function(event){
    	  event.preventDefault();
    	  event.stopPropagation();
    	}));
    	
    	$('#app').on('tap', (function(event){
    	  event.preventDefault();
    	}))
    	
    	$('#app').on('tap', 'a', function(event) {
    	  event.preventDefault();
      	event.stopPropagation();
    	  TIM.handleLinkClick(event);
    	})
    	
    	$('#app').on('click', 'a', function(event) {
    	  event.preventDefault();
    	  event.stopPropagation();
    	})
    },
  
    //should probably pass an option here of whether to 'activate' the feature
    featureLoaded: function(options) {
      console.log("Feature loaded callback: ", options);
      var feature = options.feature, path = options.path, navigate = options.navigateOnLoad;
      if(navigate) {
        feature.behavior.activate(path);
        TIM.eventAggregator.trigger('featureselected', feature); //to select the menu item?
      }
    },
    
    featureLoadError: function(options) {
      console.log("Feature loaded failed: ", options);
      TIM.showErrorMessage(options);
    },
    
    handleError: function(options) {
      console.log("General application error: ", options);
      TIM.showErrorMessage(options);
    },
  
    featureNavRendered: function(){
      var hash = window.location.hash;
      hash = hash || "cover";
      this.navigate(''); //doing this so the following call actually triggers the event
      
      this.navigate(hash, {'trigger': true}); //trigger a hashchange event
    },
  
    //this obviously needs to be more generalized - should work for <a> tags
    detailLinkClicked: function(id, featureName){
      console.log('user clicked a detail link - args are:', arguments);
      this.navigate(featureName + '/' + id, {'trigger': true}); //trigger a hashchange event
    }
        
	})
	
	TIM.app = new TIM.Router();
	
  Backbone.history.start({root: '/' + TIM.globals.authorName});
		
	$.fn.animationComplete = function( callback ) {
		if( "WebKitTransitionEvent" in window ) {
			return $( this ).one( 'webkitAnimationEnd', callback );
		}
		else{
			// defer execution for consistency between webkit/non webkit
			setTimeout( callback, 0 );
			return $( this );
		}
	};
	
	//binding to 'all' on the router - this will get fired for any hash change event
	//make sure menu item is selected
	
	TIM.app.bind('all', function(route, path) {
	    TIM.navigateHandler(route, path);  //move the handler fn outside of here so we can explicitly call it elsewhere
  });
  
  TIM.navigateHandler = function(route, path) {
	    
	    // the 'route' argument will be in the form "route:featurename"
	    
	    console.log('hash change event: ', arguments);
	    
	    localStorage.removeItem('tim_last_url');
	    
	    if(route.split(':')[0] === 'route') {
	      
  	    var featureName = route.split(':')[1]; //assuming the hash will start with the feature name
  	    //total hack for 'home page'
  	    if (featureName == 'home') {
  	      location.href = "/";
  	      return;
  	    }
  	    
  	    var feature = TIM.features.getByName(featureName);
  	    if (TIM.features.getSelectedFeature()) {
  	      TIM.setLoading(true); //make this a method on TIM
  	    }
  	    
  	    if(localStorage && localStorage.setItem) {
  	       localStorage.setItem('tim_last_url', '/' + TIM.pageInfo.authorName + "#" + featureName + (path || ""));
  	    }
  	    
  	    if(!feature) {
  	      console.log('no feature');
  	      if (TIM.features.length == 0) {
  	        TIM.eventAggregator.trigger("error", {exception: "No features loaded for this author"});
  	        localStorage.setItem('tim_last_url', '/');
  	        return;
  	      }
  	      //we get here if there was no feature in the URL
  	      //stay on the current feature if there is one, or else go to the cover page
  	      $('#app').removeClass('nav-open');
  	      if(TIM.features.getSelectedFeature()) {
  	          $('#app').removeClass('loading');
  	          TIM.app.navigate(TIM.features.getSelectedFeature().get('feature_name'), {replace:true});
  	          return;
  	      } else {
  	        feature = TIM.features.getByName("cover");
  	        TIM.app.navigate("cover", {replace:true});
  	      }
  	      resourceId = undefined;
  	    }
  	    $('#app').removeClass('nav-open');
  	    if (feature.behavior) {
  	        console.log('********* activating feature *********', path);
            feature.behavior.activate(path);
            TIM.features.setSelectedFeature(feature); //this should be a callback from the feature when it's been activated?
        } else {
          feature.loadFeature(path);
          TIM.features.setSelectedFeature(feature);
        }
      }
  };
  
  TIM.showErrorMessage = function (options) {
    TIM.setLoading(false);
    if (!TIM.errorMessageView) {
      TIM.errorMessageView = new TIM.views.ErrorMessage();
    }
    TIM.errorMessageView.render({message: options.exception});
    TIM.setErrorShowing(true);
  };
  
  //for now this simply handles the DOM page transition
  //
  //should keep a history stack & use that to determine whether to do a forward or reverse transition
  
	TIM.transitionPage = function (toPage, options) {
	  //TIM.setErrorShowing(false);
	  $('#app').removeClass('loading initializing nav-open');
	  options = options || {};
	  var fromPage = options.fromPage || TIM.currentPageElem;
	  
	  //only do transition if necessary - if the from and to page are the same, just return
	  
	  console.log('transitioning (fromPage, toPage, fromPage==toPage:) ', toPage, fromPage, toPage.is(fromPage));
	  
	  if(toPage.is(fromPage) && !options.transitionSamePage) { //always transitioning for now...
	    return;
	  }
	 
	  var animationName = options.animationName || TIM.defaultTransition;
	
	  var inClasses = " in " + animationName + " ";
	  var outClasses = " out " + animationName + " ";
	  var transitions = TIM.getAvailableTransitions();
	  if(options.reverse) {
	    inClasses += " reverse ";
	    outClasses += " reverse ";
	  } 
	  $('#app').addClass('transitioning'); //make this a TIM method?
	  if (fromPage) {
	    //animationComplete binds a one-time handler for when the animation of the element is complete
	    fromPage.removeClass('in reverse ' + transitions).addClass(outClasses).addClass('active').animationComplete(function() {
	      console.log('animation complete for from page: ');
	      $(this).removeClass(outClasses + transitions + ' active');
	      $('#app').removeClass('transitioning');
	      TIM.setErrorShowing(false);
  	    TIM.setSplashScreen(false);
	      if(options.callback) {
	        options.callback();
	      }
	     
	    });
	  }
	  toPage.removeClass('out reverse').addClass(inClasses);
	    toPage.addClass('active').animationComplete(function() {
  	    console.log('animation complete for to page: ', this);
        $(this).removeClass(transitions + " in").addClass('active');
        $('#app').removeClass('transitioning');
        setTimeout(function(){
            window.scrollTo(0, 0);
        }, 0);
      });
	  
      	  
	  TIM.currentPageElem = toPage;
	  TIM.previousPageElem = fromPage;
	};
	
	TIM.availableTransitions = ["fade","slide","flip"];
	
	TIM.getAvailableTransitions = function() {
	  return TIM.availableTransitions.join(" ");
	}
	
	//this is where we are sending all click/tap events for <a> tags
	//normalize the URL to trigger the proper hash change?
	//
	
	TIM.handleLinkClick = function (event) {
	  event.preventDefault();
	  var el = event.currentTarget;
	 
	  //everything after the first slash?
	  //this probably needs to be something more intelligent with scary regular expressions!
	  //
	  
	  var url = el.data && el.data("url") || (el.hash || el.pathname);
	  TIM.app.navigate(url, {trigger: true});
	}
	
	TIM.globalHammer = new Hammer(document.body);
	
});
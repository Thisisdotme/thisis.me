
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
TIM.pageHistory = [];
TIM.currentPageElem = TIM.currentPageElem || $('#splash-screen');
TIM.previousPageElem = undefined;
TIM.appContainerElem = $('#content-container');
TIM.placeholderIcon = "http://mvp2.thisis.me:8080/img/icons/instagram_15.png";
TIM.defaultTransition = "fade";
TIM.loading_ = false;
TIM.transitioning_ = false;
TIM.errorShowing_ = true;
TIM.errorMessageView = undefined;
TIM.currentUser = undefined; //the person who is currently logged in - will be an author object initially...
TIM.loggedIn = false;
TIM.navVisiblestyle_ = true;
TIM.authenticatedUser = TIM.authenticatedUser || undefined;

TIM.apiUrl = TIM.globals.apiBaseURL + "/v1/";

//hide address bar
window.addEventListener("load",function() {
    setTimeout(function(){
        window.scrollTo(0, 0);
    }, 0);
});

$(function() {
  //set up global event aggregator
	TIM.eventAggregator =  _.extend({}, Backbone.Events);
    
  if(!$.cookie('tim_session')) {
    $.cookie('tim_session', true);
  }
  
  //if there's no author, don't do anything!
  if(!TIM.pageInfo || !TIM.pageInfo.authorName || TIM.pageInfo.authorName === '') {
    return;
  }
  
  //have a global event/handler for window resize (reorientation?)
  //
  //views can subscribe to this and ... update their sizes accordingly if they have explicit sizes
  //especially for scrollable areas, which need an explicit size, at least for iscroll
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
  window.onorientationchange = reorient; //handle flip from partrait to landscape
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
  
  TIM.disableScrolling = function() {
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
	
	TIM.setNavVisible = function (visible) {
	  visible = true; //disabling this fn for the moment
	  TIM.navVisible_ = visible;
	  if(visible) {
	    $('#app').removeClass('nav-hidden');
	  } else {
	    $('#app').addClass('nav-hidden');
	  }
	}
	
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
	
	TIM.setInitializing = function (initializing) {
	  TIM._initializing = initializing;
	  if(initializing) {
	    $('#app').addClass('initializing');
	  } else {
	    $('#app').removeClass('initializing');
	  }
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
	
	TIM.setFlashMessageShowing = function (show) {
	  TIM.flashMessageShowing_ = show;
	  if(show) {
	    $('#app').addClass('flash-message');
	  } else {
	    $('#app').removeClass('flash-message');
	  }
	}
	
	//TIM.setLoading(true);  //don't show 'loading' message by default!
	
	//all available app features - hardcode for now, API call to get list doesn't exist?
	TIM.allFeatures = new TIM.collections.AppFeatures(
	  [ 
	    {name: "cover"},
	    { name: "timeline"  },
	    { name: "highlights" },
	    { name: "photos"  },
	    { name: "videos"  },
	    { name: "places"  },
	    { name: "bio" }
	  ]
	);
	
	TIM.currentUserFeatures = new TIM.collections.AppFeatures();
	
	TIM.features = new TIM.collections.Features();
	
	//all available services
	TIM.allServices = new TIM.collections.Services();
	
	//services for the current user
	TIM.currentUserServices = new TIM.collections.Services();

	//set up the main feature nav
	TIM.featureNavView = new TIM.views.FeatureNav({
	  collection: TIM.features
	})
	
	//get all the availiable services from the API - these will be needed for rendering
	TIM.allServices.fetch({
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
	
	//use this to figure out path information
	var parsedUri = parseUri(window.location.href);
  
  //are we looking at an author's app or are we somewhere else (homepage, etc.)
	TIM.isAuthorApp = function() {
	  var val = true;
	  if (TIM.pageInfo.authorName === 'thisis.me') {
	    val = false;
	  }
	  if(parsedUri.path === '/' || parsedUri.path == '/login' || parsedUri.path == '/settings') { //don't do all the author-specific feature stuff if we're on the home screen
      val = false;
    }
    return val;
	}
	
			
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
    	TIM.eventAggregator.bind('login', this.handleLogin, this);
    	TIM.eventAggregator.bind('logout', this.handleLogout, this);
    	TIM.eventAggregator.bind('usercreated', this.handleNewUser, this);
    	TIM.eventAggregator.bind('addedfeature', this.handleFeatureAdd, this);
    	
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
      
      if(TIM.isAuthorApp()) {
        this.navigate(hash, {'trigger': true}); //trigger a hashchange event
      }
    },
  
    //this obviously needs to be more generalized - should work for <a> tags
    detailLinkClicked: function(id, featureName){
      console.log('user clicked a detail link - args are:', arguments);
      this.navigate(featureName + '/' + id, {'trigger': true}); //trigger a hashchange event
    },
    
    handleLogin: function() {
      $('#app').addClass('logged-in').removeClass('logged-out');
    },

    handleLogout: function() {
      $('#app').removeClass('logged-in').addClass('logged-out');;
    },
    
    handleNewUser: function(user) {
      var name = user.name;
      var password = user.password;
      console.log(user);
      if (name && password) {
        TIM.authenticatedUser.doLogin(name, password, function(){
           if(TIM.isAuthorApp()) {
              TIM.app.navigate('cover', {trigger:true});
            } else {
              window.location.href = "/";
            }
        });
      }
    },
    
    handleFeatureAdd: function() {
      TIM.showFlashMessage('Added new feature!');
      TIM.showSettingsView();
    }
        
	})
	
	TIM.fetchCurrentUserServices = function(options) {
	  options = options || {};
	  if(TIM.authenticatedUser && TIM.authenticatedUser.get('name')) {
      TIM.currentUserServices.setURL(TIM.authenticatedUser.get('name'));
  	  TIM.currentUserServices.fetch({
    		//add this timeout in case call fails...
    		timeout : 5000,
    		success: function(resp) {
    		  console.log('fetched user services ', TIM.currentUserServices.length);
    		  TIM.currentUserServices.initialized = true;
    		  if(options.callback) {
    		    options.callback();
    		  }
    		},
    		error: function(resp) {
    			TIM.showErrorMessage({
    			    exception: "loading user services failed."
    			});
    		}
    	});
  	}
	}
	
	TIM.fetchCurrentUserFeatures = function(options) {
	  options = options || {};
	  TIM.currentUserFeatures.initialized = true;
	 
	  if(TIM.authenticatedUser && TIM.authenticatedUser.get('name')) {
      TIM.currentUserFeatures.setURL(TIM.authenticatedUser.get('name'));
  	  TIM.currentUserFeatures.fetch({
    		//add this timeout in case call fails...
    		timeout : 5000,
    		success: function(resp) {
    		  console.log('fetched user features ', TIM.currentUserFeatures.length);
    		  TIM.currentUserFeatures.initialized = true;
    		  if(options.callback) {
    		    options.callback();
    		  }
    		},
    		error: function(resp) {
    			TIM.showErrorMessage({
    			    exception: "loading user features failed."
    			});
    		}
    	});
  	}
	}
	
	TIM.app = new TIM.Router();
	
	if(TIM.isAuthorApp()) {
	  Backbone.history.start({root: '/' + TIM.globals.authorName});
	} else {
	  Backbone.history.start({root: parsedUri.path});
	  TIM.app.route("logout", "logout"); 
	  TIM.app.route("login", "login"); 
	}
	
	//
	//fetch the features for this author on load
	//if it's not an author's app, just add the default nav items (login, settings, home)
	//
	
	if (TIM.isAuthorApp()) {
	  TIM.features.fetch({
  		success: function(resp) {
  		  console.log('fetched features');
  		},
  		error: function(resp) {
  			TIM.showErrorMessage({
  			    exception: "loading features failed for " + TIM.pageInfo.authorName + ". perhaps this author doesn't exist?"
  			});
  		}
  	});
	} else {
	  TIM.features.reset([
	      {name: "login"},
	      {name: "settings"},
	      {name: "home"}
	    ]) 
	}
  
  //see if we have a current user
  //if we have an auth_tkt cookie we can assume we do... the api is free to reject requests even if the front end thinks there's a user
  
  TIM.authenticatedUser = new TIM.models.AuthenticatedUser();
  TIM.authenticatedUser.createFromCookie();
  
  
	$.fn.animationComplete = function( callback ) {
		if("WebKitTransitionEvent" in window) {
			return $(this).one('webkitAnimationEnd', callback);
		}
		else{
			// defer execution for consistency between webkit/non webkit
			setTimeout(callback, 0);
			return $(this);
		}
	};
	
	//binding to 'all' on the router - this will get fired for any hash change event
	
	TIM.app.bind('all', function(route, path) {
	    TIM.navigateHandler(route, path);  //move the handler fn outside of here so we can explicitly call it elsewhere
  });
  
  TIM.navigateHandler = function(route, path) {
	    
	    // the 'route' argument will be in the form "route:featurename"
	    //
	    // the 'path' argument will be there if there's additional path info for the feature to handle
	    
	    console.log('hash change event: ', arguments);
	    
	    localStorage.removeItem('tim_last_url');  //last url is for 'save to home screen' use
	    
	    if(route.split(':')[0] === 'route') {
	      
  	    var featureName = route.split(':')[1]; //assuming the hash will start with the feature name
  	    
  	    //there is no registered 'feature' for the home page, so just navigate to the site root
  	    if (featureName == 'home' || (featureName == 'catchAll' && path == 'home')) {
  	      location.href = "/";
  	      localStorage.removeItem('tim_last_url');
  	      return;
  	    }
  	    
  	     //there isn't a proper logout 'feature', so special-case this
  	    if (featureName == 'logout') {
  	      TIM.doLogout();
  	      return;
  	    }
  	    
  	    //there isn't a proper login 'feature', so special-case this
  	    if (featureName == 'login') {
  	      TIM.showLoginForm();
  	      return;
  	    }
  	    
  	    //navigate straight to the settings page if that's what the user's requesting
  	    if (parsedUri.path == "/settings" && path == 'cover') {
  	      location.href = "/settings";
  	      return;
  	    }
  	    
  	    //navigate straight to the settings page if that's what the user's requesting
  	    if (featureName == 'settings' || parsedUri.path == "/settings") {
  	      location.href = "/settings";
  	      localStorage.removeItem('tim_last_url');
  	      return;
  	    }
  	    
  	    var feature = TIM.features.getByName(featureName);
  	    
  	    //show the loading message if we're navigating from one feature to the other
  	    if (TIM.features.getSelectedFeature()) {
  	      TIM.setLoading(true); //make this a method on TIM
  	    }
  	    
  	    if(localStorage && localStorage.setItem && TIM.isAuthorApp()) {
  	       localStorage.setItem('tim_last_url', '/' + TIM.pageInfo.authorName + "#" + featureName + (path || ""));
  	    }
  	    
  	    if(!feature) {
  	      console.log('no feature');
  	      if(featureName == "logout" && parsedUri.path == "/settings") {
  	        location.href = "/settings";
    	      localStorage.removeItem('tim_last_url');
    	      return;
  	      }
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
  	          TIM.app.navigate(TIM.features.getSelectedFeature().get('name'), {replace:true});
  	          return;
  	      } else {
  	        feature = TIM.features.getByName("cover");
  	        TIM.app.navigate("cover", {replace:true});
  	      }
  	      resourceId = undefined;
  	    }
  	    $('#app').removeClass('nav-open nav-hidden');
  	    if (feature.behavior) {
  	        console.log('********* feature already loaded: activating  ********* (feature, path)', feature, path);
            feature.behavior.activate(path);
            TIM.features.setSelectedFeature(feature); //this should be a callback from the feature when it's been activated?
        } else {
          feature.loadFeature(path);
          TIM.features.setSelectedFeature(feature);
        }
      } else {
        console.log('hash change info did not start with route:');
      }
  };
  
  TIM.loadSettings = function() {
    if(TIM.authenticatedUser && TIM.authenticatedUser.loggedIn) {
      TIM.showSettingsPage();
    } else {
      TIM.showLoginForm();
    }
  }
  
  TIM.showErrorMessage = function (options) {
    TIM.setLoading(false);
    if (!TIM.errorMessageView) {
      TIM.errorMessageView = new TIM.views.ErrorMessage();
    }
    TIM.errorMessageView.render({message: options.exception});
    TIM.setErrorShowing(true);
  };
  
  TIM.showFlashMessage = function (options) {
    TIM.setLoading(false);
    if (!TIM.flashMessageView) {
      TIM.flashMessageView = new TIM.views.FlashMessage();
    }
    TIM.flashMessageView.render({message: options.text});
    TIM.setFlashMessageShowing(true);
  };
  
  TIM.showLoginForm = function (options) {
    TIM.setLoading(false);
    if (!TIM.loginView) {
      TIM.loginView = new TIM.views.Login({model: TIM.authenticatedUser});
    }
    TIM.loginView.render({message: "dam"});
    TIM.setNavVisible(false);
    TIM.app.navigate("#login");
    TIM.transitionPage (TIM.loginView.$el);
  };
  
  TIM.cancelLogin = function (options) {
    if(TIM.isAuthorApp()) {
      TIM.app.navigate("#cover", {trigger: true});
    } else {
      window.location.href = "/";
    }
    TIM.setNavVisible(true);
  };
  
  TIM.doLogout = function() {
    TIM.authenticatedUser.doLogout(function() { TIM.app.navigate('home', {trigger:true})});
  }
  

  TIM.showSettingsPage = function (options) {
    options = options || {};
    
    //make sure we have the current user's features and services loaded before displaying the page
    function showView() {
      if(!TIM.currentUserServices.initialized || !TIM.currentUserFeatures.initialized) {
        return;
      }
      TIM.setLoading(false);
      if (!TIM.settingsView) {
        TIM.settingsView = new TIM.views.Settings(
            { collection: TIM.allServices, 
              userCollection: TIM.currentUserServices,
              featureCollection: TIM.allFeatures,
              userFeatureCollection: TIM.currentUserFeatures
            }
        );
      }
      TIM.settingsView.render({message: ""});
      TIM.setNavVisible(false);
      if(!options.noHashChange) {
        TIM.app.navigate("#settings");
      }
      TIM.transitionPage (TIM.settingsView.$el);
    }
    
    function loadResources() {
      if (!TIM.currentUserServices.initialized) {
        TIM.fetchCurrentUserServices({callback:showView});
      }
      if (!TIM.currentUserFeatures.initialized) {
        TIM.fetchCurrentUserFeatures({callback:showView});
      }
    }
    
    if(TIM.currentUserServices.initialized && TIM.currentUserFeatures.initialized) {
      showView();
    } else {
      loadResources();
    }
    
  };
  
  TIM.showNewUserForm = function (options) {
    TIM.setLoading(false);
    if (!TIM.newUserView) {
      TIM.newUserView = new TIM.views.CreateUser();
    }
    TIM.newUserView.render({message: ""});
    TIM.setNavVisible(false);
    TIM.app.navigate("#login");
    TIM.transitionPage (TIM.newUserView.$el);
  };
  
  //
  //for now this simply handles the DOM page transition
  //
  //
  
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
	  
	  //there might not be a 'from page' if this is the first page we're loading
	  if (fromPage) {
	    //animationComplete binds a one-time handler for when the animation of the element is complete
	    fromPage.removeClass('in reverse ' + transitions)
	            .addClass(outClasses)
	            .addClass('active')
	            .animationComplete(function() {
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
	  
	  toPage.removeClass('out reverse')
	        .addClass(inClasses);
	  
    toPage.addClass('active')
        .animationComplete(function() {
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
	
	//
	//this is where we are sending all click/tap events for <a> tags
	//normalize the URL to trigger the proper hash change?
	//
	
	TIM.handleLinkClick = function (event) {
	  event.preventDefault();
	  var el = event.currentTarget;
	  
	  //first look at data attribute of element
	  var url = el.data && el.data("url") || (el.hash || el.pathname);
	  TIM.app.navigate(url, {trigger: true});
	}
	
	localStorage.removeItem('tim_last_url'); //this is used for saving to homescreen demo purposes
	
	//if the user's trying to go directly to the settings page, prevent them if not authenticated
	if(parsedUri.path === '/settings' || TIM.pageInfo.intendedPath === 'settings') {
	  if(!TIM.authenticatedUser.loggedIn) {
	    TIM.showLoginForm();
	    return;
	  }
	  TIM.setLoading(true);
	  TIM.showSettingsPage({noHashChange:true});
	}
	
	//show an error message if there's one present in the page (provided by the server-side page template)
	if(TIM.errorInfo && TIM.errorInfo !== '') {
	  TIM.showErrorMessage({exception: TIM.errorInfo});
	}

	
});
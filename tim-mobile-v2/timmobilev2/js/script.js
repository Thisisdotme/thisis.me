
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
TIM.currentPageElem = $('#splashScreen');
TIM.previousPageElem = undefined;
TIM.appContainerElem = $('#contentContainer');
TIM.defaultTransition = "fade";
TIM.isLoading = false;

TIM.apiUrl = TIM.globals.apiBaseURL + "/v1/";

$(function() {
  
  //set up global event dispatcher
	TIM.eventAggregator =  _.extend({}, Backbone.Events);
  
  //if there's no author, don't do anything!
  if(!TIM.pageInfo || !TIM.pageInfo.authorName || TIM.pageInfo.authorName === '') {
    return;
  }
  
  //move things like this to a utils object?
  function reorient(e) {
      var portrait = (window.orientation % 180 == 0);
      //get new window dimensions
      var height =  $(window).height(),
          width =  $(window).width();
      //don't bother for desktop sizes!
      if (height > 600) return;
      $("#app").css("min-height", height);
      $("#app").css("width", width);
  }
  window.onorientationchange = reorient;
  window.setTimeout(reorient, 0);
  
  
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
	  TIM.isLoading = loading;
	  if(loading) {
	    $('#app').addClass('loading');
	  } else {
	    $('#app').removeClass('loading');
	  }
	}
	
	TIM.setLoading(true);
	
	//collection of features for this author
	TIM.features = new TIM.collections.Features;
	
	//set up the main feature nav
	TIM.featureNavView = new TIM.views.FeatureNav({
	  collection: TIM.features
	})

	TIM.defaultFeature = "cover";
	
	//fetch the features for this author on load
	//use a JSONP plugin that properly reports errors?
	TIM.features.fetch({
		dataType: "jsonp",
		//add this timeout in case call fails...
		timeout : 10000,
		success: function(resp) {
		  console.log('fetched features');
		},
		error: function(resp) {
			TIM.appContainerElem.html("loading features failed for " + TIM.pageInfo.authorName + ". perhaps this author doesn't exist?");
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
    	
    	//move these to backbone views?
    	//make sure we have vclick event
    	
    	$('#navToggle').click(function(event){
    	  event.preventDefault();
    	  event.stopPropagation();
    	  $('#app').toggleClass('navOpen');
    	  //$('#featureNav').toggleClass('active');
    	});
    	
    	$('#app').click(function(event){
    	  event.preventDefault();
    	  //$('#featureNav').removeClass('active');
    	})
    	
    	$('#app').on('click', 'a', function(event) {
    	  event.preventDefault();
    	  TIM.handleLinkClick(event);
    	})
    },
  
    //should probably pass an option here of whether to 'activate' the feature
    featureLoaded: function(options) {
      console.log("Feature loaded callback: ", options);
      var feature = options.feature, resourceId = options.resourceId, navigate = options.navigateOnLoad;
      if(navigate) {
        feature.behavior.activate(resourceId);
        TIM.eventAggregator.trigger('featureselected', feature); //to select the menu item?
      }
    },
    
    //should probably pass an option here of whether to 'activate' the feature
    featureLoadError: function(options) {
      console.log("Feature loaded failed: ", options);
      alert("feature load failed!");
      TIM.setLoading(false);
    },
  
    featureNavRendered: function(){
      //features will have 
      //TIM.features.last().loadFeature();
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
	
	//move this to some sort of plugin?
	$.fn.animationComplete = function( callback ) {
		if( $.support.cssTransitions ) {
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
	
	TIM.app.bind('all', function(route, resourceId) {
	    
	    // the 'route' argument will be in the form "route:featurename"
	    
	    console.log('hash change event: ', arguments);
	    
	    if(route.split(':')[0] === 'route') {
	      
  	    var featureName = route.split(':')[1]; //assuming the hash will start with the feature name
  	    var feature = TIM.features.getByName(featureName);
  	    
  	    if (TIM.features.getSelectedFeature()) {
  	      $('#app').addClass('loading'); //make this a method on TIM
  	    }
  	    
  	    if(!feature) {
  	      console.log('no feature');
  	      //we get here if there was no feature in the URL
  	      //stay on the current feature if there is one, or else go to the cover page
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
  	    
  	    if (feature.behavior) {
  	        console.log('********* activating feature *********', resourceId);
            feature.behavior.activate(resourceId);
            TIM.features.setSelectedFeature(feature); //this should be a callback from the feature when it's been activated?
        } else {
          feature.loadFeature(resourceId);
          TIM.features.setSelectedFeature(feature);
        }
      }
  });
  
  //do transition between pages?
  //this is going to have to evolve to be something much more like what jquery mobile does with 'changePage'
  //for now this simply handles the DOM page transition
  
	TIM.transitionPage = function (toPage, options) {
	  $('#app').removeClass('loading initializing navOpen');
	  options = options || {};
	  var fromPage = options.fromPage || TIM.currentPageElem;
	  
	  //only do transition if necessary - if the from and to page are the same, just return
	  
	  console.log('transitioning: ', toPage, fromPage, toPage.is(fromPage));
	  
	  if(toPage.is(fromPage) && !options.transitionSamePage) {
	    return;
	  }
	  
	  //$('#app').removeClass('navOpen'); //hide the main feature nav - make this a TIM method?
	 
	  var animationName = options.animationName || TIM.defaultTransition; //changed from slide
	  
	  //fromPage.removeClass("slide fade");
	  var inClasses = "active in " + animationName;
	  var outClasses = "active out " + animationName;
	  if(options.reverse) {
	    inClasses += " reverse";
	    outClasses += " reverse";
	  } 
	  $('#app').addClass('transitioning'); //make this a TIM method?
	  if (fromPage) {
	    //animationComplete binds a one-time handler for when the animation of the element is complete
	    fromPage.removeClass('in reverse slide fade flip').addClass(outClasses).animationComplete(function() {
	      $(this).removeClass(outClasses + " slide fade flip");
	      $('#app').removeClass('transitioning');
	      if(options.callback) {
	        options.callback();
	      }
	    });
	  }
	  toPage.removeClass('out reverse').addClass(inClasses).animationComplete(function() {
      $(this).removeClass("slide fade flip");
      $('#app').removeClass('transitioning');
    });
	  TIM.currentPageElem = toPage;
	  TIM.previousPageElem = fromPage;
	};
	
	//this is where we are sending all click/tap events for <a> tags
	//normalize the URL to trigger the proper hash change?
	//
	
	TIM.handleLinkClick = function (event) {
	  event.preventDefault();
	  var el = event.currentTarget;
	  //window._el = el;
	  //return;
	  //everything after the first slash?
	  //this probably needs to be something more intelligent with scary regular expressions!
	  
	  var url = el.data && el.data("url") || (el.hash || el.pathname);
	  console.log(url);
	  TIM.app.navigate(url, {trigger: true});
	}
	
});
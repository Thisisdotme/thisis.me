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
TIM.appContainerElem = $('#contentContainer');

TIM.apiUrl = TIM.globals.apiBaseURL + "/v1/";

$(function() {
  //if there's no author, don't do anything!
  if(!TIM.pageInfo || !TIM.pageInfo.authorName || TIM.pageInfo.authorName === '') {
    return;
  }
  
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
	
	//alert($(window).width() + " " + $(window).height());
	
	//set up global event dispatcher
	TIM.eventDispatcher =  _.extend({}, Backbone.Events);
		
	TIM.features = new TIM.collections.Features;
	
	TIM.featureNavView = new TIM.views.FeatureNav({
	  collection: TIM.features
	})

	TIM.defaultFeature = "cover";
	//fetch the features for this author on load
	TIM.features.fetch({
		dataType: "jsonp",
		//add this timeout in case call fails...
		timeout : 5000,
		success: function(resp) {
		  //
		  console.log('fetched features');
		},
		error: function(resp) {
			TIM.appContainerElem.html("couldn't find author " + TIM.pageInfo.authorName);
		}
	});
	
	//1. get features for author
	//2. get cover page assets for author
		
  TIM.Router = Backbone.Router.extend({
	  
	  //dynamically inject routes & methods for features?
	  
	  //need an initial route or the history object won't start
	  routes: {
	        //setting these routes so that basically every hash change gets handled, whether there's a corresponding feature fo it or not
	        "*anything" : "catchAll",
	        "" : "catchAll"
        },

    initialize: function() {
          	
    	TIM.eventDispatcher.bind('featureloaded', this.featureLoaded, this);
    	TIM.eventDispatcher.bind('featurenavrendered', this.featureNavRendered, this);
    	TIM.eventDispatcher.bind('detailLinkClicked', this.detailLinkClicked, this);
    	//move these to backbone views?
    	//make sure we have vclick event
    	$('#navToggle').click(function(event){
    	  event.preventDefault();
    	  event.stopPropagation();
    	  $('#featureNav').toggleClass('active');
    	});
    	$('#app').click(function(event){
    	  event.preventDefault();
    	  $('#featureNav').removeClass('active');
    	})
    },
  
    //should probably pass an option here of whether to 'activate' the feature
    featureLoaded: function(options) {
      console.log("Feature loaded callback: ", options);
      var feature = options[0], resourceId = options[1];
      //var loadedFeature = feature.behavior;//TIM.loadedFeatures[feature.get('feature_name')];
      feature.behavior.activate(resourceId);
      TIM.eventDispatcher.trigger('featureselected', feature); //to select the menu item?
    },
  
    featureNavRendered: function(){
      //features will have 
      //TIM.features.last().loadFeature();
      var hash = window.location.hash;
      hash = hash || "cover";
      this.navigate('');
      console.log('featurenav loaded');
      this.navigate(hash, {'trigger': true}); //trigger a hashchange event
    },
  
    //this obviously needs to be more generalized
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
	
	
	//when any hash change event happens?
	//make sure menu item is selected
	TIM.app.bind('all', function(route, resourceId) {
	    // the 'route' argument is "route:featurename"
	    console.log('hash change event: ', arguments);
	    if(route.split(':')[0] === 'route') {
  	    var featureName = route.split(':')[1];
  	    var feature = TIM.features.getByName(featureName);
  	    if (TIM.features.getSelectedFeature()) {
  	      $('#app').addClass('loading');
  	    }
  	    if(!feature) {
  	      console.log('no feature');
  	      //stay on the current feature if there is one, or else go to the coeve page
  	      if(TIM.features.getSelectedFeature()) {
  	          $('#app').removeClass('loading');
  	          return;
  	      } else {
  	        feature = TIM.features.getByName("cover");
  	      }
  	      resourceId = undefined;
  	    } else if (feature.behavior) {
            feature.behavior.activate(resourceId);
            TIM.features.setSelectedFeature(feature);
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
	  $('#app').removeClass('loading initializing');
	  options = options || {};
	  var fromPage = options.fromPage || TIM.currentPageElem;
	  //only do transition if necessary
	  console.log('transitioning: ', toPage, fromPage, toPage.is(fromPage));
	  if(toPage.is(fromPage) && !options.transitionSamePage) {
	    return;
	  }
	  $('#featureNav').removeClass('active'); //hide the main feature nav
	 
	  var animationName = options.animationName || "fade"; //changed from slide
	  
	  //fromPage.removeClass("slide fade");
	  var inClasses = "active in " + animationName;
	  var outClasses = "active out " + animationName;
	  if(options.reverse) {
	    inClasses += " reverse";
	    outClasses += " reverse";
	  } 
	  $('#app').addClass('transitioning');
	  if (fromPage) {
	    //animationComplete binds a one-time handler for when the animation of the element is complete
	    fromPage.removeClass('in reverse slide fade').addClass(outClasses).animationComplete(function() {
	      $(this).removeClass(outClasses + " slide fade");
	      $('#app').removeClass('transitioning');
	    });
	  }
	  toPage.removeClass('out reverse').addClass(inClasses).animationComplete(function() {
      $(this).removeClass("slide fade");
      $('#app').removeClass('transitioning');
    });
	  TIM.currentPageElem = toPage;
	};
	
});
window.TIM = TIM || {};
TIM.routers = TIM.routers || {};
TIM.models = TIM.models || {};
TIM.collections = TIM.collections || {};
TIM.views = TIM.views || {};
TIM.featureHandlers = TIM.featureHandlers || {};
TIM.loadedFeatures = TIM.loadedFeatures || {};

//TIM.apiUrl = "http://10.0.1.8:6543/v1/";
TIM.apiUrl = TIM.globals.apiBaseURL + "/v1/";

$(function() {
	document.ontouchmove = function(e) {e.preventDefault()};
	
	//set up global event dispatcher
	TIM.eventDispatcher =  _.extend({}, Backbone.Events);
	
	//initially load author info
	//cover info
	
	TIM.features = new TIM.collections.Features;
	
	TIM.featureNavView = new TIM.views.FeatureNav({
	  collection: TIM.features
	})
	
	console.log('fetching features');
	TIM.defaultFeature = "cover";
	
	TIM.features.fetch({
		dataType: "jsonp",
		success: function(resp) {
		  //
		},
		error: function(resp) {
			
		}
	});
	
	
	
	//1. get features for author
	//2. get cover page assets for author
		
  TIM.Router = Backbone.Router.extend({
	  
	  //dynamically inject routes & methods for features?
	  
	  routes: {
            "": "coverPage"
        },

        initialize: function() {

            var self = this;

            // Keep track of the history of pages (we only store the page URL). Used to identify the direction
            // (left or right) of the sliding transition between pages.
            this.pageHistory = [];
            
            this.actions = [];
            /*
            
            $('#featureNav').on('click', function(event) {
                if (TIM.featureHandlers.Highlights) {
                  self.navigate('/highlights', {trigger: true});
                } else {
                  self.loadFeature('highlights');
                }
                return false;
            });
            
            */

            //this.allAuthors = new TIM.collections.Authors;
          	//this.myTimeline = new TIM.collections.Timeline;
          	//this.profiles = new TIM.collections.Profiles;
          	//this.authorList = new TIM.views.AuthorList({collection: this.allAuthors});
          	//this.timelineView = new TIM.views.EventList({collection: this.myTimeline});
          	
          	TIM.eventDispatcher.bind('featureloaded', this.featureLoaded, this);
        },

        coverPage: function() {
          console.log('coverPage!');
        },
        
        eventFeature: function() {
          alert('event feature!');
        },
        
        loadFeature: function(name) {
          var self = this;
          //load the appropriate scripts, templates?
          //move this to the feature model
          //load the list of features on startup, initialize them...
          $.getScript("/loree/asset/highlights.behavior.js", function(data, textStatus, jqxhr) {
             TIM.loadedModel = new TIM.models.TestNewModel();
             self.actions.push(TIM.featureHandlers[name]);
             console.log('history before: ', Backbone.history.handlers);
             self.route(name, name, function(){ TIM.featureHandlers.Highlights(); });
             console.log('history after: ', Backbone.history.handlers);
             //add route?
             
          });
        },
        
        
        highlightFeature: function() {
          var self = this;
          //load the appropriate scripts, templates?
          this.route('highlight2', 'highlight2', function(){ alert('new action!!')  });
          console.log(Backbone.history);
          //
          TIM.timelineView = new TIM.views.EventList({collection: this.myTimeline});
          TIM.appView = new TIM.views.App();
        	TIM.appView.loadEvents();
        	
        },
        
        featureLoaded: function(feature) {
          var loadedFeature = TIM.loadedFeatures[feature.get('feature_name')];
          loadedFeature.activate();
          //console.log('feature loaded: ', TIM.loadedFeatures[feature.get('feature_name')]);
        }
        
	})
	TIM.app = new TIM.Router();
  Backbone.history.start({root: '/' + TIM.globals.authorName + '/'});
	
	var allAuthors = new (TIM.collections.Authors);
	//var myTimeline = new (TIM.collections.Timeline);
	var profiles = new TIM.collections.Profiles;
	
	
	//var authorList = new TIM.views.AuthorList({collection: allAuthors})
	//var timelineView = new TIM.views.EventList({collection: myTimeline})
	
	//TIM.authorList = authorList;
	//TIM.myTimeline = myTimeline;
	//TIM.timelineView = timelineView;
	
	/*
	TIM.profile = new TIM.models.Profile({authorName: 'loree'});
	TIM.profile.fetch();
	TIM.profiles = profiles;
	*/
	
	
	
});
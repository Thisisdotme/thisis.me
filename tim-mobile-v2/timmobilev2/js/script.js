window.TIM = TIM || {};
TIM.routers = TIM.routers || {};
TIM.models = TIM.models || {};
TIM.collections = TIM.collections || {};
TIM.views = TIM.views || {};
//TIM.apiUrl = "http://10.0.1.8:6543/v1/";
TIM.apiUrl = TIM.globals.apiBaseURL + "/v1/";

$(function() {
	document.ontouchmove = function(e) {e.preventDefault()};
	
	//initially load author info
	//cover info
	
	TIM.features = new TIM.collections.Features;
	
	//1. get features for author
	//2. get cover page assets for author
		
  TIM.Router = Backbone.Router.extend({
	  
	  //dynamically inject routes & methods for features?
	  
	  routes: {
            "": "coverPage",
            "events": "eventFeature",
            "highlights": "highlightFeature"
        },

        initialize: function() {

            var self = this;

            // Keep track of the history of pages (we only store the page URL). Used to identify the direction
            // (left or right) of the sliding transition between pages.
            this.pageHistory = [];

            // Register event listener for back button troughout the app
            $('#featureNav').on('click', function(event) {
                alert('feature nav!');
                return false;
            });

            // We keep a single instance of the SearchPage and its associated Employee collection throughout the app
            this.allAuthors = new TIM.collections.Authors;
          	this.myTimeline = new TIM.collections.Timeline;
          	this.profiles = new TIM.collections.Profiles;
          	this.authorList = new TIM.views.AuthorList({collection: this.allAuthors})
          	this.timelineView = new TIM.views.EventList({collection: this.myTimeline})
        },

        coverPage: function() {
          console.log('coverPage!');
        },
        
        eventFeature: function() {
          console.log('event feature!');
        },
        
        highlightFeature: function() {
          console.log('highlight feature!');
        }
	  
	  
	})
	
	TIM.app = new TIM.Router();
  Backbone.history.start();
	
	var allAuthors = new (TIM.collections.Authors);
	var myTimeline = new (TIM.collections.Timeline);
	var profiles = new TIM.collections.Profiles;
	var authorList = new TIM.views.AuthorList({collection: allAuthors})
	var timelineView = new TIM.views.EventList({collection: myTimeline})
	
	TIM.authorList = authorList;
	TIM.myTimeline = myTimeline;
	TIM.timelineView = timelineView;
	TIM.appView = new TIM.views.App();
	TIM.appView.loadEvents();
	/*
	TIM.profile = new TIM.models.Profile({authorName: 'loree'});
	TIM.profile.fetch();
	TIM.profiles = profiles;
	*/
	
	
	
});
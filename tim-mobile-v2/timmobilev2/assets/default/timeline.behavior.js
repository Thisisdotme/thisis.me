//behavior would specify transition info?

(function(TIM) {
  var feature = {};
  feature.models = {};
  feature.views = {};
  feature.collections = {};
  feature.showDetailView = false;
  feature.collectionInitialized = false;
  feature.showDetailView = false;
  feature.showDetailId = 0;
  feature.path = "/timeline/";
  feature.detailCache = {};
  
  TIM.models.Event = Backbone.Model.extend({

    defaults: {
			time_ago: ""
    },

    initialize: function() {
			//not sure this would be the right place to do this...
			this.set("time_ago", $.timeago(new Date(this.get("create_time") * 1000)));
			//this.set("time_ago", '1 day');
    },
	
    clear: function() {
      this.destroy();
      this.view.remove();
    }

  });
  
  TIM.models.EventDetail = Backbone.Model.extend({
    
    urlRoot: TIM.apiUrl + 'authors/' + TIM.pageInfo.authorName + '/events',
    
    defaults: {
    },

    initialize: function() {
			//not sure this would be the right place to do this...
			//this.set("time_ago", $.timeago(new Date(this.get("create_time") * 1000)));
			this.set("time_ago", '1 day');
    },
	
    clear: function() {
      this.destroy();
      this.view.remove();
    },
    
    parse: function(resp) {
		  return (resp.event);
		}

  });

  TIM.collections.Events = Backbone.Collection.extend({
  		//setting which subclass the model is here?  not sure if this is necessary....
  	 	model: function(attrs) {
  			switch(attrs.feature) {
           case "linkedin":
             return new TIM.models.Event(attrs);
             break;
           default:
             return new TIM.models.Event(attrs);
         }
  		},
  		
  		url: TIM.apiUrl + 'authors/' + TIM.pageInfo.authorName + '/events?callback=?',
  		
  		initialize: function() {
  		   _.extend(this, TIM.mixins.paging);  //give this collection the ability to page
    		 this.initializePaging();
  		},
  		
  		//could also subclass in parse?
  		parse: function(resp) {
  		  return (resp.events);
  		}

  });
  
  //is this view just a page of 1-3 events?  ...with appropriate templating based on the number of events in its 'collection'?

  TIM.views.EventList = Backbone.View.extend( {
      id: "timeline",
      className: "flippage flippage-container app-page light",   
      pageTemplate: "event",
      
      initialize: function() {
          //add flipset functionality to this view
          _.extend(this, TIM.mixins.flipset);
          this.initializeFlipset();
          
          _.bindAll(this, "render", "renderPage");
          
  				//collection fires 'reset' event when fetch is complete
          this.collection.bind( "reset", this.render );
      },

  		events: {
  			//"click .event" : "showDetailView"
  		},

      render: function() {
        //mixing in FlipSet functionality to this view, so the main purpose of 'render' is to render the flipset
        this.renderFlipSet();
        //go straight to the detail view if we got here from an external link to a story
        //change this to more like what the photo feature does...
        
        if(feature.showDetails) {
          feature.showDetailView();
          feature.showDetails = false;
        } else {
          TIM.transitionPage ($(this.el));
        }
      },
      
      showDetailView: function(event) {
  		  if (event) {
  		    console.log('detail click event: ', event);
  		    var detailId = $(event.currentTarget).data('event_id');
  		    feature.showDetailId = detailId;
  		    TIM.app.navigate(feature.path + detailId, {'trigger': true});
  		  }
      }

  } );
  
   
  TIM.views.EventDetail = Backbone.View.extend( {
      id: "event-detail-container",

      className: "app-page",

      initialize: function(spec) {
        _.bindAll(this);
        //this thing below is repeated all over the place...
        if(TIM.appContainerElem.find(this.el).length == 0)  {
          TIM.appContainerElem.append(this.$el);
        }
        this.model.bind( "change", this.render );	
    		
      },

      events: {
        "swiperight" : "showListView"
      },

      render: function( ) {
    	
      	var html = TIM.views.renderTemplate("eventDetail", this.model.toJSON());
        this.$el.html(html);
      
      },

      showListView: function(event) {
         feature.showDetails = false;
         TIM.app.navigate("/timeline");
         TIM.transitionPage($('#timeline'), {animationName: "slide", reverse: true});
      }

  } );
  
  //this should follow the /authorname/feature/detail_id pattern?
  feature.activate = function(resourceId) {
    if(resourceId) { 
      
      //turning off direct navigation to the 
      //go straight to detail view for this resource...
      //actually we want to just go to the proper location in the timeline
      //load collection first?
      feature.showDetails = true;
      feature.showDetailId = resourceId;
    }
    //only fetch timeline, create view, etc. if need be...
    feature.mainCollection = feature.mainCollection || new (TIM.collections.Events);
    feature.timelineView = feature.timelineView || new TIM.views.EventList({collection: feature.mainCollection});
  
    if(!feature.collectionInitialized) {
      feature.mainCollection.fetch({
  			dataType: "jsonp",
  			success: function(resp) {
			    feature.collectionInitialized = true;
  			},
  			error: function(resp) {
				
  			}
  		});
  	} else {
  	  if (feature.showDetails) {
  	    feature.showDetailView(resourceId);
  	  } else {
  	    TIM.transitionPage (feature.timelineView.$el);
  	  }
  	}
  };
  
  //maybe have methods to show detail view, show list view, show grid view?
  //instead of drilling in, at this point...
  //at the very least, go to the correct spot in the flipset
  
  feature.showDetailView = function(resourceId) {
    //do this or else should have the detail view fetch the model?
    //cache models that have already been fetched?
    var pageNum = 1;
    resourceId = resourceId || feature.showDetailId;
    
    console.log('showing detail view for timeline: ', resourceId, feature.mainCollection);
    
    feature.detailView = feature.detailView || new TIM.views.EventDetail({
      model: new TIM.models.EventDetail({
        id: resourceId
      })
    });
    
    var model = feature.detailCache['' + resourceId];
    
	  if(model) {
	    console.log('have a model for the detail');
	    feature.detailView.model = model;
		  feature.detailView.render();
		  //TIM.transitionPage (feature.detailView.$el, {"animationName":"slide"});
		  
		  TIM.transitionPage (feature.timelineView.$el, {"animationName":"slide"});
		  //figure out which page the event is on!
      pageNum = feature.findPageForEvent(resourceId);          
      feature.timelineView.goToPage(pageNum);
		  
		  feature.showDetailsId = 0;
		  feature.showDetails = false;
		} else {
		  //fetch the model from the server
		  	  
		  feature.detailView.model = new TIM.models.EventDetail({id: resourceId});
		  feature.detailView.model.fetch({
		    dataType: "jsonp",
		    success: function(model, response) {
          console.log('fetched model: ', model);
          feature.detailView.render();
          //TIM.transitionPage (feature.detailView.$el, {"animationName":"slide"});
          
          TIM.transitionPage (feature.timelineView.$el, {"animationName":"slide"});
          
          //figure out which page the event is on!
          pageNum = feature.findPageForEvent(resourceId);          
          feature.timelineView.goToPage(pageNum);
          
          feature.detailCache['' + resourceId] = model; //so we don't have to get the same details twice
		    }
		  });
		}
  }
  
  feature.findPageForEvent = function(eventId) {
    var pageNum = 1;
    for(var i = 0; i < feature.timelineView.pages.length; i++) {
      var page = feature.timelineView.pages[i];
      for(var j = 0; j < page.events.length; j++) {
        console.log(page.events[j], eventId);
        if (page.events[j].id == eventId) {
          pageNum = i + 1;
        }
      }
    }
    return pageNum;
  }
  
  //add to feature?
  TIM.features.getByName("timeline").behavior = feature;
  
  TIM.loadedFeatures["timeline"] = feature;
  
})(TIM);

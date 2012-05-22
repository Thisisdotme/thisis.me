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

  feature.models.Timeline = TIM.models.FeatureBehavior.extend({
    initialize: function() {
      this.constructor.__super__.initialize.apply(this, arguments);
    },
    // Default attributes 
    defaults: {
  		name: "timeline"
    },

    navigate: function() {
      TIM.app.navigate("/timeline");
    }

  });
  
  TIM.models.Event = Backbone.Model.extend({

    defaults: {
			time_ago: ""
    },

    initialize: function() {
			//not sure this would be the right place to do this...
			//this.set("time_ago", $.timeago(new Date(this.get("create_time") * 1000)));
			this.set("time_ago", '1 day');
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

  //should this collection have the equivalent of 'paging info', the 'flipset', etc.?
  //this should handle both highlights and regular events, right?

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
  		},
  		//could also subclass in parse?
  		parse: function(resp) {
  		  return (resp.events);
  		}

  });
  
  //is this view just a page of 1-3 events?  ...with appropriate templating based on the number of events in its 'collection'?

  TIM.views.EventList = Backbone.View.extend( {
      id: "timeline",
      className: "flippage flippage-container appPage",   
      pageTemplate: "event",
      
      initialize: function() {
          //add flipset functionality to this view
          _.extend(this, TIM.mixins.flipset);
          this.initializeFlipset();
          
          _.bindAll(this, "render", "renderPage");
          
  				//collection fires 'reset' event when fetch is complete
  				//should collection have methods to get newer and older events so we don't have to get all at once?
  				//is this the right place to have all this info?
          this.collection.bind( "reset", this.render );
      },

  		events: {
  			//"swipeup .flip-set" : "flipNext",
  			//  "swipedown .flip-set" : "flipPrevious",
  			// "click .event" : "showDetail",
  			"click .event" : "showDetailView"
  		},

      render: function() {
        //mixing in FlipSet functionality to this view, so the main purpose of 'render' is to render the flipset
        this.renderFlipSet();
        //go straight to the detail view if we got here from an external link to a story
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
        id: "eventDetailContainer",

        className: "appPage",

        initialize: function(spec) {
           _.bindAll(this);
           if(TIM.appContainerElem.find(this.el).length == 0)  {
        		  TIM.appContainerElem.append(this.$el);
        		}
        	this.model.bind( "change", this.render );	
        		
        },

        events: {
          "swiperight" : "showListView"
        },

        render: function( ) {
        	var that = this;
        	dust.render("eventDetail", this.model.toJSON(), function(err, out) {
        	  if(err != null) {
        			console.log(err);
        		}
        	  $(that.el).html(out);
        	  //alert('detail rendered!');
        	});	
        },

        showListView: function(event) {
           feature.showDetails = false;
           TIM.app.navigate("/timeline");
           TIM.transitionPage($('#timeline'), {animationName: "slide", reverse: true});
        }

   } );
  
  feature.model = new feature.models.Timeline();
  
  feature.activate = function(resourceId) {
    console.log('activating timeline with resource ID: ', resourceId);
    if(resourceId) {
      //go straight to detail view for this resource...
      //load collection first?
      feature.showDetails = true;
      feature.showDetailId = resourceId;
    }
    //only fetch timeline, create view, etc. if need be...
    feature.mainCollection = feature.mainCollection || new (TIM.collections.Events);
    feature.timelineView = feature.timelineView || new TIM.views.EventList({collection: feature.mainCollection});
    //feature.gridView = feature.gridView || new TIM.views.HighlightGrid({collection: feature.myTimeline});
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
  	  //feature.gridView.render();
  	  //feature.timelineView.render();
  	  if (feature.showDetails) {
  	    //TIM.transitionPage ($("#detailContainer"));
  	    //feature.timelineView.showDetail();
  	    feature.showDetailView(resourceId);
  	  } else {
  	    //feature.timelineView.showDetail();
  	    TIM.transitionPage (feature.timelineView.$el);
  	  }
  	}
  };
  
  //maybe have methods to show detail view, show list view, show grid view?
  feature.showDetailView = function(resourceId) {
    //do this or else should have the detail view fetch the model?
    //cache models that have already been fetched?
    resourceId = resourceId || feature.showDetailId;
    console.log('showing detail view for timeline: ', resourceId, feature.mainCollection);
    
    feature.detailView = feature.detailView || new TIM.views.EventDetail({
      model: new TIM.models.EventDetail({
        id: resourceId
      })
    });
    
    var model = feature.detailCache['' + resourceId];//feature.mainCollection.find(function(model){return model.get('event_id') == resourceId});
    
	  if(model) {
	    console.log('have a model for the detail');
	    feature.detailView.model = model;
		  feature.detailView.render();
		  TIM.transitionPage (feature.detailView.$el, {"animationName":"slide"});
		  feature.showDetailsId = 0;
		  feature.showDetails = false;
		} else {
		  //fetch the model from the server
		  
		  console.log('FETCHING DETAILLLLL!!!!!!');
		  
		  feature.detailView.model = new TIM.models.EventDetail({id: resourceId});
		  feature.detailView.model.fetch({
		    dataType: "jsonp",
		    success: function(model, response) {
          console.log('fetched model: ', model);
          feature.detailView.render();
          TIM.transitionPage (feature.detailView.$el, {"animationName":"slide"});
          feature.detailCache['' + resourceId] = model;
		    }
		  });
		}
  }
  
  //add to feature?
  TIM.features.getByName("timeline").behavior = feature;
  
  TIM.loadedFeatures["timeline"] = feature;
  
})(TIM);

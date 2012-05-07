//behavior would specify transition info?

(function(TIM) {
  var feature = {};
  feature.models = {};
  feature.views = {};
  feature.collections = {};
  feature.showDetailView = false;
  feature.hasFetchedCollection = false;
  feature.showDetailView = false;
  feature.showDetailId = 0;
  
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

    //show?  

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
      
      initialize: function() {
          _.bindAll(this, "render", "renderPage");
  				//collection fires 'reset' event when fetch is complete
  				//should collection have methods to get newer and older events so we don't have to get all at once?
  				//is this the right place to have all this info?
          this.collection.bind( "reset", this.render );
      },

  		events: {
  			"swipeup .flip-set" : "flipNext",
  			"swipedown .flip-set" : "flipPrevious",
  			//"click .event" : "showDetail",
  			"swipeleft .event" : "showDetail"
  		},

      render: function() {
        //mixing in FlipSet functionality to this view, so the main purpose of 'render' is to render the flipset
        this.renderFlipSet();
        
        //go straight to the detail view if we got here from an external link to a story
        if(feature.showDetailView) {
          this.showDetail();
          feature.showDetailView = false;
        } else {
          TIM.transitionPage ($(this.el));
        }
      },
      
      showDetail: function(event) {
  		  if (event) {
  		    console.log('detail click event: ', event);
  		    feature.showDetailId = $(event.currentTarget).data('event_id');
  		    //event.stopPropagation();
  		  }
  		  var model = this.collection.find(function(model){return model.get('event_id') == feature.showDetailId})
  		  if(model) {
  		    console.log('have a model for the detail');
  		    feature.detailView.model = model;
    		  feature.detailView.render();
    		  TIM.transitionPage ($('#eventDetailContainer'), {"animationName":"slide"});
    		} else {
    		  console.log("can't find a model for the detail");
    		  TIM.transitionPage (this.$el, {"animationName":"fade"});
    		}
      }

  } );
  
  //add flipset functionality to the Highlight list view
   _.extend(TIM.views.EventList.prototype, TIM.mixins.flipset);
   
   TIM.views.EventDetail = Backbone.View.extend( {
       id: "eventDetailContainer",

       className: "appPage",

       initialize: function(spec) {
           _.bindAll(this);
           if(TIM.appContainerElem.find(this.el).length == 0)  {
     			  TIM.appContainerElem.append(this.$el);
     			}
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
   			});	
       },

       showListView: function(event) {
         feature.showDetailView = false;
         TIM.app.navigate("/timeline");
         TIM.transitionPage($('#timeline'), {animationName: "slide", reverse: true});
       }

   } );
  
  feature.model = new feature.models.Timeline();
  
  feature.activate = function(resourceId) {
    
    console.log('activating timeline: ', resourceId);
    if(resourceId) {
      //go straight to detail view for this resource...
      //load collection first?
      feature.showDetailView = true;
      feature.showDetailId = resourceId;
    }
    
    //only fetch timeline, create view, etc. if need be...
    feature.eventCollection = feature.eventCollection || new (TIM.collections.Events);
    feature.timelineView = feature.timelineView || new TIM.views.EventList({collection: feature.eventCollection});
    
    var myTimeline = new (TIM.collections.Events);
    feature.timelineView || new TIM.views.EventList({collection: myTimeline});
    feature.detailView = feature.detailView || new TIM.views.EventDetail();
    
    if(!feature.hasFetchedCollection) {
      feature.timelineView.collection.fetch({
  			dataType: "jsonp",
  			success: function(resp) {
			    feature.hasFetchedCollection = true;
  			},
  			error: function(resp) {
				
  			}
  		});
  	} else {
  	  if (feature.showDetailView) {
  	    //TIM.transitionPage ($("#detailContainer"));
  	    feature.timelineView.showDetail();
  	  } else {
  	    //feature.timelineView.showDetail();
  	    TIM.transitionPage (feature.timelineView.$el);
  	  }
  	}
		
  };
  
  feature.navigate = function() {
    TIM.app.navigate("/timeline");
  }
  
  //add to feature?
  TIM.features.getByName("timeline").behavior = feature;
  
  TIM.loadedFeatures["timeline"] = feature;
  
})(TIM);

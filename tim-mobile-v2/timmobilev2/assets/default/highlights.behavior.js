//view?

//collection?

//object holding all views, models & collections that drive the feature
//add route & navigate?
//send app event saying 'hey, i've loaded, navigate and run me!'
//

(function(TIM) {
  var feature = {};
  feature.models = {};
  feature.views = {};
  feature.collections = {};
  feature.hasFetchedCollection = false;
  feature.showDetailView = false;
  feature.showDetailId = 0;

  feature.models.Highlights = TIM.models.FeatureBehavior.extend({
    initialize: function() {
      this.constructor.__super__.initialize.apply(this, arguments);
    },
    // Default attributes 
    defaults: {
  		name: "highlights"
    },

    navigate: function(resourceId) {
      
      TIM.app.navigate("/highlights" + (resourceId ? '/' + resourceId : ''));
    }

    //show?  

  });
  
  TIM.models.Highlight = Backbone.Model.extend({

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

  TIM.collections.Highlights = Backbone.Collection.extend({
  		//setting which subclass the model is here?  not sure if this is necessary....
  	 	model: function(attrs) {
  			switch(attrs.feature) {
           case "linkedin":
             return new TIM.models.Highlight(attrs);
             break;
           default:
             return new TIM.models.Highlight(attrs);
         }
  		},
  		url: TIM.apiUrl + 'authors/' + TIM.pageInfo.authorName + '/highlights?callback=?',
  		initialize: function() {
  		},
  		//could also subclass in parse?
  		parse: function(resp) {
  		  return (resp.events);
  		}

  });
  
  //is this view just a page of 1-3 events?  ...with appropriate templating based on the number of events in its 'collection'?

  TIM.views.HighlightList = Backbone.View.extend( {
      id: "highlights",
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
  			"swipeleft .event" : "showDetail"
  		},
      
      render: function() {
        //mixing in FlipSet functionality to this view, so the main purpose of 'render' is to render the flipset
        this.renderFlipSet();
        
        //go straight to the detail view if we got here from an external link to a story
        if(feature.showDetailView) {
          feature.showDetailViewFn();
          feature.showDetailView = false;
        } else {
          TIM.transitionPage ($(this.el));
        }
      },
    
  		showDetail: function(event) {
  		  if (event) {
  		    console.log('detail click event: ', event);
  		    var detailId = $(event.currentTarget).data('event_id');
  		    feature.showDetailId = detailId;
  		    TIM.app.navigate("/highlights/" + detailId, {'trigger': true});
  		  }
  		  /*
  		  var model = this.collection.find(function(model){return model.get('event_id') == feature.showDetailId})
  		  if(model) {
  		    console.log('have a model for the detail');
  		    feature.detailView.model = model;
    		  feature.detailView.render();
    		  TIM.transitionPage ($('#detailContainer'), {"animationName":"slide"});
    		} else {
    		  console.log("can't find a model for the detail");
    		  //go staight to the list view
    		  TIM.transitionPage (this.$el, {"animationName":"fade"});
    		} */
  		} 

  } );
  
  //add flipset functionality to the Highlight list view
  _.extend(TIM.views.HighlightList.prototype, TIM.mixins.flipset);
  
  TIM.views.HighlightDetail = Backbone.View.extend( {
      id: "detailContainer",
      
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
  			dust.render("highlightDetail", this.model.toJSON(), function(err, out) {
  			  if(err != null) {
  					console.log(err);
  				}
  			  $(that.el).html(out);
  			});	
      },
      
      showListView: function(event) {
        feature.showDetailView = false;
        TIM.app.navigate("/highlights");
        TIM.transitionPage($('#highlights'), {animationName: "slide", reverse: true});
      }
      
  } );
  
  TIM.views.HighlightGrid = Backbone.View.extend( {
      el: "#gridContainer",
      
      initialize: function(spec) {
          _.bindAll(this);
          
          this.collection.bind( "reset", this.render );
      },
      
      events: {
  			"click .item" : "showDetail"
  		},

      render: function( ) {
  			var that = this;
  			dust.render("highlightGrid", {}, function(err, out) {
  			  if(err != null) {
  					console.log(err);
  				}
  			  $(that.el).html(out).removeClass("out").addClass("in");
  			  $('#highlights').removeClass("in").addClass("out");
  			});	
      },
      
      showListView: function(event) {
        alert("list time!");
      },
      
      showDetail: function(event) {
        alert("show details!");
      }
      
  } );
  
  feature.model = new feature.models.Highlights();
  
  //features have an 'activate' method that is called to navigate to & show that feature
  
  feature.activate = function(resourceId) {
    console.log('activating highlights: ', resourceId);
    if(resourceId) {
      //go straight to detail view for this resource...
      //load collection first?
      feature.showDetailView = true;
      feature.showDetailId = resourceId;
    }
    //only fetch timeline, create view, etc. if need be...
    feature.highlightCollection = feature.highlightCollection || new (TIM.collections.Highlights);
    feature.timelineView = feature.timelineView || new TIM.views.HighlightList({collection: feature.highlightCollection});
    //feature.gridView = feature.gridView || new TIM.views.HighlightGrid({collection: feature.myTimeline});
    feature.detailView = feature.detailView || new TIM.views.HighlightDetail();
    if(!feature.hasFetchedCollection) {
      feature.highlightCollection.fetch({
  			dataType: "jsonp",
  			success: function(resp) {
			    feature.hasFetchedCollection = true;
  			},
  			error: function(resp) {
				
  			}
  		});
  	} else {
  	  //feature.gridView.render();
  	  //feature.timelineView.render();
  	  if (feature.showDetailView) {
  	    //TIM.transitionPage ($("#detailContainer"));
  	    //feature.timelineView.showDetail();
  	    feature.showDetailViewFn(resourceId);
  	  } else {
  	    //feature.timelineView.showDetail();
  	    TIM.transitionPage (feature.timelineView.$el);
  	  }
  	}
  };
  
  //maybe have methods to show detail view, show list view, show grid view?
  feature.showDetailViewFn = function(resourceId) {
    //do this or else should have the detail view fetch the model?
    //cache models that have already been fetched?
    console.log(feature.highlightCollection);
    resourceId = resourceId || feature.showDetailId;
    var model = feature.highlightCollection.find(function(model){return model.get('event_id') == resourceId});
	  if(model) {
	    console.log('have a model for the detail');
	    feature.detailView.model = model;
		  feature.detailView.render();
		  TIM.transitionPage ($('#detailContainer'), {"animationName":"slide"});
		  feature.showDetailsId = 0;
		  feature.showDetailView = false;
		} else {
		  console.log("can't find a model for the detail");
		  //go staight to the list view
		  //TIM.transitionPage (this.$el, {"animationName":"fade"});
		}
  }
  
  feature.navigate = function(resourceId) {
    console.log('navigate called on highlights feature!');
    /// TIM.app.navigate("/highlights");
  }
  
  //add to feature?
  TIM.features.getByName("highlights").behavior = feature;
  TIM.loadedFeatures["highlights"] = feature;
  
})(TIM);






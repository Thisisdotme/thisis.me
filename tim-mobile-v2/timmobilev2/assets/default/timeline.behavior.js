
(function(TIM) {
  console.log('tim: ', TIM);
  var feature = {};
  feature.models = {};
  feature.views = {};
  feature.collections = {};
  
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
      el: $( "#timeline" ),

      initialize: function() {
          _.bindAll(this, "render", "renderPage");
  				//collection fires 'reset' event when fetch is complete
  				//should collection have methods to get newer and older events so we don't have to get all at once?
  				//is this the right place to have all this info?
          this.collection.bind( "reset", this.render );
  				this.pageNum = 0;
  				this.pages = [];
  				this.flipSet = {};
  				this.flipSetInitialized = false;
  				this.chunkSize = 4;
  				this.renderedIndex = 0;
      },

  		events: {
  			"swipeup .flip-set" : "flipNext",
  			"swipedown .flip-set" : "flipPrevious"
  		},

  		renderPage: function(page){

  				//send pages, which can be 1-3 events to the event View
  		    var pageView = new TIM.views.EventPage({page: page});
          pageView.render();

  				if (!this.flipSetInitialized) {
  					this.flipSet = new FlipSet($(this.el), 320, 370, [$(pageView.el)]);
  					console.log(this);
  					this.flipSetInitialized = true;
  				} else {
  					this.flipSet.push($(pageView.el));
  				}
      },

      render: function(){
  			//make pages here?  let's try it!!
  			this.pages = [];
  			var self = this;
  			var page = [];

  			//make page objects with either 1 or 2 events
  			//if the event has a photo, it takes a full page
  			//otherwise, stuff 2 events in a page

  			//should a 'page' be a backbone model?
  			//have a collection of pages?

  			//modify this so it doesn't skip too many non-photo events if there's a long series of photo events

  			//only do this a little bit at a time?

  			//store whether an event has been added to a page?

  			this.collection.each(function(item) {
  				if(item.get("content").photo_url !== undefined) {
  					self.pages.push({"events" : [item.toJSON()]});
  				} else {
  					page.push(item);
  					if(page.length == 2) {
  						self.pages.push({"events" : [page[0].toJSON(), page[1].toJSON()]});
  						page = [];
  					}
  				}
  			});

  			//rather than rendering all pages at once, make it intelligent?
  			this.renderPageChunk(0);
  			this.renderPageNum();
  			return this;
      },

  		renderPageChunk: function(start) {

  			//would this fn check for earlier/later events if they haven't been loaded?

  			var end = start + this.chunkSize;
  			if (end > this.pages.length) {
  				end = this.pages.length;
  			}
  			for (var i = start; i < end; i++) {
  				this.renderPage(this.pages[i]);
  				this.renderedIndex++;
  			}
  		},

  		renderPageNum: function() {
  			$('#pageNum').html(this.pageNum + 1);
  		},

  		//should these get the next or previous page & render if necessary?
  		//rather than rendering all the pages upon fetch/collection refresh

  		//

  		flipNext: function(){
  			//$.mobile.silentScroll(0);
  			//check if there are more pages to go
  			//if they've been rendered

  			//prerender 2 pages in advance?
  			if(this.pageNum == (this.renderedIndex - 2)) {
  				this.renderPageChunk(this.renderedIndex);
  			}
  			console.log(this);
  			if (this.flipSet.canGoNext()) {
  				this.flipSet.next(function(){});
  				this.pageNum++;
  				this.renderPageNum();
  			}
  		},

  		flipPrevious: function(){
  			//$.mobile.silentScroll(0);

  			if (this.pageNum == 0) {
  				//check for newer events at this point?
  				//poll for newer events?
  			} 

  			if (this.flipSet.canGoPrevious()) {
  				this.flipSet.previous(function(){});
  				this.pageNum--;
  				this.renderPageNum();
  			}
  		}

  } );

  TIM.views.EventPage = Backbone.View.extend( {

      initialize: function(spec) {
          _.bindAll(this, "render");
  				this.page = spec.page;
      },

      render: function( ) {
  			var that = this;
  			var tmpl = this.page.events.length === 1 ? "event" : "page";
  			dust.render(tmpl, this.page, function(err, out) {
  			  if(err != null) {
  					console.log(err);
  				}
  			  $(that.el).append(out);
  			});	
      }
  } );
  
  feature.model = new feature.models.Timeline();
  
  feature.activate = function() {
    var myTimeline = new (TIM.collections.Events);
    var timelineView = new TIM.views.EventList({collection: myTimeline});
    timelineView.collection.fetch({
			dataType: "jsonp",
			success: function(resp) {
			  
			},
			error: function(resp) {
				
			}
		});
  };
  
  TIM.loadedFeatures["timeline"] = feature;
  
})(TIM);

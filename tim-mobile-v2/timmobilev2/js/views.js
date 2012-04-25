//use this to control the main ap view
TIM.views.App = Backbone.View.extend( {
    el: $( "#app_container" ),
		
		events: {
        "click #fetch_authors" : "loadAuthors",
				"click #fetch_events" : "loadEvents"
    },

    initialize: function() {
        
    },
		
		loadAuthors: function() {
			TIM.authorList.collection.fetch({
				dataType: "jsonp"
			});
		},
		
		loadEvents: function() {
			TIM.timelineView.collection.fetch({
				dataType: "jsonp",
				success: function(resp) {
				  
				},
				error: function(resp) {
					
				}
			});
		}

} );

TIM.views.FeatureNav = Backbone.View.extend( {
   //
})

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
			"swipedown .flip-set" : "flipPrevious",
			"vclick .avatar" : "showProfile"
		},
		
		renderPage: function(page){
			
				//send pages, which can be 1-3 events to the event View
		    var pageView = new TIM.views.Page({page: page});
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
		},
		
		showProfile: function(event){
			var authorName = $(event.currentTarget).data("authorname");
			//look for this author in a collection first to prevent more requests?
			event.preventDefault();
			event.stopPropagation();
			
			
			var profile = TIM.profiles.find(function(profile) {
			  return profile.get("authorName") === authorName;
			})
			
			if (profile) {
				profile.set("reloading", true);
			} else {
				profile = new TIM.models.Profile({authorName: authorName});
				TIM.profiles.add(profile);
				var profView = new TIM.views.Profile({model: profile});
				profile.fetch();
			}
		}
		
} );

TIM.views.Page = Backbone.View.extend( {
    
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

TIM.views.Event = Backbone.View.extend( {

    initialize: function() {
        _.bindAll(this, "render");
        //this.collection.bind( "add", this.addOne );
    },

    render: function( ) {
			var that = this;
			dust.render("event", this.model.toJSON(), function(err, out) {
			  if(err != null) {
			    console.log(err);
			  }
			  $(that.el).append(out);
			});
				
    }
} );

TIM.views.AuthorList = Backbone.View.extend( {
    el: $( "#author_list" ),

    initialize: function() {
        _.bindAll(this, "renderList");
        this.collection.bind( "reset", this.renderList );
    },

    renderList: function( collection ) {
				var that = this;
				
				$(this.el).html('');
				_.each(collection.models, function(model) {
					dust.render("author", model.toJSON(), function(err, out) {
					  if(err != null) {
					    console.log(err);
						}
					  $(that.el).append(out);
					});
				})
        
    }
} );

TIM.views.Profile = Backbone.View.extend( {
    el: $( "#profile_dialog" ),

		model: TIM.models.Profile,
		
		events: {
			'swiperight': 'goBack'
		},

    initialize: function(spec) {
        _.bindAll(this, "render");
				this.model.on('change', this.render, this);
    },

    render: function( ) {
			//toggling this so we will trigger the change event
			//this.model.set("reloading", false);
			console.log('rendering profile!');
			var that = this;
			dust.render("profile", this.model.toJSON(), function(err, out) {
			  if(err != null) {
			    console.log(err);
				}
			  $(that.el).find('.profile_content').html(out);
			});
			//$.mobile.changePage($(this.el));
    },

		goBack: function() {
			history.back();
			return false;
		}
} );

/*
TIM.views.AuthorView = Backbone.View.extend( {
    
		model: TIM.models.Author,

    initialize: function() {
        _.bindAll(this, "render");
    },

    render: function(  ) {
				var that = this;
        dust.render("author", this.toJSON(), function(err, out) {
				  if(err != null)
				    alert("Error loading page");
				  //assume we have jquery
				  $(that.el).html(out);
				});
    }
} );
*/
//extending backbone view object to allow for DOM removal & event unbinding in one call
//see http://lostechies.com/derickbailey/2011/09/15/zombies-run-managing-page-transitions-in-backbone-apps/
Backbone.View.prototype.close = function(){
  this.remove();
  this.unbind();
  if (this.onClose){
    this.onClose();
  }
}

TIM.views.FeatureNav = Backbone.View.extend( {
   el: $( "#featureNavItems" ),
		
   initialize: function() {
       this.collection.bind( "reset", this.render, this );
       TIM.eventAggregator.bind('featureselected', this.highlightSelectedNavItem, this);
   },
   
   addAll : function () {
      this.collection.each (this.addOne);
      //notify the app that the feature nav has been rendered
      TIM.eventAggregator.trigger('featurenavrendered', this);
   },
		
  addOne : function ( item ) {
  	var view = new TIM.views.FeatureViewItem({model:item});
  	$( "#featureNavItems" ).append(view.render().el);
  },

  render: function() {
   this.addAll();
  },

 	highlightSelectedNavItem: function(selectedFeature) {
 	  this.collection.each (function(feature) {
 	    if (feature.get('feature_name') == selectedFeature.get('feature_name')) {
 	      feature.set('selected', true);
 	    } else {
 	      feature.set('selected', false);
 	    }
 	    //console.log(feature);
 	  });
 	  $("#featureNav").removeClass('active');
 	}
})

TIM.views.FeatureViewItem = Backbone.View.extend({
	tagName : 'li',

	initialize: function() {
		this.model.bind('change', this.render, this);
		this.model.bind('destroy', this.remove, this);
		this.model.bind('loaded', this.featureLoaded, this);
	},
	
	events: {
		"vclick" : "loadFeature"
	},

	render : function () {
	  var self = this;
	  var selected = this.model.get('selected');
	  //console.log('rendering menu item');
	  dust.render("featureNavItem", this.model.toJSON(), function(err, out) {
		  if(err != null) {
				console.log(err);
			}
		  $(self.el).html(out).removeClass('selected').addClass(selected ? 'selected' : '');
		});
		return this;
	},
	
	loadFeature : function() {
	  if(this.$el.hasClass('selected')) {
	    return;
	  }
	  TIM.app.navigate(this.model.get('feature_name'), {trigger: true});
	},
	
	featureLoaded: function() {
	  //alert('the view knows the feature is loaded!!!!!!!!');
	}
	
});

//toolbar triggers events on its parent view?
TIM.views.Toolbar = Backbone.View.extend( {
        
    className: "toolbar",
    
    template: "toolbar",
    
    events: {
      "click span" : "itemClicked"
    },
    
    items:[ 
      {name: 'gridLink'},
      {name: 'detailLink'}
    ],
    
    initialize: function(spec) {
        spec = spec || {};
        _.bindAll(this);
    },
    
    render: function() {
      var that = this;
      dust.render(this.template, {items:this.items}, function(err, out) {
  		  if(err != null) {
  				console.log(err);
  			}
  		  that.$el.html(out);
  		});
  		return this.$el;
    },
    
    //parent views probably shouldn't rely on this event, but you never know
    //maybe broadcast it app-wide?
    
    itemClicked: function(event) {
      var item = event.currentTarget;//event.data('name')
      //console.log(event, item);
      this.trigger('itemClicked', $(item).data('toolbar-item'));
    }
    
} );

//this view is used by the flipset mixin
//do we need to have a view at all?
//maybe to include a toolbar?

TIM.views.Page = Backbone.View.extend( {
    
    className: "page",
    
    initialize: function(spec) {
        _.bindAll(this, "render");
				this.pages = spec.pages;
    },

    render: function( tmpl, callback ) {
			var that = this;
			//console.log("pages: ", this.pages);
			tmpl = tmpl || "event";//(this.page.events.length === 1 ? "event" : "page");
			dust.render(tmpl, this.pages[0], function(err, out) {
			  if(err != null) {
			    callback(err);
					console.log(err);
				} else{
				  callback(out);
				}
			});	
    }
} );

//should probably have some sort of function that does the template rendering 
//to prevent lots of code copying and pasting

//an attempt to define the flipset functionality as a mixin

//key is the 'pages' array... it's different than underlying event/photo/etc collection in that there can be multiple items on a page

TIM.mixins.flipset = {
		
		//resetFlipSet: function() {
		  //flipSet: {},
  		//flipSetInitialized: false,
  		//chunkSize: 4,
  		//renderedIndex: 0,
		//},
		initializeFlipset: function() {
		  var that = this;
      this.pageNum = 0;
  		this.pages = [];
  		this.flipSet = {};
  		this.flipSetInitialized = false;
  		this.chunkSize = 50;
  		this.renderedIndex = 0;
  		this.numResourcesRendered = 0;
  		this.flipMode = true;
		},
		
		//send pages to the flips script one at a time as strings?
		renderPage: function(pages){
        //console.log('in render page!, pages: ', pages);
  			//send pages, which can be 1-3 events to the event View
		    var pageView = new TIM.views.Page({pages: pages});
		    var tmpl = this.pageTemplate;
		    var that = this;
		    
        pageView.render(tmpl, function(pageHtml){
          if (!that.flipSetInitialized) {
  					//this.flipSet = new Flipset($(this.el), 320, 370, [$(pageView.el)]);
  					
  					that.flipSet = new Flipset({containerEl: $(that.el), pages: [pageHtml], parentView: that});
  					window.flipSet = that.flipSet; //for debugging
  					//console.log("hey, here's teh pageview elem", $(pageView.el, pageView.el));
  					//var flip = this.$el.flips({pages:$(pageView.el, pageView.el)});
  					//this.$el.flips("addPage", pageView.$el);
  					that.flipSetInitialized = true;
  				} else {
  					that.flipSet.addSourceItem(pageHtml);
  				}
        });
        

    },
    
    //
    
    renderFlipSet: function(options){
			//make pages here?  let's try it!!
			options = options || {};
			console.log("rendering flipset, options: ", options);
			var startIndex = this.numResourcesRendered;
			this.pages = this.pages || [];
			var self = this;
			var page = [];
			var itemJSON;
			this.renderedIndex = this.renderedIndex || 0;
			this.flipSetInitialized = this.flipSetInitialized || false;

			//make page objects with either 1 or 2 events
			//if the event has a photo, it takes a full page
			//otherwise, stuff 2 events in a page

			//should a 'page' be a backbone model?
			//have a collection of pages?

			//modify this so it doesn't skip too many non-photo events if there's a long series of photo events

			//only do this a little bit at a time?

			//store whether an event has been added to a page?
			
			this.collection.each(function(item, index) {
			  //console.log(index, startIndex);
			  if(index < startIndex) return;
			  itemJSON = item.toJSON();
			  if(options.pageMetaData) {
			    
			  }
			  //this is very dependent on the old structure of the data
			  
				if(item.get('title') !== undefined || item.get("content").photo_url !== undefined) {
					self.pages.push({num: index+1, options: options, "event_class" : "full-page", "events" : [itemJSON]});
				} else {
					page.push(item);
					if(page.length == 2) {
						self.pages.push({"event_class" : "half-page", "events" : [page[0].toJSON(), page[1].toJSON()]});
						page = [];
					}
				}
				self.numResourcesRendered++;
			});
			
			//if there's one left over, make a page of it!
			if(page.length == 1) {
			  self.pages.push({"event_class" : "full-page", "events" : [page[0].toJSON()]});
			}
      
			//rather than rendering all pages at once, make it intelligent?
			
			if(startIndex == 0) {
			  this.$el.html(''); //if this if the first time rendering this flipset, make sure its element is empty
			}
			this.renderPageChunk(this.renderedIndex);
			
			if(TIM.appContainerElem.find(this.el).length == 0)  {
			  TIM.appContainerElem.append(this.$el);
			}
			//console.log("flipset: ", this.flipSet);
			return this;
    },
    
		renderPageChunk: function(start) {
			//would this fn check for earlier/later events if they haven't been loaded?
			
      var that = this;
			var end = start + this.chunkSize;
			if (end > this.pages.length) {
				end = this.pages.length;
			}
			for (var i = start; i < end; i++) {
			  //if(end - i > 2) {
			  //  this.renderPage([this.pages[i], this.pages[++i]]);
			   // i += 2;
  			//	this.renderedIndex += 2;
			 // } else {
			   //console.log('calling render page');
			    this.renderPage([this.pages[i]]);
  				this.renderedIndex++;
  				//that.flipSet._addPage();
			  //}
			}
			console.log('in render page chunk starting with ', start);
			//have to know how to remove the last (2?) page(s) from teh flipset & insert starting there..
			that.flipSet._createPageElements();
		},
		
		flipNext: function(){
			
			var that = this;
			//prerendering 3 pages & sending to flipset
			//we always want to have this many pages available to teh flipset because it needs to have as many as 4 pages in the DOM at one time
			
			if(this.pageNum == (this.renderedIndex - 3)) {
				this.renderPageChunk(this.renderedIndex);
			}
			
			if (this.pageNum < this.collection.length - 2) {
				this.pageNum++;
			} else {
			  
			  if($('#app').hasClass('loading') || this.collection.getNextPage === undefined) {
			    return;
			  }
			  this.collection.getNextPage();
			  this.pageNum++;
			}
		},

		flipPrevious: function(){
			//$.mobile.silentScroll(0);
			//window.scrollTo( 0, 1 );

			if (this.pageNum == 0) {
				//check for newer events at this point?
				//do a 'get previous page' call, as in 
			} 

			if (true || this.flipSet.canGoPrevious()) {
				//this.flipSet.previous(function(){});
				this.pageNum--;
			}
		},
		
		goToPage: function(num){
			
			this.pageNum = 0;
			
			//make sure pages are rendered before trying to go to that page
			
			for(var i = 0; i < num; i++) {
		    //prerender 2 pages in advance?
  			if(this.pageNum == (this.renderedIndex - 2)) {
  				this.renderPageChunk(this.renderedIndex);
  			}
  			this.pageNum++;
  		}
  	
  		this.flipSet._gotoPage(num);
  		
		},
		
		pageChanged: function (num) {
		  
		}
}


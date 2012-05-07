TIM.views.FeatureNav = Backbone.View.extend( {
   el: $( "#featureNavItems" ),
		
   initialize: function() {
       this.collection.bind( "reset", this.render, this );
       TIM.eventDispatcher.bind('featureselected', this.highlightSelectedNavItem, this);
   },
   
   addAll : function () {
      this.collection.each (this.addOne);
      //load the default feature here?
      //..or navigate?
      //send an app event?
      TIM.eventDispatcher.trigger('featurenavrendered', this);
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
		"click" : "loadFeature"
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
	  //this.model.loadFeature();
	  TIM.app.navigate(this.model.get('feature_name'), {trigger: true});
	},
	
	featureLoaded: function() {
	  //alert('the view knows the feature is loaded!!!!!!!!');
	}
	
});

//this view is used by the flipset mixin

TIM.views.Page = Backbone.View.extend( {

    initialize: function(spec) {
        _.bindAll(this, "render");
				this.page = spec.page;
    },

    render: function( tmpl ) {
			var that = this;
			tmpl = tmpl || (this.page.events.length === 1 ? "event" : "page");
			dust.render(tmpl, this.page, function(err, out) {
			  if(err != null) {
					console.log(err);
				}
			  $(that.el).append(out);
			});	
    }
} );

//an attempt to define the flipset functionality as a mixin

TIM.mixins.flipset = {
  	pageNum: 0,
		pages: [],
		flipSet: {},
		flipSetInitialized: false,
		chunkSize: 4,
		renderedIndex: 0,
		
		//resetFlipSet: function() {
		  //flipSet: {},
  		//flipSetInitialized: false,
  		//chunkSize: 4,
  		//renderedIndex: 0,
		//},
		
		renderPage: function(page){

  			//send pages, which can be 1-3 events to the event View
		    var pageView = new TIM.views.Page({page: page});
		    var tmpl = this.pageTemplate;
        pageView.render(tmpl);

				if (!this.flipSetInitialized) {
					this.flipSet = new FlipSet($(this.el), 320, 370, [$(pageView.el)]);
					this.flipSetInitialized = true;
				} else {
					this.flipSet.push($(pageView.el));
				}
    },

    renderFlipSet: function(){
			//make pages here?  let's try it!!
			this.pages = [];
			var self = this;
			var page = [];
			this.renderedIndex = 0;
			this.flipSetInitialized = false;

			//make page objects with either 1 or 2 events
			//if the event has a photo, it takes a full page
			//otherwise, stuff 2 events in a page

			//should a 'page' be a backbone model?
			//have a collection of pages?

			//modify this so it doesn't skip too many non-photo events if there's a long series of photo events

			//only do this a little bit at a time?

			//store whether an event has been added to a page?
      //console.log('rendering highlight view', this);
			this.collection.each(function(item) {
				if(item.get('caption') !== undefined || item.get("content").photo_url !== undefined) {
					self.pages.push({"events" : [item.toJSON()]});
				} else {
					page.push(item);
					if(page.length == 2) {
						self.pages.push({"events" : [page[0].toJSON(), page[1].toJSON()]});
						page = [];
					}
				}
			});
			//if there's one left over, make a page of it!
			if(page.length == 1) {
			  self.pages.push({"events" : [page[0].toJSON()]});
			}
      
			//rather than rendering all pages at once, make it intelligent?
			this.$el.html('');
			this.renderPageChunk(0);
			
			if(TIM.appContainerElem.find(this.el).length == 0)  {
			  TIM.appContainerElem.append(this.$el);
			}
			
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
		
		flipNext: function(){
		  //$.mobile.silentScroll(0);
			window.scrollTo( 0, 1 );
			//check if there are more pages to go
			//if they've been rendered

			//prerender 2 pages in advance?
			if(this.pageNum == (this.renderedIndex - 2)) {
				this.renderPageChunk(this.renderedIndex);
			}
			//console.log(this);
			if (this.flipSet.canGoNext()) {
				this.flipSet.next(function(){});
				this.pageNum++;
			}
		},

		flipPrevious: function(){
			//$.mobile.silentScroll(0);
			window.scrollTo( 0, 1 );

			if (this.pageNum == 0) {
				//check for newer events at this point?
				//poll for newer events?
			} 

			if (this.flipSet.canGoPrevious()) {
				this.flipSet.previous(function(){});
				this.pageNum--;
			}
		},
		
		goToPage: function(num){
			//$.mobile.silentScroll(0);
			window.scrollTo( 0, 1 );
			this.pageNum = 0;
			//console.log(this);
			for(var i = 0; i < num; i++) {
		    //prerender 2 pages in advance?
  			if(this.pageNum == (this.renderedIndex - 2)) {
  				this.renderPageChunk(this.renderedIndex);
  			}
  			this.pageNum++;
  		}
  		this.flipSet.currentIndex_ = this.pageNum;
  		this.flipSet.displayCurrentFlip_();
		}
}


/* flipboard functionality from blog post via Grio */

function FlipSet($wrapper, width, height, nodes) {
  this.flips_ = [];
  this.currentIndex_ = 0;
  this.width = width;
  this.height = height;

  for (var i = 0, node; node = nodes[i]; i++) {
  	this.flips_.push(new Flip(node, width, height, this));
  }
    
  this.containerNode_ = $("<div class='flip-set'/>");
  //trying out not-explicitly-sized flips
  this.containerNode_.css("width", '100%');
  this.containerNode_.css("height", '100%');
    
  this.displayCurrentFlip_();
  $wrapper.append(this.containerNode_);
} 

FlipSet.prototype.displayCurrentFlip_ = function() {
  this.containerNode_.empty();
  this.containerNode_.append(this.flips_[this.currentIndex_].originalNode_);
}

FlipSet.prototype.getCurrentIndex = function(node) {
	return this.currentIndex_;
}

FlipSet.prototype.push = function(node) {
	this.flips_.push(new Flip(node, this.width, this.height, this));
}

FlipSet.prototype.unshift = function(node) {
	this.flips_.unshift(new Flip(node, this.width, this.height, this));
    this.currentIndex_++;
}

FlipSet.prototype.getLength = function() {
	return this.flips_.length;
}

FlipSet.prototype.next = function(callback) {
  if (this.isTransitioning_) return;
  
  this.isTransitioning_ = true;
  var currentFlip = this.flips_[this.currentIndex_]
  var nextFlip = this.flips_[this.currentIndex_ + 1];
  
  currentFlip.beginFlipFrom();
  nextFlip.beginFlipTo();
  var self = this;
  nextFlip.immediate(nextFlip.foldBottom, function() {
    currentFlip.foldTop();
    nextFlip.unfold();
    currentFlip.moveToBack();
    nextFlip.onTransitionEnd(function() {
      nextFlip.endFlipTo();
      currentFlip.endFlipFrom();
      self.isTransitioning_ = false;
      callback();
    });
  });

  this.currentIndex_++;
};

FlipSet.prototype.previous = function(callback) {
  if (this.isTransitioning_) return;
  
  this.isTransitioning_ = true;
  var currentFlip = this.flips_[this.currentIndex_]
  var previousFlip = this.flips_[this.currentIndex_ - 1];
  
  currentFlip.beginFlipFrom();
  previousFlip.beginFlipTo();
  
  // Hack to make the lower part of the page appear
  var height = this.height; 
  //previousFlip.bottomInnerContainerNode_.css("top", "50%");//Math.floor(height/2) + 'px');
  //var t=setTimeout(function() {
  		//previousFlip.bottomInnerContainerNode_.css("top", "-50%");//-Math.floor(height/2) + 'px');
  	//}, 200);
  
  
  // currentFlip.bottomInnerContainerNode_.hide();
  var self = this;
  previousFlip.immediate(previousFlip.foldTop, function() {
  	currentFlip.foldBottom();
    previousFlip.unfold();
    currentFlip.moveToBack();
    previousFlip.onTransitionEnd(function() {
  	  currentFlip.bottomInnerContainerNode_.show();
      previousFlip.endFlipTo();
      currentFlip.endFlipFrom();
      self.isTransitioning_ = false;
      callback();
    });
  });	  
  
  this.currentIndex_--;
};

FlipSet.prototype.canGoNext = function() {
  return this.currentIndex_ < this.flips_.length - 1;
};

FlipSet.prototype.canGoPrevious = function() {
  return this.currentIndex_ > 0;
};

function Flip(node, width, height, parentSet) {
  this.originalNode_ = node;
  this.parentSet_ = parentSet;
  this.init_(width, height);
}

Flip.prototype.init_ = function(width, height) {
  this.originalNode_.css("height", "100%");
  var node = this.originalNode_;
  
  var containerNode = $("<div class='flip-container'/>");
  containerNode.css("width", "100%");
  containerNode.css("height", "100%");
  
  var topContainerNode = $("<div class='flip-top-container flip-transitionable'/>");
  topContainerNode.append(node.clone());
  topContainerNode.css("width", "100%");
  topContainerNode.css("height", "50%");
  //topContainerNode.find(".footer").css("bottom", -Math.floor(height/2) + 'px');
  
  var bottomContainerNode = $("<div class='flip-bottom-container flip-transitionable'/>");
  var bottomInnerContainerNode = $("<div class='flip-bottom-inner-container'/>");
  
  bottomInnerContainerNode.append(node.clone());
  bottomInnerContainerNode.css("height", "200%");

  bottomContainerNode.append(bottomInnerContainerNode);
  bottomContainerNode.css("height", "50%");
  bottomContainerNode.css("width", "100%");
  bottomInnerContainerNode.css("width", "100%");

  bottomInnerContainerNode.css("top", "-100%");
  
  containerNode.append(topContainerNode);
  containerNode.append(bottomContainerNode);
  
  this.containerNode_ = containerNode;
  this.topContainerNode_ = topContainerNode;
  this.bottomContainerNode_ = bottomContainerNode;
  this.bottomInnerContainerNode_ = bottomInnerContainerNode;
  
  
  var self = this;
  var onTransitionEnd = function() {
    if (self.onTransitionEnd_) {
      self.onTransitionEnd_();
      self.onTransitionEnd_ = null;
    }
  };
  
  try {
  	this.containerNode_.bind("webkitTransitionEnd", onTransitionEnd);
  } catch (err) {}
  
  try {
    // Should be mozTransitionEnd, but is transition end per 
    // https://developer.mozilla.org/en/CSS/CSS_transitions#Detecting_the_completion_of_a_transition
  	this.containerNode_.bind("transitionend", onTransitionEnd);
  } catch (err) {}
};

Flip.prototype.moveToFront = function() {
  this.containerNode_.css("z-index", 1);
};

Flip.prototype.moveToBack = function() {
   this.containerNode_.css("z-index", -1);
};

Flip.prototype.beginFlipFrom = function() {
  this.moveToFront();
  this.originalNode_.replaceWith(this.containerNode_);  
};

Flip.prototype.beginFlipTo = function() {
  this.parentSet_.containerNode_.append(this.containerNode_);
};

Flip.prototype.endFlipFrom = function() {
  //this.containerNode_.css("display", 'none').detach().css("display", 'block');
  this.containerNode_.detach();
  //this.containerNode_.css("display", 'block');
  this.containerNode_.css("z-index", 'auto');
};

Flip.prototype.endFlipTo = function() {
  this.containerNode_.parent().append(this.originalNode_);
  this.containerNode_.css("z-index", 'auto');
  //this.containerNode_.css("display", 'none').detach().css("display", 'block');
  this.containerNode_.detach();
  //this.containerNode_.css("display", 'block');
  this.containerNode_.css("z-index", 'auto');
};

Flip.prototype.immediate = function(method, callback) {
	this.topContainerNode_.removeClass('flip-transitionable');
	this.bottomContainerNode_.removeClass('flip-transitionable');
  
  method.call(this);
  
  var self = this;
  window.setTimeout(function() {
	self.topContainerNode_.addClass('flip-transitionable');
	self.bottomContainerNode_.addClass('flip-transitionable');
    
    callback();
  });
};

Flip.prototype.foldTop = function() {
  this.containerNode_.addClass('folded-top');
};

Flip.prototype.foldBottom = function(opt_immediate) {
  this.containerNode_.addClass('folded-bottom');
}

Flip.prototype.unfold = function(opt_immediate) {
  this.containerNode_.removeClass('folded-top');
  this.containerNode_.removeClass('folded-bottom');
}

Flip.prototype.onTransitionEnd = function(callback) {
  this.onTransitionEnd_ =callback;
};



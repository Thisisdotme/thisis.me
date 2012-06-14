/**
 * adapted from:
 *
 * jquery.flips.js
 * 
 * Copyright 2011, Pedro Botelho / Codrops
 * Free to use under the MIT license.
 *
 * Date: Fri May 4 2012
 */
 
 //get rid of History?
 //add ability to dynamically add pages
 //change to be vertical!
 
 //have vars for $prevPage, $nextPage, $currentPage
 

	var Flipset 			= function(options) {
	
		this.$el	= options.containerEl;
		this.$el.html(''); //clear out the container
		console.log("el: " , this.$el);
		this._init(options);
		
	};
	
  Flipset.defaults 	= {
		flipspeed			: 500,
		fliptimingfunction	: 'linear',
		current				: 1
	};
	
	Flipset.prototype 	= {
	  
	  //make init less 'comprehensive'
		_init 				: function(options) {
	
		  //the original raw event html pages that we use to make 'flip pages'
		  //this should just be the parent view's 'pages' array?
		  //have the parent view be responsible for rendering the pages, rather than this?
		  //..seems wasteful to keep this (potentially giant) array full of html strings...
		  
		  this.sourceItems = [];
		  
			this.options 		= $.extend(true, {}, Flipset.defaults, options);
			this.parentView = options.parentView;
			
			console.log("flipset parentview: ", this.parentView);
			
			this.loading = false; //flag for if the flipset is in the 'loading' state
			
			//DOM elements for previous, current, and next page
			this.$twoPagesPrevious = undefined;
			this.$previousPage = undefined;
			this.$currentPage = undefined;
			this.$nextPage = undefined;
			this.$loadingNext = undefined; //use for 'loading' message?
			this.$loadingPrevious = undefined; //use for 'loading' message?
			
			this.canGoNext = false;
			this.canGoPrev = false;
			
			//an array to hold the DOM objects
			this.$pageElements = [];
			
			for (var i = 0, page; i < options.pages.length; i++) {
       	page = options.pages[i]
       	this.addSourceItem(page, {skipLayout:true});
      }
			
			this.currentPage	= this.options.current || 1; //this keeps track of what page number we're on... 1-based, not 0-based
			
			this._getContainerSize();
			this._initTouchSwipe(); //this is ok - it's just on the container el
			
		},
		
		addSourceItem: function(elem, opts) {
		  opts = opts || {};
		  console.log('adding elem to source items');
		  if (opts && opts.addToStart) {
		    this.sourceItems.unshift(elem);
		  } else {
		    this.sourceItems.push(elem);
		  }
		  if (!opts.skipLayout) {
		    //this.createPageElements(); //layout puts the pages into the front/back divs and sets z-index
		  }
		},
		
		//trying out a 'partial flip' with a loading indicator
		//should let the user flip the page up to a certain level (40deg?), then stop...
		//
		//turnPage fn needs to be able to accept both an angle and a time...
		//for now, just have it flip up, stop for a couple of seconds, then flip back down?
		//
		//change text form 'loading' to 'no more items' for now?
		//
		//ok
		//yep
		//
		
		//turnpage needs to take a callback?
		//for end page flip transition?
		
		//in reality... maybe let the user drag out to something like 40deg, then prevent from dragging further while 'loading'
		//
		//as this is happening, tell the parent collection to get the next page...
		//
		//usually, we would 'fetch ahead' so that the user wouldn't get to this state often
		//
		//-let them 'undrag'/cancel the load
		//
		//need to be more closely coupled with the parent view/collection
		//when the parent collection is loaded... it either has more items, which triggers a render here & flips next/prev
		//or if it doesn't havne more items, the 'loading message' should say something like 'no more items' and flip back
		//
		//
		//should have some sort of global state where we're at the end or beginning of the collection
		//keeping track of page number
		//
		// collection length vs. view.numRendered
		//
		//
		// definitely a 'loading' state where flipping is not allowed
		
		testLoadingFlip: function () {
		  if (this.loading) {
		     this.loading = false;
    		 //this.$loadingNext.css('z-index',2);
    		 
    		 this._turnPage(0, false, 400);
		  } else {
		     this.loading = true;
    		 this._setFlippingPage(this.$currentPage);
    		 this.$loadingNext.css('z-index',4);
    		 this._turnPage(40, false, 400);
		  }
		 
		},
		
		testLoadingFlipPrev: function () {
		  if (this.loading) {
		     this.loading = false;
    		 //this.$loadingNext.css('z-index',2);
    		 //alert('unturning!!!!!!!!!');
    		 this._turnPage(179.999, false, 400);
		  } else {
		     this.loading = true;
    		 this._setFlippingPage (this.$previousPage);
    		 this.$loadingPrevious.css('z-index',4);
    		 this._turnPage(140, false, 400);
		  }
		 
		},
		
		//this gets the size of the flipset's container element
		_getContainerSize			: function() {
			
			var $win = this.$el;
			
			this.containerDimensions = {
				width	: $win.width(),
				height	: $win.height()
			};
		
		},
		
		//
		//adjustLayout makes sure the z-indexes and rotation of the current 4 DOM elements are correct
		//
		//do we need a fifth element in the case of a 'loading' message at the bottom when the user tries to page to a page beyon what's in the collection?
		//
		//
		
		_adjustLayout		: function(page) { //page is the index of... the current page
		  console.log("in adjust layout, current page is: ", this.currentPage);
		  
			var _self = this;
			
			if(this.$twoPagesPrevious) {
			  this.$twoPagesPrevious.css({
  				'-webkit-transform'	: 'rotateX(0deg)',
  				'-moz-transform'	: 'rotateX(0deg)',
  				'z-index'			: 1
  			});
			}
			
			this.$previousPage.css({
				'-webkit-transform'	: 'rotateX(180deg)',
				'-moz-transform'	: 'rotateX(180deg)',
				'z-index'			: 5
			});
			
			this.$currentPage.css({
				'-webkit-transform'	: 'rotateX(0deg)', 
				'-moz-transform'	: 'rotateX(0deg)',
				'z-index'			: 4
			});
			if (this.$nextPage) {
			  this.$nextPage.css({
  				'-webkit-transform'	: 'rotateX(0deg)',
  				'-moz-transform'	: 'rotateX(0deg)',
  				'z-index'			: 1
  			});
			}
	
		},
		
		//move this stuff up into the dust templates?
		//...except for the size css, which we could do with $.css
		//instead of going through all pages, do this through add...
		
		//when adding a new element
		//have to make sure the last page is a 'special'
		//
		// <front>lastPage</front>
		// <back>blank</back>
		//
		//
		
		createPageElements				: function() {
			var that = this;
			
			//don't loop through this necessarily - only do when necessary?
			var numExistingElems = this.$pageElements.length;
			var initializing = numExistingElems === 0;
			
			//always
			var begin = numExistingElems - 1;
			var end = this.sourceItems.length;
			
			if (initializing) {
			 
			} else {
			  this.$pageElements.pop(); //get rid of the 'special' last page that only the 'front' div populated
			  begin--;
			}
			
			//should this just do the full rendering of the initial event page, or at least tell the parent view to render it & use that html?
			//....probably the latter....
			
			for(var i = begin; i < end; i++) {
  			var	page 		= that.sourceItems[i] || "<span class='big-num'>" + i  + "</span>",
  			  nextPage = that.sourceItems[ i + 1 ] || "<div class='loading-next'>loading...</div>",
  				pageData	= {
  					frontContent			: page,
  					backContent			: nextPage,
  					zIndex : 0,
  					pageNum: i
  				};
			  var elem = this._renderDOMElem (pageData, i < 3);
			  //add first 3 page elems to the dom if initializing this flipset
	      if (initializing && i < 3) {
	        //elem.appendTo(this.$el);
	      }
	      this.$pageElements.push (elem);
  		}
  		if(initializing) {
  		  this._initDOMVars(this.currentPage);
  		  this._adjustLayout();
  		}
		},
		
		
		//make this FN actually add the DOM elements to the container
		//empty the container if anything's in there
		
		_initDOMVars: function (index) {
		  
		  index = index || this.currentPage;
		  this.$el.html(''); //empty the DOM container
		  
		  //elements for showing 'loading' message...
		  //need 2?  probably can get away with just one with content divs at the top and bottom
		  this.$loadingPrevious = $('<div class="loadingPrevious">loading...</div>');
		  this.$loadingNext = $('<div class="loadingNext">loading...</div>');
		  this.$el
	      .append(this.$loadingPrevious)
	      .append(this.$loadingNext);
		  
		  this.$twoPagesPrevious = this.$pageElements[index - 2] || undefined;
	    this.$previousPage = this.$pageElements[index - 1];
	    this.$currentPage = this.$pageElements[index];
	    this.$nextPage = this.$pageElements[index + 1] || undefined;
	    
	    if (this.$twoPagesPrevious) {
	      this.$el.append(this.$twoPagesPrevious);
	    }
	    this.$el
	      .append(this.$previousPage)
	      .append(this.$currentPage);
      if (this.$nextPage) {
	      this.$el.append(this.$nextPage);
	    }
		},
		
		_renderDOMElem:  function (pageData) {
		  var domElem, that = this;
		  
		  var html = TIM.views.renderTemplate("flipPage", pageData);
  		domElem = $(html);
		  
			return domElem;
		},
		
		_gotoPage: function (pageNum) {
		  this.currentPage = pageNum;
		  this._initDOMVars();
		  this._adjustLayout();
		},
		
		//updatePage keeps track of the 4 DOM nodes that we have in the document at any given time
		//
		//increments or decrement the 'currentPage' var
		//
		//should we throw up a special 'loading' next page if necessary?
		
		_updatePage			: function(direction) {
		  
		  direction = direction || this.flipDirection;
		  
		  if(direction === 'next') {
				++this.currentPage;
				this.parentView.flipNext();
				
				//detach pages not needed, (re)attach new pages that are needed
				if (this.$twoPagesPrevious) {
				  this.$twoPagesPrevious.remove();
				}
				console.log('flipping ot next page, ', this.currentPage);
				this.$currentPage = this.$pageElements[this.currentPage];
				this.$previousPage = this.$pageElements[this.currentPage - 1];
				this.$nextPage = this.$pageElements[this.currentPage + 1];
				this.$twoPagesPrevious = this.$pageElements[this.currentPage - 2];
				
				if (this.$nextPage) {
				  this.$nextPage.appendTo(this.$el).css('z-index', 0);
				} else {
				  console.log('next page not available, currentPage is ', this.currentPage);
				  //alert('no next page!');
				}
				
				
		  } else if(direction === 'prev') {
			  
				--this.currentPage;
				this.parentView.flipPrevious();
				
				if (this.$nextPage)
				  this.$nextPage.remove();
				
				this.$currentPage = this.$pageElements[this.currentPage];
				this.$previousPage = this.$pageElements[this.currentPage - 1];
				this.$nextPage = this.$pageElements[this.currentPage + 1];
				if(this.currentPage > 1) {
				  this.$twoPagesPrevious = this.$pageElements[this.currentPage - 2];
  				this.$twoPagesPrevious.prependTo(this.$el);
				} else {
				  this.$twoPagesPrevious = undefined;
				}
				
			} else { //no direction specified, but we still want to set the DOM elements
			  
			  	this.$currentPage = this.$pageElements[this.currentPage];
    			this.$previousPage = this.$pageElements[this.currentPage - 1];
    			this.$nextPage = this.$pageElements[this.currentPage + 1] || undefined;
    			this.$twoPagesPrevious = this.$pageElements[this.currentPage - 2] || undefined;
			}
						
		},
		
		//this is the big 'swipe' event handler
		//uses the jquery touchSwipe plugin...
		//possibly eventually move to our own touch event handling code
		//
		
		_initTouchSwipe		: function() {
			
			var _self = this;
			
			this.$el.swipe({
				threshold			: 0,
				allowPageScroll: "none",
				swipeStatus			: function(event, phase, start, end, direction, distance) {
				  //if view is not in flip mode, return
				  if(_self.parentView && !_self.parentView.flipMode) {
				    return;
				  }
					//get container size if it hasn't been set...
					if (_self.containerDimensions.height == 0) {
					  _self._getContainerSize();
					}
					
					var startY		= start.y,
						endY		= end.y,
						sym, angle,
						oob			= false,
						noflip		= false;
					
					// check the "page direction" to flip:
					// check only if not animating
					
					// note - this isn't how flipboard does it - they use the initial direction of the swipe
					if(!_self._isAnimating() && !_self.loading) {
						(startY < _self.containerDimensions.height / 2) ? _self.flipDirection = 'prev' : _self.flipDirection = 'next';
					}
					
					if(direction === 'left' || direction === 'right') {
						if(_self.angle === undefined || _self.angle === 0 || true) {	
							_self._removeOverlays();
							return false;	
						}
						else {			
							(_self.angle < 90) ? direction = 'up' : direction = 'down';							
						}
					};
					
					_self.swipeDirection = direction;
					
					// on the first & last page neighbors we don't flip
					// KL -we'll have a 'special' first page and last page that's never reachable!
					if(_self.flipDirection == 'prev' && !_self.$twoPagesPrevious) {
					  console.log("trying to go back too far!");
						return false;
					}
					
					if(_self.flipDirection == 'next' && !_self.$nextPage) {
					  console.log("no next page - try to queue it up");
					  var $newNext = _self.$pageElements[_self.currentPage + 1];
					  
					  if ($newNext) {
					    $newNext.appendTo(_self.$el).css('z-index', 0);
					    _self.$nextPage = $newNext;
					  } else {
					    //try the 'fake flip' here...
					    console.log("no new next: ", _self.currentPage);
					    _self.testLoadingFlip();
					    console.log("trying to go forward too far!");
					    return false;
					  }
					}
					
					// save ending point (symetric point):
					// if we touch / start dragging on, say [x=10], then
					// we need to drag until [window's width - 10] in order to flip the page 100%.
					// if the symetric point is too close we are giving some margin:
					// if we would start dragging right next to [window's width / 2] then
					// the symmetric point would be very close to the starting point. A very short swipe
					// would be enough to flip the page..
					sym	= _self.containerDimensions.height - startY;
					
					var symMargin = 0.9 * (_self.containerDimensions.height / 2);
					if(Math.abs(startY - sym) < symMargin) {
						(_self.flipDirection === 'next') ? sym -= symMargin / 2 : sym += symMargin / 2;
					}
					
					// some special cases:
					// Page is on the right side, 
					// and we drag/swipe to the same direction
					// ending on a point > than the starting point
					// -----------------------
					// |          |          |
					// |          |          |
					// |   sym    |     s    |
					// |          |      e   |
					// |          |          |
					// -----------------------
					if(endY > startY && _self.flipDirection === 'next') {
						angle		= 0;
						oob 		= true;
						noflip		= true;
					}
					// Page is on the right side, 
					// and we drag/swipe to the opposite direction
					// ending on a point < than the symmetric point
					// -----------------------
					// |          |          |
					// |          |          |
					// |   sym    |     s    |
					// |  e       |          |
					// |          |          |
					// -----------------------
					else if(endY < sym && _self.flipDirection === 'next') {
						angle		= 180;
						oob 		= true;
					}
					// Page is on the left side, 
					// and we drag/swipe to the opposite direction
					// ending on a point > than the symmetric point
					// -----------------------
					// |          |          |
					// |          |          |
					// |    s     |   sym    |
					// |          |      e   |
					// |          |          |
					// -----------------------
					else if(endY > sym && _self.flipDirection === 'prev') {
						angle		= 0;
						oob 		= true;
					}
					// Page is on the left side, 
					// and we drag/swipe to the same direction
					// ending on a point < than the starting point
					// -----------------------
					// |          |          |
					// |          |          |
					// |    s     |   sym    |
					// |   e      |          |
					// |          |          |
					// -----------------------
					else if(endY < startY && _self.flipDirection === 'prev') {
						angle		= 180;
						oob 		= true;
						noflip		= true;
					}
					// we drag/swipe to a point between 
					// the starting point and symetric point
					// -----------------------
					// |          |          |
					// |    s     |   sym    |
					// |   sym    |    s     |
					// |         e|          |
					// |          |          |
					// -----------------------
					else {
						var s, e, val;
						
						(_self.flipDirection === 'next') ?
							(s = startY, e = sym, val = startY - distance) : 
							(s = sym, e = startY , val = startY + distance);
						
						angle = _self._calcAngle(val, s, e);
						
						if((direction === 'up' && _self.flipDirection === 'prev') || (direction === 'down' && _self.flipDirection === 'next')) {
							noflip	= true;
						}
					}
					
					switch(phase) {
					
						case 'start' :
							
							if(_self._isAnimating()) {
								//return false;
								// the user can still grab a page while one is flipping (in this case not being able to move)
								// and once the page is flipped the move/touchmove events are triggered..
								_self.start = true;
								return false;
							} 
							else {
								_self.start = false;
							
							}
							
							// check which page is clicked/touched
							_self._setFlippingPage();
							
							// check which page comes before & after the one we are clicking
							// use our vars instead of jquery prev and next?
							_self.$beforePage 	= _self.currentPage > 1 ? _self.$flippingPage.prev() : $('#noelementonthepage');
							_self.$afterPage 	= _self.$flippingPage.next();
							
							break;
							
						case 'move' :
							
							if(distance > 0) {
								if(_self._isAnimating() || _self.start) {	
									return false;
								}
								
								// adds overlays: shows shadows while flipping
								if(!_self.hasOverlays) {
									_self._addOverlays();	
								}
								// save last angle
								_self.angle = angle;
								// we will update the rotation value of the page while we move it
								_self._turnPage(angle , true);
							}
							break;
							
						case 'end' :
							
							if(distance > 0) {
								if(_self._isAnimating() || _self.start) return false;
								
								console.log('setting animating to true');
								_self.isAnimating = true;
								
								// keep track if the page was actually flipped or not
								// the data flip will be used later on the transitionend event
								_self.$flippingPage.data('flip', !noflip);
								
								// if out of bounds we will "manually" flip the page,
								// meaning there will be no transition set
								if(oob) {
									if(!noflip) {
										// the page gets flipped (user dragged from the starting point until the symmetric point)
										// update current page
										_self._updatePage();
									}
                  console.log('oob!');
									_self._onEndFlip(_self.$flippingPage);
								}
								else {
									//return;
									// save last angle
									_self.angle = angle;
									// calculate the speed to flip the page:
									// the speed will depend on the current angle.
									_self._calculateSpeed();
									//alert (direction);
									_self._turnPage(direction == "up" ? 179.99 : 0.01);  //safari bug? - if 180 the first flip flickers!
									if(!noflip) {
									  _self._updatePage();
									}
									
								}
							}
							break;
					};
				}
			});
		
		},
		
		//setFlippingPage is where the transition end handler is attached to the 
		
		_setFlippingPage	: function(page) {
			
			var _self = this;
			if (page) {
			  this.$flippingPage = page;
			} else {
			  this.$flippingPage 	= (this.flipDirection === 'prev') ? this.$previousPage : this.$currentPage;
			}
	
			this.$flippingPage.one('webkitTransitionEnd.flips transitionend.flips OTransitionEnd.flips', function(event) {
				
				if($(event.target).hasClass('page')) {
				  console.log('calling transition end handler');
					_self._onEndFlip($(this));
				
				}
				
			});
		
		},
				
		_isAnimating		: function() {
			if(this.isAnimating) {
				return true;
			}
			return false;
		},
		
		_onEndFlip			: function($page) {
		  if(this.loading) {
		    return;
		  }
			this._adjustLayout();
			
			this.$flippingPage.css({
				'-webkit-transition' 	: 'none',
				'-moz-transition' 		: 'none'
			});
			
			// remove overlays
			this._removeOverlays();
			
			this.isAnimating = false;
			
			// hack (todo: issues with safari / z-indexes)
			if(this.flipDirection === 'next' || (this.flipDirection === 'prev' && !$page.data('flip'))) {
				this.$flippingPage.find('.back').css('-webkit-transform', 'rotateX(180deg)');
			}
		},
		
		// given the touch/drag start point (s), the end point (e) and a value in between (x)
		// calculate the respective angle (0deg - 180deg)
		_calcAngle			: function(x, s, e) {
			return (-180 / (s - e)) * x + ((s * 180) / (s - e));
		},
		
		// given the current angle and the default speed, calculate the respective speed to accomplish the flip
		_calculateSpeed		: function() {
			//make this less severe near the edges
			(this.swipeDirection === 'up') ? 
				this.flipSpeed = (this.options.flipspeed / 180) * this.angle :
				this.flipSpeed = - (this.options.flipspeed / 180) * this.angle + this.options.flipspeed;
		},
		
		//this is the fn that does the flipping
		//
		//it either turns a specific angle
		//
		//or sets a transition for the whole page flip
		//
		//
		
		_turnPage			: function(angle, update, time) {
			
			time = time || this.flipSpeed;
			
			// hack / todo: before page that was set to 181deg should have 180deg
			if (this.$beforePage) {
			  this.$beforePage.css({
  				'-webkit-transform'	: 'rotateX(180deg)',
  				'-moz-transform'	: 'rotateX(180deg)'
  			});
			}
			
			// if not moving manually set a transition to flip the page
			if(!update) {
				this.$flippingPage.css({
					'-webkit-transition' : '-webkit-transform ' + time + 'ms ' + this.options.fliptimingfunction,
					'-moz-transition' : '-moz-transform ' + time + 'ms ' + this.options.fliptimingfunction
				});
			}
			
			// if page is a right side page, we need to set its z-index higher as soon the page starts to flip.
			// this will make the page be on "top" of the left ones.
			// note: if the flipping page is on the left side then we set the z-index after the flip is over.
			// this is done on the _onEndFlip function.
			
			var idx	= (this.flipDirection === 'next') ? this.currentPage : this.currentPage - 1;
			if(this.flipDirection === 'next') {
				this.$flippingPage.css('z-index', 5);
			}
			
			// hack (todo: issues with safari / z-indexes)
			this.$flippingPage.find('.back').css('-webkit-transform', 'rotateX(180deg)');

			// update the angle
			this.$flippingPage.css({
				'-webkit-transform'		: 'rotateX(' + angle + 'deg)',
				'-moz-transform'		: 'rotateX(' + angle + 'deg)'
			});
			
			// show overlays
			this._overlay(angle, update);
			
		},
		
		_addOverlays		: function() {
			//return;
			var _self = this;
			
			// remove current overlays
			this._removeOverlays();
			
			this.hasOverlays	= true;
			
			// overlays for the flipping page. One in the front, one in the back.
			//just keep these around in variables & append/detach as needed?
			
			this.$frontoverlay	= $('<div class="flipoverlay"></div>').appendTo(this.$flippingPage.find('div.front > .outer'));
			this.$backoverlay	= $('<div class="flipoverlay"></div>').appendTo(this.$flippingPage.find('div.back > .outer'))
			
			// overlay for the page "under" the flipping page.
			if(this.$afterPage) {
				this.$afterOverlay	= $('<div class="overlay"></div>').appendTo(this.$afterPage.find('div.front > .outer'));
			}
			
			// overlay for the page "before" the flipping page
			if(this.$beforePage) {
				this.$beforeOverlay	= $('<div class="overlay"></div>').appendTo(this.$beforePage.find('div.back > .outer'));
			}
		},
		
		_removeOverlays		: function() {
			
			// removes the 4 overlays
			if(this.$frontoverlay)
				this.$frontoverlay.remove();
			if(this.$backoverlay)
				this.$backoverlay.remove();
			if(this.$afterOverlay)
				this.$afterOverlay.remove();
			if(this.$beforeOverlay)
				this.$beforeOverlay.remove();
				
			this.hasOverlays	= false;
				
		},
		
		_overlay			: function(angle, update) {
			
			// changes the opacity of each of the overlays.
			if(update) {
				// if update is true, meaning we are manually flipping the page,
				// we need to calculate the opacity that corresponds to the current angle
				var afterOverlayOpacity 	= - (1 / 90) * angle + 1,
					beforeOverlayOpacity 	= (1 / 90) * angle - 1;
				
				if(this.$afterOverlay) {
					this.$afterOverlay.css('opacity', afterOverlayOpacity);
				}
				if(this.$beforeOverlay) {
					this.$beforeOverlay.css('opacity', beforeOverlayOpacity);
				}
				
				// the flipping page will have a fixed value.
				// todo: add a gradient instead.
				var flipOpacity 	= 0.1;
				this.$frontoverlay.css('opacity', flipOpacity);
				this.$backoverlay.css('opacity', flipOpacity);
				
			}
			else {
				
				var _self = this;
				
				// if we release the mouse / touchend then we will set a transition for the overlays.
				// we will need to take in consideration the current angle, the speed (given the angle)
				// and the delays for each overlay (the opacity of the overlay will only change
				// when the flipping page is on the same side).
				var afterspeed	= this.flipSpeed,
					beforespeed	= this.flipSpeed,
					margin		= 60; // hack (todo: issues with safari / z-indexes)
				
				if(this.$afterOverlay) {
					var afterdelay = 0;
					
					if(this.swipeDirection === 'down') {
						if(this.angle > 90) {
							afterdelay 	= Math.abs(this.flipSpeed - this.options.flipspeed / 2 - margin);
							afterspeed	= this.options.flipspeed / 2 - margin ;
						}
						else {
							afterspeed -= margin;
						}
					}
					else {
						afterspeed	= Math.abs(this.flipSpeed - this.options.flipspeed / 2);
					}
					
					if(afterspeed <= 0) afterspeed = 1;
					
					this.$afterOverlay.css({
						'-webkit-transition' 	: 'opacity ' + afterspeed + 'ms ' + this.options.fliptimingfunction + ' ' + afterdelay + 'ms',
						'-moz-transition' 		: 'opacity ' + afterspeed + 'ms ' + this.options.fliptimingfunction + ' ' + afterdelay + 'ms',
						'opacity'				: (this.swipeDirection === 'up') ? 0 : 1
					});
					
				}
				
				if(this.$beforeOverlay) {
				
					var beforedelay = 0;
					
					if(this.swipeDirection === 'up')  {
						if(this.angle < 90) {
							beforedelay = Math.abs(this.flipSpeed - this.options.flipspeed / 2 - margin) ;
							beforespeed = this.options.flipspeed / 2 - margin;
						}
						else {
							beforespeed -= margin;
						}
					}
					else {
						beforespeed = Math.abs(this.flipSpeed - this.options.flipspeed / 2);
					}
					
					if(beforespeed <= 0) beforespeed = 1;
					
					this.$beforeOverlay.css({
						'-webkit-transition'	: 'opacity ' + beforespeed + 'ms ' + this.options.fliptimingfunction + ' ' + beforedelay + 'ms',
						'-moz-transition'		: 'opacity ' + beforespeed + 'ms ' + this.options.fliptimingfunction + ' ' + beforedelay + 'ms',
						'opacity'				: (this.swipeDirection === 'up') ? 1 : 0
					});
				}
			}
		}
	};
	
	

/**
 * jquery.flips.js
 * 
 * Copyright 2011, Pedro Botelho / Codrops
 * Free to use under the MIT license.
 *
 * Date: Fri May 4 2012
 */
 
/**
 * Note: This is highly experimental and just a proof-of-concept! 
 * There are some few "hacks", probably some bugs, and some functionality 
 * is incomplete... definitely not ready for a production environment.
 *
 *
 * Tested and working on:
 * - Google Chrome 18.0.1025.168
 * - Apple Safari 5.1.5
 * - Apple Safari 5.1 Mobile
 * 
 */
 
 //get rid of History?
 //add ability to dynamically add pages
 //change to be vertical!
 
 //have vars for $prevPage, $nextPage, $currentPage
 

	var Flipset 			= function( options ) {
	
		this.$el	= options.containerEl;
		console.log("el: " , this.$el);
		this._init( options );
		
	};
	
  Flipset.defaults 	= {
		flipspeed			: 500,
		fliptimingfunction	: 'linear',
		current				: 1
	};
	
	Flipset.prototype 	= {
	  
	  //make init less 'comprehensive'
		_init 				: function( options ) {
		  //pass in original pages as raw strings, turn into special flip pages - can use dust instead of jquery - just use the string
		  //no need to pass in pages? just get from parent view's collection?
		  //maybe keep track of pages back up in the view?
		  
		  
		  
		  this.sourceItems = [];
			this.pages = [];
			this.options 		= $.extend( true, {}, Flipset.defaults, options );
			this.parentView = options.parentView;
			this.flipPagesCount = 0;
			
			//DOM elements for previous, current, and next page
			this.$previousPage = undefined;
			this.$currentPage = undefined;
			this.$nextPage = undefined;
			
			for (var i = 0, page; i < options.pages.length; i++) {
       	page = options.pages[i]
       	this.addPage(page, {skipLayout:true});
      }
			
			this.pagesCount		= this.pages ? this.pages.length : 0;
		
			this.currentPage	= this.options.current || 1;
			//don't let the person flip to the first page?
			
			this._getWinSize();
		
			this._initTouchSwipe(); //this is ok - it's just on the container el
			this._loadEvents(); //this means binding the events -it's fine to do right away
			//this._goto();
			
		},
		addPage: function(elem, opts) {
		  opts = opts || {};
		  if (opts && opts.addToStart) {
		    this.sourceItems.unshift(elem);
		  } else {
		    this.sourceItems.push(elem);
		  }
		  this.pagesCount++;
		  if (!opts.skipLayout) {
		    this._layout(); //layout puts the pages into the front/back divs and sets z-index
		    this._loadEvents();
		  }
		},
		//returns a jquery object with all page elems
		_getPageElems: function() {
		  return this.$el.children( 'div.page' );
		},
		//returns a jquery object with all page elems
		_setPageElems: function() {
		  this._$pageElems = this.$el.children( 'div.page' );
		},
		_getWinSize			: function() {
			
			var $win = this.$el;//$( window );
			
			this.windowProp = {
				width	: $win.width(),
				height	: $win.height()
			};
		
		},
		_goto				: function() {
			
			var page = ( this.state === undefined ) ? this.currentPage : this.state;
			
			if( page < 1 || page > this.flipPagesCount ) {
			
				page = 1;
			
			}
			
			this.currentPage = page;
			
		},
		_adjustLayout		: function( page ) { //page is the index of... the current page
		  console.log("in adjust layout, page is: ", page);
		  
			var _self = this;
			
			var $flipPages = this._getPageElems();
			var flipPageCount
			
			$flipPages.each( function( i ) {
				
				var $page	= $(this);
				
				if( i === page - 1 ) {
				
					$page.css({
						'-webkit-transform'	: 'rotateX( 180deg )',
						'-moz-transform'	: 'rotateX( 180deg )',
						'z-index'			: _self.flipPagesCount - 1 + i
					});
				
				}
				else if( i < page ) {
				
					$page.css({
						'-webkit-transform'	: 'rotateX( 181deg )', // todo: fix this (should be 180deg)
						'-moz-transform'	: 'rotateX( 181deg )', // todo: fix this (should be 180deg)
						'z-index'			: _self.flipPagesCount - 1 + i
					});
				
				}
				else {
				
					$page.css({
						'-webkit-transform'	: 'rotateX( 0deg )',
						'-moz-transform'	: 'rotateX( 0deg )',
						'z-index'			: _self.flipPagesCount - 1 - i
					});
				
				}
						
			} );
		
		},
		
		//move this stuff up into the dust templates?
		//...except for the size css, which we could do with $.css
		//instead of going through all pages, do this through add...
		
		_layout				: function() {
			console.log('in layout');
			this._setLayoutSize();
			console.log('pages count', this.pagesCount);
			var that = this;
			//start and end with a fake page?
			//that.$el.append("<div class='page'></div>");
			
			//don't loop through this necessarily - only do when necessary?
			
			for( var i = this.flipPagesCount - 1; i <= this.pagesCount; ++i ) {
  			var	page 		= that.sourceItems[i] || "", //"<span class='big-num'>" + i  + "</span>";//
  			  nextPage = that.sourceItems[ i + 1 ] || '', //"<span class='big-num'>" + (i+1)  + "</span>";//t
  				pageData	= {
  					frontContent			: page,
  					backContent			: nextPage,
  					//theStyle				: 'z-index: ' + ( this.pagesCount - i ) + ';left: ' + ( this.windowProp.width / 2 ) + 'px;',
  					//theContentStyleFront	: 'width:' + this.windowProp.width + 'px;',
  					//theContentStyleBack		: 'width:' + this.windowProp.width + 'px;'
  					zIndex : this.pagesCount - i,
  					pageNum: i,
  					backPageNum: i + 1 
  				};
			  

  			  //console.log("front content ", $page.find('.front .content'))
  			  //$page.find('.front .content').css('width', ( this.windowProp.width / 2 ) + 'px');
  			  //$page.find('.back .content').css('width', ( this.windowProp.width / 2 ) + 'px');
  			  //$page.find('.front > div > .content').css('width', '100%').css('left', '-100%');
  			  //$page.find('.back > div > .content').css('width', '100%');
  				//pageData.theContentStyleFront += 'left:-' + ( this.windowProp.width / 2 ) + 'px';
				
			
  			//.appendTo( this.$el );
  			//console.log("container, page", this.$el, page);
			
  			dust.render("flipPage", pageData, function(err, out) {
  			  var pageElem = $(out);
  		    pageElem.appendTo(that.$el);
  			  that.pages.push(pageElem);
  			  if(err != null) {
  					console.log(err);
  					that.$el.append(pageElem);
  				} else{
  				  that.$el.append(pageElem);
  				}
  			});
  		}
			
			//this.pages.remove();
			this.$flipPages		= this._getPageElems();
			this.flipPagesCount	= this.$flipPages.length;
			
			//adjust layout
			this._adjustLayout( ( this.state === undefined ) ? this.currentPage : this.state );
			
		},
		_renderPage : function (sourceItem) {
		  
		  
		},
		//set this to the size of the app container, not the window
		//
		_setLayoutSize		: function() {
		
			this.$el.css( {
				//width	: this.windowProp.width,
				//height	: this.windowProp.height
			} );
		
		},
		_initTouchSwipe		: function() {
			
			var _self = this;
			
			this.$el.swipe( {
				threshold			: 5,
				swipeStatus			: function( event, phase, start, end, direction, distance ) {
				  //if view is not in flip mode, return
				  if(_self.parentView && !_self.parentView.flipMode) {
				    return;
				  }
					//get window size if it hasn't been set...
					if (_self.windowProp.height == 0) {
					  _self._getWinSize();
					}
					
					var startY		= start.y,
						endY		= end.y,
						sym, angle,
						oob			= false,
						noflip		= false;
					
					// check the "page direction" to flip:
					// if the page flips from the right to the left (right side page)
					// or from the left to the right (left side page).
					// check only if not animating
					if( !_self._isAnimating() ) {
					
						( startY < _self.windowProp.height / 2 ) ? _self.flipSide = 'l2r' : _self.flipSide = 'r2l';
						//console.log(startY, _self.flipSide, _self.windowProp.width / 2, _self.windowProp, _self.$el);
					
					}
					
					if( direction === 'left' || direction === 'right' ) {
						
						if( _self.angle === undefined || _self.angle === 0 ) {
						
							_self._removeOverlays();
							return false;
						
						}
						else {
							
							( _self.angle < 90 ) ? direction = 'up' : direction = 'down';
							
						}
						
					};
					
					_self.flipDirection = direction;
					
					// on the first & last page neighbors we don't flip
					// KL -we'll have a 'special' first page and last page that's never reachable!
					if( _self.currentPage <= 1 && _self.flipSide === 'l2r' || _self.currentPage >= _self.flipPagesCount - 1 && _self.flipSide === 'r2l' ) {
						
						return false;
					
					}
					
					// save ending point (symetric point):
					// if we touch / start dragging on, say [x=10], then
					// we need to drag until [window's width - 10] in order to flip the page 100%.
					// if the symetric point is too close we are giving some margin:
					// if we would start dragging right next to [window's width / 2] then
					// the symmetric point would be very close to the starting point. A very short swipe
					// would be enough to flip the page..
					sym	= _self.windowProp.height - startY;
					
					var symMargin = 0.9 * ( _self.windowProp.height / 2 );
					if( Math.abs( startY - sym ) < symMargin ) {
					
						( _self.flipSide === 'r2l' ) ? sym -= symMargin / 2 : sym += symMargin / 2;
					
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
					if( endY > startY && _self.flipSide === 'r2l' ) {
					
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
					else if( endY < sym && _self.flipSide === 'r2l' ) {
					
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
					else if( endY > sym && _self.flipSide === 'l2r' ) {
					
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
					else if( endY < startY && _self.flipSide === 'l2r' ) {
					
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
						
						( _self.flipSide === 'r2l' ) ?
							( s = startY, e = sym, val = startY - distance ) : 
							( s = sym, e = startY , val = startY + distance );
						
						angle = _self._calcAngle( val, s, e );
						
						if( ( direction === 'up' && _self.flipSide === 'l2r' ) || ( direction === 'down' && _self.flipSide === 'r2l' ) ) {
							
							noflip	= true;
						
						}
						
					}
					
					switch( phase ) {
					
						case 'start' :
							
							if( _self._isAnimating() ) {
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
							_self.$beforePage 	= _self.currentPage > 1 ? _self.$flippingPage.prev() : $('#noelementonthepage');
							_self.$afterPage 	= _self.$flippingPage.next();
							
							break;
							
						case 'move' :
							
							if( distance > 0 ) {
							
								if( _self._isAnimating() || _self.start ) {
										
									return false;
								
								}
								
								// adds overlays: shows shadows while flipping
								if( !_self.hasOverlays ) {
									
									_self._addOverlays();
									
								}
								
								// save last angle
								_self.angle = angle;
								// we will update the rotation value of the page while we move it
								_self._turnPage( angle , true );
							
							}
							break;
							
						case 'end' :
							
							if( distance > 0 ) {
								
								if( _self._isAnimating() || _self.start ) return false;
								
								_self.isAnimating = true;
								
								// keep track if the page was actually flipped or not
								// the data flip will be used later on the transitionend event
								( noflip ) ? _self.$flippingPage.data( 'flip', false ) : _self.$flippingPage.data( 'flip', true );
								
								// if out of bounds we will "manually" flip the page,
								// meaning there will be no transition set
								if( oob ) {
									
									if( !noflip ) {
										
										// the page gets flipped (user dragged from the starting point until the symmetric point)
										// update current page
										_self._updatePage();
									
									}
                  console.log('oob!');
									_self._onEndFlip( _self.$flippingPage );
								
								}
								else {
									//return;
									// save last angle
									_self.angle = angle;
									// calculate the speed to flip the page:
									// the speed will depend on the current angle.
									_self._calculateSpeed();
							
									switch( direction ) {
										
										case 'up' :
											
											_self._turnPage( 180 );
											
											if( _self.flipSide === 'r2l' ) {
												
												_self._updatePage();
											
											}
											
											break;
										
										case 'down' :
											
											_self._turnPage( 0 );
											
											if( _self.flipSide === 'l2r' ) {
												
												_self._updatePage();
											
											}
											
											break;
										
									};
								
								}
								
							}
							
							break;

					};
					
				}
				
			} );
		
		},
		_setFlippingPage	: function() {
			
			var _self = this;
			//console.log("set flipping page: - pages: ", this.pages);
			( this.flipSide === 'l2r' ) ?
				this.$flippingPage 	= this.pages[this.currentPage - 1] :
				this.$flippingPage	= this.pages[this.currentPage] ;
			
			console.log("setting flipping page: ", this.$flippingPage);
			
			this.$flippingPage.on( 'webkitTransitionEnd.flips transitionend.flips OTransitionEnd.flips', function( event ) {
				
				if( $( event.target ).hasClass( 'page' ) ) {
				  console.log('calling transition end handler');
					_self._onEndFlip( $(this) );
				
				}
				
			});
		
		},
		_updatePage			: function() {
			if( this.flipSide === 'r2l' ) {
				++this.currentPage;
				this.parentView.flipNext();
			}
			else if( this.flipSide === 'l2r' ) {
				--this.currentPage;
				this.parentView.flipPrevious();
			}
			
		},
		_isAnimating		: function() {
			if( this.isAnimating ) {
				return true;
			}
			return false;
		},
		_loadEvents			: function() {
			var _self = this;
			
			$( window ).on( 'resize', function( event ) {
			  return;
				_self._getWinSize();
				_self._setLayoutSize();
				var $flipPages = _self._getPageElems();
				
				//$flippages is a jquery object
				var $contentFront	= $flipPages.children( 'div.front' ).find( 'div.content' ),
					$contentBack	= $flipPages.children( 'div.back' ).find( 'div.content' )
				
				//$flipPages.css( 'left', _self.windowProp.width / 2 );
				
				$contentFront.css( {
					//width	: _self.windowProp.width,
					//left	: -_self.windowProp.width / 2
				} );
				$contentFront.eq( 0 ).css( 'height', _self.windowProp.height );
				
				$contentBack.css( 'height', _self.windowProp.height );
			
			} );
				
		},
		_onEndFlip			: function( $page ) {
			
			console.log('\n in End Flip function for page ', $page, this.flipSide);
			//this._adjustLayout(this.currentPage);
			
			// if the page flips from left to right we will need to change the z-index of the flipped page
			if( ( this.flipSide === 'l2r' && $page.data( 'flip' ) ) || 
				( this.flipSide === 'r2l' && !$page.data( 'flip' ) )  ) {
        console.log('changing z-index of page ' + $page.index() + ' to', ( this.flipPagesCount - 2 - $page.index()), $page);
				//$page.css( 'z-index', this.pagesCount - 2 - $page.index() );
			  $page.css( 'z-index', 500 );
			}
			
			this.$flippingPage.css( {
				'-webkit-transition' 	: 'none',
				'-moz-transition' 		: 'none'
			} );
			
			// remove overlays
			this._removeOverlays();
			
			this.isAnimating = false;
			
			// hack (todo: issues with safari / z-indexes)
			if( this.flipSide === 'r2l' || ( this.flipSide === 'l2r' && !$page.data( 'flip' ) ) ) {
				this.$flippingPage.find('.back').css( '-webkit-transform', 'rotateX(180deg)' );
			
			}
			
		},
		// given the touch/drag start point (s), the end point (e) and a value in between (x)
		// calculate the respective angle ( 0deg - 180deg )
		_calcAngle			: function( x, s, e ) {
			
			return ( -180 / ( s - e ) ) * x + ( ( s * 180 ) / ( s - e ) );
		
		},
		// given the current angle and the default speed, calculate the respective speed to accomplish the flip
		_calculateSpeed		: function() {
			
			( this.flipDirection === 'up' ) ? 
				this.flipSpeed = ( this.options.flipspeed / 180 ) * this.angle :
				this.flipSpeed = - ( this.options.flipspeed / 180 ) * this.angle + this.options.flipspeed;
		
		},
		_turnPage			: function( angle, update ) {
			
			// hack / todo: before page that was set to 181deg should have 180deg
			this.$beforePage.css({
				'-webkit-transform'	: 'rotateX( 180deg )',
				'-moz-transform'	: 'rotateX( 180deg )'
			});
			
			// if not moving manually set a transition to flip the page
			if( !update ) {
				
				this.$flippingPage.css( {
					'-webkit-transition' : '-webkit-transform ' + this.flipSpeed + 'ms ' + this.options.fliptimingfunction,
					'-moz-transition' : '-moz-transform ' + this.flipSpeed + 'ms ' + this.options.fliptimingfunction
				} );
				
			}
			
			// if page is a right side page, we need to set its z-index higher as soon the page starts to flip.
			// this will make the page be on "top" of the left ones.
			// note: if the flipping page is on the left side then we set the z-index after the flip is over.
			// this is done on the _onEndFlip function.
			var idx	= ( this.flipSide === 'r2l' ) ? this.currentPage : this.currentPage - 1;
			if( this.flipSide === 'r2l' ) {
				//console.log('changing z-index in turnpage: ', this.flipPagesCount - 1 + idx )
				this.$flippingPage.css( 'z-index', this.flipPagesCount - 1 + idx );
			
			}
			
			// hack (todo: issues with safari / z-indexes)
			//console.log(this.$flippingPage.css('z-index'));
			this.$flippingPage.find('.back').css( '-webkit-transform', 'rotateX(180deg)' );
			//this.$flippingPage.find('.back').css( 'border', '1px solid red' );
			//this.$flippingPage.find('.front').css( 'border', '1px solid green' );
			//this.$flippingPage.children().css( '-webkit-transform', 'translate3d(0px, 0px, 0px)' );
			//this.$flippingPage.css( 'z-index', '9000' );
			// update the angle
			this.$flippingPage.css( {
				'-webkit-transform'		: 'rotateX(' + angle + 'deg)',
				'-moz-transform'		: 'rotateX(' + angle + 'deg)'
			} );
			
			// show overlays
			this._overlay( angle, update );
			
		},
		_addOverlays		: function() {
			//return;
			var _self = this;
			
			// remove current overlays
			this._removeOverlays();
			
			this.hasOverlays	= true;
			
			// overlays for the flipping page. One in the front, one in the back.
			
			this.$frontoverlay	= $( '<div class="flipoverlay"></div>' ).appendTo( this.$flippingPage.find( 'div.front > .outer' ) );
			this.$backoverlay	= $( '<div class="flipoverlay"></div>' ).appendTo( this.$flippingPage.find( 'div.back > .outer' ) )
			
			// overlay for the page "under" the flipping page.
			if( this.$afterPage ) {
				
				this.$afterOverlay	= $( '<div class="overlay"></div>' ).appendTo( this.$afterPage.find( 'div.front > .outer' ) );
			
			}
			
			// overlay for the page "before" the flipping page
			if( this.$beforePage ) {
				
				this.$beforeOverlay	= $( '<div class="overlay"></div>' ).appendTo( this.$beforePage.find( 'div.back > .outer' ) );
			
			}
		
		},
		_removeOverlays		: function() {
			
			// removes the 4 overlays
			if( this.$frontoverlay )
				this.$frontoverlay.remove();
			if( this.$backoverlay )
				this.$backoverlay.remove();
			if( this.$afterOverlay )
				this.$afterOverlay.remove();
			if( this.$beforeOverlay )
				this.$beforeOverlay.remove();
				
			this.hasOverlays	= false;
				
		},
		_overlay			: function( angle, update ) {
			
			// changes the opacity of each of the overlays.
			if( update ) {
				
				// if update is true, meaning we are manually flipping the page,
				// we need to calculate the opacity that corresponds to the current angle
				var afterOverlayOpacity 	= - ( 1 / 90 ) * angle + 1,
					beforeOverlayOpacity 	= ( 1 / 90 ) * angle - 1;
				
				if( this.$afterOverlay ) {
				
					this.$afterOverlay.css( 'opacity', afterOverlayOpacity );
					
				}
				if( this.$beforeOverlay ) {
				
					this.$beforeOverlay.css( 'opacity', beforeOverlayOpacity );
					
				}
				
				// the flipping page will have a fixed value.
				// todo: add a gradient instead.
				var flipOpacity 	= 0.1;
				this.$frontoverlay.css( 'opacity', flipOpacity );
				this.$backoverlay.css( 'opacity', flipOpacity );
				
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
				
				if( this.$afterOverlay ) {
				
					var afterdelay = 0;
					
					if( this.flipDirection === 'down' ) {
						
						if( this.angle > 90 ) {
							
							afterdelay 	= Math.abs( this.flipSpeed - this.options.flipspeed / 2 - margin );
							afterspeed	= this.options.flipspeed / 2 - margin ;
						
						}
						else {
							
							afterspeed -= margin;
						
						}
						
					}
					else {
						
						afterspeed	= Math.abs( this.flipSpeed - this.options.flipspeed / 2 );
					
					}
					
					if( afterspeed <= 0 ) afterspeed = 1;
					
					this.$afterOverlay.css( {
						'-webkit-transition' 	: 'opacity ' + afterspeed + 'ms ' + this.options.fliptimingfunction + ' ' + afterdelay + 'ms',
						'-moz-transition' 		: 'opacity ' + afterspeed + 'ms ' + this.options.fliptimingfunction + ' ' + afterdelay + 'ms',
						'opacity'				: ( this.flipDirection === 'up' ) ? 0 : 1
					} ).on( 'webkitTransitionEnd.flips transitionend.flips OTransitionEnd.flips', function( event ) {
						if( _self.$beforeOverlay ) _self.$beforeOverlay.off( 'webkitTransitionEnd.flips transitionend.flips OTransitionEnd.flips');
						setTimeout( function() {
							 _self._adjustLayout(_self.currentPage);
						}, _self.options.flipspeed / 2 - margin );
					} );
					
				}
				
				if( this.$beforeOverlay ) {
				
					var beforedelay = 0;
					
					if( this.flipDirection === 'up' )  {
						
						if( this.angle < 90 ) {
						
							beforedelay = Math.abs( this.flipSpeed - this.options.flipspeed / 2 - margin ) ;
							beforespeed = this.options.flipspeed / 2 - margin;
						
						}
						else {
							
							beforespeed -= margin;
						
						}
						
					}
					else {
						
						beforespeed = Math.abs( this.flipSpeed - this.options.flipspeed / 2 );
						
					}
					
					if( beforespeed <= 0 ) beforespeed = 1;
					
					this.$beforeOverlay.css( {
						'-webkit-transition'	: 'opacity ' + beforespeed + 'ms ' + this.options.fliptimingfunction + ' ' + beforedelay + 'ms',
						'-moz-transition'		: 'opacity ' + beforespeed + 'ms ' + this.options.fliptimingfunction + ' ' + beforedelay + 'ms',
						'opacity'				: ( this.flipDirection === 'up' ) ? 1 : 0
					} ).on( 'webkitTransitionEnd.flips transitionend.flips OTransitionEnd.flips', function( event ) {
						if( _self.$afterOverlay ) _self.$afterOverlay.off( 'webkitTransitionEnd.flips transitionend.flips OTransitionEnd.flips');
						_self._adjustLayout(_self.currentPage);
					} );
					
				}
				
			}
				
		}
	};
	
	

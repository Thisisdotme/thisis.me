
/*
the behavior for the photo feature

-a good place to try out the Gridview > Listview > Detailview structure

-the album list view (default)
-the gridview for one album
-the listview - the flippable view for an album - it has 'flip mode' and 'detail mode', which allows pinching/zooming, also 'comment mode'

-have whether to show the grid of list/flip view determined internally, not via the URL

*/

(function(TIM) {
  var feature = {};
  feature.models = {};
  feature.views = {};
  feature.collections = {};
  feature.showDetails = false;
  feature.showDetailId = 0;
  feature.cachedResources = {};
  
  feature.models.Photos = TIM.models.FeatureBehavior.extend({
    initialize: function() {
      this.constructor.__super__.initialize.apply(this, arguments);
    },
    // Default attributes 
    defaults: {
  		name: "photos"
    },

    navigate: function() {
      TIM.app.navigate("/photos");
    }

    //show list view
    //show detail view  

  });
  
  TIM.models.PhotoAlbum = Backbone.Model.extend({

    initialize: function() {
      this.photos = new TIM.collections.Photos();
    },
	
    clear: function() {
      this.destroy();
      this.view.remove();
    }

  });
  
  TIM.collections.PhotoAlbums = Backbone.Collection.extend({
  	 	model: TIM.models.PhotoAlbum,
  		//url: TIM.apiUrl + 'authors/' + TIM.pageInfo.authorName + '/photos?callback=?',
  		
  		//let's fake this with flickr
			  		
  		initialize: function(options) {
  		  _.extend(this, TIM.mixins.paging);  //give this collection the ability to page  //+ 
  		  this.initializePaging();
  			this.url = TIM.apiUrl + 'authors/' + TIM.pageInfo.authorName + '/photoAlbums?callback=?';
  		  //alert(this.url);
  		},
  		
  		
  		parse: function(resp) {
  		  return (resp.photos.photo);
  		}

  });
  
  
  TIM.models.Photo = Backbone.Model.extend({

    defaults: {
			time_ago: ""
    },

    initialize: function() {
    },
	
    clear: function() {
      this.destroy();
      this.view.remove();
    }

  });
  
  TIM.collections.Photos = Backbone.Collection.extend({
  	 	model: TIM.models.Photo,
  		//url: TIM.apiUrl + 'authors/' + TIM.pageInfo.authorName + '/photos?callback=?',
  		
  		//let's fake this with flickr
  		max: 0,
			  		
  		initialize: function(options) {
  		  options = options || {};
  		  _.extend(this, TIM.mixins.paging);  //give this collection the ability to page  //+
  		  this.initializePaging({pageSize:100});
  		  this.max = options.max || 0;
  		  var authorName = TIM.pageInfo.authorFirstName;
  			this.url = "http://api.flickr.com/services/rest/?format=json&jsoncallback=?&method=flickr.photos.search&text="
  			            + authorName 
  			            + "&per_page=" + this.pageSize + "&api_key=8662e376985445d92a07c79ff7d12ff8";
  		},
  		
  		
  		parse: function(resp) {
  		  return (resp.photos.photo);
  		},
  		
  		//trying to make this so it doesn't get photos past teh album's 'count'
  		//
  		//
  		
  		setURL: function(searchTerm, pageSize) {
  		  searchTerm = searchTerm || this.searchTerm;
  		  this.searchTerm = searchTerm;
  		  
  		  pageSize = pageSize || this.pageSize;
  		  
  		  if(this.max && (this.pageSize > this.max)) {
  		    this.pageSize = this.max;
  		  }
  		  
  		  searchTerm = searchTerm || TIM.pageInfo.authorFirstName;
  		  this.url = "http://api.flickr.com/services/rest/?format=json&jsoncallback=?&method=flickr.photos.search&text="
  			            + searchTerm 
  			            + "&per_page=" + pageSize + "&api_key=8662e376985445d92a07c79ff7d12ff8";
  		}

  });
  
  //the 'home view' for the photos feature - a list of the author's photo albums
  TIM.views.PhotoAlbumList = Backbone.View.extend( {
      id: "photoAlbums",
      className: "appPage photoFeature",
      numRendered: 0,

      initialize: function() {
          _.extend(this, TIM.mixins.paging);  //give this collection the ability to page  //+ 
          _.bindAll(this, "render");
          this.collection.bind( "reset", this.render );
          this.collection.bind('pageLoaded', this.renderNextPageset, this);
      },

  		events: {
  		  "vclick .album": "showGridView"
  		},


      render: function(){
        var that = this;

        var albums = this.collection.toJSON();
        var template_context = {
                                "albums": albums
        };
        
  		  dust.render("photoAlbums", template_context, function(err, out) {
  			  if(err != null) {
  					console.log(err);
  				}
  			  $(that.el).append(out);
  			  that.numRendered = that.collection.length;
  			});
  		  
  		  if(TIM.appContainerElem.find(this.el).length == 0)  {
  			  TIM.appContainerElem.append(this.$el);
  			}
  			
  			$('#photoAlbumList').css('height', TIM.getViewportSize().height - 40 + 'px');
  			
  			this.iScrollElem = new iScroll('photoAlbumList', { hScroll: false });
  			setTimeout(function () { that.iScrollElem.refresh() }, 0);
  			
  		  if(!feature.showDetails) {
  		    TIM.transitionPage (this.$el);
		    }
  		    		  
      },

      showFlipView: function(event) {
  		  var resourceId = 0;
  		  if (event) {
  		    resourceId = $(event.currentTarget).data('id');
  		    albumId = $(event.currentTarget).data('album_id');
  		  }
  		  feature.showListView(resourceId, {albumId: albumId, animationName: "slide"});
      },
      
      showGridView: function(event) {
  		  var resourceId = 0;
  		  if (event) {
  		    resourceId = $(event.currentTarget).data('album_id');
  		  }
  		  feature.showGridView({albumId: resourceId, animationName: "slide"});
      },
      
      //figure out the next elements, add those to the grid
      renderNextPageset: function() {
        console.log('render next pageset');
      },
      
      resetScrollElem: function() {
        var that = this;
        setTimeout(function () { that.iScrollElem.refresh() }, 0);
      }
      
  });
  
  
  //basic placeholder for photo
  //this would be the grid view
  //need to have view for the album list
  //and a grid view for a single album
  //
  //make this grid view have an album
  //
  //make paging happen!
  
  TIM.views.PhotoGrid = Backbone.View.extend( {
      id: "photoGrid",
      className: "appPage photoFeature",
      numRendered: 0,
      chunkSize: 15,
      initialRenderSize: 30,
      chunkRendering: false,

      initialize: function() {
          _.bindAll(this);
          //this.collection.bind( "reset", this.render );
          this.collection.bind('pageLoaded', this.renderNextPageset, this);
          this.numRendered = 0;
      },

  		events: {
  		  "vclick .thumb": "showFlipView",
  		  "vclick .gridLink": "showAlbumView",
  			"swiperight" : "showAlbumView"
  		},
  		
  		setCollection: function(album) {
  		  this.album = album;
        this.collection = album.photos;
        this.collection.bind('pageLoaded', this.renderNextPageset, this);
  			this.collection.bind( "reset", this.render );
      },


      render: function(){
        var that = this;
        
        //clean out the container element
        this.numRendered = 0;
        this.$el.html('');
        
        //append the element to the document if it's not in there already
        
        if(TIM.appContainerElem.find(this.el).length == 0)  {
  			  TIM.appContainerElem.append(this.$el);
  			}
  			//render container with no photos initially
  			var template_context = {photos:[], name: this.album.get('name')};
  			
  			dust.render("photoGrid", template_context, function(err, out) {
  			  if(err != null) {
  					console.log(err);
  				}
  			  (that.$el).append(out);
  			  //that.numRendered = that.collection.length;
  			});
  			//alert(that.$el.html());
  			
  			//if there's an existing iscroll element, destroy it!
  			if (this.iScrollElem) {
          this.iScrollElem.destroy();
          this.iScrollElem = null;
        }
  			
  			//now render the initial batch of photos
        this.renderChunk(this.initialRenderSize);  		  
      },
      
      resetScrollElem: function(options) {
        options = options || {};
        var that = this;
        //make sure the elem container is the right height
        $('#photoGridScroll').css('height', TIM.getViewportSize().height - 40); //window height - the toolbar height
        if (this.iScrollElem) {
          if (options.destroy) {
            this.iScrollElem.destroy();
            this.iScrollElem = null;
          } else if(options.addScrollDistance) {
            this.iScrollElem.maxScrollY += options.addScrollDistance;
          } else {
            setTimeout(function () { that.iScrollElem.refresh();  }, 0);
            return;
          }
          
        }
        this.iScrollElem = new iScroll('photoGridScroll', { 
            //maybe instead of checking vs. the iscroll value, check to see which item is currently in view, then render next chunk if it's not visible & we're getting close to needing it
          		onScrollMove: function () {
          		},
              onScrollEnd: function () {
          			if (this.y < (this.maxScrollY + 30 )) {
          			  that.renderChunk();
          			}
          		},
              hScroll: false,
              vScrollbar: false
         });
  			setTimeout(function () { that.iScrollElem.refresh();  }, 0);
      },

      showFlipView: function(event) {
  		  var photoId = 0;
  		  if (event) {
  		    photoId = $(event.currentTarget).data('photo_id');
  		  }
  		  feature.showListView({albumId: this.album.id, photoId: photoId, collection: this.collection, animationName: "slide"});
      },
      
      showAlbumView: function(event) {
  		  TIM.transitionPage (feature.albumListView.$el, {
  		    animationName: "slide", reverse: true,
  		    callback: function() {
            feature.albumListView.resetScrollElem();
            TIM.app.navigate('/photos');
          }
  		  });
      },
      
      //figure out the next elements, add those to the grid
      //decouple page requests and rendering
      //for both grid view and flip view (already doing it for flip view)
      //
      //render in groups of 3?
      //
      //maybe have this fn ask for the next page if necessary?
      //
      
      renderChunk: function(chunkSize) {
          var that = this;
          if (this.chunkRendering) {
            console.log('chunk rendering - gonna return now');
            return;
          }
          this.chunkRendering = true;
         //only render the ones we haven't already rendered
          chunkSize = chunkSize || this.chunkSize;
          
          //only render up to the album's count size!
          var numLeft = this.album.get('count') - this.numRendered;
          if(numLeft <= 0) {
            console.log('no more to render');
            this.$el.find('.loading').html('---');
            this.chunkRendering = false;
            return;
          }
          
          if (numLeft < chunkSize) {
            chunkSize = numLeft;
            this.$el.find('.loading').html('---');
          }
         
          var photos = this.collection.toJSON();
          
          //fetch next page if we're getting close to the end of the collection
          //this need to be more intelligent so it doesn't keep asking for thing that aren't there
          //
          //make this automatically triggered by an event?
          //
          
          if(this.collection.length <= this.numRendered + (2 * chunkSize)) {
            //make this only get until the number specified by the album's 'count'!
            this.collection.getNextPage();
          }
          
          photos = photos.slice(this.numRendered, this.numRendered + chunkSize);
          if (photos.length === 0) {
            this.chunkRendering = false;
            return;
          }
          
          console.log('in render chunk', chunkSize, this.numRendered, photos.length);

          var template_context = {"photos": photos};
    		  dust.render("_photoList", template_context, function(err, out) {
    			  if(err != null) {
    					console.log(err);
    				}
    				//that.iScrollElem.destroy();
    			  $('#photoGridScroll .gridContainer').append(out);
    			  that.resetScrollElem();
    			  that.numRendered += photos.length;
    			  TIM.setLoading(false);
    			  that.chunkRendering = false; 
    			});
      },
      
      //is this used?
      
      renderNextPageset: function() {
      }
      
  });
  
  
  //make it so this view doesn't flip beyond its collection's official 'count'
  //
  //
  //other things to do: fake comments list and map icon/overlays
  //
  //
  
  TIM.views.PhotoList = Backbone.View.extend( {
          
      id: "photoListContainer",
      
      className: "appPage flipMode photoFeature",
      
      pageTemplate: "photoPage",
      
      hasRendered: false,
      
      //make scrollable behavior a mixin?
      
      iScrollElem: undefined,
      
      flipMode: true,

      initialize: function(spec) {
          
          
          //add flipset functionality to this view
          _.extend(this, TIM.mixins.flipset);
          
          _.bindAll(this);
          console.log ('photo detail view: ', this);
          
          this.initializeFlipset();
          
          if(TIM.appContainerElem.find(this.el).length == 0)  {
    			  TIM.appContainerElem.append(this.$el);
    			}
    			this.collection.bind('pageLoaded', this.renderNextPageset, this);
    			this.collection.bind( "reset", this.render );
      },
      
      setCollection: function(album) {
        this.album = album
        this.collection = album.photos;
        this.collection.max = album.get("count");
        this.collection.bind('pageLoaded', this.renderNextPageset, this);
  			this.collection.bind( "reset", this.render );
      },
      
      //add the flip events to the flip mixin
      //this view should have the ability to not be flippable & return back to other modules
      //e.g., if we get here from the highlight or timeline feature
      
      events: {
    			"vclick .detailLink" : "toggleMode",
    			"vclick .gridLink" : "showGridView",
    			//"vclick .image" : "toggleMode",
    			"vclick .fullPhoto" : "toggleMode",
    			"swiperight" : "showGridView"
  		},

      render: function( ) {
        //mixing in FlipSet functionality to this view, so the main purpose of 'render' is to render the flipset
        console.log('rendering photo list view');
        if(!this.hasRendered) {
          this.renderFlipSet({
            pageMetaData: {count:this.album.get('count')}
          });
          this.hasRendered = true;
          //this.toolbarView = new TIM.views.Toolbar();
          //var toolbarEl = this.toolbarView.render();
          //this.$el.append(toolbarEl);
          //this.toolbarView.bind('itemClicked', this.toolbarClicked, this);
        }
      },

      showGridView: function(event) {
        console.log('toolbar clicked');
        event.preventDefault();
        if(!this.flipMode) {
          return;
        }
        var that = this;
        feature.showDetails = false;
        feature.showGridView({albumId: this.album.id, reverse:true});
        /*
          TIM.transitionPage(feature.gridView.$el, {
          //TIM.transitionPage(feature.albumListView.$el, {
              animationName: "slide", 
              reverse: true,
              callback: function() {
                feature.gridView.resetScrollElem();
                TIM.app.navigate('/photos/' + that.album.id);
              }
          });
        */
      },
      //we're attempting to load ahead of teh flip
      renderNextPageset: function() {
        this.renderFlipSet();
        //maybe do this a coupld of flips ahead?
        //this.flipNext();
        TIM.setLoading(false);
      },
      
      //this is going to need some work to be able to (fairly) seamlessly transition between
      // 'flip mode' and a mode where the image is scrollable and zoomable
      //
      // also should have a 'comments mode' and perhaps a 'map mode'
      //
      
      toggleMode: function(event) {
        var that = this;
  		  
  		  if (this.flipMode) {
  		    this.$el.toggleClass('flipMode');
  		    this.flipMode = false;
  		    
  		    //make an iscroll container
  		    //get the actual photo image & lay the over the actual flip area?
  		    var overlay = $("<div class='scrollOverlay photoFeature'></div>");
  		    //this.$el.prepend(overlay);
  		    $('#contentContainer').prepend(overlay);
  		    var clonedPage = $('.back .photoPage').eq(1).clone();
  		    //alert(img.css('background-image'));
  		    
  		    overlay.append(clonedPage);
  		    this.$el.addClass('hidden');
  		    var img = clonedPage.find('.image');
  		    $('.scrollOverlay > div').css('width', img.width() + 'px');
  		    //console.log('imgae: ', img);
  		    
  		    window.setTimeout(function() {
  		      overlay.addClass('noToolbars');
  		    }, 10);
  		    
  		    overlay.on('vclick', function(event){
  		      that.toggleMode();
  		    })
  		    var containerEl = overlay.get(0);
  		    //var containerEl = $("#contentContainer").css('height','200px');//this.$el.get(0);
  		    if(containerEl) {
  		      this.iScrollElem = new iScroll(containerEl, { zoom: true, vScroll: true, hScroll: true, hScrollbar: false, vScrollbar: false });
  		       window.setTimeout(function() {
      		      that.iScrollElem.refresh();
      		    }, 10); 
  		    }
  		    
  		  } else {
  		     this.$el.removeClass('hidden');
  		     window.setTimeout(function() {
    		      that.$el.toggleClass('flipMode');
    		    }, 10);
  		    $('.scrollOverlay').remove();
  		    this.flipMode = true;
  		    this.iScrollElem.destroy();
          this.iScrollElem = null;
  		  }
      },
      
      getCurrentModel: function() {
        return this.collection.at(this.pageNum);
      },
      
      toolbarClicked: function(info) {
        console.log("toolbar clicked: ", info);
        if(info === 'detailLink') {
          this.toggleMode();
        }
        if(info === 'gridLink') {
          this.showGridView();
        }
      },
      
      //keep track of our album id & current photo id?
      updateRouter: function() {
        var curPhoto = this.collection.at(this.pageNum);
        var photoId = curPhoto ? curPhoto.id : 0;
        TIM.app.navigate("/photos/" + this.album.id + "/" + photoId, {replace:true});
      }

  } );
  		
  feature.model = new feature.models.Photos();
  
  //maybe have the ability to prefetch collection before actually showing the feature?
  //
  //we're assuming that the url for theis feature will be /photos/<album_id>/<photo_id>
  
  //if there's no photo id, go to the album grid view
  //if there's no album id, just go to the main 'album list' view
  
  //
  
  feature.activate = function(path) {
    var args = path ? path.split('/') : [];
    
    var albumId = args[0];
    var photoId = args[1];
   
    feature.albumCollection = feature.albumCollection || new TIM.collections.PhotoAlbums();
    feature.mainCollection = feature.mainCollection || new TIM.collections.Photos();
    
    //keep grid/list views hanging around or just use one for each and swap out collections?
    
    //feature.gridView =  feature.gridView || new TIM.views.PhotoGrid();
    
    feature.listView = feature.listView || new TIM.views.PhotoList({collection: feature.mainCollection});
    feature.albumListView = feature.albumListView || new TIM.views.PhotoAlbumList({collection: feature.albumCollection});

    
    //always make sure we have a list of albums?
    var showView = function(options) {
      if(options.albumId) {
  		  if(photoId) {
  		    feature.showListView(options);
  		  } else {
  		    feature.showGridView(options);
  		  }
  		} else {
  		  feature.showAlbumListView();
  		}
    }
    
    if(!feature.hasFetchedCollection) {
      console.log('fetching collection!'); 
      
      //this will eventually get the photo albums for the author
      //it should be paged via (perhaps) infinite scroll
      feature.fakeAlbumData = feature.fakeAlbumData.concat(getFakeAlbums(35));
      console.log("feature.fakeAlbumData", feature.fakeAlbumData);
      
      feature.albumCollection.reset(feature.fakeAlbumData);
  		feature.hasFetchedCollection = true;
  		showView({albumId: albumId, photoId: photoId});
  	} else {
  	  showView({albumId: albumId, photoId: photoId});
  	}
  };
  
  feature.showAlbumListView = function(options) {
    options = options || {};
    TIM.transitionPage (feature.albumListView.$el);
  }
  
  //
  //maybe have methods to show detail view, show list view, show grid view?
  //in this case, resourceId is the ID of the first resource to show
  //have to fetch the collection if it doesn't aready exist
  //should jump straight to the page that has that resource ID if possible
  //
  
  feature.showListView = function(options) {
    
    //do this or else should have the detail view fetch the model?
    //cache models that have already been fetched?
    console.log('show list view: ', options);
    
    TIM.setLoading(true);
    options = options || {};
    TIM.disableScrolling();
    resourceId = options.photoId;
    var album = feature.albumCollection.get(options.albumId);
    album.photos.setURL(album.get("searchTerm"));
    
    var collection = album.photos; // || feature.mainCollection;
    
    var showView = function(album) {
        //this isn't ideal - should be able to re-use the flip view if it's the last one the user saw
        if (feature.listView) {
         feature.listView.close();
        }

        var listView = new TIM.views.PhotoList({collection: album.photos});
        listView.setCollection (album);
        listView.initializeFlipset();
        listView.render();
        feature.listView = listView;

        var model = collection.find(function(model){return model.get('id') == resourceId});
        listView.model = model;
        var pageNum = model ? collection.indexOf(model) + 1 : 1;
        listView.goToPage(pageNum);
        TIM.app.navigate('/photos/' + album.id + "/" + resourceId);
        TIM.transitionPage (listView.$el, {"animationName":options.animationName || "fade", "reverse": options.reverse});
        feature.showDetailId = 0;
        feature.showDetails = false;
        TIM.setLoading(false);
     }
    
    if (!album.hasFetchedPhotos) {
      album.photos.fetch({
  			dataType: "jsonp",
  			success: function(resp) {
  		    //alert('got photos for album!');
  		    album.hasFetchedPhotos = true;
  		    showView(album);
  			},
  			error: function(resp) {
          console.log("error: ", resp);
  			}
  		});
    } else {
      //just show the album?
      showView(album);
    }
  }
  
  //show the grid view of one album
  //fetch the collection of photos for the album if necessary
  
  feature.showGridView = function(options) {
    TIM.setLoading(true);
    options = options || {};
    var album = feature.albumCollection.get(options.albumId);
    album.photos.setURL(album.get("searchTerm"));
    //don't make a new one each time?
    feature.gridView = feature.gridView || new TIM.views.PhotoGrid({collection: album.photos});
    feature.gridView.album = album;
    
    var showView = function () {
      //transition to this view
			//this needs to not be so silly - shouldn't do this by default
			//
		  TIM.setLoading(false);
	    TIM.app.navigate('/photos/' + album.id);
	    TIM.transitionPage (feature.gridView.$el, {animationName: "slide", reverse: options.reverse});
    }
    
    if (!album.hasFetchedPhotos) {
      album.photos.fetch({
  			dataType: "jsonp",
  			success: function(resp) {
  		    //alert('got photos for album!');
          album.hasFetchedPhotos = true;
          feature.gridView.setCollection (album);
          feature.gridView.render();
          showView();
  			},
  			error: function(resp) {
          console.log("error: ", resp);
  			}
  		});
    } else {
      //just show the album?
      feature.gridView.setCollection (album);
      feature.gridView.render();
      showView();
    }
  }
  
  //add to feature?
  TIM.features.getByName("photos").behavior = feature;
  
  TIM.loadedFeatures["photos"] = feature; //this is mainly a shorthand for console debugging?
  
  //the rest of the code here is for generating fake photo album data to drive the feature
  
  var searchTerms = ["frog","cat","horse","groovy","magnetic","spacy","elephant","water","mountains","jackson","music","angry","bloody","beautiful","jazz","bass",
  "elvin","coltrane","butterfly","marathon","bert","lsd","philadelphia","macrame","jungle","philosophy","philandering","boorish","race","fly","cimena","basketball","boxing","instagram","scale","architecture",
  "elusive","spiral","spiritual","lake","droplet"];
  
  var thumbUrls = ["http://farm8.static.flickr.com/7071/7263178698_0706a03933_s.jpg","http://farm8.static.flickr.com/7101/7317518440_575f7473e9_s.jpg","http://farm8.static.flickr.com/7102/7317495298_6f865be565_s.jpg",
  "http://farm9.static.flickr.com/8019/7317489980_9d0948e075_s.jpg","http://farm8.static.flickr.com/7074/7317442018_1401bf1bdf_s.jpg","http://farm8.static.flickr.com/7071/7315388362_5f94d64f9e_s.jpg",
  "http://farm3.static.flickr.com/2650/3979691504_b570db2465_s.jpg","http://farm9.static.flickr.com/8008/7317204782_a9be30ffe4_s.jpg","http://farm9.static.flickr.com/8148/7310548548_dd8c16edd9_s.jpg",
  "http://farm8.static.flickr.com/7077/7309112088_30b4e0295f_s.jpg","http://farm8.static.flickr.com/7076/7317232294_5799de05bf_s.jpg","http://farm8.static.flickr.com/7244/7317325330_918e450255_s.jpg",
  "http://farm8.static.flickr.com/7097/7316591786_14cce6b6af_s.jpg","http://farm8.static.flickr.com/7243/7315224968_7ea76566bb_s.jpg","http://farm9.static.flickr.com/8156/7317521928_b274e5e203_s.jpg",
  "http://farm8.static.flickr.com/7226/7317491966_37b3b759b6_s.jpg"];
  
  feature.fakeAlbumData = [
    {
      name: "All Photos",
      count: "318",
      id: 1000,
      searchTerm: TIM.pageInfo.authorFirstName,
      thumbs: [
        {image_url: "http://farm8.static.flickr.com/7071/7263178698_0706a03933_s.jpg", id: 123},
       /* {image_url: "http://farm8.static.flickr.com/7071/7263178698_0706a03933_s.jpg", id: 123},
        {image_url: "http://farm8.static.flickr.com/7071/7263178698_0706a03933_s.jpg", id: 123},
        //{image_url: "http://farm8.static.flickr.com/7071/7263178698_0706a03933_s.jpg", id: 123} */
      ]
    },
    {
      name: "Photos of " + TIM.pageInfo.authorFirstName,
      count: "31",
      id: 1001,
      searchTerm: searchTerms[Math.floor((Math.random()*searchTerms.length)+1)],
       thumbs: [
          {image_url: "http://farm8.static.flickr.com/7212/7296052850_4b75dae217_s.jpg", id: 123},
          /* {image_url: "http://farm8.static.flickr.com/7071/7263178698_0706a03933_s.jpg", id: 123},
            {image_url: "http://farm8.static.flickr.com/7071/7263178698_0706a03933_s.jpg", id: 123},
            //{image_url: "http://farm8.static.flickr.com/7071/7263178698_0706a03933_s.jpg", id: 123} */
        ]
    },
    {
      name: "Photos " + TIM.pageInfo.authorFirstName + " has taken",
      count: "156",
      id: 1002,
      searchTerm: searchTerms[Math.floor((Math.random()*searchTerms.length)+1)],
      thumbs: [
        {image_url: "http://farm8.static.flickr.com/7098/7296136912_d29bb66142_s.jpg", id: 123},
        /* {image_url: "http://farm8.static.flickr.com/7071/7263178698_0706a03933_s.jpg", id: 123},
          {image_url: "http://farm8.static.flickr.com/7071/7263178698_0706a03933_s.jpg", id: 123},
          //{image_url: "http://farm8.static.flickr.com/7071/7263178698_0706a03933_s.jpg", id: 123} */
      ]
    },
    {
      name: "Photos " + TIM.pageInfo.authorFirstName + " has liked",
      count: "23",
      id: 1003,
      searchTerm: searchTerms[Math.floor((Math.random()*searchTerms.length)+1)],
       thumbs: [
          {image_url: "http://farm8.static.flickr.com/7220/7296052840_6372ef6dff_s.jpg", id: 123},
          /* {image_url: "http://farm8.static.flickr.com/7071/7263178698_0706a03933_s.jpg", id: 123},
            {image_url: "http://farm8.static.flickr.com/7071/7263178698_0706a03933_s.jpg", id: 123},
            //{image_url: "http://farm8.static.flickr.com/7071/7263178698_0706a03933_s.jpg", id: 123} */
        ]
    },
    {
      name: "Detroit, May 1977",
      count: "15",
      id: 1004,
      searchTerm: searchTerms[Math.floor((Math.random()*searchTerms.length)+1)],
       thumbs: [
          {image_url: "http://farm8.static.flickr.com/7082/7295851342_99f8612529_s.jpg", id: 123},
          /* {image_url: "http://farm8.static.flickr.com/7071/7263178698_0706a03933_s.jpg", id: 123},
            {image_url: "http://farm8.static.flickr.com/7071/7263178698_0706a03933_s.jpg", id: 123},
            //{image_url: "http://farm8.static.flickr.com/7071/7263178698_0706a03933_s.jpg", id: 123} */
        ]
    },
    {
      name: "Tahoe 2009",
      count: "37",
      id: 1005,
      searchTerm: "tahoe",
       thumbs: [
          {image_url: "http://farm8.static.flickr.com/7228/7314556638_e004c47b52_s.jpg", id: 123},
          /* {image_url: "http://farm8.static.flickr.com/7071/7263178698_0706a03933_s.jpg", id: 123},
            {image_url: "http://farm8.static.flickr.com/7071/7263178698_0706a03933_s.jpg", id: 123},
            //{image_url: "http://farm8.static.flickr.com/7071/7263178698_0706a03933_s.jpg", id: 123} */
        ]
    }
  ]
  var album_id_num = 1006;
  
  
  var getFakeAlbums = function (num) {
    num = num || 10;
    var fakeAlbums = [];
    for (var i = 0; i < num; i++) {
      fakeAlbums.push(generateAlbumJSON());
    }
    return fakeAlbums;
  }
  
  var generateAlbumJSON = function () {
    var searchTerm = searchTerms[Math.floor((Math.random()*searchTerms.length))];
    var thumb = thumbUrls[Math.floor((Math.random()*thumbUrls.length))];
    return {
     name: searchTerm,
     count: Math.floor((Math.random()*78)+1),
     id: album_id_num++,
     searchTerm: searchTerm,
      thumbs: [
         {image_url: thumb, id: 123},
         /* {image_url: "http://farm8.static.flickr.com/7071/7263178698_0706a03933_s.jpg", id: 123},
           {image_url: "http://farm8.static.flickr.com/7071/7263178698_0706a03933_s.jpg", id: 123},
           //{image_url: "http://farm8.static.flickr.com/7071/7263178698_0706a03933_s.jpg", id: 123} */
       ]
    }
  }
  
  
})(TIM);

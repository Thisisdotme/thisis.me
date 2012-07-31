
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
    
  TIM.models.PhotoAlbum = Backbone.Model.extend({

    initialize: function() {
      this.photos = new TIM.collections.Photos({albumId: this.id});
    },
	
    clear: function() {
      this.destroy();
      this.view.remove();
    }

  });
  
  TIM.collections.PhotoAlbums = TIM.collections.BaseCollection.extend({
  	 	model: TIM.models.PhotoAlbum,
  		url: TIM.apiUrl + 'authors/' + TIM.pageInfo.authorName + '/photoalbums',
			  		
  		initialize: function(options) {
  		  _.extend(this, TIM.mixins.paging);  //give this collection the ability to page  //+ 
  		  this.initializePaging();
  		},
  		
  		parse: function(resp) {
       //the first 'image' for each photo should be the smallest - let's call it the 'thumb image'
  		  //this will be more intelligent in the future
  		  _.each(resp.photo_albums, function(album) {
  		    console.log('album: ', album);
  		    album.headline = album.headline || 'All Photos';
  		    //album.cover_photo.thumb_image = album.cover_photo.images[0];
  		    var cover_photo = album.post_type_detail.photo_album.cover_photos[0];
  		    album.main_image = cover_photo[cover_photo.length-1];
  		  });
  		  return (resp.photo_albums);
  		}

  });
  
  
  TIM.models.Photo = Backbone.Model.extend({

    defaults: {
			time_ago: ""
    },

    initialize: function() {
      this.set("time_ago", $.timeago(new Date(this.get("create_time") * 1000)));
      this.set("location", "");
    },
	
    clear: function() {
      this.destroy();
      this.view.remove();
    }

  });
  
  TIM.collections.Photos = TIM.collections.BaseCollection.extend({
  	 	model: TIM.models.Photo,
  		url: TIM.apiUrl + 'authors/' + TIM.pageInfo.authorName + '/photos',
  		max: 0,
  		albumId:0,
			  		
  		initialize: function(options) {
  		  options = options || {};
  		  _.extend(this, TIM.mixins.paging);  //give this collection the ability to page  //+
  		  
  		  this.albumId = options.albumId || 0;
  		  
  		  this.max = options.max || 0;
  		  var pageSize = this.max || 100;
  		  
  		  this.initializePaging({pageSize:pageSize});
  		  
  		  var authorName = TIM.pageInfo.authorFirstName;
  			
  			this.url = TIM.apiUrl + 'authors/' + TIM.pageInfo.authorName + '/photoalbums/' + this.albumId + '/photos';
  			
  		},
  		
  		
  		parse: function(resp) {
  		  //the first 'image' for each photo should be the smallest - let's call it the 'thumb image'
  		  //this will be more intelligent in the future - making decisions based on image size metadata
  		  console.log("photos in album:", resp.photos);
  		  _.each(resp.photos, function(photo) {
  		    //photo.thumb_image = photo.images[0];
  		    //photo.main_image = photo.images[photo.images.length-1];
  		    
  		    photo.thumb_image = photo.post_type_detail.photo[0];
    		  photo.main_image = photo.post_type_detail.photo[photo.post_type_detail.photo.length - 1]; //photo.images[photo.images.length-1];
  		    
  		  });
  		  return (resp.photos);
  		  
  		},
  		
  		//trying to make this so it doesn't get photos past teh album's 'count'
  		//
  		//was more relevant when I was using the flickr api
  		
  		setURL: function(searchTerm, pageSize) {
  		  
  		}

  });
  
  //the 'home view' for the photos feature - a list of the author's photo albums 
  TIM.views.PhotoAlbumList = Backbone.View.extend( {
      id: "photo-albums",
      className: "app-page photo-feature",
      numRendered: 0,
      template: "photoAlbums",

      initialize: function() {
          _.bindAll(this, "render");
          this.collection.bind( "reset", this.render );
          this.collection.bind('pageLoaded', this.renderNextPageset, this);
      },

  		events: {
  		  "tap .album": "showGridView"
  		  //"click .album": "showGridView"
  		},


      render: function(){
        var that = this;

        var albums = this.collection.toJSON();
        console.log('albums: ', albums);
        var templateContext = {
                                "photo_albums": albums
        };
        
        var html = TIM.views.renderTemplate(this.template, templateContext);
    		this.$el.html(html);
    		this.numRendered = this.collection.length;
        
  		  if(TIM.appContainerElem.find(this.el).length == 0)  {
  			  TIM.appContainerElem.append(this.$el);
  			}
  			
  			$('#photo-album-list').css('height', TIM.getViewportSize().height - 40 + 'px'); //subtracting 40 for the toolbar height?
  			
  			this.iScrollElem = new iScroll('photo-album-list', { hScroll: false });
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
  
  
  //this is the 'grid view' for a photo album
  //
  //reached via /photos/<album_id>
  
  TIM.views.PhotoGrid = Backbone.View.extend( {
      id: "photo-grid",
      className: "app-page photo-feature",
      numRendered: 0,
      chunkSize: 15,
      initialRenderSize: 30,
      chunkRendering: false,
      template: "photoGrid",

      initialize: function() {
          _.bindAll(this);
          //this.collection.bind( "reset", this.render );
          this.collection.bind('pageLoaded', this.renderNextPageset, this);
          this.numRendered = 0;
      },

  		events: {
  		  "tap .thumb": "showFlipView",
  		  //"tap .grid-link": "showAlbumView",
  		  //"click .thumb": "showFlipView",
    		"click .grid-link": "showAlbumView",
  			"swiperight" : "showAlbumView"
  		},
  		
  		setCollection: function(album) {
  		  this.album = album;
        this.collection = album.photos;
        this.collection.max = album.get("count");
        this.collection.setURL();
        this.collection.bind('pageLoaded', this.renderNextPageset, this);
  			//this.collection.bind("reset", this.render);
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
  			var templateContext = {photos:[], headline: this.album.get('headline')};
  			
  			var html = TIM.views.renderTemplate(this.template, templateContext);
    		this.$el.append(html);
    		
  			
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
        $('#photo-grid-scroll').css('height', TIM.getViewportSize().height - 40); //window height - the toolbar height
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
        this.iScrollElem = new iScroll('photo-grid-scroll', { 
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
            console.log('chunk rendering already in process - gonna return now');
            return;
          }
          this.chunkRendering = true;
         //only render the ones we haven't already rendered
          chunkSize = chunkSize || this.chunkSize;
          
          //only render up to the album's count size!
          var count = this.album.get('post_type_detail').photo_album.photo_count;
          var numLeft = count - this.numRendered;
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

          var templateContext = {"photos": photos};
          
          var html = TIM.views.renderTemplate("_photoList", templateContext);
    			$('#photo-grid-scroll .grid-container').append(html);
  			  that.resetScrollElem();
  			  that.numRendered += photos.length;
  			  TIM.setLoading(false);
  			  that.chunkRendering = false; 
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
          
      id: "photo-list-container",
      
      className: "app-page flip-mode photo-feature",
      
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
        this.collection.setURL();
        this.collection.bind('pageLoaded', this.renderNextPageset, this);
  			this.collection.bind( "reset", this.render );
      },
      
      //add the flip events to the flip mixin
      //this view should have the ability to not be flippable & return back to other modules
      //e.g., if we get here from the highlight or timeline feature
      
      events: {
    			//"tap .detail-link" : "toggleMode",
    			//"tap .grid-link" : "showGridView",
    			"tap .grid-link" : "showGridView",
    			//"tap .full-photo" : "toggleMode",
    			"tap .interaction-icons .comments" : "showComments",
    			"tap .interaction-icons .location" : "showLocation",
    			//"tap .interaction-icons" : "interactionIconsClicked",
    			"tap .interaction-icons" : "interactionIconsClicked",
    			"swiperight" : "showGridView",
    			
  		},

      render: function( ) {
        //mixing in FlipSet functionality to this view, so the main purpose of 'render' is to render the flipset
        console.log('rendering photo list view');
        if(!this.hasRendered) {
          this.renderFlipSet({
            pageMetaData: {count:getAlbumCount(this.album)}
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
        feature.showGridView({albumId: this.album.id, reverse:true, animationName: "slide"});
      },
      
      //we're attempting to load ahead of teh flip
      renderNextPageset: function() {
        this.renderFlipSet();
        //maybe do this a coupld of flips ahead?
        //this.flipNext();
        TIM.setLoading(false);
      },
      
      // this is going to need some work to be able to (fairly) seamlessly transition between
      // 'flip mode' and a mode where the image is scrollable and zoomable
      //
      // also should have a 'comments mode' and perhaps a 'map mode'
      //
      
      toggleMode: function(event) {
        var that = this;
        
        var photoObj = this.collection.at(this.pageNum);
        //
  		  
  		  if (this.flipMode) {
  		    this.$el.toggleClass('flip-mode');
  		    this.flipMode = false;
  		    
  		    //make an iscroll container
  		    //get the actual photo image & lay the over the actual flip area?
  		    var overlay = $("<div class='scroll-overlay photo-feature'></div>");
  		    //this.$el.prepend(overlay);
  		    $('#content-container').prepend(overlay);
  		    var clonedPage = $('.back .photo-page').eq(1).clone();
  		    //alert(img.css('background-image'));
  		    
  		    overlay.append(clonedPage).css("height", TIM.viewportHeight_);
  		    this.$el.addClass('hidden');
  		    var img = clonedPage.find('.image');
  		    //$('.scroll-overlay > div').css('width', photoObj.get('width') + 'px').css('height', photoObj.get('height') + 'px');
  		    $('.scroll-overlay > div').css('width', TIM.viewportWidth_ + 'px').css('height', TIM.viewportHeight_ + 'px');
  		    //console.log('imgae: ', img);
  		    
  		    window.setTimeout(function() {
  		      overlay.addClass('no-toolbars');
  		    }, 10);
  		    
  		    overlay.on('tap', function(event){
  		      that.toggleMode();
  		    })
  		    var containerEl = overlay.get(0);
  		    //var containerEl = $("#content-container").css('height','200px');//this.$el.get(0);
  		    if(containerEl) {
  		      this.iScrollElem = new iScroll(containerEl, { zoom: true, vScroll: true, hScroll: true, hScrollbar: false, vScrollbar: false });
  		       window.setTimeout(function() {
      		      that.iScrollElem.refresh();
      		    }, 10); 
  		    }
  		    
  		  } else {
  		     this.$el.removeClass('hidden');
  		     window.setTimeout(function() {
    		      that.$el.toggleClass('flip-mode');
    		    }, 10);
  		    $('.scroll-overlay').remove();
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
        if(info === 'detail-link') {
          this.toggleMode();
        }
        if(info === 'grid-link') {
          this.showGridView();
        }
      },
      
      //call the feature's 'show comments view' method & pass in the id of the photo/resource to get comments for...
      showComments: function(event) {
        //event.stopPropagation();
        
        //get photo id from the data attribute... maybe this view should simply know what photo id we're on so we don't have to do this
        var photoId = 0;
  		  if (event) {
  		    photoId = $(event.currentTarget).data('photo_id');
  		  }
        
        event.preventDefault();
        feature.showCommentsView({albumId: this.album.id, photoId: photoId});
      },
      
      showLocation: function(event) {
        //event.stopPropagation();
        event.preventDefault();
        alert('show location overlay!');
      },
      
      //if the user clicks near the 'interaction icons (comments, location)', prevent from going into 'detail mode'
      interactionIconsClicked: function(event) {
        event.stopPropagation();
      },
      
      //keep track of our album id & current photo id?
      updateRouter: function() {
        var curPhoto = this.collection.at(this.pageNum);
        var photoId = curPhoto ? curPhoto.id : 0;
        TIM.app.navigate("/photos/" + this.album.id + "/" + photoId, {replace:true});
      }

  } );
  		
 
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
    var showComments = false;
    if(args[2] && args[2] == "comments" || args[1] && args[1] == "comments") {
      showComments = true;
    }
   
    feature.albumCollection = feature.albumCollection || new TIM.collections.PhotoAlbums();
    feature.mainCollection = feature.mainCollection || new TIM.collections.Photos();
    
    //keep grid/list views hanging around or just use one for each and swap out collections?
    
    //feature.listView = feature.listView || new TIM.views.PhotoList({collection: feature.mainCollection});
    feature.albumListView = feature.albumListView || new TIM.views.PhotoAlbumList({collection: feature.albumCollection});
    
    if(!feature.hasFetchedCollection) {
      
      //this gets the photo albums for the author
      //it should be paged via (perhaps) infinite scroll
      
      //call fetch here
      //let's try the jsonp plugin here...
      feature.albumCollection.fetch({
  			success: function(model, resp) {
  		    //alert('got photos for album!');
  		    feature.hasFetchedCollection = true;
      		feature.showView({albumId: albumId, photoId: photoId, showComments : showComments});
  			},
  			error: function(model, resp) {
          console.log("error: ", resp);
          TIM.eventAggregator.trigger("error", {exception: "Could not load photo albums for this author"});
  			}
  		});
    
  	} else {
  	  feature.showView({albumId: albumId, photoId: photoId, showComments : showComments});
  	}
  };
  
  //always make sure we have a list of albums?
  feature.showView = function(options) {
    if(options.showComments) {
      feature.showCommentsView();
      return;
    }
    if(options.albumId) {
      if(options.photoId) {
        feature.showListView(options);
      } else {
        feature.showGridView(options);
      }
    } else {
      feature.showAlbumListView();
    }
  }
  
  //be sure to specify the proper transition
  feature.showAlbumListView = function(options) {
    options = options || {};
    TIM.transitionPage (feature.albumListView.$el);
  }
  
  //show the list view for an album
  //this is the 'flippable' view with one photo per page
  //
  //when coming here 'out of nowhere', maybe have an animation where it flips a bit to give a visual indication that this is 'flippable'
  
  feature.showListView = function(options) {
    
    //do this or else should have the detail view fetch the model?
    //cache models that have already been fetched?
    console.log('show list view: ', options);
    
    TIM.setLoading(true);
    options = options || {};
    TIM.disableScrolling();
    resourceId = options.photoId;
    var album = feature.albumCollection.get(options.albumId);
    var collection = album.photos;
    collection.setURL();
    
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
        var pageNum = model ? collection.indexOf(model) + 1 : 1; //pageNum is 1-based
        listView.goToPage(pageNum);
        TIM.app.navigate('/photos/' + album.id + "/" + resourceId);
        TIM.transitionPage (listView.$el, {"animationName":options.animationName || "fade", "reverse": options.reverse});
        feature.showDetailId = 0;
        feature.showDetails = false;
        TIM.setLoading(false);
     }
    //make this a method with a callback
    if (!album.hasFetchedPhotos) {
      album.photos.fetch({
  			success: function(resp) {
  		    album.hasFetchedPhotos = true;
  		    showView(album);
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
    //don't make a new one each time?
    if (feature.gridView) {
     feature.gridView.close();
    }
    
    feature.gridView = new TIM.views.PhotoGrid({collection: album.photos});
    feature.gridView.album = album;
    
    //have an inner function here so it's available via callback if we have to fetch
    var showView = function () {
      //transition to this view
			//
			feature.gridView.setCollection(album);
      feature.gridView.render();
		  TIM.setLoading(false);
		  
	    TIM.app.navigate('/photos/' + album.id);
	    TIM.transitionPage (feature.gridView.$el, {
	      animationName: "slide", reverse: options.reverse,
	      callback: function() {
	        feature.gridView.resetScrollElem();
	      }
	    });
    }
    
    //make this a method with a callback since it's repeated between the list/grid views
    
    if (!album.hasFetchedPhotos) {
      //album.photos.max = album.get("count");
      //album.photos.setURL(album.get("searchTerm"), album.get("count"));
      album.photos.fetch({
        timeout:25000,
  			success: function(resp) {
          album.hasFetchedPhotos = true;
          showView();
  			},
  		  error: function(resp, err) {
          console.log("error: ", resp, err);
  			}
  		});
    } else {
      //just show the album?
      showView();
    }
  }
  
  //comments view should have...
  //a base resource/event id that it's based on
  //one or more 'comments collections' - one for each 'source'
  //these collections should be 'pageable'
  //
  //the 'comments area' should be (infinitely?) scrollable
  //
  //
  //the comments view has a way to toggle between comments collections per source/service
   
  
  feature.showCommentsView = function (options) {
    options = options || {};
    var resourceId = options.photoId || options.albumId;
  
    feature.commentsView = feature.commentsView || 
      new TIM.views.Comments({
          resourceId:resourceId,
          sources:[{source_name:"facebook", selected:"selected"}, {source_name:"twitter", selected:""}, {source_name:"instagram", selected:""}]
      });
    feature.commentsView.render();
    console.log("comments view:", feature.commentsView);
    TIM.app.navigate('/photos/album/' + resourceId + "/comments");
    TIM.transitionPage (feature.commentsView.$el, {animationName: "slide"});
  }
  
  //add to feature?
  TIM.features.getByName("photos").behavior = feature;
  TIM.loadedFeatures["photos"] = feature; //this is mainly a shorthand for console debugging...
  
  function getAlbumCount(album) {
    var count = 0;
    try {
      count = album.get('post_type_detail').photo_album.photo_count;
    } catch (e) {
      
    }
    return count;
  }
    
  
})(TIM);

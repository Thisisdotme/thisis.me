
/*
the behavior for the photo feature

-a good place to try out the Gridview > Listview > Detailview structure
-the gridview is the initial view
-the listview is the flippable view
-the detailview allows pinching & scrolling & zooming, etc.

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
			  		
  		initialize: function() {
  		  _.extend(this, TIM.mixins.paging);  //give this collection the ability to page  //+ 
  		  this.initializePaging();
  		  //var authorName = 'kitten';
  		  var authorName = TIM.pageInfo.authorFirstName;
  			this.url = "http://api.flickr.com/services/rest/?format=json&jsoncallback=?&method=flickr.photos.search&text="
  			            + authorName 
  			            + "&per_page=" + this.pageSize + "&api_key=8662e376985445d92a07c79ff7d12ff8";
  		  //alert(this.url);
  		},
  		
  		
  		parse: function(resp) {
  		  return (resp.photos.photo);
  		}

  });
  
  //basic placeholder for photo
  //this would be the grid view
  
  TIM.views.PhotoGrid = Backbone.View.extend( {
      id: "photos",
      className: "appPage",
      numRendered: 0,

      initialize: function() {
          _.bindAll(this, "render");
          this.collection.bind( "reset", this.render );
          this.collection.bind('pageLoaded', this.renderNextPageset, this);
      },

  		events: {
  		  "click .thumb": "showFlipView"
  		},


      render: function(){
        var that = this;
        //split the collection into 2
        var photos = this.collection.toJSON();
        var photos_of_author = photos.slice(0,5);
        var photo_stream = photos.slice(5);
        var template_context = {"author":{first_name:TIM.pageInfo.authorFirstName}, "photos_of_author": {photos: photos_of_author}, "photo_stream": {photos: photo_stream}};
        
  		  dust.render("photos", template_context, function(err, out) {
  			  if(err != null) {
  					console.log(err);
  				}
  			  $(that.el).append(out);
  			  that.numRendered = that.collection.length;
  			});
  		  
  		  if(TIM.appContainerElem.find(this.el).length == 0)  {
  			  TIM.appContainerElem.append(this.$el);
  			}
  			
  			this.iScrollElem = new iScroll('photoStreamContainer', { hScroll: false });
  			setTimeout(function () { that.iScrollElem.refresh() }, 500)
  			
  		  if(!feature.showDetails) {
  		    TIM.transitionPage (this.$el);
		    }
  		    		  
      },

      showFlipView: function(event) {
  		  var resourceId = 0;
  		  if (event) {
  		    resourceId = $(event.currentTarget).data('photo_id');
  		  }
  		  feature.showListView(resourceId, {animationName: "slide"});
      },
      
      //figure out the next elements, add those to the grid
      renderNextPageset: function() {
        
        //only render the ones we haven't already rendered
        var photos = this.collection.toJSON();
        photos = photos.slice(this.numRendered);
        var that = this;
      
        var template_context = {"photos": photos};
  		  dust.render("_photoList", template_context, function(err, out) {
  			  if(err != null) {
  					console.log(err);
  				}
  				that.iScrollElem.destroy();
  			  $('#photoStreamContainer > div').append(out);
  			  that.iScrollElem = new iScroll('photoStreamContainer', { hScroll: false });
  			  that.numRendered += photos.length;
  			});
      }
      
  });
  
  
  TIM.views.PhotoList = Backbone.View.extend( {
          
      id: "photoListContainer",
      
      className: "appPage flipMode",
      
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
      
      //add the flip events to the flip mixin
      //this view should have the ability to not be flippable & return back to other modules
      //e.g., if we get here from the highlight or timeline feature
      
      events: {
    			"swiperight" : "showGridView",
    			//"swipeup .flipMode .flip-set" : "flipNext",
    			//"swipedown .flipMode .flip-set" : "flipPrevious",
    			//"click .detailLink" : "toggleMode",
    			//"click .gridLink" : "showGridView",
    			"click img" : "toggleMode"
  		},

      render: function( ) {
        //mixing in FlipSet functionality to this view, so the main purpose of 'render' is to render the flipset
        console.log('rendering photo list view');
        if(!this.hasRendered) {
          this.renderFlipSet();
          this.hasRendered = true;
          this.toolbarView = new TIM.views.Toolbar();
          var toolbarEl = this.toolbarView.render();
          this.$el.append(toolbarEl);
          this.toolbarView.bind('itemClicked', this.toolbarClicked, this);
        }
      },

      showGridView: function(event) {
        if(!this.flipMode) {
          return;
        }
        var that = this;
        feature.showDetails = false;
        //if(feature.listView.$el.is(TIM.previousPageElem)) {
          //history.back();
        //} else {
          TIM.app.navigate("/photos");
          TIM.transitionPage(feature.gridView.$el, {
              animationName: "slide", 
              reverse: true,
              callback: function() {
                feature.gridView.iScrollElem.refresh();
              }
          });
        //}
      },
      
      renderNextPageset: function() {
        this.renderFlipSet();
        //maybe do this a coupld of flips ahead?
        this.flipNext();
        $('#app').removeClass('loading');
      },
      
      toggleMode: function(event) {
  		  this.$el.toggleClass('flipMode');
  		  if(this.flipMode) {
  		    //make an iscroll container
  		    var containerEl = this.$el.find('.photoPage')[0];
  		    if(containerEl) {
  		      this.iScrollElem = new iScroll(containerEl, { zoom: true });
  		    }
  		    this.flipMode = false;
  		  } else {
  		    this.flipMode = true;
  		    this.iScrollElem.destroy();
          this.iScrollElem = null;
  		  }
      },
      
      getCurrentModel: function() {
        return this.collection.at(this.pageNum);
      },
      
      toolbarClicked: function(info) {
        if(info === 'detailLink') {
          this.toggleMode();
        }
        if(info === 'gridLink') {
          this.showGridView();
        }
      }

  } );
  		
  feature.model = new feature.models.Photos();
  
  //maybe have the ability to prefetch collection before actually showing the feature?
  
  feature.activate = function(resourceId) {
    if(resourceId) {
      //go straight to detail view for this resource...
      //load collection first?
      feature.showDetails = true;
      feature.showDetailId = resourceId;
    }
  
    feature.mainCollection = feature.mainCollection || new TIM.collections.Photos();
    
    feature.gridView =  feature.gridView || new TIM.views.PhotoGrid({collection: feature.mainCollection});
    feature.listView = feature.listView || new TIM.views.PhotoList({collection: feature.mainCollection});
    
    //feature.detailView = feature.detailView || new TIM.views.PhotoDetail();
    
    if(!feature.hasFetchedCollection) {
      console.log('fetching collection!'); 
      feature.mainCollection.fetch({
  			dataType: "jsonp",
  			success: function(resp) {
  		    feature.hasFetchedCollection = true;
  		    if (feature.showDetails) {
  		      feature.showDetailView();
  		    }
  			},
  			error: function(resp) {
          console.log("error: ", resp);
  			}
  		});
  	} else {
  	  if (feature.showDetails) {
  	    if (feature.hasFetchedCollection) {
  	      feature.showDetailView(resourceId);
  	    }
  	  } else {
  	    TIM.enableScrolling();
  	    TIM.transitionPage (feature.gridView.$el);
  	  }
  	}
  };
  
  //maybe have methods to show detail view, show list view, show grid view?
  //in this case, resourceId is the ID of the first resource to show
  feature.showListView = function(resourceId, options) {
    //do this or else should have the detail view fetch the model?
    //cache models that have already been fetched?
    options = options || {};
    TIM.disableScrolling();
    resourceId = resourceId || feature.showDetailId;
    var model = feature.mainCollection.find(function(model){return model.get('id') == resourceId});
	  if(model) {
	    console.log('have a model for the resource: ', model);
	    feature.listView.model = model;
	    
		  feature.listView.render();
		  
		  var pageNum = model ? feature.mainCollection.indexOf(model) : 0;
		  feature.listView.goToPage(pageNum);
		  
		  TIM.transitionPage (feature.listView.$el, {"animationName":options.animationName || "fade", "reverse": options.reverse});
		  feature.showDetailId = 0;
		  feature.showDetails = false;
		} else {
		  console.log("can't find a model for the resource, heading back to the main view", resourceId, feature.photoCollection);
		  feature.showDetailId = 0;
		  feature.showDetails = false;
		  TIM.app.navigate("/photos", {trigger: true}); //if we can't find the resource, just go the default feature view
		}
  }
  
  //show the grid view
  feature.showGridView = function() {
    
  }
  
  
  feature.showDetailView = function(resourceId, options) {
    resourceId = resourceId || feature.showDetailId;
    options = options || {};
    var model = feature.mainCollection.find(function(model){return model.get('id') == resourceId});
	  if(model) {
	    feature.detailView.model = model;
	    feature.detailView.render();
	    TIM.transitionPage (feature.detailView.$el, {"animationName":options.animationName || "fade", "reverse": options.reverse});
	  } else {
	    feature.showDetailId = 0;
		  feature.showDetails = false;
		  TIM.app.navigate("/photos", {trigger: true}); //if we can't find the resource, just go the default feature view
	  }
  }
  
  //add to feature?
  TIM.features.getByName("photos").behavior = feature;
  
  TIM.loadedFeatures["photos"] = feature;
  
  
})(TIM);

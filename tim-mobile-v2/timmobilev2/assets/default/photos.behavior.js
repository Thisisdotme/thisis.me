
(function(TIM) {
  var feature = {};
  feature.models = {};
  feature.views = {};
  feature.collections = {};
  feature.showDetails = false;
  feature.showDetailId = 0;
  
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

    //show?  

  });
  
  TIM.models.Photo = Backbone.Model.extend({

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


  TIM.collections.Photos = Backbone.Collection.extend({
  	 	model: TIM.models.Photo,
  		url: TIM.apiUrl + 'authors/' + TIM.pageInfo.authorName + '/photos?callback=?',
  		initialize: function() {
  		
  		},
  		
  		parse: function(resp) {
  		  return (resp.photos);
  		}

  });
  
  //basic placeholder for photo
  TIM.views.Photos = Backbone.View.extend( {
      id: "photos",
      className: "appPage",

      initialize: function() {
          //_.bindAll(this, "render", "renderPage");
      },

  		events: {
  		  "click .thumb": "showDetail"
  		},
  		
  		parse: function(data) {
  		  return (data.photos_of_author);
  		},


      render: function(){
        var that = this;
  		  dust.render("photos", fakePhotoData, function(err, out) {
  			  if(err != null) {
  					console.log(err);
  				}
  			  $(that.el).append(out);
  			});
  		  
  		  if(TIM.appContainerElem.find(this.el).length == 0)  {
  			  TIM.appContainerElem.append(this.$el);
  			}
  		  TIM.transitionPage (this.$el);
      },

      showDetail: function(event) {
  		  if (event) {
  		    console.log('detail click event: ', event);
  		    feature.showDetailId = $(event.currentTarget).data('photo_id');
  		    //event.stopPropagation();
  		  }
  		  feature.showDetailViewFn();
  		  return;
  		  //var model = this.collection.find(function(model){return model.get('photo_id') == feature.showDetailId})
  		  //if(model) {
  		    console.log('have a model for the detail');
  		    //feature.detailView.collection = this.collection;
  		    if(!feature.detailView.hasRendered); {
    		    feature.detailView.render();
    		    
    		    
    		  }
    		  feature.detailView.pageNum = 0;
    		  var model = this.collection.find(function(model){return model.get('photo_id') == feature.showDetailId});
    		  var pageNum = model ? this.collection.indexOf(model) : 0;
    		  feature.detailView.goToPage(pageNum);
    		  TIM.app.navigate("/photos/" + feature.showDetailId);
    		  TIM.transitionPage ($('#photoDetailContainer'), {"animationName":"slide"});
    		//} else {
    		  //console.log("can't find a model for the detail");
    		//}
      }
  });
  
  //this view would be part of a flipset??!?!?  yep... maybe you'd make a separate request to get more details
  //it should have a collection and not just one modelll...
  
  TIM.views.PhotoDetail = Backbone.View.extend( {
      id: "photoDetailContainer",

      className: "appPage",
      
      pageTemplate: "photoDetail",
      
      hasRendered: false,

      initialize: function(spec) {
          _.bindAll(this);
          if(TIM.appContainerElem.find(this.el).length == 0)  {
    			  TIM.appContainerElem.append(this.$el);
    			}
      },

      events: {
    			"swiperight" : "showListView",
    			"swipeup .flip-set" : "flipNext",
    			"swipedown .flip-set" : "flipPrevious"
  		},

      render: function( ) {
        //mixing in FlipSet functionality to this view, so the main purpose of 'render' is to render the flipset
        //should renderFlipSet take some sort of options (templates, etc.... probably!!!!!!!!!!!$!#@#!%#%!#@!)
        
        this.renderFlipSet();
        this.hasRendered = true;
        
        /*
        
  			var that = this;
  			dust.render("photoDetail", this.model.toJSON(), function(err, out) {
  			  if(err != null) {
  					console.log(err);
  				}
  			  $(that.el).html(out);
  			});	*/
      },

      showListView: function(event) {
        feature.showDetailView = false;
        TIM.app.navigate("/photos");
        TIM.transitionPage($('#photos'), {animationName: "slide", reverse: true});
      },
      
      expandCaption: function(event) {
        //alert ("hey!  you can't do that!");
      }

  } );
  
  //add flipset functionality to the Photo list view
  _.extend(TIM.views.PhotoDetail.prototype, TIM.mixins.flipset);  

  		
  
  feature.model = new feature.models.Photos();
  
  feature.activate = function(resourceId) {
    
    if(resourceId) {
      //go straight to detail view for this resource...
      //load collection first?
      feature.showDetailView = true;
      feature.showDetailId = resourceId;
    }
    
    var photoList = new TIM.collections.Photos(fakePhotoData.photos_of_author.concat(fakePhotoData.photo_stream));
    var photosView = new TIM.views.Photos({collection: photoList});
    feature.listView = photosView;
    feature.detailView = feature.detailView || new TIM.views.PhotoDetail({collection: photoList});
    feature.photoCollection = photoList;
    console.log('hey!  this is the feature view!', feature.detailView);
    
    photosView.render();
    
    if (feature.showDetailView) {
	    //TIM.transitionPage ($("#detailContainer"));
	    //feature.timelineView.showDetail();
	    feature.showDetailViewFn(resourceId);
	  } else {
	    //feature.timelineView.showDetail();
	    TIM.enableScrolling();
	    TIM.transitionPage (feature.listView.$el);
	  }
    
    //also prerender (but don't show) the 
  };
  
  //maybe have methods to show detail view, show list view, show grid view?
  feature.showDetailViewFn = function(resourceId) {
    //do this or else should have the detail view fetch the model?
    //cache models that have already been fetched?
    console.log(feature.photoCollection, resourceId);
    TIM.disableScrolling();
    resourceId = resourceId || feature.showDetailId;
    var model = feature.photoCollection.find(function(model){return model.get('photo_id') == resourceId});
	  if(model) {
	    console.log('have a model for the detail');
	    feature.detailView.model = model;
	    console.log('model: ', model);
	    
		  feature.detailView.render();
		  
		  var pageNum = model ? feature.photoCollection.indexOf(model) : 0;
		  feature.detailView.goToPage(pageNum);
		  
		  TIM.transitionPage (feature.detailView.$el, {"animationName":"slide"});
		  feature.showDetailId = 0;
		  feature.showDetailView = false;
		} else {
		  console.log("can't find a model for the detail");
		  //go staight to the list view
		  //TIM.transitionPage (this.$el, {"animationName":"fade"});
		}
  }
  
  feature.navigate = function() {
    //TIM.app.navigate("/photos");
  }
  
  //add to feature?
  TIM.features.getByName("photos").behavior = feature;
  
  TIM.loadedFeatures["photos"] = feature;
  
  var fakePhotoData = { author:{first_name:TIM.pageInfo.authorFirstName}, 
                        photos_of_author:[{src:"/img/sample_photos/img_1.png",caption:"Yes, Phil's having one hell of a bad hair day, but you would too if you had to talk to VCs all day. Ugh! Those people are despicable -- truly the dregs from the cesspool of human waste that is this sordid Valley.",photo_id:1001}, 
                                          {src:"/img/sample_photos/img_2.png",caption:"This photo is slightly different than the other one.",photo_id:1002}, 
                                          {src:"/img/sample_photos/img_3.png",caption:"A magnificent day for cycling!  Taken October 4, 2011 with my Polaroid DX-2000.",photo_id:1003}, 
                                          {src:"/img/sample_photos/img_4.jpg",caption:"Now this is a real cycle!",photo_id:1004} ,
                                          {src:"/img/sample_photos/img_5.jpg",caption:"Check out my dope new tattoos!",photo_id:1005}],
                        photo_stream:[{src:"/img/sample_photos/img_6.jpg",caption:"Weird!",photo_id:1006}, 
                                      {src:"/img/sample_photos/img_1.png",caption:"hey!",photo_id:1007}, 
                                      {src:"/img/sample_photos/img_1.png",caption:"hey!",photo_id:1007},
                                      {src:"/img/sample_photos/img_1.png",caption:"hey!",photo_id:1009}, 
                                      {src:"/img/sample_photos/img_1.png",caption:"hey!",photo_id:1010}, 
                                      {src:"/img/sample_photos/img_1.png",caption:"hey!",photo_id:1011},
                                      {src:"/img/sample_photos/img_1.png",caption:"hey!",photo_id:1012}, 
                                      {src:"/img/sample_photos/img_1.png",caption:"hey!",photo_id:1013}, 
                                      {src:"/img/sample_photos/img_1.png",caption:"hey!",photo_id:1014}]
                      }
  
  
})(TIM);

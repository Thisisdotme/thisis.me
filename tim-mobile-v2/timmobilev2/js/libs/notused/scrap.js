//no landscape mode hack?
if(false) {
  $(window)    
    .bind('orientationchange', function(){
         if (window.orientation % 180 == 0){
             $(document.body).css("-webkit-transform-origin", "")
                 .css("-webkit-transform", "");               
         } 
         else {                   
             if ( window.orientation > 0) { //clockwise
               $(document.body).css("-webkit-transform-origin", "200px 190px")
                 .css("-webkit-transform",  "rotate(-90deg)");  
             }
             else {
               $(document.body).css("-webkit-transform-origin", "280px 190px")
                 .css("-webkit-transform",  "rotate(90deg)"); 
             }
         }
     })
    .trigger('orientationchange');
}
function reorient(e) {
    var portrait = (window.orientation % 180 == 0);
    $("body > div").css("-webkit-transform", !portrait ? "rotate(-90deg)" : "");
  }
  //window.onorientationchange = reorient;
  //window.setTimeout(reorient, 0);
  
  
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


  //use this to control the main app view
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
		
//from photo detail render:


/*

var that = this;
dust.render("photoDetail", this.model.toJSON(), function(err, out) {
  if(err != null) {
		console.log(err);
	}
  $(that.el).html(out);
});	*/


//from photos collection:

/*	sync: function (method, model, options) {

			params = _.extend({
			type: 'GET',
			dataType: 'jsonp',
			jsonpCallback: 'callback',
			data: decodeURIComponent('&page=' + this.page),
			url: this.url,
			processData: false
		}, options);

		return $.ajax(params);
	}, */
	
	/*
	
	parse: function(response) {
	  //return (data.photos_of_author);
	  console.log('flickr returned: ', response);
	  return response.photos;
	},
	
	*/
	
	
//models we're not using (yet)

TIM.models.Service = Backbone.Model.extend({

  // Default attributes 
  defaults: {
  },

  initialize: function() {
  },

  clear: function() {
    this.destroy();
  }

});

TIM.models.Profile = Backbone.Model.extend({
	url: function() {
			return TIM.apiUrl + 'authors/' + this.get('authorName') + '/features/linkedin/profile?callback=?';
	},
	
  // Default attributes 
  defaults: {
		authorName : 'ken',
		first_name: '',
		last_name: '',
		headline: 'Founder and CEO',
		industry: '',
		location: '',
		name: '',
		pictureUrl: 'https://fbcdn-profile-a.akamaihd.net/static-ak/rsrc.php/v1/yo/r/UlIqmHJn-SK.gif',
		profileUrl: '',
		profileIcon: '/img/social_icons/linkedin.png',
		specialties: '',
		summary: 'Placeholder summary '
  },

  initialize: function() {
  
	},

  clear: function() {
    this.destroy();
  }

});

TIM.models.Author = Backbone.Model.extend({

  // Default attributes 
  defaults: {
  },

  initialize: function() {
  },

  clear: function() {
    this.destroy();
  }

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

//just trying this out to test out subclassing...

TIM.models.LinkedInEvent = TIM.models.Event.extend({

  // Default attributes 
  defaults: {
		featureName: "linkedIn"
  }

});

//collections not used yet...


TIM.collections.Authors = Backbone.Collection.extend({
	 	model: TIM.models.Author,
		url: TIM.apiUrl + 'authors',
		parse: function(resp) {
		  return (resp.authors);
		}
});


TIM.collections.Profiles = Backbone.Collection.extend({
	 	model: TIM.models.Profile
});
	
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
                                      
                                      
/*  from the photo behavior */

//this is the view where you can zoom/scroll the photo
// it is *not* the flipboard view

TIM.views.PhotoDetail = Backbone.View.extend( {
        
    id: "photoDetailContainer",
    
    className: "app-page",
    
    iScrollElem: undefined,
    
    pageTemplate: "photoDetail",
    
    hasRendered: false,

    initialize: function(spec) {  
        _.bindAll(this);
        
        if(TIM.appContainerElem.find(this.el).length == 0)  {
  			  TIM.appContainerElem.append(this.$el);
  			}
    },

    events: {
  			"click .listLink" : "showListView",
  			"click img" : "showListView",
  			"click .gridLink" : "showGridView"
		},

    render: function( ) {
      var that = this;
      //if(!this.hasRendered) {
        var template_context = {photo: this.model.toJSON()};
        console.log(this.model);
        dust.render(this.pageTemplate, template_context, function(err, out) {
  			  if(err != null) {
  					console.log(err);
  				}
  			  $(that.el).html(out);
  			});
        //this.hasRendered = true;
        this.iScrollElem = new iScroll('photoContainer', { zoom: true });
      //}
    },

    showListView: function(event) {
      var that = this;
      feature.showDetails = false;
      var resourceId = 0;
      if (event) {
		    resourceId = this.model.get("id");
		  }
		  TIM.app.navigate("/photos");
		  feature.showListView(resourceId, {reverse:true, animationName:"flip"});
      
      //if(feature.listView.$el.is(TIM.previousPageElem)) {
        //history.back();
      //} else {
        /*
        TIM.app.navigate("/photos");
        TIM.transitionPage(feature.listView.$el, {
            animationName: "slide", 
            reverse: true,
            callback: function() {
              //feature.listView.iScrollElem.refresh();
            }
        });
      //} */
    },
    
    showGridView: function(event) {
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
      }
} );


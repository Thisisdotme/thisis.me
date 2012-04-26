
(function(TIM) {
  console.log('tim: ', TIM);
  var feature = {};
  feature.models = {};
  feature.views = {};
  feature.collections = {};
  
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
      el: $( "#timeline" ),

      initialize: function() {
          //_.bindAll(this, "render", "renderPage");
      },

  		events: {
  		},


      render: function(){
  		  $(this.el).html('photo feature');
      }
  });

  		
  
  feature.model = new feature.models.Photos();
  
  feature.activate = function() {
    var photoList = new (TIM.collections.Photos);
    var photosView = new TIM.views.Photos({collection: photoList});
    photosView.render();
  };
  
  TIM.loadedFeatures["photos"] = feature;
  
})(TIM);

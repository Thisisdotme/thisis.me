
(function(TIM) {
  console.log('tim: ', TIM);
  var feature = {};
  feature.models = {};
  feature.views = {};
  feature.collections = {};
  
  feature.models.Cover = TIM.models.FeatureBehavior.extend({
    initialize: function() {
      this.constructor.__super__.initialize.apply(this, arguments);
    },
    // Default attributes 
    defaults: {
  		name: "bio"
    },

    navigate: function() {
      TIM.app.navigate("/bio");
    }

    //show?  

  });
  
  TIM.models.Cover = Backbone.Model.extend({

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
  
  //basic placeholder for photo
  TIM.views.Cover = Backbone.View.extend( {
      el: $( "#timeline" ),

      initialize: function() {
          //_.bindAll(this, "render", "renderPage");
      },

  		events: {
  		},

      render: function(){
  		  $(this.el).html('cover feature');
      }
  });

  		
  
  feature.model = new feature.models.Cover();
  
  feature.activate = function() {
    var coverModel = new (TIM.models.Cover);
    var coverView = new TIM.views.Cover({model: coverModel});
    coverView.render();
  };
  
  TIM.loadedFeatures["cover"] = feature;
  
})(TIM);

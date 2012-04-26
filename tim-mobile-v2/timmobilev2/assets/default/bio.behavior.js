
(function(TIM) {
  console.log('tim: ', TIM);
  var feature = {};
  feature.models = {};
  feature.views = {};
  feature.collections = {};
  
  feature.models.Bio = TIM.models.FeatureBehavior.extend({
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
  
  TIM.models.Bio = Backbone.Model.extend({

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
  TIM.views.Bio = Backbone.View.extend( {
      el: $( "#timeline" ),

      initialize: function() {
          //_.bindAll(this, "render", "renderPage");
      },

  		events: {
  		},

      render: function(){
  		  $(this.el).html('bio feature');
      }
  });

  		
  
  feature.model = new feature.models.Bio();
  
  feature.activate = function() {
    var bioModel = new (TIM.models.Bio);
    var bioView = new TIM.views.Bio({model: bioModel});
    bioView.render();
  };
  
  TIM.loadedFeatures["bio"] = feature;
  
})(TIM);

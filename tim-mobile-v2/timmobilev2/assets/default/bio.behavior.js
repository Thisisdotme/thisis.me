
(function(TIM) {
  var feature = {};
  feature.models = {};
  feature.views = {};
  feature.collections = {};
  feature.hasFetchedModel = false;
  
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
    
    url: TIM.apiUrl + 'authors/' + TIM.pageInfo.authorName + '/services/linkedin/profile',
    
    parse: function(resp) {
      console.log(resp);
		  return (resp);
		},
    
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
      id: "bio-page",
      
      className: "app-page",
      
      hasRendered: false,
      
      iScrollElem: undefined,

      initialize: function() {
          _.bindAll(this, "render");
          this.model.bind( "change", this.render );
      },

  		events: {
  		},
  		
      render: function(){
        var that = this;
        if(!this.hasRendered) {
          dust.render("bio", this.model.toJSON(), function(err, out) {
    			  if(err != null) {
    					console.log(err);
    				}
    			  $(that.el).append(out);
    			});
    			this.hasRendered = true;
        }

  		  if(TIM.appContainerElem.find(this.el).length == 0)  {
  			  TIM.appContainerElem.append(this.$el);
  			}
  			var containerEl = this.$el.find('.bio')[0];
  			this.iScrollElem = new iScroll(containerEl, { hScroll: false });
  		  TIM.transitionPage (this.$el, {
  		      callback: function() {
              that.iScrollElem.refresh();
            }
        });
      }
  });

  		
  
  feature.model = new feature.models.Bio();
  
  feature.activate = function() {
    feature.bioModel = feature.bioModel || new (TIM.models.Bio);
    console.log("the bio model: " + feature.bioModel);
    feature.bioView = feature.bioView || new TIM.views.Bio({model: feature.bioModel});
    if(!feature.hasFetchedModel) {
      feature.bioView.model.fetch ({
        dataType: "jsonp",
  	  	//add this timeout in case call fails...
    		timeout : 5000,
    		success: function(resp) {
    		  //
    		  console.log('fetched bio');
    		},
    		error: function(resp) {
    			TIM.eventAggregator.trigger("error", {exception:"couldn't find profile for " + TIM.pageInfo.authorName});
    		}
    	});
    	feature.hasFetchedModel = true;
    } else {
      feature.bioView.render();
    }

  };
  
  feature.navigate = function() {
    TIM.app.navigate("/bio");
  }
  
  //add to feature?
  TIM.features.getByName("bio").behavior = feature;
  
  TIM.loadedFeatures["bio"] = feature;
  
})(TIM);


(function(TIM) {
  var feature = {};
  feature.models = {};
  feature.views = {};
  feature.collections = {};
  feature.hasFetchedModel = false;
    
  TIM.models.Bio = Backbone.Model.extend({
    
    url: TIM.apiUrl + 'authors/' + TIM.pageInfo.authorName + '/profile',
    
    parse: function(resp) {
		  return (resp);
		},
    
    initialize: function() {
    },
	
    clear: function() {
      this.destroy();
      this.view.remove();
    }
    

  });
  
  TIM.views.Bio = Backbone.View.extend( {
      id: "bio-page",
      
      className: "app-page toolbar-top",
      
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
          var templateContext =  this.model.toJSON();
          
          if (TIM.pageInfo.authorName === "mchammer") {
            if(!templateContext.summary) {
              templateContext.summary = "Stanley Kirk Burrell, better known by his stage name MC Hammer, is an American rapper, entrepreneur, and actor. " +
                                        "He had his greatest commercial success and popularity from the late 1980s until the mid-1990s. " +
                                        "MC Hammer was born in Oakland, California. He was raised by his mother, along with his eight brothers and sisters, He would spend much of his childhood dancing in the Oakland Coliseum parking lot, to a beatbox, or selling stray baseballs.";
            }
          }
          
          var html = TIM.views.renderTemplate("bio", templateContext);
          this.$el.append(html);
          this.hasRendered = true;
        }

  		  if(TIM.appContainerElem.find(this.el).length == 0)  {
  			  TIM.appContainerElem.append(this.$el);
  			}
  			var containerEl = this.$el.find('.bio')[0];
  			containerEl.style.height = TIM.viewportHeight_ - 10 + "px";
  			this.iScrollElem = new iScroll(containerEl, { hScroll: false });
  		  TIM.transitionPage (this.$el, {
  		      callback: function() {
              that.iScrollElem.refresh();
            }
        });
      }
  });
  
  feature.activate = function() {
    feature.bioModel = feature.bioModel || new (TIM.models.Bio);
    feature.bioView = feature.bioView || new TIM.views.Bio({model: feature.bioModel});
    if(!feature.hasFetchedModel) {
      feature.bioView.model.fetch ({
        dataType: "jsonp",
  	  	//add this timeout in case call fails...
    		timeout :10000,
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


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
              /*templateContext.summary = "Stanley Kirk Burrell, better known by his stage name MC Hammer, is an American rapper, entrepreneur, and actor. " +
                                        "He had his greatest commercial success and popularity from the late 1980s until the mid-1990s. " +
                                        "MC Hammer was born in Oakland, California. He was raised by his mother, along with his eight brothers and sisters, He would spend much of his childhood dancing in the Oakland Coliseum parking lot, to a beatbox, or selling stray baseballs."; */
             templateContext.bio =[];
             templateContext.picture_url = "/img/hammer_thumb.jpg";
             templateContext.name = "MC Hammer";
             templateContext.location = "Bay Area, California";
             templateContext.summary = "Three-time Grammy Award winner MC Hammer is one of the most prolific recording artists of all time. He has been recognized with numerous industry awards, has managed a record label and has produced a cable" 
                      + " television show, \"Hammertime\" on A&E. In addition to his international music and entertainment success, Hammer has extensive experience working in sports management. In the early 1990's, Hammer managed "
                      + "one of the all-time greatest fighters, Evander Holyfield, to the world heavyweight boxing championship. ";

              templateContext.bio[0] =  {text:"Hammer has represented a number of other top professional athletes during their careers. Recently, Hammer became one of the most influential figures on the social media platform Twitter" 
                       + "with over 2.7 million followers. He has been a featured speaker covering social media and business at top colleges and universities such as the business schools at Stanford University" 
                       + "and at Harvard University. He is CEO of Alchemist Management, Founder and Chief Strategy Officer of DanceJam.com, and Co-Founder of WireDoo"
                       + "- a \"deep search\" engine that is planned to compete with major search engines including Google and Bing."};

              templateContext.bio[1] = {text:"Hammer is a native of Oakland California. He and his wife Stephanie have been married for 24 years and they have 6 children."};
              
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
    		timeout :TIM.pageInfo.authorName === "mchammer" ? 20 : 4000,
    		success: function(resp) {
    		  //
    		  console.log('fetched bio');
    		},
    		error: function(resp) {
    		  if (TIM.pageInfo.authorName === "mchammer") {
    		    feature.bioView.render(); 
    		  } else {
    		    feature.bioView.render();
    		  }
    			//TIM.eventAggregator.trigger("error", {exception:"couldn't find profile for " + TIM.pageInfo.authorName});
    			 //just render a fake bio for now for hammer
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

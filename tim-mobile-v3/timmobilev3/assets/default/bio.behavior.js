
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
          //this.model.bind( "change", this.render );
      },

  		events: {
  		},
  		
      render: function(options){
        options = options || {};
        var that = this;
        if(!this.hasRendered) {
          var templateContext =  this.model.toJSON();
          
          if (TIM.pageInfo.authorName === "mchammer") {
            if(!templateContext.summary) {
              templateContext.bio =[];
             templateContext.picture_url = "/img/hammer_thumb.jpg";
             templateContext.name = "MC Hammer";
             templateContext.location = "Bay Area, California";
             templateContext.summary = "Three-time Grammy Award winner MC Hammer is one of the most prolific recording artists of all time. He has been recognized with numerous industry awards, has managed a record label and has produced a cable" 
                      + " television show, \"Hammertime\" on A&E. In addition to his international music and entertainment success, Hammer has extensive experience working in sports management. In the early 1990's, Hammer managed "
                      + "one of the all-time greatest fighters, Evander Holyfield, to the world heavyweight boxing championship. ";

              templateContext.bio[0] =  {text:"Hammer has represented a number of other top professional athletes during their careers. Recently, Hammer became one of the most influential figures on the social media platform Twitter" 
                       + " with over 2.7 million followers. He has been a featured speaker covering social media and business at top colleges and universities such as the business schools at Stanford University" 
                       + " and at Harvard University. He is CEO of Alchemist Management, Founder and Chief Strategy Officer of DanceJam.com, and Co-Founder of WireDoo"
                       + "- a \"deep search\" engine that is planned to compete with major search engines including Google and Bing."};

              templateContext.bio[1] = {text:"Hammer is a native of Oakland California. He and his wife Stephanie have been married for 24 years and they have 6 children."};
              
            }
          }
          
          //make a fallback picture_url
          templateContext.picture_url = templateContext.picture_url || "/img/default_profile_thumb.jpg";
          
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
  		        window.setTimeout(function(){that.iScrollElem.refresh()}, 200);
              
              if(options.error) {
                //alert(options);
                TIM.eventAggregator.trigger("error", {exception:"couldn't find profile for " + TIM.pageInfo.authorName});
              }
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
        callbackParameter: "callback",
  	  	//add this timeout in case call fails...
    		timeout: TIM.pageInfo.authorName === "mchammer" ? 20 : 4000,
    		success: function(resp) {
    		  //
    		  console.log('fetched bio');
    		  feature.bioView.render(); 
    		},
    		error: function(model, resp) {
    		  if (TIM.pageInfo.authorName === "mchammer") {
    		    feature.bioView.render(); 
    		  } else {
    		    feature.bioView.render({error: resp});
    		  }
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

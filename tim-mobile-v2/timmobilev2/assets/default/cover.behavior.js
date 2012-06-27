
(function(TIM) {
  var feature = {};
  feature.models = {};
  feature.views = {};
  feature.collections = {};
  feature.collectionLoaded = false;
  
  TIM.models.TopStory = Backbone.Model.extend({

    defaults: {
    },

    initialize: function() {
    },
	
    clear: function() {
      this.destroy();
      this.view.remove();
    }

  });
  
  //get top stories
  
  TIM.collections.TopStories = Backbone.Collection.extend({
  		//setting which subclass the model is here?  not sure if this is necessary....
  	 	model: TIM.models.TopStory,
  		url: TIM.apiUrl + 'authors/' + TIM.pageInfo.authorName + '/topstories?callback=?',
  		initialize: function() {
  		},
  		//could also subclass in parse?
  		parse: function(resp) {
  		  return (resp.events);
  		}

  });
  
  
  //basic placeholder for photo
  TIM.views.Cover = Backbone.View.extend( {
      id: "cover-container",
      
      className: "app-page",
      
      events: {
        "vclick .highlight" : "showHighlight",
        "vclick a" : "linkClicked"
        
      },
      
      hasRendered: false,

      initialize: function() {
          _.bindAll(this, "render");
          this.collection.bind( "reset", this.render, this);
      },

      render: function( collection ) {
  				var that = this;
          if(!TIM.appContainerElem.find(this.$el).length)  {
            TIM.appContainerElem.append(this.$el);
    			}
  				$(this.el).html('');
  				var out = "";
  				/*
  				  transform data structure into something that corresponds to cover info
  				  //name, primaryStory, secondaryStory ... the explicitly named primary, secondary, etc. are probably stupid
  				  -should really just have it as an array, iterate & append the index to the classname
  				  -handle display location, etc. in the css
  				  -should we truncate, etc. here or in the template?
  				  -this is a good place for the jquery text sizer thingy?
  				*/
  				var name = this.collection.at(0) ? this.collection.at(0).get('author').full_name : TIM.pageInfo.authorFullName;
  				//alert(name);
  				window.n = name;
  				var context = {
  				  name: name,
  				  first_name: name.split(' ')[0],
  				  last_name: name.split(' ')[1] || '',
  				  primaryStory: this.collection.at(0) ? this.collection.at(0).toJSON() : [],
  				  secondaryStory: [], //this.collection.at(1) ? this.collection.at(1).toJSON() : [],
  				  tertiaryStory: [], //this.collection.at(2) ? this.collection.at(2).toJSON() : [],
  				}
  				console.log ("cover story:", context.primaryStory);
  				//this pattern could probably be generalized to a basic TIM view
  				if(!this.hasRendered) {
            var html = TIM.views.renderTemplate("coverpage", context);
            this.$el.append(html);
            this.hasRendered = true;
          }
          TIM.transitionPage(that.$el, {animationName:"fade"});
          //TIM.setLoading(true);
          if(name.length === 2) {
            $("#first-name").fitText(.3);
        		$("#last-name").fitText(.5);
          }
          

      },
      
      showHighlight: function(event) {
        //load highlight feature if necessary
        //navigate to that highlight
        //going to default to the timeline feature for now since we don't know if it's a highlight or photo or regular event, etc.
        event.preventDefault();
        event.stopPropagation();
        
        if($(event.currentTarget).tagName == "a" || $(event.relatedTarget).tagName == "a") {
          return;
        }
        TIM.eventAggregator.trigger('detailLinkClicked', $(event.currentTarget).data('event_id'), 'timeline');
      },
      
      linkClicked: function(event) {
        $(window).off('resize');
        event.preventDefault();
        event.stopPropagation(); //let the global handler for link clicks take care of it!
        TIM.handleLinkClick(event);
      }
  });
  
  feature.activate = function() {
    
    if(!feature.collectionLoaded) {
      var topStories = new (TIM.collections.TopStories);
      var coverView = new TIM.views.Cover({collection: topStories});
      feature.mainView = coverView;
      feature.mainCollection = topStories;
      //TODO - global json fetch method with error handling
      coverView.collection.fetch({
  			dataType: "jsonp",
  			timeout : 10000,
  			success: function(resp) {
  			  feature.collectionLoaded = true;
  			},
  			error: function(resp) {
				  TIM.eventAggregator.trigger("error", {exception: "Could not load cover stories."})
  			}
  		});
    } else {
      TIM.transitionPage ($("#cover-container"));
    }
  };
  
  feature.navigate = function() {
    TIM.app.navigate("/cover");
  }
  
  //add to feature?
  TIM.features.getByName("cover").behavior = feature;
  
  TIM.loadedFeatures["cover"] = feature;
  
})(TIM);

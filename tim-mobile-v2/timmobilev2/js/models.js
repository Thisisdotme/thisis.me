(function ( TIM ) {
  
  TIM.models.FeatureBehavior = Backbone.Model.extend({
    navigate: function() {
      alert("hey!  I'm coming from the behavior superclass! my name is " + this.get('name'));
    }
  });
  
  //change this to featureloader? featurefactory?
	
	TIM.models.Feature = Backbone.Model.extend({
    
    //features loaded from API will extend this
    //should have a loadassets/loadresources method?
    //this would load the template, behavior, css
    //call render when done?
    //initially has attributes from the API list call
    //which would populate the collection?
    
    // Default attributes 
    defaults: {
      templateLoaded: false,
      behaviorLoaded: false,
      styleLoaded: false,
      resourcesLoaded: false
    },

    initialize: function() {
    },

    clear: function() {
      this.destroy();
    },
    
    loadFeature: function() {
      
      //are resources loaded? if not, load them!
      console.log(this);
      if(!this.get("resourcesLoaded")) {
        this.loadResources();
      } else {
        //actually do the navigation
        TIM.loadedFeatures[this.get('feature_name')].model.navigate();
      }
    },
    
    loadResources: function() {
      var self = this;
       //load behavior script, template, stylesheet
      console.log('loading the resources for ' + this.get('feature_name'));
      var featureName = this.get('feature_name');
      
      //feature behavior is an object holding models, views, collections for the feature?
      
      
      //load the behavior
      $.getScript("/" + TIM.pageInfo.authorName + "/asset/" + featureName + ".behavior.js")
        .done(function(data, textStatus, jqxhr) {
         //TIM.loadedModel = new TIM.models.TestNewModel();
         //self.actions.push(TIM.featureHandlers[name]);
         //console.log('history before: ', Backbone.history.handlers);
         //self.route(name, name, function(){ TIM.featureHandlers.Highlights(); });
         //console.log('history after: ', Backbone.history.handlers);
         //
         //console.log('script loaded, new model: ', TIM.loadedModels.);
         self.set('behaviorLoaded', true, {silent:true});
         self.resourceLoaded();
       })
       .fail(function(jqxhr, settings, exception) {
         console.log(exception);
       });
      
      //load the template
      $.getScript("/" + TIM.pageInfo.authorName + "/asset/" + featureName + ".dust.js", function(data, textStatus, jqxhr) {
         self.set('templateLoaded', true, {silent:true});
         self.resourceLoaded();
      });
      
      //load the stylesheet
      //TODO: do this with a callback when the stylesheet is loaded - different browsers handle differently... find plugin?
      $('head').append('<link rel="stylesheet" type="text/css" href="/' + TIM.pageInfo.authorName + '/asset/' + featureName + '.css">');
      self.set('styleLoaded', true, {silent:true});
      self.resourceLoaded();
      
      //this.set('resourcesLoaded', true, {silent: true}) 
    },
    
    //call this when resources have been loaded for this feature:
    //this should navigate to the feature... or should be an option to do that
    resourceLoaded: function() {
      //
      if(this.get("templateLoaded") && this.get("behaviorLoaded") && this.get("styleLoaded")) {
        console.log('in resourceloaded');
        this.set("resourcesLoaded", true, {silent:true});
        this.trigger('loaded', 'true');
        TIM.eventDispatcher.trigger('featureloaded', this);
        this.loadFeature();
      }
    }
    

  });
  
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
	

	
})( TIM );
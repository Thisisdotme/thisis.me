(function ( TIM ) {
  
  TIM.models.FeatureBehavior = Backbone.Model.extend({
    navigate: function() {
      console.log("hey!  I'm coming from the behavior superclass! my name is " + this.get('name'));
    }
  });
  
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
      resourcesLoaded: false,
      selected: false,
      initialResourceId: 0,
      navigateOnLoad: true
    },

    initialize: function() {
      //add route to this feature to router  /<featurename>
      //also add route to detail view to router /<featurename>/<resourceid>
      //could also be /featurename/<listid>/<resourceid>
      
      //if 3 levels, add 3rd route?
      
      var featureName = this.get('feature_name');
      //a route for /<featurename>
      
      TIM.app.route(featureName, featureName); 
      //TIM.app.route(featureName + "/:resource", featureName, function(number){});
      
      //TIM.app.route(featureName + "/:collection/:resource", featureName, function(resource, collection){return 9000}); //we probably have to get way more 'general-purpose' here, but this might (tenuously) do for now?
      TIM.app.route(featureName + "/*path", featureName, function(path){});
      
    },

    clear: function() {
      this.destroy();
    },
    
    loadFeature: function(path) {
      if(path) {
        this.set('initialPath', path);
      }
      if(!this.get("resourcesLoaded")) {
        this.loadResources();
      } else {
        //send an event notifying that the feature has loaded
        TIM.eventAggregator.trigger('featureloaded', {"feature": this, "path": this.get('initialPath'), "navigateOnLoad": this.get('navigateOnLoad')});
      }
    },
    
    loadResources: function() {
      var self = this;
      //load behavior script, template, stylesheet
      var featureName = this.get('feature_name');
      
      //load the behavior
      $.getScript("/" + TIM.pageInfo.authorName + "/asset/" + featureName + ".behavior.js")
        .done(function(data, textStatus, jqxhr) {
         self.set('behaviorLoaded', true, {silent:true});
         //bind these instead of calling?
         self.resourceLoaded();
       })
       .fail(function(jqxhr, settings, exception) {
         //start throwing app-wide error events
         console.log(exception);
         TIM.eventAggregator.trigger('error:featureload', {"feature": this, "resource": "behavior", "exception": exception});
       });
      
      //load the template
      $.getScript("/" + TIM.pageInfo.authorName + "/asset/" + featureName + ".dust.js")
         .done(function(data, textStatus, jqxhr) {
           self.set('templateLoaded', true, {silent:true});
           self.resourceLoaded();
         })
         .fail(function(jqxhr, settings, exception) {
            console.log("template load failed: ", exception);
            TIM.eventAggregator.trigger('error:featureload', {"feature": this, "resource": "template", "exception": exception});
          });
          
      //load the stylesheet
      //TODO: do this with a callback when the stylesheet is loaded - different browsers handle differently... find plugin?
      $('head').append('<link rel="stylesheet" type="text/css" href="/' + TIM.pageInfo.authorName + '/asset/' + featureName + '.css">');
      self.set('styleLoaded', true, {silent:true});
      self.resourceLoaded();
    },
    
    //call this when resources have been loaded for this feature:
    //this should navigate to the feature... or should be an option to do that
    resourceLoaded: function() {
      //
      if(this.get("templateLoaded") && this.get("behaviorLoaded") && this.get("styleLoaded")) {
        this.set("resourcesLoaded", true, {silent:true});
        this.trigger('loaded', 'true');
        this.loadFeature();
      }
    }
  });
	
	
})( TIM );
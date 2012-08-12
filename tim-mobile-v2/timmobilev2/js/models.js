(function ( TIM ) {
  
  TIM.models.AuthenticatedUser = Backbone.Model.extend({
      url: TIM.apiUrl + "login",
      loggedIn: false,
      logoutUrl: TIM.apiUrl + "logout",
      doLogin: function(name, password, callback) {
        
        
          var self = this;
          
          /*
          
          $.post('/login', { name: name, password: password }, function(data) {
            self.set(data); // data should be in JSON and contain model of this user
          }, 'json').error(
            self.trigger('loginError'); // our custom event
          );
          
          */
          
          $.ajax({
            type: 'POST',
            url: this.url,
            data: JSON.stringify({ login: name, password: password}),
            xhrFields: {withCredentials: true},
            contentType: 'application/json',
            success: function(data, xhr) {
               console.log("login response: ", data, status, xhr);
               //do something with the data...
               self.set(data);
               $.cookie('tim_author_name', data.name);
               self.loggedIn = true;
               if(callback) {
                 callback();
               }
               TIM.eventAggregator.trigger('login', {name:data.name});
             },
             error: function(data) {
               console.log("login error: ", data);
               $('.login-form .message').html('Could not find that user name and password.').css('visibility','visible');
               self.trigger('loginError');
             },
            dataType: "json"
          });
        
      },
      doLogout: function(callback) {
        $.ajax({
           type: 'POST',
           url: this.logoutUrl,
           xhrFields: {withCredentials: true},
           contentType: 'application/json',
           success: function(data, xhr) {
              $.removeCookie('tim_author_name');
              if(callback) {
                callback();
              }
              TIM.eventAggregator.trigger('logout', {});
            },
            error: function(data) {
              alert('logout failed!!!');
            },
           dataType: "json"
         });
      },
      createFromCookie: function() {
        //see if there's a session and tim_author_name cookie...
        var authorName = $.cookie('tim_author_name');
        if(authorName) {
          this.set({'name': authorName});
          this.loggedIn = true;
          TIM.eventAggregator.trigger('login', {});
        } else {
          this.loggedIn = false;
          TIM.eventAggregator.trigger('logout', {});
        }
      }
  });
  
  //this was a sort of experimental 'model' to use for a feature's behavior...
  //for now I think it was a case of 'object-oriented overkill', but I'm keeping it here for the moment but not using it
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
      
      var featureName = this.get('name');
      //a route for /<featurename>
      this.set('path', (featureName === "home" ? "/" : "/" + featureName));
      
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
      var featureName = this.get('name');
      
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
  
  //base model for all comments
  TIM.models.Comment  = Backbone.Model.extend({
    
  });
  
  //model for services, e.g. facebook, twitter, etc.
  TIM.models.Service  = Backbone.Model.extend({
    getFooterImage: function() {
      return this.get('color_icon_high_res');
    }
  });
  
  //model for event/post types, e.g. .
  /*
  
  +---------+-------------+
  | type_id | label       |
  +---------+-------------+
  |       1 | highlight   |
  |       2 | photo-album |
  |       3 | photo       |
  |       4 | checkin     |
  |       5 | status      |
  |       6 | follow      |
  |       7 | video       |
  |       8 | video-album |
  |       9 | correlation |
  |      10 | correlation |
  +---------+-------------+
  
  
  */
  
  TIM.models.PostType  = Backbone.Model.extend({
    
  });
  
  TIM.models.Author  = Backbone.Model.extend({
  });
  
  TIM.models.User  = Backbone.Model.extend({
    name: "ken",
    dataType:"jsonp",
    callbackFunction: "callback",
    url: TIM.apiUrl + 'authors/',
    initialize: function(options) {
      this.url = TIM.apiUrl + 'authors/' + this.get('name');
    },
    parse: function(resp) {
		  return (resp.author);
		}
  });
	
	
})( TIM );
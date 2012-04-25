(function ( TIM ) {
	
	TIM.models.Feature = Backbone.Model.extend({

    // Default attributes 
    defaults: {
    },

    initialize: function() {
    },

    clear: function() {
      this.destroy();
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
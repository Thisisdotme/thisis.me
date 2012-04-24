TIM.collections.Features = Backbone.Collection.extend({
	 	model: TIM.models.Feature,
		url: TIM.apiUrl + 'features',
		parse: function(resp) {
		  return (resp.features);
		}
});

TIM.collections.Authors = Backbone.Collection.extend({
	 	model: TIM.models.Author,
		url: TIM.apiUrl + 'authors',
		parse: function(resp) {
		  return (resp.authors);
		}
});

//should this collection have the equivalent of 'paging info', the 'flipset', etc.?
//this should handle both highlights and regular events, right?

TIM.collections.Timeline = Backbone.Collection.extend({
		//setting which subclass the model is here?  not sure if this is necessary....
	 	model: function(attrs) {
			switch(attrs.feature) {
         case "linkedin":
           return new TIM.models.LinkedInEvent(attrs);
           break;
         default:
           return new TIM.models.Event(attrs);
       }
		},
		url: TIM.apiUrl + 'authors/' + TIM.pageInfo.authorName + '/highlights?callback=?',
		//url: TIM.apiUrl + 'authors/' + TIM.authorName + '/groups/follow/events?callback=?',
		initialize: function() {
		},
		//could also subclass in parse?
		parse: function(resp) {
		  return (resp.events);
		}
		
});

TIM.collections.Profiles = Backbone.Collection.extend({
	 	model: TIM.models.Profile
});
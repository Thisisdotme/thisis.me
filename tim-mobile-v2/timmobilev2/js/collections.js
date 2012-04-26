TIM.collections.Features = Backbone.Collection.extend({
	 	model: TIM.models.Feature,
		url: TIM.apiUrl + 'authors/' + TIM.pageInfo.authorName,
		parse: function(resp) {
		  return (resp.author.features);
		}
});

TIM.collections.Authors = Backbone.Collection.extend({
	 	model: TIM.models.Author,
		url: TIM.apiUrl + 'authors',
		parse: function(resp) {
		  return (resp.authors);
		}
});



TIM.collections.Profiles = Backbone.Collection.extend({
	 	model: TIM.models.Profile
});
TIM.collections.Features = Backbone.Collection.extend({
	 	model: TIM.models.Feature,
		url: TIM.apiUrl + 'authors/' + TIM.pageInfo.authorName,
		parse: function(resp) {
		  //this is probably a bad place to o this, but...
		  console.log(resp);
		  TIM.pageInfo.authorFirstName = resp.author.author_name;
		  TIM.pageInfo.authorFullName = resp.author.full_name;
		  return (resp.author.features);
		},
		getByName: function(name) {
		  return this.find(function(model){return model.get('feature_name') == name});
		},
		getSelectedFeature: function() {
		  return this.find(function(model){return model.get('selected') == true});
		},
		setSelectedFeature: function(modelToSelect) {
		  this.each(function(model){
		    model.set('selected', model === modelToSelect);
		  });
		  return modelToSelect;
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
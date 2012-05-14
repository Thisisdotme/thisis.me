TIM.collections.Features = Backbone.Collection.extend({
	 	model: TIM.models.Feature,
		url: TIM.apiUrl + 'authors/' + TIM.pageInfo.authorName,
		parse: function(resp) {
		  //this is probably a bad place to do this, but...
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

//paging for collection as a mixin

TIM.mixins.paging = {
  
  initializePaging: function(options) {
    this.page = 1;
  	this.pageSize = 15 || options.pageSize; 
  },
  
  //get earlier events and append them to the beginning of the collection
  //basically the same as  getNextPage with 'at' set to 0 in the call to 'fetch'
  getPrevPage: function() {
  
  },
  
  getNextPage: function() {
    var that = this;
    this.page++;
    //alert(this.collection.page);
    $('#app').addClass('loading');
    this.fetch({
      add:true,
      data: {page: this.page},
      success: function(coll, resp) {
  		  console.log('first item in collection after fetch: ', coll.at(0).get('id'));
  		  that.trigger("pageLoaded");
  		},
  		error: function(resp) {
        console.log("paging error: ", resp);
  		}
    });
  }
  
}
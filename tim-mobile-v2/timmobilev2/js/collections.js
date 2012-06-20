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

//
// base collections for all comments in teh system
//

TIM.collections.Comments = Backbone.Collection.extend({
	 	model: TIM.models.Comment,
		url: TIM.apiUrl + 'authors/' + TIM.pageInfo.authorName, //obviously this isnt' right... maybe will go to our API, maybe directly to the API of the service, i.e. facebook, twitter, etc.
		
		initialize: function(options) {
		  options = options || {};
		  _.extend(this, TIM.mixins.paging);  //give this collection the ability to page  //+ 
		  this.initializePaging();
		  this.source = options.source; //should be service... a TIM.models.Service?
			//set url for source...
		},
		
});

//
// base collections for all services, eg. facebook, twitter, instagram
//

TIM.collections.Services = Backbone.Collection.extend({
	 	model: TIM.models.Service,
		url: TIM.apiUrl + 'authors/' + TIM.pageInfo.authorName + "/services", //get a list of the services that this author has activated... hm, should probably also keep a list of *all* services
		
		initialize: function(options) {
		  options = options || {};
		},
		
});

//paging for collection as a mixin
//
//have some sort of variable that says whether there's a maximum/total count - after reaching this count, don't try to get the next page?
//

TIM.mixins.paging = {
  
  initializePaging: function(options) {
    options = options || {};
    this.page = 1;
  	this.pageSize = options.pageSize || 15;
  	this.max = options.max || 0; 
  },
  
  //get earlier events and append them to the beginning of the collection
  //basically the same as  getNextPage with 'at' set to 0 in the call to 'fetch'
  getPrevPage: function() {
  
  },
  
  getNextPage: function() {
    var that = this;
    
    if(this.max) {
       if (this.max && this.length >= this.max) {
          console.log("tried to page too far!")
          return;
        }      
    }
  
    this.page++;

    TIM.setLoading(true);
    
    this.fetch({
      add:true,
      dataType:"jsonp",
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
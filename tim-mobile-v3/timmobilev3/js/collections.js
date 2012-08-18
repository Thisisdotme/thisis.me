TIM.collections.BaseCollection = Backbone.Collection.extend( {
   //override 'fetch' globally here
   fetch: function(options) {
     //set some global defaults for fetching
     //
     
     options = options || {};
     options.dataType = options.dataType || "json";
     options.callbackParameter = options.callbackParameter || "callback";
     options.timeout = options.timeout || 25000;
     
     //CORS!
     options.xhrFields = {withCredentials: true};
     options.contentType = 'application/json';
     
     options.error = options.error || function(model, resp) {
       TIM.eventAggregator.trigger("error", {exception: "API call failed"});
     }
    
     return Backbone.Collection.prototype.fetch.call(this, options);
   },
  getByName: function(name) {
	  return this.find(function(model){return model.get('name') == name});
	}
});

TIM.collections.Features = TIM.collections.BaseCollection.extend({
	 	model: TIM.models.Feature,
		url: TIM.apiUrl + 'authors/' + TIM.pageInfo.authorName,
		parse: function(resp) {
		  //this is probably a bad place to do this, but...
		  TIM.pageInfo.authorFirstName = resp.author_name;
		  TIM.pageInfo.authorFullName = resp.full_name;
		  
		  return (resp.features);
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
// base collection for all comments in the system
//

TIM.collections.Comments = TIM.collections.BaseCollection.extend({
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

TIM.collections.Services = TIM.collections.BaseCollection.extend({
	 	model: TIM.models.Service,
		url: TIM.apiUrl + "services", //get a list of the services that this author has activated... hm, should probably also keep a list of *all* services
		initialized: false,
		
		initialize: function(options) {
		  options = options || {};
		},
		parse: function(resp) {
		  console.log('services: ', resp)
		  return (resp.services);
		},
		setURL: function(username) {
		  this.url = TIM.apiUrl + "authors/" + username + "/services";
		},
		getFooterImage : function(name) {
		  var service = this.getByName(name);
		  if (service) {
		    return service.getFooterImage();
		  } else {
		    return "http://mvp2.thisis.me:8080/img/icons/instagram_15.png";
		  }
		}
		
});


//
// base collections for all features, eg. photos, cover, etc.
//

TIM.collections.AppFeatures = TIM.collections.BaseCollection.extend({
	 	model: TIM.models.AppFeature,
		url: TIM.apiUrl + "services", //get a list of the services that this author has activated... hm, should probably also keep a list of *all* services
		initialized: false,
		
		initialize: function(options) {
		  options = options || {};
		},
		parse: function(resp) {
		  console.log('features response: ', resp)
		  return (resp.features);
		},
		getByName: function(name) {
		  return this.find(function(model){return model.get('name') == name});
		},
		setURL: function(username) {
		  this.url = TIM.apiUrl + "authors/" + username;
		}
		
});

TIM.collections.Authors = TIM.collections.BaseCollection.extend({
	 	model: TIM.models.Author,
		url: TIM.apiUrl + "authors", //get a list of the authors in the app
		
		initialize: function(options) {
		  options = options || {};
		},
		parse: function(resp) {
		  return (resp);
		},
		getByName: function(name) {
		  return this.find(function(model){return model.get('name') == name});
		}
});


//
// collection holding all types of posts the ui has to support
//  -e.g. photo, photo-slbum, 
//
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


TIM.collections.PostTypes = TIM.collections.BaseCollection.extend({
	 	model: TIM.models.PostTypes,
		url: TIM.apiUrl + "types",
		
		initialize: function(options) {
		  options = options || {};
		},
		parse: function(resp) {
		  return (resp.types);
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
  //basically the same as getNextPage with 'at' set to 0 in the call to 'fetch'
  getPrevPage: function() {
  
  },
  
  getNextPage: function() {
    
    if (!this.paging.next) {
       this.trigger("noMorePages");
       return;
    }
    
    var that = this;
    
    this.page++;
    this.url = this.paging.next;
    
    TIM.setLoading(true);
    
    this.fetch({
      add:true,
      
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
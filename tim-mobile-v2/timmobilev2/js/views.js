//use this to control the main app view
TIM.views.App = Backbone.View.extend( {
    el: $( "#app_container" ),
		
		events: {
        "click #fetch_authors" : "loadAuthors",
				"click #fetch_events" : "loadEvents"
    },

    initialize: function() {
        
    },
		
		loadAuthors: function() {
			TIM.authorList.collection.fetch({
				dataType: "jsonp"
			});
		},
		
		loadEvents: function() {
			TIM.timelineView.collection.fetch({
				dataType: "jsonp",
				success: function(resp) {
				  
				},
				error: function(resp) {
					
				}
			});
		}

} );

TIM.views.FeatureNav = Backbone.View.extend( {
   el: $( "#featureNav" ),
		
   initialize: function() {
       this.collection.bind( "reset", this.render, this );
   },
   
   addAll : function () {
      this.collection.each (this.addOne);
      //load the default feature here?
   },
		
  addOne : function ( item ) {
  	var view = new TIM.views.FeatureViewItem({model:item});
  	$('#featureNav').append(view.render().el);
  },
		
	 render: function() {
	   this.addAll();
	 }
})

TIM.views.FeatureViewItem = Backbone.View.extend({
	tagName : 'li',

	initialize: function() {
		this.model.bind('change', this.render, this);
		this.model.bind('destroy', this.remove, this);
		this.model.bind('loaded', this.featureLoaded, this);
	},
	
	events: {
		"click" : "loadFeature"
	},

	render : function () {
	  var self = this;
	  dust.render("featureNavItem", this.model.toJSON(), function(err, out) {
		  if(err != null) {
				console.log(err);
			}
		  $(self.el).append(out);
		});
		return this;
	},
	
	loadFeature : function() {
	  this.model.loadFeature();
	},
	
	featureLoaded: function() {
	  //alert('the view knows the feature is loaded!!!!!!!!');
	}
	
}); 



TIM.views.Event = Backbone.View.extend( {

    initialize: function() {
        _.bindAll(this, "render");
        //this.collection.bind( "add", this.addOne );
    },

    render: function( ) {
			var that = this;
			dust.render("event", this.model.toJSON(), function(err, out) {
			  if(err != null) {
			    console.log(err);
			  }
			  $(that.el).append(out);
			});
				
    }
} );

TIM.views.AuthorList = Backbone.View.extend( {
    el: $( "#author_list" ),

    initialize: function() {
        _.bindAll(this, "renderList");
        this.collection.bind( "reset", this.renderList );
    },

    renderList: function( collection ) {
				var that = this;
				
				$(this.el).html('');
				_.each(collection.models, function(model) {
					dust.render("author", model.toJSON(), function(err, out) {
					  if(err != null) {
					    console.log(err);
						}
					  $(that.el).append(out);
					});
				})
        
    }
} );

TIM.views.Profile = Backbone.View.extend( {
    el: $( "#profile_dialog" ),

		model: TIM.models.Profile,
		
		events: {
			'swiperight': 'goBack'
		},

    initialize: function(spec) {
        _.bindAll(this, "render");
				this.model.on('change', this.render, this);
    },

    render: function( ) {
			//toggling this so we will trigger the change event
			//this.model.set("reloading", false);
			console.log('rendering profile!');
			var that = this;
			dust.render("profile", this.model.toJSON(), function(err, out) {
			  if(err != null) {
			    console.log(err);
				}
			  $(that.el).find('.profile_content').html(out);
			});
			//$.mobile.changePage($(this.el));
    },

		goBack: function() {
			history.back();
			return false;
		}
} );

/*
TIM.views.AuthorView = Backbone.View.extend( {
    
		model: TIM.models.Author,

    initialize: function() {
        _.bindAll(this, "render");
    },

    render: function(  ) {
				var that = this;
        dust.render("author", this.toJSON(), function(err, out) {
				  if(err != null)
				    alert("Error loading page");
				  //assume we have jquery
				  $(that.el).html(out);
				});
    }
} );
*/
//extending backbone view object to allow for DOM removal & event unbinding in one call
//see http://lostechies.com/derickbailey/2011/09/15/zombies-run-managing-page-transitions-in-backbone-apps/
Backbone.View.prototype.close = function(){
  this.remove();
  this.unbind();
  if (this.onClose){
    this.onClose();
  }
}

/*
  // - have a base 'event view'
  // - extend this if necessary to handle different post types
  // - the different post types could have different templates, probably 'master classes' to allow css namespacing
  //
*/

TIM.views.EventView = Backbone.View.extend( {
   className: "event",
   template:"_event",
   render: function() {
     var html = '';
     
     
   }
});

TIM.views.messageView = Backbone.View.extend( {
   className: "message",
   template:"message",
   render: function() {
     var html = ''; 
   }
});

TIM.tapEvent = "tap";

TIM.views.Highlight = TIM.views.EventView.extend( {
   className: "event highlight",
   template:"_event"
});

TIM.views.PhotoAlbum = TIM.views.EventView.extend( {
  className: "event photo-album",
  template:"_event"  
});

TIM.views.Photo = TIM.views.EventView.extend( {
  className: "event photo",
  template:"_event"  
});

TIM.views.Checkin = TIM.views.EventView.extend( {
  className: "event checkin",
  template:"_event"   
});

TIM.views.Status = TIM.views.EventView.extend( {
  className: "event status",
  template:"_event"   
});

TIM.views.Follow = TIM.views.EventView.extend( {
  className: "event follow",
  template:"_follow"  
});

TIM.views.Video = TIM.views.EventView.extend( {
  className: "event video",
  template:"_event"   
});

TIM.views.VideoAlbum = TIM.views.EventView.extend( {
  className: "event video-album",
  template:"_event"   
});

TIM.views.Correlation = TIM.views.EventView.extend( {
  className: "event correlation",
  template:"_event"   
});

TIM.views.getEventView = function (event) {
  var view;
  switch(event.type) {
    case "follow":
      view = new TIM.views.Follow({event: event});
      break;
    default: 
      view = new TIM.views.EventView({event: event});
  }
  return view;
}

//is this named improperly?  maybe 'render event page'?
TIM.views.renderEvent = function(event, template) {
  template = template || "timelinePage";
  
  event.event_template = event.event_template || "_event";
  for(var i = 0; i < event.events.length; i++) {
    var ev = event.events[i];
    var view = TIM.views.getEventView(ev);
    console.log('event view event_type', ev, view, ev.type)
    ev.event_template = view.template; //this is horseshit - do those really need to be views?
  }
  return TIM.views.renderTemplate(template, event);
}

//
//template is the name of the dust template
//context is the JSON we use to drive the template
//

TIM.views.renderTemplate = function(template, context) {
  
  var html = "";
  dust.render(template, context, function(err, out) {
	  if(err != null) {
			TIM.eventAggregator.trigger("error", {exception: "template error: " + err});
		}
		html = out;
	});
	return html;
}

TIM.renderTemplate = TIM.views.renderTemplate; //shorthand?

TIM.views.Login = Backbone.View.extend( {
        
    className: "app-page light",
    template: "login",
    
    events: {
      //"click span" : "itemClicked"
      "click .cancel-link" : "cancel",
      "click #login-submit" : "submitForm",
      "click #create-user-link" : "newUser"
    },
    
    initialize: function(options) {
        options = options || {};
        var that = this;
        
        _.bindAll(this);
        //make this a Comments collection
        
        
        if(TIM.appContainerElem.find(this.el).length == 0)  {
           TIM.appContainerElem.append(this.$el);
        }
    },
    
    render: function() {
      var that = this;
      
      var templateContext = {
        message: "Hey!"
      }
      
      var html = TIM.views.renderTemplate(this.template, templateContext);
  		this.$el.html(html);
  		window.setTimeout("$('#login-login').focus()", 50);
  		
  		return this.$el;
    },
    
    submitForm: function(e) {
      var url = TIM.apiUrl + "login";
      $('#login-form').attr('action', url);
      var login = $('#login-login').val();
      var password = $('#login-password').val();
      //fake the ajax submit here!
      
      this.model.doLogin(login, password, function() {
        if(TIM.isAuthorApp()) {
          TIM.app.navigate('cover', {trigger:true});
        } else {
          window.location.href = "/";
        }
      });
 
      return false;
    },
    
    newUser: function(e) {
      TIM.showNewUserForm();
      e.preventDefault();
      e.stopPropagation();
    },
    
    cancel: function(e) {
      TIM.cancelLogin();
      e.preventDefault();
    }
    
    
} );

TIM.views.CreateUser = Backbone.View.extend( {
        
    className: "app-page light",
    template: "newuser",
    
    events: {
      //"click span" : "itemClicked"
      "click .cancel-link" : "cancel",
      "click #newuser-submit" : "submitForm",
      "click #login-link" : "showLogin"
    },
    
    initialize: function(options) {
        options = options || {};
        var that = this;
        
        _.bindAll(this);
        
        if(TIM.appContainerElem.find(this.el).length == 0)  {
           TIM.appContainerElem.append(this.$el);
        }
    },
    
    render: function() {
      var that = this;
      
      var templateContext = {
        message: "Hey!"
      }
      
      var html = TIM.views.renderTemplate(this.template, templateContext);
  		this.$el.html(html);
  		window.setTimeout("$('#newuser-name').focus()", 50);
  		
  		return this.$el;
    },
    
    submitForm: function(e) {
      
      
      var authorName = $('#newuser-name').val();
      var fullName = $('#newuser-fullname').val();
      var email = $('#newuser-email').val();
      var password = $('#newuser-password').val();
      
      alert("trying to create " + authorName);
      
      var url = TIM.apiUrl + "authors";
     
      //fake the ajax submit here!
      
      $.ajax({
        type: 'POST',
        url: TIM.apiUrl + 'authors',
        data: JSON.stringify({ name: authorName, full_name: fullName, email: email, password: password}),
        xhrFields: {withCredentials: true},
        contentType: 'application/json',
        success: function(data, xhr) {
           console.log("create response: ", data, status, xhr);
           //do something with the data...
           alert('hey! new user!');
           
           TIM.eventAggregator.trigger('usercreated', {name:data.name});
         },
         error: function(data) {
           console.log("create error: ", data);
           $('.newuser-form .message').html('could not create that user.');
           self.trigger('newuserError');
         },
        dataType: "json"
      });
            
      return false;
    },
    
    showLogin: function(e) {
      TIM.showLoginForm();
      e.preventDefault();
      e.stopPropagation();
    },
    
    cancel: function(e) {
      TIM.cancelLogin();
      e.preventDefault();
    }
    
    
} );


TIM.views.Settings = Backbone.View.extend( {
        
    className: "app-page light toolbar-top settings-page services",
    template: "settings",
    
    events: {
      //"click span" : "itemClicked"
      "click .cancel-link" : "cancel",
      "click li a" : "toggleSetting",
      "click #logout-link" : "doLogout",
      "click .profile-tab" : "showProfileInfo",
      "click .services-tab" : "showServices",
      "click .features-tab" : "showFeatures"
    },
    
    initialize: function(options) {
        options = options || {};
        var that = this;
        
        _.bindAll(this);
        //make this a Comments collection
        
        
        if(TIM.appContainerElem.find(this.el).length == 0)  {
           TIM.appContainerElem.append(this.$el);
        }
    },
    
    render: function() {
      var that = this;
      
      //remove the 'me' service for display
      var me = that.collection.getByName('me');
      if(me) {
        that.collection.remove(me);
      }
      
      //compare the list of all services vs. the author's services
      this.collection.each(function(item){
        
        var name = item.get('name');
        
        item.set('url', '/oauth/' + name);
        
        if(TIM.currentUserServices && TIM.currentUserServices.getByName(name)) {
          item.set('enabled', 'enabled');
        } else {
          item.set('enabled', 'disabled');
        }
        
        
        
      })
      
      var userName = TIM.authenticatedUser.get('name') || '';
      
      var templateContext = {name: userName, services: this.collection.toJSON()};
      
      var html = TIM.views.renderTemplate(this.template, templateContext);
  		this.$el.html(html);
  		return this.$el;
    },
    
    toggleSetting: function(e) {
      event.preventDefault();
      event.stopPropagation();
      var href = "";
      try {
        href = e.currentTarget.href;
      } catch(e) {
        href = "";
      }
      if (href !== "") {
        //alert(href);
        window.location.href = href;
      }
      return false;
    },
    
    cancel: function(e) {
      TIM.cancelLogin();
      e.preventDefault();
    },
    
    doLogout: function(e) {
      TIM.doLogout();
      e.preventDefault();
    },
    
    showProfileInfo: function(e) {
      e.preventDefault();
      e.stopPropagation();
      this.$el.addClass('profile');
      this.$el.removeClass('services features');
    },
    
    showServices: function(e) {
      e.preventDefault();
      e.stopPropagation();
      this.$el.addClass('services');
      this.$el.removeClass('features profile');
    
    },
    
    showFeatures: function(e) {
      e.preventDefault();
      e.stopPropagation();
      this.$el.addClass('features');
      this.$el.removeClass('services profile');
    }
    
} );




TIM.views.ErrorMessage = Backbone.View.extend( {
   id: "error-message",
   
   initialize: function() {
       _.bindAll(this);
       this.$messageEl = $('#error-message > div');
   },
   
   render: function (options) {
     options = options || {};
     var message = options.message || "We encountered an error.  Please try again.";
     this.$el.html('<div>' + message + '</div>');
     console.log(this.$el);
     if(TIM.appContainerElem.find(this.el).length == 0)  {
			  TIM.appContainerElem.append(this.$el);
		  }     
   }
});
   

TIM.views.FeatureNav = Backbone.View.extend( {
   el: $( "#feature-nav-items" ),
		
   initialize: function() {
       this.collection.bind( "reset", this.render, this );
       TIM.eventAggregator.bind('featureselected', this.highlightSelectedNavItem, this);
   },
   
   addAll : function () {
      this.collection.each (this.addOne);
      //notify the app that the feature nav has been rendered
      TIM.eventAggregator.trigger('featurenavrendered', this);
   },
		
  addOne : function ( item ) {
    console.log(item);
  	var view = new TIM.views.FeatureNavItem({model:item});
  	
  	view.render();
  	
  	if(!view.hidden) {  
  	  $( "#feature-nav-items" ).append(view.render().el);
  	}
  },

  render: function() {
   this.addAll();
   //this is horrible... adding 'settings' as a 'feature'?
   if(TIM.isAuthorApp()) {
     if(false || true) {
       var f = new TIM.models.Feature({
         name:"home",

       });
       this.addOne(
         f
       );
     }
     if (false || true) {
       var f2 = new TIM.models.Feature({
          name:"login",

        });
        this.addOne(
          f2
        )
      }
      if (false || true) {
        var f3 = new TIM.models.Feature({
           name:"settings",

         });
         this.addOne(
           f3
         )
       }
   }
  },

 	highlightSelectedNavItem: function(selectedFeature) {
 	  this.collection.each (function(feature) {
 	    if (feature.get('name') == selectedFeature.get('name')) {
 	      feature.set('selected', true);
 	    } else {
 	      feature.set('selected', false);
 	    }
 	    //console.log(feature);
 	  });
 	  $("#feature-nav").removeClass('active');
 	}
})

TIM.views.FeatureNavItem = Backbone.View.extend({
	tagName : 'li',
  
  hidden: false,
  
	initialize: function() {
		this.model.bind('change', this.render, this);
		this.model.bind('destroy', this.remove, this);
		this.model.bind('loaded', this.featureLoaded, this);
	},
	
	events: {
		"tap" : "loadFeature"
	},

	render : function () {
	  var self = this;
	  var selected = this.model.get('selected');
	  console.log('rendering menu item');
	  var templateContext = this.model.toJSON();
	  
	  //temporary hack to change 'timeline' to 'news'
	  if(templateContext.name === 'timeline') {
	    templateContext.name = 'news';
	  }
	  
	  //temporary hack - don't show highlights or places features
	  if(templateContext.name === 'highlights' || templateContext.name === 'places') {
	    //return;
	  }
	  
	  var html = TIM.views.renderTemplate("featureNavItem", templateContext);
    this.$el.html(html)
      .attr('id', 'nav-' + templateContext.name)
      .removeClass('selected')
      .addClass(selected ? 'selected' : '');
      
    //temporary hack - don't show highlights or places features
	  if(templateContext.name === 'highlights' || templateContext.name === 'places') {
	    this.hidden = true;
	  }
    
		return this;
	},
	
	loadFeature : function() {
	  if (this.model.get('name') == 'settings' || this.model.get('name') == 'login') {
	    TIM.loadSettings();
	    return;
	  }
	  if(this.$el.hasClass('selected')) {
	    //return;
	    TIM.navigateHandler("route:" + this.model.get('name')); //kinda hack way of navigating to same feature
	    return;
	  }
	  TIM.app.navigate(this.model.get('name'), {trigger: true});
	},
	
	featureLoaded: function() {
	  //alert('the view knows the feature is loaded!!!!!!!!');
	}
	
});

//make the comments area scrollable - really should have scrollable areas based on classes <div class="scrollable"><div class="scroll-inner"></div></div>
//fake toggling between services
// -throw up spinner, wait, then fade in new content
//
// need to be able to handle general transitions, etc. when we don't explicitly know what the last item was
// keep history of ... urls/pages ... & try to determine transition intelligently

// or have comments view keep a pointer to its previous view & just explicitly go there
// 
// ...
//
// have notion of the available services & which one is selected

TIM.views.Comments = Backbone.View.extend( {
        
    className: "app-page comment-list toolbar-top",
    template: "commentList",
    commentCollections: [],
    collectionNum: 0,
    
    events: {
      //"click span" : "itemClicked"
      "swiperight" : "hideComments",
      "tap .back-link" : "hideComments",
      "tap .service-tabs li" : "switchService"
    },
    
    initialize: function(options) {
        options = options || {};
        var that = this;
        this.commentCollections = [];
        
        console.log("options: ", options);
        
        _.bindAll(this);
        //make this a Comments collection
        
        this.resource = options.resource;
        
        this.sources = options.sources || []; //or should this view be responsible for asking the API what the comment sources are?
        
        for(var i = 0; i < this.sources.length; i++) {
          var source = this.sources[i];
          this.commentCollections.push(new TIM.collections.Comments({source:source}));
        }
        
        this.items = generateFakeComments(51);
        
        this.selectedSource = this.sources[0];
        
        //initialize collections - one for each source/service
        this.commentCollections[this.collectionNum].reset(generateFakeComments(51));
        
        if(TIM.appContainerElem.find(this.el).length == 0)  {
           TIM.appContainerElem.append(this.$el);
        }
    },
    
    render: function() {
      var that = this;
      
      var templateContext = {
                  sources: this.sources, 
                  comments:this.commentCollections[this.collectionNum].toJSON(), 
                  toolbar:true
      }
      
      var html = TIM.views.renderTemplate(this.template, templateContext);
      this.$scrollElem = undefined;
      this.iScrollElem = undefined;
  		this.$el.html(html);
  		this.resetScrollElem()
  		return this.$el;
    },
    
    //make the comments area scrollable
    //this scrollable stuff definitely needs to be generalized
    
    resetScrollElem: function(options) {
       options = options || {};
       var that = this;
       
       //make sure the elem container is the right height
       this.$scrollElem = this.$el.find('.scrollable'); //this.$scrollElem || this.$el.find('.scrollable');
       this.$scrollElem.css('height', TIM.getViewportSize().height - 40); //window height - the toolbar height
       if (this.iScrollElem) {
         if (options.destroy) {
           this.iScrollElem.destroy();
           this.iScrollElem = null;
         } else {
           setTimeout(function () { that.iScrollElem.refresh();  }, 0);
           return;
         }
       }
       this.iScrollElem = new iScroll(this.$scrollElem.get(0), { 
           //maybe instead of checking vs. the iscroll value, check to see which item is currently in view, then render next chunk if it's not visible & we're getting close to needing it
         		onScrollMove: function () {
         		},
            onScrollEnd: function () {
         			//this is where we might do the 'loading next chunk' for infinite scroll
         		},
             hScroll: false,
             vScrollbar: false
        });
 			  setTimeout(function () { that.iScrollElem.refresh();  }, 0);
     },
    
    hideComments: function() {
      window.history.back();
    },
    
    //set TIM.loading to true
    //change selected item in 'tabs'
    //get comments from new service if they're not already loaded
    //load them into the 'commentlist' div  (fade transition?)
    //set TIM.loading to false
    //
    //do we want a special 'view' for these tabs
    //
    //seems like the pattern might/will be used several times in the app...
    
    switchService: function() {
      var that = this;
      TIM.setLoading(true);
      this.collectionNum++;
      if (this.collectionNum >= this.sources.length) {
        this.collectionNum = 0;
      }
      
      this.commentCollections[this.collectionNum].reset(generateFakeComments(randomNum(83)));
      window.setTimeout(function() {
        that.render();
        that.setSelectedService();
        that.resetScrollElem();
        TIM.setLoading(false);
      }, 1000);
      
      
      
    },
    
    setSelectedService: function () {
      var i = 0;
      var that = this;
      this.$el.find('.service-tabs li').each(function(){
        $(this).removeClass('selected');
        if(i == that.collectionNum) {
          $(this).addClass('selected');
        }
        i++;
      })
    }
    
} );

//a stab at a 'toolbar view'  that other views could theoretically add & customize & respond to
//toolbar triggers events on its parent view?
//
//this isn't being used at the moment and is maybe overkill, but we may want to use it later?

TIM.views.Toolbar = Backbone.View.extend( {
        
    className: "toolbar",
    template: "toolbar",
    
    events: {
      "click span" : "itemClicked"
    },
    
    items:[ 
      {name: 'gridLink'},
      {name: 'detailLink'}
    ],
    
    initialize: function(spec) {
        spec = spec || {};
        _.bindAll(this);
    },
    
    render: function() {
      var that = this;
      var templateContext = {items:this.items};
      var html = TIM.views.renderTemplate(this.template, templateContext);
     
  		this.$el.html(html);
  		return this.$el;
    },
    
    //parent views probably shouldn't rely on this event, but you never know
    //maybe broadcast it app-wide?
    
    itemClicked: function(event) {
      var item = event.currentTarget;//event.data('name')
      //console.log(event, item);
      this.trigger('itemClicked', $(item).data('toolbar-item'));
    }
    
} );

//
//this view is used by the flipset mixin
//do we need to have a view object for this at all?
//this might be the ideal place to create different views for event types (photo, short-form, etc.)
//
//except there are potentially many events on a page
//

TIM.views.Page = Backbone.View.extend( {
    
    className: "page",
    
    hasRendered: false,
    
    initialize: function(spec) {
        _.bindAll(this, "render");
				this.page = spec.page;
    },

    render: function( tmpl, callback ) {
      
      console.log('rendering page: ', this.page);
			var that = this;
			tmpl = tmpl || "timelinePage";
			
			var html = TIM.views.renderEvent(this.page, tmpl);
			///var html = TIM.views.renderTemplate(tmpl, this.page);
      //this.$el.append(html);
      callback(html);
      this.hasRendered = true;
    }
} );

//an attempt to define the flipset functionality as a mixin

//key is the 'pages' array... it's different than underlying event/photo/etc collection in that there can be multiple items on a page
//this flipset object should probably work off of that...
//
//the underlying collection for this view will be a collection of raw events from our API
//

TIM.mixins.flipset = {
		
		initializeFlipset: function() {
		  var that = this;
      this.pageNum = 0;
  		this.pages = [];
  		this.flipSet = {};
  		this.flipSetInitialized = false;
  		this.chunkSize = 50;
  		this.renderedIndex = 0;
  		this.numResourcesRendered = 0;
  		this.flipMode = true;
		},
		
		//
		// send pages to the flips script one at a time as strings?
		// maybe have the flips script render the pages instead?
		//
		
		renderPage: function(page){  //'pages' could just be 'page'
			//make a Page View out of 1-3 events
	    var pageView = new TIM.views.Page({page:page});
	    var tmpl = page.template ? page.template : this.pageTemplate;
	    var that = this;
	    
	    console.log("page template: ", tmpl);
	    
	    //maybe do away with this process of sending html strings to the flipset to be injected into the flipset templates?
	    //seems wasteful
      pageView.render(tmpl, function(pageHtml){
        if (!that.flipSetInitialized) {
					
					that.flipSet = new Flipset({containerEl: $(that.el), pages: [pageHtml], parentView: that});
					window.flipSet = that.flipSet; //for debugging
					that.flipSetInitialized = true;
				} else {
					that.flipSet.addSourceItem(pageHtml);
				}
      });
        

    },
    
    //the view's render method will call this
    
    renderFlipSet: function(options){
	
			options = options || {};
			console.log("rendering flipset, options: ", options);
			
			var startIndex = this.numResourcesRendered;
			this.pages = this.pages || [];
			var self = this;
			var page = [];
			var itemJSON;
			this.renderedIndex = this.renderedIndex || 0;
			this.flipSetInitialized = this.flipSetInitialized || false;

			options.start = startIndex;
			
			//makePages groups raw events into 'pages' which will be rendered into html for the flipset
			console.log("making pages hammer");
			this.makePages(options);
			console.log("made pages hammer");
			
			if(startIndex == 0) {
			  this.$el.html(''); //if this if the first time rendering this flipset, make sure its container element is empty
			}
			this.renderPageChunk(this.renderedIndex); //render the first chunk of pages
			
			if(TIM.appContainerElem.find(this.el).length == 0)  {
			  TIM.appContainerElem.append(this.$el);
			}
			
			//replace this with this.$el.hammer() ???
			try{
			  this.flipSet.initializeHammer();
			} catch(e) {
			  console.log(e);
			}
			return this;
    },
    
    //
    //this function turns raw events into 'pages' that are ready to be rendered as one 'flip page'
    //this allows more than one event to appear on a page
    //
    
    makePages: function(options) {
      
      var self = this;
			var page = [];
			var itemJSON;
			
      var start = options.start || 0;
      var end = options.end || this.collection.length;
      
      this.collection.each(function(item, index) {
			  if(index < start || index >= end) return; //return if out of range
			  
			  itemJSON = item.toJSON();
			  		   
			  //this is very dependent on the old structure of the data
			  //will probably change going forward...
			  //possibly different templates for different event types?
			  //
			  //shouldn't skip too many non-one-page events...
			  
				if(itemJSON.title !== undefined || itemJSON.type === "photo" || itemJSON.photo !== undefined || itemJSON.post_type_detail !== undefined) {
				  var template = self.pageTemplate;
					self.pages.push({template: template, num: index+1, options: options, "event_class" : "full-page", "events" : [itemJSON]});
				} else {
					page.push(item);
					if(page.length == 2) {
						self.pages.push({template: template, "event_class" : "half-page", "events" : [page[0].toJSON(), page[1].toJSON()]});
						page = [];
					}
				}
				self.numResourcesRendered++;
			});
			
			//if there's one left over, make a page of it!
			if(page.length == 1) {
			  self.pages.push({"event_class" : "full-page", "events" : [page[0].toJSON()]});
			}
			
    },
    
		renderPageChunk: function(start) {
			//would this fn check for earlier/later events if they haven't been loaded?
			var end = start + this.chunkSize;
			if (end > this.pages.length) {
				end = this.pages.length;
			}
			for (var i = start; i < end; i++) {
			  this.renderPage(this.pages[i]);
  			this.renderedIndex++;
			}
			if (this.flipSet && this.pages.length > 0) {
			  this.flipSet.createPageElements();
			} else {
			  this.$el.html('<div class="flipset-empty"><p>This user has no highlights</p></div>'); //hack for empty highlights, should be generalized
			}
		},
		
		
		//this is called when the user has flipped to the next page in the flipset...
		flipNext: function(){
			
			var that = this;
			
			//prerendering 3 pages & sending to flipset
			//we always want to have this many pages available to teh flipset because it needs to have as many as 4 pages in the DOM at one time
			
			if(this.pageNum == (this.renderedIndex - 3)) {
				this.renderPageChunk(this.renderedIndex);
			}
			
			if (this.pageNum < this.collection.length - 2) {
				this.pageNum++;
			} else {
			  
			  if(TIM.isLoading() || this.collection.getNextPage === undefined) {
			    return;
			  }
			  this.collection.getNextPage();
			  this.pageNum++;
			}
			if (this.updateRouter) {
			  this.updateRouter();
			}
		},
    
    //this is called when the user has flipped to the previous page in the flipset...
		flipPrevious: function(){

			if (this.pageNum == 0) {
				//check for newer events at this point?
				//do a 'get previous page' call, as in 
			} 

			if (true || this.flipSet.canGoPrevious()) {
				this.pageNum--;
			}
			if (this.updateRouter) {
			  this.updateRouter();
			}
		},
		
		//go to an arbitrary page in the flipset
		goToPage: function(num){
			
			this.pageNum = 0;
			
			//make sure pages are rendered before trying to go to that page
			//this should probably not have to render the entire thing up to the page we want
			//in case the person is asking for page 500 or something
			
			for(var i = 0; i < num; i++) {
		    //prerender 2 pages in advance?
  			if(this.pageNum == (this.renderedIndex - 2)) {
  				this.renderPageChunk(this.renderedIndex);
  			}
  			this.pageNum++;
  		}
  	
  		this.flipSet._gotoPage(num);
  		if (this.updateRouter) {
			  this.updateRouter();
			}
  		
		},
		
		//maybe a handler to do something when the user has flipped a page
		pageChanged: function (num) {
		  
		}
}

//abstraction of iscroll element for a view...
//
//maybe eventually do away with iscroll
//
//have methods to create, refresh, destroy
//
//set height, change height of container (full window, specific height, full height - toolbar, etc.)
//
//...or 'scrollable' mixin?  ...which could have one or more scrollable areas...
//
//probably would base this on class names, eg. 'scrollable-vert', 'scrollable-horiz'?
//


TIM.views.scrollElem = {
  
  
}

//a bunch of nonsense below to make fake comments!

var commenterNames = ["Charlie Smith", "Emma Fallon", "Kelly Toms", "George Burrows", "Jose Williams", "Englebert Humperdink", "Fleegj Wilsheim", "Grover Cleveland the 44th", "Jerry", "Mr. Wilkinson", "The Junkyard Dog", "Kevin McHale", "Dan Roundfield", "Brian Sipe", "Tim O'Reilly",
                      "Freddy Deltoids", "Napoleon Khan", "Madeline Albright", "Dan Fouts", "Kris Kristofferson", "Fu-Hang Schmlertervlowitz", "Bub", "Timmy the Talking Unicycle", "Long Tall Steve", "Conquistador #7", "Margaret Blumenfeld", "Ramon Ramen", "Ramona X."];
var commentTexts = ["Great Photo!", "I agree!", "This is a prime example of what makes America great: shoehorns", "Foghorn Leghorn is my favorite bicyclist", "So the casserole goes in the oven for 2 hours and 35 minutes at 450 degrees? Thanks!",
                    "I like treehouses.  They're fun and special and bright and airy.", "Wait, is that a #pheasant?", "Four score and 38 years ago we desecrated a great lamppost based on burritos and vigilante justice.", "Who's going to the 1971 Philadelphia 76ers reunion banquet tomorrow?",
                    "Connect Four was a great game.", "the cartoon #Garfield is criminally underrrated.", "@hammer is my favorite thisis.me member <a href='http://thisis.me/hammer'>thisis.me/hammer</a>", "So wait, are you saying there isn't a Flying Spaghetti Monster?", "Cookie Monster is my hero.",
                    "I really think that whole Benjamin Franklin flying a kite lightning electricity thing was a #sham", "So are you trying to tell me I can't write a really, really, really long comment.  Balderdash!  I can write any kind of comment I like.  This is America, not Poland or Yugoslavia!",
                    "cool.", "you rock, Philip!", "pancakes are best served with a touch of tragic whimsy.", "Celtics 142, Bullets 81.  Oh yes!", "Could #joebarrycarroll be the next #chiefrobertparish", "I *will* win Wimbledon this year!!", "You *will* not!",
                    "...and so my thoughts on the government of Bahrain are as follows: excellent judicial system, everything else is crap."];

var generateFakeComments = function(num) {
  var comments = [];
  for (var i = 0; i < num; i++) {
    var comment = {
      "authorName":randomItem(commenterNames),
      "text":randomItem(commentTexts),
      "time":"1 hr ago" //get a decent 'time ago' solution
    }
    comments.push(comment);
  }
  return comments;
}

function randomItem(arr) {
  return arr[Math.floor((Math.random()*arr.length))];
}

function randomNum(max) {
  return Math.floor((Math.random()*max));
}

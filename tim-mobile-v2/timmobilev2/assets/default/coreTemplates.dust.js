(function(){dust.register("featureNavItem",body_0);function body_0(chk,ctx){return chk.reference(ctx.get("feature_name"),ctx,"h");}return body_0;})();
(function(){dust.register("toolbar",body_0);function body_0(chk,ctx){return chk.section(ctx.get("items"),ctx,{"block":body_1},null);}function body_1(chk,ctx){return chk.write("<span class=\"").reference(ctx.get("name"),ctx,"h").write("\" data-toolbar-item=\"").reference(ctx.get("name"),ctx,"h").write("\"/>");}return body_0;})();
(function(){dust.register("flipPage",body_0);function body_0(chk,ctx){return chk.write("<div class=\"page flip-").reference(ctx.get("pageNum"),ctx,"h").write("\" data-num=\"").reference(ctx.get("pageNum"),ctx,"h").write("\" style=\"z-index:").reference(ctx.get("zIndex"),ctx,"h").write("\"><div class=\"front\"><div class=\"outer\"><div class=\"content\" style=\"\"><div class=\"inner\">").reference(ctx.get("frontContent"),ctx,"h",["s"]).write("</div></div></div></div><div class=\"back\"><div class=\"outer\"><div class=\"content\" style=\"\"><div class=\"inner\">").reference(ctx.get("backContent"),ctx,"h",["s"]).write("</div></div></div></div></div>");}return body_0;})();
(function(){dust.register("commentList",body_0);function body_0(chk,ctx){return chk.exists(ctx.get("toolbar"),ctx,{"block":body_1},null).write("<div class=\"split-pane\"><ul class=\"service-tabs\">").section(ctx.get("sources"),ctx,{"block":body_2},null).write("</ul><div class=\"comments scrollable\"><div class=\"scroll-inner\">").section(ctx.get("comments"),ctx,{"block":body_3},null).write("</div></div></div>");}function body_1(chk,ctx){return chk.write("<div class=\"toolbar\"><span class=\"back-link\" data-toolbar-item=\"back-link\"/><h1>Comments</h1></div>");}function body_2(chk,ctx){return chk.write("<li class=\"").reference(ctx.get("source_name"),ctx,"h").write(" ").reference(ctx.get("selected"),ctx,"h").write("\"></li>");}function body_3(chk,ctx){return chk.write("<div class=\"comment\"><div class=\"user-thumb\"></div><div class=\"info\"><div class=\"user-name\">").reference(ctx.get("authorName"),ctx,"h").write("<span class=\"time-ago\">").reference(ctx.get("time"),ctx,"h").write("</span></div><div class=\"text\">").reference(ctx.get("text"),ctx,"h",["s"]).write("</div></div></div>");}return body_0;})();
(function(){dust.register("_eventFooter",body_0);function body_0(chk,ctx){return chk.write("<footer><div class=\"avatar\"><div class=\"frame\"><img src=\"").reference(ctx.getPath(false,["author","profile_image_url"]),ctx,"h").write("\"/></div></div>\t\t  <div class=\"main-text\">").exists(ctx.get("tagline"),ctx,{"block":body_1},null).write("</div><div><!-- loop through sources -->").section(ctx.getPath(false,["sources","items"]),ctx,{"block":body_4},null).write("<!-- move this whole caption/bottom info bar thing to a partial! --><span class=\"time-and-location\">").reference(ctx.get("time_ago"),ctx,"h").write(" ").reference(ctx.get("location"),ctx,"h").write("</span></div></footer>");}function body_1(chk,ctx){return chk.helper("truncate",ctx,{"block":body_2},{"value":body_3,"length":"50"});}function body_2(chk,ctx){return chk;}function body_3(chk,ctx){return chk.reference(ctx.get("tagline"),ctx,"h");}function body_4(chk,ctx){return chk.write(" ").exists(ctx.get("service_image_url"),ctx,{"block":body_5},null);}function body_5(chk,ctx){return chk.write("<!-- <img class=\"").reference(ctx.get("service_name"),ctx,"h").write("\" src=\"").reference(ctx.get("service_image_url"),ctx,"h").write("\" /> --><span class=\"service-icon ").reference(ctx.get("service_name"),ctx,"h").write("\"></span>");}return body_0;})();
(function(){dust.register("photoPage",body_0);function body_0(chk,ctx){return chk.write("<div class=\"photo-page\"><div class=\"toolbar\"><span class=\"grid-link\" data-toolbar-item=\"grid-link\"/><span class=\"detail-link\" data-toolbar-item=\"detail-link\"/><h1>").reference(ctx.get("num"),ctx,"h").write(" of ").reference(ctx.getPath(false,["options","pageMetaData","count"]),ctx,"h").write("</h1></div>").section(ctx.get("events"),ctx,{"block":body_1},null).write("</div>");}function body_1(chk,ctx){return chk.section(ctx.get("main_image"),ctx,{"block":body_2},null).write("<!-- img class=\"image\" src=\"").reference(ctx.get("url"),ctx,"h").write("\" data-photo_id=\"").reference(ctx.get("id"),ctx,"h").write("\" / -->").partial("_eventFooter",ctx).write("<div class=\"interaction-icons\"><span class=\"location\" data-photo_id=\"").reference(ctx.get("id"),ctx,"h").write("\"></span><span class=\"comments\" data-photo_id=\"").reference(ctx.get("id"),ctx,"h").write("\"></span></div>");}function body_2(chk,ctx){return chk.write("<div class=\"full-photo\" style=\"background-image:url(").reference(ctx.get("url"),ctx,"h").write(")\" data-photo_id=\"").reference(ctx.get("id"),ctx,"h").write("\"/>");}return body_0;})();
(function(){dust.register("timelinePage",body_0);function body_0(chk,ctx){return chk.write("<div class=\"toolbar\"><h1>News</h1></div><div class=\"mi-content\"  style=\"height: 100%;\">").section(ctx.get("events"),ctx,{"block":body_1},null).write("</div>");}function body_1(chk,ctx){return chk.write("<div class=\"event ").reference(ctx.get("event_class"),ctx,"h").write("\" data-event_id=\"").reference(ctx.get("event_id"),ctx,"h").write("\">").partial(body_2,ctx).write("</div>");}function body_2(chk,ctx){return chk.reference(ctx.get("event_template"),ctx,"h");}return body_0;})();
//moving timeline templates to global templates file
(function(){dust.register("_event",body_0);function body_0(chk,ctx){return chk.section(ctx.get("content"),ctx,{"block":body_1},null).partial("_eventFooter",ctx);}function body_1(chk,ctx){return chk.write("<div class=\"content\">").exists(ctx.get("photo_url"),ctx,{"else":body_2,"block":body_3},null).write("<div class=\"inner-text\">").exists(ctx.get("label"),ctx,{"block":body_4},null).exists(ctx.get("data"),ctx,{"block":body_5},null).write("</div></div>");}function body_2(chk,ctx){return chk;}function body_3(chk,ctx){return chk.write("<div class=\"inner-image\"><img src='").reference(ctx.get("photo_url"),ctx,"h").write("' /></div>");}function body_4(chk,ctx){return chk.write("<p>").reference(ctx.get("label"),ctx,"h").write("</p>");}function body_5(chk,ctx){return chk.write("<p>").reference(ctx.get("data"),ctx,"h").write("</p>");}return body_0;})();
(function(){dust.register("page",body_0);function body_0(chk,ctx){return chk.write("<div class=\"mi-content\" style=\"height: 100%;\">").section(ctx.get("events"),ctx,{"block":body_1},null).write("</div>");}function body_1(chk,ctx){return chk.write("<div class=\"event half-page\" data-event_id=\"").reference(ctx.get("event_id"),ctx,"h").write("\">").partial("_event",ctx).write("</div>");}return body_0;})();
(function(){dust.register("eventDetail",body_0);function body_0(chk,ctx){return chk.write("<div class=\"eventDetail\">DETAIL VIEW FOR TIMELINE EVENT!").section(ctx.get("content"),ctx,{"block":body_1},null).write("</div>");}function body_1(chk,ctx){return chk.write("<div class=\"content\">").exists(ctx.get("photo_url"),ctx,{"else":body_2,"block":body_3},null).write("<div class=\"inner-text\"><p>").reference(ctx.get("data"),ctx,"h").write("</p></div></div>");}function body_2(chk,ctx){return chk;}function body_3(chk,ctx){return chk.write("<div class=\"inner-image\"><img src='").reference(ctx.get("photo_url"),ctx,"h").write("' /></div>");}return body_0;})();
//event/post types
(function(){dust.register("_photo",body_0);function body_0(chk,ctx){return chk.write("<img class=\"thumb\" src=\"http://farm").reference(ctx.get("farm"),ctx,"h").write(".static.flickr.com/").reference(ctx.get("server"),ctx,"h").write("/").reference(ctx.get("id"),ctx,"h").write("_").reference(ctx.get("secret"),ctx,"h").write("_s.jpg\" data-photo_id=\"").reference(ctx.get("id"),ctx,"h").write("\"/>");}return body_0;})();
(function(){dust.register("_follow",body_0);function body_0(chk,ctx){return chk.section(ctx.get("content"),ctx,{"block":body_1},null).partial("_eventFooter",ctx);}function body_1(chk,ctx){return chk.write("<div class=\"content\">").exists(ctx.get("photo_url"),ctx,{"else":body_2,"block":body_3},null).write("<div class=\"inner-text\">").exists(ctx.get("label"),ctx,{"block":body_4},null).exists(ctx.get("data"),ctx,{"block":body_5},null).write("</div></div>");}function body_2(chk,ctx){return chk;}function body_3(chk,ctx){return chk.write("<div class=\"inner-image\"><img src='").reference(ctx.get("photo_url"),ctx,"h").write("' /></div>");}function body_4(chk,ctx){return chk.write("<p>").reference(ctx.get("label"),ctx,"h").write("</p>");}function body_5(chk,ctx){return chk.write("<p>").reference(ctx.get("data"),ctx,"h").write("</p>");}return body_0;})();

(function(){
  
  //put global dust helper fns here
  
  function renderParameter(name, chunk, context, bodies, params) {
  	if (params && params[name]) {
  		if (typeof params[name] === "function") {
  			var output = "";
  			chunk.tap(function (data) {
  				output += data;
  				return "";
  			}).render(params[name], context).untap();
  			return output;
  		} else {
  			return params[name];
  		}
  	}
  	return "";
  }

  dust.helpers.truncate = function(chunk, context, bodies, params) {
    var str = renderParameter("value", chunk, context, bodies, params);
    var length = params.length || 15;
    if (str.length > length) {
      chunk.write(str.substring(0,length) + "...");
    } else {
      chunk.write(str);
    }
    return chunk;
  }

})()

/* maybe put a fn to render 'friendly time' here? */
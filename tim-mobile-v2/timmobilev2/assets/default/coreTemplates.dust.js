(function(){dust.register("featureNavItem",body_0);function body_0(chk,ctx){return chk.reference(ctx.get("feature_name"),ctx,"h");}return body_0;})();
(function(){dust.register("toolbar",body_0);function body_0(chk,ctx){return chk.section(ctx.get("items"),ctx,{"block":body_1},null);}function body_1(chk,ctx){return chk.write("<span class=\"").reference(ctx.get("name"),ctx,"h").write("\" data-toolbar-item=\"").reference(ctx.get("name"),ctx,"h").write("\"/>");}return body_0;})();
(function(){dust.register("flipPage",body_0);function body_0(chk,ctx){return chk.write("<div class=\"page flip-").reference(ctx.get("pageNum"),ctx,"h").write("\" data-num=\"").reference(ctx.get("pageNum"),ctx,"h").write("\" style=\"z-index:").reference(ctx.get("zIndex"),ctx,"h").write("\"><div class=\"front\"><div class=\"outer\"><div class=\"content\" style=\"\"><div class=\"inner\">").reference(ctx.get("frontContent"),ctx,"h",["s"]).write("</div></div></div></div><div class=\"back\"><div class=\"outer\"><div class=\"content\" style=\"\"><div class=\"inner\">").reference(ctx.get("backContent"),ctx,"h",["s"]).write("</div></div></div></div></div>");}return body_0;})();
(function(){dust.register("commentList",body_0);function body_0(chk,ctx){return chk.exists(ctx.get("toolbar"),ctx,{"block":body_1},null).write("<div class=\"split-pane\"><ul class=\"service-tabs\">").section(ctx.get("sources"),ctx,{"block":body_2},null).write("</ul><div class=\"comments scrollable\"><div class=\"scroll-inner\">").section(ctx.get("comments"),ctx,{"block":body_3},null).write("</div></div></div>");}function body_1(chk,ctx){return chk.write("<div class=\"toolbar\"><span class=\"back-link\" data-toolbar-item=\"back-link\"/><h1>Comments</h1></div>");}function body_2(chk,ctx){return chk.write("<li class=\"").reference(ctx.get("source_name"),ctx,"h").write(" ").reference(ctx.get("selected"),ctx,"h").write("\"></li>");}function body_3(chk,ctx){return chk.write("<div class=\"comment\"><div class=\"user-thumb\"></div><div class=\"info\"><div class=\"user-name\">").reference(ctx.get("authorName"),ctx,"h").write("<span class=\"time-ago\">").reference(ctx.get("time"),ctx,"h").write("</span></div><div class=\"text\">").reference(ctx.get("text"),ctx,"h",["s"]).write("</div></div></div>");}return body_0;})();
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
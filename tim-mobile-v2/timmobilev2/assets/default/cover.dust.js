(function(){dust.register("coverpage",body_0);function body_0(chk,ctx){return chk.write("<div class=\"coverPage\"><h1 class=\"title\">").reference(ctx.get("name"),ctx,"h").write("</h1><div class=\"primaryStory highlight\" data-event_id=\"").reference(ctx.getPath(false,["primaryStory","event_id"]),ctx,"h").write("\"><a href=\"timeline/").reference(ctx.getPath(false,["primaryStory","event_id"]),ctx,"h").write("\">").reference(ctx.getPath(false,["primaryStory","content","label"]),ctx,"h").write("</a></div><div class=\"secondaryStory highlight\" data-event_id=\"").reference(ctx.getPath(false,["secondaryStory","event_id"]),ctx,"h").write("\">").exists(ctx.getPath(false,["secondaryStory","content","label"]),ctx,{"block":body_1},null).exists(ctx.getPath(false,["secondaryStory","content","data"]),ctx,{"block":body_4},null).write("</div><div class=\"tertiaryStory highlight\" data-event_id=\"").reference(ctx.getPath(false,["tertiaryStory","event_id"]),ctx,"h").write("\">").reference(ctx.getPath(false,["tertiaryStory","content","label"]),ctx,"h").write("</div></div>");}function body_1(chk,ctx){return chk.helper("truncate",ctx,{"block":body_2},{"value":body_3,"length":"35"});}function body_2(chk,ctx){return chk;}function body_3(chk,ctx){return chk.reference(ctx.getPath(false,["secondaryStory","content","label"]),ctx,"h");}function body_4(chk,ctx){return chk.helper("truncate",ctx,{"block":body_5},{"value":body_6,"length":"35"});}function body_5(chk,ctx){return chk;}function body_6(chk,ctx){return chk.reference(ctx.getPath(false,["secondaryStory","content","data"]),ctx,"h");}return body_0;})();
(function(){
  
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
    chunk.write(str.substring(0,length) + "...");
    return chunk;
  }

})()
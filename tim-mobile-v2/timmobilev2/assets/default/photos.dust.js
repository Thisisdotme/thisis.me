(function(){dust.register("_event",body_0);function body_0(chk,ctx){return chk.section(ctx.get("content"),ctx,{"block":body_1},null).write("<div class=\"footer\"><div class=\"avatar\" data-authorName=\"").reference(ctx.getPath(false,["author","name"]),ctx,"h").write("\"><div class=\"frame\"><a href=\"\"><img src='").reference(ctx.getPath(false,["author","profile_image_url"]),ctx,"h").write("' /></a></div></div><div class=\"info\"><div class=\"author\"><a href=\"/").reference(ctx.getPath(false,["author","name"]),ctx,"h").write("/timeline\">").reference(ctx.getPath(false,["author","full_name"]),ctx,"h").write("</a></div><div class=\"caption\">").reference(ctx.getPath(false,["content","label"]),ctx,"h").write("</div></div><div class=\"baseline\">").section(ctx.getPath(false,["sources","items"]),ctx,{"block":body_4},null).write("<div class=\"fuzzy-time\">").reference(ctx.get("time_ago"),ctx,"h").write("</div></div></div>");}function body_1(chk,ctx){return chk.write("<div class=\"content\">").exists(ctx.get("photo_url"),ctx,{"else":body_2,"block":body_3},null).write("<div class=\"inner-text\"><p>").reference(ctx.get("data"),ctx,"h").write("</p></div></div>");}function body_2(chk,ctx){return chk;}function body_3(chk,ctx){return chk.write("<div class=\"inner-image\"><img src='").reference(ctx.get("photo_url"),ctx,"h").write("' /></div>");}function body_4(chk,ctx){return chk.write(" ").exists(ctx.get("feature_image_url"),ctx,{"block":body_5},null);}function body_5(chk,ctx){return chk.write("<img src=\"").reference(ctx.get("feature_image_url"),ctx,"h").write("\" /> ");}return body_0;})();
(function(){dust.register("event",body_0);function body_0(chk,ctx){return chk.write("<div class=\"mi-content\"  style=\"height: 100%;\">").section(ctx.get("events"),ctx,{"block":body_1},null).write("</div>");}function body_1(chk,ctx){return chk.write("<div class=\"event full-page\">").partial("_event",ctx).write("</div>");}return body_0;})();
(function(){dust.register("page",body_0);function body_0(chk,ctx){return chk.write("<div class=\"mi-content\" style=\"height: 100%;\">").section(ctx.get("events"),ctx,{"block":body_1},null).write("</div>");}function body_1(chk,ctx){return chk.write("<div class=\"event half-page\">").partial("_event",ctx).write("</div>");}return body_0;})();

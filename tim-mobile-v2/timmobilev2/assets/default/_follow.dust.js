(function(){dust.register("_follow",body_0);function body_0(chk,ctx){return chk.write(" <div class=\"content follow\">").exists(ctx.get("photo"),ctx,{"else":body_1,"block":body_2},null).write("<div class=\"inner-text\">").exists(ctx.get("headline"),ctx,{"block":body_3},null).exists(ctx.get("content"),ctx,{"block":body_4},null).write("</div></div>").partial("_eventFooter",ctx);}function body_1(chk,ctx){return chk;}function body_2(chk,ctx){return chk.write("<div class=\"inner-image\"><img src='").reference(ctx.getPath(false,["photo","image_url"]),ctx,"h").write("' /></div>");}function body_3(chk,ctx){return chk.write("<p>").reference(ctx.get("headline"),ctx,"h").write("</p>");}function body_4(chk,ctx){return chk.write("<p>").reference(ctx.get("content"),ctx,"h").write("</p>");}return body_0;})();
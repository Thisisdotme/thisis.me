(function(){dust.register("photoPage",body_0);function body_0(chk,ctx){return chk.write("<div class=\"photo-page\"><div class=\"toolbar\"><span class=\"grid-link\" data-toolbar-item=\"grid-link\"/><span class=\"detail-link\" data-toolbar-item=\"detail-link\"/><h1>").reference(ctx.get("num"),ctx,"h").write(" of ").reference(ctx.getPath(false,["options","pageMetaData","count"]),ctx,"h").write("</h1></div>").section(ctx.get("events"),ctx,{"block":body_1},null).write("</div>");}function body_1(chk,ctx){return chk.section(ctx.get("main_image"),ctx,{"block":body_2},null).write("<!-- img class=\"image\" src=\"").reference(ctx.get("url"),ctx,"h").write("\" data-photo_id=\"").reference(ctx.get("id"),ctx,"h").write("\" / --><footer class=\"caption\"><div class=\"profile-thumb\"></div>\t\t  <div class=\"main-text\">").exists(ctx.get("tagline"),ctx,{"block":body_3},null).write("</div><div><!-- loop through sources -->").section(ctx.get("sources"),ctx,{"block":body_6},null).write("<!-- move this whole caption/bottom info bar thing to a partial! --><span class=\"time-and-location\">").reference(ctx.get("time_ago"),ctx,"h").write(" ").reference(ctx.get("location"),ctx,"h").write("</span></div></footer><div class=\"interaction-icons\"><span class=\"location\" data-photo_id=\"").reference(ctx.get("id"),ctx,"h").write("\"></span><span class=\"comments\" data-photo_id=\"").reference(ctx.get("id"),ctx,"h").write("\"></span></div>");}function body_2(chk,ctx){return chk.write("<div class=\"full-photo\" style=\"background-image:url(").reference(ctx.get("url"),ctx,"h").write(")\" data-photo_id=\"").reference(ctx.get("id"),ctx,"h").write("\"/>");}function body_3(chk,ctx){return chk.helper("truncate",ctx,{"block":body_4},{"value":body_5,"length":"35"});}function body_4(chk,ctx){return chk;}function body_5(chk,ctx){return chk.reference(ctx.get("tagline"),ctx,"h");}function body_6(chk,ctx){return chk.write("<span class=\"source-img ").reference(ctx.get("source_name"),ctx,"h").write("\"></span>");}return body_0;})();
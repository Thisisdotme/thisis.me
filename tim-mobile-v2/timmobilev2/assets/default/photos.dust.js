(function(){dust.register("photoAlbums",body_0);function body_0(chk,ctx){return chk.write("<div class=\"toolbar\"><h1>Photos</h1></div><div class=\"photo-albums\" id=\"photo-album-list\"><div>").section(ctx.get("albums"),ctx,{"block":body_1},null).write("</div></div>");}function body_1(chk,ctx){return chk.write("<div class=\"album\" data-album_id=\"").reference(ctx.get("id"),ctx,"h").write("\"><div class=\"album-info\">").reference(ctx.get("name"),ctx,"h").write(" (").reference(ctx.get("count"),ctx,"h").write(") <span class=\"more-link\" data-album_id=\"").reference(ctx.get("id"),ctx,"h").write("\">see all &#187;</span></div><div class=\"thumbs clearfix\">").section(ctx.get("cover_photo"),ctx,{"block":body_2},{"album_id":ctx.get("id")}).write("</div></div>");}function body_2(chk,ctx){return chk.write("<!-- img class=\"thumb\" src=\"").reference(ctx.get("url"),ctx,"h").write("\" data-id=\"").reference(ctx.get("id"),ctx,"h").write("\" data-album_id=\"").reference(ctx.get("album_id"),ctx,"h").write("\"/ --><div class=\"thumb\" style=\"background-image:url(").reference(ctx.get("url"),ctx,"h").write(");\" data-id=\"").reference(ctx.get("id"),ctx,"h").write("\" data-album_id=\"").reference(ctx.get("album_id"),ctx,"h").write("\"></div>");}return body_0;})();
(function(){dust.register("photoDetail",body_0);function body_0(chk,ctx){return chk.write("<div class=\"photo-detail\">").section(ctx.get("photo"),ctx,{"block":body_1},null).write("</div>");}function body_1(chk,ctx){return chk.write("<div id=\"photo-container\"><img src=\"http://farm").reference(ctx.get("farm"),ctx,"h").write(".static.flickr.com/").reference(ctx.get("server"),ctx,"h").write("/").reference(ctx.get("id"),ctx,"h").write("_").reference(ctx.get("secret"),ctx,"h").write(".jpg\" data-photo_id=\"").reference(ctx.get("id"),ctx,"h").write("\" /></div><div class=\"caption\"><div>").reference(ctx.get("title"),ctx,"h").write("</div><span class=\"list-link\"/><span class=\"grid-link\"/></div>");}return body_0;})();
(function(){dust.register("photoPage",body_0);function body_0(chk,ctx){return chk.write("<div class=\"photo-page\"><div class=\"toolbar\"><span class=\"grid-link\" data-toolbar-item=\"grid-link\"/><span class=\"detail-link\" data-toolbar-item=\"detail-link\"/><h1>").reference(ctx.get("num"),ctx,"h").write(" of ").reference(ctx.getPath(false,["options","pageMetaData","count"]),ctx,"h").write("</h1></div>").section(ctx.get("events"),ctx,{"block":body_1},null).write("</div>");}function body_1(chk,ctx){return chk.write("<div class=\"full-photo\" style=\"background-image:url(").reference(ctx.get("url"),ctx,"h").write(")\" data-photo_id=\"").reference(ctx.get("id"),ctx,"h").write("\"/><!-- img class=\"image\" src=\"").reference(ctx.get("url"),ctx,"h").write("\" data-photo_id=\"").reference(ctx.get("id"),ctx,"h").write("\" / --><div class=\"caption\"><div class=\"profile-thumb\"></div>\t\t  <div class=\"main-text\">").exists(ctx.get("title"),ctx,{"block":body_2},null).write("</div><div><!-- loop through sources -->").section(ctx.get("sources"),ctx,{"block":body_5},null).write("<!-- move this whole caption/bottom info bar thing to a partial! --><div class=\"time-and-location\">2 hrs ago, San Francisco</div></div></div><div class=\"interaction-icons\"><span class=\"location\" data-photo_id=\"").reference(ctx.get("id"),ctx,"h").write("\"></span><span class=\"comments\" data-photo_id=\"").reference(ctx.get("id"),ctx,"h").write("\"></span></div>");}function body_2(chk,ctx){return chk.helper("truncate",ctx,{"block":body_3},{"value":body_4,"length":"35"});}function body_3(chk,ctx){return chk;}function body_4(chk,ctx){return chk.reference(ctx.get("title"),ctx,"h");}function body_5(chk,ctx){return chk.write("<!-- loop through sources 2 --><span class=\"source-img ").reference(ctx.get("source_name"),ctx,"h").write("\"></span>");}return body_0;})();
(function(){dust.register("_photoList",body_0);function body_0(chk,ctx){return chk.section(ctx.get("photos"),ctx,{"block":body_1},null);}function body_1(chk,ctx){return chk.write("<div class=\"thumb\" style=\"background-image:url(").reference(ctx.get("url"),ctx,"h").write(")\" data-photo_id=\"").reference(ctx.get("id"),ctx,"h").write("\"></div>");}return body_0;})();
(function(){dust.register("photoGrid",body_0);function body_0(chk,ctx){return chk.write("<div class=\"toolbar\"><span class=\"grid-link\" data-toolbar-item=\"gridLink\"/><span class=\"detail-link\" data-toolbar-item=\"detailLink\"/><h1>").reference(ctx.get("name"),ctx,"h").write("</h1></div><div class=\"photo-grid\"><div id=\"photo-grid-scroll\" class=\"clearfix\"><div> <div class=\"clearfix grid-container\">").partial("_photoList",ctx).write("</div><div class=\"loading\">loading more...</div></div></div></div>");}return body_0;})();

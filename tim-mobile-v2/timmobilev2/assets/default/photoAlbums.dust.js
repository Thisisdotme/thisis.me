(function(){dust.register("photoAlbums",body_0);function body_0(chk,ctx){return chk.write("<div class=\"toolbar\"><h1>Photos</h1></div><div class=\"photo-albums\" id=\"photo-album-list\"><div>").section(ctx.get("albums"),ctx,{"block":body_1},null).write("</div></div>");}function body_1(chk,ctx){return chk.write("<div class=\"album\" data-album_id=\"").reference(ctx.get("id"),ctx,"h").write("\"><div class=\"album-info\">").reference(ctx.get("headline"),ctx,"h").write(" (").reference(ctx.get("count"),ctx,"h").write(") <span class=\"more-link\" data-album_id=\"").reference(ctx.get("id"),ctx,"h").write("\">see all &#187;</span></div><div class=\"thumbs clearfix\">").section(ctx.get("cover_photo"),ctx,{"block":body_2},{"album_id":ctx.get("id")}).write("</div></div>");}function body_2(chk,ctx){return chk.section(ctx.get("main_image"),ctx,{"block":body_3},null);}function body_3(chk,ctx){return chk.write("<!-- img class=\"thumb\" src=\"").reference(ctx.get("url"),ctx,"h").write("\" data-id=\"").reference(ctx.get("id"),ctx,"h").write("\" data-album_id=\"").reference(ctx.get("album_id"),ctx,"h").write("\"/ --><div class=\"thumb\" style=\"background-image:url(http://distilleryimage11.s3.amazonaws.com/177d99cebf3d11e1a9f71231382044a1_7.jpg);\" data-id=\"").reference(ctx.get("id"),ctx,"h").write("\" data-album_id=\"").reference(ctx.get("album_id"),ctx,"h").write("\"></div>");}return body_0;})();
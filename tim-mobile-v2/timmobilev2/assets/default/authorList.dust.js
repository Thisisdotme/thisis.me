(function(){dust.register("authorList",body_0);function body_0(chk,ctx){return chk.write("<div id=\"index-content\" data-role=\"content\"><ul>").section(ctx.get("authors"),ctx,{"block":body_1},null).write("</ul></div><!-- /content -->");}function body_1(chk,ctx){return chk.write("<li><a href=\"").reference(ctx.get("author_name"),ctx,"h").write("\" data-author_name=\"").reference(ctx.get("author_name"),ctx,"h").write("\"\"><img src=\"/").reference(ctx.get("author_name"),ctx,"h").write("/asset/profile_thumb.jpg\"/><span>").reference(ctx.get("full_name"),ctx,"h").write("</span></a></li>");}return body_0;})();
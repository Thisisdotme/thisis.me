(function(){dust.register("_authorFeatures",body_0);function body_0(chk,ctx){return chk.write("<div class=\"features-form tab-content settings-form\"><h3>Add/Remove Features for ").reference(ctx.get("name"),ctx,"h").write("</h3><ul>").section(ctx.get("features"),ctx,{"block":body_1},null).write("</ul><form id=\"features-form\" method=\"POST\"></form></div>");}function body_1(chk,ctx){return chk.write("<li class=\"").reference(ctx.get("name"),ctx,"h").write(" ").reference(ctx.get("enabled"),ctx,"h").write("\"> ").reference(ctx.get("name"),ctx,"h").write(" <a class=\"activate\" data-feature-name=\"").reference(ctx.get("name"),ctx,"h").write("\" href=\"").reference(ctx.get("url"),ctx,"h").write("\">activate</a><span class=\"deactivate\">active</span></li>");}return body_0;})();
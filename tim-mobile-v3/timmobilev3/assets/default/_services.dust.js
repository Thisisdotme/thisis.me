(function(){dust.register("_services",body_0);function body_0(chk,ctx){return chk.write("<div class=\"services-form settings-form tab-content\"><h3>Add/Remove Accounts for ").reference(ctx.get("name"),ctx,"h").write("</h3><ul>").section(ctx.get("services"),ctx,{"block":body_1},null).write("</ul><form id=\"services-form\" method=\"POST\"></form></div>");}function body_1(chk,ctx){return chk.write("<li class=\"").reference(ctx.get("name"),ctx,"h").write(" ").reference(ctx.get("enabled"),ctx,"h").write("\"> ").reference(ctx.get("name"),ctx,"h").write(" <a class=\"activate\" href=\"").reference(ctx.get("url"),ctx,"h").write("\">activate</a><span class=\"deactivate\">active</span></li>");}return body_0;})();
(function(){dust.register("toolbar",body_0);function body_0(chk,ctx){return chk.section(ctx.get("items"),ctx,{"block":body_1},null);}function body_1(chk,ctx){return chk.write("<span class=\"").reference(ctx.get("name"),ctx,"h").write("\" data-toolbar-item=\"").reference(ctx.get("name"),ctx,"h").write("\"/>");}return body_0;})();
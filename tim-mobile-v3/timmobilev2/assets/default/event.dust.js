(function(){dust.register("event",body_0);function body_0(chk,ctx){return chk.write("<div class=\"toolbar\"><h1>News</h1></div><div class=\"mi-content\"  style=\"height: 100%;\">").section(ctx.get("events"),ctx,{"block":body_1},null).write("</div>");}function body_1(chk,ctx){return chk.write("<div class=\"event ").reference(ctx.get("event_class"),ctx,"h").write("\" data-event_id=\"").reference(ctx.get("event_id"),ctx,"h").write("\">").partial(body_2,ctx).write("</div>");}function body_2(chk,ctx){return chk.reference(ctx.get("event_template"),ctx,"h");}return body_0;})();
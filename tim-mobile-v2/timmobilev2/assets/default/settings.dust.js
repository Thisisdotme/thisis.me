(function(){dust.register("settings",body_0);function body_0(chk,ctx){return chk.write("<div class=\"toolbar\"><span class=\"cancel-link\" href=\"#\">Back</span><h1>Settings</h1></div><div class=\"settings-container split-pane\"><nav class=\"side-tabs\"><ul><li class=\"profile-tab\"></li><li class=\"services-tab\"></li><li class=\"features-tab\"></li></ul></nav><div class=\"main-content\">").partial("_profileEdit",ctx).partial("_services",ctx).partial("_authorFeatures",ctx).write("</div></div>");}return body_0;})();
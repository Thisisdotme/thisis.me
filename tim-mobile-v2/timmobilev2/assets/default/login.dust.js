(function(){dust.register("login",body_0);function body_0(chk,ctx){return chk.write("<div class=\"toolbar\"><span class=\"cancel-link\" href=\"#\">Cancel</span><h1>Log In</h1></div><div class=\"login-form\"><div class=\"message\"></div><form id=\"login-form\" action=\"\" method=\"post\"><label for=\"login-login\">Author Name</label><input id=\"login-login\" type=\"text\" autocapitalize=\"off\" autocorrect=\"off\" autocomplete=\"off\" name=\"login\" value=\"\"/><label for=\"login-password\">Password</label><input id=\"login-password\" type=\"password\" name=\"password\" value=\"\"/></form><input id=\"login-submit\" type=\"submit\" value=\"Log In\" /><a id=\"create-user-link\" href=\"/newuser\">Sign Up</a></div>");}return body_0;})();
(function(){dust.register("newuser",body_0);function body_0(chk,ctx){return chk.write("<div class=\"toolbar\"><span class=\"cancel-link\" href=\"#\">Cancel</span><h1>Create New User</h1></div><div class=\"newuser-form input-form\"><div class=\"form-container\"><div class=\"message\"></div><form id=\"newuser-form\" action=\"\" method=\"post\"><label for=\"newuser-name\">Author Name</label><input id=\"newuser-name\" type=\"text\" autocapitalize=\"off\" autocorrect=\"off\" autocomplete=\"off\" name=\"login\" value=\"\"/><label for=\"newuser-fullname\">Full Name</label><input id=\"newuser-fullname\" type=\"text\" autocapitalize=\"off\" autocorrect=\"off\" autocomplete=\"off\" name=\"login\" value=\"\"/><label for=\"newuser-email\">Email</label><input id=\"newuser-email\" type=\"email\" autocapitalize=\"off\" autocorrect=\"off\" autocomplete=\"off\" name=\"login\" value=\"\"/><label for=\"newuser-password\">Password</label><input id=\"newuser-password\" type=\"password\" name=\"password\" value=\"\"/></form><input id=\"newuser-submit\" type=\"submit\" value=\"Create\" /><a id=\"login-link\" href=\"/newuser\">Already have an account? Sign In!</a></div></div>");}return body_0;})();
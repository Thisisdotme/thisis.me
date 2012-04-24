
# define services
#
curl -i -X PUT -d '{"color_icon_high_res":"img/h/services/color/Me.png","color_icon_medium_res":"img/m/services/color/Me.png","color_icon_low_res":"img/l/services/color/Me.png","mono_icon_high_res":"img/h/services/mono/placeholder.png","mono_icon_medium_res":"img/m/services/mono/placeholder.png","mono_icon_low_res":"img/l/services/mono/placeholder.png"}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/services/me
curl -i -X PUT -d '{"color_icon_high_res":"img/h/services/color/Twitter.png","color_icon_medium_res":"img/m/services/color/Twitter.png","color_icon_low_res":"img/l/services/color/Twitter.png","mono_icon_high_res":"img/h/services/mono/Twitter.png","mono_icon_medium_res":"img/m/services/mono/Twitter.png","mono_icon_low_res":"img/l/services/mono/Twitter.png"}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/services/twitter
curl -i -X PUT -d '{"color_icon_high_res":"img/h/services/color/Facebook.png","color_icon_medium_res":"img/m/services/color/Facebook.png","color_icon_low_res":"img/l/services/color/Facebook.png","mono_icon_high_res":"img/h/services/mono/Facebook.png","mono_icon_medium_res":"img/m/services/mono/Facebook.png","mono_icon_low_res":"img/l/services/mono/Facebook.png"}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/services/facebook
curl -i -X PUT -d '{"color_icon_high_res":"img/h/services/color/Wordpress.png","color_icon_medium_res":"img/m/services/color/Wordpress.png","color_icon_low_res":"img/l/services/color/Wordpress.png","mono_icon_high_res":"img/h/services/mono/Wordpress.png","mono_icon_medium_res":"img/m/services/mono/Wordpress.png","mono_icon_low_res":"img/l/services/mono/Wordpress.png"}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/services/wordpress
curl -i -X PUT -d '{"color_icon_high_res":"img/h/services/color/YouTube.png","color_icon_medium_res":"img/m/services/color/YouTube.png","color_icon_low_res":"img/l/services/color/YouTube.png","mono_icon_high_res":"img/h/services/mono/YouTube.png","mono_icon_medium_res":"img/m/services/mono/YouTube.png","mono_icon_low_res":"img/l/services/mono/YouTube.png"}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/services/youtube
curl -i -X PUT -d '{"color_icon_high_res":"img/h/services/color/LinkedIn.png","color_icon_medium_res":"img/m/services/color/LinkedIn.png","color_icon_low_res":"img/l/services/color/LinkedIn.png","mono_icon_high_res":"img/h/services/mono/LinkedIn.png","mono_icon_medium_res":"img/m/services/mono/LinkedIn.png","mono_icon_low_res":"img/l/services/mono/LinkedIn.png"}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/services/linkedin
curl -i -X PUT -d '{"color_icon_high_res":"img/h/services/color/GooglePlus.png","color_icon_medium_res":"img/m/services/color/GooglePlus.png","color_icon_low_res":"img/l/services/color/GooglePlus.png","mono_icon_high_res":"img/h/services/mono/GooglePlus.png","mono_icon_medium_res":"img/m/services/mono/GooglePlus.png","mono_icon_low_res":"img/l/services/mono/GooglePlus.png"}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/services/googleplus
curl -i -X PUT -d '{"color_icon_high_res":"img/h/services/color/Foursquare.png","color_icon_medium_res":"img/m/services/color/Foursquare.png","color_icon_low_res":"img/l/services/color/Foursquare.png","mono_icon_high_res":"img/h/services/mono/Foursquare.png","mono_icon_medium_res":"img/m/services/mono/Foursquare.png","mono_icon_low_res":"img/l/services/mono/Foursquare.png"}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/services/foursquare
curl -i -X PUT -d '{"color_icon_high_res":"img/h/services/color/Instagram.png","color_icon_medium_res":"img/m/services/color/Instagram.png","color_icon_low_res":"img/l/services/color/Instagram.png","mono_icon_high_res":"img/h/services/mono/Instagram.png","mono_icon_medium_res":"img/m/services/mono/Instagram.png","mono_icon_low_res":"img/l/services/mono/Instagram.png"}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/services/instagram
curl -i -X PUT -d '{"color_icon_high_res":"img/h/services/color/placeholder.png","color_icon_medium_res":"img/m/services/color/placeholder.png","color_icon_low_res":"img/l/services/color/placeholder.png","mono_icon_high_res":"img/h/services/mono/placeholder.png","mono_icon_medium_res":"img/m/services/mono/placeholder.png","mono_icon_low_res":"img/l/services/mono/placeholder.png"}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/services/flickr
#curl -i -X PUT -d '{}' api.thisis.me/v1/services/typepad
#curl -i -X PUT -d '{}' api.thisis.me/v1/services/blogger
#curl -i -X PUT -d '{}' api.thisis.me/v1/services/last.fm

# create new author howard and associate services
#
curl -i -X PUT -d '{"password":"mi","fullname":"Howard Burrows","email":"howard@mobileidentity.me"}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/authors/howard

curl -i -X PUT -d '{}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/authors/howard/services/me
curl -i -X PUT -d '{"access_token":"14058912-DWWuU3QOcNVwEXMQO8oZT0XsEX8BV3ABbnNhsp80Q","access_token_secret":"qxg2IOkLfj82KQlJTuZ1LwtkpVZ0xdDBel6Q2MS9ik"}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/authors/howard/services/twitter
curl -i -X PUT -d '{"access_token":"12937196.d43579f.d38f14f7f8f742048f14d826dbc1bce7"}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/authors/howard/services/instagram
curl -i -X PUT -d '{"access_token":"72157628366602963-cae202cd31e7af05"}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/authors/howard/services/flickr


# create new author loree and associate services
#
curl -i -X PUT -d '{"password":"mi","fullname":"Loree Hirschman","email":"loree@mobileidentity.me"}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/authors/loree

curl -i -X PUT -d '{}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/authors/loree/services/me
curl -i -X PUT -d '{"access_token":"14603721-z82wscRuTCjIeTRqlqE8ckKjeuy7P9TBZhnnuwKk","access_token_secret":"AI2fWbgEkErymyd3GUgD0uQvjhKNGC61kYj6H5I"}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/authors/loree/services/twitter
curl -i -X PUT -d '{"access_token":"815189.d43579f.8e06d7278a214a609c5e7c2354695557"}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/authors/loree/services/instagram
curl -i -X PUT -d '{}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/authors/loree/services/facebook
curl -i -X PUT -d '{}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/authors/loree/services/wordpress
curl -i -X PUT -d '{}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/authors/loree/services/flickr
curl -i -X PUT -d '{"access_token":"ee529f7f-6d21-49f0-badf-f8d337926cd6","access_token_secret":"a524b247-8207-4e5f-a84b-f7d69eab4774"}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/authors/loree/services/linkedin

# create new user alan - user has non-ascii character
#
curl -X PUT -F password=mi -F fullname="Alan Ascaño" -F email=allanascano@gmail.com api.thisis.me/v1/authors/alan
curl -i -X PUT -d '{}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/authors/alan/services/me

# create new user dee - user has non-ascii character
#
curl -X PUT -F password=mi -F fullname="Dee Santiago" -F email=deesantiago@gmail.com api.thisis.me/v1/authors/dee
curl -i -X PUT -d '{}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/authors/dee/services/me

# create new user tina - user has non-ascii character
#
curl -X PUT -F password=mi -F fullname="Tina Galve" -F email=tina.galve@gmail.com api.thisis.me/v1/authors/tina
curl -i -X PUT -d '{}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/authors/tina/services/me

# create new user phil - user has non-ascii character
#

# Philip Goffin <phil@mobileidentity.me>
curl -X PUT -F password=mi -F fullname="Philip Goffin" -F email=phil@mobileidentity.me api.thisis.me/v1/authors/phil
curl -X PUT -d '{}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/authors/phil/services/me

# Harry Thompson <harry@mobileidentity.me>
curl -X PUT -F password=mi -F fullname="Harry Thompson" -F email=harry@mobileidentity.me api.thisis.me/v1/authors/harry
curl -X PUT -d '{}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/authors/harry/services/me

# Phil Black <pblack@trueventures.com>
curl -X PUT -F password=mi -F fullname="Philip Black" -F email=pblack@trueventures.com api.thisis.me/v1/authors/philblack
curl -X PUT -d '{}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/authors/philblack/services/me


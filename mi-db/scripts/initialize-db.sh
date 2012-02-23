
# define features
#
curl -i -X PUT -d '{"color_icon_high_res":"img/h/features/color/Me.png","color_icon_medium_res":"img/m/features/color/Me.png","color_icon_low_res":"img/l/features/color/Me.png","mono_icon_high_res":"img/h/features/mono/placeholder.png","mono_icon_medium_res":"img/m/features/mono/placeholder.png","mono_icon_low_res":"img/l/features/mono/placeholder.png"}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/features/me
curl -i -X PUT -d '{"color_icon_high_res":"img/h/features/color/Twitter.png","color_icon_medium_res":"img/m/features/color/Twitter.png","color_icon_low_res":"img/l/features/color/Twitter.png","mono_icon_high_res":"img/h/features/mono/Twitter.png","mono_icon_medium_res":"img/m/features/mono/Twitter.png","mono_icon_low_res":"img/l/features/mono/Twitter.png"}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/features/twitter
curl -i -X PUT -d '{"color_icon_high_res":"img/h/features/color/Facebook.png","color_icon_medium_res":"img/m/features/color/Facebook.png","color_icon_low_res":"img/l/features/color/Facebook.png","mono_icon_high_res":"img/h/features/mono/Facebook.png","mono_icon_medium_res":"img/m/features/mono/Facebook.png","mono_icon_low_res":"img/l/features/mono/Facebook.png"}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/features/facebook
curl -i -X PUT -d '{"color_icon_high_res":"img/h/features/color/Wordpress.png","color_icon_medium_res":"img/m/features/color/Wordpress.png","color_icon_low_res":"img/l/features/color/Wordpress.png","mono_icon_high_res":"img/h/features/mono/Wordpress.png","mono_icon_medium_res":"img/m/features/mono/Wordpress.png","mono_icon_low_res":"img/l/features/mono/Wordpress.png"}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/features/wordpress
curl -i -X PUT -d '{"color_icon_high_res":"img/h/features/color/YouTube.png","color_icon_medium_res":"img/m/features/color/YouTube.png","color_icon_low_res":"img/l/features/color/YouTube.png","mono_icon_high_res":"img/h/features/mono/YouTube.png","mono_icon_medium_res":"img/m/features/mono/YouTube.png","mono_icon_low_res":"img/l/features/mono/YouTube.png"}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/features/youtube
curl -i -X PUT -d '{"color_icon_high_res":"img/h/features/color/LinkedIn.png","color_icon_medium_res":"img/m/features/color/LinkedIn.png","color_icon_low_res":"img/l/features/color/LinkedIn.png","mono_icon_high_res":"img/h/features/mono/LinkedIn.png","mono_icon_medium_res":"img/m/features/mono/LinkedIn.png","mono_icon_low_res":"img/l/features/mono/LinkedIn.png"}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/features/linkedin
curl -i -X PUT -d '{"color_icon_high_res":"img/h/features/color/GooglePlus.png","color_icon_medium_res":"img/m/features/color/GooglePlus.png","color_icon_low_res":"img/l/features/color/GooglePlus.png","mono_icon_high_res":"img/h/features/mono/GooglePlus.png","mono_icon_medium_res":"img/m/features/mono/GooglePlus.png","mono_icon_low_res":"img/l/features/mono/GooglePlus.png"}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/features/googleplus
curl -i -X PUT -d '{"color_icon_high_res":"img/h/features/color/Foursquare.png","color_icon_medium_res":"img/m/features/color/Foursquare.png","color_icon_low_res":"img/l/features/color/Foursquare.png","mono_icon_high_res":"img/h/features/mono/Foursquare.png","mono_icon_medium_res":"img/m/features/mono/Foursquare.png","mono_icon_low_res":"img/l/features/mono/Foursquare.png"}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/features/foursquare
curl -i -X PUT -d '{"color_icon_high_res":"img/h/features/color/Instagram.png","color_icon_medium_res":"img/m/features/color/Instagram.png","color_icon_low_res":"img/l/features/color/Instagram.png","mono_icon_high_res":"img/h/features/mono/Instagram.png","mono_icon_medium_res":"img/m/features/mono/Instagram.png","mono_icon_low_res":"img/l/features/mono/Instagram.png"}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/features/instagram
curl -i -X PUT -d '{"color_icon_high_res":"img/h/features/color/placeholder.png","color_icon_medium_res":"img/m/features/color/placeholder.png","color_icon_low_res":"img/l/features/color/placeholder.png","mono_icon_high_res":"img/h/features/mono/placeholder.png","mono_icon_medium_res":"img/m/features/mono/placeholder.png","mono_icon_low_res":"img/l/features/mono/placeholder.png"}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/features/flickr
#curl -i -X PUT -d '{}' api.thisis.me/v1/features/typepad
#curl -i -X PUT -d '{}' api.thisis.me/v1/features/blogger
#curl -i -X PUT -d '{}' api.thisis.me/v1/features/last.fm

# create new author howard and associate features
#
curl -i -X PUT -F password=mi -F fullname="Howard Burrows" -F email=howard@mobileidentity.me api.thisis.me/v1/authors/howard

curl -i -X PUT -d '{}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/authors/howard/features/me
curl -i -X PUT -d '{"access_token":"14058912-DWWuU3QOcNVwEXMQO8oZT0XsEX8BV3ABbnNhsp80Q","access_token_secret":"qxg2IOkLfj82KQlJTuZ1LwtkpVZ0xdDBel6Q2MS9ik"}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/authors/howard/features/twitter
curl -i -X PUT -d '{"access_token":"12937196.d43579f.d38f14f7f8f742048f14d826dbc1bce7"}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/authors/howard/features/instagram
curl -i -X PUT -d '{"access_token":"72157628366602963-cae202cd31e7af05"}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/authors/howard/features/flickr


# create new author loree and associate features
#
curl -i -X PUT -F password=mi -F fullname="Loree Hirschman" -F email=loree@mobileidentity.me api.thisis.me/v1/authors/loree

curl -i -X PUT -d '{}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/authors/loree/features/me
curl -i -X PUT -d '{"access_token":"14603721-z82wscRuTCjIeTRqlqE8ckKjeuy7P9TBZhnnuwKk","access_token_secret":"AI2fWbgEkErymyd3GUgD0uQvjhKNGC61kYj6H5I"}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/authors/loree/features/twitter
curl -i -X PUT -d '{"access_token":"815189.d43579f.8e06d7278a214a609c5e7c2354695557"}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/authors/loree/features/instagram
curl -i -X PUT -d '{}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/authors/loree/features/facebook
curl -i -X PUT -d '{}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/authors/loree/features/wordpress
curl -i -X PUT -d '{}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/authors/loree/features/flickr
curl -i -X PUT -d '{"access_token":"ee529f7f-6d21-49f0-badf-f8d337926cd6","access_token_secret":"a524b247-8207-4e5f-a84b-f7d69eab4774"}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/authors/loree/features/linkedin

# create new user alan - user has non-ascii character
#
curl -X PUT -F password=mi -F fullname="Alan Ascaño" -F email=allanascano@gmail.com api.thisis.me/v1/authors/alan
curl -i -X PUT -d '{}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/authors/alan/features/me

# create new user dee - user has non-ascii character
#
curl -X PUT -F password=mi -F fullname="Dee Santiago" -F email=deesantiago@gmail.com api.thisis.me/v1/authors/dee
curl -i -X PUT -d '{}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/authors/dee/features/me

# create new user tina - user has non-ascii character
#
curl -X PUT -F password=mi -F fullname="Tina Galve" -F email=tina.galve@gmail.com api.thisis.me/v1/authors/tina
curl -i -X PUT -d '{}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/authors/tina/features/me

# create new user phil - user has non-ascii character
#

# Philip Goffin <phil@mobileidentity.me>
curl -X PUT -F password=mi -F fullname="Philip Goffin" -F email=phil@mobileidentity.me api.thisis.me/v1/authors/phil
curl -X PUT -d '{}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/authors/phil/features/me

# Harry Thompson <harry@mobileidentity.me>
curl -X PUT -F password=mi -F fullname="Harry Thompson" -F email=harry@mobileidentity.me api.thisis.me/v1/authors/harry
curl -X PUT -d '{}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/authors/harry/features/me

# Phil Black <pblack@trueventures.com>
curl -X PUT -F password=mi -F fullname="Philip Black" -F email=pblack@trueventures.com api.thisis.me/v1/authors/philblack
curl -X PUT -d '{}' -H "Content-Type: application/json; charset=utf-8" api.thisis.me/v1/authors/philblack/features/me


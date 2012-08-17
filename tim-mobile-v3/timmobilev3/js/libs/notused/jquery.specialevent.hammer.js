/*
 * special event API with Hammer.JS
 * version 0.9
 * author: Damien Antipa
 * https://github.com/dantipa/hammer.js
 */
(function ($) {
    var hammerEvents = ['hold','tap','doubletap','transformstart','transform','transformend','dragstart','drag','dragend','swipe','release'];

    $.each(hammerEvents, function(i, event) {
        var elems = $([]);

        $.event.special[event] = {

            setup: function(data, namespaces, eventHandle) {
                var $target = $(this),
                    $body = $('body'),
                    hammer;
                    
                elems = elems.add( this );
                //console.log('target', $target);
                
                if (elems.length === 1) {
                    $body.data('hammerjs_' + event, new Hammer(document.body, data));
                }

                hammer = $body.data('hammerjs_' + event);

                hammer['on'+ event] = function (ev) {
                    eventHandler(ev, event, $target);
                };
            },

            teardown: function(namespaces) {
                var $target = $(this),
                    $body = $('body'),
                    hammer = $body.data('hammerjs_' + event);

                if(hammer && hammer['on'+ event]) {
                    delete hammer['on'+ event];
                }
            }
        };
        function eventHandler(event, eventName) {
          //alert(event);
          var $target = $(event.target ? event.target : event.originalEvent.target);
          //console.log(event, eventName, $target);
          $target.trigger($.Event(eventName, event));
        }
    });
}(jQuery));

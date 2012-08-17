
// usage: log('inside coolFunc', this, arguments);
// paulirish.com/2009/log-a-lightweight-wrapper-for-consolelog/
window.log = function(){
  log.history = log.history || [];   // store logs to an array for reference
  log.history.push(arguments);
  if(this.console) {
    arguments.callee = arguments.callee.caller;
    var newarr = [].slice.call(arguments);
    (typeof console.log === 'object' ? log.apply.call(console.log, console, newarr) : console.log.apply(console, newarr));
  }
};

// make it safe to use console.log always
(function(b){function c(){}for(var d="assert,clear,count,debug,dir,dirxml,error,exception,firebug,group,groupCollapsed,groupEnd,info,log,memoryProfile,memoryProfileEnd,profile,profileEnd,table,time,timeEnd,timeStamp,trace,warn".split(","),a;a=d.pop();){b[a]=b[a]||c}})((function(){try
{console.log();return window.console;}catch(err){return window.console={};}})());


// place any jQuery/helper plugins in here, instead of separate, slower script files.

// parseUri 1.2.2
// (c) Steven Levithan <stevenlevithan.com>
// MIT License

function parseUri (str) {
	var	o   = parseUri.options,
		m   = o.parser[o.strictMode ? "strict" : "loose"].exec(str),
		uri = {},
		i   = 14;

	while (i--) uri[o.key[i]] = m[i] || "";

	uri[o.q.name] = {};
	uri[o.key[12]].replace(o.q.parser, function ($0, $1, $2) {
		if ($1) uri[o.q.name][$1] = $2;
	});

	return uri;
};

parseUri.options = {
	strictMode: false,
	key: ["source","protocol","authority","userInfo","user","password","host","port","relative","path","directory","file","query","anchor"],
	q:   {
		name:   "queryKey",
		parser: /(?:^|&)([^&=]*)=?([^&]*)/g
	},
	parser: {
		strict: /^(?:([^:\/?#]+):)?(?:\/\/((?:(([^:@]*)(?::([^:@]*))?)?@)?([^:\/?#]*)(?::(\d*))?))?((((?:[^?#\/]*\/)*)([^?#]*))(?:\?([^#]*))?(?:#(.*))?)/,
		loose:  /^(?:(?![^:@]+:[^:@\/]*@)([^:\/?#.]+):)?(?:\/\/)?((?:(([^:@]*)(?::([^:@]*))?)?@)?([^:\/?#]*)(?::(\d*))?)(((\/(?:[^?#](?![^?#\/]*\.[^?#\/.]+(?:[?#]|$)))*\/?)?([^?#\/]*))(?:\?([^#]*))?(?:#(.*))?)/
	}
};

/**
 * Timeago is a jQuery plugin that makes it easy to support automatically
 * updating fuzzy timestamps (e.g. "4 minutes ago" or "about 1 day ago").
 *
 * @name timeago
 * @version 0.10.0
 * @requires jQuery v1.2.3+
 * @author Ryan McGeary
 * @license MIT License - http://www.opensource.org/licenses/mit-license.php
 *
 * For usage and examples, visit:
 * http://timeago.yarp.com/
 *
 * Copyright (c) 2008-2011, Ryan McGeary (ryanonjavascript -[at]- mcgeary [*dot*] org)
 */
(function($) {
  $.timeago = function(timestamp) {
    if (timestamp instanceof Date) {
      return inWords(timestamp);
    } else if (typeof timestamp === "string") {
      return inWords($.timeago.parse(timestamp));
    } else {
      return inWords($.timeago.datetime(timestamp));
    }
  };
  var $t = $.timeago;

  $.extend($.timeago, {
    settings: {
      refreshMillis: 60000,
      allowFuture: false,
      strings: {
        prefixAgo: null,
        prefixFromNow: null,
        suffixAgo: "ago",
        suffixFromNow: "from now",
        seconds: "a minute",
        minute: "a minute",
        minutes: "%d minutes",
        hour: "an hour",
        hours: "%d hours",
        day: "a day",
        days: "%d days",
        month: "a month",
        months: "%d months",
        year: "a year",
        years: "%d years",
        numbers: []
      }
    },
    inWords: function(distanceMillis) {
      var $l = this.settings.strings;
      var prefix = $l.prefixAgo;
      var suffix = $l.suffixAgo;
      if (this.settings.allowFuture) {
        if (distanceMillis < 0) {
          prefix = $l.prefixFromNow;
          suffix = $l.suffixFromNow;
        }
      }

      var seconds = Math.abs(distanceMillis) / 1000;
      var minutes = seconds / 60;
      var hours = minutes / 60;
      var days = hours / 24;
      var years = days / 365;

      function substitute(stringOrFunction, number) {
        var string = $.isFunction(stringOrFunction) ? stringOrFunction(number, distanceMillis) : stringOrFunction;
        var value = ($l.numbers && $l.numbers[number]) || number;
        return string.replace(/%d/i, value);
      }

      var words = seconds < 45 && substitute($l.seconds, Math.round(seconds)) ||
        seconds < 90 && substitute($l.minute, 1) ||
        minutes < 45 && substitute($l.minutes, Math.round(minutes)) ||
        minutes < 90 && substitute($l.hour, 1) ||
        hours < 24 && substitute($l.hours, Math.round(hours)) ||
        hours < 48 && substitute($l.day, 1) ||
        days < 30 && substitute($l.days, Math.floor(days)) ||
        days < 60 && substitute($l.month, 1) ||
        days < 365 && substitute($l.months, Math.floor(days / 30)) ||
        years < 2 && substitute($l.year, 1) ||
        substitute($l.years, Math.floor(years));

      return $.trim([prefix, words, suffix].join(" "));
    },
    parse: function(iso8601) {
      var s = $.trim(iso8601);
      s = s.replace(/\.\d\d\d+/,""); // remove milliseconds
      s = s.replace(/-/,"/").replace(/-/,"/");
      s = s.replace(/T/," ").replace(/Z/," UTC");
      s = s.replace(/([\+\-]\d\d)\:?(\d\d)/," $1$2"); // -04:00 -> -0400
      return new Date(s);
    },
    datetime: function(elem) {
      // jQuery's `is()` doesn't play well with HTML5 in IE
      var isTime = $(elem).get(0).tagName.toLowerCase() === "time"; // $(elem).is("time");
      var iso8601 = isTime ? $(elem).attr("datetime") : $(elem).attr("title");
      return $t.parse(iso8601);
    }
  });

  $.fn.timeago = function() {
    var self = this;
    self.each(refresh);

    var $s = $t.settings;
    if ($s.refreshMillis > 0) {
      setInterval(function() { self.each(refresh); }, $s.refreshMillis);
    }
    return self;
  };

  function refresh() {
    var data = prepareData(this);
    if (!isNaN(data.datetime)) {
      $(this).text(inWords(data.datetime));
    }
    return this;
  }

  function prepareData(element) {
    element = $(element);
    if (!element.data("timeago")) {
      element.data("timeago", { datetime: $t.datetime(element) });
      var text = $.trim(element.text());
      if (text.length > 0) {
        element.attr("title", text);
      }
    }
    return element.data("timeago");
  }

  function inWords(date) {
    return $t.inWords(distance(date));
  }

  function distance(date) {
    return (new Date().getTime() - date.getTime());
  }

  // fix for IE6 suckage
  document.createElement("abbr");
  document.createElement("time");
}(jQuery));

/*global jQuery */
/*!	
* FitText.js 1.0
*
* Copyright 2011, Dave Rupert http://daverupert.com
* Released under the WTFPL license 
* http://sam.zoy.org/wtfpl/
*
* Date: Thu May 05 14:23:00 2011 -0600
*/

(function( $ ){
	
  $.fn.fitText = function( kompressor, options ) {
	   
    // Setup options
    var compressor = kompressor || 1,
        settings = $.extend({
          'minFontSize' : Number.NEGATIVE_INFINITY,
          'maxFontSize' : Number.POSITIVE_INFINITY
        }, options);
	
    return this.each(function(){

      // Store the object
      var $this = $(this); 
        
      // Resizer() resizes items based on the object width divided by the compressor * 10
      var resizer = function () {
        $this.css('font-size', Math.max(Math.min($this.width() / (compressor*10), parseFloat(settings.maxFontSize)), parseFloat(settings.minFontSize)));
      };

      // Call once to set.
      resizer();
				
      // Call on resize. Opera debounces their resize by default. 
      $(window).on('resize', resizer);
      	
    });

  };

})( jQuery );

//jquery cookies
/*jshint eqnull:true */
/*!
 * jQuery Cookie Plugin v1.2
 * https://github.com/carhartl/jquery-cookie
 *
 * Copyright 2011, Klaus Hartl
 * Dual licensed under the MIT or GPL Version 2 licenses.
 * http://www.opensource.org/licenses/mit-license.php
 * http://www.opensource.org/licenses/GPL-2.0
 */
(function ($, document, undefined) {

	var pluses = /\+/g;

	function raw(s) {
		return s;
	}

	function decoded(s) {
		return decodeURIComponent(s.replace(pluses, ' '));
	}

	$.cookie = function (key, value, options) {

		// key and at least value given, set cookie...
		if (value !== undefined && !/Object/.test(Object.prototype.toString.call(value))) {
			options = $.extend({}, $.cookie.defaults, options);

			if (value === null) {
				options.expires = -1;
			}

			if (typeof options.expires === 'number') {
				var days = options.expires, t = options.expires = new Date();
				t.setDate(t.getDate() + days);
			}

			value = String(value);

			return (document.cookie = [
				encodeURIComponent(key), '=', options.raw ? value : encodeURIComponent(value),
				options.expires ? '; expires=' + options.expires.toUTCString() : '', // use expires attribute, max-age is not supported by IE
				options.path    ? '; path=' + options.path : '',
				options.domain  ? '; domain=' + options.domain : '',
				options.secure  ? '; secure' : ''
			].join(''));
		}

		// key and possibly options given, get cookie...
		options = value || $.cookie.defaults || {};
		var decode = options.raw ? raw : decoded;
		var cookies = document.cookie.split('; ');
		for (var i = 0, parts; (parts = cookies[i] && cookies[i].split('=')); i++) {
			if (decode(parts.shift()) === key) {
				return decode(parts.join('='));
			}
		}

		return null;
	};

	$.cookie.defaults = {};

	$.removeCookie = function (key, options) {
		if ($.cookie(key, options) !== null) {
			$.cookie(key, null, options);
			return true;
		}
		return false;
	};

})(jQuery, document);


//iscroll
(function(a,b){function E(a){if(e==="")return a;a=a.charAt(0).toUpperCase()+a.substr(1);return e+a}var c=Math,d=b.createElement("div").style,e=function(){var a="t,webkitT,MozT,msT,OT".split(","),b,c=0,e=a.length;for(;c<e;c++){b=a[c]+"ransform";if(b in d){return a[c].substr(0,a[c].length-1)}}return false}(),f=e?"-"+e.toLowerCase()+"-":"",g=E("transform"),h=E("transitionProperty"),i=E("transitionDuration"),j=E("transformOrigin"),k=E("transitionTimingFunction"),l=E("transitionDelay"),m=/android/gi.test(navigator.appVersion),n=/iphone|ipad/gi.test(navigator.appVersion),o=/hp-tablet/gi.test(navigator.appVersion),p=E("perspective")in d,q="ontouchstart"in a&&!o,r=!!e,s=E("transition")in d,t="onorientationchange"in a?"orientationchange":"resize",u=q?"touchstart":"mousedown",v=q?"touchmove":"mousemove",w=q?"touchend":"mouseup",x=q?"touchcancel":"mouseup",y=e=="Moz"?"DOMMouseScroll":"mousewheel",z=function(){if(e===false)return false;var a={"":"transitionend",webkit:"webkitTransitionEnd",Moz:"transitionend",O:"oTransitionEnd",ms:"MSTransitionEnd"};return a[e]}(),A=function(){return a.requestAnimationFrame||a.webkitRequestAnimationFrame||a.mozRequestAnimationFrame||a.oRequestAnimationFrame||a.msRequestAnimationFrame||function(a){return setTimeout(a,1)}}(),B=function(){return a.cancelRequestAnimationFrame||a.webkitCancelAnimationFrame||a.webkitCancelRequestAnimationFrame||a.mozCancelRequestAnimationFrame||a.oCancelRequestAnimationFrame||a.msCancelRequestAnimationFrame||clearTimeout}(),C=p?" translateZ(0)":"",D=function(c,d){var e=this,l;e.wrapper=typeof c=="object"?c:b.getElementById(c);e.wrapper.style.overflow="hidden";e.scroller=e.wrapper.children[0];e.options={hScroll:true,vScroll:true,x:0,y:0,bounce:true,bounceLock:false,momentum:true,lockDirection:true,useTransform:true,useTransition:false,topOffset:0,checkDOMChanges:false,handleClick:true,hScrollbar:true,vScrollbar:true,fixedScrollbar:m,hideScrollbar:n,fadeScrollbar:n&&p,scrollbarClass:"",zoom:false,zoomMin:1,zoomMax:4,doubleTapZoom:2,wheelAction:"scroll",snap:false,snapThreshold:1,onRefresh:null,onBeforeScrollStart:function(a){a.preventDefault()},onScrollStart:null,onBeforeScrollMove:null,onScrollMove:null,onBeforeScrollEnd:null,onScrollEnd:null,onTouchEnd:null,onDestroy:null,onZoomStart:null,onZoom:null,onZoomEnd:null};for(l in d)e.options[l]=d[l];e.x=e.options.x;e.y=e.options.y;e.options.useTransform=r&&e.options.useTransform;e.options.hScrollbar=e.options.hScroll&&e.options.hScrollbar;e.options.vScrollbar=e.options.vScroll&&e.options.vScrollbar;e.options.zoom=e.options.useTransform&&e.options.zoom;e.options.useTransition=s&&e.options.useTransition;if(e.options.zoom&&m){C=""}e.scroller.style[h]=e.options.useTransform?f+"transform":"top left";e.scroller.style[i]="0";e.scroller.style[j]="0 0";if(e.options.useTransition)e.scroller.style[k]="cubic-bezier(0.33,0.66,0.66,1)";if(e.options.useTransform)e.scroller.style[g]="translate("+e.x+"px,"+e.y+"px)"+C;else e.scroller.style.cssText+=";position:absolute;top:"+e.y+"px;left:"+e.x+"px";if(e.options.useTransition)e.options.fixedScrollbar=true;e.refresh();e._bind(t,a);e._bind(u);if(!q){e._bind("mouseout",e.wrapper);if(e.options.wheelAction!="none")e._bind(y)}if(e.options.checkDOMChanges)e.checkDOMTime=setInterval(function(){e._checkDOMChanges()},500)};D.prototype={enabled:true,x:0,y:0,steps:[],scale:1,currPageX:0,currPageY:0,pagesX:[],pagesY:[],aniTime:null,wheelZoomCount:0,handleEvent:function(a){var b=this;switch(a.type){case u:if(!q&&a.button!==0)return;b._start(a);break;case v:b._move(a);break;case w:case x:b._end(a);break;case t:b._resize();break;case y:b._wheel(a);break;case"mouseout":b._mouseout(a);break;case z:b._transitionEnd(a);break}},_checkDOMChanges:function(){if(this.moved||this.zoomed||this.animating||this.scrollerW==this.scroller.offsetWidth*this.scale&&this.scrollerH==this.scroller.offsetHeight*this.scale)return;this.refresh()},_scrollbar:function(a){var d=this,e;if(!d[a+"Scrollbar"]){if(d[a+"ScrollbarWrapper"]){if(r)d[a+"ScrollbarIndicator"].style[g]="";d[a+"ScrollbarWrapper"].parentNode.removeChild(d[a+"ScrollbarWrapper"]);d[a+"ScrollbarWrapper"]=null;d[a+"ScrollbarIndicator"]=null}return}if(!d[a+"ScrollbarWrapper"]){e=b.createElement("div");if(d.options.scrollbarClass)e.className=d.options.scrollbarClass+a.toUpperCase();else e.style.cssText="position:absolute;z-index:100;"+(a=="h"?"height:7px;bottom:1px;left:2px;right:"+(d.vScrollbar?"7":"2")+"px":"width:7px;bottom:"+(d.hScrollbar?"7":"2")+"px;top:2px;right:1px");e.style.cssText+=";pointer-events:none;"+f+"transition-property:opacity;"+f+"transition-duration:"+(d.options.fadeScrollbar?"350ms":"0")+";overflow:hidden;opacity:"+(d.options.hideScrollbar?"0":"1");d.wrapper.appendChild(e);d[a+"ScrollbarWrapper"]=e;e=b.createElement("div");if(!d.options.scrollbarClass){e.style.cssText="position:absolute;z-index:100;background:rgba(0,0,0,0.5);border:1px solid rgba(255,255,255,0.9);"+f+"background-clip:padding-box;"+f+"box-sizing:border-box;"+(a=="h"?"height:100%":"width:100%")+";"+f+"border-radius:3px;border-radius:3px"}e.style.cssText+=";pointer-events:none;"+f+"transition-property:"+f+"transform;"+f+"transition-timing-function:cubic-bezier(0.33,0.66,0.66,1);"+f+"transition-duration:0;"+f+"transform: translate(0,0)"+C;if(d.options.useTransition)e.style.cssText+=";"+f+"transition-timing-function:cubic-bezier(0.33,0.66,0.66,1)";d[a+"ScrollbarWrapper"].appendChild(e);d[a+"ScrollbarIndicator"]=e}if(a=="h"){d.hScrollbarSize=d.hScrollbarWrapper.clientWidth;d.hScrollbarIndicatorSize=c.max(c.round(d.hScrollbarSize*d.hScrollbarSize/d.scrollerW),8);d.hScrollbarIndicator.style.width=d.hScrollbarIndicatorSize+"px";d.hScrollbarMaxScroll=d.hScrollbarSize-d.hScrollbarIndicatorSize;d.hScrollbarProp=d.hScrollbarMaxScroll/d.maxScrollX}else{d.vScrollbarSize=d.vScrollbarWrapper.clientHeight;d.vScrollbarIndicatorSize=c.max(c.round(d.vScrollbarSize*d.vScrollbarSize/d.scrollerH),8);d.vScrollbarIndicator.style.height=d.vScrollbarIndicatorSize+"px";d.vScrollbarMaxScroll=d.vScrollbarSize-d.vScrollbarIndicatorSize;d.vScrollbarProp=d.vScrollbarMaxScroll/d.maxScrollY}d._scrollbarPos(a,true)},_resize:function(){var a=this;setTimeout(function(){a.refresh()},m?200:0)},_pos:function(a,b){if(this.zoomed)return;a=this.hScroll?a:0;b=this.vScroll?b:0;if(this.options.useTransform){this.scroller.style[g]="translate("+a+"px,"+b+"px) scale("+this.scale+")"+C}else{a=c.round(a);b=c.round(b);this.scroller.style.left=a+"px";this.scroller.style.top=b+"px"}this.x=a;this.y=b;this._scrollbarPos("h");this._scrollbarPos("v")},_scrollbarPos:function(a,b){var d=this,e=a=="h"?d.x:d.y,f;if(!d[a+"Scrollbar"])return;e=d[a+"ScrollbarProp"]*e;if(e<0){if(!d.options.fixedScrollbar){f=d[a+"ScrollbarIndicatorSize"]+c.round(e*3);if(f<8)f=8;d[a+"ScrollbarIndicator"].style[a=="h"?"width":"height"]=f+"px"}e=0}else if(e>d[a+"ScrollbarMaxScroll"]){if(!d.options.fixedScrollbar){f=d[a+"ScrollbarIndicatorSize"]-c.round((e-d[a+"ScrollbarMaxScroll"])*3);if(f<8)f=8;d[a+"ScrollbarIndicator"].style[a=="h"?"width":"height"]=f+"px";e=d[a+"ScrollbarMaxScroll"]+(d[a+"ScrollbarIndicatorSize"]-f)}else{e=d[a+"ScrollbarMaxScroll"]}}d[a+"ScrollbarWrapper"].style[l]="0";d[a+"ScrollbarWrapper"].style.opacity=b&&d.options.hideScrollbar?"0":"1";d[a+"ScrollbarIndicator"].style[g]="translate("+(a=="h"?e+"px,0)":"0,"+e+"px)")+C},_start:function(a){var b=this,d=q?a.touches[0]:a,e,f,h,i,j;if(!b.enabled)return;if(b.options.onBeforeScrollStart)b.options.onBeforeScrollStart.call(b,a);if(b.options.useTransition||b.options.zoom)b._transitionTime(0);b.moved=false;b.animating=false;b.zoomed=false;b.distX=0;b.distY=0;b.absDistX=0;b.absDistY=0;b.dirX=0;b.dirY=0;if(b.options.zoom&&q&&a.touches.length>1){i=c.abs(a.touches[0].pageX-a.touches[1].pageX);j=c.abs(a.touches[0].pageY-a.touches[1].pageY);b.touchesDistStart=c.sqrt(i*i+j*j);b.originX=c.abs(a.touches[0].pageX+a.touches[1].pageX-b.wrapperOffsetLeft*2)/2-b.x;b.originY=c.abs(a.touches[0].pageY+a.touches[1].pageY-b.wrapperOffsetTop*2)/2-b.y;if(b.options.onZoomStart)b.options.onZoomStart.call(b,a)}if(b.options.momentum){if(b.options.useTransform){e=getComputedStyle(b.scroller,null)[g].replace(/[^0-9\-.,]/g,"").split(",");f=e[4]*1;h=e[5]*1}else{f=getComputedStyle(b.scroller,null).left.replace(/[^0-9-]/g,"")*1;h=getComputedStyle(b.scroller,null).top.replace(/[^0-9-]/g,"")*1}if(f!=b.x||h!=b.y){if(b.options.useTransition)b._unbind(z);else B(b.aniTime);b.steps=[];b._pos(f,h)}}b.absStartX=b.x;b.absStartY=b.y;b.startX=b.x;b.startY=b.y;b.pointX=d.pageX;b.pointY=d.pageY;b.startTime=a.timeStamp||Date.now();if(b.options.onScrollStart)b.options.onScrollStart.call(b,a);b._bind(v);b._bind(w);b._bind(x)},_move:function(a){var b=this,d=q?a.touches[0]:a,e=d.pageX-b.pointX,f=d.pageY-b.pointY,h=b.x+e,i=b.y+f,j,k,l,m=a.timeStamp||Date.now();if(b.options.onBeforeScrollMove)b.options.onBeforeScrollMove.call(b,a);if(b.options.zoom&&q&&a.touches.length>1){j=c.abs(a.touches[0].pageX-a.touches[1].pageX);k=c.abs(a.touches[0].pageY-a.touches[1].pageY);b.touchesDist=c.sqrt(j*j+k*k);b.zoomed=true;l=1/b.touchesDistStart*b.touchesDist*this.scale;if(l<b.options.zoomMin)l=.5*b.options.zoomMin*Math.pow(2,l/b.options.zoomMin);else if(l>b.options.zoomMax)l=2*b.options.zoomMax*Math.pow(.5,b.options.zoomMax/l);b.lastScale=l/this.scale;h=this.originX-this.originX*b.lastScale+this.x,i=this.originY-this.originY*b.lastScale+this.y;this.scroller.style[g]="translate("+h+"px,"+i+"px) scale("+l+")"+C;if(b.options.onZoom)b.options.onZoom.call(b,a);return}b.pointX=d.pageX;b.pointY=d.pageY;if(h>0||h<b.maxScrollX){h=b.options.bounce?b.x+e/2:h>=0||b.maxScrollX>=0?0:b.maxScrollX}if(i>b.minScrollY||i<b.maxScrollY){i=b.options.bounce?b.y+f/2:i>=b.minScrollY||b.maxScrollY>=0?b.minScrollY:b.maxScrollY}b.distX+=e;b.distY+=f;b.absDistX=c.abs(b.distX);b.absDistY=c.abs(b.distY);if(b.absDistX<6&&b.absDistY<6){return}if(b.options.lockDirection){if(b.absDistX>b.absDistY+5){i=b.y;f=0}else if(b.absDistY>b.absDistX+5){h=b.x;e=0}}b.moved=true;b._pos(h,i);b.dirX=e>0?-1:e<0?1:0;b.dirY=f>0?-1:f<0?1:0;if(m-b.startTime>300){b.startTime=m;b.startX=b.x;b.startY=b.y}if(b.options.onScrollMove)b.options.onScrollMove.call(b,a)},_end:function(a){if(q&&a.touches.length!==0)return;var d=this,e=q?a.changedTouches[0]:a,f,h,j={dist:0,time:0},k={dist:0,time:0},l=(a.timeStamp||Date.now())-d.startTime,m=d.x,n=d.y,o,p,r,s,t;d._unbind(v);d._unbind(w);d._unbind(x);if(d.options.onBeforeScrollEnd)d.options.onBeforeScrollEnd.call(d,a);if(d.zoomed){t=d.scale*d.lastScale;t=Math.max(d.options.zoomMin,t);t=Math.min(d.options.zoomMax,t);d.lastScale=t/d.scale;d.scale=t;d.x=d.originX-d.originX*d.lastScale+d.x;d.y=d.originY-d.originY*d.lastScale+d.y;d.scroller.style[i]="200ms";d.scroller.style[g]="translate("+d.x+"px,"+d.y+"px) scale("+d.scale+")"+C;d.zoomed=false;d.refresh();if(d.options.onZoomEnd)d.options.onZoomEnd.call(d,a);return}if(!d.moved){if(q){if(d.doubleTapTimer&&d.options.zoom){clearTimeout(d.doubleTapTimer);d.doubleTapTimer=null;if(d.options.onZoomStart)d.options.onZoomStart.call(d,a);d.zoom(d.pointX,d.pointY,d.scale==1?d.options.doubleTapZoom:1);if(d.options.onZoomEnd){setTimeout(function(){d.options.onZoomEnd.call(d,a)},200)}}else if(this.options.handleClick){d.doubleTapTimer=setTimeout(function(){d.doubleTapTimer=null;f=e.target;while(f.nodeType!=1)f=f.parentNode;if(f.tagName!="SELECT"&&f.tagName!="INPUT"&&f.tagName!="TEXTAREA"){h=b.createEvent("MouseEvents");h.initMouseEvent("click",true,true,a.view,1,e.screenX,e.screenY,e.clientX,e.clientY,a.ctrlKey,a.altKey,a.shiftKey,a.metaKey,0,null);h._fake=true;f.dispatchEvent(h)}},d.options.zoom?250:0)}}d._resetPos(200);if(d.options.onTouchEnd)d.options.onTouchEnd.call(d,a);return}if(l<300&&d.options.momentum){j=m?d._momentum(m-d.startX,l,-d.x,d.scrollerW-d.wrapperW+d.x,d.options.bounce?d.wrapperW:0):j;k=n?d._momentum(n-d.startY,l,-d.y,d.maxScrollY<0?d.scrollerH-d.wrapperH+d.y-d.minScrollY:0,d.options.bounce?d.wrapperH:0):k;m=d.x+j.dist;n=d.y+k.dist;if(d.x>0&&m>0||d.x<d.maxScrollX&&m<d.maxScrollX)j={dist:0,time:0};if(d.y>d.minScrollY&&n>d.minScrollY||d.y<d.maxScrollY&&n<d.maxScrollY)k={dist:0,time:0}}if(j.dist||k.dist){r=c.max(c.max(j.time,k.time),10);if(d.options.snap){o=m-d.absStartX;p=n-d.absStartY;if(c.abs(o)<d.options.snapThreshold&&c.abs(p)<d.options.snapThreshold){d.scrollTo(d.absStartX,d.absStartY,200)}else{s=d._snap(m,n);m=s.x;n=s.y;r=c.max(s.time,r)}}d.scrollTo(c.round(m),c.round(n),r);if(d.options.onTouchEnd)d.options.onTouchEnd.call(d,a);return}if(d.options.snap){o=m-d.absStartX;p=n-d.absStartY;if(c.abs(o)<d.options.snapThreshold&&c.abs(p)<d.options.snapThreshold)d.scrollTo(d.absStartX,d.absStartY,200);else{s=d._snap(d.x,d.y);if(s.x!=d.x||s.y!=d.y)d.scrollTo(s.x,s.y,s.time)}if(d.options.onTouchEnd)d.options.onTouchEnd.call(d,a);return}d._resetPos(200);if(d.options.onTouchEnd)d.options.onTouchEnd.call(d,a)},_resetPos:function(a){var b=this,c=b.x>=0?0:b.x<b.maxScrollX?b.maxScrollX:b.x,d=b.y>=b.minScrollY||b.maxScrollY>0?b.minScrollY:b.y<b.maxScrollY?b.maxScrollY:b.y;if(c==b.x&&d==b.y){if(b.moved){b.moved=false;if(b.options.onScrollEnd)b.options.onScrollEnd.call(b)}if(b.hScrollbar&&b.options.hideScrollbar){if(e=="webkit")b.hScrollbarWrapper.style[l]="300ms";b.hScrollbarWrapper.style.opacity="0"}if(b.vScrollbar&&b.options.hideScrollbar){if(e=="webkit")b.vScrollbarWrapper.style[l]="300ms";b.vScrollbarWrapper.style.opacity="0"}return}b.scrollTo(c,d,a||0)},_wheel:function(a){var b=this,c,d,e,f,g;if("wheelDeltaX"in a){c=a.wheelDeltaX/12;d=a.wheelDeltaY/12}else if("wheelDelta"in a){c=d=a.wheelDelta/12}else if("detail"in a){c=d=-a.detail*3}else{return}if(b.options.wheelAction=="zoom"){g=b.scale*Math.pow(2,1/3*(d?d/Math.abs(d):0));if(g<b.options.zoomMin)g=b.options.zoomMin;if(g>b.options.zoomMax)g=b.options.zoomMax;if(g!=b.scale){if(!b.wheelZoomCount&&b.options.onZoomStart)b.options.onZoomStart.call(b,a);b.wheelZoomCount++;b.zoom(a.pageX,a.pageY,g,400);setTimeout(function(){b.wheelZoomCount--;if(!b.wheelZoomCount&&b.options.onZoomEnd)b.options.onZoomEnd.call(b,a)},400)}return}e=b.x+c;f=b.y+d;if(e>0)e=0;else if(e<b.maxScrollX)e=b.maxScrollX;if(f>b.minScrollY)f=b.minScrollY;else if(f<b.maxScrollY)f=b.maxScrollY;if(b.maxScrollY<0){b.scrollTo(e,f,0)}},_mouseout:function(a){var b=a.relatedTarget;if(!b){this._end(a);return}while(b=b.parentNode)if(b==this.wrapper)return;this._end(a)},_transitionEnd:function(a){var b=this;if(a.target!=b.scroller)return;b._unbind(z);b._startAni()},_startAni:function(){var a=this,b=a.x,d=a.y,e=Date.now(),f,g,h;if(a.animating)return;if(!a.steps.length){a._resetPos(400);return}f=a.steps.shift();if(f.x==b&&f.y==d)f.time=0;a.animating=true;a.moved=true;if(a.options.useTransition){a._transitionTime(f.time);a._pos(f.x,f.y);a.animating=false;if(f.time)a._bind(z);else a._resetPos(0);return}h=function(){var i=Date.now(),j,k;if(i>=e+f.time){a._pos(f.x,f.y);a.animating=false;if(a.options.onAnimationEnd)a.options.onAnimationEnd.call(a);a._startAni();return}i=(i-e)/f.time-1;g=c.sqrt(1-i*i);j=(f.x-b)*g+b;k=(f.y-d)*g+d;a._pos(j,k);if(a.animating)a.aniTime=A(h)};h()},_transitionTime:function(a){a+="ms";this.scroller.style[i]=a;if(this.hScrollbar)this.hScrollbarIndicator.style[i]=a;if(this.vScrollbar)this.vScrollbarIndicator.style[i]=a},_momentum:function(a,b,d,e,f){var g=6e-4,h=c.abs(a)/b,i=h*h/(2*g),j=0,k=0;if(a>0&&i>d){k=f/(6/(i/h*g));d=d+k;h=h*d/i;i=d}else if(a<0&&i>e){k=f/(6/(i/h*g));e=e+k;h=h*e/i;i=e}i=i*(a<0?-1:1);j=h/g;return{dist:i,time:c.round(j)}},_offset:function(a){var b=-a.offsetLeft,c=-a.offsetTop;while(a=a.offsetParent){b-=a.offsetLeft;c-=a.offsetTop}if(a!=this.wrapper){b*=this.scale;c*=this.scale}return{left:b,top:c}},_snap:function(a,b){var d=this,e,f,g,h,i,j;g=d.pagesX.length-1;for(e=0,f=d.pagesX.length;e<f;e++){if(a>=d.pagesX[e]){g=e;break}}if(g==d.currPageX&&g>0&&d.dirX<0)g--;a=d.pagesX[g];i=c.abs(a-d.pagesX[d.currPageX]);i=i?c.abs(d.x-a)/i*500:0;d.currPageX=g;g=d.pagesY.length-1;for(e=0;e<g;e++){if(b>=d.pagesY[e]){g=e;break}}if(g==d.currPageY&&g>0&&d.dirY<0)g--;b=d.pagesY[g];j=c.abs(b-d.pagesY[d.currPageY]);j=j?c.abs(d.y-b)/j*500:0;d.currPageY=g;h=c.round(c.max(i,j))||200;return{x:a,y:b,time:h}},_bind:function(a,b,c){(b||this.scroller).addEventListener(a,this,!!c)},_unbind:function(a,b,c){(b||this.scroller).removeEventListener(a,this,!!c)},destroy:function(){var b=this;b.scroller.style[g]="";b.hScrollbar=false;b.vScrollbar=false;b._scrollbar("h");b._scrollbar("v");b._unbind(t,a);b._unbind(u);b._unbind(v);b._unbind(w);b._unbind(x);if(!b.options.hasTouch){b._unbind("mouseout",b.wrapper);b._unbind(y)}if(b.options.useTransition)b._unbind(z);if(b.options.checkDOMChanges)clearInterval(b.checkDOMTime);if(b.options.onDestroy)b.options.onDestroy.call(b)},refresh:function(){var a=this,b,d,e,f,g=0,h=0;if(a.scale<a.options.zoomMin)a.scale=a.options.zoomMin;a.wrapperW=a.wrapper.clientWidth||1;a.wrapperH=a.wrapper.clientHeight||1;a.minScrollY=-a.options.topOffset||0;a.scrollerW=c.round(a.scroller.offsetWidth*a.scale);a.scrollerH=c.round((a.scroller.offsetHeight+a.minScrollY)*a.scale);a.maxScrollX=a.wrapperW-a.scrollerW;a.maxScrollY=a.wrapperH-a.scrollerH+a.minScrollY;a.dirX=0;a.dirY=0;if(a.options.onRefresh)a.options.onRefresh.call(a);a.hScroll=a.options.hScroll&&a.maxScrollX<0;a.vScroll=a.options.vScroll&&(!a.options.bounceLock&&!a.hScroll||a.scrollerH>a.wrapperH);a.hScrollbar=a.hScroll&&a.options.hScrollbar;a.vScrollbar=a.vScroll&&a.options.vScrollbar&&a.scrollerH>a.wrapperH;b=a._offset(a.wrapper);a.wrapperOffsetLeft=-b.left;a.wrapperOffsetTop=-b.top;if(typeof a.options.snap=="string"){a.pagesX=[];a.pagesY=[];f=a.scroller.querySelectorAll(a.options.snap);for(d=0,e=f.length;d<e;d++){g=a._offset(f[d]);g.left+=a.wrapperOffsetLeft;g.top+=a.wrapperOffsetTop;a.pagesX[d]=g.left<a.maxScrollX?a.maxScrollX:g.left*a.scale;a.pagesY[d]=g.top<a.maxScrollY?a.maxScrollY:g.top*a.scale}}else if(a.options.snap){a.pagesX=[];while(g>=a.maxScrollX){a.pagesX[h]=g;g=g-a.wrapperW;h++}if(a.maxScrollX%a.wrapperW)a.pagesX[a.pagesX.length]=a.maxScrollX-a.pagesX[a.pagesX.length-1]+a.pagesX[a.pagesX.length-1];g=0;h=0;a.pagesY=[];while(g>=a.maxScrollY){a.pagesY[h]=g;g=g-a.wrapperH;h++}if(a.maxScrollY%a.wrapperH)a.pagesY[a.pagesY.length]=a.maxScrollY-a.pagesY[a.pagesY.length-1]+a.pagesY[a.pagesY.length-1]}a._scrollbar("h");a._scrollbar("v");if(!a.zoomed){a.scroller.style[i]="0";a._resetPos(200)}},scrollTo:function(a,b,c,d){var e=this,f=a,g,h;e.stop();if(!f.length)f=[{x:a,y:b,time:c,relative:d}];for(g=0,h=f.length;g<h;g++){if(f[g].relative){f[g].x=e.x-f[g].x;f[g].y=e.y-f[g].y}e.steps.push({x:f[g].x,y:f[g].y,time:f[g].time||0})}e._startAni()},scrollToElement:function(a,b){var d=this,e;a=a.nodeType?a:d.scroller.querySelector(a);if(!a)return;e=d._offset(a);e.left+=d.wrapperOffsetLeft;e.top+=d.wrapperOffsetTop;e.left=e.left>0?0:e.left<d.maxScrollX?d.maxScrollX:e.left;e.top=e.top>d.minScrollY?d.minScrollY:e.top<d.maxScrollY?d.maxScrollY:e.top;b=b===undefined?c.max(c.abs(e.left)*2,c.abs(e.top)*2):b;d.scrollTo(e.left,e.top,b)},scrollToPage:function(a,b,c){var d=this,e,f;c=c===undefined?400:c;if(d.options.onScrollStart)d.options.onScrollStart.call(d);if(d.options.snap){a=a=="next"?d.currPageX+1:a=="prev"?d.currPageX-1:a;b=b=="next"?d.currPageY+1:b=="prev"?d.currPageY-1:b;a=a<0?0:a>d.pagesX.length-1?d.pagesX.length-1:a;b=b<0?0:b>d.pagesY.length-1?d.pagesY.length-1:b;d.currPageX=a;d.currPageY=b;e=d.pagesX[a];f=d.pagesY[b]}else{e=-d.wrapperW*a;f=-d.wrapperH*b;if(e<d.maxScrollX)e=d.maxScrollX;if(f<d.maxScrollY)f=d.maxScrollY}d.scrollTo(e,f,c)},disable:function(){this.stop();this._resetPos(0);this.enabled=false;this._unbind(v);this._unbind(w);this._unbind(x)},enable:function(){this.enabled=true},stop:function(){if(this.options.useTransition)this._unbind(z);else B(this.aniTime);this.steps=[];this.moved=false;this.animating=false},zoom:function(a,b,c,d){var e=this,f=c/e.scale;if(!e.options.useTransform)return;e.zoomed=true;d=d===undefined?200:d;a=a-e.wrapperOffsetLeft-e.x;b=b-e.wrapperOffsetTop-e.y;e.x=a-a*f+e.x;e.y=b-b*f+e.y;e.scale=c;e.refresh();e.x=e.x>0?0:e.x<e.maxScrollX?e.maxScrollX:e.x;e.y=e.y>e.minScrollY?e.minScrollY:e.y<e.maxScrollY?e.maxScrollY:e.y;e.scroller.style[i]=d+"ms";e.scroller.style[g]="translate("+e.x+"px,"+e.y+"px) scale("+c+")"+C;e.zoomed=false},isReady:function(){return!this.moved&&!this.zoomed&&!this.animating}};d=null;if(typeof exports!=="undefined")exports.iScroll=D;else a.iScroll=D})(window,document)







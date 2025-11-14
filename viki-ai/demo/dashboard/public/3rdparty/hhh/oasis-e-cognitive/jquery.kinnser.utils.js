/**
 * Appended for backward compatibility.
 */

(function($) {
	$.fn.customFadeIn = function(speed, callback) {
		$(this).fadeIn(speed, function() {
			if(jQuery.browser.msie)
				$(this).get(0).style.removeAttribute('filter');
			if(callback != undefined)
				callback();
		});
	};
	$.fn.customFadeOut = function(speed, callback) {
		$(this).fadeOut(speed, function() {
			if(jQuery.browser.msie)
				$(this).get(0).style.removeAttribute('filter');
			if(callback != undefined)
				callback();
		});
	};
})(jQuery);

(function($) {
	$.fn.customSlideDown = function(speed, callback) {
		$(this).slideDown(speed, function() {
			if(jQuery.browser.msie)
				$(this).get(0).style.removeAttribute('filter');
			if(callback != undefined)
				callback();
		});
	};
	$.fn.customSlideUp = function(speed, callback) {
		$(this).slideUp(speed, function() {
			if(jQuery.browser.msie)
				$(this).get(0).style.removeAttribute('filter');
			if(callback != undefined)
				callback();
		});
	};
	$.fn.customSlideToggle = function(speed, callback) {
		$(this).slideToggle(speed, function() {
			if(jQuery.browser.msie)
				$(this).get(0).style.removeAttribute('filter');
			if(callback != undefined)
				callback();
		});
	};
})(jQuery);

(function($) {
	$.fn.customToggle = function(speed, callback) {
		$(this).toggle(speed, function() {
			if(jQuery.browser.msie)
				$(this).get(0).style.removeAttribute('filter');
			if(callback != undefined)
				callback();
		});
	};

})(jQuery);

jQuery.fn.fadeTo = function(speed,to,callback) {
	return this.animate({opacity: to}, speed, function() {
	if (to == 1 && jQuery.browser.msie)
		this.style.removeAttribute('filter');
	if (jQuery.isFunction(callback))
	callback();
	});
};

(function($) {
	$.fn.focusNextInputField = function() {
		return this.each(function() {
			var fields = $(this).parents('form:eq(0),body').find('button,input,textarea,select').filter(':visible').filter(':enabled');
			var index = fields.index( this );
			// added the logic for not focusable elements, if the next element is 
			// not focusable, leaves the focus on the calendar field -- problem ie8
			if ( index > -1 && ( index + 1 ) < fields.length ) {
				try { 
					fields.eq( index + 1 ).focus();
				} catch (e) {	
					fields.eq( index ).focus();
				}
			}
			return false;
		});
	};
})(jQuery);

(function($) {
	$.fn.valueOfLinkedField = function() {
		return this.each(function() {
			var LinkedId = $(this).attr('linkedField');
			if (typeof LinkedId !== 'undefined' && LinkedId !== false) {
				if ($('#' + LinkedId).val() == '') {
					$('#' + LinkedId).focus();
					$('#' + LinkedId).val( $(this).val() )
				}
			}	
			return false;
		});
	};
})(jQuery);

// Extracted from https://github.com/miketaylr/jQuery-html5-placeholder and customized for our needs.
//
// HTML5 placeholder plugin version 1.01
// Copyright (c) 2010-The End of Time, Mike Taylor, http://miketaylr.com
// MIT Licensed: http://www.opensource.org/licenses/mit-license.php
//
// Enables cross-browser HTML5 placeholder for inputs, by first testing
// for a native implementation before building one.
//
//
// USAGE:
//$('input[placeholder]').placeholder({inputmask:'xxxx'});
(function ($) {
	//feature detection
	var hasPlaceholder = 'placeholder' in document.createElement('input');

	//sniffy sniff sniff -- just to give extra left padding for the older
	//graphics for type=email and type=url
	var isOldOpera = $.browser.opera && $.browser.version < 10.5;

	$.fn.placeholder = function (options) {
		//merge in passed in options, if any
		var options = $.extend({}, $.fn.placeholder.defaults, options);

		//first test for native placeholder support before continuing
		//feature detection inspired by ye olde jquery 1.4 hawtness, with paul irish
		return (hasPlaceholder) ? this : this.each(function () {
			//TODO: if this element already has a placeholder, exit

			//local vars
			var $this = $(this),
				inputVal = $.trim($this.val());

			// Refresh placeholder status
			placeholderRefresh = function () {
				var show = !$.trim($this.val()) ;			// when the field is empty
				
				$this.toggleClass(options.classname, show);
			}
			// Add placeholder data to the input element
			$this.data('placeholder', { refresh: placeholderRefresh });
			
			//set placeholder initial state
			placeholderRefresh();

			//hide placeholder on focus
			$this.focus(function () {
				if (!$.trim($this.val()) || $this.val() == options.inputmask) {
					$this.toggleClass(options.classname, false);
				}
			});

			//show placeholder if the input is empty
			$this.blur( placeholderRefresh );
		});
	};

	//expose defaults
	$.fn.placeholder.defaults = {
		classname: 'placeholder',
		inputmask: ''
	};
	
	if(!hasPlaceholder){
		$.valHooks['input'] = {
			set: function(el, val){
				el.value = val;
				if (typeof $(el).data('placeholder') == 'object') {
					$(el).data('placeholder').refresh.call(el);
				}
			}
		};
	}
})(jQuery);
/***************** END - HTML5 placeholder plugin version 1.01 *******************/
/*********************************************************************************/

(function($) {
    $.fn.focusToEnd = function() {
        return this.each(function() {
            var v = $(this).val();
            $(this).focus().val("").val(v);
        });
    };
})(jQuery);

(function($) {
    $.fn.serializeObject = function()
    {
        var o = {};
        var a = this.serializeArray();
        $.each(a, function() {
            if (o[this.name] !== undefined) {
                if (!o[this.name].push) {
                    o[this.name] = [o[this.name]];
                }
                o[this.name].push(this.value || '');
            } else {
                o[this.name] = this.value || '';
            }
        });
        return o;
    };
})(jQuery);

/**
 * not part of jQuery but great helper function;
 * takes a form object and returns paramaters needed for form or url post
 */
function getForm(fobj) {    var str = "";   var ft = "";   var fv = "";  var fn = "";  var els = "";  for(var i = 0;i < fobj.elements.length;i++) {   els = fobj.elements[i];   ft = els.title;   fv = els.value;   fn = els.name; switch(els.type) {   case "text":   case "hidden":   case "password":   case "textarea":   if(encodeURI(ft) == "required" && encodeURI(fv).length < 1) {     alert('\''+fn+'\' is a required field, please complete.');     els.focus();     return false;   } str += fn + "=" + encodeURI(fv) + "&";  break;  case "checkbox":   case "radio":    if(els.checked) str += fn + "=" + encodeURI(fv) + "&";  break; case "select-one":  str += fn + "=" +    els.options[els.selectedIndex].value + "&";break;}}  str = str.substr(0,(str.length - 1));    return str;  }

function getFormAsStruct(fobj) {    var struct = new Object();   var ft = "";   var fv = "";  var fn = "";  var els = ""; for(var i = 0;i < fobj.elements.length;i++){	els = fobj.elements[i];   ft = els.title;   fv = els.value;   fn = els.name; switch(els.type)	{ 		case "text":   case "hidden":   case "password":   case "textarea":		if(encodeURI(ft) == "required" && encodeURI(fv).length < 1)	{   alert('\''+fn+'\' is a required field, please complete.');	els.focus(); return false;		}  		struct[fn] = fv;		break; 		case "checkbox":   	case "radio":  	if(els.checked)		struct[fn] = fv;	break; 	case "select-one":  struct[fn] = els.options[els.selectedIndex]?els.options[els.selectedIndex].value:''; 	 break; 	} }   return struct; }

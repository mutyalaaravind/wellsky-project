(function() {
	'use strict';

	angular.module('directives.kinnser.infinate-scroll', []).directive('infinateScroll', function() {
	    return function(scope, elm, attr) {
	        var raw = elm[0];
	        elm.bind('scroll', function() {
	        	
	            if (raw.scrollTop + raw.offsetHeight >= raw.scrollHeight) {
	                scope.$apply(attr.infinateScroll);
	            }
	        });
	    };
	});
})();
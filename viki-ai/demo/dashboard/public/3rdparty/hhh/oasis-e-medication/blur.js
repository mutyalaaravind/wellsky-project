(function() {
	'use strict';

	var blur = angular.module('directives.kinnser.blur', []);

	blur.directive('kBlur', ['$parse', function($parse) {
	  return function(scope, element, attr) {
	    var fn = $parse(attr['kBlur']);
	    element.bind('blur', function(event) {
	      scope.$apply(function() {
	        fn(scope, {$event:event});
	      });
	    });
	  }
	}]);
})();
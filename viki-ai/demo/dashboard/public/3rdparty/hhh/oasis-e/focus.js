(function() {
	'use strict';

	var focus = angular.module('directives.kinnser.focus', []);

	focus.directive('kFocus', ['$parse', function($parse) {
	  return function(scope, element, attr) {
	    var fn = $parse(attr['kFocus']);
	    element.bind('focus', function(event) {
	      scope.$apply(function() {
	        fn(scope, {$event:event});
	      });
	    });
	  }
	}]);
})();
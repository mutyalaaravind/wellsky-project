(function(){
	'use strict';
	
    var UXservice = angular.module('services.ux.ux-service', []);
	
    UXservice.factory('UXService', [function(){
		var UXService = {},
			config = {
				appBaseUrl: '',
				shortDateFormat: 'mm/dd/yyyy',
				dateInputMask: '__/__/____',
				skinBaseUrl: '/AM/css/ux/'
			};
		
		UXService.getShortDateFormat = function(){ return config.shortDateFormat; };
		UXService.getShortDateFormatJUI = function(){ return config.shortDateFormat.replace('yyyy','yy');};
		UXService.getShortDateFormatNG = function(){ return config.shortDateFormat.replace('mm','MM');};
		UXService.getSkinBaseUrl = function(){ return config.skinBaseUrl;};
		UXService.getDateInputMask = function(){ return config.dateInputMask;};
		
		UXService.ieVersion = function(){
			var undef,
				v = 3,
				div = document.createElement('div'),
				all = div.getElementsByTagName('i');
			
			while(
				div.innerHTML = '<!--[if gt IE ' + (++v) + ']><i></i><![endif]-->',
				all[0]
			);
			
			return v > 4 || Function('/*@cc_on return document.documentMode===10@*/')() ? v : undef;
		};

		UXService.isTimeForFeature = function(dateToCheck, productionFeatureDate, testFeatureDate){
			if(!testFeatureDate){
				testFeatureDate = productionFeatureDate;
			}
			return Date.parse(dateToCheck) >= (Date.now() < Date.parse(productionFeatureDate) ? Date.parse(testFeatureDate) : Date.parse(productionFeatureDate)); 
		}
		
		return UXService;
    }]);
})();
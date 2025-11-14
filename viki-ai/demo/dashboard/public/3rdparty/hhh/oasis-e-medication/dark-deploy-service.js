(function(){

	'use strict';

	var DarkDeployService = angular.module('services.dark-deploy.dark-deploy-service', []);

	DarkDeployService.factory('DarkDeployService', ['SERVICES_CONFIG', '$http', '$q', function (SERVICES_CONFIG, $http, $q) {

		var DarkDeployService = {};
		var servicePath = SERVICES_CONFIG.baseURL + 'DarkDeploy/DarkDeployService.cfc';
		var evvServicePath = SERVICES_CONFIG.baseURL + 'DarkDeploy/EvvDarkDeployService.cfc';

		DarkDeployService.callAPI = function(type, url){
			var enabled = false;
			$.ajax({
				type: type,
				url: url,
				async: false
			}).done(function(result){
				if (result == "true"){
					enabled = true;
				}
			});
			return enabled;
		};

		DarkDeployService.callAPIAsync = function(method, url) {
			var defer = $q.defer();

			$http({url: url, method: method}).then(
				function(response) {
					if (response && response.data == 'true') {
						defer.resolve();
					} else {
						defer.reject('');
					}
				},
				function() {
					defer.reject('');
				}
			);

			return defer.promise;
		};

		DarkDeployService.isCorporationFeatureEnabled = function(settingName, corporationKey){
			var queryString = "&settingName=" + settingName;
			queryString += "&corporationKey=" + corporationKey;
			return DarkDeployService.callAPI('GET', servicePath + '?method=isCorporationFeatureEnabled' + queryString);
		};

		DarkDeployService.isClinicFeatureEnabled = function(settingName, clinicKey, async) {
			var queryString = "&settingName=" + settingName;
			queryString += "&clinicKey=" + clinicKey;
			var method = '?method=isClinicFeatureEnabled';

			if (async) {
				return DarkDeployService.callAPIAsync('GET', servicePath + method + queryString);
			} else {
				return DarkDeployService.callAPI('GET', servicePath + method + queryString);
			}
		};

		DarkDeployService.isApplicationFeatureEnabled = function(settingName, async) {
			var queryString = "&settingName=" + settingName;
			var method = '?method=isApplicationLevelFeatureEnabled';

			if (async) {
				return DarkDeployService.callAPIAsync('GET', servicePath + method + queryString);
			} else {
				return DarkDeployService.callAPI('GET', servicePath + method + queryString);
			}
		};

		DarkDeployService.isServerLevelFeatureEnabled = function(settingName, async) {
			var queryString = "&settingName=" + settingName;
			var method = '?method=isServerLevelFeatureEnabled';

			if (async) {
				return DarkDeployService.callAPIAsync('GET', servicePath + method + queryString);
			} else {
				return DarkDeployService.callAPI('GET', servicePath + method + queryString);
			}
		};

		DarkDeployService.isSpecialFeatureEnabled = function(settingName, params){
			var queryString = "&settingName=" + settingName;
			var paramString = encodeURIComponent(JSON.stringify(params));
			queryString += "&params=" + paramString;
			return DarkDeployService.callAPI('GET', servicePath + '?method=isSpecialFeatureEnabled' + queryString);
		};

		DarkDeployService.isEvvEnabled = function(clinicKey){
			var queryString = "&clinicKey=" + clinicKey;			
			var method = '?method=isEvvEnabled';

			return DarkDeployService.callAPI('GET', evvServicePath + method + queryString);
		};

		DarkDeployService.isKvvEnabled = function(clinicKey){
			var queryString = "&clinicKey=" + clinicKey;			
			var method = '?method=isKvvEnabled';

			return DarkDeployService.callAPI('GET', evvServicePath + method + queryString);
		};

		return DarkDeployService;
	}]);
})();

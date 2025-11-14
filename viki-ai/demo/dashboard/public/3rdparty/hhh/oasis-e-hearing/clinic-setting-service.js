(function() {
	'use strict';

	var clinicSettingServiceModule = angular.module('services.clinic.clinic-setting-service', []);


	clinicSettingServiceModule.factory('ClinicSettingService', [
		function () {
			var clinicSettings = {};

			return {
				/*
					Returns the clinic setting object for a given setting.
					@settingObject: a setting object (see ClinicSettingService.settings)
				*/
				getClinicSetting: function(settingObject) {
					return clinicSettings[settingObject.StaticVariable];
				},

				/*
					Walks through each setting object to return a set of restricted/un-restricted (depending on the argument) setting objects
					@isRestricted: boolean to determine whether or not we're looking for restricted settings
				*/
				getSettingsByRestriction: function(isRestricted) {
					var restrictedSettings = {};

					angular.forEach(this.settings, function(settingObject, setting) {
						//build the object to return given the argument
						if( !!settingObject.Restricted === isRestricted ){
							restrictedSettings[setting] = settingObject;
						}
					});

					return restrictedSettings;
				},

				/*
					Returns a boolean determining if the clinic has the given setting.
					@settingObject: a setting object (see ClinicSettingService.settings)
				*/
				hasClinicSetting: function(settingObject) {
					return angular.isDefined(clinicSettings[settingObject.StaticVariable]);
				},

				/*
					Returns the clinic setting value, if missing returns undefined
					@settingObject: a setting object (see ClinicSettingService.settings)
				*/
				getValue: function(settingObject) {
					return this.hasClinicSetting( settingObject ) ? clinicSettings[settingObject.StaticVariable] : undefined;
				},

				/*
					Initializer function for this service.
					@allSettings: an object that contains all settings that a clinic can have
					@currentSettings: an object that contains the specific settings for a clinic
				*/
				init: function(allSettings, currentSettings) {
					//all available settings
					angular.extend(this.settings, allSettings);

					//clinic specific settings
					angular.extend(clinicSettings, currentSettings);
				},

				//a publicly exposed list of settings (object)
				settings: {}
			};
		}
	]);
})();
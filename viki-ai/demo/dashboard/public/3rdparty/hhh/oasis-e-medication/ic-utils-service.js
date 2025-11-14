(function() {
    'use strict';

    angular
        .module('services.ic.utils', ['services.dark-deploy.dark-deploy-service'])
        .service('InfectionControlUtilsService', ['DarkDeployService', '$q', service ]);

    function service(DarkDeployService, $q) {

        var service = angular.extend(this, {
            isShutdown: isShutdown,
            fixCaseManagerUserKey: fixCaseManagerUserKey,
            fixClinicUserKey : fixClinicUserKey,
            isCurrentClinicUser: isCurrentClinicUser,
            initializeDD : initializeDD,
        });

        var privates = {
            isShutdownSettingEnabled: false,
            isUserKeyFixSettingEnabled: false
        };

        function fixCaseManagerUserKey(caseManagerObj) {
            if(!privates.isUserKeyFixSettingEnabled){
                return caseManagerObj.AMUSERKEY;
            } else {
                return caseManagerObj.USERSKEY;
            }
        }

        function fixClinicUserKey(clinicUser) {
            if(!privates.isUserKeyFixSettingEnabled){
                return clinicUser.clinicUserKey;
            } else {
                return clinicUser.usersKey;
            }
        }

        function isCurrentClinicUser(clinicUser, currentUser) {
            if(!privates.isUserKeyFixSettingEnabled) {
                return (clinicUser.clinicUserKey === currentUser.amUserKey)
            } else {
                return (clinicUser.usersKey === currentUser.userKey)
            }
        }

        function isShutdown(){
            return privates.isShutdownSettingEnabled;
        }

        //initialization
        function initializeDD() {
            var defer = $q.defer();
            
            DarkDeployService.isApplicationFeatureEnabled('DARK_DEPLOY_HH16711_IC_USERKEY_FIX',true)
            .then(
                function() {
                    privates.isUserKeyFixSettingEnabled = true;
                },
                function() {
                    privates.isUserKeyFixSettingEnabled = false;
                }
            )
            .then(function() {
                DarkDeployService.isApplicationFeatureEnabled('DARK_DEPLOY_HH16711_IC_SHUTDOWN',true)
                .then(
                    function() {
                        privates.isShutdownSettingEnabled = true;
                    },
                    function() {
                        privates.isShutdownSettingEnabled = false;
                    }
                )
            })
            .then(function(){
                defer.resolve();
            });

            return defer.promise;
        }
        
        return service;
    }
}) ();

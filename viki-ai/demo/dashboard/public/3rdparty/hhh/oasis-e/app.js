var AMNG = angular.module('AMNG', [
    '$strap.directives',
    'ngCookies',
    'resources.RESTResource',
    'resources.cost-center',
    'resources.episodeFrequency',
    'resources.icd',
    'resources.list-frequency',
    'resources.list-interval',
    'directives.kinnser.blur',
    'directives.kinnser.focus',
    'directives.kinnser.icd-lookup',
    'directives.kinnser.infinate-scroll',
    'directives.kinnser.oss-grid',
    'directives.kinnser.oss-modal',
    'directives.kinnser.am-print-view.page-builder',
    'directives.kinnser.ux.date-picker',
    'services.clinic.clinic-setting-service',
    'services.pdgm.pdgm-validation',
    'services.user.user',
    'services.util.form-util',
    'services.util.util',
    'resources.hh-order-resource',
    'amng.conditions-of-participation',
    'amng.cop-poc-printview',
    'am-pho-printview',
    'am-scic-order-printview',
    'amng.goals-and-interventions',
    'amng.goals-and-interventions-v2',
    'amng.infectionLog',
    'amng.falltracker',
    'resources.fallTracker-patient',
    'amng.interventions-poc',
    'amng.patient-summary-printview',
    'MAR'    
]);

AMNG.constant('REST_CONFIG', {
        baseURL: '/rest/V1/'
    })
    .constant('SERVICES_CONFIG', {
        baseURL: '/API/services/'
    });
AMNG.constant('LOG_OUT', function() {
    window.name = '';
    window.location = '/login.cfm?logout=1';
});

AMNG.config(['$httpProvider', function($httpProvider) {
    /* transform all post requests to form posts */
    $httpProvider.defaults.headers.post['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8';

    //Transform all post paramaters to jQuery params
    $httpProvider.defaults.transformRequest = [function(data) {
        return angular.isObject(data) && String(data) !== '[object File]' ? jQuery.param(data) : data;
    }];

    //before transforming json into object, remove <*> prefix where present
    $httpProvider.defaults.transformResponse.unshift(function(data) {
        if (typeof(data) === 'string') {
            data = data.replace(/<\*>/ig, '');
        }
        return data;
    });

    /*http interceptor, will intercept every http request.  Strips json prefix and fires events based on status.*/
    $httpProvider.responseInterceptors.push(['$rootScope', '$q', '$parse', function(scope, $q, $parse) {

        function success(response) {
            //strip json prefix
            if (typeof(response.data) === 'string' && response.data.substring(0, 2) === '//') {
                response.data = response.data.replace(/":"<\*>/ig, '":"');
                //if ($.browser.msie && $.browser.version < 9){
                try {
                    response.data = jQuery.parseJSON(response.data.substring(2, response.data.length));
                } catch (e) {
                    response.data = $parse(response.data.substring(2, response.data.length))();
                }

                return response;
            } else {
                return response;
            }
        }

        function error(response) {

            var status = response.status;
            if (status === 401 || status === 404) {
                scope.$broadcast('event:401-404');
            }

            if (status === 500) {
                try {
                    //Log API Error
                    scope.$broadcast('event:LogAPIError', response);
                    //Throw a message to the screen and refresh rest services if the 500 error is of a certain type
                    if (response.data.indexOf('object is not an instance of declaring class') > 0 || response.data.indexOf('java.lang.ClassCastException') > 0) {
                        scope.$broadcast('event:500-refreshrest');
                    } else {
                        scope.$broadcast('event:500');
                    }
                    //clear loader requests so that the 'loading' graphic doesn't hang
                    scope.$emit('event:clearLoaderRequests');
                } catch (e) {}
            }

            // otherwise
            return $q.reject(response);
        }
        return function(promise) {
            return promise.then(success, error);
        };

    }]);

}]);

AMNG.run(['$http', '$rootScope', '$cookies', '$location', 'UserService', 'ClinicSettingService', 'LOG_OUT', 'REST_CONFIG','PdgmValidationService',
    function($http, $rootScope, $cookies, $location, UserService, ClinicSettingService, LOG_OUT, REST_CONFIG, PdgmValidationService) {

        //default ajax requests
        $.ajaxSetup({
            headers: { "token": $cookies.EHRTOKEN },
            cache: false,
            dataFilter: function(data, type) {
                // remove "//"
                if (type == 'json') {
                    data = data.substring(2, data.length); //remove "//"
                    // remove '<*>' prefix from every field value (serializeJSON fix for CF)
                    data = data.replace(/":"(<\*>)+/ig, '":"');
                }
                return data;
            }
        });

        //default angular http requests
        $http.defaults.headers.common.token = $cookies.EHRTOKEN;
        $http.defaults.transformRequest.push(function(data) {
            $rootScope.$broadcast('event:START_REQUEST');
            return data;
        });

        $http.defaults.transformResponse.push(function(data) {
            $rootScope.$broadcast('event:END_REQUEST');
            return data;
        });


        // populate user service
        $.ajax({
            type: 'GET',
            url: '' + REST_CONFIG.baseURL + 'User/me',
            dataType: 'json',
            async: false
        }).done(function(data) {
            if ($.isEmptyObject(data)) {
                LOG_OUT(); //logout if the session did not come back for any reason
            } else {
                /*Set Global Vars and User*/
                UserService.User(data, $cookies.EHRCURRENTUSER);
            }
        }).fail(function() {
            $http.get('/API/APILog.cfc?method=RefreshRestServices');
        });

        // get list setting
        var listSettingsObject = undefined;
        $.ajax({
            type: 'GET',
            url: REST_CONFIG.baseURL + 'ListSetting',
            dataType: 'json',
            async: false
        }).done(function(listSettings) {
            if ($.isEmptyObject(listSettings)) {
                LOG_OUT();
            }

            listSettingsObject = listSettings;

        });

        //This won't be defined in Corporate and since there is no concept of clinic settings we just won't run this section for now
        if (angular.isDefined(UserService.clinicKey)) {
            $.ajax({
                type: 'GET',
                url: REST_CONFIG.baseURL + 'ClinicSetting/Clinic/' + UserService.clinicKey,
                dataType: 'json',
                async: false
            }).done(function(data) {
                if ($.isEmptyObject(data)) {
                    LOG_OUT();
                } else {
                    ClinicSettingService.init(listSettingsObject, data);
                }
            });
        }
    }
]);

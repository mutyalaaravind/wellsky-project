(function(moment) {
    'use strict';

    angular.module('amng.woundcare2024', [
        'LocalStorageModule',
        'services.ic.utils'
    ]).controller('WoundCareController', controller)

    controller.$inject = [
        'localStorageService',
        '$window',
        '$q'
    ];

    function controller(
        localStorageService,
        $window,
        $q
    ) {
        var vm = angular.extend(this, {
            patientKey: null,
            patientTaskKey: null,
            woundCareUrl: null,
            taskName: null,
            abbreviation: null,
            visitDate: null,
            errorList: [],
            initialize: initialize,
            addNewWoundCare: addNewWoundCare,
            applySaveFormFunction: applySaveFormFunction,
        });
        
        function initialize(
            patientKey,
            patientTaskKey,
            woundCareUrl,
            taskName,
            abbreviation,
            visitDate
        ){
            vm.patientKey = patientKey;
            vm.patientTaskKey = patientTaskKey;
            vm.woundCareUrl = woundCareUrl;
            vm.taskName = taskName;
            vm.abbreviation = abbreviation;
            vm.visitDate = visitDate
        }

        function addNewWoundCare(){
            var urlSearchParams = new URLSearchParams({
                patientKey: vm.patientKey,
                patientTaskKey: vm.patientTaskKey,
                taskName: vm.taskName,
                abbreviation: vm.abbreviation
            });
            var fullPath = vm.woundCareUrl + '/wound-dashboard?' + urlSearchParams;
            var params = [undefined, 'Save', fullPath, undefined];
            vm.applySaveFormFunction('validateSubmit', params)
        }

        function applySaveFormFunction(fn, params) {
            $window[fn].apply(null, params);
        }
    }
}) (moment);

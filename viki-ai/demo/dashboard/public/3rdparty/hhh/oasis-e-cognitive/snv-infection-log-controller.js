(function(moment) {
    'use strict';

    angular
        .module('amng.infectionLog', [
            'resources.infection-patient',
            'LocalStorageModule',
            'services.ic.utils'
        ])
        .controller('InfectionLogController', controller)
        .constant('ICConstants', {
            btnText: 'New Infection Log',
            addNewInfectionLogURL: '/EHR/#/AM/QualityControl/log/patient/',
            errorMessage: 'There was an error saving this form, Please contact support if the problem persists.',
            errorTypes: {error: 'error', warning: 'warning'}
        });
        ;

        controller.$inject = [
            'ICConstants',
            'InfectionPatient',
            'InfectionControlUtilsService',
            'localStorageService',
            '$window',
            '$rootScope',
            '$q'
        ];


    function controller(
        ICConstants,
        InfectionPatient,
        InfectionControlUtilsService,
        localStorageService,
        $window,
        $rootScope,
        $q
    ) {
        var vm = angular.extend(this, {
            //members
            caseManagerId: null,
            clinicId: null,
            errorList: [],
            ICConstants: ICConstants,
            infectionTypes:[],
            patientId: null,
            patientInfections:[],
            physicianId: null,
            reportedById:null,
            saveFormFunction: 'modifyForm',
            //methods
            addNewInfection: addNewInfection,
            applySaveFormFunction: applySaveFormFunction,
            getSaveFormCallback: getSaveFormCallback,
            haveErrors: haveErrors,
            initialize: initialize,
            saveForm: saveForm,
            setErrorMessage: setErrorMessage,
            showMessages: showMessages,
        });

        function addNewInfection(){
            vm.saveForm();
        }

        function applySaveFormFunction(fn, params) {
            $window[fn].apply(null, params);
        }

        function getSaveFormCallback() {
            var defer = $q.defer();
            var modifyPromise = defer.promise;
            modifyPromise.then(vm.addNewInfection);

            return (
                function saveFormCallback(resultType) {
                    if (resultType === 'pass') {
                        defer.resolve();
                    } else {
                        defer.reject();
                    }
                    $rootScope.$apply();
                }
            )
        }

        function haveErrors() {
            return (vm.errorList.length);
        }

        function initialize(
            patientId,
            physicianId,
            caseManagerAmUserKey,
            caseManagerUsersKey,
            reportedById,
            clinicId,
            saveFormFunction
         ){
            vm.patientId = patientId;
            vm.physicianId = physicianId;
            vm.caseManagerId = InfectionControlUtilsService.fixCaseManagerUserKey({ AMUSERKEY: caseManagerAmUserKey, USERSKEY: caseManagerUsersKey});
            vm.reportedById = reportedById;
            vm.clinicId = clinicId;
            vm.saveFormFunction = saveFormFunction;
            InfectionPatient.getInfectionLogsByPatient(vm.clinicId,vm.patientId).then(function(response) {
                response.result.forEach(function(infection) {
                    var infectionOtherTypeText = infection.infectionSiteOtherDescription ? ' ' + infection.infectionSiteOtherDescription : '';
                    var infectionTypeText = infection.infectionTypeName ?  infection.infectionTypeName + infectionOtherTypeText : '';
                    if(vm.infectionTypes.indexOf(infectionTypeText) === -1){
                        vm.infectionTypes.push(infectionTypeText);
                    }
                    var infectionOtherSiteText = infection.infectionSiteOtherDescription ? ' ' + infection.infectionSiteOtherDescription : '';
                    vm.patientInfections.push({
                        typeName: infectionTypeText,
                        siteName: infection.infectionSiteName? infection.infectionSiteName + infectionOtherSiteText : '',
                        onSet: infection.isPresentUponAdmission ? 'Present Upon Admission' : infection.dateOfOnset? moment(infection.dateOfOnset).format('MM/DD/YYYY') : '',
                        dateReported: moment(infection.reportedDateTime).format('MM/DD/YYYY'),
                        communicable : infection.communicableOption === "notSelected" ? "" : infection.communicableOption === "yes"? "Yes" : "No",
                        medications: infection.medications ? infection.medications : '',
                        status: (infection.hasOwnProperty('statusOption'))? infection.statusOption.charAt(0).toUpperCase() + infection.statusOption.slice(1): ''
                    });
                });
            });
        }

        function saveForm() {
            if ($window[vm.saveFormFunction] || vm.saveFormFunction == 'saveOasisPage') {
                var params
                var destination = vm.ICConstants.addNewInfectionLogURL + vm.patientId;
                if (vm.saveFormFunction === 'modifyForm') {
                    var saveFormCallback = vm.getSaveFormCallback();
                    params = ['save', destination, undefined, undefined, saveFormCallback];
                } else if (vm.saveFormFunction === 'validateSubmit') {
                    localStorageService.add('snv-ic-return-path', $window.location.href);
                    localStorageService.add('ic-patient-id', vm.patientId);
                    localStorageService.add('ic-physician-id', vm.physicianId);
                    localStorageService.add('ic-case-manager-id', vm.caseManagerId);
                    localStorageService.add('ic-reported-by-id', vm.reportedById);
                    params = [undefined, 'Save', destination, undefined];
                } else if ( vm.saveFormFunction === 'saveOasisPage'){
                    var saveFormCallback = vm.getSaveFormCallback();
                    params = ['s', saveFormCallback];
                } else {
                    vm.setErrorMessage();
                    vm.showMessages();
                    return false;
                }

                vm.applySaveFormFunction(vm.saveFormFunction, params)
            } else {
                vm.setErrorMessage();
                vm.showMessages();
            }
        }

        function setErrorMessage() {
            vm.setErrorList([vm.ICConstants.errorMessage], ICConstants.errorTypes.error);
        }

        function showMessages() {
            if (vm.haveErrors()) {
                vm.showErrorMssg = true;
            }
        }
    }
}) (moment);

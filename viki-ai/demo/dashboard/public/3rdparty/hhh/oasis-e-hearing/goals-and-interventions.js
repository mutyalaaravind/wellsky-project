(function() {
    'use strict';

    angular
        .module('amng.goals-and-interventions', [
            'resources.ptg',
            'LocalStorageModule',
            'services.ptg.instruction-preview'
        ])
        .controller('GoalsAndInterventionsController', controller)
        .filter('sanitizeCustomTags', filter)
        .constant('PTGConstants', {
            btnText: 'Go To Goals and Interventions',
            noDisiplineErrorMessage: 'A discipline must be set before entering Goals and Interventions.',
            errorMessage: 'There was an error retrieving the goals and interventions information for this document. Please contact support if the problem persists.',
            errorTypes: {error: 'error', warning: 'warning'},
            url: '/EHR/#/AM/progress-to-goal/unmet-goals/patienttask/'
        });

    controller.$inject = ['Ptg', 'UserService', 'PTGConstants', 'localStorageService', '$window', '$q', '$rootScope'];

    function controller(Ptg, UserService, PTGConstants, localStorageService, $window, $q, $rootScope) {
        var vm = angular.extend(this, {
            // members
            errorList: [],
            errorType: '',
            goals: [],
            patientTaskKey: null,
            PTGConstants: PTGConstants,
            showAudits: null,
            showErrorMssg: false,
            showGoToPTGButton: null,
            shouldShowSaveForm: false,
            saveFormFunction: 'modifyForm',
            visitDate: '',

            // methods
            applySaveFormFunction: applySaveFormFunction,
            callGetFormAsStruct: callGetFormAsStruct,
            getDisciplines: getDisciplines,
            getSaveFormCallback: getSaveFormCallback,
            getPatientGoalByPatientTask: getPatientGoalByPatientTask,
            getPatientTaskDiscipline: getPatientTaskDiscipline,
            getProcessOasisJSObject: getProcessOasisJSObject,
            goToPTG: goToPTG,
            goToPTGFromOASIS: goToPTGFromOASIS,
            haveErrors: haveErrors,
            hideErrors: hideErrors,
            initialize: initialize,
            initialSync: initialSync,
            onDisciplineChange: onDisciplineChange,
            processGoToPTG: processGoToPTG,
            redirectToPTG: redirectToPTG,
            saveForm: saveForm,
            setErrorAndReject: setErrorAndReject,
            setErrorList: setErrorList,
            setErrorMessage: setErrorMessage,
            showMessages: showMessages,
            sync: sync
        });

        function initialize(
            patientTaskKey,
            visitDate,
            showGoToPTGButton,
            showAudits,
            checkForDiscipline,
            showSimplifiedAudits,
            patientBranchKey,
            shouldShowSaveForm,
            saveFormFunction
        ) {
            vm.patientTaskKey = patientTaskKey;
            vm.ptgUrl = PTGConstants.url + vm.patientTaskKey;
            vm.showGoToPTGButton = showGoToPTGButton;
            vm.showAudits = showAudits;
            vm.checkForDiscipline = checkForDiscipline;
            vm.showSimplifiedAudits = showSimplifiedAudits;
            vm.patientBranchKey = patientBranchKey;
            vm.shouldShowSaveForm = shouldShowSaveForm;
            vm.saveFormFunction = saveFormFunction;
            vm.visitDate = visitDate;
            
            vm.initialSync();
        }

        function initialSync() {
            if (vm.visitDate) {
                vm.sync(true).then(function() {
                    if (vm.checkForDiscipline) {
                        vm.getDisciplines().then(
                                function() {
                                    vm.getPatientTaskDiscipline(true)
                                },
                                vm.showMessages
                        );
                    }
                });
            }
        }

        function sync(hideMessages) {
            return Ptg
                .getSyncStatus(UserService.clinicKey, vm.patientBranchKey, vm.patientTaskKey)
                .then(function(response) {
                    if (response.httpStatusCode !== 200) {
                        if (response.errorList && response.errorList.length) {
                            vm.setErrorList(response.errorList, PTGConstants.errorTypes.warning);
                        } else {
                            vm.setErrorMessage();

                            if (!hideMessages) {
                                vm.showMessages();
                            }
                        }

                        return $q.reject(response);
                    } else if (vm.showAudits) {
                        return vm.getPatientGoalByPatientTask();
                    }
                });
        }

        function getPatientGoalByPatientTask() {
            return Ptg
                .getPatientGoalByPatientTask(UserService.clinicKey, vm.patientBranchKey, vm.patientTaskKey)
                .then(function(response) {
                    if (response.haveError) {
                        vm.setErrorMessage();
                        vm.showMessages();

                        return $q.reject();
                    } else {
                        vm.goals = response;
                    }
                });
        }

        function getPatientTaskDiscipline(hideMessages) {
            return Ptg
                .getPatientTaskDiscipline(UserService.clinicKey, vm.patientBranchKey, vm.patientTaskKey)
                .then(function(response) {
                    if (response.haveError) {
                        if (response.errorList && response.errorList.length) {
                            vm.setErrorList([vm.PTGConstants.noDisiplineErrorMessage], PTGConstants.errorTypes.warning);
                        } else {
                            vm.setErrorMessage();
                        }

                        if (!hideMessages) {
                            vm.showMessages();
                        }

                        return $q.reject();
                    } else {
                        vm.disciplines = vm.disciplines.slice(1);
                        vm.selectedDiscipline = response.discipline;
                        vm.shouldShowDisciplineSelector = response.updatable;
                    }
                }, function () {
                    vm.setErrorMessage();

                    if (!hideMessages) {
                        vm.showMessages();
                    }

                    return $q.reject()
                });
        }

        function getDisciplines() {
            return Ptg
                .getDisciplines(UserService.clinicKey, vm.patientBranchKey)
                .then(function(response) {
                    vm.selectedDiscipline = {listDisciplineKey: 0, disciplineName: ""};
                    vm.disciplines = [vm.selectedDiscipline].concat(response);
                    vm.shouldShowDisciplineSelector = true;
                }, vm.setErrorAndReject);
        }

        function onDisciplineChange() {
            if (vm.selectedDiscipline && vm.selectedDiscipline.listDisciplineKey) {
                Ptg
                    .setPatientTaskDiscipline(
                        UserService.clinicKey,
                        vm.patientBranchKey,
                        vm.patientTaskKey,
                        vm.selectedDiscipline
                    )
                    .then(function(response) {
                        if (response.status === 200 && !(response.haveError)) {
                            vm.hideErrors();
                        } else {
                            vm.setErrorMessage();
                            vm.showMessages();
                        }
                    });
            }
        }

        function setErrorList(errorList, errorType) {
            vm.errorList = errorList;
            vm.errorClass = 'alert-' + errorType;
        }

        function showMessages() {
            if (vm.haveErrors()) {
                vm.showErrorMssg = true;
            }
        }

        function hideErrors() {
            vm.showErrorMssg = false;
        }

        function haveErrors() {
            return (vm.errorList.length);
        }

        function goToPTG() {
            if (vm.shouldShowSaveForm) {
                vm.saveForm();
            } else {
                vm.processGoToPTG();
            }
        }

        function saveForm() {
            if ($window[vm.saveFormFunction] || vm.saveFormFunction == 'saveOasisPage') {
                var params
                if (vm.saveFormFunction === 'modifyForm') {
                    var saveFormCallback = vm.getSaveFormCallback();
                    params = ['save', undefined, undefined, undefined, saveFormCallback];
                } else if (vm.saveFormFunction === 'validateSubmit') {
                    localStorageService.add('oasis-ptg-return-path', $window.location.href);
                    var destination = PTGConstants.url + vm.patientTaskKey;
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

        function getSaveFormCallback() {
            var defer = $q.defer();
            var modifyPromise = defer.promise;
            modifyPromise.then(vm.processGoToPTG);

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

        function applySaveFormFunction(fn, params) {
            $window[fn].apply(null, params);
        }

        function processGoToPTG() {
            var syncPromise = vm.sync();

            if (vm.checkForDiscipline) {
                syncPromise
                    .then(vm.getPatientTaskDiscipline)
                    .then(vm.redirectToPTG, vm.showMessages);
            } else {
                syncPromise
                    .then(vm.redirectToPTG, vm.showMessages);
            }
        }

        function getProcessOasisJSObject() {
            return new processOasisJS();
        }

        function callGetFormAsStruct(element) {
            return getFormAsStruct(element);
        }

        function goToPTGFromOASIS() {
            var result;
            var formStruct = vm.callGetFormAsStruct(document.getElementById('OasisForm'));
            var processOasisObj = vm.getProcessOasisJSObject();

            processOasisObj.setHTTPMethod('POST');
            processOasisObj.modifyOasis(formStruct, 's');
            vm.goToPTG();
        }

        function redirectToPTG() {
            localStorageService.add('oasis-ptg-return-path', $window.location.href);

            $window.location.href = PTGConstants.url + vm.patientTaskKey;
        }

        function setErrorMessage() {
            vm.setErrorList([vm.PTGConstants.errorMessage], PTGConstants.errorTypes.error);
        }

        function setErrorAndReject() {
            vm.setErrorMessage();
            return $q.reject();
        }
    }

    filter.$inject = ['InstructionPreviewService'];

    function filter(InstructionPreviewService) {
        return function(item) {
            return InstructionPreviewService.sanitizeInstruction(item);
        };
    }
}) ();

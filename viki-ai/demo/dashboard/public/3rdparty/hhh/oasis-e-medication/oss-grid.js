(function() {
    'use strict';

    angular
        .module('directives.kinnser.oss-grid', [
            'resources.episodeFrequency'
        ])
        .constant('kOssGridConstants', {
            taskTypesLookup: {
                'SN': 1,
                'PT': 3,
                'OT': 6,
                'ST': 7,
                'HHA': 4,
                'MSW': 8
            }
        })
        .directive('kOssGrid', directive);

    directive.$inject = ['EpisodeFrequency', 'kOssGridConstants'];

    function directive(EpisodeFrequency, CONSTANT) {
        return {
            restrict: 'E',
            templateUrl: '/EHR/scripts/directives/kinnser/oss-grid/oss-grid.html?868cfec8ed2afa02',
            scope:{
                backDate: '@',
                disciplineType: '@?',
                episodeEndDate: '@',
                episodeKey: '@',
                episodeStartDate: '@',
                firstDayWeek: '@',
                frequencyRanges: '@',
                isNewOrder: '@',
                isPhysicianOrder: '@?',
                isPostHospital: '@',
                isRoc: '@',
                isTransitionPatient: '@?',
                oasisMode: '@',
                ossModel: '=',
                patientTaskKey: '@?',
                recert: '@',
                transitionPatientCheckbox: '@?',
                isOasisroc: '@'
            },
            controller: [
                '$scope',
                '$modal',
                'OssModalService',
                '$dialog',
                'EpisodeFrequency',
                '$timeout',
            function($scope, $modal, OssModalService, $dialog, EpisodeFrequency, $timeout) {
                $scope.dcDate = new Date();
                $scope.episodeFrequencies = [];
                $scope.frequencyOptions = [];
                $scope.intervalOptions = [];
                $scope.OssModalService = OssModalService;
                $scope.currentFrequencyStatusKey = 2;
                $scope.currentByTaskType = {};

                $scope.discontinuationStatus = {
                    1: {
                        show: false,
                        disabled: false
                    },
                    3: {
                        show: false,
                        disabled: false
                    },
                    6: {
                        show: false,
                        disabled: false
                    },
                    7: {
                        show: false,
                        disabled: false
                    },
                    4: {
                        show: false,
                        disabled: false
                    },
                    8: {
                        show: false,
                        disabled: false
                    }
                };

                EpisodeFrequency.getEpisodeDiscontinuationStatus($scope.episodeKey)
                    .then(function(data) {
                        $scope.discontinuationStatus = data;
                    });

                $scope.headerText = 'Orders';

                if($scope.isPostHospital === 'true'){
                    $scope.headerText = 'Post Hospital Orders';
                }

                if($scope.isRoc === 'true' && $scope.isPostHospital === 'false'){
                    $scope.headerText = 'Orders for Recertification';
                }

                $scope.getDates = function getDates() {
                    var startDate;
                    var endDate;

                    if (angular.isDefined($scope.isTransitionPatient)) {
                        // is transition patient -> use as SOC (i.e.: freqs will be in this episode)
                        if (eval($scope.isTransitionPatient)) {
                            startDate = moment($scope.episodeStartDate);
                            endDate = moment($scope.episodeEndDate);
                        }

                        // is recert -> use as Recert (i.e.: freqs will be in the next episode)
                        else {
                            startDate = moment($scope.episodeEndDate).add(1, 'days');
                            endDate = moment($scope.episodeEndDate).add(59, 'days');
                        }
                    } else if ($scope.recert === 'true') {
                        startDate = moment($scope.episodeEndDate).add(1, 'days');
                        endDate = moment($scope.episodeEndDate).add(59, 'days');
                    } else {
                        startDate = moment($scope.episodeStartDate);
                        endDate = moment($scope.episodeEndDate);
                    }

                    return {
                        startDate: startDate,
                        endDate: endDate
                    };
                }

                var dates = $scope.getDates();

                $scope.episodeStart = dates.startDate;
                $scope.episodeEnd = dates.endDate;

                if($scope.firstDayWeek === 'SATURDAY'){
                    $scope.wStart = 6;
                    $scope.wEnd = moment($scope.episodeStart).day() === 6 ? 12 : 5;
                }else if($scope.firstDayWeek === 'MONDAY'){
                    $scope.wStart = 1;
                    $scope.wEnd = 7;
                }else{
                    $scope.wStart = 0;
                    $scope.wEnd = 6;
                }

                $scope.episode = [];

                if ($scope.transitionPatientCheckbox) {
                    var $e = $('#' + $scope.transitionPatientCheckbox);

                    if ($e.length) {
                        $scope.isTransitionPatient = $e.is(':checked');

                        $e.change(function(e) {
                            $timeout(function() {
                                $scope.isTransitionPatient = $e.is(':checked');

                                var dates = $scope.getDates();

                                $scope.episodeStart = dates.startDate;
                                $scope.episodeEnd = dates.endDate;

                                $scope.episode = [];
                                $scope.findEpisodeWorkWeeks();

                                $scope.$broadcast('oss-grid:transition-patient-changed', {
                                    endDate: dates.endDate,
                                    episode: $scope.episode,
                                    startDate: dates.startDate
                                });
                            }, 0);
                        });

                        $scope.frequenciesCount = {SN: 0, PT: 0, OT: 0, ST: 0, HHA: 0, MSW: 0};

                        $scope.$on('oss-modal:frequencies-count-changed', function(event, data) {
                            $scope.frequenciesCount[data.discipline] = data.count;

                            $e.attr('disabled', $scope.taskHaveFrequencies($scope.frequenciesCount));
                        });

                        $scope.taskHaveFrequencies = function taskHaveFrequencies(frequencies) {
                            var result = false;

                            Object.keys(frequencies).forEach(function(discipline) {
                                if (frequencies[discipline] > 0) {
                                    result = true;
                                }
                            });

                            return result;
                        }
                    }
                }

                $scope.getWorkWeek = function(){
                    return {start: '', end: '', weekNumber: 1, last: false};
                }

                $scope.getEndOfWorkWeek = function(date){
                    return moment(date).day($scope.wEnd).format('MM/DD/YYYY');
                }

                $scope.getEndOfNextWorkWeek = function(date){
                    return moment(date).add(6, 'days').format('MM/DD/YYYY');
                }

                $scope.isWorkWeekStartDay = function(date){
                    return moment(date).day() === $scope.wStart ? true : false;
                }

                $scope.firstWorkWeek = function(){
                    var week = $scope.getWorkWeek();

                    week.start = moment($scope.episodeStart).format('MM/DD/YYYY');
                    week.end = $scope.getEndOfWorkWeek(week.start);

                    return week;
                }

                $scope.nextWorkWeeks = function(){
                    for(var i = 0; i < $scope.episode.length; i++){
                        var week = $scope.getWorkWeek();

                        week.start = moment($scope.episode[i].end).add(1, 'day').format('MM/DD/YYYY');
                        week.end = $scope.getEndOfNextWorkWeek(week.start);
                        week.weekNumber = i + 2;

                        $scope.episode.push(week);

                        if( moment(week.start).diff(moment($scope.episodeEnd), 'days') <= 0 && moment(week.end).diff(moment($scope.episodeEnd), 'days') >= 0 ){
                            week.lastWeekEnd = week.end;
                            week.end = moment($scope.episodeEnd).format('MM/DD/YYYY');
                            week.last = true;

                            return;
                        }

                    }
                }

                $scope.findEpisodeWorkWeeks = function(){
                    $scope.episode.push($scope.firstWorkWeek());
                    $scope.nextWorkWeeks();
                }

                $scope.findEpisodeWorkWeeks();

                OssModalService.getListData().then(function(data) {
                    $scope.$broadcast('oss-grid:list-data-loaded', data);
                });

                $scope.showDcModal = function(discipline){
                    var processingInstance = $modal({
                        template : '/EHR/scripts/directives/kinnser/oss-grid/templates/oss-grid-discontinue.html?90918f68fc99e956',
                        backdrop : 'static',
                        scope    : $scope,
                        show     : false,
                        persist  : true
                    });

                    var taskTypeId = CONSTANT.taskTypesLookup[discipline];
                    var disciplineDiscStatus = $scope.discontinuationStatus[taskTypeId];

                    $scope.modal =  {
                        showCloseButton  : true,
                        headerContent    : 'Discontinue',
                        goButtonText     : 'OK',
                        cancelButtonText : 'Cancel',
                        cancelButtonAction : function(){},
                        goButtonAction   : function( ){
                            OssModalService.discontinueFrequencies(discipline, $scope.dcDate, $scope.dcReason, $scope.episode, $scope.isPostHospital);
                            $scope.dcDate = new Date();
                            $scope.dcReason = '';
                            $scope.$broadcast('oss-grid:frequency-discontined', discipline);
                            disciplineDiscStatus.disabled = true;
                            $scope.hide();
                        }
                    };

                    processingInstance.then(function(modalTemplate) {
                        modalTemplate.modal('show');
                    });
                };

                $scope.showDeleteModal = function(discipline) {
                    if ($scope.shouldDisableDelete(discipline)) {
                        return false;
                    }

                    $dialog.messageBox(
                        'Delete ',
                        'This action will delete the pending frequencies for this discipline. ' +
                        'Are you sure you wish to proceed?',
                        [
                            {
                                result: false,
                                label: 'Cancel'
                            },
                            {
                                result: true,
                                label: 'Delete',
                                cssClass: 'btn-primary'
                            }
                        ]
                    )
                    .open()
                    .then(function(result) {
                        if (result) {
                            OssModalService
                                .deleteFrequencies(discipline, $scope.isPostHospital)
                                .then(function() {
                                    $scope.$broadcast('oss-grid:frequencies-deleted', discipline);
                                    OssModalService.clearEpisodeFrequencies(discipline, $scope.isPostHospital);
                                    $scope.$emit('oss-modal:frequencies-count-changed', {
                                        discipline: discipline,
                                        count: 0
                                    });
                                });
                        }
                    });
                };

                $scope.shouldShowDC = function shouldShowDC(discipline) {
                    var result;
                    var taskTypeId = CONSTANT.taskTypesLookup[discipline];

                    if ($scope.recert === 'true' && !eval($scope.isTransitionPatient)) {
                        result = false;
                    } else {
                        result = $scope.discontinuationStatus[taskTypeId].show;
                    }

                    return result;
                };

                $scope.shouldShowDelete = function shouldShowDelete(discipline) {
                    var result;

                    if ($scope.recert === 'true' && !eval($scope.isTransitionPatient)) {
                        result = false;
                    } else {
                        result = (!$scope.shouldShowDC(discipline));
                    }

                    return result;
                };

                $scope.shouldDisableDC = function shouldDisableDC(discipline) {
                    var taskTypeId = CONSTANT.taskTypesLookup[discipline];
                    var oasis = eval($scope.oasisMode);
                    var oasisRoc = eval($scope.isOasisroc);

                    return $scope.discontinuationStatus[taskTypeId].show &&
                           (
                               $scope.discontinuationStatus[taskTypeId].disabled ||
                               (oasis && !oasisRoc) ||
                               (oasisRoc && $scope.isRoc === 'true' && $scope.isPostHospital === 'false')
                            );
                }

                $scope.shouldDisableDelete = function shouldDisableDelete(discipline) {
                    return !OssModalService.retrieveEpisodeFrequencyKeys(discipline, 'New', $scope.isPostHospital) &&
                           !OssModalService.retrieveEpisodeFrequencyKeys(discipline, 'Current', $scope.isPostHospital);
                }
            }]
        };
    };
})();

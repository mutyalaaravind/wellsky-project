(function() {
	'use strict';

	angular
        .module('directives.kinnser.oss-modal', [
            'resources.episodeFrequency',
            'resources.list-frequency',
            'resources.list-interval',
            'directives.kinnser.oss-modal.oss-modal-service',
            'directives.kinnser.oss-modal.oss-modal-confirmation-controller',
            'ui.bootstrap'
		])
        .constant('kOssModalConstants', {
            confirmationModal: {
                controller: 'OSSModalConfirmationController',
                template: '/EHR/scripts/directives/kinnser/oss-modal/oss-modal-confirmation.html'
            },
            currentStatusKey: 2
        })
        .directive('kOssModal', directive);

    directive.$inject = ['kOssModalConstants'];

	function directive(CONSTANTS) {
		return {
			restrict: 'E',
			templateUrl: '/EHR/scripts/directives/kinnser/oss-modal/oss-modal.html?f5886e74c5fc26f1',
			scope:{
                backDate: '@',
                currDiscReason: '=',
                currentFrequencyString: '=',
                currPrnReason: '=',
                discipline: '@',
                disciplineType: '@?',
                discReason: '=',
                encodedFrequencyString: '=',
                episodeKey: '@',
                frequencyRanges: '@',
                isPhysicianOrder: '@?',
                isTransitionPatient: '@?',
                ossModel: '=',
                patientTaskKey: '@?',
                prnReason: '=',
                recert: '@',
                taskType: '@',
                temp: '@'
			},
			controller: [
				'$scope',
				'$q',
				'$modal',
                '$location',
                'EpisodeFrequency',
                'OssModalService',
                '$dialog',
                '$timeout',
			function($scope, $q, $modal, $location, EpisodeFrequency, OssModalService, $dialog, $timeout) {
                $scope.getLoadStatusList = getLoadStatusList;
                $scope.getFrequencyStatusKey = getFrequencyStatusKey;
                $scope.resetSortedIndexes = resetSortedIndexes;

                $scope.episodeStart = $scope.$parent.$parent.$parent.episodeStart;
                $scope.episodeEnd = $scope.$parent.$parent.$parent.episodeEnd;

                $scope.isPho = $scope.$parent.$parent.$parent.isPostHospital;

                if ($scope.recert === 'true' || eval($scope.isTransitionPatient)) {
                    $scope.firstEffectiveDate = $scope.episodeStart;
                } else {
                    $scope.firstEffectiveDate = moment().format('MM/DD/YYYY');
                }

                $scope.firstEffectiveDate = moment($scope.firstEffectiveDate).format('MM/DD/YYYY');

                $scope.frequencyOptions = [];
                $scope.intervalOptions = [];

                $scope.currentOrderFrequencies = [];
                $scope.currentFrequencyString = '';

                $scope.prn = {
                    count: 0,
                    reason: ''
                };

                $scope.episode = $scope.$parent.$parent.$parent.episode;
                $scope.oasisMode = $scope.$parent.$parent.$parent.oasisMode;
                $scope.isNewOrder = $scope.$parent.$parent.$parent.isNewOrder;

                $scope.maxRowIndex = 5;                 //Governs max number of modal rows based on index (0 through 5: 6 rows)
                $scope.maxVisibleIndex = 0;             //Tracks the currently max visible row by index
                $scope.episodeStatusString = '';
                $scope.alertStyle = '';
                $scope.validDuration = false;
                $scope.submissionError = {error: false, text: ''};
                $scope.discontinueString;

                $scope.sorted = [];
                $scope.loadingCurrentOrder = false;     //If current order is being loaded certain things like calcEffectiveDates should not run how they usually do

                $scope.$on('oss-grid:transition-patient-changed', function(event, data) {
                    $timeout(function() {
                        $scope.firstEffectiveDate = moment(data.startDate).format('MM/DD/YYYY');
                        $scope.episodeStart = moment(data.startDate).format('MM/DD/YYYY');
                        $scope.episodeEnd = moment(data.endDate).format('MM/DD/YYYY');
                        $scope.episode = data.episode;

                        $scope.items.forEach(function(item) {
                            if (item.frequencyObject.effectiveDate && !item.frequencyObject.patientTaskKey) {
                                item.frequencyObject.effectiveDate = $scope.firstEffectiveDate;
                            }
                        });
                    }, 0);
                });

                $scope.loadStatusList = $scope.getLoadStatusList();

                //Default empty modal
                $scope.getDefaultEmptyModal = function getDefaultEmptyModal() {
                    return [
                        {
                            decoded: false,
                            disabled: false,
                            display: true,
                            frequencyObject: {
                                active: 1,
                                discontinueDate: '',
                                discontinueFlag: false,
                                discontinueReason: '',
                                duration: 0,
                                effectiveDate: $scope.firstEffectiveDate,
                                episodeFrequencyKey: 0,
                                episodeKey: $scope.episodeKey,
                                inFrequency: false,
                                listFrequencyKey: 3,
                                listFrequencyStatusKey: $scope.getFrequencyStatusKey(),
                                listIntervalKey: 1,
                                listTaskTypeKey: $scope.taskType,
                                occurrenceMax: 0,
                                occurrenceMin: '',
                                pending: 0
                            },
                            showAdd: true,
                            valid: true,
                            validBack: true,
                            wwNum: 0
                        },
                        {
                            decoded: false,
                            disabled: false,
                            display: false,
                            frequencyObject: {
                                active: 1,
                                discontinueDate: '',
                                discontinueFlag: false,
                                discontinueReason: '',
                                duration: 0,
                                effectiveDate: '',
                                episodeFrequencyKey: 0,
                                episodeKey: $scope.episodeKey,
                                inFrequency: false,
                                listFrequencyKey: 3,
                                listFrequencyStatusKey: $scope.getFrequencyStatusKey(),
                                listIntervalKey: 1,
                                listTaskTypeKey: $scope.taskType,
                                occurrenceMax: 0,
                                occurrenceMin: '',
                                pending: 0
                            },
                            showAdd: true,
                            valid: true,
                            validBack: true,
                            wwNum: 0
                        }
                    ];
                }

                $scope.items = $scope.getDefaultEmptyModal();
                $scope.discontinuedItems = [];
                $scope.discontinuedIndexes = [];

                $scope.setupWatchers = function setupWatchers() {
                    $scope.$watch('items[0].frequencyObject', function(newVal, oldVal){
                        if(!$scope.loadingCurrentOrder){
                            $scope.handleRowAlteration(newVal, oldVal, 1);
                        }
                    }, true);

                    $scope.$watch('items[1].frequencyObject', function(newVal, oldVal){
                        if(!$scope.loadingCurrentOrder){
                            $scope.handleRowAlteration(newVal, oldVal, 2);
                        }
                    }, true);

                    $scope.$watch('items[2].frequencyObject', function(newVal, oldVal){
                        if(!$scope.loadingCurrentOrder){
                            $scope.handleRowAlteration(newVal, oldVal, 3);
                        }
                    }, true);

                    $scope.$watch('items[3].frequencyObject', function(newVal, oldVal){
                        if(!$scope.loadingCurrentOrder){
                            $scope.handleRowAlteration(newVal, oldVal, 4);
                        }
                    }, true);

                    $scope.$watch('items[4].frequencyObject', function(newVal, oldVal){
                        if(!$scope.loadingCurrentOrder){
                            $scope.handleRowAlteration(newVal, oldVal, 5);
                        }
                    }, true);

                    $scope.$watch('items[5].frequencyObject', function(newVal, oldVal){
                        if(!$scope.loadingCurrentOrder){
                            $scope.handleRowAlteration(newVal, oldVal, 6);
                        }
                    }, true);
                }

                $scope.$on('oss-grid:list-data-loaded', function(event, data) {
                    $scope.frequencyOptions = data.frequencyOptions;
                    $scope.intervalOptions = data.intervalOptions;

                    //Set up watchers for each row now that we have frequency data
                    $scope.setupWatchers();

                    //Current frequencies always loaded first
                    OssModalService.getEpisodeFrequencies(
                        $scope.episodeKey,
                        $scope.taskType,
                        $scope.discipline,
                        $scope.loadStatusList[0],
                        $scope.recert,
                        $scope.isPho,
                        $scope.episode,
                        $scope.isTransitionPatient
                    ).then(function(result) {
                        $scope.currentOrderFrequencies = result.model;

                        if($scope.currentOrderFrequencies.length > 0){
                            $scope.populateModal($scope.currentOrderFrequencies);
                            $scope.currentFrequencyString = $scope.encode(true, $scope.currentOrderFrequencies);
                            $scope.currPrnReason = $scope.currentOrderFrequencies[0].PRNReason;
                            $scope.currDiscReason = $scope.discontinueString;
                        }

                        //This is if we need to show something other than the current frequencies, can be oasis saved or newly saved
                        if($scope.loadStatusList.length > 1){
                            OssModalService.getEpisodeFrequencies(
                                $scope.episodeKey,
                                $scope.taskType,
                                $scope.discipline,
                                $scope.loadStatusList[1],
                                $scope.recert,
                                $scope.isPho,
                                $scope.episode,
                                $scope.isTransitionPatient
                            ).then(function(result) {
                                var frequencies = [];

                                //If we pull oasis saved we overwrite the previously pulled 'current' frequencies
                                if ($scope.loadStatusList[1] === '3') {
                                    frequencies = $scope.currentOrderFrequencies = result.model;
                                } else {  //Otherwise pull in the 'new' frequencies and save them alongside the 'current'
                                    $scope.newOrderFrequencies = result.model;
                                    $scope.disableMatchingNew($scope.newOrderFrequencies, $scope.currentOrderFrequencies);
                                    frequencies = $scope.newOrderFrequencies;
                                }

                                if (frequencies.length > 0) {
                                    $scope.populateModal(frequencies);
                                    $scope.encode(false, frequencies);
                                }
                            });
                        }
                    });
                });

                $scope.tempArr = [];

                //Function to take the current item array and convert it into a frequency string
                $scope.encode = function(returnString, frequencies){
                    var filteredFrequencies = frequencies.filter(function(frequency) {
                        return frequency.listFrequencyStatusKey !== CONSTANTS.currentStatusKey
                            || !frequency.discontinueFlag
                            || frequency.discontinuedNotSaved;
                    });

                    var string = OssModalService.getFrequenciesString(filteredFrequencies,$scope.frequencyRanges);

                    if (filteredFrequencies.length) {
                        var reason = '';
                        var discDates = {};

                        angular.forEach(filteredFrequencies, function(item, index){
                            if (item.discontinueReason) {
                                item.discontinueReason = item.discontinueReason.replace(/'/g, '');
                            }

                            if (item.discontinueDate != '') {
                                reason = reason || item.discontinueReason;
                                discDates[item.discontinueDate] = true;
                            }
                        });

                        var discontinueString = '';

                        if (Object.keys(discDates).length) {
                            discontinueString = 'Discontinuations: ' + Object.keys(discDates).join(', ');

                            if (reason) {
                                discontinueString += ', Reason: ' + reason;
                            }
                        }

                        $scope.discontinueString = discontinueString;
                        $scope.discReason = $scope.discontinueString;
                    }

                    if (returnString) {
                        return string;
                    } else {
                        $scope.encodedFrequencyString = string;
                    }
                };

                //Called when a row is changed, sets validation data for each row, re-checks frequency end dates and triggers cascade of effective date calculations
                $scope.handleRowAlteration = function(newVal, oldVal, index){
                    if(angular.isDefined(newVal)){
                        if(newVal.effectiveDate !== ''){
                            newVal.listIntervalKey = newVal.listFrequencyKey != 3 ? 1 : newVal.listIntervalKey; //Only weekly can be set to 'every other'
                            newVal.frequencyEnd = OssModalService.calcFreqEnd(newVal, $scope.episode);

                            $scope.items[index-1].validBack = true;
                            if(angular.isDefined($scope.items[index - 2])){
                                var freq = $scope.items[index - 2].frequencyObject;

                                //Checks if a frequency has been illegally backdated into another frequency
                                if(moment(newVal.effectiveDate).diff(freq.frequencyEnd) <= 0){
                                    $scope.items[index-1].validBack = false || freq.discontinueDate !== '' || $scope.backDate === 'true';
                                }

                                if(freq.discontinueDate !== ''){
                                    if($scope.backDate === 'false' && moment(newVal.effectiveDate).diff(freq.discontinueDate) <= 0 && freq.discontinueDate !== ''){
                                        $scope.items[index-1].validBack = false
                                    }
                                }
                            }
                        }

                        if(OssModalService.validEffectiveDate(newVal.effectiveDate, $scope.episodeStart)){
                            $scope.items[index-1].valid = true;
                            $scope.calcEffectiveDates(index);
                        }else{
                            $scope.items[index-1].valid = false;
                        }
                    }
                };

                //Helper function to calculate effective dates for the passed index and every entry below
                $scope.calcEffectiveDates = function(index){
                    // ugly hack to avoid the $watchers() to change the effective dates when sorting the frequencies
                    // by effective date
                    if ($scope.sorted[index - 1]) {
                        $scope.sorted[index - 1] = false;

                        return;
                    }

                    if(angular.isDefined($scope.items[index])){
                        for(var i = index; i < $scope.items.length; i++){
                            var row = $scope.items[i];
                            var prev = $scope.items.length !== 2 ? $scope.items[i-1].frequencyObject : $scope.items[i].frequencyObject;
                            var shouldUpdateEffectiveDate = (
                                row.display &&
                                !row.disabled &&
                                !row.frequencyObject.patientTaskKey &&
                                !$scope.loadingCurrentOrder
                            );

                            if (shouldUpdateEffectiveDate) {
                                row.frequencyObject.effectiveDate = moment(prev.frequencyEnd).add(1, 'days').format("MM/DD/YYYY");
                            }
                        }
                    }

                    //Calculate work week numbers
                    angular.forEach($scope.items, function(item){
                        if(item.display && !item.disabled){
                            item.wwNum = OssModalService.calcWorkWeekNumber(item.frequencyObject.effectiveDate, $scope.episode);
                        }
                    });

                    $scope.setStatusBar($scope.maxVisibleIndex);
                };

                //Helper function to calculate the latest end date for the status bar (effective date + duration * frequency)
                $scope.calcLatestEndDate = function(){
                    var items = $scope.items.filter(function(item) {
                        var date = item.frequencyObject.discontinueDate || item.frequencyObject.frequencyEnd;

                        return angular.isDefined(date);
                    });

                    items.sort(function(a, b) {
                        var dateA = a.frequencyObject.discontinueDate || a.frequencyObject.frequencyEnd;
                        var dateB = b.frequencyObject.discontinueDate || b.frequencyObject.frequencyEnd;

                        return moment(dateB).unix() - moment(dateA).unix();
                    });

                    return items[0].frequencyObject.discontinueDate || items[0].frequencyObject.frequencyEnd;
                };

                //Sets the status bar content
                $scope.setStatusBar = function(){
                    var dateRangeEnd = $scope.calcLatestEndDate();
                    var episodeEnd = moment($scope.episodeEnd);

                    var days = episodeEnd.diff(dateRangeEnd, 'days');
                    var weeks = days / 7;

                    if (weeks >= 1) {
                       $scope.episodeStatusString = Math.ceil(weeks) + ' weeks (' + days + ' days) remaining in' + ($scope.recert === 'true' ? ' the next ' : ' this ') + 'episode. (' + moment($scope.episodeEnd).format('MM/DD/YYYY') + ')';
                    } else {
                        $scope.episodeStatusString = days + ' days remaining in' + ($scope.recert === 'true' ? ' the next ' : ' this ' ) + 'episode. (' + moment($scope.episodeEnd).format('MM/DD/YYYY') + ')';
                    }

                    if (days < 0) {
                        $scope.validDuration = false;
                        $scope.alertStyle = 'error';
                    } else if (days === 0) {
                        $scope.validDuration = true;
                        $scope.alertStyle = '';
                    } else {
                        $scope.validDuration = true;
                        $scope.alertStyle = 'info';
                    }
                };

                $scope.sortFrequencies = function sortFrequencies() {
                    var sortedItems = [];
                    var leftItems = [];

                    $scope.items.slice(0).forEach(function(item) {
                        var newItem = angular.extend({}, item, {showAdd: false});

                        if (item && item.frequencyObject && item.frequencyObject.effectiveDate) {
                            sortedItems.push(newItem);
                        } else {
                            leftItems.push(newItem);
                        }
                    });

                    sortedItems.sort(function(a, b) {
                        return moment(a.frequencyObject.effectiveDate).unix() - moment(b.frequencyObject.effectiveDate).unix();
                    });

                    $scope.items = sortedItems.concat(leftItems);
                    $scope.resetSortedIndexes();
                }

                //Add a new row by showing buffer row and adding a new buffer when needed
                $scope.addRow = function(index){
                    $scope.sortFrequencies();

                    var row = $scope.items[index];
                    var prev = $scope.items[index-1];

                    // In case prev freq is totally discontinued but there are others that not
                    $scope.items.slice(0, index).forEach(function(item) {
                        if (!item.frequencyObject.discontinueFlag) {
                            prev = item;
                        }
                    });

                    //Keep adding buffer rows to aid with HTML rendering until we are at max rows, in that case just display the buffer
    				if(index !== $scope.maxRowIndex){
    					$scope.addBufferRow();
                        row.display = row.showAdd = true;
    				}else{
    					$scope.items[$scope.maxRowIndex].display = true;
    				}

                    $scope.maxVisibleIndex++;

                    // Check if we use the next sequential effective date or just use discontinuation date logic
                    var date;

                    if (prev.frequencyObject.discontinueDate !== '') {
                        var prevDiscDate = moment(prev.frequencyObject.discontinueDate);
                        date = (prev.frequencyObject.discontinueFlag ? prevDiscDate : prevDiscDate.add(1, 'days'))
                            .format('MM/DD/YYYY');
                    } else {
                        date = OssModalService.useWorkWeekStart(prev.frequencyObject, row.frequencyObject, $scope.episode);
                    }

                    row.frequencyObject.effectiveDate = !date ? OssModalService.calcRangeEnd(prev.frequencyObject) : date;
                    row.frequencyObject.frequencyEnd = OssModalService.calcFreqEnd(row.frequencyObject, $scope.episode);

                    $scope.setStatusBar($scope.maxVisibleIndex);
    			};

                //Remove row by splicing it out of the items array
                $scope.removeRow = function(index){
                    //If we remove a row when the items array is maxed then we re-insert the buffer item into the items array
                    if(angular.isDefined($scope.items[$scope.maxRowIndex])){
                        if($scope.items[$scope.maxRowIndex].display){
                            $scope.addBufferRow();
                        }
                    }

                    $scope.maxVisibleIndex--;
                    $scope.items.splice(index, 1);
                    $scope.items[$scope.items.length-2].showAdd = true;

                    $scope.setStatusBar($scope.maxVisibleIndex);
                };

                //Helper function to push a buffer object into the item array, these are initiall not displayed so adding a row only means unhiding the buffer, done to prevent html flickering bug
                $scope.createEmptyRow = function createEmptyRow() {
                    return {
                        decoded: false,
                        disabled: false,
                        display: false,
                        frequencyObject: {
                            active: 1,
                            discontinueDate: '',
                            discontinueFlag: false,
                            discontinueReason: '',
                            duration: 0,
                            effectiveDate: '',
                            episodeFrequencyKey: 0,
                            episodeKey: $scope.episodeKey,
                            inFrequency: false,
                            listFrequencyKey: 3,
                            listFrequencyStatusKey: $scope.getFrequencyStatusKey(),
                            listIntervalKey: 1,
                            listTaskTypeKey: $scope.taskType,
                            occurrenceMax: 0,
                            occurrenceMin: '',
                            pending: 0
                        },
                        showAdd: false,
                        valid: true,
                        validBack: true,
                        wwNum: 0
                    };
                };

                $scope.addBufferRow = function(){
                    $scope.items.push($scope.createEmptyRow());
                };

                $scope.emptyFirstRow = function emptyFirstRow() {
                    $scope.encodedFrequencyString = '';
                    $scope.prn.reason = '';
                    $scope.prn.count = 0;
                    OssModalService.saveEpisodeFrequencies(
                        $scope.episodeKey,
                        [],
                        $scope.discipline,
                        $scope.recert,
                        $scope.loadStatusList[0],
                        $scope.isPho,
                        $scope.patientTaskKey,
                        $scope.isTransitionPatient
                    ).then(function() {
                        $scope.items = $scope.getDefaultEmptyModal();
                    });
                }

                $scope.blankRow = function blankRow(index) {
                    var backdropListener = setInterval(function() {
                        var $backdrops = $('.modal-backdrop');

                        if ($backdrops.size() > 1) {
                            var $msgBoxBackdrop = $backdrops.last();
                            var $msgBoxModal = $msgBoxBackdrop.siblings('.modal').last();
                            var zIndex = parseInt($backdrops.first().css('zIndex')) || 5000;

                            $msgBoxBackdrop.css('zIndex', zIndex + 20);
                            $msgBoxModal.css('zIndex', zIndex + 30);

                            clearInterval(backdropListener);
                        }
                    }, 10);

                    $dialog
                        .messageBox()
                        .open(CONSTANTS.confirmationModal.template, CONSTANTS.confirmationModal.controller)
                        .then(function(result) {
                            if (result) {
                                $scope.emptyFirstRow();

                                $scope.$emit('oss-modal:frequencies-count-changed', {
                                    discipline: $scope.discipline,
                                    count: 0
                                });
                            }

                            OssModalService.setForcedBlankRow($scope.taskType, result);
                        });
                }

                //Sends data to the grid and closes modal, validation done as well
                $scope.submitFrequencies = function(event){
                    event.preventDefault();

                    $scope.submissionError = OssModalService.validateFrequencies($scope.items, $scope.maxVisibleIndex, $scope.frequencyRanges, $scope.prn.count, $scope.episodeStart, $scope.episodeEnd, $scope.validDuration, $scope.episode);

                    //No apostrophes in this string
                    if ($scope.prn.reason) {
                        $scope.prn.reason = $scope.prn.reason.replace(/'/g, '');
                    }

                    if(!$scope.submissionError.error){
                        var frequencies = [];
                        var discIndex = 0;
                        var itemIndex = 0;

                        var prevEnd = '01/01/1900';

                        $scope.sortFrequencies();

                        //Combine the modal frequencies with any removed discontinued frequencies
                        for(var i = 0; i < $scope.items.length + $scope.discontinuedIndexes.length; i++){
                            var item = $scope.items[itemIndex];
                            var disc = $scope.discontinuedItems[discIndex];

                            if(item.display){
                                if($scope.discontinuedIndexes[discIndex] === i){
                                    frequencies.push(disc.frequencyObject);
                                    discIndex++;
                                }else{
                                    item.frequencyObject.discontinueFlag = angular.isDefined(item.frequencyObject.discontinueFlag) ? item.frequencyObject.discontinueFlag : false;
                                    item.display ? frequencies.push(item.frequencyObject) : '';
                                    itemIndex++;
                                }
                            }
                        }

                        // Do not use totally discontinued freq to encode each frequencyString
                        var frequenciesNoDiscontFlag = frequencies.filter(function(f) {
                            return !f.discontinueFlag;
                        });

                        //Set PRN values on model before submitting
                        angular.forEach(frequencies, function(item, index){
                            item.PRN = $scope.prn.count;
                            item.PRNReason = $scope.prn.reason;
                            item.frequencyString = $scope.encode(true, frequenciesNoDiscontFlag);
                        });

                        $scope.prnReason = $scope.prn.reason;
                        $scope.encode(false, frequencies);

                        $scope.loadingCurrentOrder = true;

                        var that = this;

                        // Do not send current freqs that are completely discontinued so we prevent
                        // from duplicating it and creating a new freq
                        frequencies = frequencies.filter(function(f) {
                            return !(
                                f.listFrequencyStatusKey === CONSTANTS.currentStatusKey
                                && f.discontinueFlag
                                && !f.discontinuedNotSaved
                            );
                        })

                        OssModalService.saveEpisodeFrequencies(
                            $scope.episodeKey,
                            frequencies,
                            $scope.discipline,
                            $scope.recert,
                            $scope.loadStatusList[0],
                            $scope.isPho,
                            $scope.patientTaskKey,
                            $scope.isTransitionPatient
                        ).then(function() {
                            $scope.loadingCurrentOrder = false;

                            $scope.$emit('oss-modal:frequencies-count-changed', {
                                discipline: $scope.discipline,
                                count: frequencies.length
                            });

                            that.hide();
                        });
                    }
                };

                //Need to rebuild the modal if a discontinuation is made
                $scope.$on('oss-grid:frequency-discontined', function(event, discipline){
                    $scope.currentOrderFrequencies = OssModalService.retrieveEpisodeFrequencies($scope.discipline, 'Current', $scope.isPho);
                    $scope.currentOrderFrequencies = $scope.currentOrderFrequencies.length === 0 ? [$scope.items[0].frequencyObject] : $scope.currentOrderFrequencies;

                    if(discipline === $scope.discipline){
                        $scope.populateModal($scope.currentOrderFrequencies);
                        angular.forEach($scope.currentOrderFrequencies, function(item, index){
                            item.frequencyString = $scope.encode(true, $scope.currentOrderFrequencies);
                        });
                        $scope.encode(false, $scope.currentOrderFrequencies);
                        OssModalService.saveEpisodeFrequencies(
                            $scope.episodeKey,
                            $scope.currentOrderFrequencies,
                            $scope.discipline,
                            $scope.recert,
                            $scope.loadStatusList[0],
                            $scope.isPho,
                            $scope.patientTaskKey,
                            $scope.isTransitionPatient
                        );
                    }
                });

                //Need to rebuild the modal if the frequencies are deleted
                $scope.$on('oss-grid:frequencies-deleted', function(event, discipline){
                    if(discipline === $scope.discipline) {
                        $scope.currentOrderFrequencies = [];
                        $scope.items = [];
                        $scope.tempItems = [];
                        $scope.currentFrequencyString = '';

                        if($scope.oasisMode === 'false') {
                            $scope.encodedFrequencyString = '';
                        }

                        $scope.prn = {
                            count: 0,
                            reason: ''
                        };
                        $scope.items = $scope.getDefaultEmptyModal();
                    }
                });

                //Opens modal
                $scope.open = function() {
                    $scope.loadingCurrentOrder = true;
                    $scope.submissionError = {error: false, text: ''};

                    $modal({
                        backdrop: 'static',
                        scope: $scope.$new(),
                        template: '/EHR/scripts/directives/kinnser/oss-modal/oss-modal-template.html'
                    });

                    $scope.loadingCurrentOrder = false;

                    $scope.sortFrequencies();

                    if ($scope.items.length === $scope.maxRowIndex + 1) {
                        if ($scope.items[$scope.maxRowIndex].frequencyObject.effectiveDate) {
                            $scope.items[$scope.maxRowIndex].showAdd = false;
                        } else {
                            $scope.items[$scope.items.length - 2].showAdd = true;
                        }
                    } else {
                        $scope.items[$scope.items.length - 2].showAdd = true;
                    }
                }

                //Populates the modal based on provided episodeFrequency objects
                $scope.populateModal = function(frequencies){
                    $scope.$emit('oss-modal:frequencies-count-changed', {
                        discipline: $scope.discipline,
                        count: frequencies.length
                    });

                    $scope.discontinuedItems = [];
                    $scope.discontinuedIndexes = [];
                    $scope.loadingCurrentOrder = true;
                    $scope.tempItems = [];

                    $scope.prn.count = frequencies[0].PRN;
                    $scope.prn.reason = frequencies[0].PRNReason;
                    $scope.prnReason = frequencies[0].PRNReason;    //This goes to hidden form inputs on the grid

                    $scope.submissionError = {error: false, text: ''};

                    angular.forEach(frequencies, function(item, index){
                        var discontinued = false;
                        item.occurrenceMin = item.occurrenceMin === 0 ? '' : item.occurrenceMin;

                        // No discontinue date means it isn't "truly" discontinued
                        if (item.discontinueDate !== '') {
                            discontinued = item.listFrequencyStatusKey === CONSTANTS.currentStatusKey 
                                        && item.discontinueFlag
                                        && !item.discontinuedNotSaved;
                        }

                        //Discontinued items should not show in the modal
                        discontinued ? $scope.discontinuedItems.push($scope.calcNewItem(item)) : $scope.tempItems.push($scope.calcNewItem(item));
                        discontinued ? $scope.discontinuedIndexes.push(index) : '';
                    });

                    $scope.items = $scope.tempItems;    //Use temp swap to avoid repeatedly setting off watchers as we insert items one at a time

                    // hack to prevent "$scope.items[$scope.items.length-1].showAdd = true;" from failing when DCing a
                    // freq to the start of the episode
                    if ($scope.items.length !== 0) {
                        $scope.maxVisibleIndex = $scope.items.length - 1;

                        if($scope.items.length-1 < $scope.maxRowIndex){ //If fewer than max number of items inserted, add buffer and show the add row button on the last item
                            $scope.items[$scope.items.length-1].showAdd = true;
                            $scope.addBufferRow();
                        }

                        $scope.setStatusBar();
                    } else {
                        $scope.items = $scope.getDefaultEmptyModal();
                    }
                }

                //Helper function to take a frequency object and turn it into an item row for $scope.items
                $scope.calcNewItem = function(frequency){
                    var item = {display: true, showAdd: false, valid: true, validBack: true, disabled: false, decoded: true, wwNum: 0, frequencyObject: frequency};
                    item.frequencyObject.effectiveDate = moment(item.frequencyObject.effectiveDate).format("MM/DD/YYYY");
                    item.wwNum = OssModalService.calcWorkWeekNumber(item.frequencyObject.effectiveDate, $scope.episode);
                    item.disabled = item.frequencyObject.listFrequencyStatusKey == 2
                                 || item.disabled
                                 || item.duplicatesCurrent
                                 || angular.isDefined(item.frequencyObject.disabled);

                    return item;
                };

                //Disable the 'new' frequencies which were already present in current frequencies
                $scope.disableMatchingNew = function(newFreq, currentFreq){
                    newFreq.forEach(function(item, index){
                        if( angular.isDefined(currentFreq[index]) ){
                            if(
                                (
                                    currentFreq[index].frequencyString === item.frequencyString
                                    && currentFreq[index].effectiveDate === item.effectiveDate
                                )
                                || item.duplicatesCurrent
                            ){
                                item.disabled = true;
                            }
                        }
                    })
                };

                function getLoadStatusList() {
                    var result;

                    // Physician order pulls in all freqs
                    if ($scope.isPhysicianOrder === 'true') {
                        result = ['2', '1,3,4,5,6'];
                    }

                    // ROC/SOC, pull current first, if oasis saved exist overwrite
                    else if ($scope.oasisMode === "true") {
                        result = ['2', '3'];
                    }

                    // File new physician order, get the current, no new frequencies
                    else if ($scope.isNewOrder === "true") {
                        result = ['2'];
                    }

                    // Edit physician order, get current and pull in new
                    else {
                        result = ['2', $scope.getFrequencyStatusKey()];
                    }

                    return result;
                }

                function getFrequencyStatusKey() {
                    var newStatusKey = '1';

                    if (angular.isDefined($scope.disciplineType)) {
                        var statusKeyLookup = {
                            '3': '4', // discipline type is PT Eval/Re-Eval --> flag is PTNew
                            '6': '5', // discipline type is OT Eval/Re-Eval --> flag is OTNew
                            '7': '6'  // discipline type is ST Eval/Re-Eval --> flag is STNew
                        };
                        newStatusKey = statusKeyLookup[$scope.disciplineType] || newStatusKey;
                    }

                    return newStatusKey;
                }

                function resetSortedIndexes() {
                    $scope.sorted = [];

                    for (var i = 0; i <= $scope.maxRowIndex; i++) {
                        $scope.sorted.push(true);
                    }
                }
            }]
		};
	};
}) ();

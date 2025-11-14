(function() {
    'use strict';

    var OssModalService = angular
        .module('directives.kinnser.oss-modal.oss-modal-service', [
            'resources.episodeFrequency'
        ])
        .constant('kOssModalServiceConstants', {
            listFrequencyStatus: {
                New: 1,
                Current: 2,
                OasisNew: 3,
                PTNew: 4,
                OTNew: 5,
                STNew: 6
            }
        });

    OssModalService.factory('OssModalService', [
        'EpisodeFrequency',
        'ListFrequency',
        'ListInterval',
        '$filter',
        '$q',
        'kOssModalServiceConstants',
    function(EpisodeFrequency, ListFrequency, ListInterval, $filter, $q, CONSTANTS) {
        var frequencyOptions = [];
        var intervalOptions = [];

        OssModalService.frequencies = {};
        OssModalService.frequencyKeys = {};
        OssModalService.forcedBlankRows = {SN: false, PT: false, OT: false, ST: false, HHA: false, MSW: false};

        var disciplines = ['SN', 'PT', 'OT', 'ST', 'HHA', 'MSW'];

        for(var i = 0; i < disciplines.length; i++){
            OssModalService.frequencies[disciplines[i] + 'NewFrequencyModel'] = {};
            OssModalService.frequencies[disciplines[i] + 'NewFrequencyModelPHO'] = {};
            OssModalService.frequencies[disciplines[i] + 'CurrentFrequencyModel'] = {};
            OssModalService.frequencies[disciplines[i] + 'CurrentFrequencyModelPHO'] = {};

            OssModalService.frequencyKeys[disciplines[i] + 'NewFrequencyKeys'] = '';
            OssModalService.frequencyKeys[disciplines[i] + 'NewFrequencyKeysPHO'] = '';
            OssModalService.frequencyKeys[disciplines[i] + 'CurrentFrequencyKeys'] = '';
            OssModalService.frequencyKeys[disciplines[i] + 'CurrentFrequencyKeysPHO'] = '';
        }

        /********* Functions for retreiving data ********/

        OssModalService.getListData = function(){
            var deferred = $q.defer();

            ListFrequency.getListFrequency().then(function(result){
                angular.forEach(result, function(value, key){
                    if(key !== '0'){
                        value.plural = value.frequency.toLowerCase() + 's';
                        frequencyOptions.push(value);
                    }   
                });

                ListInterval.getListInterval().then(function(result){
                    angular.forEach(result, function(value){
                        intervalOptions.push(value);
                    });

                    deferred.resolve({
                        frequencyOptions: frequencyOptions,
                        intervalOptions: intervalOptions
                    });

                });
            });

            return deferred.promise;
        }

        OssModalService.getEpisodeFrequencies = function getEpisodeFrequencies(
            episodeKey,
            taskType,
            discipline,
            status,
            recert,
            isPho,
            episode,
            isTransitionPatient
        ) {
            var currentOrderFrequencyKeys = '';
            var deferred = $q.defer();
            var frequencies = [];
            var tempArr = [];

            var freqType = status === '1' ? 'New' : 'Current';    //Only status of 'new' should default save to the new episode frequency models
            var phoFreq = isPho === 'true' ? 'PHO' : '';
            var pending = 0;

            if (recert === 'true' && !eval(isTransitionPatient)) {
                pending = 1;
            }

            EpisodeFrequency.getEpisodeFrequencyByTaskType(episodeKey, taskType, status, pending).then(function(data){
                angular.forEach(data, function(item){
                    item.effectiveDate = moment(item.effectiveDate).format("MM/DD/YYYY");
                    item.discontinueDate = item.discontinueDate === '' ? '' : moment(item.discontinueDate).format("MM/DD/YYYY");
                    item.frequencyEnd = OssModalService.calcFreqEnd(item, episode);

                    frequencies.push(item);
                    tempArr.push(item.episodeFrequencyKey);
                });

                OssModalService.frequencyKeys[discipline + freqType + 'FrequencyKeys' + phoFreq] = tempArr.join(","); 

                if(data.length > 0){    //SOC/ROC pulls in 'current' freqs first, 'oasis saved' second, should not overwrite 'current' freqs if there are no 'oasis saved' 
                    OssModalService.frequencies[discipline + freqType + 'FrequencyModel' + phoFreq] = data;
                }

                deferred.resolve({keys: currentOrderFrequencyKeys, model: frequencies});
            });

            return deferred.promise;
        }

        OssModalService.retrieveEpisodeFrequencies = function(discipline, status, isPho){
            var phoFreq = isPho === 'true' ? 'PHO' : '';
            return OssModalService.frequencies[discipline + status + 'FrequencyModel' + phoFreq];
        }

        OssModalService.retrieveEpisodeFrequencyKeys = function(discipline, status, isPho){
            var phoFreq = isPho === 'true' ? 'PHO' : '';
            return OssModalService.frequencyKeys[discipline + status + 'FrequencyKeys' + phoFreq];
        }

        OssModalService.retrieveEpisodeNewFrequencies = function(discipline, isPho){
            var frequencies = OssModalService.retrieveEpisodeFrequencies(discipline, 'New', isPho);
            return Array.isArray(frequencies) ? frequencies : [];
        }

        OssModalService.retrieveEpisodeCurrentFrequencies = function(discipline, isPho){
            var frequencies = OssModalService.retrieveEpisodeFrequencies(discipline, 'Current', isPho);
            return Array.isArray(frequencies) ? frequencies : [];
        }

        OssModalService.clearEpisodeFrequencies = function(discipline, isPho){
            var phoFreq = isPho === 'true' ? 'PHO' : '';
            ['New', 'Current'].forEach(function(status) {
                OssModalService.frequencies[discipline + status + 'FrequencyModel' + phoFreq] = {};
                OssModalService.frequencyKeys[discipline + status + 'FrequencyKeys' + phoFreq] = '';
            });
        }

        //Discontinuing via modal
        OssModalService.discontinueFrequencies = function(discipline, discontinueDate, discontinueReason, episode, isPho){
            var frequencies = OssModalService.retrieveEpisodeFrequencies(discipline, 'Current', isPho);

            frequencies.forEach(function(item, index){
                if (item.listFrequencyStatusKey === 2 || item.duplicatesCurrent) {
                    OssModalService.discLogic(item, discontinueReason, discontinueDate);
                    item.discontinuedNotSaved = true;
                }
            });
        }

        OssModalService.discLogic = function(freq, discontinueReason, discontinueDate){
            if( moment(discontinueDate).diff(moment(freq.effectiveDate)) <= 0 ){
                freq.discontinueFlag = true;
                freq.discontinueDate = freq.discontinueDate === '' ? discontinueDate : freq.discontinueDate;
                freq.discontinueReason = freq.discontinueReason === '' ? discontinueReason : freq.discontinueReason;
            } else if( moment(discontinueDate).diff(moment(freq.frequencyEnd)) < 0 ){
                freq.discontinueFlag = false;
                freq.discontinueDate = freq.discontinueDate === '' ? discontinueDate : freq.discontinueDate;
                freq.discontinueReason = freq.discontinueReason === '' ? discontinueReason : freq.discontinueReason;
            }
        }

        OssModalService.saveEpisodeFrequencies = function saveEpisodeFrequencies(
            episodeKey,
            frequencies,
            discipline,
            recert,
            status,
            isPho,
            patientTaskKey,
            isTransitionPatient
        ) {
            var tempArr = [];
            var newOrderFrequencyKeys = '';
            var deferred = $q.defer();
            var CURRENT_STATUS = 2;

            //All modal saves should be done with null/0 EpisodeFrequency keys so that a new table insertion is made
            angular.forEach(frequencies, function(item, index){
                item.active = 0;
                item.pending = false;

                if (recert === 'true' && !eval(isTransitionPatient)) {
                    item.pending = true;
                }

                item.episodeKey = episodeKey;
                item.episodeFrequencyKey = 0;
                item.FrequencyEndDate = '01/25/1998';       //Setting a date just so the save will work, doesn't persist anywhere
                item.updatedBy = patientTaskKey;
                item.patientTaskKey = item.patientTaskKey || patientTaskKey;

                if (item.listFrequencyStatusKey === CURRENT_STATUS) {
                    item.DuplicatesCurrent = 1;
                }

            });

            //Save and then re-update the grid model and generate a new list of frequency keys, these will be set to active if the Oasis/Physician Order is saved
            EpisodeFrequency.saveEpisodeFrequency({data: frequencies}).then(function(data){
                frequencies = data;
                angular.forEach(frequencies, function(item, index){
                    tempArr.push(item.episodeFrequencyKey);
                });

                //Clean this up
                if(status === "1"){
                    var temp2 = '';
                    var temp = OssModalService.frequencyKeys[discipline + 'NewFrequencyKeys'].split(",");
                    temp2 += OssModalService.frequencyKeys[discipline + 'CurrentFrequencyKeys'] === '' ? '' + temp.join(",") : ',' + temp.join(",");
                    OssModalService.frequencyKeys[discipline + 'CurrentFrequencyKeys'] = temp2;
                }

                var phoFreq = '';

                if(isPho === 'true'){
                    var phoFreq = 'PHO'
                }

                OssModalService.frequencyKeys[discipline + 'CurrentFrequencyKeys' + phoFreq] +=  ',' + OssModalService.frequencyKeys[discipline + 'NewFrequencyKeys' + phoFreq]; 

                OssModalService.frequencyKeys[discipline + 'NewFrequencyKeys' + phoFreq] = tempArr.join(",");
                OssModalService.frequencies[discipline + 'FrequencyModel'] = frequencies;

                deferred.resolve(newOrderFrequencyKeys);
            });

            return deferred.promise;
        }

        /******* Functions for manipulating/checking data *********/

        //Converts a single modal row into a piece of the overall frequency string
        OssModalService.calcNewFrequency = function(frequency, frequencyRanges){
            var string = frequencyRanges && frequency.occurrenceMin > 0 ? frequency.occurrenceMin + '-' + frequency.occurrenceMax : frequency.occurrenceMax;
            string += frequency.listIntervalKey === 2 ? 'qo' : '';
            frequency.listFrequencyKey === 2 ? string += 'da' : frequency.listFrequencyKey === 3 ? string += 'w' : string += 'm';
            string += frequency.duration;

            return string;
        };

        //Finds which work week the effective date falls into
        OssModalService.calcWorkWeekNumber = function(date, episode){
            var wwNum = '';
            angular.forEach(episode, function(item, index){
                var end = angular.isDefined(item.lastWeekEnd) ? item.lastWeekEnd : item.end;    //If this is the final week in the episode compare against the work week end date
                if(moment(date).diff(moment(item.start), 'days') >= 0 && moment(date).diff(moment(end), 'days') <= 0){
                    wwNum = episode[index].weekNumber;
                }
            })

            return wwNum;
        }

        //Calculates a frequency objects end date (effective date + range)
        OssModalService.calcRangeEnd = function(frequency) {
            return moment(frequency.effectiveDate)
                .add(parseInt(frequency.duration), frequencyOptions[frequency.listFrequencyKey - 2].plural)
                .format('MM/DD/YYYY');
        };

        //Returns the actual frequency end date by taking into account the work week start/end dates
        OssModalService.calcFreqEnd = function(freq, episode){
            var duration = freq.duration || 0;

            if(parseInt(duration) !== 0){
                if(freq.listFrequencyKey === 3){  //Weekly frequencies need to terminate at the end of work weeks
                    var workWeekNum = OssModalService.calcWorkWeekNumber(OssModalService.calcRangeEnd(freq), episode);
                    //If the range extends beyond the episode...
                    if(!angular.isDefined(episode[workWeekNum - 2])){
                        var diff = moment(OssModalService.calcRangeEnd(freq)).diff(episode[episode.length-1].lastWeekEnd, 'days');
                        //If it ends less than a week after episode end date it means the episode is full and ends on the episode end date
                        if(diff >= 0 && diff <= 7){
                            return episode[episode.length-1].end;
                        }
                        //Otherwise the episode is over scheduled and the range end date is returned
                        return OssModalService.calcRangeEnd(freq);
                    }
                    //If it doesn't, return the end date of the work week it fills
                    return episode[workWeekNum - 2].end;
                }else if(freq.listFrequencyKey === 2){
                    return moment(freq.effectiveDate).add(parseInt(duration) - 1, frequencyOptions[freq.listFrequencyKey-2].plural).format('MM/DD/YYYY');  //Non-weekly frequqencies terminate anywhere in a work week, no extra logic
                }else{
                    return moment(freq.effectiveDate).add(parseInt(30 * duration) - 1, 'days').format('MM/DD/YYYY');
                }
            }else{
                return moment(freq.effectiveDate).add(-1, 'days').format('MM/DD/YYYY');
            }
        };

        //Checks if an effective date is valid
        OssModalService.validEffectiveDate = function(date, episodeStart){
            if(date === null || date === ''){
                return false;
            }else{
                return moment(date).diff(episodeStart, 'days') >= 0 ? true : false;
            }
        };

        //Checks if necessary to use the start of a work week
        OssModalService.useWorkWeekStart = function(prevRow, newRow, episode){
            var previousRowEndDate;
            var weekNumber;
            var result = false;

            if (prevRow.listFrequencyKey === 3) {
                previousRowEndDate = OssModalService.calcRangeEnd(prevRow);
                weekNumber = OssModalService.calcWorkWeekNumber(previousRowEndDate, episode);

                if (weekNumber != 0) {
                    result = moment(episode[weekNumber - 1].start).format('MM/DD/YYYY');
                }
            }

            return result;
        }

        OssModalService.validateFrequencies = function(frequencies, maxIndex, ranges, prnCount, episodeStart, episodeEnd, validDuration, episode){
            var valid, zeroFreq, backValid, validChars, result;
            valid = zeroFreq = backValid = validChars = true;

            result = {error: false, text: ''};

            for(var i = 0; i <= maxIndex; i++){
                //Check that no frequency dates are earlier than the episode start date
                valid = frequencies[i].valid ? valid && true : false;

                //Duration/occurrences cannot be zero
                zeroFreq = parseInt(frequencies[i].frequencyObject.duration) === 0 ? false : zeroFreq && true; 
                zeroFreq = parseInt(frequencies[i].frequencyObject.occurrenceMax) === 0 ? false : zeroFreq && true; 
                zeroFreq = ranges === 'true' ? frequencies[i].frequencyObject.occurrenceMin === 0 ? false : zeroFreq && true : zeroFreq && true;

                //Frequency will not be marked as validBack if it has been illegally backdated
                backValid = frequencies[i].validBack && backValid;

                //No special characters in numerical fields
                validChars = !/[^0-9]/.test( frequencies[i].frequencyObject.occurrenceMax ) && validChars;
                validChars = !/[^0-9]/.test( frequencies[i].frequencyObject.occurrenceMin ) && validChars;
                validChars = !/[^0-9]/.test( frequencies[i].frequencyObject.duration ) && validChars;
            }

            validChars = !/[^0-9]/.test( prnCount ) && validChars;

            if(!validChars){
                result.error = true;
                result.text = 'Please only use numeric values occurrences, duration, and PRN visits';
            }

            if(!zeroFreq){
                result.error = true;
                result.text = 'You cannot submit a frequency with a duration or occurrence count of zero.';
            }

            if(!backValid){
                result.error = true;
                result.text = 'You cannot backdate orders into the range of a previous frequency.';
            }

            if(!valid){
                result.error = true;
                result.text = 'You have an effective date that is earlier than the episode start date. (' + episodeStart + ')';
            }

            if(!validDuration){
                result.error = true;
                result.text = 'The range of this frequency extends beyond the episode end date. (' + episodeEnd + ')';
            }

            if (OssModalService.haveOverlappingVisits(frequencies, episode)) {
                result.error = true;
                result.text = 'This patient is scheduled with overlapping visit frequencies for this discipline. ' +
                    'Please update your frequencies accordingly.';
            }

            return result;

        }

        OssModalService.haveOverlappingVisits = function haveOverlappingVisits(frequencies, episode) {
            var start;
            var end;
            var toCompareStart;
            var toCompareEnd;
            var overlap = false;

            var freqs = frequencies.filter(function(item) {
                return (
                    item.frequencyObject.effectiveDate
                    && item.frequencyObject.duration
                    && !item.frequencyObject.discontinueFlag
                );
            });

            if (freqs.length >= 2) {
                for (var i = 0; i < freqs.length - 1; i++) {
                    if (!overlap) {
                        start = moment(freqs[i].frequencyObject.effectiveDate).unix();
                        end = freqs[i].frequencyObject.discontinueDate
                            ? moment(freqs[i].frequencyObject.discontinueDate).unix()
                            : moment(OssModalService.calcFreqEnd(freqs[i].frequencyObject, episode)).unix();

                        for (var j = i + 1; j < freqs.length; j++) {
                            toCompareStart = moment(freqs[j].frequencyObject.effectiveDate).unix();
                            toCompareEnd = freqs[j].frequencyObject.discontinueDate
                                ? moment(freqs[j].frequencyObject.discontinueDate).unix()
                                : moment(OssModalService.calcFreqEnd(freqs[j].frequencyObject, episode)).unix();

                            if (start <= toCompareEnd && end >= toCompareStart) {
                                overlap = true;
                            }
                        }
                    }
                }
            }

            return overlap;
        };

        OssModalService.deleteFrequencies = function deleteFrequencies(discipline, isPho) {
            var frequencies = OssModalService.retrieveEpisodeNewFrequencies(discipline, isPho);
            frequencies = frequencies.concat(OssModalService.retrieveEpisodeCurrentFrequencies(discipline, isPho));

            var frequencyKeysList = frequencies
                .map(function(freq) { return freq.episodeFrequencyKey })
                .join(',');

            return EpisodeFrequency.updateEpisodeFrequencyActive(frequencyKeysList, 0);
        }

        OssModalService.setForcedBlankRow = function setForcedBlankRow(taskTypeKey, value) {
            var taskTypesLookup = {
                '1': 'SN',
                '3': 'PT',
                '6': 'OT',
                '7': 'ST',
                '4': 'HHA',
                '8': 'MSW'
            };
            var key = taskTypesLookup[taskTypeKey];

            OssModalService.forcedBlankRows[key] = value;
        }

        OssModalService.getEpisodeFrequencyByPatientTask = function getEpisodeFrequencyByPatientTask(
            patientTaskKey,
            active
        ) {
            return EpisodeFrequency.getEpisodeFrequencyByPatientTask(patientTaskKey, active);
        }

        OssModalService.getFrequenciesString = function getFrequenciesString(frequencies, frequencyRanges) {
            var resultString = '';

            if (frequencies.length) {
                var head = frequencies[0];
                var tail = frequencies.slice(1);
                var tailStrings = [];


                var headString = 'Eff. ' + head.effectiveDate + ' ' + OssModalService.calcNewFrequency(head, frequencyRanges);
                if (head.discontinueDate) {
                    headString += ', Eff. ' + moment(head.discontinueDate).format('MM/DD/YYYY') + ' Discontinued';
                }

                tailStrings = tail
                    .filter(function(freq) { return !freq.discontinueFlag; })
                    .map(function(freq) {
                        var string = ', Eff. '
                            + freq.effectiveDate
                            + ' '
                            + OssModalService.calcNewFrequency(freq, frequencyRanges);

                        if (freq.discontinueDate) {
                            string += ', Eff. ' + moment(freq.discontinueDate).format('MM/DD/YYYY') + ' Discontinued';
                        }

                        return string;
                    });

                resultString = [headString]
                    .concat(tailStrings)
                    .join('')
                    + ', PRN: ' + head.PRN;
            }

            return resultString;
        }

        return OssModalService;
    }]);
})();

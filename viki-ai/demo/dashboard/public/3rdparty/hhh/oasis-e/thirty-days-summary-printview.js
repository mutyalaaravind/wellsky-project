(function() {

    'use strict';

    angular.module('am-thirty-days-summary-printview',
        [
            'directives.kinnser.am-print-view.page-builder-new'
        ])
    .constant('AM30dsTaskPrintConstants', {
        
    })
    .controller('AM30dsTaskPrintviewController',  AM30dsTaskPrintviewController);
    
    AM30dsTaskPrintviewController.$inject = [
        '$rootScope',
        '$route',
        '$location',
        'pvObjects',
        'AM30dsTaskPrintConstants'
    ];
    
    function AM30dsTaskPrintviewController(
        $rootScope,
        $route,
        $location,
        pvObjects,
        AM30dsTaskPrintConstants
    ) {
        var am30dspv = angular.extend(this, { 
            // members
            serviceData: '',
            mockData: '--',

            // methods
            initialize: initialize,
            getHospitalizationSection: getHospitalizationSection,
            getAcutePhysicianVisitSection: getAcutePhysicianVisitSection,
            getUpdateNeededCurrDiagnosisSection: getUpdateNeededCurrDiagnosisSection,
            getUpdateNeededNewDiagnosisSection: getUpdateNeededNewDiagnosisSection,
            getGoalProgressSection: getGoalProgressSection,
            getPrimaryFocusSection: getPrimaryFocusSection,
            getFollowUpPlansSection: getFollowUpPlansSection,
            getBottomData: getBottomData
        });

        pvObjects.resetAll();
        var currentSectionIndex = 0;
        
        function initialize(serviceData) {
            am30dspv.serviceData = serviceData.DATA;
	        $rootScope.print = true;
	        am30dspv.boot = [];
            am30dspv.idSuffix = "";

            getHeader(am30dspv.serviceData.headerSection);
            am30dspv.boot.push(am30dspv.getHospitalizationSection(currentSectionIndex++));
            am30dspv.boot.push(am30dspv.getAcutePhysicianVisitSection(currentSectionIndex++));
            am30dspv.boot.push(am30dspv.getUpdateNeededCurrDiagnosisSection(currentSectionIndex++));
            am30dspv.boot.push(am30dspv.getUpdateNeededNewDiagnosisSection(currentSectionIndex++));
            am30dspv.boot.push(am30dspv.getGoalProgressSection(currentSectionIndex++));
            am30dspv.boot.push(am30dspv.getPrimaryFocusSection(currentSectionIndex++));
            am30dspv.boot.push(am30dspv.getFollowUpPlansSection(currentSectionIndex++));
            am30dspv.boot.push(am30dspv.getBottomData(currentSectionIndex++));
        }

        function validateObjectProperties(value) {
	        return value === 'undefined' || value == null || value === '';
        }

        function getYesNoOrUnset(value) {
            var yesNoOrUnset;

            if (value === 'YES') {
                yesNoOrUnset = 'Yes';
            } else if (value === 'NO') {
                yesNoOrUnset = 'No';
            } else {
                yesNoOrUnset = am30dspv.mockData;
            }
            
            return yesNoOrUnset;
        }
        
        function getHeader(headerSection) {
	        am30dspv.orderNumber = 0;
            am30dspv.pageTitle = {
	            title: "30-DAY SUMMARY",
                taskName: (validateObjectProperties(headerSection.thirtyDaysSummaryName)) ? am30dspv.mockData : headerSection.thirtyDaysSummaryName,
	            patientTaskKey: (validateObjectProperties(headerSection.patientTaskKey)) ? am30dspv.mockData : headerSection.patientTaskKey,
                patientName: ((validateObjectProperties(headerSection.patientLastName)) ? am30dspv.mockData : headerSection.patientLastName) + ", " + ((validateObjectProperties(headerSection.patientFirstName)) ? "" : headerSection.patientFirstName),
                patientMedicalRecordKey: (validateObjectProperties(headerSection.patientmedicalrecordkey)) ?  am30dspv.mockData : headerSection.patientmedicalrecordkey,
                episodeForSummary: (validateObjectProperties(headerSection.episodeForSummary)) ? '' : headerSection.episodeForSummary,
                dateOfSummary: (validateObjectProperties(headerSection.dateOfSummary)) ? '' : headerSection.dateOfSummary,
	            clinicName: (validateObjectProperties(headerSection.clinicName)) ? am30dspv.mockData : headerSection.clinicName,
	            clinicAddressone: (validateObjectProperties(headerSection.clinicAddressone)) ?   am30dspv.mockData : headerSection.clinicAddressone,
	            clinicCity: (validateObjectProperties(headerSection.clinicCity)) ? am30dspv.mockData : headerSection.clinicCity,
	            clinicState: (validateObjectProperties(headerSection.clinicState)) ? am30dspv.mockData : headerSection.clinicState,
	            clinicZipcode: (validateObjectProperties(headerSection.clinicZipcode)) ? am30dspv.mockData : headerSection.clinicZipcode,
                clinicPhone: (validateObjectProperties(headerSection.clinicPhone)) ? am30dspv.mockData : headerSection.clinicPhone,
                clinicFax: ((validateObjectProperties(headerSection.clinicFax)) ? am30dspv.mockData : headerSection.clinicFax)
	        };
        }
        
        function getHospitalizationSection(currentSectionIndex) {
	        var hospitalizationSection = {
	            sectionIndex: currentSectionIndex,
	            header: 'Patient Status',
	            row: []
            };

            var hospitalization = getYesNoOrUnset(am30dspv.serviceData.hospitalizationSection.hospitalization);
            var hospitalizationDate = validateObjectProperties(am30dspv.serviceData.hospitalizationSection.hospitalizationDate) ? '' : am30dspv.serviceData.hospitalizationSection.hospitalizationDate;
            var hospitalizationReason = validateObjectProperties(am30dspv.serviceData.hospitalizationSection.hospitalizationReason) ? '' : am30dspv.serviceData.hospitalizationSection.hospitalizationReason;

            hospitalizationSection.row.push({
                rowIndex: 1,
                layout: 'twoColumn-twoCell-t6',
                rowTopMargin: true,
                dynamicHeight: true,
                columns: [
                    {
                        index: 1,
                        cells: [{
                            index: 1,
                            body: '<b>Hospitalization? </b>' + hospitalization
                        }]
                    },
                    {
                        index: 2,
                        cells: [{
                            index: 1,
                            body: '<b>Date: </b>' + hospitalizationDate
                        }]
                    }
                ]
            });
            
            hospitalizationSection.row.push({
	            rowIndex: 1,
	            layout: 'oneColumn-oneCell-t1',
                rowTopMargin: false,
                dynamicHeight: true,
	            columns: [{
	                index: 1,
	                cells: [{
	                    index: 1,
                        title: 'Reason: ',
                        body: hospitalizationReason
	                }]
	            }]
	        });
            
	        return hospitalizationSection;
        }
        
        function getAcutePhysicianVisitSection(currentSectionIndex) {
	        var acutePhysicianVisitSection = {
	            sectionIndex: currentSectionIndex,
	            header: '',
	            row: []
            };

            var acutePhysicianVisit = getYesNoOrUnset(am30dspv.serviceData.acutePhysicianVisitSection.acutePhysicianVisit);
            var acutePhysicianVisitDate = validateObjectProperties(am30dspv.serviceData.acutePhysicianVisitSection.acutePhysicianVisitDate) ? '' : am30dspv.serviceData.acutePhysicianVisitSection.acutePhysicianVisitDate;
            var acutePhysicianVisitReason = validateObjectProperties(am30dspv.serviceData.acutePhysicianVisitSection.acutePhysicianVisitReason) ? '' : am30dspv.serviceData.acutePhysicianVisitSection.acutePhysicianVisitReason;
            
	        acutePhysicianVisitSection.row.push({
                rowIndex: 1,
                layout: 'twoColumn-twoCell-t6',
                rowTopMargin: true,
                dynamicHeight: true,
                columns: [
                    {
                        index: 1,
                        cells: [{
                            index: 1,
                            body: '<b>Acute Physician Visit? </b>' + acutePhysicianVisit
                        }]
                    },
                    {
                        index: 2,
                        cells: [{
                            index: 1,
                            body: '<b>Date: </b>' + acutePhysicianVisitDate
                        }]
                    }
                ]
            });

            acutePhysicianVisitSection.row.push({
	            rowIndex: 1,
	            layout: 'oneColumn-oneCell-t1',
                rowTopMargin: false,
                dynamicHeight: true,
	            columns: [{
	                index: 1,
	                cells: [{
	                    index: 1,
                        title: 'Reason: ',
	                    body: acutePhysicianVisitReason
	                }]
	            }]
	        });
            
	        return acutePhysicianVisitSection;
        }
        
        function getUpdateNeededCurrDiagnosisSection(currentSectionIndex) {
	        var updatesNeededCurrDiagnosisSection = {
	            sectionIndex: currentSectionIndex,
	            header: '',
	            row: []
            };

            var updatesNeededCurrDiagnosis = getYesNoOrUnset(am30dspv.serviceData.updatesNeededCurrDiagnosisSection.updatesNeededCurrDiagnosis);
            var updatesNeededCurrDiagnosisText = validateObjectProperties(am30dspv.serviceData.updatesNeededCurrDiagnosisSection.updatesNeededCurrDiagnosisText) ? '' : am30dspv.serviceData.updatesNeededCurrDiagnosisSection.updatesNeededCurrDiagnosisText;

            updatesNeededCurrDiagnosisSection.row.push({
                rowIndex: 1,
                layout: 'twoColumn-twoCell-t6',
                rowTopMargin: true,
                dynamicHeight: true,
                columns: [
                    {
                        index: 1,
                        cells: [{
                            index: 1,
                            body: '<b>Any updates needed for current diagnoses? </b>' + updatesNeededCurrDiagnosis
                        }]
                    },
                    {
                        index: 2,
                        cells: [
                            {
                                index: 1,
                                title: '',
                                body: ''
                            }
                        ]
                    }
                ]
            });
            
            updatesNeededCurrDiagnosisSection.row.push({
	            rowIndex: 1,
	            layout: 'oneColumn-oneCell-t1',
                rowTopMargin: false,
                dynamicHeight: true,
	            columns: [{
	                index: 1,
	                cells: [{
	                    index: 1,
                        title: 'Explanation: ',
                        body: updatesNeededCurrDiagnosisText
	                }]
	            }]
	        });
            
	        return updatesNeededCurrDiagnosisSection;
        }

        function getUpdateNeededNewDiagnosisSection(currentSectionIndex) {
	        var updatesNeededNewDiagnosisSection = {
	            sectionIndex: currentSectionIndex,
	            header: '',
	            row: []
            };

            var updatesNeededNewDiagnosis = getYesNoOrUnset(am30dspv.serviceData.updatesNeededNewDiagnosisSection.updatesNeededNewDiagnosis);
            var updatesNeededNewDiagnosisText = validateObjectProperties(am30dspv.serviceData.updatesNeededNewDiagnosisSection.updatesNeededNewDiagnosisText) ? '' : am30dspv.serviceData.updatesNeededNewDiagnosisSection.updatesNeededNewDiagnosisText;
            
            updatesNeededNewDiagnosisSection.row.push({
                rowIndex: 1,
                layout: 'oneColumn-oneCell-t1',
                rowTopMargin: true,
                dynamicHeight: true,
                columns: [
                    {
                        index: 1,
                        cells: [{
                            index: 1,
                            body: '<b>Any updates needed for new diagnoses? </b>' + updatesNeededNewDiagnosis
                        }]
                    }
                ]
            });
            
            updatesNeededNewDiagnosisSection.row.push({
	            rowIndex: 1,
	            layout: 'oneColumn-oneCell-t1',
                rowTopMargin: false,
                dynamicHeight: true,
	            columns: [{
	                index: 1,
	                cells: [{
	                    index: 1,
                        title: 'Explanation: ',
                        body: updatesNeededNewDiagnosisText
	                }]
	            }]
            });
            
	        return updatesNeededNewDiagnosisSection;
        }

        function getGoalProgressSection(currentSectionIndex) {
	        var goalProgressSection = {
	            sectionIndex: currentSectionIndex,
	            header: '',
	            row: []
            };

            var goalProgress = validateObjectProperties(am30dspv.serviceData.goalProgressSection.goalProgress) ? [] : am30dspv.serviceData.goalProgressSection.goalProgress;
            var checkboxChecked = '<img src="/AM/images/checkbox-selected.png" />';
            var checkboxUnchecked = '<img src="/AM/images/checkbox.png" />';
            var goalProgressImproving;
            var goalProgressStabilizing;
            var goalProgressNotProgressing;
            var goalProgressDeclining;
            var goalProgressOther = am30dspv.serviceData.goalProgressSection.goalProgressOther === 'YES';
            var goalProgressOtherText = validateObjectProperties(am30dspv.serviceData.goalProgressSection.goalProgressOtherText) ? '' : am30dspv.serviceData.goalProgressSection.goalProgressOtherText;
            
            for (var i = 0; i < goalProgress.length; i++) {
                if (goalProgress[i].name === 'Improving') {
                    goalProgressImproving = goalProgress[i].value === 'YES';
                } else if (goalProgress[i].name === 'Stabilizing') {
                    goalProgressStabilizing = goalProgress[i].value === 'YES';
                } else if (goalProgress[i].name === 'NotProgressing') {
                    goalProgressNotProgressing = goalProgress[i].value === 'YES';
                } else if (goalProgress[i].name === 'Declining') {
                    goalProgressDeclining = goalProgress[i].value === 'YES';
                }
            }

            var goalProgressComments = validateObjectProperties(am30dspv.serviceData.goalProgressSection.goalProgressComments) ? '' : am30dspv.serviceData.goalProgressSection.goalProgressComments;

            goalProgressSection.row.push({
	            rowIndex: 1,
	            layout: 'oneColumn-oneCell-t1',
                rowTopMargin: false,
                dynamicHeight: true,
	            columns: [{
	                index: 1,
	                cells: [{
	                    index: 1,
                        body: '<b>Goal Progress: </b>'
	                }]
	            }]
            });

            goalProgressSection.row.push({
                rowIndex: 1,
                layout: 'fourColumn-fourCell-t2',
                rowTopMargin: false,
                dynamicHeight: true,
                columns: [
                    {
                        index: 1,
                        cells: [
                            {
                                index: 1,
                                body: (goalProgressImproving ? checkboxChecked : checkboxUnchecked) + ' Improving'
                            }
                        ]
                    },
                    {
                        index: 2,
                        cells: [
                            {
                                index: 2,
                                body: (goalProgressStabilizing ? checkboxChecked : checkboxUnchecked) + ' Stabilizing'
                            }
                        ]
                    },
                    {
                        index: 3,
                        cells: [
                            {
                                index: 3,
                                body: (goalProgressNotProgressing ? checkboxChecked : checkboxUnchecked) + ' Not progressing'
                            }
                        ]
                    },
                    {
                        index: 4,
                        cells: [
                            {
                                index: 4,
                                body: (goalProgressDeclining ? checkboxChecked : checkboxUnchecked) + ' Declining'
                            }
                        ]
                    }
                ]
            });

            goalProgressSection.row.push({
                rowIndex: 1,
                layout: 'twoColumn-twoCell-t7',
                rowTopMargin: false,
                dynamicHeight: true,
                columns: [
                    {
                        index: 1,
                        cells: [
                            {
                                index: 1,
                                body: (goalProgressOther ? checkboxChecked : checkboxUnchecked) + ' Other'
                            }
                        ]
                    },
                    {
                        index: 2,
                        cells: [
                            {
                                index: 1,
                                body: ''
                            }
                        ]
                    }
                ]
            });

            goalProgressSection.row.push({
	            rowIndex: 1,
	            layout: 'oneColumn-oneCell-t1',
                rowTopMargin: false,
                dynamicHeight: true,
	            columns: [{
	                index: 1,
	                cells: [{
	                    index: 1,
                        title: '',
                        body: goalProgressOtherText
	                }]
	            }]
            });
            
            goalProgressSection.row.push({
	            rowIndex: 1,
	            layout: 'oneColumn-oneCell-t1',
                rowTopMargin: false,
                dynamicHeight: true,
	            columns: [{
	                index: 1,
	                cells: [{
	                    index: 1,
                        title: 'Comments: ',
                        body: goalProgressComments
	                }]
	            }]
            });
            
	        return goalProgressSection;
        }

        function getPrimaryFocusSection(currentSectionIndex) {
	        var primaryFocusSection = {
	            sectionIndex: currentSectionIndex,
	            header: '',
	            row: []
            };

            var primaryFocusText = validateObjectProperties(am30dspv.serviceData.primaryFocusSection.primaryFocusText) ? '' : am30dspv.serviceData.primaryFocusSection.primaryFocusText;

            primaryFocusSection.row.push({
                rowIndex: 1,
                layout: 'oneColumn-oneCell-t1',
                rowTopMargin: true,
                dynamicHeight: true,
                columns: [
                    {
                        index: 1,
                        cells: [{
                            index: 1,
                            body: '<b>What is the primary focus of care for the next 30 days in the episode? </b>',
                        }]
                    }
                ]
            });
            
            primaryFocusSection.row.push({
	            rowIndex: 1,
	            layout: 'oneColumn-oneCell-t1',
                rowTopMargin: false,
                dynamicHeight: true,
	            columns: [{
	                index: 1,
	                cells: [{
	                    index: 1,
                        title: '',
                        body: primaryFocusText
	                }]
	            }]
            });
            
	        return primaryFocusSection;
        }

        function getFollowUpPlansSection(currentSectionIndex) {
	        var followUpPlansSection = {
	            sectionIndex: currentSectionIndex,
	            header: '',
	            row: []
            };

            var followUpPlansText = validateObjectProperties(am30dspv.serviceData.followUpPlansSection.followUpPlansText) ? '' : am30dspv.serviceData.followUpPlansSection.followUpPlansText;

            followUpPlansSection.row.push({
                rowIndex: 1,
                layout: 'oneColumn-oneCell-t1',
                rowTopMargin: true,
                dynamicHeight: true,
                columns: [
                    {
                        index: 1,
                        cells: [{
                            index: 1,
                            body: '<b>Plans for follow-up or change of care recommendations for remainder of episode: </b>',
                        }]
                    }
                ]
            });
            
            followUpPlansSection.row.push({
	            rowIndex: 1,
	            layout: 'oneColumn-oneCell-t1',
                rowTopMargin: false,
                dynamicHeight: true,
	            columns: [{
	                index: 1,
	                cells: [{
	                    index: 1,
                        title: '',
                        body: followUpPlansText
	                }]
	            }]
            });
            
	        return followUpPlansSection;
        }

        function getBottomData(currentSectionIndex) {
            var bottomDataSection = {
	            sectionIndex: currentSectionIndex,
	            row: []
            };

            var clinicianSignature = am30dspv.mockData;
            var clinicianDate = am30dspv.mockData;
            if (!validateObjectProperties(am30dspv.serviceData.bottomDataSection)) {
                clinicianSignature = validateObjectProperties(am30dspv.serviceData.bottomDataSection.clinicianSignature) ? clinicianSignature : am30dspv.serviceData.bottomDataSection.clinicianSignature;
                clinicianDate = validateObjectProperties(am30dspv.serviceData.bottomDataSection.clinicianDate) ? clinicianDate : am30dspv.serviceData.bottomDataSection.clinicianDate;
            }
            
            bottomDataSection.row.push({
	            rowIndex: 1,
	            rowHeader: '',
	            layout: 'twoColumn-twoCell-t1',
	            rowTopMargin: false,
	            dynamicHeight: true,
	            columns: [{
	                index: 1,
	                cells: [{
	                    index: 1,
	                    title: 'Clinician Signature: ',
	                    body: clinicianSignature
	                }]
	            },
	                {
	                    index: 2,
	                    cells: [{
	                        title: 'Date: ',
	                        body: clinicianDate
	                    }]
	                }]
	        });

            return bottomDataSection;
        }
        
    }
    
})(moment);

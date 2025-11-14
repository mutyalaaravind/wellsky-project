(function () {
    'use strict';

    angular.module('am-scic-order-printview',
        [
            'directives.kinnser.am-print-view.page-builder-new',
            'resources.hh-order-resource'
        ])
        .controller('AMSCICOrderPrintviewController', AMSCICOrderPrintviewController);

    AMSCICOrderPrintviewController.$inject = [
    	'$rootScope',
    	'pvObjects'
	];

    function AMSCICOrderPrintviewController(
    	$rootScope, 
    	pvObjects
	) {

        var scicopv = angular.extend(this, {
            serviceData: '',
            mockData: '--',
            initialize: initialize,
            getHeader: getHeader,
            getPatientInformationSection: getPatientInformationSection,
            getRiskProfileSection: getRiskProfileSection,
            getAdvanceDirectives: getAdvanceDirectives,
            getMedicationSection: getMedicationSection,
            getDmeAndSuppliesSection: getDmeAndSuppliesSection,
            getOrdersAndTreatmentsSections: getOrdersAndTreatmentsSections,
            getGoalsAndOutcomes: getGoalsAndOutcomes,
            getBottomData: getBottomData
        });

        pvObjects.resetAll();
        var currentSectionIndex = 0;

        function initialize(serviceData) {
	        scicopv.serviceData = serviceData;
	        $rootScope.print = true;
	        scicopv.boot = [];
	        scicopv.idSuffix = "";
	        getHeader(scicopv.serviceData.HEADERSECTION);
	        scicopv.boot.push(scicopv.getPatientInformationSection(currentSectionIndex++));
	        scicopv.boot.push(scicopv.getRiskProfileSection(currentSectionIndex++));
	        scicopv.boot.push(scicopv.getAdvanceDirectives(currentSectionIndex++));
	        scicopv.boot.push(scicopv.getMedicationSection(currentSectionIndex++));
	        scicopv.boot.push(scicopv.getDmeAndSuppliesSection(currentSectionIndex++));
	        scicopv.boot.push(scicopv.getOrdersAndTreatmentsSections(currentSectionIndex++));
	        scicopv.boot.push(scicopv.getGoalsAndOutcomes(currentSectionIndex++));
	        scicopv.boot.push(scicopv.getBottomData(currentSectionIndex++));
	    }
	
	    function validateObjectProperties(value) {
	        return value === 'undefined' || value == null || value === '';
	    }
	
	    function getHeader(headerSection) {
	        scicopv.orderNumber = (validateObjectProperties(headerSection.PATIENTTASKKEY)) ?  scicopv.mockData : headerSection.PATIENTTASKKEY;
	        scicopv.pageTitle = {
	            title: "Significant Change in Care Order",
	            taskName: (validateObjectProperties(headerSection.POSTHOSPITALORDERNAME)) ? scicopv.mockData : headerSection.POSTHOSPITALORDERNAME,
	            patientTaskDate: (validateObjectProperties(headerSection.PATIENTTASKDATE)) ? scicopv.mockData : headerSection.PATIENTTASKDATE,
				patientTaskKey: (validateObjectProperties(headerSection.PATIENTTASKKEY)) ? scicopv.mockData : headerSection.PATIENTTASKKEY,
	            patientName: ((validateObjectProperties(headerSection.PATIENTLASTNAME)) ? scicopv.mockData : headerSection.PATIENTLASTNAME) + ", " + ((validateObjectProperties(headerSection.PATIENTFIRSTNAME)) ? "" : headerSection.PATIENTFIRSTNAME),                patientMedicalRecordKey: (validateObjectProperties(headerSection.PATIENTMEDICALRECORDKEY)) ? scicopv.mockData : headerSection.PATIENTMEDICALRECORDKEY,
				patientDateOfBirth: (validateObjectProperties(headerSection.PATIENTDATEOFBIRTH)) ? scicopv.mockData : headerSection.PATIENTDATEOFBIRTH,
	            episodeDate: (validateObjectProperties(headerSection.EPISODEDATE)) ? scicopv.mockData : headerSection.EPISODEDATE,
	            followUpDate: (validateObjectProperties(headerSection.FOLLOWUPDATE)) ? scicopv.mockData : headerSection.FOLLOWUPDATE,
	            clinicName: (validateObjectProperties(headerSection.CLINICNAME)) ? scicopv.mockData : headerSection.CLINICNAME,
	            clinicAddressone: (validateObjectProperties(headerSection.CLINICADDRESSONE)) ?  scicopv.mockData : headerSection.CLINICADDRESSONE,
	            clinicCity: (validateObjectProperties(headerSection.CLINICCITY)) ? scicopv.mockData : headerSection.CLINICCITY,
	            clinicState: (validateObjectProperties(headerSection.CLINICSTATE)) ? scicopv.mockData : headerSection.CLINICSTATE,
	            clinicZipcode: (validateObjectProperties(headerSection.CLINICZIPCODE)) ? scicopv.mockData : headerSection.CLINICZIPCODE,
				clinicPhone: (validateObjectProperties(headerSection.CLINICPHONE)) ? scicopv.mockData : headerSection.CLINICPHONE,
				clinicFax: ((validateObjectProperties(headerSection.CLINICFAX)) ? scicopv.mockData : headerSection.CLINICFAX)
	        };
	    }
	
	    function getPatientInformationSection(currentSectionIndex) {
	        var patientInfoSection = {
	            sectionIndex: currentSectionIndex,
	            header: 'Patient Information',
	            row: []
	        };
	
	        var diagOeE = 134;
	        var diagOeO = 131;
	
	        patientInfoSection.row.push({
	            rowIndex: 1,
	            layout: 'oneColumn-oneCell-t1',
	            rowTopMargin: false,
	            columns: [{
	                index: 1,
	                cells: [{
	                    index: 1,
	                    title: 'Change of Care Type:',
	                    body: scicopv.serviceData.PATIENTINFORMATIONSECTION.CHANGEOFCARETYPE
	                }]
	            }]
	        });
	
	        scicopv.serviceData.PATIENTINFORMATIONSECTION.SURGICALPROCEDURE.forEach(function (element, i) {
	            patientInfoSection.row.push({
	                rowIndex: 1,
	                rowHeader: i == 0 ? 'Surgical Procedures' : '',
	                layout: 'twoColumn-twoCell-t6',
	                rowTopMargin: false,
	                dynamicHeight: true,
	                columns: [{
	                    index: 1,
	                    cells: [{
	                        index: 1,
	                        body: element.PROCEDURECODE + " " + element.DIAGNOSIS
	                    }]
	                },
	                    {
	                        index: 2,
	                        cells: [{
	                            index: 1,
	                            body: 'DATE: ' + element.DIAGDATE
	                        }]
	                    }]
	            });
	        });
	
	        scicopv.serviceData.PATIENTINFORMATIONSECTION.PATIENTDIAGNOSIS.forEach(function (element, i) {
	            patientInfoSection.row.push({
	                rowIndex: 1,
	                rowHeader: i == 0 ? 'Patient Diagnosis' : '',
	                layout: 'oneColumn-oneCell-t4',
	                rowTopMargin: false,
	                columns: [{
	                    index: 1,
	                    cells: [{
	                        index: 1,
	                        body: element.PROCEDURECODE + " " + element.DIAGNOSIS
	                    }]
	                }]
	            });
	        });
	
	        patientInfoSection.row.push({
	            rowIndex: 1,
	            rowHeader: 'Primary Diagnosis',
	            layout: 'twoColumn-twoCell-t6',
	            rowTopMargin: false,
	            columns: [{
	                index: 1,
	                cells: [{
	                    index: 1,
	                    body: scicopv.serviceData.PATIENTINFORMATIONSECTION.PRIMARYDIAGNOSIS[0].DIAGNOSISCODE + " " +
	                        scicopv.serviceData.PATIENTINFORMATIONSECTION.PRIMARYDIAGNOSIS[0].DIAGNOSISDESC + " " +
	                        (scicopv.serviceData.PATIENTINFORMATIONSECTION.PRIMARYDIAGNOSIS[0].DIAGNOSISOE == diagOeE ? "(E)" : (scicopv.serviceData.PATIENTINFORMATIONSECTION.PRIMARYDIAGNOSIS[0].DIAGNOSISOE == diagOeO ? "(O)" : ""))
	                }]
	            },
	                {
	                    index: 2,
	                    cells: [{
	                        index: 1,
	                        body: 'DATE: ' + scicopv.serviceData.PATIENTINFORMATIONSECTION.PRIMARYDIAGNOSIS[0].DIAGNOSISDATE
	                    }]
	                }]
	        });
	
	        scicopv.serviceData.PATIENTINFORMATIONSECTION.OTHERDIAGNOSIS.forEach(function (element, i) {
	            patientInfoSection.row.push({
	                rowIndex: 1,
	                rowHeader: i == 0 ? 'Secondary/Other Diagnosis' : '',
	                layout: 'twoColumn-twoCell-t6',
	                rowTopMargin: false,
	                columns: [{
	                    index: 1,
	                    cells: [{
	                        index: 1,
	                        body: element.DIAGNOSISCODE + " " + element.DIAGNOSISDESC + " " + (element.DIAGNOSISOE == diagOeO ? "(O)" : (element.DIAGNOSISOE == diagOeE ? "(E)" : ""))
	                    }]
	                },
	                    {
	                        index: 2,
	                        cells: [{
	                            index: 1,
	                            body: 'DATE: ' + element.DIAGNOSISDATE
	                        }]
	                    }]
	            });
	        });
	        return patientInfoSection;
	    }
	
	    function getRiskProfileSection(currentSectionIndex) {
	
	        var riskProfileSection = {
	            sectionIndex: currentSectionIndex,
	            header: 'Risk Profile',
	            row: []
	        };
	
	        riskProfileSection.row.push({
	            rowIndex: 1,
	            layout: 'oneColumn-oneCell-t1',
	            rowTopMargin: false,
	            dynamicHeight: true,
	            columns: [{
	                index: 1,
	                cells: [{
	                    index: 1,
	                    body: (validateObjectProperties(scicopv.serviceData.RISKPROFILESECTION.RISKPROFILE)) ? scicopv.mockData : scicopv.serviceData.RISKPROFILESECTION.RISKPROFILE
	                }]
	            }]
	        });
	        return riskProfileSection;
	    }
	
	    function getAdvanceDirectives(currentSectionIndex) {
	
	        var advanceDirectivesSection = {
	            sectionIndex: currentSectionIndex,
	            header: 'Advance Directives',
	            row: []
	        };
	
	        advanceDirectivesSection.row.push({
	            rowIndex: 1,
	            layout: 'oneColumn-oneCell-t1',
	            rowTopMargin: false,
	            dynamicHeight: true,
	            columns: [{
	                index: 1,
	                cells: [{
	                    index: 1,
	                    body: (validateObjectProperties(scicopv.serviceData.ADVANCEDIRECTIVESSECTION.ADVANCEDIRECTIVE)) ? scicopv.mockData : scicopv.serviceData.ADVANCEDIRECTIVESSECTION.ADVANCEDIRECTIVE
	                }]
	            }]
	        });
	        return advanceDirectivesSection;
	    }
	
	    function getMedicationSection(currentSectionIndex) {
	
	        var medicationSection = {
	            sectionIndex: currentSectionIndex,
	            header: 'Medications',
	            row: []
	        };
	
	        medicationSection.row.push({
	            rowIndex: 1,
	            layout: 'oneColumn-oneCell-t1',
	            rowTopMargin: false,
	            dynamicHeight: true,
	            columns: [{
	                index: 1,
	                cells: [{
	                    index: 1,
	                    title: '',
	                    body: (validateObjectProperties(scicopv.serviceData.MEDICATIONSECTION.MEDICATION)) ? scicopv.mockData : scicopv.serviceData.MEDICATIONSECTION.MEDICATION
	                }]
	            }]
	        })
	        return medicationSection;
	    }
	
	    function getDmeAndSuppliesSection(currentSectionIndex) {
	        var dmeAndSuppliesSection = {
	            sectionIndex: currentSectionIndex,
	            header: 'DME and Supplies',
	            row: []
	        };
	
	        dmeAndSuppliesSection.row.push({
	            rowIndex: 1,
	            layout: 'oneColumn-oneCell-t1',
	            rowTopMargin: false,
	            dynamicHeight: true,
	            columns: [{
	                index: 1,
	                cells: [{
	                    index: 1,
	                    title: '',
	                    body: (validateObjectProperties(scicopv.serviceData.DMEANDSUPPLIESSECTION.DMEANDSUPPLIES)) ? scicopv.mockData : scicopv.serviceData.DMEANDSUPPLIESSECTION.DMEANDSUPPLIES
	                }]
	            }]
	        })
	        return dmeAndSuppliesSection;
	    }
	
	    function getOrdersAndTreatmentsSections(currentSectionIndex) {
	        var ordersAndTreatmentsSection = {
	            sectionIndex: currentSectionIndex,
	            header: 'Orders and Treatments',
	            row: []
	        }
	
	        ordersAndTreatmentsSection.row.push({
	            rowIndex: 0,
	            rowHeader: 'Frequencies',
	            layout: 'oneColumn-oneCell-t1',
	            rowTopMargin: false,
	            dynamicHeight: true,
	            columns: [{
	                index: 1,
	                cells: [{
	                    index: 1,
	                    body: (validateObjectProperties(scicopv.serviceData.ORDERSANDTREATMENTS.FREQUENCIES)) ? scicopv.mockData : scicopv.serviceData.ORDERSANDTREATMENTS.FREQUENCIES
	                }]
	            }]
	        });

			if (scicopv.serviceData.ORDERSANDTREATMENTS.PRORENATAS){
				ordersAndTreatmentsSection.row.push({
					rowIndex: 0,
					rowHeader: 'PRN Orders',
					layout: 'oneColumn-oneCell-t1',
					rowTopMargin: false,
					dynamicHeight: true,
					columns: [{
						index: 1,
						cells: [{
							index: 1,
							body: (validateObjectProperties(scicopv.serviceData.ORDERSANDTREATMENTS.PRORENATAS)) ? scicopv.mockData : scicopv.serviceData.ORDERSANDTREATMENTS.PRORENATAS
						}]
					}]
				});
			}

			if (scicopv.serviceData.ORDERSANDTREATMENTS.ADDITIONALCOMMENTS && (scicopv.serviceData.DARKDEPLOYSECTION.ADDITIONALCOMMENTSDD === 'true')){
				ordersAndTreatmentsSection.row.push({
					rowIndex: 0,
					rowHeader: 'Additional Orders',
					layout: 'oneColumn-oneCell-t1',
					rowTopMargin: false,
					dynamicHeight: true,
					columns: [{
						index: 1,
						cells: [{
							index: 1,
							body: (validateObjectProperties(scicopv.serviceData.ORDERSANDTREATMENTS.ADDITIONALCOMMENTS)) ? scicopv.mockData : scicopv.serviceData.ORDERSANDTREATMENTS.ADDITIONALCOMMENTS
						}]
					}]
				});
			}

	        ordersAndTreatmentsSection.row.push({
	            rowIndex: 1,
	            rowHeader: 'Interventions',
	            layout: 'oneColumn-oneCell-t1',
	            rowTopMargin: false,
	            dynamicHeight: true,
	            columns: [{
	                index: 1,
	                cells: [{
	                    index: 1,
	                    body: (validateObjectProperties(scicopv.serviceData.ORDERSANDTREATMENTS.INTERVENTIONS)) ? scicopv.mockData : scicopv.serviceData.ORDERSANDTREATMENTS.INTERVENTIONS
	                }]
	            }]
	        });
	
	        ordersAndTreatmentsSection.row.push({
	            rowIndex: 2,
	            rowHeader: 'Homebound Status ',
	            layout: 'oneColumn-oneCell-t1',
	            rowTopMargin: false,
	            dynamicHeight: true,
	            columns: [{
	                index: 1,
	                cells: [{
	                    index: 1,
	                    body: (validateObjectProperties(scicopv.serviceData.ORDERSANDTREATMENTS.HOMEBOUNDSTATUS)) ? scicopv.mockData : scicopv.serviceData.ORDERSANDTREATMENTS.HOMEBOUNDSTATUS
	                }]
	            }]
	        });
	
	        ordersAndTreatmentsSection.row.push({
	            rowIndex: 3,
	            rowHeader: 'Vital Sign Parameters',
	            layout: 'oneColumn-oneCell-t1',
	            rowTopMargin: false,
	            dynamicHeight: true,
	            columns: [{
	                index: 1,
	                cells: [{
	                    index: 1,
	                    body: (validateObjectProperties(scicopv.serviceData.ORDERSANDTREATMENTS.VITALPARAMETERS)) ? scicopv.mockData : scicopv.serviceData.ORDERSANDTREATMENTS.VITALPARAMETERS
	                }]
	            }]
	        });
	
	        return ordersAndTreatmentsSection;
	    }
	
	    function getGoalsAndOutcomes(currentSectionIndex) {
	
	        var goalsAndOutcomesSection = {
	            sectionIndex: currentSectionIndex,
	            header: 'Goals and Outcomes',
	            row: []
	        };
	
	        goalsAndOutcomesSection.row.push({
	            rowIndex: 1,
	            rowHeader: 'Goals',
	            layout: 'oneColumn-oneCell-t1',
	            rowTopMargin: false,
	            dynamicHeight: true,
	            columns: [{
	                index: 1,
	                cells: [{
	                    index: 1,
	                    title: '',
	                    body: (validateObjectProperties(scicopv.serviceData.GOALSANDOUTCOMESSECTION.GOALSTEXT)) ? scicopv.mockData : scicopv.serviceData.GOALSANDOUTCOMESSECTION.GOALSTEXT
	                }]
	            }]
	        })
	
	        goalsAndOutcomesSection.row.push({
	            rowIndex: 2,
	            rowHeader: 'Rehab Potential',
	            layout: 'oneColumn-oneCell-t1',
	            rowTopMargin: false,
	            dynamicHeight: true,
	            columns: [{
	                index: 1,
	                cells: [{
	                    index: 1,
	                    title: '',
	                    body: (validateObjectProperties(scicopv.serviceData.GOALSANDOUTCOMESSECTION.REHABPOTENTIAL)) ? scicopv.mockData : scicopv.serviceData.GOALSANDOUTCOMESSECTION.REHABPOTENTIAL
	                }]
	            }]
	        });
	
	        goalsAndOutcomesSection.row.push({
	            rowIndex: 3,
	            rowHeader: 'Discharge Planning',
	            layout: 'oneColumn-oneCell-t1',
	            rowTopMargin: false,
	            dynamicHeight: true,
	            columns: [{
	                index: 1,
	                cells: [{
	                    index: 1,
	                    title: '',
	                    body: (validateObjectProperties(scicopv.serviceData.GOALSANDOUTCOMESSECTION.DISCHARGEPLANNING)) ? scicopv.mockData : scicopv.serviceData.GOALSANDOUTCOMESSECTION.DISCHARGEPLANNING
	                }]
	            }]
	
	        });
	        return goalsAndOutcomesSection;
	    }
	
	    function getBottomData(currentSectionIndex) {
	
	        var bottomDataSection = {
	            sectionIndex: currentSectionIndex,
	            row: []
	        };
	
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
	                    title: 'Clinician Signature:',
	                    body: (validateObjectProperties(scicopv.serviceData.BOTTOMDATASECTION.CLINICIANSIGNATURE)) ? scicopv.mockData : scicopv.serviceData.BOTTOMDATASECTION.CLINICIANSIGNATURE
	                }]
	            },
	                {
	                    index: 2,
	                    cells: [{
	                        title: 'Date:',
	                        body: (validateObjectProperties(scicopv.serviceData.BOTTOMDATASECTION.CLINICIANDATE)) ? scicopv.mockData : scicopv.serviceData.BOTTOMDATASECTION.CLINICIANDATE
	                    }]
	                }]
	        })
	
	        bottomDataSection.row.push({
	            rowIndex: 2,
	            layout: 'twoColumn-fourCell-t1',
	            rowTopMargin: false,
	            columns: [{
	                index: 1,
	                cells: [{
	                    index: 1,
	                    title: 'Physician\'s Name:',
	                    body: (validateObjectProperties(scicopv.serviceData.BOTTOMDATASECTION.PHYSICIANNAME)) ? scicopv.mockData : scicopv.serviceData.BOTTOMDATASECTION.PHYSICIANNAME
	                },
	                    {
	                        index: 2,
	                        title: 'Physician\'s Address:',
	                        body: (validateObjectProperties(scicopv.serviceData.BOTTOMDATASECTION.PHYSICIANADDRESS)) ? scicopv.mockData : scicopv.serviceData.BOTTOMDATASECTION.PHYSICIANADDRESS
	                    }]
	            },
	                {
	                    index: 2,
	                    cells: [{
	                        index: 1,
	                        title: 'Phone Number',
	                        body: scicopv.serviceData.BOTTOMDATASECTION.PHONE
	                    },
	                        {
	                            index: 2,
	                            title: 'Fax Number',
	                            body: scicopv.serviceData.BOTTOMDATASECTION.FAX
	                        }
	                    ]
	                }
	            ]
	        })
	
	        bottomDataSection.row.push({
	            rowIndex: 3,
	            layout: 'twoColumn-twoCell-t1',
	            rowTopMargin: false,
	            dynamicHeight: true,
	            columns: [{
	                index: 1,
	                cells: [{
	                    index: 1,
	                    title: 'Physician\'s Signature:',
	                    body: (validateObjectProperties(scicopv.serviceData.BOTTOMDATASECTION.PHYSICIANSIGNATURE)) ? scicopv.mockData : scicopv.serviceData.BOTTOMDATASECTION.PHYSICIANSIGNATURE
	                }]
	            },
	                {
	                    index: 2,
	                    cells: [{
	                        index: 1,
	                        title: 'Date:',
	                        body: (validateObjectProperties(scicopv.serviceData.BOTTOMDATASECTION.PHYSICIANDATE)) ? scicopv.mockData : scicopv.serviceData.BOTTOMDATASECTION.PHYSICIANDATE
	                    }]
	                }]
	        })
	        return bottomDataSection;
	    }
    }
}());

(function () {
    'use strict';

    angular.module('am-pho-printview',
        [
            'directives.kinnser.am-print-view.page-builder-new',
            'resources.hh-order-resource'
        ])
        .controller('AMPhoPrintViewController', controller);

    controller.$inject = ['$rootScope', '$route', 'pvObjects'];

    function controller($rootScope, $route, pvObjects) {

        var vm = angular.extend(this, {
            serviceData: '',
            mockData: '--',
            initialize: initialize,
            getHeader: getHeader,
            getImpatientInformationSection: getImpatientInformationSection,
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
            vm.serviceData = serviceData;
            $rootScope.print = true;
            vm.boot = [];
            vm.idSuffix = "";

            getHeader(vm.serviceData.HEADERSECTION);
            vm.boot.push(vm.getImpatientInformationSection(currentSectionIndex++));
            vm.boot.push(vm.getRiskProfileSection(currentSectionIndex++));
            vm.boot.push(vm.getAdvanceDirectives(currentSectionIndex++));
            vm.boot.push(vm.getMedicationSection(currentSectionIndex++));
            vm.boot.push(vm.getDmeAndSuppliesSection(currentSectionIndex++));
            vm.boot.push(vm.getOrdersAndTreatmentsSections(currentSectionIndex++));
            vm.boot.push(vm.getGoalsAndOutcomes(currentSectionIndex++));
            vm.boot.push(vm.getBottomData(currentSectionIndex++));
        }

        function validateObjectProperties(value) {
            return value === 'undefined' || value == null || value === '';
        }

        function getHeader(headerSection) {
            vm.orderNumber = (validateObjectProperties(headerSection.PATIENTTASKKEY)) ?  vm.mockData : headerSection.PATIENTTASKKEY;
            vm.pageTitle = {
                title: "Post Hospital Order",
                taskName: (validateObjectProperties(headerSection.POSTHOSPITALORDERNAME)) ? vm.mockData : headerSection.POSTHOSPITALORDERNAME,
                patientTaskDate: (validateObjectProperties(headerSection.PATIENTTASKDATE)) ? vm.mockData : headerSection.PATIENTTASKDATE,
                patientTaskKey: (validateObjectProperties(headerSection.PATIENTTASKKEY)) ? vm.mockData : headerSection.PATIENTTASKKEY,
                patientName: ((validateObjectProperties(headerSection.PATIENTLASTNAME)) ? vm.mockData : headerSection.PATIENTLASTNAME) + ", " + ((validateObjectProperties(headerSection.PATIENTFIRSTNAME)) ? "" : headerSection.PATIENTFIRSTNAME),                patientMedicalRecordKey: (validateObjectProperties(headerSection.PATIENTMEDICALRECORDKEY)) ? vm.mockData : headerSection.PATIENTMEDICALRECORDKEY,
                patientDateOfBirth: (validateObjectProperties(headerSection.PATIENTDATEOFBIRTH)) ? vm.mockData : headerSection.PATIENTDATEOFBIRTH,
                episodeDate: (validateObjectProperties(headerSection.EPISODEDATE)) ? vm.mockData : headerSection.EPISODEDATE,
                resumptionOfCareDate: (validateObjectProperties(headerSection.RESUMPTIONOFCAREDATE)) ? vm.mockData : headerSection.RESUMPTIONOFCAREDATE,
                clinicName: (validateObjectProperties(headerSection.CLINICNAME)) ? vm.mockData : headerSection.CLINICNAME,
                clinicAddressone: (validateObjectProperties(headerSection.CLINICADDRESSONE)) ?  vm.mockData : headerSection.CLINICADDRESSONE,
                clinicCity: (validateObjectProperties(headerSection.CLINICCITY)) ? vm.mockData : headerSection.CLINICCITY,
                clinicState: (validateObjectProperties(headerSection.CLINICSTATE)) ? vm.mockData : headerSection.CLINICSTATE,
                clinicZipcode: (validateObjectProperties(headerSection.CLINICZIPCODE)) ? vm.mockData : headerSection.CLINICZIPCODE,
                clinicPhone: (validateObjectProperties(headerSection.CLINICPHONE)) ? vm.mockData : headerSection.CLINICPHONE,
                clinicFax: ((validateObjectProperties(headerSection.CLINICFAX)) ? vm.mockData : headerSection.CLINICFAX)
            };
        }

        function getImpatientInformationSection(currentSectionIndex) {
            var patientInfoSection = {
                sectionIndex: currentSectionIndex,
                header: 'Inpatient Information',
                row: []
            };

            var HOSPITALADMIT = vm.serviceData.IMPATIENTINFORMATIONSECTION.HOSPITALADMIT,
                HOSPITALDISCHARGE = vm.serviceData.IMPATIENTINFORMATIONSECTION.HOSPITALDISCHARGE;

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
                        title: 'Hospital Stay From:',
                        body: HOSPITALADMIT + ' - ' + HOSPITALDISCHARGE
                    }]
                }]
            });

            vm.serviceData.IMPATIENTINFORMATIONSECTION.SURGICALPROCEDURE.forEach(function (element, i) {
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

            vm.serviceData.IMPATIENTINFORMATIONSECTION.IMPATIENTDIAGNOSIS.forEach(function (element, i) {
                patientInfoSection.row.push({
                    rowIndex: 1,
                    rowHeader: i == 0 ? 'Inpatient Diagnosis' : '',
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
                        body: vm.serviceData.IMPATIENTINFORMATIONSECTION.PRIMARYDIAGNOSIS[0].DIAGNOSISCODE + " " +
                            vm.serviceData.IMPATIENTINFORMATIONSECTION.PRIMARYDIAGNOSIS[0].DIAGNOSISDESC + " " +
                            (vm.serviceData.IMPATIENTINFORMATIONSECTION.PRIMARYDIAGNOSIS[0].DIAGNOSISOE == diagOeE ? "(E)" : (vm.serviceData.IMPATIENTINFORMATIONSECTION.PRIMARYDIAGNOSIS[0].DIAGNOSISOE == diagOeO ? "(O)" : ""))
                    }]
                },
                    {
                        index: 2,
                        cells: [{
                            index: 1,
                            body: 'DATE: ' + vm.serviceData.IMPATIENTINFORMATIONSECTION.PRIMARYDIAGNOSIS[0].DIAGNOSISDATE
                        }]
                    }]
            });

            vm.serviceData.IMPATIENTINFORMATIONSECTION.OTHERDIAGNOSIS.forEach(function (element, i) {
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
                        body: (validateObjectProperties(vm.serviceData.RISKPROFILESECTION.RISKPROFILE)) ? vm.mockData : vm.serviceData.RISKPROFILESECTION.RISKPROFILE
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
                        body: (validateObjectProperties(vm.serviceData.ADVANCEDIRECTIVESSECTION.ADVANCEDIRECTIVE)) ? vm.mockData : vm.serviceData.ADVANCEDIRECTIVESSECTION.ADVANCEDIRECTIVE
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
                        body: (validateObjectProperties(vm.serviceData.MEDICATIONSECTION.MEDICATION)) ? vm.mockData : vm.serviceData.MEDICATIONSECTION.MEDICATION
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
                        body: (validateObjectProperties(vm.serviceData.DMEANDSUPPLIESSECTION.DMEANDSUPPLIES)) ? vm.mockData : vm.serviceData.DMEANDSUPPLIESSECTION.DMEANDSUPPLIES
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
                        body: (validateObjectProperties(vm.serviceData.ORDERSANDTREATMENTS.FREQUENCIES)) ? vm.mockData : vm.serviceData.ORDERSANDTREATMENTS.FREQUENCIES
                    }]
                }]
            });

            if (vm.serviceData.ORDERSANDTREATMENTS.PRORENATAS){
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
                            body: (validateObjectProperties(vm.serviceData.ORDERSANDTREATMENTS.PRORENATAS)) ? vm.mockData : vm.serviceData.ORDERSANDTREATMENTS.PRORENATAS
                        }]
                    }]
                });
            }

            if (vm.serviceData.ORDERSANDTREATMENTS.ADDITIONALCOMMENTS && (vm.serviceData.DARKDEPLOYSECTION.ADDITIONALCOMMENTSDD === 'true')){
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
                            body: (validateObjectProperties(vm.serviceData.ORDERSANDTREATMENTS.ADDITIONALCOMMENTS)) ? vm.mockData : vm.serviceData.ORDERSANDTREATMENTS.ADDITIONALCOMMENTS
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
                        body: (validateObjectProperties(vm.serviceData.ORDERSANDTREATMENTS.INTERVENTIONS)) ? vm.mockData : vm.serviceData.ORDERSANDTREATMENTS.INTERVENTIONS
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
                        body: (validateObjectProperties(vm.serviceData.ORDERSANDTREATMENTS.HOMEBOUNDSTATUS)) ? vm.mockData : vm.serviceData.ORDERSANDTREATMENTS.HOMEBOUNDSTATUS
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
                        body: (validateObjectProperties(vm.serviceData.ORDERSANDTREATMENTS.VITALPARAMETERS)) ? vm.mockData : vm.serviceData.ORDERSANDTREATMENTS.VITALPARAMETERS
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
                        body: (validateObjectProperties(vm.serviceData.GOALSANDOUTCOMESSECTION.GOALSTEXT)) ? vm.mockData : vm.serviceData.GOALSANDOUTCOMESSECTION.GOALSTEXT
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
                        body: (validateObjectProperties(vm.serviceData.GOALSANDOUTCOMESSECTION.REHABPOTENTIAL)) ? vm.mockData : vm.serviceData.GOALSANDOUTCOMESSECTION.REHABPOTENTIAL
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
                        body: (validateObjectProperties(vm.serviceData.GOALSANDOUTCOMESSECTION.DISCHARGEPLANNING)) ? vm.mockData : vm.serviceData.GOALSANDOUTCOMESSECTION.DISCHARGEPLANNING
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
                        body: (validateObjectProperties(vm.serviceData.BOTTOMDATASECTION.CLINICIANSIGNATURE)) ? vm.mockData : vm.serviceData.BOTTOMDATASECTION.CLINICIANSIGNATURE
                    }]
                },
                    {
                        index: 2,
                        cells: [{
                            title: 'Date:',
                            body: (validateObjectProperties(vm.serviceData.BOTTOMDATASECTION.CLINICIANDATE)) ? vm.mockData : vm.serviceData.BOTTOMDATASECTION.CLINICIANDATE
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
                        body: (validateObjectProperties(vm.serviceData.BOTTOMDATASECTION.PHYSICIANNAME)) ? vm.mockData : vm.serviceData.BOTTOMDATASECTION.PHYSICIANNAME
                    },
                        {
                            index: 2,
                            title: 'Physician\'s Address:',
                            body: (validateObjectProperties(vm.serviceData.BOTTOMDATASECTION.PHYSICIANADDRESS)) ? vm.mockData : vm.serviceData.BOTTOMDATASECTION.PHYSICIANADDRESS
                        }]
                },
                    {
                        index: 2,
                        cells: [{
                            index: 1,
                            title: 'Phone Number',
                            body: vm.serviceData.BOTTOMDATASECTION.PHONE
                        },
                            {
                                index: 2,
                                title: 'Fax Number',
                                body: vm.serviceData.BOTTOMDATASECTION.FAX
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
                        body: (validateObjectProperties(vm.serviceData.BOTTOMDATASECTION.PHYSICIANSIGNATURE)) ? vm.mockData : vm.serviceData.BOTTOMDATASECTION.PHYSICIANSIGNATURE
                    }]
                },
                    {
                        index: 2,
                        cells: [{
                            index: 1,
                            title: 'Date:',
                            body: (validateObjectProperties(vm.serviceData.BOTTOMDATASECTION.PHYSICIANDATE)) ? vm.mockData : vm.serviceData.BOTTOMDATASECTION.PHYSICIANDATE
                        }]
                    }]
            })
            return bottomDataSection;
        }
    }
}());

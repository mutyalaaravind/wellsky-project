(function() {
    'use strict';

    angular
        .module('amng.cop-poc-printview', [
            'AMNG',
            'directives.kinnser.am-print-view.page-builder',
            'services.dark-deploy.dark-deploy-service'
        ])
        .controller('COPPOCPrintviewController', controller)
        .constant('COPPOCPrintConstants', {});

    controller.$inject = ['COPPOCPrintConstants'];

    function controller(COPPOCPrintConstants) {
        var vm = angular.extend(this, {
            // members
            printData: {},
            targetDate: Date,
            // methods
            initialize: initialize,
            getPatientInformationSection: getPatientInformationSection,
            getClinicalDataSection: getClinicalDataSection,
            getTreatmentsSection: getTreatmentsSection,
            getSignatureSection: getSignatureSection
        });
        var cutDate = new Date('2021-09-30');

        function initialize(printData) {
            vm.printData = printData;
            vm.targetDate = new Date(printData.clinicalData.taskTargetDate);
            vm.boot = [];
            vm.idSuffix = "CoP";
            vm.pageTitle = {
                title: "Home Health Certification and Plan of Care",
                patientName: vm.printData.patientInformation.patientName,
                certifiedPeriod: {
                    from: vm.printData.patientInformation.certificationPeriodFrom,
                    to: vm.printData.patientInformation.certificationPeriodTo
                }
            }; //Hard coded value of the page headers

            vm.boot.push(vm.getPatientInformationSection());
            vm.boot.push(vm.getClinicalDataSection());
            vm.boot.push(vm.getTreatmentsSection());
            vm.boot.push(vm.getSignatureSection());
        }

        function getPatientInformationSection() {
            var patientInfoSection = {
                sectionIndex: 1,
                header: 'Patient Information',
                row: []
            };

            patientInfoSection.row.push({
                rowIndex: 1,
                layout: 'fourColumn-fourCell-t1',
                rowTopMargin: false,
                columns: [{
                        index: 1,
                        cells: [{
                            index: 1,
                            title: 'Patient\'s HI Claim No.',
                            body: vm.printData.patientInformation.patientHIClainNo
                        }]
                    },
                    {
                        index: 2,
                        cells: [{
                            index: 1,
                            title: 'Start of Care Date',
                            body: vm.printData.patientInformation.startCareDate
                        }]
                    },
                    {
                        index: 3,
                        cells: [{
                            index: 1,
                            type: 'date',
                            title: 'Certification Period',
                            childCells: [{
                                    index: 1,
                                    title: 'From',
                                    body: vm.printData.patientInformation.certificationPeriodFrom
                                },
                                {
                                    index: 2,
                                    title: 'To',
                                    body: vm.printData.patientInformation.certificationPeriodTo
                                }
                            ]
                        }]
                    },
                    {
                        index: 4,
                        cells: [{
                            index: 1,
                            title: 'Medical Record No.',
                            body: vm.printData.patientInformation.medicalRecordNo
                        }]
                    }
                ]
            });

            patientInfoSection.row.push({
                rowIndex: 2,
                layout: 'threeColumn-sixCell-t1',
                rowTopMargin: false,
                rowHeight: 100,
                columns: [{
                        index: 1,
                        cells: [{
                            index: 1,
                            title: 'Patient\'s Name and Address',
                            body: vm.printData.patientInformation.patientName + "\n " +
                                vm.printData.patientInformation.patientAddress
                        }]
                    },
                    {
                        index: 2,
                        cells: [{
                                index: 1,
                                title: 'Gender',
                                body: vm.printData.patientInformation.gender
                            },
                            {
                                index: 2,
                                title: 'Date of Birth',
                                body: vm.printData.patientInformation.birthday
                            },
                            {
                                index: 3,
                                title: 'Email',
                                body: vm.printData.patientInformation.email
                            }
                        ]
                    },
                    {
                        index: 3,
                        cells: [{
                                index: 1,
                                title: 'Phone Number',
                                body: vm.printData.patientInformation.phoneNumber
                            },
                            {
                                index: 2,
                                title: 'Primary Language',
                                body: vm.printData.patientInformation.primaryLanguage
                            }
                        ]
                    }
                ]
            });

            if (vm.printData.patientInformation.showPatientRepresentative) {
                patientInfoSection.row.push({
                    rowIndex: 3,
                    layout: 'threeColumn-sixCell-t3',
                    rowTopMargin: true,
                    rowHeight: 105,
                    columns: [{
                            index: 1,
                            cells: [{
                                    index: 1,
                                    title: 'Patient\'s Representative',
                                    body: vm.printData.patientInformation.patientRepresentative.name
                                },
                                {
                                    index: 2,
                                    title: 'Phone Number',
                                    body: vm.printData.patientInformation.patientRepresentative.phoneNumber
                                },
                                {
                                    index: 3,
                                    title: 'Representative Type',
                                    body: vm.printData.patientInformation.patientRepresentative.representativeType
                                }
                            ]
                        },
                        {
                            index: 2,
                            cells: [{
                                index: 1,
                                title: 'Address',
                                body: vm.printData.patientInformation.patientRepresentative.address
                            }]
                        },
                        {
                            index: 3,
                            cells: [{
                                    index: 1,
                                    title: 'Relationship',
                                    body: vm.printData.patientInformation.patientRepresentative.relationship
                                },
                                {
                                    index: 2,
                                    title: 'Primary Language',
                                    body: vm.printData.patientInformation.patientRepresentative.primaryLanguage
                                }
                            ]
                        }
                    ]
                });
            }

            patientInfoSection.row.push({
                rowIndex: 4,
                layout: 'oneColumn-oneCell-t1',
                rowTopMargin: true,
                dynamicHeight: true,
                columns: [{
                    index: 1,
                    cells: [{
                        index: 1,
                        title: 'Patient Risk Profile',
                        body: vm.printData.patientInformation.riskProfile
                    }]
                }]
            });
            return patientInfoSection;
        }

        function getClinicalDataSection() {
            var clinicalDataSection = {
                sectionIndex: 2,
                header: 'Clinical Data',
                row: []
            };

            clinicalDataSection.row.push({
                rowIndex: 1,
                layout: 'threeColumn-fiveCell-t1',
                rowTopMargin: false,
                columns: [{
                        index: 1,
                        cells: [{
                                index: 1,
                                title: 'Clinical Manager',
                                body: vm.printData.clinicalData.clinicalManager.name
                            },
                            {
                                index: 2,
                                title: 'Provider Number - Medicare Number',
                                body: vm.printData.clinicalData.clinicalManager.providerNumber
                            }
                        ]
                    },
                    {
                        index: 2,
                        cells: [{
                            index: 1,
                            title: 'Branch Name and Address',
                            body: vm.printData.clinicalData.clinicalManager.address
                        }]
                    },
                    {
                        index: 3,
                        cells: [{
                                index: 1,
                                title: 'Phone Number',
                                body: vm.printData.clinicalData.clinicalManager.phoneNumber
                            },
                            {
                                index: 2,
                                title: 'Fax Number',
                                body: vm.printData.clinicalData.clinicalManager.faxNumber
                            }
                        ]
                    }
                ]

            });
            if (vm.targetDate < cutDate) {
                clinicalDataSection.row.push({
                    rowIndex: 2,
                    layout: 'threeColumn-fiveCell-t1',
                    rowTopMargin: true,
                    columns: [{
                        index: 1,
                        cells: [{
                            index: 1,
                            title: 'Primary Physician',
                            body: vm.printData.clinicalData.primaryPhysician.name
                        },
                            {
                                index: 2,
                                title: 'NPI',
                                body: vm.printData.clinicalData.primaryPhysician.npi
                            }
                        ]
                    },
                        {
                            index: 2,
                            cells: [{
                                index: 1,
                                title: 'Address',
                                body: vm.printData.clinicalData.primaryPhysician.address
                            }]
                        },
                        {
                            index: 3,
                            cells: [{
                                index: 1,
                                title: 'Phone Number',
                                body: vm.printData.clinicalData.primaryPhysician.phoneNumber
                            },
                                {
                                    index: 2,
                                    title: 'Fax Number',
                                    body: vm.printData.clinicalData.primaryPhysician.faxNumber
                                }
                            ]
                        }
                    ]

                });
            }
            
            var rowIndex = 3;
            for (var i = 0; i < vm.printData.clinicalData.associatePhysician.length; i++) {
                clinicalDataSection.row.push({
                    rowIndex: rowIndex,
                    layout: 'threeColumn-fiveCell-t1',
                    rowTopMargin: true,
                    columns: [{
                            index: 1,
                            cells: [{
                                    index: 1,
                                    title: 'Associate Physician',
                                    body: vm.printData.clinicalData.associatePhysician[i].name
                                },
                                {
                                    index: 2,
                                    title: 'NPI',
                                    body: vm.printData.clinicalData.associatePhysician[i].npi
                                }
                            ]
                        },
                        {
                            index: 2,
                            cells: [{
                                index: 1,
                                title: 'Address',
                                body: vm.printData.clinicalData.associatePhysician[i].address
                            }]
                        },
                        {
                            index: 3,
                            cells: [{
                                    index: 1,
                                    title: 'Phone Number',
                                    body: vm.printData.clinicalData.associatePhysician[i].phoneNumber
                                },
                                {
                                    index: 2,
                                    title: 'Fax Number',
                                    body: vm.printData.clinicalData.associatePhysician[i].faxNumber
                                }
                            ]
                        }
                    ]

                });
                rowIndex++;
            }
            clinicalDataSection.row.push({
                rowIndex: rowIndex,
                rowHeader: 'Primary Diagnosis',
                layout: 'oneColumn-oneCell-t2',
                dynamicHeight: true,
                rowTopMargin: true,
                columns: [{
                    index: 1,
                    cells: [{
                        index: 1,
                        cellLayout: 'threeColumn-t1',
                        titleList: [{
                            code: 'Code',
                            description: 'Description',
                            date: 'Date'
                        }],
                        childCells: [{
                            code: vm.printData.clinicalData.primaryDiagnosis.code,
                            description: vm.printData.clinicalData.primaryDiagnosis.description,
                            date: vm.printData.clinicalData.primaryDiagnosis.date
                        }]
                    }]
                }]
            });
            rowIndex++;
            if(vm.printData.printViewVersion != 11){
                clinicalDataSection.row.push({
                    rowIndex: rowIndex,
                    rowHeader: 'Surgical Procedures',
                    layout: 'oneColumn-oneCell-t2',
                    dynamicHeight: true,
                    rowTopMargin: false,
                    columns: [{
                        index: 1,
                        cells: [{
                            index: 1,
                            cellLayout: 'threeColumn-t1',
                            titleList: [{
                                code: 'Code',
                                description: 'Description',
                                date: 'Date'
                            }],
                            childCells: vm.printData.clinicalData.surgicalDiagnosis
                        }]
                    }]
                });
                rowIndex++;   
            }
            
            clinicalDataSection.row.push({
                rowIndex: rowIndex,
                rowHeader: 'Secondary/Other Diagnosis',
                layout: 'oneColumn-oneCell-t2',
                rowTopMargin: false,
                dynamicHeight: true,
                columns: [{
                    index: 1,
                    cells: [{
                        index: 1,
                        cellLayout: 'threeColumn-t1',
                        titleList: [{
                            code: 'Code',
                            description: 'Description',
                            date: 'Date'
                        }],
                        childCells: vm.printData.clinicalData.secondaryDiagnosis
                    }]
                }]
            });
            rowIndex++;
            
            if(vm.printData.printViewVersion == 11){
                clinicalDataSection.row.push({
                    rowIndex: rowIndex,
                    layout: 'oneColumn-oneCell-t1',
                    rowTopMargin: true,
                    dynamicHeight: true,
                    columns: [{
                        index: 1,
                        cells: [{
                            index: 1,
                            title: 'Mental Status',
                            body: vm.printData.clinicalData.mentalStatus
                        }]
                    }]
                });
                rowIndex++;
            }else {
                clinicalDataSection.row.push({
                    rowIndex: rowIndex,
                    layout: 'twoColumn-twoCell-t1',
                    rowTopMargin: true,
                    columns: [{
                        index: 1,
                        cells: [{
                            index: 1,
                            title: 'Mental Status',
                            body: vm.printData.clinicalData.mentalStatus
                        }]
                    },
                        {
                            index: 2,
                            cells: [{
                                index: 1,
                                title: 'Other',
                                body: vm.printData.clinicalData.mentalStatusOther
                            }]
                        }
                    ]
                });
                rowIndex++;
            }
            if(vm.printData.printViewVersion != 11){
                clinicalDataSection.row.push({
                    rowIndex: rowIndex,
                    layout: 'oneColumn-oneCell-t1',
                    rowTopMargin: true,
                    dynamicHeight: true,
                    columns: [{
                        index: 1,
                        cells: [{
                            index: 1,
                            title: 'Additional Orders',
                            body: vm.printData.clinicalData.mentalAdditionalOrders
                        }]
                    }]
                });
                rowIndex++;
            }
            if(vm.printData.printViewVersion != 11){
                clinicalDataSection.row.push({
                    rowIndex: rowIndex,
                    layout: 'twoColumn-twoCell-t3',
                    rowTopMargin: true,
                    rowHeight: 98,
                    columns: [{
                        index: 1,
                        cells: [{
                            index: 1,
                            title: 'Neurological',
                            body: vm.printData.clinicalData.neurological
                        },
                            {
                                index: 2,
                                title: 'Tremor Location(s)',
                                body: vm.printData.clinicalData.tremorLocation
                            }
                        ]
                    },
                        {
                            index: 2,
                            cells: [{
                                index: 1,
                                title: 'Psychosocial',
                                body: vm.printData.clinicalData.psychosocial
                            }]
                        }
                    ]
                });
                rowIndex++;
            }
            if(vm.printData.printViewVersion != 11){
                clinicalDataSection.row.push({
                    rowIndex: rowIndex,
                    layout: 'oneColumn-oneCell-t1',
                    rowTopMargin: false,
                    dynamicHeight: true,
                    columns: [{
                        index: 1,
                        cells: [{
                            index: 1,
                            title: 'Comments',
                            body: vm.printData.clinicalData.comments
                        }]
                    }]
                });
                rowIndex++;
            }
            
            clinicalDataSection.row.push({
                rowIndex: rowIndex,
                layout: 'oneColumn-oneCell-t1',
                rowTopMargin: true,
                dynamicHeight: true,
                columns: [{
                    index: 1,
                    cells: [{
                        index: 1,
                        title: 'DME & Supplies',
                        body: vm.printData.clinicalData.supplies
                    }]
                }]
            });
            rowIndex++;
            clinicalDataSection.row.push({
                rowIndex: rowIndex,
                layout: 'oneColumn-oneCell-t1',
                rowTopMargin: true,
                columns: [{
                    index: 1,
                    cells: [{
                        index: 1,
                        title: 'Prognosis',
                        body: vm.printData.clinicalData.prognosis
                    }]
                }]
            });
            rowIndex++;
            clinicalDataSection.row.push({
                rowIndex: rowIndex,
                layout: 'oneColumn-oneCell-t1',
                rowTopMargin: true,
                dynamicHeight: true,
                columns: [{
                    index: 1,
                    cells: [{
                        index: 1,
                        title: 'Safety Measures',
                        body: vm.printData.clinicalData.safetyMeasures
                    }]
                }]
            });
            rowIndex++;
            clinicalDataSection.row.push({
                rowIndex: rowIndex,
                layout: 'oneColumn-oneCell-t1',
                rowTopMargin: true,
                dynamicHeight: true,
                columns: [{
                    index: 1,
                    cells: [{
                        index: 1,
                        title: 'Nutritional Requirements',
                        body: vm.printData.clinicalData.nutritionalRequirements
                    }]
                }]
            });
            rowIndex++;
            clinicalDataSection.row.push({
                rowIndex: 14,
                layout: 'oneColumn-oneCell-t1',
                rowTopMargin: true,
                rowHeight: 52,
                columns: [{
                    index: 1,
                    cells: [{
                        index: 1,
                        title: 'Functional Limitations',
                        body: vm.printData.clinicalData.functionalLimitations
                    }]
                }]
            });
            clinicalDataSection.row.push({
                rowIndex: 15,
                layout: 'oneColumn-oneCell-t1',
                dynamicHeight: true,
                columns: [{
                    index: 2,
                    cells: [{
                        index: 1,
                        title: 'Other',
                        body: vm.printData.clinicalData.functionalLimitationsOther
                    }]
                }]
            });
            rowIndex++;
            clinicalDataSection.row.push({
                rowIndex: rowIndex,
                layout: 'twoColumn-twoCell-t1',
                rowTopMargin: true,
                rowHeight: 66,
                columns: [{
                        index: 1,
                        cells: [{
                            index: 1,
                            title: 'Activities Permitted',
                            body: vm.printData.clinicalData.activitiesPermitted
                        }]
                    },
                    {
                        index: 2,
                        cells: [{
                            index: 1,
                            title: 'Other',
                            body: vm.printData.clinicalData.activitiesPermittedOther
                        }]
                    }
                ]

            });
            return clinicalDataSection;
        }

        function getTreatmentsSection() {
            var treatmentsSection = {
                sectionIndex: 3,
                header: 'Treatments',
                row: []
            };

            treatmentsSection.row.push({
                rowIndex: 1,
                layout: 'oneColumn-oneCell-t1',
                rowTopMargin: true,
                dynamicHeight: true,
                columns: [{
                    index: 1,
                    cells: [{
                        index: 1,
                        title: 'Medications',
                        body: vm.printData.treatments.medications
                    }]
                }]
            });
            if (vm.printData.treatments.isAllergyGrid) {
                treatmentsSection.row.push({
                    rowIndex: 2,
                    rowHeader: 'Allergies',
                    layout: 'oneColumn-oneCell-t2',
                    rowTopMargin: false,
                    dynamicHeight: true,
                    columns: [{
                        index: 1,
                        cells: [{
                            index: 1,
                            cellLayout: 'twoColumn-t1',
                            titleList: [{
                                substance: 'Substance',
                                reaction: 'Reaction'
                            }],
                            childCells: vm.printData.treatments.allergies
                        }]
                    }]
                });
            }
            else {
                treatmentsSection.row.push({
                    rowIndex: 2,
                    layout: 'oneColumn-oneCell-t1',
                    rowTopMargin: true,
                    dynamicHeight: true,
                    columns: [{
                        index: 1,
                        cells: [{
                            index: 1,
                            title: 'Allergies',
                            body: vm.printData.treatments.allergies
                        }]
                    }]
                });
            }
            treatmentsSection.row.push({
                rowIndex: 3,
                layout: 'oneColumn-oneCell-t1',
                rowTopMargin: true,
                dynamicHeight: true,
                columns: [{
                    index: 1,
                    cells: [{
                        index: 1,
                        title: 'Orders and Treatments',
                        body: vm.printData.treatments.ordersAndTreatments
                    }]
                }]
            });
            treatmentsSection.row.push({
                rowIndex: 4,
                layout: 'oneColumn-oneCell-t1',
                rowTopMargin: true,
                dynamicHeight: true,
                columns: [{
                    index: 1,
                    cells: [{
                        index: 1,
                        title: 'Goals and Outcomes',
                        body: vm.printData.treatments.goalsAndOutcomes
                    }]
                }]
            });

            return treatmentsSection;
        }


        function getSignatureSection() {

            var signatureSection = {
                sectionIndex: 4,
                header: '',
                row: []
            };


            var attendingPhysicianRow = {
                rowIndex: 2,
                layout: 'twoColumn-twoCell-t4',
                // dont use this property with other row objects
                interrupt: "auto", //
                rowTopMargin: true,
                columns: [{
                    index: 1,
                    cells: [{
                        index: 1,
                        title: 'Attending Physician’s Signature and Date Signed',
                        body: vm.printData.digitallySigned.physicianSignature
                    }]
                },
                    {
                        index: 2,
                        cells: [{
                            index: 1,
                            title: 'Date',
                            body: vm.printData.digitallySigned.physicianDate
                        }]
                    }
                ]

            };

            var attendingPhysicianDataRow = {
                rowIndex: 1,
                layout: 'threeColumn-fiveCell-t1',
                rowTopMargin: true,
                columns: [{
                    index: 1,
                    cells: [{
                        index: 1,
                        title: 'Primary Physician',
                        body: vm.printData.clinicalData.primaryPhysician.name
                    },
                        {
                            index: 2,
                            title: 'NPI',
                            body: vm.printData.clinicalData.primaryPhysician.npi
                        }
                    ]
                },
                    {
                        index: 2,
                        cells: [{
                            index: 1,
                            title: 'Address',
                            body: vm.printData.clinicalData.primaryPhysician.address
                        }]
                    },
                    {
                        index: 3,
                        cells: [{
                            index: 1,
                            title: 'Phone Number',
                            body: vm.printData.clinicalData.primaryPhysician.phoneNumber
                        },
                            {
                                index: 2,
                                title: 'Fax Number',
                                body: vm.printData.clinicalData.primaryPhysician.faxNumber
                            }
                        ]
                    }
                ]

            };
            
            if (vm.printData.printViewVersion >= 8) 
            {
                attendingPhysicianRow.rowHeight = 78;
            }

            var nurseSignatureRow = {
                rowIndex: 3,
                layout: 'twoColumn-twoCell-t4',
                rowTopMargin: false,
                columns: [{
                        index: 1,
                        cells: [{
                            index: 1,
                            title: 'Nurse Signature and Date of Verbal SOC Where Applicable',
                            body: vm.printData.digitallySigned.signature
                        }]
                    },
                    {
                        index: 2,
                        cells: [{
                            index: 1,
                            title: 'Date',
                            body: vm.printData.digitallySigned.date
                        }]
                    }
                ]
            };

            var certString = "";
            if (vm.printData.digitallySigned.certDisplay) {
                var printViewVersion = vm.printData.printViewVersion;
                if(printViewVersion >= 10) {
                    certString = vm.printData.digitallySigned.certStatement;
                } else if(printViewVersion === 8) {
                    certString = "I certify/recertify that this patient is confined to his/her home and needs intermittent skilled nursing care, physical therapy and/or speech therapy or continues to need occupational therapy. This patient is under my care, and I have authorized the services on this plan of care and I or another physician will periodically review this plan. I attest that the patient had a face-to-face encounter with an allowed provider type on ____________________________________ and the encounter was related to the primary reason for home health care.";
                } else {
                    certString = "I certify/recertify that this patient is confined to his/her home and needs intermittent skilled nursing care, physical therapy and/or speech therapy or continues to need occupational therapy. This patient is under my care, and I have authorized the services on this plan of care and I or another physician will periodically review this plan. I attest that a valid face-to-face encounter occured (or will occur) within timeframe requirements and it is related to the primary reason the patient requires home health services.";
                }
            }

            var certifyRow = {
                rowIndex: 4,
                layout: 'twoColumn-twoCell-t5',
                rowHeight: 96,
                rowTopMargin: false,
                columns: [{
                        index: 1,
                        cells: [{
                            index: 1,
                            title: certString
                        }]
                    },
                    {
                        index: 2,
                        cells: [{
                            index: 1,
                            title: 'Anyone who misrepresents, falsifies, or conceals essential information required for payment of Federal funds may be subject to fine, imprisonment, or civil penalty under applicable Federal laws.'
                        }]
                    }
                ]
            };

            if (vm.printData.printViewVersion === 8 
                || vm.printData.printViewVersion === 9) 
            {
                certifyRow.rowHeight = 105;
            } else if (vm.printData.printViewVersion >= 10) {
                certifyRow.rowHeight = 145;
                attendingPhysicianRow.interrupt = false;
                
            }
            
            if (vm.printData.printViewVersion >= 7) {
                nurseSignatureRow.rowTopMargin = true;
                attendingPhysicianRow.rowTopMargin = false;
                if (vm.targetDate < cutDate) {
                    signatureSection.row = [nurseSignatureRow, certifyRow, attendingPhysicianRow];
                } else {
                    signatureSection.row = [nurseSignatureRow, certifyRow, attendingPhysicianDataRow, attendingPhysicianRow];
                }
                
                
            } else {
                signatureSection.row = [attendingPhysicianRow, nurseSignatureRow, certifyRow];
            }

            return signatureSection;
        }
    }

})();

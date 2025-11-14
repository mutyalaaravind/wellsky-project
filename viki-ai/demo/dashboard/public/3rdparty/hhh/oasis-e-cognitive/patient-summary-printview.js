(function() {
    'use strict';

    angular
        .module('amng.patient-summary-printview', [
            'AMNG',
            'directives.kinnser.am-print-view.page-builder'
        ])
        .controller('COPPOCPatientSummaryPrintviewController', controller);

    controller.$inject = [];

    function controller() {
        var vm = angular.extend(this, {
            // members
            printData: {},
            boot: [],
            idSuffix: "PoCPS",
            pageTitle: {
                title: "Patient Plan of Care",
                patientName: "",
                certifiedPeriod: {
                    from: "",
                    to: ""
                }
            },

            // methods
            initialize: initialize
        });

        function initialize(printData) {
            vm.printData = printData;
            vm.pageTitle.patientName = printData.patientSummary.patientName;
            vm.pageTitle.certifiedPeriod = {
                from: printData.patientSummary.certificationStartDate,
                to: printData.patientSummary.certificationEndDate
            };

            // section object
            var patientSummaryConfig = {
                sectionIndex: 1,
                header: '',
                row: [{
                        rowIndex: 1,
                        layout: 'threeColumn-threeCell-t4',
                        rowTopMargin: false,
                        rowHeight: 52,
                        columns: [{
                                index: 1,
                                cells: [{
                                    index: 1,
                                    title: 'Patient\'s Name',
                                    body: printData.patientSummary.patientName
                                }]
                            },
                            {
                                index: 2,
                                cells: [{
                                    index: 1,
                                    type: 'date',
                                    title: 'Certification Period',
                                    childCells: [{
                                            index: 1,
                                            title: 'From',
                                            body: printData.patientSummary.certificationStartDate
                                        },
                                        {
                                            index: 2,
                                            title: 'To',
                                            body: printData.patientSummary.certificationEndDate
                                        }
                                    ]
                                }]
                            },
                            {
                                index: 3,
                                cells: [{
                                    index: 1,
                                    title: 'Date of Birth',
                                    body: printData.patientSummary.dateOfBirth
                                }]
                            }
                        ]

                    },
                    {
                        rowIndex: 2,
                        layout: 'threeColumn-threeCell-t4',
                        rowTopMargin: true,
                        rowHeight: 52,
                        columns: [{
                                index: 1,
                                cells: [{
                                    index: 1,
                                    title: 'Clinical Manager',
                                    body: printData.patientSummary.clinicalManagerName
                                }]
                            },
                            {
                                index: 2,
                                cells: [{
                                    index: 1,
                                    title: 'Agency Name',
                                    body: printData.patientSummary.clinicName
                                }]
                            },
                            {
                                index: 3,
                                cells: [{
                                    index: 1,
                                    title: 'Phone Number',
                                    body: printData.patientSummary.clinicPhoneNumber
                                }]
                            }
                        ]

                    },
                    {
                        rowIndex: 3,
                        layout: 'oneColumn-oneCell-t1',
                        rowTopMargin: true,
                        dynamicHeight: true,
                        columns: [{
                            index: 1,
                            cells: [{
                                index: 1,
                                title: 'Orders and Treatments',
                                body: printData.patientSummary.ordersAndTreatmentsText
                            }]
                        }]
                    },
                    {
                        rowIndex: 5,
                        layout: 'oneColumn-oneCell-t1',
                        rowTopMargin: true,
                        dynamicHeight: true,
                        columns: [{
                            index: 1,
                            cells: [{
                                index: 1,
                                title: 'Medications',
                                body: printData.patientSummary.medications
                            }]
                        }]
                    },
                    {
                        rowIndex: 5,
                        layout: 'oneColumn-oneCell-t1',
                        rowTopMargin: true,
                        dynamicHeight: true,
                        columns: [{
                            index: 1,
                            cells: [{
                                index: 1,
                                title: 'Other Pertinent Information',
                                body: printData.patientSummary.otherPertinentInformationText
                            }]
                        }]
                    }
                ]
            };
            vm.boot.push(patientSummaryConfig);
        }

    }

})();
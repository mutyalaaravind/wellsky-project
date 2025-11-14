(function () {
    'use strict';

    var applicationSettingService = angular.module('services.util.application-setting', []);


    applicationSettingService.factory('ApplicationSettingService', [
        '$http',
        function ($http) {
            var ApplicationSettingService = {},
                applicationServicePath = '/API/services/ApplicationSetting/ApplicationSettingService.cfc';

            var financialsURL;
            var gcpFinancialsURL;
            var oasisServiceURL;
            var gcpOasisServiceURL;
            var corporationManagerUrl;
            var referralManagerURL;
            var newInsuranceUrl;
            var gcpInsuranceUrl;
            var financialsCloudApiUrl;
            var evvTransactionManagerUrl;
            var gcpEvvTransactionmanagerURL;
            var billedUnbilledManagedCareReportUrl;
            var enterprisePatientMasterUrl;
            var enterprisePatientSolution;
            
            /** To get the Financials Application URL based on the environment */
            ApplicationSettingService.getFinancialsURL = function () {
                var url = applicationServicePath + '?method=getFinancialsApplicationVariable';

                if (financialsURL) {
                    return financialsURL;
                } else {
                    return $http.get(url).
                        then(function (result) {
                            financialsURL = result.data;
                            return financialsURL;
                        });
                }
            };


            ApplicationSettingService.getFinancialsCloudApiURL = function(){
                var url = applicationServicePath + '?method=getFinancialsCloudApiURL';
                if (financialsCloudApiUrl) {
                    return financialsCloudApiUrl;
                } else {
                    return $http.get(url).
                        then(function (result) {
                            financialsCloudApiUrl = result.data;
                            return financialsCloudApiUrl;
                        });
                }
            };

                /** To get the GCP Financials Application URL based on the environment */
            ApplicationSettingService.getGcpFinancialsURL = function () {
                var url = applicationServicePath + '?method=getGcpFinancialsApplicationVariable';

                if (gcpFinancialsURL) {
                    return gcpFinancialsURL;
                } else {
                    return $http.get(url).
                        then(function (result) {
                            gcpFinancialsURL = result.data;
                            return gcpFinancialsURL;
                        });
                }
            };

            /** To get the Corporation Manager Application URL based on the environment */
            ApplicationSettingService.getCorporationManagerUrl = function () {
                var url = applicationServicePath + '?method=getCorporationManagerUrlApplicationVariable';

                if (corporationManagerUrl) {
                    return corporationManagerUrl;
                } else {
                    return $http.get(url).
                        then(function (result) {
                            corporationManagerUrl = result.data;
                            return corporationManagerUrl;
                        });
                }
            };

            /** To get the Oasis Service UI Application URL based on the environment */
            ApplicationSettingService.getOasisServiceURL = function () {
                if (oasisServiceURL) {
                    return oasisServiceURL;
                } else {
                    return '/clinical/oasis-service-ui';
                }
            };

            /** To get the GCP Oasis Service UI Application URL based on the environment */
            ApplicationSettingService.getGcpOasisServiceURL = function () {
                if (gcpOasisServiceURL) {
                    return gcpOasisServiceURL;
                } else {
                    return '/wsh/clinical/oasis-service-ui';
                }
            };
            
            var noeURL;
            ApplicationSettingService.getNOEURL = function () {
                var url = applicationServicePath + '?method=getNOEApplicationVariable';

                if (noeURL) {
                    return noeURL;
                } else {
                    return $http.get(url).
                        then(function (result) {
                            noeURL = result.data;
                            return noeURL;
                        });
                }
            };

            var GcpNoeURL;
            ApplicationSettingService.getGcpNOEURL = function () {
                var url = applicationServicePath + '?method=getGcpNOEApplicationVariable';

                if (GcpNoeURL) {
                    return GcpNoeURL;
                } else {
                    return $http.get(url).
                        then(function (result) {
                            GcpNoeURL = result.data;
                            return GcpNoeURL;
                        });
                }
            };

            ApplicationSettingService.getReferralManagerURL = function () {
                var url = applicationServicePath + '?method=getReferralManagerApplicationVariable';

                if (referralManagerURL) {
                    return referralManagerURL;
                } else {
                    return $http.get(url).
                        then(function (result) {
                            referralManagerURL = result.data;
                            return referralManagerURL;
                        });
                }
            };

            ApplicationSettingService.getApplicationSettingByName = function (applicationSettingName) {
                var url = applicationServicePath + '?method=getApplicationSettingByName&settingName=' + applicationSettingName;
                
                return $http.get(url).
                    then(function (result) {
                        var appSetting = result.data;
                        return appSetting;
                    });                
            };

            /** To get the New Insurance Application URL based on the environment */
            ApplicationSettingService.getNewInsuranceUrl = function () {
                var url = applicationServicePath + '?method=getNewInsuranceApplicationVariable';
            
                if (newInsuranceUrl) {
                    return newInsuranceUrl;
                } else {
                    return $http.get(url).
                        then(function (result) {
                            newInsuranceUrl = result.data;
                            return newInsuranceUrl;
                        });
                }
            };

            /** To get the GCP Insurance Application URL based on the environment */
            ApplicationSettingService.getGcpInsuranceUrl = function () {
                var url = applicationServicePath + '?method=getGcpInsuranceApplicationVariable';
            
                if (gcpInsuranceUrl) {
                    return gcpInsuranceUrl;
                } else {
                    return $http.get(url).
                        then(function (result) {
                            gcpInsuranceUrl = result.data;
                            return gcpInsuranceUrl;
                        });
                }
            };

            /** To get the New Insurance Application URL based on the environment */
            ApplicationSettingService.getEvvTransactionManagerUrl = function () {
                var url = applicationServicePath + '?method=getEvvtransactionManagerApplicationVariable';
            
                if (evvTransactionManagerUrl) {
                    return evvTransactionManagerUrl;
                } else {
                    return $http.get(url).
                        then(function (result) {
                            evvTransactionManagerUrl = result.data;
                            return evvTransactionManagerUrl;
                        });
                }
            };

            /** To get the GCP Insurance Application URL based on the environment */
            ApplicationSettingService.getGcpEvvTransactionmanagerURL = function () {
                var url = applicationServicePath + '?method=getGcpEvvtransactionManagerApplicationVariable';
            
                if (gcpEvvTransactionmanagerURL) {
                    return gcpEvvTransactionmanagerURL;
                } else {
                    return $http.get(url).
                        then(function (result) {
                            gcpEvvTransactionmanagerURL = result.data;
                            return gcpEvvTransactionmanagerURL;
                        });
                }
            };

            ApplicationSettingService.getBilledUnbilledManagedCareReportUrl = function () {
                var url = applicationServicePath + '?method=getBilledUnbilledManagedCareReportUrl';
                return $http.get(url).
                    then(function (result) {
                        billedUnbilledManagedCareReportUrl = result.data;
                        return billedUnbilledManagedCareReportUrl;
                    });
            };

            /** To get the EnterprisePatientMasterUrl & SolutionName Application URL based on the environment */
            ApplicationSettingService.getEnterprisePatientMasterUrl = function () {
                var url = applicationServicePath + '?method=getEnterprisePatientMasterUrlApplicationVariable';
            
                if (enterprisePatientMasterUrl) {
                    return enterprisePatientMasterUrl;
                } else {
                    return $http.get(url).
                        then(function (result) {
                            enterprisePatientMasterUrl = result.data;
                            return enterprisePatientMasterUrl;
                        });
                }
            };

            ApplicationSettingService.getEnterprisePatientSolution = function () {
                var url = applicationServicePath + '?method=getEnterprisePatientSolutionApplicationVariable';
            
                if (enterprisePatientSolution) {
                    return enterprisePatientSolution;
                } else {
                    return $http.get(url).
                        then(function (result) {
                            enterprisePatientSolution = result.data;
                            return enterprisePatientSolution;
                        });
                }
            };

            return ApplicationSettingService;
        }
    ]);
})();

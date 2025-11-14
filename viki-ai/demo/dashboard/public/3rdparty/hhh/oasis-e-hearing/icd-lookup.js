(function() {
	'use strict';

	var icdLookup = angular.module('directives.kinnser.icd-lookup', [
			'resources.RESTResource', 'resources.icd','directives.kinnser.infinate-scroll'
		]);


	icdLookup.directive('kIcdLookup',['$document', function($document) {
		return {
			restrict: 'E',
			templateUrl: '/EHR/scripts/directives/kinnser/icd-lookup/icd-lookup.html?61f6e73ad05ccba0',
			scope:{
				userKey: '@',
				codeType: '@',
				hideCodeInput: '@',
				displayState: '@',
				selectedCode: '=',
				searchText: '=',
				listIcdKey: '=',
				uniqueName: '@',
				uniqueNameCode: '@',
				lookupSize: '@',
				skipped: '@',
				context: '@',
				targetDate: '@',
				placeHolderText: '@',
				inputSize: '@',
                clearLastResult: '@',
                clinicKey: '@',
                pdgmWarnCode: '@',
			},
			link: function(scope, element, attr){
				// this closes all "popped up" divs when user clicks outside of this instance of the directive
				$document.bind('click', function(event){
					var isClickedElementChildOfMe = element.find(event.target).length > 0;

					if(isClickedElementChildOfMe){
						return;
					}

					scope.showMenu = false;
					scope.showOptions = false;
					scope.$apply();
				});

			},
			controller: [
                '$scope',
                'PdgmValidationService',
				'ICD',
				'$q',
				'ClinicSettingService',
				'$timeout',
                function ($scope, PdgmValidationService, ICD, $q, ClinicSettingService, $timeout) {

				$scope.timeout = null;
                $scope.isIncludeInPDGM = true;
                $scope.hasClinicSettingEnable = ClinicSettingService.hasClinicSetting({ StaticVariable: 'ENABLEWARMICD10NONPDGM' })
				$scope.lookupSize = angular.isUndefined($scope.lookupSize) ? 'large' : $scope.lookupSize;
				$scope.inputSizeMax = angular.isUndefined($scope.inputSize) ? '60' : $scope.inputSize;
				$scope.clearLastResult = angular.isUndefined($scope.clearLastResult) ? 'false' : $scope.clearLastResult;
				$scope.context = angular.isUndefined($scope.context) ? '' : $scope.context;
				$scope.loadedData = [];
				$scope.infinateIndex = 0;
				$scope.infinateInterval = 10;
				$scope.doingAutoLookup = false;
				if ($scope.targetDate == undefined) {
					$scope.targetDate = "";
                }

                $scope.pdgmValidation = function () {
                    if ($scope.clinicKey) {
                        PdgmValidationService.validateICD10CodeClinicOnly($scope.clinicKey, $scope.selectedCode, $scope.targetDate).then(function (data) {
                            $scope.isIncludeInPDGM = data.data.ISINCLUDEDINPDGM;
                            if ($scope.isIncludeInPDGM) {
                                $($scope.pdgmWarnCode).hide();
                            } else {
                                $($scope.pdgmWarnCode).show();
                            }
                        });
                    }
                }

                if ($scope.selectedCode) {
                    $scope.pdgmValidation();
                }

				//If the target date value change the controller send a changeTargetDate event with the new value
				$scope.$on('changeTargetDate', function(e, newTargetDate){
					$scope.targetDate = newTargetDate;
		        });
				
				// clinic setting that determines whether to show broad or specific code search results
				var showSpecific = ClinicSettingService.hasClinicSetting({StaticVariable: 'ICD10SEARCHSPECIFICCODE'});

				if(showSpecific){
					var tempValue = ClinicSettingService.getClinicSetting({StaticVariable: 'ICD10SEARCHSPECIFICCODE'}).SettingValue;
					showSpecific = tempValue === '' ? true : tempValue;
				}

				//Hide crosswalk, in this case for procedure codes
				$scope.crossWalkDisabled = function(){
				    return $scope.codeType == 'procedure' || $scope.codeType == 'dxNoCrosswalk';
				};

				// private function to get filtered ICD Codes
				var doAutoLookup = function(){

					// reset index
					$scope.infinateIndex = 0;
					var panels = angular.element($(document.querySelectorAll('.ks-icd-tool-container')));//[0].scrollTop = 0;

					angular.forEach(panels,function(item){
						item.scrollTop = 0;
					});

					var deferred = $q.defer();
					var lookupLength = 4;
					var lookupVersion = 10; //$scope.lookupMode === 0 ? 10 : 9; // KH-7113: Locked to ICD-10


					// check to see if user is typing in a code. If search text length is 3 and contains a number, its a code.
					if($scope.searchText.length >= 3 && $scope.searchText.match(/\d+/g) !== null){
						lookupLength = 3;
					}

					// don't get anything if not long enough
					if($scope.searchText.length < lookupLength){
						if($scope.lookupMode === 1){
						    $scope.goBack();
						};

						if($scope.favorites.length === 0){
							$scope.showOptions = false;
						}
						deferred.resolve([]);
					}
					// grab the filtered ICD codes from the server
					// anything else will be filtered on the client side via angular filter
					else if($scope.searchText.length >= lookupLength){
						$scope.loading = true;
                        if ($scope.codeType === "procedure"){
                                ICD.getProcedureCodes({q: $scope.searchText, version: lookupVersion, index: $scope.infinateIndex, interval: $scope.infinateInterval}).then(function(data){
                                    $scope.showOptions = true;
                                    $scope.infinateIndex = $scope.infinateIndex + 1
                                    deferred.resolve(data);
                                });
                            }
                            else {
                            	if(lookupLength === 3){

                            		if(lookupVersion === 9){
                            			ICD.getDiagnosisCodes({q: $scope.searchText, version: lookupVersion, showSpecific: false, index: $scope.infinateIndex, interval: $scope.infinateInterval}).then(function(data){
		                                    $scope.showOptions = true;
		                                    $scope.infinateIndex = $scope.infinateIndex + 1
		                                    deferred.resolve(data);
	                                	});
                            		}
                            		else{
	                            		ICD.getDiagnosisCodeByCode({q: $scope.searchText, showSpecific: showSpecific, index: $scope.infinateIndex, interval: $scope.infinateInterval, targetDate: $scope.targetDate}).then(function(data){
		                                    $scope.showOptions = true;
		                                    $scope.infinateIndex = $scope.infinateIndex + 1
		                                    deferred.resolve(data);
	                                	});
	                                }
                            	}
                            	else{

                            		ICD.getDiagnosisCodes({q: $scope.searchText, version: lookupVersion, showSpecific: showSpecific, index: $scope.infinateIndex, interval: $scope.infinateInterval, targetDate: $scope.targetDate}).then(function(data){
	                                    $scope.showOptions = true;
	                                    $scope.infinateIndex = $scope.infinateIndex + 1
	                                    deferred.resolve(data);
                                	});
                            	}

                            }

                    }

					$scope.currentLookupLength = $scope.searchText.length
					return deferred.promise;
				};

				// lookup mode state. 0 = normal lookup, 1 = crosswalk
				$scope.lookupMode = 0;

				// flag to know if a popup should be shown for adjusting admission
				$scope.admissionFlag = 0;

				// show or hide options selection menu
				$scope.showOptions = false;

				// show or hide icd version menu
				$scope.showMenu = false;

				// current length of lookup string
				$scope.currentLookupLength = 0;

				// current ICD codes filtered by lookup string
				$scope.searchResults = [];

				// users favorite ICD codes
				$scope.favorites = null;

				// variable to store current favorite codes to show/hide add favorites link
				$scope.favoriteCodes = [];

				// show the icd 10 equivelent div
				$scope.showICD10Header = false;

				// place holder array to retain icd 9 search results
				$scope.icd9Placeholder = null;

				// whether we are in a loading state or not, to apply loading style
				$scope.loading = false;

				// sets selected code based on selection from option menu
				$scope.doCodeSelect = function(selectedICD, isFav){

					// default display to just description
					var displayString = selectedICD.icdDescription;


					// if displayState is supplied in attributes, set displayString accordingly
					if($scope.displayState === 'code'){
						displayString = selectedICD.icdCode;
					}
					else if($scope.displayState === 'description'){
					    displayString = selectedICD.icdAbbreviation;
					}
					else if ($scope.displayState === 'both'){
						displayString = selectedICD.icdCode + ' - ' + selectedICD.icdDescription;
					}


					if($scope.lookupMode === 0){
						$scope.selectedCode = selectedICD.icdCode;
						$scope.searchText = displayString;
						$scope.showOptions = false;
						$scope.listIcdKey = selectedICD.listICDKey;
					}
					else{

						if(!$scope.showICD10Header && !isFav){
							$scope.showICD10Header = true;
							$scope.admissionFlag = 1;
							ICD.getICD10ByICD9Code({diagnosisCode: selectedICD.icdCode, version: 10}).then(function(data){
								$scope.icd9Placeholder = $scope.searchResults;
								$scope.searchResults = data;
								$scope.admissionFlag = 0;
							});
						}

						else{
							$scope.selectedCode = selectedICD.icdCode;
							$scope.searchText = displayString;
							$scope.showOptions = false;
							$scope.listIcdKey = selectedICD.listICDKey;
							$scope.showICD10Header = false;
							$scope.admissionFlag = 0;
						}
					}
                    $scope.$emit('codeSelected', selectedICD);

                    if ($scope.hasClinicSettingEnable) {
                        $scope.pdgmValidation();
                    }
				};

				// every time the scroll bar hits max, load more data based on infinate interval
				$scope.loadNextResults = function(){
					ICD.getDiagnosisCodes(
						{
							q: $scope.searchText, 
							version: 10, //version: $scope.lookupMode === 0 ? 10 : 9, // KH-7113 : Locked to ICD10
							showSpecific: showSpecific, 
							index: $scope.infinateIndex, 
							interval: $scope.infinateInterval
						}
					).then(function(data){
							angular.forEach(data,function(result){
								$scope.searchResults.push(result);
							});

							$scope.infinateIndex = $scope.infinateIndex + 1
                	});
				}

				// applies filter based on lookup string
				$scope.doLookup = function(){
					if($scope.timeout){ //if there is already a timeout in process cancel it
						$timeout.cancel($scope.timeout);
					}

					$scope.timeout = $timeout(function(){
						$scope.showMenu = false;
						doAutoLookup().then(function(data){
							// if data is less than infintate interval just display it

							$scope.searchResults = data;
							// if its larger then grab the first set of data
							$scope.loading = false;
							$scope.timeout = null;
						});
					},1000);

				};

				// gets user favorite ICD codes
				$scope.loadFavorites = function(){

					if ($scope.clearLastResult) {
						$scope.searchResults = [];
					}
					ICD.getFavoritesList({userKey: $scope.userKey, version: 10, targetDate: $scope.targetDate}).then(function(data){
						$scope.favorites = data;
						$scope.favoriteCodes = [];
						angular.forEach(data, function(fav){
							$scope.favoriteCodes.push(fav.icdCode);
						});

						if(data.length > 0){
							$scope.showOptions = true;
						}
					});

				};

				// open/close mode menu
				$scope.toggleMenu = function(){
					if(!($scope.skipped === 'true')){
						$scope.showMenu = !$scope.showMenu
						$scope.showOptions = false;
					}
				};

				// runs when user makes mode menu selection
				$scope.toggleMenuSelection = function(mode){
					return; // KH-7113 : disable crosswalk and lock to ICD 10
					if($scope.lookupMode === mode){
						$scope.toggleMenu();
						return;
					}

					if(mode === 0){
						$scope.showICD10Header = false;
					}

					$scope.lookupMode = mode;
					$scope.admissionFlag = mode;
					$scope.selectedCode = null;
					$scope.searchResults = [];
					$scope.searchText = '';
					$scope.toggleMenu();
					$scope.icd9Placeholder = null;
				};

				// hide/show add favorites link based on what is populated in favorites array
				$scope.showAddFavorites = function(favCode){
					return $scope.favoriteCodes.indexOf(favCode) === -1;
				};

				// adds favorite for user
				$scope.addFavorite = function(code){
					ICD.addFavoriteDiagnosisCode({
						userKey: $scope.userKey,
						diagnosisCode: code.icdCode
					}).then(function(data){
						$scope.favorites = null;
						$scope.loadFavorites();
					});
				};

				// removes favorite for user
				$scope.removeFavoriteDiagnosisCode = function(code){
					ICD.removeFavoriteDiagnosisCode({
						userKey: $scope.userKey,
						diagnosisCode: code.icdCode,
						diagnosisFavoritesKey: code.favoritesKey
					}).then(function(data){
						$scope.favorites = null;
						$scope.loadFavorites();
					});
				};

				// tranfer from icd 10 equivelant div to
				$scope.goBack = function(){
					$scope.admissionFlag = 1;
					$scope.showICD10Header = false;
					$scope.searchResults = $scope.icd9Placeholder;
					$scope.lookupMode = 1;
				};

				// applys styling to search text
				$scope.displayResultRow = function(text, searchText){
					return text.replace(
						new RegExp(searchText.replace(/\\/g, ''), 'gi'),
						'<span class="ks-search-string-highlight">$&</span>'
					);
				}


				// format id attribute for form system
				$scope.formatIDAttribute = function(){
                    if($scope.uniqueName){
                        return $scope.uniqueName.substring(0,$scope.uniqueName.indexOf('|'));
                    }
                    else
                        return;
                }

				// format name attribute for form system
				$scope.formatNameAttribute = function(id, type){
                    if($scope.uniqueName.indexOf('isOasis') === -1){
                        if(id){
                            return $scope.uniqueName
                                .replace($scope.uniqueName.substring(0,$scope.uniqueName.indexOf('|')), $scope.uniqueName.substring(0,$scope.uniqueName.indexOf('|')) + '_id')
                                .replace('[type]', type);
                        }
                        else
                            return $scope.uniqueName.replace('[type]', type);
                    }
                    else
                        return;
				}
				
				if($scope.placeHolderText) {
					$scope.$watch('placeHolderText', function(newVal, oldVal) {
						if(newVal) {
							setTimeout(function(){
								$("[ng-model='searchText']").attr('placeholder', newVal);
							}, 500);
						}
					});
				}
            }]
		};
	}]);
})();

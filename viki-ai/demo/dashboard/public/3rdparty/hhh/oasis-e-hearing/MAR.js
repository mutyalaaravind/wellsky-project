var MARModule = angular.module('MAR', [

]);

MARModule.controller('MARController', [
	'$scope',
	'$route',
	function ($scope, $route) {

		// can use this to point to private functions and unit test.
		var $this = this;

		// need to initialize medications array here
		$scope.medications = [];

		// add new medication object in array
		$scope.addMedication = function () {
			if ($scope.medsCounter < 20) {
				var med = $this.getMedObject(-1);
				$scope.medications.push(med);
				$scope.medsCounter++;
			}
		};

		// remove an object from array
		$scope.removeMedication = function () {
			if ($scope.medsCounter > 1) {
				$scope.medications.pop();
				$scope.medsCounter--;
			}
		};

		//sets indexing identifier after the elements 
		$scope.setIndex = function (index) {
			if (index == 0) {
				return '';
			}
			else {
				return '_IDX_' + index;
			}

		}

		$scope.isHospiceClinic = function (clinicTypeKey) {
			if (clinicTypeKey == 15) {
				return 'Hospice';
			}
			else {
				return '';
			}
		}

		// this watches questionValueStruct to initialize data on the form load
		$scope.$watch('questionValueStruct', function (newValue, oldValue) {
			$this.buildMedicationsArray(newValue);
		});

		// method to build meds array on the initial form load
		$this.buildMedicationsArray = function (valueString) {
			// to make sure array does not have any existing records
			$scope.medications = []; 
			//Initialize the first section if form is empty or if form is opened for the first time (REQUEST.prefill = TRUE)
			if (angular.equals("{}", valueString) || $scope.isPrefill === "true") {
				var med = $this.getMedObject(-1); // -1 returns empty object
				$scope.medications.push(med);
				$scope.medsCounter = 1;
			}
			else {
				var valueObj = JSON.parse(valueString);
				// in case when valueString not empty but FRM_MEDSCOUNTER doesn't exist
				if (valueObj.hasOwnProperty('FRM_MEDSCOUNTER') && parseInt(valueObj.FRM_MEDSCOUNTER) > 0) {
					var index = valueObj.FRM_MEDSCOUNTER;
					for (var i = 0; i < index; i++) {
						var med = $this.getMedObject(i, valueObj);
						$scope.medications.push(med);
					}
				}
				// this will preserve the saved medication before multiple sections got introduced
				else if (valueObj.hasOwnProperty('FIRSTTIMEDOCUMENTSAVED') && valueObj.FIRSTTIMEDOCUMENTSAVED.length !== 0 ) {
					var med = $this.getMedObject(0, valueObj);
					$scope.medications.push(med);
					$scope.medsCounter = 1;
				}
				// if no medications exist insert empty object 
				else {
					var med = $this.getMedObject(-1);
					$scope.medications.push(med);
					$scope.medsCounter = 1;
				}
			}
		}

		// this returns medication object by index to inset in array
		$this.getMedObject = function (index, obj) {
			if (index == -1) {
				return {
					frm_marmedication: '',
					frm_mardose: '',
					frm_marroute: '',
					frm_marfrequency: '',
					frm_marprnreason: '',
					frm_marlocation: '',
					frm_marresponse: '',
					frm_marcomment: ''
				};
			}
			else {
				return {
					frm_marmedication: obj.hasOwnProperty('FRM_MARMEDICATION' + $scope.setIndex(index)) ? obj['FRM_MARMEDICATION' + $scope.setIndex(index)] : '',
					frm_mardose: obj.hasOwnProperty('FRM_MARDOSE' + $scope.setIndex(index)) ? obj['FRM_MARDOSE' + $scope.setIndex(index)] : '',
					frm_marroute: obj.hasOwnProperty('FRM_MARROUTE' + $scope.setIndex(index)) ? obj['FRM_MARROUTE' + $scope.setIndex(index)] : '',
					frm_marfrequency: obj.hasOwnProperty('FRM_MARFREQUENCY' + $scope.setIndex(index)) ? obj['FRM_MARFREQUENCY' + $scope.setIndex(index)] : '',
					frm_marprnreason: obj.hasOwnProperty('FRM_MARPRNREASON' + $scope.setIndex(index)) ? obj['FRM_MARPRNREASON' + $scope.setIndex(index)] : '',
					frm_marlocation: obj.hasOwnProperty('FRM_MARLOCATION' + $scope.setIndex(index)) ? obj['FRM_MARLOCATION' + $scope.setIndex(index)] : '',
					frm_marresponse: obj.hasOwnProperty('FRM_MARRESPONSE' + $scope.setIndex(index)) ? obj['FRM_MARRESPONSE' + $scope.setIndex(index)] : '',
					frm_marcomment: obj.hasOwnProperty('FRM_MARCOMMENT' + $scope.setIndex(index)) ? obj['FRM_MARCOMMENT' + $scope.setIndex(index)] : ''
				}
			}
		}

	}]
);

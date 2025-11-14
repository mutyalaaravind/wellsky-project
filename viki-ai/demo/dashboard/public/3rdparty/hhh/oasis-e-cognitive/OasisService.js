class OasisService {
	
	
	constructor(clinicKey,clinicBranchKey,listTaskTypeKey,rfa){
		this.clinicKey = clinicKey;
		this.clinicBranchKey = clinicBranchKey;
		this.listTaskTypeKey = listTaskTypeKey;
		this.rfa = rfa;
	}	
	
	//Transform the raw data inputs to key/value pairs and reduce the set to only items that the OasisService cares about
	transformData(formStruct) {
		var processOASISPath = ux.statePersistance.addSessionCacheKeyToURL('/AM/OASIS/OASISE/processOasis.cfc?method=transformDataForOasisService');
		return $.ajax({
			type: "POST",
			url: processOASISPath,
			data: {
				formCollection: JSON.stringify(formStruct)
			},
			async: false,
			dataType: 'json',
			success: function(data){
				var result = data;
			},
			error: function(xhr, error){
				console.log(error);
				console.log(xhr);
				var result = {};
			}
		})
	}
	
	//Get the environments serviceurl
	getServiceUrl() {
		var helpServiceURL = ux.statePersistance.addSessionCacheKeyToURL('/packages/KSI/OasisService/OasisData.cfc?method=getSaveOasisDataEndpoint&OasisVersion=E');
		return $.ajax({
			type: "GET",
			url: helpServiceURL,
			token: $.cookie('EHRTOKEN'),
			async: false,
			dataType: 'json',
			success: function(data){
				var result = data;
				},
			error: function(xhr, error){
				console.log(error);
				console.log(xhr);
				var result = {};
				}
			})
	}

	/**
	* Convert ListTaskTypeKey from the ListTaskType table into a Discipline defined in M0080
	* @param {!number} listTaskTypeKey - the ListTaskType key defined in the patient task
	* @return {number} - an integer representation of the discipline value defined in M0080
	*/
	listTaskTypeKeyToM0080DisciplineConverter(listTaskTypeKey) {
		switch (listTaskTypeKey) {
			case 1: case '1': return 1;
			case 3: case '3': return 2;
			case 7: case '7': return 3;
			case 6: case '6': return 4;
			default: return 0;
		}
	};

		
	writeToOasisService(formStruct){
		var result = {'resultType':'','resultData':{}};
		//When both service calls are complete, 
		$.when(this.transformData(formStruct),this.getServiceUrl()).done(function(oasisData,serviceUrl){
			//replacing all '/' with '_' so that url's wont break
			var pageName = oasisData[0].pageName.replaceAll('/','_');
			var patientTaskKey = oasisData[0].fPatientTaskKey;
			var sentDateTime = moment().utc();
			var insertedBy = oasisData[0].amUserKey;
			var formData = oasisData[0];
			var discipline = this.listTaskTypeKeyToM0080DisciplineConverter(this.listTaskTypeKey);
			
			$.ajax({
				type: "POST",
				url: serviceUrl[0],
				data: JSON.stringify({
						"RefPatientTaskKey": patientTaskKey,
						"SentDateTime": sentDateTime,
						"InsertedBy": insertedBy,
						"FormData":formData,
						"Rfa": this.rfa,
						"Section": pageName,
						"Discipline": discipline
					}),
				headers: {  
					"Content-Type": "application/json",
					"clinicKey":this.clinicKey,
					"clinicBranchKey":this.clinicBranchKey,
					"Access-Control-Allow-Origin" : "*"
				},
				async: false,
				success: function(data){
					result = {'resultType':'pass','resultData':data};
				},
				error: function(xhr, error){
					console.log(xhr);
					console.log(error);
					var errorMessage = xhr.statusText;
					if (xhr.responseText !== undefined){
						errorMessage += ' - ' + xhr.responseText; 
					}
					result = {'resultType':'fail','resultData':{'errorMessage': errorMessage}};
				}
			})
		}.bind(this));	
		return result;	
	}	
}
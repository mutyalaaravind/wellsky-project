var CreateNewEpisodeValidation = (function() {
	//private object to hold information about the validation of a patient's insurance
	var oPatientInsurance = {
		validationQuery: 'a.createNewEpisode', //jQuery selector
		bUseUXDialog: true, //do we have access to the ux namespace? assume so for now...
		sMissingActiveInsurance: 'An active insurance must be added to this patient before an episode can be created.' //message to display to the user
	};
	
	return {
		patientInsuranceValidationQuery: oPatientInsurance.validationQuery,
		
		createLegacyDialog: function(sDialogID) {
			//set UXDialog flag and append other useful data to the patient insurance object
			oPatientInsurance.bUseUXDialog = false;
			oPatientInsurance.sLegacyDialogID = sDialogID;
			
			//create HTML for a dialog, obviously we can not use ux.dialog...
			$('<div id="' + oPatientInsurance.sLegacyDialogID.slice(1) + '" style="display: none;"></div>').appendTo('body');
			
			//so, create our own
			$(oPatientInsurance.sLegacyDialogID).dialog({
				bgiframe:true,
				height:200,
				width:500,
				modal: true,
				autoOpen:false,
				buttons:{ //only feature a single button as this is an alert to the user
					OK: function(){
						$(this).dialog('close');
					}
				}
			});
			
			//setup the HTML for said dialog; include message from patient insurance object
			$(oPatientInsurance.sLegacyDialogID).html(oPatientInsurance.sMissingActiveInsurance);
		},
		
		callServerValidation: function(oDOMElement) {
			//look for active insurances for a patient or set of patients
			$.ajax({
				type: 'GET',
				url: '/AM/Patient/PatientProxy.cfc',
				data: {
					method: 'hasActivePatientInsurance',
					patientKey: oDOMElement.attr('data-patientKey')
				},
				dataType: 'json',
				success: function(data){
					if( data.hasActiveInsurance ){ //active insurances found!
						window.location = ux.statePersistance.addSessionCacheKeyToURL(oDOMElement.attr('href')); //redirect to create an episode
					} else{ //otherwise explain to user why we cannot continue on to creating a new episode
						if( oPatientInsurance.bUseUXDialog ){
							ux.dialog.alert(oPatientInsurance.sMissingActiveInsurance); //ux.dialog (newer implementation)
						} else{
							$(oPatientInsurance.sLegacyDialogID).dialog('open'); //use dialog we just created (legacy implementation)
						}
					}
				}
			});
		}
	};
})();


$(document).ready(function() {
	if( typeof window.ux.dialog !== 'object' ){ //check for access to the ux.dialog
		CreateNewEpisodeValidation.createLegacyDialog('#inactiveInsuranceDialog'); //ux.dialog not present, ready a dialog object
	}
	
	//trigger for validation
	$(CreateNewEpisodeValidation.patientInsuranceValidationQuery).click(function(oEvent) {
		oEvent.preventDefault(); //prevent anchor tag's redirect
		
		oCreateNewEpisodeLink = $(this); //hold jQuery's link object here
		CreateNewEpisodeValidation.callServerValidation(oCreateNewEpisodeLink); //check a patient's insurance information
	});
});
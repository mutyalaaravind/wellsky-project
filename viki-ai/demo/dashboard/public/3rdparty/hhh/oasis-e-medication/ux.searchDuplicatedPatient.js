/**
 * Search Patient Dialog functionality
 *
 */
var searchDuplicatedPatient = (function(){
	
	//Private
	var formatSearchResultMessage = function(patientData) {
		var html = '<h4>Are you entering one of the following patients?</h4></br>';

		  html += '<table class="table table-hover table-bordered table-striped"><tr><th>Last Name</th><th>First Name</th><th>Middle Initial</th><th>Date of Birth</th><th>SSN</th><th>MRN</th><th>Last Discharge Date</th><th>&nbsp;</th></tr>';

		  //Loop the results adding a row for each
		  for(i=0;i<patientData.length;i++) {
		    html += '<tr>';
		    html += '<td>' + patientData[i].LASTNAME + '</td>';
		    html += '<td>' + patientData[i].FIRSTNAME + '</td>';
		    html += '<td>' + patientData[i].MIDDLEINITIAL + '</td>';
		    html += '<td>' + patientData[i].DOB + '</td>';
		    html += '<td>' + patientData[i].SSN + '</td>';
		    html += '<td>' + patientData[i].MRN + '</td>';
			html += '<td>' + patientData[i].LASTDISCHARGEDATE + '</td>';
		    html += '<td><a class="btn" href="/EHR/#/AM/episode-list/patient/'+patientData[i].PATIENTKEY+'">Select Patient</a></td>';
		    html += '</tr>';
		  }

		  html += '</table>';
		  return html;
	};
	
	var searchPatients = function(firstName, lastName, clinicBranchKeyList, divDialog) {
		
		if (validateNameForSearch(firstName, lastName)) {
			$.ajax({
				type: 'GET',
				url: '/rest/V1/Patient?LastName=' + lastName + '&FirstName='+ firstName + '&ClinicBranchKeyList=' + clinicBranchKeyList,
				dataType: 'json'
			}).success(function( response ) {
				if (response.length>0) {
					
					divDialog.dialog({
						autoOpen: true,
						resizable: false,
						modal: true,
						width: 920,
						position: ['center', 45],
						title: 'Possible Matches',
						create: function() {
					        $(this).css("maxHeight", 500);        
					    },
						buttons: [ 
						{ 
							text:'Cancel',
							class: 'btn', 
							id:"OverlappingVisitsCancelButton", 
							click: function() { 
								$(this).dialog('close'); 
							} 
						} 
					]});
					var patientsFound = formatSearchResultMessage(response);
					divDialog.html(patientsFound);
				}
				
			}).error(function(response) {
				console.log(response);
			});
		}
	};
	
	// Validate first and last name are present
	var validateNameForSearch = function(lastname, firstname){
		return (lastname != "" && firstname != "");
	};
	
	var generateJQId = function(id) {
		return "#"+id;
	}
	//Public
	return {
		init: function(firstName, lastName, clinicBranchKeyList) {
			$(document.body).append('<div id="PatientSearch" style="display:none;">&nbsp;</div>');
			$(generateJQId(firstName.prop('id')) + ", " + generateJQId(lastName.prop('id'))).blur(function(event) {
				searchPatients(firstName.val(), lastName.val(), clinicBranchKeyList.val(), $("#PatientSearch"));
			});
		}
	};
	
	
})();

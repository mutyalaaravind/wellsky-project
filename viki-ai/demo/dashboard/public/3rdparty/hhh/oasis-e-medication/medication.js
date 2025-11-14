function loadMeds(){

	loadFutureMeds();
	loadCurrentMeds();
	loadDiscontinuedMeds();

}

function createMedHeader(title){
	var html = '<div class="moduleRow">'+
				'<strong>' + title + '</strong>'+
				'</div>'+
				'<div class="moduleRow medLabelRow">'+
					'<div class="moduleCol lsCol"></div>'+
					'<div class="moduleCol startCol">Start Date</div>'+
					'<div class="moduleCol dcCol">Discontinue Date</div>'+
					'<div class="moduleCol medCol">Medication</div>'+
				'</div>';
	return html;
}

function addMedicationRow(rowIndex, medication, divId, requiresOrderCheckbox){
	var theClass = '';
	var rowId = divId + "_" + rowIndex;

	/*  Building theClass variable correctly is important for being able to click on the
		medication description in the grid and opening the correct modal. */
	switch(medication.MEDICATIONTYPE)
	{
		case 'FreeForm':
			theClass = 'freeform';
		break;
		case 'MultiDose':
			theClass = 'multidose';
		break;
		case 'Medispan':
			theClass = 'medication';
		break;
		default:
			alert('An unknown MedicationType exists.');
	}

	if(divId == 'discontinuedMeds') {
		theClass = 'medicationDiscontinued';
	}

	if (medication.DISCONTINUEDATE.length <= 0)
		medication.DISCONTINUEDATE = '<input type="button" value="D/C" />';

    var orderCheckbox = '';

    if(requiresOrderCheckbox){
		var medHeading = '';
		if(divId == 'discontinuedMeds')
			medHeading = 'Discontinued Medication:';
		else if(divId == 'currentMeds')
			medHeading = 'Current Medication:';
		else if(divId == 'futureMeds')
			medHeading = 'Future Medication:';

        orderCheckbox =  '<input class="order-checkbox-node" type="checkbox" name="medOrderCheckbox" id="orderCheckbox' + medication.PATIENTMEDISPANKEY + '" />';
    }

	var html =  '<div class="moduleRow medRow" id="' + medication.PATIENTMEDISPANREGISTRYKEY + '" ><div class="moduleCol lsCol">' +
				medication.LS + '</div><div class="moduleCol startCol" id="' + rowId + '_startDate" >' +
				medication.STARTDATE + '</div><div class="moduleCol dcCol discontinue" id="' + rowId + '_discontinuedDate" >' +
				'<span class="dcText">' + medication.DISCONTINUEDATE + '</span>' + '</div><div class="moduleCol medCol ' + theClass + '" style="width: 30%;" id="' + rowId + '_medicationTitle" ><span class="medTitle">' +
				'<span class="medication-title-node"></span> ' +
				'<span class="medication-new-node"></span> ' +
				'<span class="medication-change-node"></span>';
				if (medication.MEDICATIONDOSE.length > 0) {
					for(var i=0; i<medication.MEDICATIONDOSE.length; i++) {
						html += '<br />' + medication.MEDICATIONDOSE[i];
					}
				}
				html += '<br /><span class="medClass">' + medication.CLASS + '</span>' +
				'</div><div class="moduleCol deleteCol" id="' + rowId + '_deleteButton" style="width: 30%;"><input type="button" value="Delete" class="delete" style="width: 20%; margin-left: 2%;" /></div><div class="moduleCol" id="' + rowId + '_checkBox" >' + orderCheckbox + '</div></div>';

	var htmlElement = $(html);

	$('#' + divId).append(htmlElement);

	if (orderCheckbox) {
		$('.order-checkbox-node', htmlElement).attr('value', medHeading + '\n' + medication.MEDICATIONORDERSTRING);
	}

	var replaceMap = {
		'medication-title-node': medication.TITLE,
		'medication-new-node': medication.NEW,
		'medication-change-node': medication.CHANGE
	};

	$.each(replaceMap, function(key, value) {
		$('.' + key, htmlElement).text(value);
	});
}

function loadModals()
{
	openMed();
	openFreeForm();
	openMultiDose();
	openDelete();
	openDiscontinue();
}

function openMed(){
	$('.moduleCol.medication').each(function(){
		$(this).click(function(){
			var pmKey = $(this).parent().attr("id");
			$('#updateMedicationModal').load('/AM/Medication/MedicationProfile/saveMedispan.cfm?PatientMedispanRegistryKey='+pmKey);
			$('#updateMedicationModal').dialog('open');
		});
	});
}

function openFreeForm(){
	$('.moduleCol.freeform').each(function(){
		$(this).click(function(){
			var pmKey = $(this).parent().attr("id");
			$('#updateFreeFormModal').load('/AM/Medication/MedicationProfile/saveFreeForm.cfm?PatientMedispanRegistryKey='+pmKey);
			$('#updateFreeFormModal').dialog('open');
			});
		});
}

function openMultiDose(){
	$('.moduleCol.multidose').each(function(){
		$(this).click(function(){
			var pmKey = $(this).parent().attr("id");
			$('#updateMultiDoseModal').load('/AM/Medication/MedicationProfile/saveMultiDose.cfm?PatientMedispanRegistryKey='+pmKey);
			$('#updateMultiDoseModal').dialog('open');
		});
	});
}

function openDelete(){
	$('.delete').each(function(){
		$(this).click(function(){
			var pmKey = $(this).parent().parent().attr("id");
			$('#deleteMedicationModal').load('/AM/Medication/MedicationProfile/deleteMedication.cfm?PatientMedispanRegistryKey='+pmKey);
			$('#deleteMedicationModal').dialog('open');
			});
		});
}

function openDeleteRefillConfirm(formStruct){
	$('#refillDeleteConfirmModal').load('/AM/Medication/MedicationProfile/refillDeleteConfirmation.cfm?PatientMedispanRefillKey='+formStruct.PatientMedispanRefillKey+ '&PatientMedispanRegistryKey='+formStruct.fPatientMedispanRegistryKey+'&Units='+formStruct.OldUnits+'&RefillDate='+formStruct.OldRefillDate+'&LastRefillDate='+formStruct.LastRefillDate+'&SecondToLastRefillDate='+formStruct.SecondToLastRefillDate+'&Charge='+formStruct.OldRefillCharge+'&inMedispan='+formStruct.oldInMedispan);
	$('#refillDeleteConfirmModal').dialog('open');
}

function openDiscontinue(){
	$('.moduleCol.discontinue').each(function(){
		$(this).click(function(){
			var pmKey = $(this).parent().attr("id");
			$('#discontinueMedicationModal').load('/AM/Medication/MedicationProfile/discontinueMedication.cfm?PatientMedispanRegistryKey='+pmKey);
			$('#discontinueMedicationModal').dialog('open');
			});
		});
}

// ************* save/update/delete/discontinue validate ********************

function validateForm(formStruct, id){
	$.ajax({
		type: "GET",
		dataType: "json",
		url: '/AM/Medication/MedicationProfile/MedicationProfileManager.cfc?method=validateForm',
		data: formStruct,
		success: function(result){
				if (!result.ISVALID)
				{
					var errorLen = result.errors.length;
					var theHtml = '';
					for( var i = 0; i<errorLen; i++){
						theHtml = theHtml + '<p>' + result.errors[i] + '</p>';
						}
					$('#errorModal').html(theHtml);
					$('#errorModal').dialog('open');
					$('#addMedispanButton,#saveMultiDoseButton, #addAdditionalButton').removeAttr('disabled');
				}
				if(result.ISVALID){
					if(id == 'addAdditionalButton') {
                        resetAddMedForm();
						saveAndAddMedication(formStruct);
					} else {
						saveMedication(formStruct);
					}
				}
			},
		error: function(data){
			}
		});
}


function resetAddMedForm(){
    $('#HCPCS').empty();
    $('#NDC').empty();
    $('#coveredRadioYes').attr('checked',false);
    $('#coveredRadioNo').attr('checked',false);
    $('#infusionPumpYes').attr('checked',false);
    $('#infusionPumpNo').attr('checked',true);
    $('#injectableYes').attr('checked',false);
    $('#injectableNo').attr('checked',false);
    $('#PTCG').val('YES');
    $('#HCPCS').show();
    $('#HCPCSAlt').hide();
    $('#NDC').show();
    $('#NDCAlt').hide();
}

function resetAddMedFreeForm(){
    $('#HCPCS').val('');
    $('#NDC').val('');
    $('#coveredRadioYes').attr('checked',false);
    $('#coveredRadioNo').attr('checked',false);
    $('#infusionPumpYes').attr('checked',false);
    $('#infusionPumpNo').attr('checked',true);
    $('#injectableYes').attr('checked',false);
    $('#injectableNo').attr('checked',false);
    $('#PTCG').val('YES');
    $('#HCPCS').attr('disabled',true);
    $('#NDC').attr('disabled',true);
}

function validateFreeForm(formStruct, id){
	$.ajax({
		type: "GET",
		dataType: "json",
		url: '/AM/Medication/MedicationProfile/MedicationProfileManager.cfc?method=validateFreeForm',
		data: formStruct,
		success: function(result){
				if (!result.ISVALID)
				{
					var errorLen = result.errors.length;
					var theHtml = '';
					for( var i = 0; i<errorLen; i++){
						theHtml = theHtml + '<p>' + result.errors[i] + '</p>';
						}
					$('#errorModal').html(theHtml);
					$('#errorModal').dialog('open');

				}
				if(result.ISVALID){
					if(id == 'addAdditionalButton') {
                        resetAddMedFreeForm();
						saveAndAddMedication(formStruct);
					} else {
						saveMedication(formStruct);
					}
				}
			},
		error: function(data){
			}
		});
}

function validateDiscontinue(formStruct){
	$.ajax({
		type: "GET",
		dataType: "json",
		url: '/AM/Medication/MedicationProfile/MedicationProfileManager.cfc?method=validateDiscontinue',
		data: formStruct,
		success: function(result){
				if (!result.ISVALID)
				{
					var errorLen = result.errors.length;
					var theHtml = '';
					for( var i = 0; i<errorLen; i++){
						theHtml = theHtml + '<p>' + result.errors[i] + '</p>';
						}
					$('#errorModal').html(theHtml);
					$('#errorModal').dialog('open');

				}
				if(result.ISVALID){
					discontinueMedication(formStruct);
				}
			},
		error: function(data){
			}
		});
}

function saveMedication(formStruct){
	$.ajax({
		type: "GET",
		dataType: "json",
		url: '/AM/Medication/MedicationProfile/MedicationProfileManager.cfc?method=saveMedication',
		data: formStruct,
		success: function(result){
			$('#Medispan').empty();
			$('#FreeForm').empty();
			$('#MultiDose').empty();
			$('#updateMedicationModal').dialog('close');
			$('#updateFreeFormModal').dialog('close');
			$('#updateMultiDoseModal').dialog('close');
			var field = $('#medicationType');
			field.val($('option:first', field).val());
			loadMeds();
			},
		error: function(data){
		}
	});
}

function saveAndAddMedication(formStruct){
	$.ajax({
		type: "GET",
		dataType: "json",
		url: '/AM/Medication/MedicationProfile/MedicationProfileManager.cfc?method=saveMedication',
		data: formStruct,
		success: function(){
			resetFields();
			$('#medAdded').show();
			var field = $('#medicationType');
			field.val($('option:first', field).val());
			field = $('#classificationId');
			field.val($('option:first', field).val());
			$('#updateMedicationModal').dialog('close');
			$('#updateFreeFormModal').dialog('close');
			$('#updateMultiDoseModal').dialog('close');
			loadMeds();
			},
		error: function(data){
			}
		});
}

function resetFields () {

	$('#LSFlag').attr('checked', false);
	$('#ChangeFlag').attr('checked', false);
	$('#NewFlag').attr('checked', false);
	$('#StartDate').val('');
	$('#Medication').val('');
	$('#MedicationInstructions').val('');
	$('#Dose').val('');
	$('#Dose1').val('');
	$('#DiscontinueDate').val('');
	$('#multiDoseChild').empty();
	$('#multiDoseParent').find('input[type=text]').val('');
	$('#addMedispanButton,#saveMultiDoseButton,#addFreeFormButton, #addAdditionalButton').removeAttr('disabled');
}

function resetRefillsFields () {
	$('#PatientMedispanRefillKey').val(-1);
	$('#units').val('');
	$('#refillDate').val('');
}

function deleteMedication(formStruct){
	$.ajax({
		type: "GET",
		dataType: "json",
		url: '/AM/Medication/MedicationProfile/MedicationProfileManager.cfc?method=deleteMedication',
		data: formStruct,
		success: function(result){
			loadMeds();
			$('#deleteMedicationModal').dialog('close');
			},
		error: function(data){
			}
		});
}

function discontinueMedication(formStruct){
	$.ajax({
		type: "GET",
		dataType: "json",
		url: '/AM/Medication/MedicationProfile/MedicationProfileManager.cfc?method=discontinueMedication',
		data: formStruct,
		success: function(result){
			loadMeds();
			$('#discontinueMedicationModal').dialog('close');
			},
		error: function(data){
			}
		});
}

function updatePharmacy(formStruct){
	$.ajax({
		type: "GET",
		dataType: "json",
		url: '/AM/Medication/MedicationProfile/MedicationProfileManager.cfc?method=updatePharmacy',
		data: formStruct,
		success: function(result){
			loadPatientInformation();
			$('#updatePharmacy').dialog('close');
			},
		error: function(data){
			}
		});
}

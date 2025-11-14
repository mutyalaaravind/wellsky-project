// JavaScript Document

$(document).ready(function(){
	$("#saveWindow").dialog({
		bgiframe: true,
		height: 140,
		width: 350,
		modal: true,
		autoOpen:false
	});

	$("#errorWindow").dialog({
		bgiframe: true,
		height: 200,
		width: 350,
		modal: true,
		autoOpen:false,
		buttons: {
			Ok: function() {
				$(this).dialog('close');
				toggleButtons('enable');
			}
		}
	
	});
	
	$('#overlappingVisitsModal').dialog({
		width: 425,
		modal: true,
		autoOpen: false,
		buttons: [ { text:"Save", id:"OverlappingVisitsSaveButton", click: function(){ 
					$(this).dialog('close');
				}}, { text:"Cancel", id:"OverlappingVisitsCancelButton", click: function(){ 
					$(this).dialog('close'); 
					toggleButtons('enable'); 
				}}]
	});

	$('#btnContainer').find(':button').click(function(){
		toggleButtons('disable');
	})
});

function toggleButtons(type)
{
	if (type == 'disable')
		$('#btnContainer').find(':button').attr('disabled','true');
	else {
		$('#btnContainer').find(':button').removeAttr('disabled');
		// Disable buttons when task is not clocked out yet. Check function defined for DD.
		if (typeof disableClockOutButtons === "function") {
			disableClockOutButtons();	
    	}
	}
}

function pageSaving()
{
	$("#saveWindowText").text('Page is saving...');
	$("#saveWindow").dialog('open');
}

function pageSaved()
{
	$("#saveWindowText").text('Page has been saved!');
	setTimeout("$('#saveWindow').dialog('close')",850);
	toggleButtons('enable');
}

function pageError(message,fieldIDObj)
{

	$('#saveWindow').dialog('close');
	/*for(var obj in fieldIDObj)
	{
		$('#'+obj).css('background-color','red');
	}*/

	var subText = message.split(';');
	var htmlMessage = '<table>';

	$.each(subText, function(i,e) {
		htmlMessage += '<tr><td style="padding: 4px 5px;">'+ e + '</td></tr>';
	});

	htmlMessage += "</table>";

	$("#errorWindowText").html(htmlMessage);
	$("#errorWindow").dialog('open');
	toggleButtons('enable');
}

function clearICD(id)
{
    $('#'+id).val('');
    $('#'+id+'_display').val('');
    $('#'+id+'_id').val('');
    $('#'+id+'_icdId').val('');
    $('#'+id+'_icdDesc').val('');
}

/** Retrieve Medicare start of the week in order to validate the current visit date is
happening within that week, if so show the modal if not proceed with regular Overlapping 
visits validation **/
function checkOutsideMedicareWeek(clinicKey, targetDate, visitDate, action, denyOverlap, userKey, gotoPage, afterSaveCallback){
	$.ajax({
		type: "GET",
		dataType: "json",
		url: ux.config.getAppBaseUrl() + "Forms/FormsProxy.cfc",
		data: {
			method: 'checkDateInsideMedicareWeek',
			ClinicKey: clinicKey,
			targetDate: targetDate,
			visitDate: visitDate
		},
		success: function(resultStruct){
			if (!resultStruct.isInsideMedicareWeek) {
				$('#visitOutsideMedicareWorkWeekModal').dialog({
					width: 425,
					modal: true,
					autoOpen: false,
					buttons: [ { text:"Yes", id:"outsideMedicareWorkWeekSaveButton", click: function(){ 
						$(this).dialog('close');
						if (FormUtil.getTimeIn() != undefined || FormUtil.getTimeOut() != undefined ){
							getOverlappingVisits(
								action, 
								gotoPage, 
								FormUtil.getEpisodeKey(), 
								FormUtil.getPatientTaskKey(), 
								visitDate, 
								FormUtil.getTimeIn(), 
								FormUtil.getTimeOut(), 							
								userKey,
								afterSaveCallback);
						} else {
							modifyFormHelper(action,gotoPage, afterSaveCallback);
						}
					}}, { text:"No", id:"outsideMedicareWorkWeekCancelButton", click: function(){ 
						$(this).dialog('close'); 
					}}]
				});
				$('#visitOutsideMedicareWorkWeekModal').html("WARNING:  The visit date you entered is outside of the Medicare work week.  Are you sure you want to continue? ");
				$('#visitOutsideMedicareWorkWeekModal').dialog('open');
			} else if (FormUtil.getTimeIn() != undefined || FormUtil.getTimeOut() != undefined ){
				getOverlappingVisits(
					action,
					gotoPage,
					FormUtil.getEpisodeKey(),
					FormUtil.getPatientTaskKey(),
					visitDate,
					FormUtil.getTimeIn(),
					FormUtil.getTimeOut(),
					userKey,
					afterSaveCallback);
			} else {
				modifyFormHelper(action,gotoPage, afterSaveCallback);
			}
		},
		error: function(){}
	});
}
/**
 * Check for any overlapping visits for the given task in the given episode.
 *
 * @param action			The action to be taken. (Save, Submit, etc.)
 * @param gotoPage			The page to redirect to once the action is completed.
 * @param episodeKey		Episode key.
 * @param patientTaskKey	Patient task key for the visit to be checked.
 * @param visitDate			Visit date. (Expecting a string, not a date object.)
 * @param timeIn			Time in. (Expecting a string.)
 * @param timeOut			Time out. (Expecting a string.)
 */
function getOverlappingVisits( action, gotoPage, episodeKey, patientTaskKey, visitDate, timeIn, timeOut, userKey, afterSaveCallback ) {
    OverlappingVisits.checkOverlappings( 
		episodeKey, 
		patientTaskKey, 
		visitDate, 
		timeIn, 
		timeOut,	
		userKey,			
		function onContinueCallback() { modifyFormHelper(action, gotoPage, afterSaveCallback); },
		function onErrorCallback(errorStruct){ pageError(errorStruct) }
	);
}

/**
 * Modifies a form.
 *
 * @param action	    	The action to be taken. (Save, Submit, etc.)
 * @param gotoPage	    	The page to redirect to once the action is completed.
 * @param denyOverlap   	(optional) Used to determine if overlapping visits are allowed or not
 * @param afterSaveCallback	(optional) Callback to invoke after AJAX call is completed 
 */
function modifyForm(action, gotoPage, denyOverlap, userKey, afterSaveCallback)
{
	if (action=='nothing'){
		window.location = ux.statePersistance.addSessionCacheKeyToURL(gotoPage);
		return;
	};

	if (action == 'saveQuiet')//reset the saveQuiet to 'save' so that they will work similarly through the app
		action = 'save';
		
	$('#whattodo').val(action);

	var episodeKey = FormUtil.getEpisodeKey();
    var clinicKey = FormUtil.getClinicKey();
	var patientTaskKey = FormUtil.getPatientTaskKey();
	var targetDate = FormUtil.getTargetDate();
	var visitDate = FormUtil.getVisitDate();
	var timeIn = FormUtil.getTimeIn();
	var timeOut = FormUtil.getTimeOut();
	var categoryShortName = FormUtil.getCategoryShortName();
	var clinicBranchKey = FormUtil.getClinicBranchKey();
	var PTGVersion = FormUtil.getPTGVersion();
	var listClinicTypeKey = FormUtil.getListClinicTypeKey();

	// check for overlapping visits if the following is available
	if(visitDate != undefined && timeIn != undefined && timeOut != undefined)
	{
		if(visitDate.length != 0 && timeIn.length != 0 && timeOut.length != 0)
		{
			if(isDate(visitDate) && isTime(timeIn) && isTime(timeOut)){
			    if (action == 'submit' && categoryShortName=="RV" && PTGVersion=="1" && listClinicTypeKey=="12") {
					validateAddressedPatientGoals(clinicKey, clinicBranchKey, patientTaskKey, targetDate, visitDate, action, denyOverlap, userKey, gotoPage, afterSaveCallback);
				}
				else {
					checkOutsideMedicareWeek(clinicKey, targetDate, visitDate, action, denyOverlap, userKey, gotoPage, afterSaveCallback);
					setTimeout("toggleButtons('enabled')",250);
				}
			} else {
				// re-enable buttons after their click listener is triggered
				setTimeout("toggleButtons('enabled')",250);
			}
		} else {
			// proceed with normal behavior
			modifyFormHelper(action,gotoPage, afterSaveCallback);
		}
	} else {
	    if (action == 'submit' && categoryShortName=="RV" && PTGVersion=="1" && listClinicTypeKey=="12") {
			validateAddressedPatientGoals(clinicKey, clinicBranchKey, patientTaskKey, targetDate, visitDate, action, denyOverlap, userKey, gotoPage);
		} else {
			// proceed with normal behavior
			modifyFormHelper(action,gotoPage, afterSaveCallback);
		}
	}
}

function validateAddressedPatientGoals(clinicKey, clinicBranchKey, patientTaskKey, targetDate, visitDate, action, denyOverlap, userKey, gotoPage, afterSaveCallback) {
	$.ajax({
		type: "GET",
		url: "/KSI/PTGService/Clinic/"+clinicKey+"/ClinicBranch/"+clinicBranchKey+"/v1/PatientTask/"+patientTaskKey+"/CheckAtLeasOneGoalAddressed",
		success: function(result){
			if (result.showWarning) {
				// modal to display the error msg...
				$('#validationAddressGoalsModal').dialog({
					width: 425,
					modal: true,
					autoOpen: false,
					buttons: [
								{ text:"Submit", id:"_SubmitButton", click: function(){
									checkOutsideMedicareWeek(clinicKey, targetDate, visitDate, action, denyOverlap, userKey, gotoPage, afterSaveCallback);
									setTimeout("toggleButtons('enabled')",250);
									$(this).dialog('close');
								}},
								{ text:"No", id:"_CancelButton", click: function(){ 
									$(this).dialog('close'); 
									toggleButtons('enable'); 
								}}
							]
				});
				$('#validationAddressGoalsModal').html(result.message);
				$('#validationAddressGoalsModal').dialog('open');
			} else {
				checkOutsideMedicareWeek(clinicKey, targetDate, visitDate, action, denyOverlap, userKey, gotoPage);
				setTimeout("toggleButtons('enabled')",250);
			}
		},
		error: function(){}
	});
	
}

/**
 * Continuation of the logic for modifyForm, after overlapping visits
 * have been checked for.
 *
 * @param action	The action to be taken. (Save, Submit, etc.)
 * @param gotoPage	The page to redirect to once the action is completed.
 * @param afterSaveCallback	(optional) Callback to invoke after AJAX call is completed 
 */
function modifyFormHelper(action,gotoPage, afterSaveCallback)
{
	//Check for ESAS validation
	if (typeof validateESAS === "function")
	{
		if(validateESAS(action,gotoPage, afterSaveCallback))
			return;
	}

	if (action == 'save')
		pageSaving();

	$.ajax({
		type: "POST",
		url: "/AM/Forms/processForm.cfc?method=modifyForm",
		data: FormUtil.getFormStruct(),
		dataType : 'json',
		success: function(jsonData){
			postLoad(jsonData,action,gotoPage, afterSaveCallback);
		}
	})

	
	function postLoad(jsonData,action,gotoPage, afterSaveCallback)
	{
		if (jsonData.resultType=='pass')
		{
			pageSaved();
			if (jsonData.pageInstruction == 'reload' || (action != 'save'))
			{
				document.getElementById('frmForm').submit();
			}
			if (gotoPage != undefined)
			{
				window.location = ux.statePersistance.addSessionCacheKeyToURL(gotoPage);
			}
		}
		else if (jsonData.resultType=='timeout')
		{
			window.location = '/AM/login.cfm?logout=1';
		}
		else
		{
			toggleButtons('enable');
			pageError(jsonData.errorMessage,jsonData.fieldID);
		}
		
		if (afterSaveCallback){
			afterSaveCallback(jsonData.resultType);
		}
	}
}

function clearRadio(section){
	$('input[name*='+section+']' ).each(function(){
                 $(this).removeAttr('checked');
           })    
}


//*** Skip Pattern Code		
function toggleChecked()
{
	if ( $('#' + arguments[0] + ':checked').val() == 1)
	{
		for (var i=1;i<arguments.length;i++)
		{				
			DeActivateMCodeC(arguments[i])
		}
	}	
	else
	{
		for (var i=0;i<arguments.length;i++)
		{				
			ActivateMCodeC(arguments[i])
		}
	}	
}

function clearSection(section,disableField, doFocus)
{
	if (typeof doFocus === 'undefined') {
		doFocus = true;
	}
	
	var currName = '';
	var grpNameArray = new Array(5); //initialize input name array
    var arrayIndex = 0;
        	
	$('#'+ section).find('input:radio').each(function(){ //move through the radio buttons in the section/container to get distinct input names
		if(currName == '' || currName != $(this).attr('name')){ //initial case
			$(this).trigger('change');
			grpNameArray[arrayIndex] = $(this).attr('name');
			arrayIndex++;
		}
		currName = $(this).attr('name'); //set the current input name
		$(this).attr('checked',false);
	});
	
	//Add a hidden radio id so that clear functionality will be respected
	for (var i = 0; i < arrayIndex; i++) {
		var elemSelector = '#' + grpNameArray[i].replace(/\|/g, "\\|") + '_hidden'; //we need to escape | pipes for selector to work
		if ($(elemSelector).length < 1) {
			$('#' + section).append('<input type="radio" id="' + grpNameArray[i] + '_hidden" name="' + grpNameArray[i] + '" value="" checked="true" style="display: none;">');
		}
		else {
			$('#' + grpNameArray[i] + '_hidden').attr('checked', true);
		}
	}
	
	$('#' + section + ' :input').each(function(){
		//reset the checkboxes
		if ($(this).prop('type') == 'checkbox')
		{
			$(this).attr('checked',false);
			$(this).trigger('change');
		}
		
		//-----TEXTBOXES and TEXTAREAS-----
		if ($(this).prop('type') == 'text'){
			$(this).val('');
			$(this).filter(':visible').filter(':enabled').trigger('change');
			
		}
		else if ($(this).prop('type') == 'textarea'  || $(this).attr('tagName') == 'TEXTAREA'){
			$(this).val('');
			if (doFocus) {
				$(this).filter(':visible').filter(':enabled').trigger('focus');
			}
		}
		
		//reset the select boxes	
        if ($(this).prop('type') == 'select-one' ){
            this.selectedIndex = 0;
            $(this).trigger('change');
        }

        //-----HIDDEN---
        //for clearing ICD values on OASIS that are added via the icd-lookup.js directive
        if ($(this).prop('type') == 'hidden'&& ($(this).parent().is('k-icd-lookup'))){
            $(this).val('');
            $(this).filter(':visible').filter(':enabled').trigger('change');

        }
        
		//disable the fields last because some inputs check to see if the field is enabled
      	if (disableField)
			$(this).attr('disabled','disabled');        
   });
}

function DeActivateMCodeC(MCode, doFocus)
{
	clearSection(MCode,true, doFocus);
	$('#' + MCode ).fadeTo('slow','0.33');
	
	
}
function ActivateMCodeC(MCode)
{
    var enable = false;
    if($('#' + MCode).css('opacity') < 0.5 && MCode == 'M1011'){
        enable = true;
    }
	if ($('#' + MCode + ' :input').attr('disabled') || enable)//only reactivate if it is disabled, otherwise a 'flash' will occur
	{
		$('#' + MCode ).fadeTo('slow','1');
		$('#' + MCode + ' :input').removeAttr('disabled');
	}

    //For dealing with the ICD-10 lookup tool field which needs to be permanently disabled
    $('.keep-disabled').each(function(i, obj) {
        $(obj).attr('disabled', true);
    });


}
//*** End Skip Pattern Code

function displayRemainingCharacters(targetName, counterName) { 
	$('#' + counterName).text("Remaining characters: " + (500 - $('#' + targetName).val().length));
}

function limitText(targetName, limitNum) {
	var limitField = $('#' + targetName);
	
	if(limitField.val().length >= limitNum)
	{
		limitField.val(limitField.val().substring(0, limitNum));
	}
}


FormUtil = (function(){

	function getTimeField(frm, fieldName, formId) {
		var result = frm[fieldName.replace('#','') + "|spWritefrmDate|1"];
		var $time = $( fieldName, $( formId) );
		if( result == undefined && $time.length > 0 ) 
			result = $time.val();

		return result;
	}

	function getFormStruct(){		
		return getFormAsStruct(document.getElementById('frmForm'));
	}

	return {
		'getFormStruct': getFormStruct,

		'getEpisodeKey': function getEpisodeKey(){
			return getFormStruct()["fEpisodeKey"];
		},
		'getClinicKey': function getClinicKey(){
			return getFormStruct()["fClinicKey"];
		},
		'getPatientTaskKey': function getPatientTaskKey(){
			return getFormStruct()["fPatientTaskKey"];
		},
		'getTargetDate': function getTargetDate(){
			return $("input[name='taskTargetDate']").val();
		},

		'getTimeIn': function getTimeIn() {
			return getTimeField( getFormStruct(), '#frm_timein', '#frmForm' )
		},

		'getTimeOut': function getTimeOut() {
			return getTimeField( getFormStruct(), '#frm_timeout', '#frmForm' )
		},

		'getVisitDate' : function getVisitDate() {
			var visitDate, frm = getFormStruct();
			switch(parseInt(frm["formKey"])) {
				case 194:
					visitDate = frm["frm_DateCompleted|spWritefrmDate|1"];
				case 191:
					visitDate = frm["frm_sDate|spWritefrmDate|1"];
				default:
					visitDate = frm["frm_visitdate|spWritefrmDate|1"];
			}

			if( visitDate == undefined && $( '#frm_visitdate, #frm_sDate, #frm_DateCompleted', $( '#frmForm' ) ).length > 0 ) 
				visitDate = $( '#frm_visitdate, #frm_sDate, #frm_DateCompleted', $( '#frmForm' ) ).val();

			return visitDate;
		},
		'getCategoryShortName': function getCategoryShortName(){
			return getFormStruct()["categoryShortName"];
		},
		'getClinicBranchKey': function getClinicBranchKey(){
			return getFormStruct()["fClinicBranchKey"];
		},
		'getPTGVersion': function getPTGVersion(){
            return getFormStruct()["PTGVersion"];
        },
        'getListClinicTypeKey': function getListClinicTypeKey(){
            return getFormStruct()["listClinicTypeKey"];
        },
        
	}

})();

// html string escape key-value pairs
var escapeCharacters = {
	'&': '&amp;',
	'<': '&lt;',
	'>': '&gt;',
	'"': '&quot;',
	"'": '&#39;',
	'/': '&#x2F;',
	'`': '&#x60;',
	'=': '&#x3D;'
	};

// escape a string to be html-safe
function escapeForHtml(string) {
	return String(string).replace(/[&<>"'`=\/]/g, function (s) {
		return escapeCharacters[s];
	});
};

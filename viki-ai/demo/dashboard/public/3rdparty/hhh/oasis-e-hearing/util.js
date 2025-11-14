// JavaScript Util Functions

//override default radio button behavior to allow user to uncheck
function setRadiosUncheckable() {
	 $("input:radio").mousedown(function(e) {
		if ($(this).attr("checked") == 'checked') {
            setTimeout("$('input[id=" + $(this).attr('id') + "]').removeAttr('checked').trigger('change');", 200);
            // Add a hidden field for OASIS radios
            if ($('[name="OasisForm"]').length && ($('#' + name + '_hidden').length < 1)) {
                    $('#' + $(this).attr('id')).before('<input type="hidden" id="' + $(this).attr('id') + '_hidden" name="' + $(this).attr('name') + '" value="" ">');
                }
        else {
              return true
             }
        }
	});
}
/*searches string for illegal characters (for Windows file name) */
function validateFileName(filePathStr){
	var isValid = true;
	var splitStr = filePathStr.split('\\');
	var fileName = splitStr[splitStr.length-1];	
	var regExp = /^[a-z0-9 ()_.-]+$/i
	if(fileName.search(regExp) == -1) { isValid = false };
	
	return isValid;	
}

// Read a page's GET URL variables and return them as an associative array.
function getUrlVars()
{
	var vars = [], hash;
	var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
	for(var i = 0; i < hashes.length; i++)
	{
		hash = hashes[i].split('=');
		vars.push(hash[0]);
		vars[hash[0]] = hash[1];
	}
	return vars;
}

// Convert meters to feet with the given significant digits (0 = all available digits) 
//  & round to the nearest integer, if desired
function convertMetersToFeet(value, significantDigits, roundToInteger) {
	var valueInFeet = value * 3.28084;  							// convert to feet
	if (significantDigits) {
		valueInFeet = valueInFeet.toPrecision(significantDigits);	// round to significant digits
	}
	if (roundToInteger) {
		valueInFeet = Math.round(valueInFeet); 						// round to nearest integer
	}
	return Number(valueInFeet);  									// remove any scientific notation
}

// Convert numeric degrees to radians
function convertDegreesToRadians(value) {
    return value * Math.PI / 180;
}

// Calculate the distance in meters between two map coordinate points
function getDistanceBetweenMapPoints(lat1, lng1, lat2, lng2) {
	// Uses the "haversine" formula for distance between points on the globe
	var R = 6378100; // radius of Earth in meters
	var diffLat = convertDegreesToRadians(lat2-lat1);
	var diffLng = convertDegreesToRadians(lng2-lng1);
	var lat1 = convertDegreesToRadians(lat1);
	var lat2 = convertDegreesToRadians(lat2);
	
	var a = Math.sin(diffLat/2) * Math.sin(diffLat/2) +
	        Math.sin(diffLng/2) * Math.sin(diffLng/2) * Math.cos(lat1) * Math.cos(lat2); 
	var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a)); 
	var d = R * c;
	return d;
}

// No-op function for callbacks
function nullFunction() {}

/***
 *	Returns string without a JSON packaging character ("<*>")
 *
 *	@param inputString	Trim the special character from this string
 */
var stripJSONFormatting = function(inputString)
{
	if (inputString) {
		var specialCharacter = '<*>'; //character we want to strip
		if (inputString.length > 0 && inputString.slice(0, specialCharacter.length) === specialCharacter) { //test for special "formatting" character
			inputString = inputString.slice(specialCharacter.length, inputString.length); //strip character
		}
		return inputString;
	};
	
	return '';
}
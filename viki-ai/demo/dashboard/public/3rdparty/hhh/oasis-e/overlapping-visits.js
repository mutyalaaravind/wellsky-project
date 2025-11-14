/**
 * Overlapping Visits
 */
OverlappingVisits = (function(  ){
    /* Private Variables and Methods */
    var getMessage = function getMessage (overlappings, date) {
        var overlappingsDesc = []

        overlappings.forEach(function (overlapping) {
            var desc = [];
            ["LASTNAME", "FIRSTNAME", "TASKNAME", "TIMEIN", "TIMEOUT"].forEach( function (key) {
            if( ! overlapping[key] ) return;
                desc.push( overlapping[key] );
            });
            
            desc.push( date );
            overlappingsDesc.push( "<li>" + desc.join(', ') + "</li>" );
        });
        
        return "Visits or tasks that overlaps: <br/> <ul class='errorMessage'>" +  overlappingsDesc.join('') + "</ul>";    
        
    },

    showOverlappingMessagePopUp = function showOverlappingMessagePopUp ( title, message, buttons ) {
        if ( $('#overlappingVisitsModal').length == 0 ){
            $(document.body).append( '<div id="overlappingVisitsModal" style="display:none"></div>' );
        }

        $('#overlappingVisitsModal').html( message );
        $('#overlappingVisitsModal').dialog( 'option', 'title', title );
        $('#overlappingVisitsModal').dialog( 'option', 'buttons', buttons );
        $('#overlappingVisitsModal').dialog( 'open' );
    },

    showClinicianOverlappingMessagePopUp = function showClinicianOverlappingMessagePopUp (overlappings, visitDate) {
        var overlappingVisits = getMessage(overlappings, visitDate);
        
        showOverlappingMessagePopUp(
            'Overlapping Visit',
            "You are not allowed to save or submit a visit note that has a visit date and time that overlaps another visit note. <br><br>" + overlappingVisits,
            [{ 
                text : 'OK', 
                id   : "OverlappingVisitsCancelButton",
                click: function() { $('#overlappingVisitsModal').dialog( 'close' ); }
            }]
        );
    },

    showPatientOverlappingMessagePopUp = function showPatientOverlappingMessagePopUp (overlappings, visitDate, onContinueCallback) {
        var overlappingVisits = getMessage(overlappings, visitDate);
        
        if(overlappingVisits != null){
            showOverlappingMessagePopUp(
                'Patient - Overlapping Visit',
                "WARNING:  You are saving or submitting a visit note for a patient that has occurred at the same time as another user. <br><br> " + overlappingVisits,
                [{ 
                    text : 'Continue', 
                    id   : "OverlappingVisitsSaveButton", 
                    click: function() {
                        $('#overlappingVisitsModal').dialog( 'close' );
                        onContinueCallback();
                    }
                },
                { 
                    text : 'Cancel', 
                    id   : "OverlappingVisitsCancelButton", 
                    click: function() { $('#overlappingVisitsModal').dialog( 'close' ); } 
                }]
            );    
        }else{
            onContinueCallback();
        }
        
    }
    ;


    return { 
        /**
         * Check for any overlapping visits for the given task in the given episode.
         * It always checks overlappings visits for the patient, and for clinician deppending 
         * on RESTRICTOVERLAPPINGVISITS clinic setting.
         *
         * @param episodeKey         Episode key.
         * @param patientTaskKey     Patient task key for the visit to be checked.
         * @param visitDate          Visit date. (Expecting a string, not a date object.)
         * @param timeIn             Time in. (Expecting a string.)
         * @param timeOut            Time out. (Expecting a string.)
         * @param userKey            AMUserKeyClinician assigned to the task.         
         * @param onContinueCallback Continue Button Callback function ( in patien overlapping popup, and no overlappings )         
         * @param onErrorCallback    Error Callback function
         */
        'checkOverlappings' : function getByPatient( episodeKey, patientTaskKey, visitDate, timeIn, timeOut, userKey, onContinueCallback, onErrorCallback ) {
            $.ajax({
                type     : "GET",
                dataType : "json",
                url      : "/API/services/Episode/OverlappingService.cfc",
                data: {
                    method             : 'getOverlappingVisits',
                    episodeKey         : episodeKey,
                    AMUserKeyClinician : userKey,
                    patientTaskKey     : patientTaskKey,
                    visitDate          : visitDate,
                    timeIn             : timeIn,
                    timeOut            : timeOut
                },
                success: function(resultStruct){
                    if( resultStruct.success ) {
                        if ( resultStruct.data.clinician.length > 0 ) {
                            showClinicianOverlappingMessagePopUp(resultStruct.data.clinician, visitDate);
                        } else if ( resultStruct.data.patient.length > 0 ) {
                            showPatientOverlappingMessagePopUp(resultStruct.data.patient, visitDate, onContinueCallback);
                        } else {
                            onContinueCallback();
                        }
                    } else {
                        onErrorCallback({
                            FRIENDLY : 'An error occurred.',
                            MESSAGE  : 'There was a problem while checking for overlapping visits, please try again later.'
                        });
                    }
                },
                error: function(xhr, textStatus, errorThrown) {
                    var ajaxErrorObject = {
                        FRIENDLY : 'An error occurred.',
                        MESSAGE  : 'Status Returned: ' + textStatus + '<br>Description: ' + xhr.statusText
                    }
                    onErrorCallback(ajaxErrorObject);
                }
            });
        }
        , 
        /**
         * Check for any clinician overlapping visits for the given task in the given episode.
         * It always checks overlappings visits for clinician deppending 
         * on RESTRICTOVERLAPPINGVISITS clinic setting.
         *
         * @param patientTaskKey     Patient task key for the visit to be checked.
         * @param visitDate          Visit date. (Expecting a string, not a date object.)
         * @param timeIn             Time in. (Expecting a string.)
         * @param timeOut            Time out. (Expecting a string.)
         * @param userKey            AMUserKeyClinician assigned to the task.         
         * @param onContinueCallback Continue Button Callback function ( in patien overlapping popup, and no overlappings )         
         * @param onErrorCallback    Error Callback function
         * @param onOverlappingsCallback    Callback function to be called when clinician overlappings are found
         */
        'checkClinicianOverlappings' : function checkClinicianOverlappings( userKey, visitDate, timeIn, timeOut, patientTaskKey, onContinueCallback, onErrorCallback, onOverlappingsCallback ) {
            $.ajax({
                type     : "GET",
                dataType : "json",
                url      : "/API/services/Episode/OverlappingService.cfc",
                data: {
                    method               : 'getClinicianOverlappingVisits'
                    , AMUserKeyClinician : userKey
                    , visitDate          : visitDate
                    , timeIn             : timeIn
                    , timeOut            : timeOut
                    , patientTaskKey     : patientTaskKey
                },
                success: function(resultStruct){
                    if( resultStruct.success ) {
                        if ( resultStruct.data.clinician.length > 0 ) {
                            showClinicianOverlappingMessagePopUp(resultStruct.data.clinician, visitDate);
                            onOverlappingsCallback( resultStruct.data.clinician );
                        } else {
                            onContinueCallback();
                        }
                    } else {
                        onErrorCallback({
                            FRIENDLY : 'An error occurred.',
                            MESSAGE  : 'There was a problem while checking for overlapping visits, please try again later.'
                        });
                    }
                },
                error: function(xhr, textStatus, errorThrown) {
                    var ajaxErrorObject = {
                        FRIENDLY : 'An error occurred.',
                        MESSAGE  : 'Status Returned: ' + textStatus + '<br>Description: ' + xhr.statusText
                    }
                    onErrorCallback(ajaxErrorObject);
                }
            });
        },

        /**
         * Shows a popup message containing information related to a clinician's visit overlapping
         *
         * @param overlappings       An array of objects, each of which has the following key/value pairs:
         *                           * LASTNAME: clinician's last name
         *                           * FIRSTNAME: clinician's first name
         *                           * TASKNAME: visit task name
         *                           * TIMEIN: visit time in
         *                           * TIMEOUT: visit time out
         * @param visitDate          Visit date. (Expecting a string, not a date object.)
         */
        showClinicianOverlappingMessagePopUp: function (overlappings, visitDate) {
            showClinicianOverlappingMessagePopUp(overlappings, visitDate);
        },

        /**
         * Retrieves the visits that a given clinician has scheduled for a given day
         *
         * @param visitDate          A string featuring a date in format MM/DD/YYYY
         * @param clinicianKey       A clincian AMUserKey
         *
         * @return                   A promise resolved with an array of visits or rejected with and error message
         */
        getClinicianVisits: function (visitDate, clinicianKey) {
            var promise = $.Deferred();

            $.ajax({
                type     : 'GET',
                dataType : 'json',
                url      : '/API/services/Episode/OverlappingService.cfc',
                data: {
                    method             : 'getClinicianVisits',
                    AMUserKeyClinician : clinicianKey,
                    visitDate          : visitDate
                },
                success: function (resultStruct) {
                    if (resultStruct.success) {
                        promise.resolve(resultStruct.data.data);
                    } else {
                        promise.reject({
                            FRIENDLY : 'An error occurred.',
                            MESSAGE  : 'There was a problem retrieving the clinician\'s visits, please try again later.'
                        });
                    }
                },
                error: function (xhr, textStatus, errorThrown) {
                    promise.reject({
                        FRIENDLY : 'An error occurred.',
                        MESSAGE  : 'Status Returned: ' + textStatus + '<br>Description: ' + xhr.statusText
                    });
                }
            });

            return promise;
        }
    };   
})();
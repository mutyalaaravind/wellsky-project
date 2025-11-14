angular.module('resources.ptg', ['resources.RESTResource']).factory('Ptg', ['RESTResource', '$q', function (RESTResource, $q) {
    var Ptg = RESTResource('Ptg');

    Ptg.baseUrl = '/KSI/PTGService';
    Ptg.apiVersion = '/v1';
    Ptg.apiVersion2 = '/v2';
    Ptg.getSecondPartBaseUrl = function(clinicKey, clinicBranchKey, apiVersion) {
        var currentAPIVersion = Ptg.apiVersion;
        if (apiVersion) {
            currentAPIVersion = apiVersion;
        }
        return 'Clinic/' + clinicKey + '/ClinicBranch/' + clinicBranchKey + currentAPIVersion + '/';
    };

    Ptg.getGoals = function(clinicKey, clinicBranchKey, problems, showInactive, valueSearch, page, pageSize, orderBy){
        var params = {
            problem: [],
            showInactive: showInactive,
            $skip: (page-1) * pageSize,
            $top: pageSize,
            $orderby: orderBy

        };
        if (valueSearch!=='') {
            params.search= valueSearch;
        }

        $.each( problems, function( key, value ) {
            if (value!==0) {
                params.problem.push(value);
            }
        });

        return Ptg.query({
            path: Ptg.getSecondPartBaseUrl(clinicKey, clinicBranchKey, Ptg.apiVersion2)+'Goal',
            url: Ptg.baseUrl,
            isArray: true,
            params: params,
            errorCallback: function(d, status){
                AlertServide("asdadasdas");
            }
        });
    };

    Ptg.getGoalsCount = function(clinicKey, clinicBranchKey, problems, showInactive, valueSearch){
        var params = {
            problem: [],
            showInactive: showInactive

        };
        if (valueSearch!=='') {
            params.search= valueSearch;
        }

        $.each( problems, function( key, value ) {
            if (value!==0) {
                params.problem.push(value);
            }
        });

        return Ptg.query({
            path: Ptg.getSecondPartBaseUrl(clinicKey, clinicBranchKey)+'Goal/Count',
            url: Ptg.baseUrl,
            params: params
        });
    };

    Ptg.getGoalByKey = function(clinicKey, clinicBranchKey, goalKey){

        return Ptg.query({
            path: Ptg.getSecondPartBaseUrl(clinicKey, clinicBranchKey)+'Goal/'+goalKey,
            url: Ptg.baseUrl
        });
    };

    Ptg.getGoalsByFilters = function(clinicKey, clinicBranchKey, showInactive, disciplineName, episodeKey, problem, search){
        var params = {
            showInactive: showInactive,
            disciplineName: disciplineName
        };

        if (problem !== '') {
            params.problem= problem;
        }

        if (search !== '') {
            params.search= search;
        }

        return Ptg.query({
            path: Ptg.getSecondPartBaseUrl(clinicKey, clinicBranchKey, Ptg.apiVersion2)+'Episode/'+episodeKey+'/Goal',
            url: Ptg.baseUrl,
            isArray: true,
            params: params
        });
    };

    Ptg.getProblems = function(clinicKey, clinicBranchKey){
        return Ptg.query({
            path: Ptg.getSecondPartBaseUrl(clinicKey, clinicBranchKey)+'Problem',
            url: Ptg.baseUrl,
            isArray: true
        });
    };

    Ptg.getProblemsByDisciplineName = function(clinicKey, clinicBranchKey, disciplineName){
        var params = {
            disciplineName: disciplineName
        };

        return Ptg.query({
            path: Ptg.getSecondPartBaseUrl(clinicKey, clinicBranchKey)+'Problem',
            url: Ptg.baseUrl,
            isArray: true,
            params: params
        });
    };

    Ptg.updateGoal = function(clinicKey, clinicBranchKey, goal) {
        return Ptg.updateWithoutJson({
            path: Ptg.getSecondPartBaseUrl(clinicKey, clinicBranchKey)+'Goal/'+goal.goalKey,
            url: Ptg.baseUrl,
            data: goal,
            successCallback: function(response, status) {
                response.status = status;
            }
        });
    };

    Ptg.removePatientGoal = function(clinicKey, clinicBranchKey, patientTaskKey, patientGoalKey){

		return Ptg.queryByPost({
			path: Ptg.getSecondPartBaseUrl(clinicKey, clinicBranchKey)+'PatientTask/'+patientTaskKey+'/PatientGoal/'+patientGoalKey+'/Remove',
			url: Ptg.baseUrl,
			successCallback: function(response, status) {
				response.status = status;
			}
		});
	};

    Ptg.getInterventions = function(clinicKey, clinicBranchKey, problems, showInactive, valueSearch, page, pageSize, orderBy){
        var params = {
            problem: [],
            showInactive: showInactive,
            $skip: (page-1) * pageSize,
            $top: pageSize,
            $orderby: orderBy

        };

        $.each( problems, function( key, value ) {
            if (value!=0) {
                params.problem.push(value);
            }
        });

        if (valueSearch!='') {
            params.search= valueSearch;
        }

        return Ptg.query({
            path: Ptg.getSecondPartBaseUrl(clinicKey, clinicBranchKey)+'Intervention',
            url: Ptg.baseUrl,
            isArray: true,
            params: params
        });
    };

    Ptg.getInterventionsCount = function(clinicKey, clinicBranchKey, problems, showInactive, valueSearch){
        var params = {
            problem: [],
            showInactive: showInactive

        };
        if (valueSearch!='') {
            params.search= valueSearch;
        };

        $.each( problems, function( key, value ) {
            if (value!=0) {
                params.problem.push(value);
            }
        });

        return Ptg.query({
            path: Ptg.getSecondPartBaseUrl(clinicKey, clinicBranchKey)+'Intervention/Count',
            url: Ptg.baseUrl,
            params: params
        });
    };

    Ptg.getInterventionsByFilters = function(clinicKey, clinicBranchKey, showInactive, goalKey, search, problems){
        var params = {
            showInactive: showInactive,
        };

        var url = "";
        if (goalKey!=0) {
            url = 'Goal/'+goalKey+'/';
        }

        if (search !== '') {
            params.search= search;
        }
        if (angular.isDefined(problems)) {
            params.problem = problems;
        }
        return Ptg.query({
            path: Ptg.getSecondPartBaseUrl(clinicKey, clinicBranchKey)+url+'Intervention',
            url: Ptg.baseUrl,
            isArray: true,
            params: params
        });
    };

    Ptg.getInterventionByKey = function(clinicKey, clinicBranchKey, interventionKey){
        return Ptg.query({
            path: Ptg.getSecondPartBaseUrl(clinicKey, clinicBranchKey)+'Intervention/'+interventionKey,
            url: Ptg.baseUrl
        });
    };

    Ptg.insertIntervention = function(clinicKey, clinicBranchKey, intervention) {
        return Ptg.insert({
            path: Ptg.getSecondPartBaseUrl(clinicKey, clinicBranchKey)+'Intervention',
            url: Ptg.baseUrl,
            data: intervention,
            successCallback: function(response, status) {
                response.status = status;
            }
        });
    };

    Ptg.insertFreeTextIntervention = function(clinicKey, clinicBranchKey, intervention) {
        return Ptg.insert({
            path: Ptg.getSecondPartBaseUrl(clinicKey, clinicBranchKey)+'InterventionFreeText',
            url: Ptg.baseUrl,
            data: intervention,
            successCallback: function(response, status) {
                response.status = status;
            }
        });
    };

    Ptg.getDisciplines = function(clinicKey, clinicBranchKey){
        return Ptg.query({
            path: Ptg.getSecondPartBaseUrl(clinicKey, clinicBranchKey)+'Discipline',
            url: Ptg.baseUrl,
            isArray: true
        });
    };

    Ptg.insertGoal = function(clinicKey, clinicBranchKey, goal) {
        return Ptg.insert({
            path: Ptg.getSecondPartBaseUrl(clinicKey, clinicBranchKey)+'Goal',
            url: Ptg.baseUrl,
            data: goal,
            successCallback: function(response, status) {
                response.status = status;
            }
        });
    };

    Ptg.insertFreeTextGoal = function(clinicKey, clinicBranchKey, goal) {
        return Ptg.insert({
            path: Ptg.getSecondPartBaseUrl(clinicKey, clinicBranchKey)+'GoalFreeText',
            url: Ptg.baseUrl,
            data: goal,
            successCallback: function(response, status) {
                response.status = status;
            }
        });
    };

    Ptg.updateIntervention = function(clinicKey, clinicBranchKey, intervention) {
        return Ptg.updateWithoutJson({
            path: Ptg.getSecondPartBaseUrl(clinicKey, clinicBranchKey)+'Intervention/'+intervention.interventionKey,
            url: Ptg.baseUrl,
            data: intervention,
            successCallback: function(response, status) {
                response.status = status;
            }
        });
    };

    Ptg.updateGoal = function(clinicKey, clinicBranchKey, goal) {
        return Ptg.updateWithoutJson({
            path: Ptg.getSecondPartBaseUrl(clinicKey, clinicBranchKey)+'Goal/'+goal.goalKey,
            url: Ptg.baseUrl,
            data: goal,
            successCallback: function(response, status) {
                response.status = status;
            }
        });
    };

    Ptg.patchIntervention = function(clinicKey, clinicBranchKey, intervention) {
        return Ptg.patch({
            path: Ptg.getSecondPartBaseUrl(clinicKey, clinicBranchKey)+'Intervention/'+intervention.interventionKey,
            url: Ptg.baseUrl,
            data: intervention,
            successCallback: function(response, status) {
                response.status = status;
            }
        });
    };

    Ptg.patchGoal = function(clinicKey, clinicBranchKey, goal) {
        return Ptg.patch({
            path: Ptg.getSecondPartBaseUrl(clinicKey, clinicBranchKey)+'Goal/'+goal.goalKey,
            url: Ptg.baseUrl,
            data: goal,
            successCallback: function(response, status) {
                response.status = status;
            }
        });
    };

    Ptg.patchGoalProgressNote = function(clinicKey, clinicBranchKey, patientGoalKey, data) {
        return Ptg.patch({
            path: Ptg.getSecondPartBaseUrl(clinicKey, clinicBranchKey)+'PatientGoal/'+patientGoalKey+'/DocumentProgressToGoal',
            url: Ptg.baseUrl,
            data: data,
            successCallback: function(response, status) {
                response.status = status;
            }
        });
    };

    Ptg.patchGoalProgressToDefer = function(clinicKey, clinicBranchKey, patientGoalKey, data) {
        return Ptg.patch({
            path: Ptg.getSecondPartBaseUrl(clinicKey, clinicBranchKey)+'PatientGoal/'+patientGoalKey+'/Defer',
            url: Ptg.baseUrl,
            data: data,
            successCallback: function(response, status) {
                response.status = status;
            }
        });
    };

    Ptg.patchGoalProgressToMet = function(clinicKey, clinicBranchKey, patientGoalKey, data) {
        return Ptg.patch({
            path: Ptg.getSecondPartBaseUrl(clinicKey, clinicBranchKey, Ptg.apiVersion2)+'PatientGoal/'+patientGoalKey+'/Met',
            url: Ptg.baseUrl,
            data: data,
            successCallback: function(response, status) {
                response.status = status;
            }
        });
    };

    Ptg.patchGoalProgressToNotAttainable = function(clinicKey, clinicBranchKey, patientGoalKey, data) {
        return Ptg.patch({
            path: Ptg.getSecondPartBaseUrl(clinicKey, clinicBranchKey, Ptg.apiVersion2)+'PatientGoal/'+patientGoalKey+'/NotAttained',
            url: Ptg.baseUrl,
            data: data,
            successCallback: function(response, status) {
                response.status = status;
            }
        });
    };

    Ptg.patchUndoDefer = function(clinicKey, clinicBranchKey, patientGoalKey, data) {
        return Ptg.patch({
            path: Ptg.getSecondPartBaseUrl(clinicKey, clinicBranchKey)+'PatientGoal/'+patientGoalKey+'/UndoDefer',
            url: Ptg.baseUrl,
            data: data,
            successCallback: function(response, status) {
                response.status = status;
            }
        });
    };

    Ptg.getPatientData = function(patientTaskKey){
        return Ptg.query({
            path: 'PatientData/PatientTask/'+eval(patientTaskKey)
        });
    };

    Ptg.getProgressToGoalByPatientTask = function(clinicKey, clinicBranchKey, patientTaskKey, patientGoalStatus, discipline) {
        
        var disciplineURL = "";
        if (discipline) {
            disciplineURL = "&discipline="+discipline
        }
        var url = Ptg.getSecondPartBaseUrl(clinicKey, clinicBranchKey) + 'AM/PatientTask/' + patientTaskKey +
            '/PatientGoal?patientGoalStatus=' + patientGoalStatus + disciplineURL;

        return Ptg.query({path: url, url: Ptg.baseUrl});
    };

    Ptg.getDocumentProgressList = function(clinicKey, clinicBranchKey) {
        return Ptg.query({
            path: Ptg.getSecondPartBaseUrl(clinicKey, clinicBranchKey)+'DocumentProgress',
            url: Ptg.baseUrl,
            isArray: true
        });
    };

    Ptg.assignGoalToPatient = function(clinicKey, clinicBranchKey, progressToGoalKey, patientTaskKey, goal) {
        return Ptg.insert({
            path: Ptg.getSecondPartBaseUrl(clinicKey, clinicBranchKey)+'ProgressToGoal/'+progressToGoalKey+'/PatientTask/'+patientTaskKey+'/PatientGoal',
            url: Ptg.baseUrl,
            data: goal,
            successCallback: function(response, status) {
                response.status = status;
            }
        });
    };

    Ptg.getPatientGoalByKey = function(clinicKey, clinicBranchKey, patientTaskKey, patientGoalKey){
        return Ptg.query({
            path: Ptg.getSecondPartBaseUrl(clinicKey, clinicBranchKey)+'PatientTask/'+patientTaskKey+'/PatientGoal/'+patientGoalKey,
            url: Ptg.baseUrl
        });
    };

    Ptg.assignInterventionToGoal = function(clinicKey, clinicBranchKey, patientTaskKey, patientGoalKey, intervention) {

        return Ptg.insert({
            path: Ptg.getSecondPartBaseUrl(clinicKey, clinicBranchKey)+'PatientTask/'+patientTaskKey+'/PatientGoal/'+patientGoalKey+'/PatientGoalIntervention',
            url: Ptg.baseUrl,
            data: intervention,
            successCallback: function(response, status) {
                response.status = status;
            }
        });
    };

    Ptg.getPatientGoalByPatientTask = function(clinicKey, clinicBranchKey, patientTaskKey) {
        var path = Ptg.getSecondPartBaseUrl(clinicKey, clinicBranchKey) + 'PatientGoal/PatientTask/' + patientTaskKey;
        return Ptg.query({
            isArray: true,
            path: path,
            url: Ptg.baseUrl
        });
    }

    Ptg.getSyncStatus = function getSyncStatus(clinicKey, clinicBranchKey, patientTaskKey) {
        return Ptg.query({
            path: Ptg.getSecondPartBaseUrl(clinicKey, clinicBranchKey)+'PatientTask/' + patientTaskKey + '/SyncStatus',
            url: Ptg.baseUrl
        });
    }

    Ptg.getInstructionalMethodList = function(clinicKey, clinicBranchKey){
        return Ptg.query({
            path: Ptg.getSecondPartBaseUrl(clinicKey, clinicBranchKey)+'InstructionalMethod',
            url: Ptg.baseUrl,
            isArray: true
        });
    };

    Ptg.performIntervention = function(clinicKey, clinicBranchKey, patientGoalInterventionKey, perform) {
        return Ptg.patch({
            path: Ptg.getSecondPartBaseUrl(clinicKey, clinicBranchKey)+'PatientGoalIntervention/'+patientGoalInterventionKey+'/Perform',
            url: Ptg.baseUrl,
            data: perform,
            successCallback: function(response, status) {
                response.status = status;
            }
        });
    };

    Ptg.completeIntervention = function(clinicKey, clinicBranchKey, patientGoalInterventionKey, patientTask) {
        return Ptg.patch({
            path: Ptg.getSecondPartBaseUrl(clinicKey, clinicBranchKey)+'PatientGoalIntervention/'+patientGoalInterventionKey+'/Complete',
            url: Ptg.baseUrl,
            data: patientTask,
            successCallback: function(response, status) {
                response.status = status;
            }
        });
    };

    Ptg.discontinueIntervention = function(clinicKey, clinicBranchKey, patientGoalInterventionKey, patientTask) {
        return Ptg.patch({
            path: Ptg.getSecondPartBaseUrl(clinicKey, clinicBranchKey)+'PatientGoalIntervention/'+patientGoalInterventionKey+'/Discontinue',
            url: Ptg.baseUrl,
            data: patientTask,
            successCallback: function(response, status) {
                response.status = status;
            }
        });
    };

    Ptg.removeIntervention = function(clinicKey, clinicBranchKey, patientGoalInterventionKey, patientTask) {
        return Ptg.queryByPost({
            path: Ptg.getSecondPartBaseUrl(clinicKey, clinicBranchKey)+'PatientTask/'+patientTask.fPatientTaskKey+'/PatientGoalIntervention/'+patientGoalInterventionKey+'/Remove',
            url: Ptg.baseUrl,
            successCallback: function(response, status) {
                response.status = status;
            }
        });
    };

    Ptg.getGoalsAndInterventions = function getGoalsAndInterventions(
        clinicKey,
        clinicBranches,
        episodeStartDate,
        episodeEndDate,
        patientDate,
        caseManagers
    ) {
        var result;

        if (angular.isDefined(patientDate)) {
            result = getGoalsAndInterventionsByPatientsActiveAsOf(clinicKey, clinicBranches, patientDate, caseManagers);
        } else {
            result = getGoalsAndInterventionsByEpisode(clinicKey, clinicBranches, episodeStartDate, episodeEndDate, caseManagers);
        }

        return result;
    }

    function getGoalsAndInterventionsByEpisode(clinicKey, clinicBranches, episodeStartDate, episodeEndDate, caseManagers) {
        var params = {
            listClinicBranchKey: clinicBranches,
            endDate: episodeEndDate,
            startDate: episodeStartDate
        }

        if (caseManagers) {
            params.caseManagerKey = caseManagers
        }


        return Ptg.query({
            path: 'Clinic/' + clinicKey + Ptg.apiVersion + '/Report/GoalsAndInterventions',
            url: Ptg.baseUrl,
            isArray: true,
            params: params 
        });
    }

    function getGoalsAndInterventionsByPatientsActiveAsOf(clinicKey, clinicBranches, patientDate, caseManagers) {
        var params = {
            listClinicBranchKey: clinicBranches,
            patientsActiveAsOf: patientDate
        }

        if (caseManagers) {
            params.caseManagerKey = caseManagers
        }

        return Ptg.query({
            path: 'Clinic/' + clinicKey + Ptg.apiVersion + '/Report/GoalsAndInterventionsByPatientsActiveAsOf',
            url: Ptg.baseUrl,
            isArray: true,
            params: params
        });
    }

    Ptg.getPatientTaskDiscipline = function(clinicKey, clinicBranchKey, patientTaskKey) {
        return Ptg.query({
            path: Ptg.getSecondPartBaseUrl(clinicKey, clinicBranchKey)+'PatientTask/' + patientTaskKey + '/Discipline',
            url: Ptg.baseUrl
        });
    };

    Ptg.setPatientTaskDiscipline = function(clinicKey, clinicBranchKey, patientTaskKey, discipline) {
        return Ptg.patch({
            path: Ptg.getSecondPartBaseUrl(clinicKey, clinicBranchKey)+'PatientTask/' + patientTaskKey + '/Discipline',
            url: Ptg.baseUrl,
            data: discipline,
            successCallback: function(response, status) {
                response.status = status;
            }
        });
    };

    Ptg.getNextEpisode = function(clinicKey, clinicBranchKey, patientTaskKey){
        return Ptg.query({
        	path: Ptg.getSecondPartBaseUrl(clinicKey, clinicBranchKey)+'PatientTaskKey/'+patientTaskKey+'/NextEpisode',
            url: Ptg.baseUrl
        });
    };
    
    Ptg.pushGoalToNextEpisode = function(clinicKey, clinicBranchKey, nextEpisodeKey, patientGoalKey, patientTaskKey, instruction, targetDate, goalLength) {
    	
    	var data = {
    	    instruction: instruction,
    		targetDate: targetDate,
    		goalLength: goalLength
    	}
    	
    	return Ptg.insert({
            path: Ptg.getSecondPartBaseUrl(clinicKey, clinicBranchKey, Ptg.apiVersion2)+'PatientGoal/'+patientGoalKey
            	+'/PatientTask/'+patientTaskKey+'/Episode/'+nextEpisodeKey+'/PushGoal',
            url: Ptg.baseUrl,
            data: data,
            successCallback: function(response, status) {
                response.status = status;
            }
        });
    };
    
    Ptg.getInterventionsByEpisodeKey = function(clinicKey, clinicBranchKey, episodeKey){

        return Ptg.query({
            path: Ptg.getSecondPartBaseUrl(clinicKey, clinicBranchKey)+'Episode/'+episodeKey+'/Audit/Interventions',
            isArray: true,
            url: Ptg.baseUrl
        });
    };
    
    Ptg.modifyGoal = function(clinicKey, clinicBranchKey, patientGoalKey, patientGoal) {

        return Ptg.updateWithoutJson({
            path: Ptg.getSecondPartBaseUrl(clinicKey, clinicBranchKey)+'PatientGoal/'+patientGoalKey+'/Modify',
            url: Ptg.baseUrl,
            data: patientGoal,
            successCallback: function(response, status) {
                response.status = status;
            }
        });
    };
    
    Ptg.modifyIntervention = function(clinicKey, clinicBranchKey, interventionKey, intervention) {

        return Ptg.updateWithoutJson({
            path: Ptg.getSecondPartBaseUrl(clinicKey, clinicBranchKey)+'PatientGoalIntervention/'+interventionKey+'/Modify',
            url: Ptg.baseUrl,
            data: intervention,
            successCallback: function(response, status) {
                response.status = status;
            }
        });
    };
    
    Ptg.updatePTGIn485 = function(patientTaskKey) {
        
        return Ptg.insert({
            path: 'update485/patientTask/'+patientTaskKey
        });
    };

    Ptg.getPatientAuditSummary = function(clinicKey, clinicBranchKey, episodeKey, disciplineName, visitDate){
        if (!visitDate) 
            visitDate = new Date();
        else
            visitDate = new Date(visitDate);
        formatedVisitDate = visitDate.getFullYear() + "-" + (visitDate.getMonth() + 1) + "-" + visitDate.getDate()

        return Ptg.query({
            path: Ptg.getSecondPartBaseUrl(clinicKey, clinicBranchKey, Ptg.apiVersion2)+'Episode/'+episodeKey+'/Audit/AuditSummary',
            url: Ptg.baseUrl,
            isArray: true,
            params: {
                disciplineName: disciplineName,
                visitDate: formatedVisitDate
            }
        })
    }

    Ptg.getPatientAuditUpdateAndProgress = function(clinicKey, clinicBranchKey, PatientTask){
        return Ptg.query({
            path: Ptg.getSecondPartBaseUrl(clinicKey, clinicBranchKey, Ptg.apiVersion2)+'PatientTask/'+PatientTask+'/Audit/AuditUpdateAndProgress',
            url: Ptg.baseUrl,
            isArray: false
        })
    }
    
    
    return Ptg;
}]);

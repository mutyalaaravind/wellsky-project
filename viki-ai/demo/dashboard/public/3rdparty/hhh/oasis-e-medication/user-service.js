/* Service for logged in User*/
angular.module('services.user.user', ['services.util.util', 'resources.cost-center']).factory('UserService', ['$rootScope','$http', 'UtilService', 'CostCenter', function ($rootScope,$http, UtilService, CostCenter) {

    var UserService = {},
        servicePath = '/API/services/User/UserService.cfc';

    /* Constructor */
    UserService.User = function(data, currentUserKey){
        angular.extend(this, data.USER);
        if (currentUserKey.substr(0,10) === 'CLINICUSER'){
            var clinicUserKey = currentUserKey.substr(11,currentUserKey.length);
            this.corporationKey = data.CORPORATIONKEY;
            angular.extend(this, clinicuser());
            return angular.extend(this, data.CLINICUSER[clinicUserKey]);
        }else if (currentUserKey.substr(0,15) === 'CORPORATIONUSER'){
            var corporationUserKey = currentUserKey.substr(16,currentUserKey.length);
            angular.extend(this, corporationuser());
            return angular.extend(this, data.CORPORATIONUSER[corporationUserKey]);
        }
        else{
            return angular.extend(this, defaultUser);
        }

    };

    UserService.checkUsername = function(username){
        return $http.get(servicePath + '?method=checkUsername&username=' + username ).
            then(function(result){
                return result.data;
            });
    };

    UserService.isCorpUserEmailAvailable = function(email, usersKey){
        return $http.get(servicePath + '?method=isCorpUserEmailAvailable&email=' + email +'&usersKey=' + usersKey ).
            then(function(result){
                return result.data;
            });
    };

    UserService.isCorpUserEmailAvailablev2 = function(email, usersKey, corporationKey){
        return $http.get(servicePath, {
            params: {
                method: 'isCorpUserEmailAvailable',
                email: email,
                usersKey: usersKey,
                corporationKey: corporationKey
            }}).
            then(function(result){
                return result.data;
            });
    };

    UserService.checkSignature = function(userKey,signature){
        return $http.get(servicePath + '?method=checkSignature&userKey=' + userKey + '&signature=' + signature ).
            then(function(result){
                return result.data;
            });
    };

    UserService.hasSignature = function(userKey){
        return $http.get(servicePath + '?method=hasSignature&userKey=' + userKey).
            then(function(result){
                return result.data;
            });
    };

    UserService.getSignatureString = function(clinicUserKey){
        return $http.get(servicePath + '?method=getSignatureString&clinicUserKey=' + clinicUserKey).
            then(function(result){
                    return result.data;
            });
    };

    UserService.resetPassword = function(userkey, password){
        password = password || UtilService.generatePassword();

        return $http.get(servicePath, {
            params: {
                method: 'resetPassword',
                userkey: userkey,
                password: password
            }});
    };

    UserService.toggleStatusByUser = function(userKey, active){
        return $http.get(servicePath, {
            params: {
                method: 'toggleStatusByUser',
                userkey: userKey,
                active: active
            }});
    };
	
	/*
		Figures out the clinic branch (short) name using this object's clinicBranchArray property.
		@branchKeyList: is either of type number or string (comma delimited string)
	*/
	UserService.getBranchName = function(branchKeyList) {
		//immediately box the first argument to a string...
		var branchFilter = branchKeyList.toString(),
			branchName = '';
		
		//now we can check to see if the argument is a collection of branch keys, if so it's obviously 'All Branches'
		if( branchFilter.split(',').length > 1 ){
			branchName = 'All Branches';
		} else{
			//otherwise walk the clinic branch array to check the current branch key against the argument
			angular.forEach(this.clinicBranchArray, function(branchObject, branchIndex) {
				if( branchObject.CLINICBRANCHKEY === branchKeyList ){
					branchName = branchObject.BRANCHSHORTNAME;
				}
			});
		}
		
		return branchName;
	};
	
	/*
		Returns an array of clinic branch keys from the clinic branches known to this object.
	*/
	UserService.getBranchKeys = function() {
		var branchKeyList = [];
		
		//comb the clinic branch array on this object for clinic keys
		angular.forEach(this.clinicBranchArray, function(branchObject, i) {
			branchKeyList.push(branchObject.CLINICBRANCHKEY);
		});
		
		return branchKeyList;
	};
	
    UserService.hasCostCentersWithRates = function( clinicUserKey ){
        var hasCostCentersWithRates = false;
        $.ajax({
            type: 'GET',
            url: '/rest/V1/CostCenter/User/' + clinicUserKey,
            dataType: 'json',
            async: false
        }).done(function(data){
            if (data.length > 0) {
                hasCostCentersWithRates = true;
            } 
        });
        return hasCostCentersWithRates;
    };

    UserService.getDefaultClinicUserKey = function(corporationUserKey) {
        // Convenience since we are presumably getting the corporationUserKey from the UserService anyway.
        if (corporationUserKey === undefined) {
            if (this.corporationUserKey === undefined)
                return 0;

            corporationUserKey = this.corporationUserKey;
        }


        return $http.get(servicePath, {params: {method: 'getDefaultClinicUser', corporationUserKey: corporationUserKey}} ).
            then(function(result){
                return result.data.data.defaultClinicUserKey;
            });
    };

    UserService.isCorporateUser = function() {
        return this.instance === 'CM';
    };

    return UserService;
}]);


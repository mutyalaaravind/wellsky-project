function clinicuser(){
	var UserService = {};

   /*Finds a role for any clinic branch*/
    UserService.hasUserRoleByKey = function(role) {
        for (var i=0; i< this.clinicBranchArray.length; i++){
            var clinicBranchKey = this.clinicBranchArray[i].CLINICBRANCHKEY;
            if(this.roles[clinicBranchKey].indexOf(role) > -1){
                return true;
            }
        }
        return false;
    };

    UserService.hasUserRoleInAllBranches = function (role) {
        var clinicBranchesWithPermission = this.clinicBranchArray.map(function (branchArray) {
            return this.roles[branchArray.CLINICBRANCHKEY].some(function(currentRole) {
                return currentRole === role;
            });
        }.bind(this));

        return clinicBranchesWithPermission.every(function(x) { return !!x});
    }

	return UserService;
}

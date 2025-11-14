angular.module('resources.cost-center', ['resources.RESTResource'])
	
	.factory('CostCenter', ['RESTResource', function (RESTResource) {

	var CostCenter = RESTResource('CostCenter');

	CostCenter.getCostCenterByCorporation = function(corporationKey){
		return CostCenter.query({
			path: 'Corporation/'+corporationKey
		});
	};

	CostCenter.getCostCenterByUser = function(userKey){
		return CostCenter.query({
			path: 'User/'+userKey,
			isArray: true
		});
	};
	
	CostCenter.save = function(costCenterData) {
		return CostCenter.update({
			path: 'save',
			data: costCenterData
		});
	};
	
	CostCenter.delete = function(costCenterData) {
		return CostCenter.update({
			path: 'delete',
			data: costCenterData
		});
	};
	
	return CostCenter;

}]);
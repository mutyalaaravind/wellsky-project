/*jslint es5: true */
angular.module('resources.RESTResource', ['services.util.form-util']).factory('RESTResource', ['$http', '$q', 'REST_CONFIG', 'FormUtilService', function($http, $q, REST_CONFIG, FormUtilService){

    function RESTResourceFactory(resource){

        var defaultConfig = {
            url: REST_CONFIG.baseURL + resource,
            path: null,
            params: {},
            data: {},
            headers: {},
            cache: false,
            isArray: false,
            successCallback: function(result, status, headers, config){
            },
            errorCallback: function(result, status, headers, config){

            }
        };

        var thenFactoryMethod = function(httpPromise, successCallback, errorCallback, isArray) {
            var scb = successCallback || angular.noop;
            var ecb = errorCallback || angular.noop;
            var isArrayTest = isArray || false;

            return httpPromise.then(function(response) {
                var result;
                if (isArrayTest) {
                    result = [];
                    for (var i = 0; i < response.data.length; i++) {
                        result.push(new Resource(response.data[i]));
                    }

                } else {
                    result = new Resource(response.data);
                }

                scb(result, response.status, response.headers, response.config);
                return result;
            }, function(response) {
                ecb(response.data, response.status, response.headers, response.config);
                return response.data;
            });
        };

        var Resource = function(data){
            angular.extend(this, data);
        };

        var prepConfig = function(configObject){
            var defaultConfigCopy = angular.copy(defaultConfig);
            var config = angular.isObject(configObject) ? angular.extend(defaultConfigCopy, configObject) : defaultConfig;
            config.url = config.path !== null ? (config.url + '/' + config.path) : config.url;
            return config;
        };

        Resource.all = function(configObject){
            return Resource.query(configObject);
        };

        Resource.query = function(configObject){
           var config = prepConfig(configObject);
           var httpPromise = $http.get(config.url, config);
           return thenFactoryMethod(httpPromise, config.successCallback, config.errorCallback, config.isArray);
        };

        // leverage greater size of POST body
        Resource.queryByPost = function(configObject){
            var config = prepConfig(configObject);
            var httpPromise = $http.post(config.url, config.data);
            return thenFactoryMethod(httpPromise, config.successCallback, config.errorCallback, config.isArray);

        };

        Resource.byKey = function(key, configObject){
            var config = angular.isObject(configObject) ? angular.extend({path:key}, configObject) : {path:key};
            return Resource.query(config);
        };
        
        Resource.downloadFile = function(configObject){
            var config = prepConfig(configObject);
            return $http.get(config.url, config);
        };

        Resource.downloadFileByPost = function(configObject){
            var config = prepConfig(configObject);
            return $http.post(config.url, config.data, config);
        };

        Resource.forDropdown = function(primaryKey, column, configObject){
            return Resource.all(configObject).then(function(result){
                return FormUtilService.resultToDropdown(result, primaryKey, column);
            });
        };

        Resource.insert = function(configObject){
            var config = prepConfig(configObject);
            var httpPromise = $http.post(config.url, config.data);
            return thenFactoryMethod(httpPromise, config.successCallback, config.errorCallback, config.isArray);
        };

        Resource.insertWithHeaders = function(configObject){
            var config = prepConfig(configObject);
            var httpPromise =  $http({
                url: config.url,
                method: 'POST',
                headers: config.headers,
                data: config.data
            });
            return thenFactoryMethod(httpPromise, config.successCallback, config.errorCallback, config.isArray);
        };

        Resource.getWithHeaders = function(configObject){
            var config = prepConfig(configObject);
            var httpPromise =  $http({
                url: config.url,
                method: 'GET',
                headers: config.headers
            });
            return thenFactoryMethod(httpPromise, config.successCallback, config.errorCallback, config.isArray);
        };

        Resource.update = function(configObject){
            var config = prepConfig(configObject);
            var httpPromise = $http.put(config.url, JSON.stringify(config.data));
            return thenFactoryMethod(httpPromise, config.successCallback, config.errorCallback, config.isArray);
        };

        Resource.updateWithoutJson = function(configObject){
             var config = prepConfig(configObject);
             var httpPromise = $http.put(config.url, config.data);
             return thenFactoryMethod(httpPromise, config.successCallback, config.errorCallback, config.isArray);
         };

         Resource.updateWithPutJson = function(configObject){
            var config = prepConfig(configObject);
            var httpPromise =  $http({
                url: config.url,
                method: 'PUT',
                headers: config.headers,
                data: config.data
            });
            return thenFactoryMethod(httpPromise, config.successCallback, config.errorCallback, config.isArray);
        };       
 
        Resource.patch = function(configObject){
             var config = prepConfig(configObject);
             var httpPromise = $http({ method: 'PATCH', url: config.url, data: config.data});
             return thenFactoryMethod(httpPromise, config.successCallback, config.errorCallback, config.isArray);
        };
        
        Resource['delete'] = function(configObject){
            var config = prepConfig(configObject);
            //using $http.delete() throws a parse error in IE8
            var httpPromise = $http['delete'](config.url);
            return thenFactoryMethod(httpPromise, config.successCallback, config.errorCallback, config.isArray);
        };

        return Resource;

    }

    return RESTResourceFactory;

}]);

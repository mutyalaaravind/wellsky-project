angular.module('resources.episodeFrequency', ['resources.RESTResource']).factory('EpisodeFrequency', ['RESTResource', function (RESTResource) {

    var EpisodeFrequency = RESTResource('EpisodeFrequency');

    EpisodeFrequency.getEpisodeFrequencyByEpisodeKey = function(episodeKey, listFrequencyStatusKey, pending) {
        var configuration = {
            path: 'byEpisode/' + episodeKey,
            isArray: true,
            params: {}
        };

        if (angular.isDefined(listFrequencyStatusKey)) {
            configuration.params.listFrequencyStatusKey = listFrequencyStatusKey;
        }

        if (angular.isDefined(pending)) {
            configuration.params.pending = pending;
        }

        return EpisodeFrequency.query(configuration);
    };

    EpisodeFrequency.getEpisodeFrequencyByTaskType = function(episodeKey, taskType, statusKeyList, pending){
        return EpisodeFrequency.query({
            path: 'byTaskType/' + episodeKey,
            params : {TaskTypeList : taskType, ListFrequencyStatusKeyList : statusKeyList, Pending: pending},
            isArray: true
        });
    };

    EpisodeFrequency.saveEpisodeFrequency = function(configuration) {
        configuration.isArray =  true;
        return EpisodeFrequency.update(configuration);
    };

    EpisodeFrequency.updateEpisodeFrequencyActive = function(episodeFrequencyKeyList, active) {
        return EpisodeFrequency.update({
            path:'updateEpisodeFrequencyActive',
            data: {
                episodeFrequencyKeyList: episodeFrequencyKeyList,
                active: active
            }
        });
    };

    EpisodeFrequency.getEpisodeFrequencyByPatientTask = function getEpisodeFrequencyByPatientTask(
        patientTaskKey,
        active
    ) {
        var params = {};

        if (angular.isDefined(active)) {
            params.active = active;
        }

        return EpisodeFrequency.query({
            path: 'byPatientTask/' + patientTaskKey,
            isArray: true,
            params: params
        });
    }

    EpisodeFrequency.getEpisodeDiscontinuationStatus = function getEpisodeDiscontinuationStatus(episodeKey) {
        return EpisodeFrequency.query({
            path: 'episodeDiscontinuationStatus/' + episodeKey
        });
    }

    return EpisodeFrequency;

}]);


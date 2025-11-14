(function() {
    'use strict';

    angular
        .module('amng.conditions-of-participation', [
            'AMNG',
            'resources.language',
            'resources.list-relationship-type',
            'resources.list-representative-type'
        ])
        .controller('ConditionsOfParticipationController', controller)
        .constant('COPConstants', {
            OTHER_LANGUAGE_KEY: 6,
            OTHER_RELATIONSHIP_TYPE_KEY: 7
        });

    controller.$inject = ['Language', 'ListRelationshipType', 'ListRepresentativeType', 'COPConstants', '$window', '$q', '$rootScope'];

    function controller(Language, ListRelationshipType, ListRepresentativeType, COPConstants, $window, $q, $rootScope) {
        var vm = angular.extend(this, {
            // members
            languages: [],
            languagesVisible: false,
            relationshipTypes: [],
            relationshipTypesVisible: false,
            representativeTypes: [],
            representativeTypesVisible: false,
            otherLanguage: '',
            otherRelationshipType: '',
            patientRepresentative: { enabled: false },

            // methods
            initializeLanguage: initializeLanguage,
            initializePatientRepresentative: initializePatientRepresentative,
            getLanguages: getLanguages,
            getRelationshipTypes: getRelationshipTypes,
            getRepresentativeTypes: getRepresentativeTypes,
            validateLanguageForOther: validateLanguageForOther,
            validateRelationshipTypeForOther: validateRelationshipTypeForOther
        });

        function initializeLanguage(primaryLanguageKey, otherLanguage) {
            if (primaryLanguageKey) {
                vm.primaryLanguage = primaryLanguageKey;
            }
            if (otherLanguage) {
                vm.otherLanguage = otherLanguage;
            }
            vm.getLanguages();
        }
        
        function initializePatientRepresentative(encodedPatientRepresentative) {

            var patientRepresentative = decodePatientRepresentativeFields(encodedPatientRepresentative);

            if (patientRepresentative) {
                vm.patientRepresentative = patientRepresentative;
                vm.patientRepresentative.enabled = true;
                vm.patientRepresentative.phoneA = patientRepresentative.phone.substring(0,3);
                vm.patientRepresentative.phoneB = patientRepresentative.phone.substring(3,6);
                vm.patientRepresentative.phoneC = patientRepresentative.phone.substring(6);
            }
            else {
                vm.patientRepresentative.patientRepresentativeKey = 0;
                vm.patientRepresentative.enabled = false;
            }

            vm.getLanguages();
            vm.getRelationshipTypes();
            vm.getRepresentativeTypes();
        }
        
        function decodePatientRepresentativeFields(encodedPatientRepresentative){
            var patientRepresentative = encodedPatientRepresentative;

            for(var prop in patientRepresentative){
                if(typeof patientRepresentative[prop] === 'string'){
                    patientRepresentative[prop] = encodedPatientRepresentative[prop].replace(/(x[0-9A-F]{2})/g, decodeHexString);
                }
            }
            return patientRepresentative;
        }

        function decodeHexString(match) {
            var hexCode = match.slice(1);
            var char = '';
            for (var i = 0; (i < hexCode.length && hexCode.substr(i, 2) !== '00'); i += 2)
                char += String.fromCharCode(parseInt(hexCode.substr(i, 2), 16));
            return char;
        }
        
        function getLanguages() {
            Language.forDropdown('LISTLANGUAGEKEY', 'LANGUAGENAME', { params: {orderBy:'ListLanguageKey'} }).then(function(languages){
                vm.languages = languages;
                vm.languagesVisible = true;
             });
        }
        
        function getRelationshipTypes() {
            ListRelationshipType.forDropdown('LISTRELATIONSHIPTYPEKEY', 'LISTRELATIONSHIPTYPEDESC', { params: {orderBy:'ListRelationshipTypeKey'} }).then(function(relationshipTypes) {
                vm.relationshipTypes = relationshipTypes;
                vm.relationshipTypesVisible = true;
            });
        }
        
        function getRepresentativeTypes() {
            ListRepresentativeType.all().then(function(representativeTypes) {
                vm.representativeTypes = representativeTypes;
                vm.representativeTypesVisible = true;
            });
        }
        
        function validateLanguageForOther(primaryLanguage) {
            
            if (primaryLanguage && primaryLanguage==COPConstants.OTHER_LANGUAGE_KEY) {
                return true;
            }
            vm.otherLanguage = '';
            vm.patientRepresentative.otherLanguage = '';
            
            return false;
        }

        function validateRelationshipTypeForOther(relationshipType) {
            
            if (relationshipType && relationshipType==COPConstants.OTHER_RELATIONSHIP_TYPE_KEY) {
                return true;
            }
            vm.patientRepresentative.otherRelationshipType = '';
            
            return false;
        }
        
    }

}) ();

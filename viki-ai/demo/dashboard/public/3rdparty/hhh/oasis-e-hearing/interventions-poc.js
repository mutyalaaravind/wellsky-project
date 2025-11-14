(function() {
    'use strict';

    angular
        .module('amng.interventions-poc', [
            'AMNG',
            'resources.ptg',
            'LocalStorageModule',
            'services.ptg.instruction-preview'
        ])
        .controller('InterventionsPocController', controller);

    controller.$inject = ['Ptg', 'UserService', 'localStorageService', '$rootScope'];

    function controller(Ptg, UserService, localStorageService, $rootScope) {
        var vm = angular.extend(this, {
            // members
            interventions: [],
            buttonId: '',
            textareaId: '',
            syncButtonDisabled: false,
            syncTextareaDisabled: false,
            textarea: '',
            settingEnabled: true,

            // methods
            initialize: initialize,
            getInterventions: getInterventions,
            setCharCountPTG: setCharCountPTG
        });

        function initialize(
            buttonId,
            textareaId,
            textareaValue,
            settingEnabled
        ) {
            vm.buttonId = '#'+buttonId;
            vm.textareaId = '#'+textareaId;
            vm.textarea = textareaValue;
            vm.settingEnabled = settingEnabled;
            
        }
        
        function getInterventions(clinicKey, clinicBranchKey, episodeKey) {
            vm.syncButtonDisabled = true;
            vm.syncTextareaDisabled = true;

            Ptg.getInterventionsByEpisodeKey(clinicKey, clinicBranchKey, episodeKey)
            .then(function(interventions) {
                
                for(var i=0;i<interventions.length;i++) {
                    var interventionsDisc = interventions[i];
                    if (interventionsDisc.auditItems.length>0) {
                        var output = "\n"+interventionsDisc.discipline+" Interventions\n";
                        for(var j=0;j<interventionsDisc.auditItems.length;j++) {
                            output = output+interventionsDisc.auditItems[j].instruction+"\n"
                        }
                        vm.textarea = vm.textarea + output;
                        setCharCountPTG($(vm.textareaId));
                    }
                }
                vm.syncButtonDisabled = false;
                vm.syncTextareaDisabled = false;

                setTimeout(function() {
                    $(vm.textareaId).focus();
                }, 0);
            });
        }
        
        function setCharCountPTG(element) {
            // set count remaining
            var remainingSpace = element.prop('maxLength') - vm.textarea.length;
            if (remainingSpace<0) {
                remainingSpace = 0;
            }
            $('#'+element.prop('id')+'CharCount').text(remainingSpace);

            // change text to red if max chars reached
            if(vm.textarea.length >= element.prop('maxLength')){
                $('#'+element.prop('id')+'CharCount').css('color', 'red');
                $('#'+element.prop('id')+'CharCountText').css('color', 'red');
                
                vm.textarea = vm.textarea.substring(0, element.prop('maxLength'));
                
            } else {
                $('#'+element.prop('id')+'CharCount').css('color', 'silver');
                $('#'+element.prop('id')+'CharCountText').css('color', 'silver');
            }

            // pluralize
            if(vm.textarea.length == (element.prop('maxLength') - 1)){
                $('#'+element.prop('id')+'CharCountText').text('Character Remaining');
            } else {
                $('#'+element.prop('id')+'CharCountText').text('Characters Remaining');
            }
        };
        
    }
})();

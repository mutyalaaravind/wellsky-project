(function() {
    'use strict';

    angular
        .module('directives.kinnser.oss-modal.oss-modal-confirmation-controller', [])
        .controller('OSSModalConfirmationController', controller)
        .constant('OSSModalConfirmationControllerConstants', {
            message: 'Pressing this will delete the frequency for this patient. Are you sure you wish to proceed?'
        });

    controller.$inject = ['$scope', 'dialog', 'OSSModalConfirmationControllerConstants'];

    function controller($scope, $dialog, CONSTANTS) {
        angular.extend($scope, {
            // members
            CONSTANTS: CONSTANTS,

            // methods
            onAcceptClick: onAcceptClick,
            onCancelClick: onCancelClick
        });

        function onAcceptClick() {
            $dialog.close(true);
        }

        function onCancelClick() {
            $dialog.close(false);
        }
    }
}) ();

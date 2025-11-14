(function() {
    'use strict';

    angular
        .module('services.ptg.instruction-preview', [])
        .service('InstructionPreviewService', service);

    function service() {
        var service = angular.extend(this, {
            getInstructionArray: getInstructionArray,
            sanitizeInstruction: sanitizeInstruction,
            convertInstruction: convertInstruction,
            convertInstructionToText: convertInstructionToText
        });

        var privates = {
            defaultSeparator: ' ',
            tagsSplitter: /<(ktext( value=('|")(.|\n)*?('|"))?|klabel)>(.|\n)*?<\/(ktext|klabel)>/g,
            tags: [
                {
                    regex: /<\/?klabel>/g,
                    replacement: ''
                },
                {
                    regex: /<ktext value=['"](.*?)['"]>.*?<\/ktext>/g,
                    replacement: '$1'
                },
                {
                    regex: /<\/?ktext>/g,
                    replacement: ''
                }
            ]
        };

        function getInstructionArray(instruction) {
            var result;
            if (angular.isString(instruction)) {
                result = instruction.match(privates.tagsSplitter);
            }

            return result;
        }

        function sanitizeInstruction(instruction, separator) {
            var i;
            var instructionArray;
            var result = instruction;
            var newSeparator = angular.isDefined(separator) ? separator : privates.defaultSeparator;

            if (angular.isDefined(result)) {
                instructionArray = service.getInstructionArray(result);

                if (instructionArray) {
                    result = [];

                    instructionArray.forEach(function(str) {
                        for (i = 0; i < privates.tags.length; i++) {
                            if (privates.tags[i].regex.test(str)) {
                                result.push(str.replace(privates.tags[i].regex, privates.tags[i].replacement));

                                break;
                            }
                        }
                    });

                    result = result.join(newSeparator);
                }
            }

            return result;
        }
        
        function convertInstruction(instructions, inputsDisabled) {
            var result = [];
            if (angular.isDefined(instructions)) {
                var instructionArray = getInstructionArray(instructions);

                if (instructionArray!=null) {
                    instructionArray.forEach(function(element, index) {
                        if (element.indexOf('<ktext') !== -1) {
                            var re = /(value=('|")(.|\n)*?('|")>)/g;
                            var valueTag = element.match(re);
                            var value = '';
                            if (valueTag!=null) {
                                value = valueTag[0].replace(/value=('|")/g,'');
                                value = value.replace(/('|")>/g,'');
                            }
                            var name =  element.replace(re,'');
                            name = name.replace('<ktext>','');
                            name = name.replace('</ktext>','');
                            result.push({label: name, type: '<ktext>', disabled: inputsDisabled, value: value.trim()});
                        }
                        if (element.indexOf('<klabel>') !== -1) {
                            var name = element.replace('<klabel>','');
                            name = name.replace('</klabel>','');
                            result.push({label: name, type: '<klabel>', disabled: inputsDisabled});
                        }
                    });
                }
            }

            return result;
        }
        
        function convertInstructionToText(instructionText) {
            var instructionArray = convertInstruction(instructionText, true);
            var newInstruction = "";
            for (var i = 0;i<instructionArray.length;i++) {
                if (instructionArray[i].type=='<klabel>') {
                    newInstruction += instructionArray[i].label+" ";
                }
                else {
                    newInstruction += instructionArray[i].value+" ";
                }
            }
            return newInstruction;
        }
        
    }
}) ();

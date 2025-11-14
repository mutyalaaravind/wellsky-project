'use strict';
var D0150SkipPattern = D0150SkipPattern || (function() {
    return {
        /**
         * Create initial state for D0150
         * @param {(id: string) => string} getValueText 
         * @returns {Map<string, string>} - A map of Ids in D0150 to value objects
         */
        createState: (getValueText) => {
            return 'ABCDEFGHI'
                .split('')
                .reduce((m, v) => {
                    const [one, two] = [ '1', '2'].map(suffix => `D0150${v}${suffix}`);
                    m.set(one, getValueText(one));
                    m.set(two, getValueText(two));
                    return m;
                }, new Map());
        },
        
        /**
         * Apply a (large) set of rules on the current state to generate the new state
         * @param {Map<string, (string|boolean)>} currentState - The current state
         * @returns {Map<string, (string|boolean)>} - The new, updated state
         */
        updateState: (currentState) => {
            const newState = D0150SkipPattern.deepCopyState(currentState);
            /**
             * If the value of id equals ifValue, then set the value of dependantId to dependantValue
             * @param {string} id 
             * @param {string | boolean} ifValue 
             * @param {string} dependantId 
             * @param {string} dependantValue 
             */
            const setIfValue = (id, ifValue, dependantId, dependantValue) => {
                if (newState.get(id) == ifValue) {
                    newState.set(dependantId, dependantValue);
                }
            };

            /**
             * If the value of id is in ifValueSet then set the values of dependantIds to dependantValue
             * @param {Array<string>} ids
             * @param {Set<string>} ifValueSet 
             * @param {Array<string>} dependantIds 
             * @param {string} dependantValue 
             */
            const setIfValues = (ids, ifValueSet, dependantIds, dependantValue) => {
                if (ids.every(i => ifValueSet.has(newState.get(i)))) {
                    dependantIds.forEach(i => newState.set(i, dependantValue));
                }
            };

            const aThroughI = 'ABCDEFGHI'.split('');
            const cThroughI = 'CDEFGHI'.split('');
            const nineNoneOrDash = new Set('9-^'.split(''));
            const onesIds = cThroughI.map(v => `D0150${v}1`);
            const zeroOrOne = new Set('01'.split(''));

            // -5900 	Consistency 	Fatal 	
            //  (a) If D0150A2 = [0,1] and D0150B2 = [0,1], then the following active items must equal [^]: D0150C1, D0150D1, D0150E1, D0150F1, D0150G1, D0150H1, D0150I1.
            //	(b) If D0150A1 = [-] or D0150B1 = [-], then the following active items must not equal [^]: D0150C1, D0150D1, D0150E1, D0150F1, D0150G1, D0150H1, D0150I1.
            //  (c) If D0150A1 = [9] and D0150B1 = [9], then the following active items must equal [^]: D0150C1, D0150D1, D0150E1, D0150F1, D0150G1, D0150H1, D0150I1.
            //  (d) If (D0150A2 = [^] and D0150B2 = [0,1]) OR (D0150A2 = [0,1] and D0150B2 = [^]), then the following active items must not equal [^]: D0150C1, D0150D1, D0150E1, D0150F1, D0150G1, D0150H1, D0150I1.
            //  (e) If D0150A2 = [2,3] or D0150B2 = [2,3], then the following active items must not equal [^]: D0150C1, D0150D1, D0150E1, D0150F1, D0150G1, D0150H1, D0150I1.
            setIfValues(['D0150A2', 'D0150B2'], zeroOrOne, onesIds, '^');
            setIfValues(['D0150A1', 'D0150B1'], new Set(['9']), onesIds, '^');
            // This appears in HCL-11322 but not in the specs
            setIfValues(['D0150A1', 'D0150B1'], new Set(['-']), onesIds, '-');
            setIfValues(['D0150A1', 'D0150B1'], new Set(['^']), onesIds, '^');
            setIfValues(['D0150A1', 'D0150B1'], new Set(['0']), onesIds, '^');

            // -5810 	Consistency 	Fatal 	
            // (a) If D0150A1=[0], then D0150A2 must equal [0].
            // (b) If D0150A1=[1], then D0150A2 must equal [0,1,2,3].
            // (c) If D0150A1=[9,-], then D0150A2 must equal [^].
            setIfValue('D0150A1', '0', 'D0150A2', '0');
            setIfValue('D0150A1', '9', 'D0150A2', '^');
            setIfValue('D0150A1', '-', 'D0150A2', '^');
            setIfValue('D0150A1', '^', 'D0150A2', '^');

            // -5820 	Consistency 	Fatal 	
            // (a) If D0150B1=[0], then D0150B2 must equal [0].
            // (b) If D0150B1=[1], then D0150B2 must equal [0,1,2,3].
            // (c) If D0150B1=[9,-], then D0150B2 must equal [^].
            setIfValue('D0150B1', '0', 'D0150B2', '0');
            setIfValue('D0150B1', '9', 'D0150B2', '^');
            setIfValue('D0150B1', '-', 'D0150B2', '^');
            setIfValue('D0150A1', '^', 'D0150A2', '^');

            // -5830 	Consistency 	Fatal 	
            // (a) If D0150C1=[0], then D0150C2 must equal [0].
            // (b) If D0150C1=[1], then D0150C2 must equal [0,1,2,3].
            // (c) If D0150C1=[9,^,-], then D0150C2 must equal [^].
            // D0150x1 (where x in 'C..I')
            cThroughI.forEach(v => {
                const [oneId, twoId] = [`D0150${v}1`, `D0150${v}2`];
                setIfValue(oneId, '0', twoId, '0');
                setIfValues([oneId], nineNoneOrDash, [twoId], '^');
            });

            // -5910 	Consistency 	Fatal 	Total Severity Score Calculation:
            // (a) If D0150A1 = [9] and D0150B1 = [9], then D0160 must equal [^].
            // (b) If D0150A2 = [0,1] and D0150B2 = [0,1], then D0160 must equal the sum of the values from D0150A2 and D0150B2.
            // Otherwise, the PHQ-9 must be completed, and D0160 must equal the sum of the values of the following nine items: D0150A2, D0150B2, D0150C2, D0150D2, D0150E2, D0150F2, D0150G2, D0150H2, D0150I2 and Format Integer Items to nearest integer. These are referred to as the "items in Column 2", below.
            // The following rules explain how to compute the score that is placed in item D0160. These rules consider the "number of missing items in Column 2" which is the number of items in Column 2 that are skipped.
            // (c) If the following items D0150A2, D0150B2, D0150C2, D0150D2, D0150E2, D0150F2, D0150G2, D0150H2, D0150I2 equal [0,1,2,3], then D0160 must equal the sum of these items.
            // (d) If one of the following items: D0150A2, D0150B2, D0150C2, D0150D2, D0150E2, D0150F2, D0150G2, D0150H2, D0150I2 = [^], then D0160 must equal the sum of the remaining items times 9/8(1.125), rounded to the nearest integer.
            // (e) If two of the following items: D0150A2, D0150B2, D0150C2, D0150D2, D0150E2, D0150F2, D0150G2, D0150H2, D0150I2 = [^], then D0160 must equal the sum of the remaining items times 9/7(1.286), rounded to the nearest integer.
            // (f) If three or more items between D0150A2, D0150B2, D0150C2, D0150D2, D0150E2, D0150F2, D0150G2, D0150H2 and D0150I2 = [^], then D0160 must equal [99].
            if ((newState.get('D0150A1') === '9' && newState.get('D0150B1') === '9') || (newState.get('D0150A1') === '^' && newState.get('D0150B1') === '^')) {
                newState.set('D0160', '^');
            } else if (newState.get('D0150A1') === '0' && newState.get('D0150B1') === '0') {
                newState.set('D0160', '00');
            } else if (zeroOrOne.has(newState.get('D0150A2')) && zeroOrOne.has(newState.get('D0150B2'))) {
                const d0160Value = ['D0150A2', 'D0150B2'].reduce((acc, x) => acc + parseInt(newState.get(x)), 0);
                const d0160Text = d0160Value < 10 ? '0' + d0160Value : '' + d0160Value;
                newState.set('D0160', d0160Text);
            } else {
                const symptomFrequencyValues = aThroughI.map(v => newState.get(`D0150${v}2`));
                const dashOrNone = new Set('-^'.split(''));
                const countSkippedItems = symptomFrequencyValues.reduce((acc, x) => 
                    acc = dashOrNone.has(x) ? acc + 1 : acc
                    , 0);
                const sumItems = symptomFrequencyValues.reduce((acc, x) => {
                    const i = parseInt(x);
                    acc = x !== '-' && i ? acc + i : acc
                    return acc;
                }, 0);
                
                const d0160Value = D0150SkipPattern.calculateD0160Value(countSkippedItems, sumItems);
                const d0160Text = d0160Value < 10 ? '0' + d0160Value : '' + d0160Value;
                newState.set('D0160', d0160Text);
            }
            return newState;
        },
        /**
         * Calculate the D0160 value
         * @param {number} skippedItemsCount - the count of items that were skipped
         * @param {number} sumOfItems  - the sum of the items that were not skipped
         * @returns {number}
         */
        calculateD0160Value: (skippedItemsCount, sumOfItems) => {
            switch(skippedItemsCount) {
                case 0: return sumOfItems; 
                case 1: return Math.round(sumOfItems * 1.125);
                case 2: return Math.round(sumOfItems * 1.286);
                default: return 99;
            }
        },

        /**
         * Create a new copy of the state
         * @param {Map<string, (string|boolean)>} currentState 
         * @returns {Map<string, (string|boolean)>} - a copy of the state
         */
        deepCopyState: (currentState) => {
            const newState = new Map();
            for (const [key, value] of currentState.entries()) {
                newState.set(key, value);
            }
            return newState;
        },
    }
})();
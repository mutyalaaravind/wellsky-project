import {describe, expect, test} from '@jest/globals';
import {administrative_sample} from '../assets/hhh/adminstrative_sample';
import {form} from '../assets/lhc-forms/99131-5-hh';
import parse from '../helpers/hhLHCParser';

describe('testLhcHhMerge', () => {
    it('should parse', () => {
        const result = parse(form, administrative_sample);
        let resultNode:any = {};
        const getDesiredNode = (node: any) => {
            if (node.hostFieldId === "M0102_PHYSN_ORDRD_SOCROC_DT|spWritefrmDateOasis|0|isOasis"){
                resultNode = node;
            }
        }
        result.items.forEach((item: any) => {
            if(item.items != null) {
                item.items.forEach((itemChild: any) => {
                    getDesiredNode(itemChild);
                });
            } else{
                getDesiredNode(item);
            }
        });
        expect(resultNode).toBeDefined();
        expect(resultNode.value).toEqual("01/01/2024");
    });
});

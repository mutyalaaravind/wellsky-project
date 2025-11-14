const parse = (lhcForm: any, hhData:any)=> {
    const lhcSchema = lhcForm;
    getLhcSchemaMergedWithHhData(lhcSchema, hhData);
    return lhcSchema;
}

const getLhcSchemaMergedWithHhData = (lhcNode: any, hhData:any)=> {
    const result = {};
    if (lhcNode && lhcNode.items != null) {
        lhcNode.items.forEach((lhcNodeItem:any) => {
            //const lhcNodeItem = lhcNode[key];
            if (lhcNodeItem && lhcNodeItem.items != null){
                lhcNodeItem.items.forEach((item: any) => {
                    getLhcSchemaMergedWithHhData(item, hhData);
                });
            } else{
                getLhcSchemaMergedWithHhData(lhcNodeItem, hhData);
            }
        });
    } else if (lhcNode) {
        const fieldId = lhcNode?.hostFieldId !== undefined ?  lhcNode?.hostFieldId : lhcNode?.localQuestionCode;
        if (hhData[fieldId] != null) {
            lhcNode.value = hhData[fieldId];
        }
    }
    
    return result;
}

export default parse;
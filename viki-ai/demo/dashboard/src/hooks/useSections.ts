import {  useState } from "react";


export const useSections = () => { 

    
    const [existingSections, setExistingSections] = useState<Array<any>>([]);
    const [sectionTranscripts, setSectionTranscripts] = useState<Record<string,string>>({});

    const existingSectionsTemp:Array<string>=[];
    const sectionTranscriptsTemp:Record<string,string>={};

    const getSectionData = async (transactionId:string, sections: Array<any>, env:any) => {
        sections.forEach(async (section) => {
            try{
                const response = await fetch(`${env?.AUTOSCRIBE_WIDGET_API}/api/transactions/${transactionId}/sections/${section.id}`, {
                    method: 'GET',
                })
                const data = await response.json()
                if(data != null){
                    existingSectionsTemp.push(section);
                    let text="";
                    data.text_sentences.forEach((sentence:any)=>{text = text + sentence.text + '\n'; });
                    sectionTranscriptsTemp[section.id]=text;
                    setExistingSections([...existingSectionsTemp,section]);
                    setSectionTranscripts(sectionTranscriptsTemp);
                }
            } catch(e){
                console.log("useSections error",e);
            }
        });
        
    }

    return { getSectionData, existingSections, sectionTranscripts };
}
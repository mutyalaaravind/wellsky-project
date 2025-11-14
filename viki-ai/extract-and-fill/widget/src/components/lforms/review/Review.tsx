
import { useCallback, useEffect, useState } from "react"
import {ReviewProps} from "../../../types"
import { Box, Select, Input,Button } from "@chakra-ui/react"
import AnnotatedForm from "../../review/AnnotatedForm"
import AnnotatedFormV2 from "../../review/AnnotatedFormV2"
import {AnnotatedFormAdapter} from "../../review/AnnotatedForm"
import { Checkbox } from "@mediwareinc/wellsky-dls-react"

export const Review = (props: ReviewProps) => {

    //console.log('Annotated form schema:', props.template);
    const [adapter, setAdapter] = useState<AnnotatedFormAdapter | null>(null);

    const onExtractionCompleted = (extractedText:any) => {
        console.log("onExtractionCompleted", props.extractedText);
        adapter?.setFieldsValue(JSON.parse(props.extractedText|| "{}"),props.sectionId || "");
    }

    const onSelectAll = (e:any) => {
        console.log("onSelectAll", e.target.checked);
        adapter?.setCheckboxesValue(e.target.checked);
    }

    const onApply = (e:any) => {
        props.setApprovedFormFieldValues?.(adapter?.getFieldsValue({checkedOnly: true}));
    }

    useEffect(() => {
        if(props.extractedText){
            onExtractionCompleted(props.extractedText);
        }
        
    },[props.extractedText]);
   
    return <>
            <Box>
                <Button onClick={(e:any)=>{onApply(e)}}>Apply AI Recommendations</Button>
            </Box>
            <Box><br /></Box>
            <Box>
                <Checkbox onChange={(e:any)=>{onSelectAll(e)}}></Checkbox>Select All
            </Box>
            <Box><br /></Box>
            <Box>
                <AnnotatedForm
                    schema={props.template}
                    onFormReady={(annotatedFormAdapter: AnnotatedFormAdapter) => {
                        setAdapter(annotatedFormAdapter);
                    }} 
                    onInfoClick={(e:any)=>{props.onEvidenceRequestedEvent?.(e)}}
                    sectionId={props.sectionId}
                />
                {/*
                <AnnotatedFormV2
                    originalData={JSON.parse(props.extractedText || '{}')}
                    newData={JSON.parse(props.extractedText || '{}')}
                    onPreferenceChange={(data)=>{console.log("onPreferenceChange:", data)}}
                />
                */}

            </Box>
            
        </>

    // const onFieldUpdate = useCallback((fieldId:string) =>{
    //     console.log("onFieldUpdate", fieldId, (document.getElementById(fieldId) as Element).nodeValue);
    //
    //     props.onFormSaveEvent?.(props.template);
    // }, []);
    //
    // const Section = (props:{section:any, depth: number}) => {
    //     const {section, depth} = props;
    //     return (
    //         <>
    //             <Box w='100%' p={4} bg='gray'>{section.question}</Box>
    //             <Box w='100%' p={4} >{depth.toString()}`</Box>
    //             <Box>{section.answers}</Box>
    //             {
    //                 section?.items?.map((item:any) => {
    //                     console.log("item2",item);
    //                     return renderItem(item, depth+1);
    //                 })
    //             }
    //         </>
    //     )
    // }
    //
    // const Text = (text:any) => {
    //     return (
    //         <>
    //             <Box w='100%' p={4} bg='white'>{text.question}</Box>
    //             <Box><Input id={text.linkId} value={text.answers} /></Box>
    //             <Box><Button onClick={(e:any)=>{onFieldUpdate(text.linkId);}} >Update</Button></Box>
    //         </>
    //     )
    // }
    //
    // const ComboBox = (text:any) => {
    //     return (
    //         <>
    //             <Box w='100%' p={4} bg='white'>{text.question}</Box>
    //             <Box>
    //                 <Select placeholder="select a value">{
    //                         text?.answers?.map((answer:any)=>{
    //                             return <option>{answer.text}</option>
    //                         })
    //                     }
    //                 </Select>
    //             </Box>
    //         </>
    //     )
    // }
    //
    // const renderItem = (item:any, depth:number=0) => {  
    //
    //     if (item?.dataType==="SECTION"){
    //         return <Section section={item} depth={depth} />
    //     }
    //
    //     if (item?.dataType==="CNE"){
    //         return <ComboBox {...item} />
    //     }
    //
    //     if (item?.dataType==="REAL"){
    //         return <Text {...item} />
    //     }
    //
    //     return <Text {...item} />
    //  }
    //
    // return (
    //     <>
    //         <div>{props.template?.items?.map((item:any)=>renderItem(item))}</div>
    //     </>
    // )
}

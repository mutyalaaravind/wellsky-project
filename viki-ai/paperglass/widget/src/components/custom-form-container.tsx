import useEnvJson from "../hooks/useEnvJson";
import { Env } from "../types";
import CustomFormsComponent from "./custom-form";

type CustomFormsContainerComponentProps = {
    newData?: any;
    mount?: string;
    formInstanceId?: string;
    formTemplateId?: string;
    };

export const CustomFormContainer = (props:CustomFormsContainerComponentProps) => {
    const env = useEnvJson<Env>();
    return (
        <>
        {env && <CustomFormsComponent widgetHost={env?.FORMS_WIDGETS_HOST} env={env}  newData={props.newData}/>}
        </>
    )
}
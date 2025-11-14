
import { Badge, LinkButton, Popover, Select } from "@mediwareinc/wellsky-dls-react";
import { SettingOutlined } from "@ant-design/icons/lib/icons";
import {Switch} from 'antd';
import { Box, Grid, NumberDecrementStepper, NumberIncrementStepper, NumberInput, NumberInputField, NumberInputStepper, Text } from "@chakra-ui/react";
import React from "react";

type SettingsProps = {
    onRelevanceScoreChange:(score:number)=>void;
    onModelChange:(model:string)=>void;
}

export const Settings = (props:SettingsProps) => {
    const [relevanceScore, setRelevanceScore] = React.useState<number>(0.7);
    const [model, setModel] = React.useState<string>("medlm-medium");
    const [showEmbeddingStatus, setShowEmbeddingStatus] = React.useState<boolean>(false);
    
    return (
        <Box borderBottom="1px" borderColor="gray.200" paddingY={1}>
            <div style={{ float: 'right' }}>
            <Popover title="Settings" content={(
                <Box>
                <Box>
                    <Box>Relevance Score Threshold:</Box>
                    <Box>
                    <NumberInput
                    defaultValue={relevanceScore} min={0.4} max={1.0} precision={2} step={0.05}
                    onChange={(valueString) => { setRelevanceScore(parseFloat(valueString)); props.onRelevanceScoreChange(parseFloat(valueString)) }}
                    >
                    <NumberInputField />
                    <NumberInputStepper>
                        <NumberIncrementStepper />
                        <NumberDecrementStepper />
                    </NumberInputStepper>
                    </NumberInput>
                    </Box>
                </Box>
                <Box>
                    <Box>Select the Model:</Box>
                    <Box>
                    <Select onChange={(e: any) => { console.log("moddel changed", e); setModel(e.target.value); props.onModelChange(e.target.value); }} value={model}>
                        <option value="text-bison-32k@002">Text Bison 32 K</option>
                        <option value="medlm-medium">MedLM-Medium</option>
                        <option value="medlm-large">MedLM-Large</option>
                        <option value="gemini-pro">Gemini-Pro</option>
                    </Select>
                    </Box>
                </Box>
                <Box>
                    <Box>Show Embedding Status:</Box>
                    <Box>
                    <Switch checked={showEmbeddingStatus} onChange={(e) => { setShowEmbeddingStatus(e) }} />
                    </Box>
                </Box>
                </Box>
            )} trigger="click">
                <LinkButton><SettingOutlined /></LinkButton>
            </Popover>
            </div>
            <Text fontSize="lg" fontWeight="bold">
            Oasis-E Start of Care Assessment
            </Text>
        </Box>
    )

}
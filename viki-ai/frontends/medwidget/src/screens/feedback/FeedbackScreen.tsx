import { useState } from "react";

import { PrimaryButton } from "@mediwareinc/wellsky-dls-react";

import { Bubble } from "components/Bubble";

type AnswerType = {
  [key: number]: number;
};

export const FeedbackScreen = ({ onClose }: { onClose: () => void }) => {
  const steps = [
    {
      question: "On a scale of 1 to 7, how easy was it to complete the task?",
      options: [
        { score: 1, text: "Very difficult" },
        { score: 2, text: "Difficult" },
        { score: 3, text: "Somewhat difficult" },
        { score: 4, text: "Neutral" },
        { score: 5, text: "Somewhat easy" },
        { score: 6, text: "Easy" },
        { score: 7, text: "Very easy" },
      ],
    },
    {
      question:
        "On a scale of 1 to 5, how much support/assistance would you anticipate needing to effectively complete this task?",
      options: [
        { score: 1, text: "No help needed" },
        { score: 2, text: "Minimal help" },
        { score: 3, text: "Some help" },
        { score: 4, text: "Lots of help" },
        { score: 5, text: "Constant help" },
      ],
    },
  ];
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [answers, setAnswers] = useState<AnswerType>({});
  const currentStep = steps[currentStepIndex];
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        height: "100%",
        flex: "1 0 0",
        minHeight: "0",
        alignItems: "center",
        justifyContent: "center",
        gap: "2rem",
        padding: "1rem",
      }}
    >
      {currentStep.question}
      <div
        style={{
          display: "flex",
          flexDirection: "row",
          gap: "4rem",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        {currentStep.options.map((option) => (
          <Bubble
            key={option.score}
            score={option.score}
            text={option.text}
            selected={answers[currentStepIndex] === option.score}
            onClick={() => {
              setAnswers({ ...answers, [currentStepIndex]: option.score });
            }}
          />
        ))}
      </div>
      <PrimaryButton
        onClick={() => {
          if (currentStepIndex < steps.length - 1) {
            setCurrentStepIndex(currentStepIndex + 1);
          } else {
            onClose();
          }
        }}
      >
        {(currentStepIndex === steps.length - 1
          ? "Complete task survey"
          : "Continue to next question"
        ).toUpperCase()}
      </PrimaryButton>
    </div>
  );
};

// import { useStyles } from "hooks/useStyles";
import React from "react";

// import css from "./MagicSparkle.css";

export const MagicSparkle = ({
  fontSize = 20,
  animated = false,
  onClick = undefined,
  className = "",
}: {
  fontSize?: number;
  animated?: boolean;
  onClick?: () => void;
  className?: string;
}) => {
  const [isHovered, setIsHovered] = React.useState(false);
  return (
    <>
      <style>
        {`
          /* Pulsating animation */

          @keyframes magic-sparkle-big-pulse {
            0% {
              transform: scale(1);
              animation-timing-function: ease-out;
              opacity: 1;
            }

            25% {
              transform: scale(1.1);
              animation-timing-function: ease-in;
              opacity: 1;
            }

            50% {
              transform: scale(1);
              animation-timing-function: ease-out;
              opacity: 1;
            }

            75% {
              transform: scale(0.9);
              animation-timing-function: ease-in;
              opacity: 0.5;
            }

            100% {
              transform: scale(1);
              animation-timing-function: ease-out;
              opacity: 1;
            }
          }

          .magic-sparkle-big,
          .magic-sparkle-medium,
          .magic-sparkle-small {
            transform-origin: center;
          }

          .magic-sparkle-big.magic-sparkle-animated {
            animation: magic-sparkle-big-pulse 2s infinite;
          }

          .magic-sparkle-medium.magic-sparkle-animated {
            /* Same animation, but shifted by 1/3 the duration */
            animation: magic-sparkle-big-pulse 2s infinite 0.33s;
            transform-origin: center;
          }

          .magic-sparkle-small.magic-sparkle-animated {
            /* Same animation, but shifted by 2/3 the duration */
            animation: magic-sparkle-big-pulse 2s infinite 0.66s;
            transform-origin: center;
          }

          .magic-sparkle-big.magic-sparkle-hover {
            animation: magic-sparkle-big-pulse 0.8s infinite;
          }

          .magic-sparkle-medium.magic-sparkle-hover {
            /* Same animation, but shifted by 1/3 the duration */
            animation: magic-sparkle-big-pulse 0.8s infinite 0.27s;
            transform-origin: center;
          }

          .magic-sparkle-small.magic-sparkle-hover {
            /* Same animation, but shifted by 2/3 the duration */
            animation: magic-sparkle-big-pulse 0.8s infinite 0.53s;
            transform-origin: center;
          }

        `}
      </style>
      <svg
        width={fontSize}
        height={fontSize}
        viewBox="0 0 40 40"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        onClick={onClick}
        className={className}
      >
        <path
          fillRule="evenodd"
          clipRule="evenodd"
          d="M19.6826 11.4092C19.7891 11.1348 20.2118 11.1348 20.3184 11.4092C21.6883 14.9384 24.4443 17.8431 27.9697 19.5459L28.1758 20L27.9697 20.4541C24.4444 22.1567 21.6886 25.0621 20.3184 28.5908L20.2949 28.6396C20.1693 28.8497 19.8316 28.8498 19.7061 28.6396L19.6826 28.5908C18.3126 25.0629 15.5575 22.1587 12.0332 20.4561L11.6895 20.2949C11.443 20.1829 11.443 19.8181 11.6895 19.7061C15.3785 18.0289 18.2687 15.0516 19.6826 11.4092ZM20 15.1445C18.759 17.0517 17.1317 18.7006 15.2275 20C17.1315 21.2991 18.7589 22.9478 20 24.8545C21.2409 22.9478 22.8687 21.2992 24.7725 20C22.8685 18.7005 21.2408 17.0517 20 15.1445ZM28.3105 19.7061C28.557 19.8181 28.557 20.1829 28.3105 20.2949L27.9697 20.4541L28.1758 20L27.9697 19.5459C28.0826 19.6004 28.1961 19.654 28.3105 19.7061Z"
          fill="#97449C"
          className={`magic-sparkle-big ${isHovered ? "magic-sparkle-hover" : animated ? "magic-sparkle-animated" : ""}`}
        />
        <path
          fillRule="evenodd"
          clipRule="evenodd"
          d="M27.3268 8.94922C27.45 8.67724 27.9106 8.67722 28.0338 8.94922C28.7174 10.4602 29.8922 11.7072 31.358 12.4932C31.5919 12.6187 31.592 12.9819 31.358 13.1074L31.0865 13.2598C29.7472 14.0499 28.6748 15.2349 28.0338 16.6514L28.0065 16.6992C27.864 16.9071 27.4966 16.907 27.3541 16.6992L27.3268 16.6514C26.6858 15.2349 25.6134 14.0499 24.274 13.2598L24.0026 13.1074C23.7685 12.982 23.7686 12.6186 24.0026 12.4932C25.4684 11.7072 26.6432 10.4602 27.3268 8.94922ZM27.6793 11.2705C27.2536 11.8351 26.7641 12.3488 26.2194 12.7998C26.7641 13.2508 27.2535 13.7646 27.6793 14.3291C28.105 13.7646 28.5948 13.2508 29.1393 12.7998C28.5947 12.3487 28.1049 11.8351 27.6793 11.2705Z"
          fill="#97449C"
          className={`magic-sparkle-medium ${isHovered ? "magic-sparkle-hover" : animated ? "magic-sparkle-animated" : ""}`}
        />
        <path
          fillRule="evenodd"
          clipRule="evenodd"
          d="M14.0665 11.6006C14.1305 11.4665 14.3695 11.4665 14.4335 11.6006C14.7883 12.3459 15.3981 12.9609 16.1589 13.3486C16.2804 13.4105 16.2804 13.5897 16.1589 13.6516L16.018 13.7267C15.3228 14.1164 14.7662 14.7009 14.4335 15.3995L14.4193 15.4231C14.3454 15.5256 14.1547 15.5256 14.0807 15.4231L14.0665 15.3995C13.7338 14.7009 13.1772 14.1164 12.482 13.7267L12.3411 13.6516C12.2196 13.5897 12.2196 13.4105 12.3411 13.3486C13.1019 12.9609 13.7117 12.3459 14.0665 11.6006Z"
          fill="#97449C"
          className={`magic-sparkle-small ${isHovered ? "magic-sparkle-hover" : animated ? "magic-sparkle-animated" : ""}`}
        />
      </svg>
    </>
  );
};

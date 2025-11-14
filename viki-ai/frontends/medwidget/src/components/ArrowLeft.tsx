import { SVGProps } from "react";

function ArrowLeft(props: Partial<SVGProps<SVGElement>> & any) {
  return (
    <svg
      width="20"
      height="40"
      viewBox="0 0 20 40"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      {...props}
    >
      <mask
        id="mask0_1403_149866"
        style={{ maskType: "alpha" }}
        maskUnits="userSpaceOnUse"
        x="6"
        y="13"
        width="8"
        height="13"
      >
        <path
          d="M13.71 15.1209L9.11996 19.7109L13.71 24.3009L12.29 25.7109L6.28996 19.7109L12.29 13.7109L13.71 15.1209Z"
          fill="#9E9E9E"
        />
      </mask>
      <g mask="url(#mask0_1403_149866)">
        <rect width="20" height="40" fill="#3D5463" />
      </g>
    </svg>
  );
}

export default ArrowLeft;

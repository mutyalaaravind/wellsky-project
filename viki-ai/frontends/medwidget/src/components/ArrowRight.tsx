import { SVGProps } from "react";

function ArrowRight(props: Partial<SVGProps<SVGElement>> & any) {
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
        id="mask0_1403_148691"
        style={{ maskType: "alpha" }}
        maskUnits="userSpaceOnUse"
        x="6"
        y="13"
        width="8"
        height="13"
      >
        <path
          d="M6.29508 15.1151L10.8751 19.7051L6.29508 24.2951L7.70508 25.7051L13.7051 19.7051L7.70508 13.7051L6.29508 15.1151Z"
          fill="#9E9E9E"
        />
      </mask>
      <g mask="url(#mask0_1403_148691)">
        <rect width="20" height="40" fill="#3D5463" />
      </g>
    </svg>
  );
}

export default ArrowRight;

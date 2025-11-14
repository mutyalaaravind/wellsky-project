import React, { CSSProperties } from "react";

type BlockProps = {
  children: any;
  style?: CSSProperties;
  [key: string]: any;
};

export const Block = React.forwardRef(
  (
    { children, style = {} as CSSProperties, ...props }: BlockProps,
    ref: any,
  ) => {
    return (
      <div
        style={{
          display: "flex",
          flex: "1 1 0",
          flexDirection: "column",
          borderRadius: "4px",
          overflow: "auto",
          boxShadow: "0 2px 4px rgba(0, 0, 0, 0.5)",
          ...style,
        }}
        {...props}
        ref={ref}
      >
        {children}
      </div>
    );
  },
);

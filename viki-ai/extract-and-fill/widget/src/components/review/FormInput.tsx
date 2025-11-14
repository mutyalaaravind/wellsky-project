import React, { ReactElement, ReactNode } from "react";
import { Form, Input, FormItemProps } from "antd";

interface FormInputProps extends FormItemProps {
  value?: any;
  onChange?: any;
  label?: string | ReactElement;
  rules?: Array<any>;
  required?: boolean;
  tooltip?: string | ReactElement;
  placeholder?: string;
  children?: ReactNode | ReactElement;
  isDumb?: boolean;
}

function FormInput({
  name,
  label,
  rules,
  required,
  tooltip,
  placeholder,
  children,
  isDumb = false,
  ...rest
}: FormInputProps) {
  if (isDumb) {
    return (
      <div
        className="ant-row ant-form-item"
        style={{ ...rest.style, rowGap: 0 }}
      >
        <div className="ant-col ant-form-item-label">
          <label className="ant-form-item-required" title={label?.toString()}>
            {label}
          </label>
        </div>
        <div className="ant-col ant-form-item-control">
          <div className="ant-form-item-control-input">
            <div className="ant-form-item-control-input-content">
              {children || (
                <Input
                  placeholder={placeholder}
                  value={rest?.value}
                  onChange={rest.onChange}
                />
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }
  const clonedChildren = React.Children.map(children as any, (child) => {
    return React.cloneElement(child, {
      ...(child?.props as any),
      label,
    });
  })
  return (
    <Form.Item
      name={name}
      label={label}
      rules={rules}
      required={required}
      tooltip={tooltip}
      {...rest}
      noStyle
    >
      {clonedChildren || <Input placeholder={placeholder} />}
    </Form.Item>
  );
}

export default FormInput;

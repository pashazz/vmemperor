import {FormFeedback, InputProps} from "reactstrap";
import {FieldProps} from "formik";
import {FormGroup} from "../MarginFormGroup";
import * as React from "react";
import Input from "reactstrap/lib/Input";
import Label from "reactstrap/lib/Label";
import styled from "styled-components";

interface InputComponentProps {
  label: string,
}

const MarginedLabel = styled(Label)`
margin-left: 1.25rem
`;
const CheckBoxComponent: React.FunctionComponent<FieldProps & InputProps & InputComponentProps> = (
  {
    field: {...fields},
    form,
    children,
    ...props
  }
) => {
  return (
    <FormGroup check={true}

    >
      <MarginedLabel check>
        <Input {...props} {...fields}
               type="checkbox"
               invalid={Boolean(form.touched[fields.name]
                 && form.errors[fields.name])}
        />
        {children}
      </MarginedLabel>
      {form.touched[fields.name] && form.errors[fields.name] &&
      (<FormFeedback> {form.errors[fields.name]} </FormFeedback>)}
    </FormGroup>
  )
};

export default CheckBoxComponent;

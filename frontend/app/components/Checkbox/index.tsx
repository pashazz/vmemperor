import {FormFeedback, InputProps} from "reactstrap";
import {FieldProps} from "formik";
import FormGroup from "reactstrap/lib/FormGroup";
import * as React from "react";
import Input from "reactstrap/lib/Input";
import Label from "reactstrap/lib/Label";
interface InputComponentProps {
  label: string,
}

const CheckBoxComponent : React.FunctionComponent<FieldProps & InputProps &  InputComponentProps> = (
  {
    field: {...fields},
    form,
    children,
    ...props
  }
) =>
{
  return (
    <FormGroup check={true}

    >
      <Label check>
        <Input {...props} {...fields}
               type="checkbox"
               invalid={Boolean(form.touched[fields.name]
                 && form.errors[fields.name])}
        />
        {children}
      </Label>
        { form.touched[fields.name] && form.errors[fields.name] &&
        (<FormFeedback> {form.errors[fields.name]} </FormFeedback>)}
    </FormGroup>
  )
};

export default CheckBoxComponent;

import { FieldProps } from 'formik'
import React from 'react'
import Select, { Option, ReactSelectProps } from 'react-select'
import {FormFeedback, InputGroup, InputGroupAddon} from "reactstrap";
import FormGroup from "reactstrap/lib/FormGroup";



/* See bug https://github.com/JedWatson/react-select/issues/1453
 and https://github.com/JedWatson/react-select/issues/2930 */
const SelectField: React.FunctionComponent<ReactSelectProps & FieldProps> = ({
  options,
  field,
  form,
  placeholder
}) => (
  <FormGroup>
  <div style={{ margin: '1rem 0' }}>
  <Select
    options={options}
    name={field.name}
    value={options ? options.find(option => option.value === field.value) : ''}
    onChange={(option: Option) => form.setFieldValue(field.name, option)}
    onBlur={field.onBlur}
    placeholder={placeholder}
  />

    {!!form.errors[field.name] && form.touched[field.name] && (
      <FormFeedback>
        {form.errors[field.name]}
      </FormFeedback>
    )
    }
  </div>
  </FormGroup>
);

export default SelectField;

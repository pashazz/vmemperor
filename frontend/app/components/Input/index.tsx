/**
 *
 * Input
 *
 */

import React, {HTMLAttributes} from 'react';
// import styled from 'styled-components';

import AutoInput from './autoInput';
/*
class Input extends React.Component { // eslint-disable-line react/prefer-stateless-function
  render() {
    return (
      <AvInput
        tag={AutoInput}
        {...this.props} />
    );
  }

}
*/
import {FieldProps} from "formik";
import {FormFeedback, FormGroup, Input, InputGroupText} from 'reactstrap';
import {Icon} from "@fortawesome/fontawesome-svg-core";
import InputGroup from "reactstrap/lib/InputGroup";
import InputGroupAddon from "reactstrap/lib/InputGroupAddon";
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import {InputProps} from "reactstrap";

interface InputComponentProps {
  addonIcon : Icon
};

const InputComponent : React.FunctionComponent<FieldProps & InputProps &  InputComponentProps> = (
  {
    field: {...fields},
    form,
    addonIcon,
    ...props
  }
) =>
{
  return (
    <FormGroup>
      <InputGroup>
        <InputGroupAddon style={ {"line-height": "1!important"}} addonType="prepend">
          <InputGroupText style = { { height: '100%'}}>
            <FontAwesomeIcon icon={addonIcon}/>
          </InputGroupText>
        </InputGroupAddon>
        <Input {...props} {...fields}
               invalid={Boolean(form.touched[fields.name]
                 && form.errors[fields.name])}
        />
        { form.touched[fields.name] && form.errors[fields.name] &&
        (<FormFeedback> {form.errors[fields.name]} </FormFeedback>)}
      </InputGroup>
    </FormGroup>
  )
};

export default InputComponent;

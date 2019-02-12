/**
 *
 * Input
 *
 */

import React, {HTMLAttributes} from 'react';
// import styled from 'styled-components';

import AutoInput from './autoInput';
import { AvInput } from 'availity-reactstrap-validation';
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
import {Input} from 'reactstrap';
import {Icon} from "@fortawesome/fontawesome-svg-core";

interface InputComponentProps {
  addonIcon : Icon
};

const InputComponent : React.FunctionComponent<FieldProps & React.HTMLProps<HTMLInputElement>> = (
  {
    field,
    form,
  }, props : React.HTMLProps<HTMLInputElement>
) =>
{
  return (
    <InputGroup>
  <Input>

  </Input>
    </InputGroup>
      );
}

export default Input;

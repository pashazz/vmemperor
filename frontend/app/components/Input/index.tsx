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
import {Col, FormFeedback, FormGroup, Input, InputGroupText, Label} from 'reactstrap';
import {Icon} from "@fortawesome/fontawesome-svg-core";
import InputGroup from "reactstrap/lib/InputGroup";
import InputGroupAddon from "reactstrap/lib/InputGroupAddon";
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import {InputProps} from "reactstrap";

interface InputComponentProps {
  addonIcon? : Icon,
  label? : boolean, //Use children to provide label text

};

const InputComponent : React.FunctionComponent<FieldProps & InputProps &  InputComponentProps> = (
  {
    field: {...fields},
    form,
    addonIcon,
    label,
    children,
    ...props
  }
) =>
{
  return (
    <FormGroup row={true} style={{paddingLeft: 20, paddingRight: 20}}>
      {label && (
        <Label for={fields.name} style={ { marginTop: "0.5rem"}}>
          {children}
        </Label>
      )
      }


      <Col>
      <InputGroup row={true}>
        { addonIcon && (
        <InputGroupAddon style={ {"line-height": "1!important"}} addonType="prepend">
          <InputGroupText>
            <FontAwesomeIcon icon={addonIcon}/>
          </InputGroupText>
        </InputGroupAddon>
        )
        }
        <Input {...props} {...fields}
               invalid={Boolean(form.touched[fields.name]
                 && form.errors[fields.name])}
        />
        { form.touched[fields.name] && form.errors[fields.name] &&
        (<FormFeedback> {form.errors[fields.name]} </FormFeedback>)}
      </InputGroup>
      </Col>
    </FormGroup>
  )
};

export default InputComponent;

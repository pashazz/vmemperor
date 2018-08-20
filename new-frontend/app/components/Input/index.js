/**
 *
 * Input
 *
 */

import React from 'react';
// import styled from 'styled-components';

import AutoInput from './autoInput';
import { AvInput } from 'availity-reactstrap-validation';

class Input extends React.Component { // eslint-disable-line react/prefer-stateless-function
  render() {
    return (
      <AvInput
        tag={AutoInput}
        {...this.props} />
    );
  }

}

export default Input;

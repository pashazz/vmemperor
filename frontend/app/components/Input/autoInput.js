/**
 *
 * Input
 *
 */

import React from 'react';
// import styled from 'styled-components';

import {Input as ReactstrapInput } from 'reactstrap';
import   "./styles.css";
import classNames from 'classnames';
class Input extends React.Component { // eslint-disable-line react/prefer-stateless-function
  constructor(props) {
    super(props);

  }

  render() {
    return (
      <ReactstrapInput
        innerRef={(ref) => { this.inputRef = ref;}}
                 {...this.props} />

    );
  }
  componentDidMount() {
    this.inputRef.addEventListener('change', this.onChange);
  }

  onChange = (event) => {
    // React actually uses the input even for onChange, this causes autofill to
    // break in iOS Chrome as it only fires a change event.
    if (this.props.onChange) {
      this.props.onChange(event);
    }
  };

  componentWillUnmount() {
    this.inputRef.removeEventListener('change', this.onChange);
  }
}

export default Input;

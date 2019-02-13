/**
*
* SinglePoolLogin
*
*/

import React from 'react';
import styled from 'styled-components';
import {InputGroup, InputGroupAddon, InputGroupText, Form, FormGroup, Label, Input} from 'reactstrap';
import { AvGroup, AvFeedback } from 'availity-reactstrap-validation';
import T from 'prop-types';
import { injectIntl, intlShape } from 'react-intl';
import messages from './messages';

const MarginedInputGroup = styled(InputGroup)`
margin-bottom:10px
`;

class SinglePoolLogin extends React.PureComponent { // eslint-disable-line react/prefer-stateless-function
  render()
  {
    const { description } = this.props;
    const { formatMessage } = this.props.intl;
    return (
      <AvGroup>
        <InputGroup id="pool1">
          <InputGroupAddon addonType="prepend">Test</InputGroupAddon>
          <Input type="text" name="login" required id="singlePoolLogin" placeholder={formatMessage(messages.loginPlaceholder)} />
          <Input type="password" name="password" required id="singlePoolPassword" placeholder={formatMessage(messages.passwordPlaceholder)} />
          <AvFeedback>Enter credentials</AvFeedback>
          </InputGroup>

      </AvGroup>
    );
  }
}


export default injectIntl(SinglePoolLogin);

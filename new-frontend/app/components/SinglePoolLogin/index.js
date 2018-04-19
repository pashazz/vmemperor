/**
*
* SinglePoolLogin
*
*/

import React from 'react';
import styled from 'styled-components';
import {Input, InputGroup, InputGroupAddon, InputGroupText, Form, FormGroup, Label} from 'reactstrap';

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
        <InputGroup id="pool1">
          <InputGroupAddon addonType="prepend">Test</InputGroupAddon>
          <Input type="text" name="login" id="singlePoolLogin" placeholder={formatMessage(messages.loginPlaceholder)} />
          <Input type="password" name="password" id="singlePoolPassword" placeholder={formatMessage(messages.passwordPlaceholder)} />
          </InputGroup>
    );
  }
}

SinglePoolLogin.propTypes = {
  description: T.string.isRequired,
  intl: intlShape.isRequired,
  index: T.number.isRequired,

};

export default injectIntl(SinglePoolLogin);

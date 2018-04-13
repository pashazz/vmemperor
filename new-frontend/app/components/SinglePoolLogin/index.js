/**
*
* SinglePoolLogin
*
*/

import React from 'react';
// import styled from 'styled-components';
import {Input, InputGroup, InputGroupAddon, InputGroupText, Form, FormGroup} from 'reactstrap';

import T from 'prop-types';
import { injectIntl, intlShape } from 'react-intl';
import messages from './messages';


class SinglePoolLogin extends React.PureComponent { // eslint-disable-line react/prefer-stateless-function
  render()
  {
    const { description } = this.props;
    const { formatMessage } = this.props.intl;
    return (
      <Form inline>
        <InputGroup>
          <InputGroupAddon addonType="prepend">{description}</InputGroupAddon>
          <Input type="text" name="login" id="singlePoolLogin" placeholder={formatMessage(messages.loginPlaceholder)} />
          <Input type="password" name="password" id="singlePoolPassword" placeholder={formatMessage(messages.passwordPlaceholder)} />
        </InputGroup>
      </Form>
    );
  }
}

SinglePoolLogin.propTypes = {
  description: T.string.isRequired,
  intl: intlShape.isRequired,
  index: T.number.isRequired,

};

export default injectIntl(SinglePoolLogin);

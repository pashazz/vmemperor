/**
 *
 * LoginPage
 *
 */

import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { FormattedMessage } from 'react-intl';
import { createStructuredSelector } from 'reselect';
import { compose } from 'redux';
import { Button, Modal, ModalHeader, ModalBody, ModalFooter, Form } from 'reactstrap';


import injectSaga from 'utils/injectSaga';
import injectReducer from 'utils/injectReducer';
import makeSelectLoginPage from './selectors';
import reducer from './reducer';
import saga from './saga';
import messages from './messages';

export class LoginPage extends React.PureComponent { // eslint-disable-line react/prefer-stateless-function

  constructor() {
    super();
    this.handleSubmit = this.handleSubmit.bind(this);
    this.handleChange = this.handleChange.bind(this);
    this.state = {
      login: {},
    };
  }

  handleSubmit(e) {
    e.preventDefault();
    this.props.auth(this.state.login);
  }

  handleChange(e) {
    const loginState = this.state.login;
    loginState[e.target.name] = e.target.value;
    this.setState({ login: loginState });
  }

  render() {
    return (
      <Modal isOpen>
        <ModalHeader> VM Emperor Login </ModalHeader>
        <Form role="form" onChange={this.handleChange} onSubmit={this.handleSubmit}>
          <ModalBody>
            {
              this.props.pools.map((pool, index) =>
                <SinglePoolLogin key={pool.id} description={pool.description} index={index} />)
            }
          </ModalBody>
          <ModalFooter>
            {
              this.props.pools.length > 0 ?
                <button type="submit" className="btn btn-lg btn-primary btn-block">Login</button> :
                <h4>
                  <FormattedMessage {...messages.noPools} />
                </h4>
            }
          </ModalFooter>
        </Form>
      </Modal>
    );
  }
}

LoginPage.propTypes = {
  dispatch: PropTypes.func.isRequired,
  auth: PropTypes.func.isRequired,
};

const mapStateToProps = createStructuredSelector({
  loginpage: makeSelectLoginPage(),
});

function mapDispatchToProps(dispatch) {
  return {
    dispatch,
  };
}

const withConnect = connect(mapStateToProps, mapDispatchToProps);

const withReducer = injectReducer({ key: 'loginPage', reducer });
const withSaga = injectSaga({ key: 'loginPage', saga });

export default compose(
  withReducer,
  withSaga,
  withConnect,
)(LoginPage);

/*
 *
 * LoginPage
 *
 */

import React, { PropTypes as T } from 'react';
import { connect } from 'react-redux';
import selectLoginPage from './selectors';
import { FormattedMessage } from 'react-intl';
import messages from './messages';

import { auth } from 'containers/App/actions';
import Modal from 'components/Modal';
import SinglePoolLogin from 'components/SinglePoolLogin';

export class LoginPage extends React.Component {
  static propTypes = {
    pools: T.array.isRequired,
    auth: T.func.isRequired,
  };

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
      <Modal title="VM Emperor Login">
        <form role="form" onChange={this.handleChange} onSubmit={this.handleSubmit}>
          <div className="modal-body">
            {
              this.props.pools.map((pool, index) =>
                <SinglePoolLogin key={pool.id} description={pool.description} index={index} />)
            }
          </div>
          <div className="modal-footer">
            {
              this.props.pools.length > 0 ?
                <button type="submit" className="btn btn-lg btn-primary btn-block">Login</button> :
                <h4>
                  <FormattedMessage {...messages.noPools} />
                </h4>
            }
          </div>
        </form>
      </Modal>
    );
  }
}

const mapStateToProps = selectLoginPage();

const mapDispatchToProps = {
  auth,
};

export default connect(mapStateToProps, mapDispatchToProps)(LoginPage);

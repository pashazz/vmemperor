/**
 *
 * Logout
 *
 */

import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { injectIntl, FormattedMessage, intlShape } from 'react-intl';
import { compose } from 'redux';
import { Modal, ModalBody, ModalHeader, ModalFooter, Button } from 'reactstrap';
import { withRouter } from 'react-router-dom';
import messages from './messages';


import { logout } from "../App/actions";

class Logout extends React.Component{

  render()
  {
    console.log('in logout');
    return(

        <Modal isOpen>
          <ModalHeader><FormattedMessage {...messages.header} /></ModalHeader>
          <ModalBody>
           <FormattedMessage {...messages.body}/>
          </ModalBody>
          <ModalFooter>
            <Button color="primary" onClick={this.props.logout}>
              <FormattedMessage {...messages.ok}/>
            </Button>
            <Button color="secondary" onClick={this.props.history.goBack}>
              <FormattedMessage {...messages.cancel}/>
            </Button>
          </ModalFooter>
        </Modal>

    );
  }

}


Logout.propTypes = {
  intl: intlShape.isRequired,
  logout: PropTypes.func.isRequired,
  history: PropTypes.object.isRequired
};

const mapDispatchToProps = {
  logout,
};
const withConnect = connect(null, mapDispatchToProps);

export default compose(
  withRouter,
  withConnect,
  injectIntl,
)(Logout);

/**
 *
 * NetworkController
 *
 */

import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { FormattedMessage } from 'react-intl';
import { createStructuredSelector } from 'reselect';
import { compose } from 'redux';

import injectSaga from 'utils/injectSaga';
import injectReducer from 'utils/injectReducer';
import makeSelectNetworkController from './selectors';
import reducer from './reducer';
import saga from './saga';
import messages from './messages';

export class NetworkController extends React.PureComponent { // eslint-disable-line react/prefer-stateless-function
  render() {
    return (
      <div>
        <FormattedMessage {...messages.header} />
      </div>
    );
  }
}

NetworkController.propTypes = {
  dispatch: PropTypes.func.isRequired,
};

const mapStateToProps = createStructuredSelector({
  networkcontroller: makeSelectNetworkController(),
});

function mapDispatchToProps(dispatch) {
  return {
    dispatch,
  };
}

const withConnect = connect(mapStateToProps, mapDispatchToProps);

const withReducer = injectReducer({ key: 'networkController', reducer });
const withSaga = injectSaga({ key: 'networkController', saga });

export default compose(
  withReducer,
  withSaga,
  withConnect,
)(NetworkController);

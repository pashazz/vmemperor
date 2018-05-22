/**
 *
 * Vms
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
import makeSelectVms from './selectors';
import reducer from './reducer';
import saga from './saga';
import messages from './messages';
import { Server } from 'mock-socket';
import axios from 'axios';

export class Vms extends React.Component { // eslint-disable-line react/prefer-stateless-function
  render() {
    return (
      <div>
        <FormattedMessage {...messages.header} />
      </div>
    );
  }

  componentDidMount(){

  }

  componentWillUnmount()
  {
  }
}


Vms.propTypes = {
  dispatch: PropTypes.func.isRequired,
};

const mapStateToProps = createStructuredSelector({
  vms: makeSelectVms(),
});

function mapDispatchToProps(dispatch) {
  return {
    dispatch,
  };
}

const withConnect = connect(mapStateToProps, mapDispatchToProps);

const withReducer = injectReducer({ key: 'vms', reducer });
const withSaga = injectSaga({ key: 'vms', saga });

export default compose(
  withReducer,
  withSaga,
  withConnect,
)(Vms);

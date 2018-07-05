/**
 *
 * CreateVm
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
import makeSelectCreateVm from './selectors';
import reducer from './reducer';
import saga from './saga';
import messages from './messages';

export class CreateVm extends React.Component { // eslint-disable-line react/prefer-stateless-function
  render() {
    return (
      <div>
        <FormattedMessage {...messages.header} />
      </div>
    );
  }
}

CreateVm.propTypes = {
  dispatch: PropTypes.func.isRequired,
};

const mapStateToProps = createStructuredSelector({
  createvm: makeSelectCreateVm(),
});

function mapDispatchToProps(dispatch) {
  return {
    dispatch,
  };
}

const withConnect = connect(mapStateToProps, mapDispatchToProps);

const withReducer = injectReducer({ key: 'createVm', reducer });
const withSaga = injectSaga({ key: 'createVm', saga });

export default compose(
  withReducer,
  withSaga,
  withConnect,
)(CreateVm);

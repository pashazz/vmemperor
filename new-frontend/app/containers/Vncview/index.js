/**
 *
 * Vncview
 *
 */

import React from 'react';
import T from 'prop-types';
import { connect } from 'react-redux';
import { FormattedMessage } from 'react-intl';
import { createStructuredSelector } from 'reselect';
import { compose } from 'redux';

import { VncDisplay } from 'react-vnc-display';

import injectSaga from 'utils/injectSaga';
import injectReducer from 'utils/injectReducer';
import Loader from 'components/Loader';
import { makeSelectUrl } from './selectors';
import reducer from './reducer';
import saga from './saga';
import messages from './messages';
import { vncRequest } from "./actions";


export class Vncview extends React.Component { // eslint-disable-line react/prefer-stateless-function
  constructor(props){
    super(props);
  }
  render() {
    return (
      <div>
        { this.props.url ?
          (
            <VncDisplay url={this.props.url}/>
          )
          : (
            <Loader/>
          )}
      </div>
    );
  }
  componentWillMount() {
    this.props.vncRequest(this.props.match.params.uuid);
  }
}

Vncview.propTypes = {
  url: T.string,
  vncRequest: T.func.isRequired,
  match: T.shape({
    params: T.shape({
      uuid: T.string.isRequired,
    }).isRequired,
  }).isRequired,

};

const mapStateToProps = createStructuredSelector({
  url: makeSelectUrl(),
});

const  mapDispatchToProps =  {
    vncRequest,
};

const withConnect = connect(mapStateToProps, mapDispatchToProps);

const withReducer = injectReducer({ key: 'vncview', reducer });
const withSaga = injectSaga({ key: 'vncview', saga });

export default compose(
  withReducer,
  withSaga,
  withConnect,
)(Vncview);

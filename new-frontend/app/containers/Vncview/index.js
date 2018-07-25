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

import  VncDisplay from 'components/VncDisplay';

import injectSaga from 'utils/injectSaga';
import injectReducer from 'utils/injectReducer';
import Loader from 'components/Loader';
import { makeSelectUrl,
  makeSelectError
} from './selectors';
import reducer from './reducer';
import saga from './saga';
import messages from './messages';
import { vncRequest } from "./actions";
import NavLink from "../../components/NavLink";


export class Vncview extends React.PureComponent { // eslint-disable-line react/prefer-stateless-function
  constructor(props){
    super(props);

  }

  render() {
    console.log(this.props.error);
    return (
      <div>
        { this.props.error && (<div>
          <h1 className="text-center">Unable to open VNC console </h1>
          <p className="text-monospace"> {JSON.stringify(this.props.error)} </p>
        </div>) || (
          this.props.url ?
          (
            <VncDisplay url={this.props.url}/>
          ) : ( <Loader/>)
          )
        }
      </div>
    );
  }
  componentWillMount() {
    if (this.props.match) {
      this.props.vncRequest(this.props.match.params.uuid);
    }
    else {
     this.props.vncRequest(this.props.uuid);
    }

  }
}


const mapStateToProps = createStructuredSelector({
  url: makeSelectUrl(),
  error: makeSelectError(),
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

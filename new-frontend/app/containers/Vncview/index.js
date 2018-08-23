/**
 *
 * Vncview
 *
 */

import React, {Fragment} from 'react';
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
  makeSelectError,
  makeSelectUuid
} from './selectors';
import reducer from './reducer';
import saga from './saga';
import messages from './messages';
import { vncRequest } from "./actions";
import NavLink from "../../components/NavLink";
import { makeSelectVmData} from "../App/selectors";


export class Vncview extends React.PureComponent { // eslint-disable-line react/prefer-stateless-function
  constructor(props){
    super(props);

  }

  render() {
    console.log(this.props.error);
    let label = null;
    if (this.props.url)
    {
      console.log('label');
      label =this.props.vmData.get(this.props.uuid_selected).name_label;

    }


    return (
      <div>
        { this.props.error && (<div>
          <h1 className="text-center">Unable to open VNC console </h1>
          <p className="text-monospace"> {JSON.stringify(this.props.error)} </p>
        </div>) || (

          this.props.url ?
          (
            <Fragment>
            <h2>{
              label
            }</h2>
            <VncDisplay url={this.props.url}/>
            </Fragment>
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
  uuid_selected: makeSelectUuid(),
  vmData: makeSelectVmData(),
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

/**
 *
 * Vmsettings
 *
 */

import React from 'react';
import T from 'prop-types';
import IPT from 'react-immutable-proptypes';
import { connect } from 'react-redux';
import { createStructuredSelector } from 'reselect';
import { compose } from 'redux';

import injectSaga from 'utils/injectSaga';
import injectReducer from 'utils/injectReducer';
import makeSelectVmsettings from './selectors';
import reducer from './reducer';
import saga from './saga';
import VmsettingsForm from "../../components/VmsettingsForm";
import {makeSelectVmData} from "../../containers/App/selectors";
import { halt, run, reboot } from "../App/actions";
import {requestDiskInfo, vm_convert, vdi_detach, vdi_attach, vmWatch} from "./actions";
import {makeSelectDiskInfo} from "./selectors";

class VMSettings extends React.PureComponent { // eslint-disable-line react/prefer-stateless-function
  constructor(props)
  {
    super(props);
    this.render = this.render.bind(this);
    this.onHalt = this.onHalt.bind(this);
    this.onReboot = this.onReboot.bind(this);
    this.onConvertVm = this.onConvertVm.bind(this);
    this.onDetachVdi = this.onDetachVdi.bind(this);
    this.onAttachVdi = this.onAttachVdi.bind(this);

  }

  /* static getDerivedStateFromProps(props, state)
  {
    if (props.vm_data) {
      return {
        uuid: props.match.params.uuid,
        data: props.vm_data.get(props.match.params.uuid),
        loading: false,
      }
    }
    else{
      return {loading: true,}
    }
  } */
  onHalt()
  {
    const data  = this.props.vm_data.get(this.props.match.params.uuid);
    if (data.power_state === 'Halted')
    {
      this.props.run([data.uuid]);
    }
    else
    {
      this.props.halt([data.uuid]);
    }
  }

  onReboot()
  {

    const data  = this.props.vm_data.get(this.props.match.params.uuid);
    if (data.power_state === 'Running')
    {
      console.log("Rebooting");
      this.props.reboot([data.uuid]);
    }
  }

  onConvertVm()
  {
    const data  = this.props.vm_data.get(this.props.match.params.uuid);
    if (data.power_state === 'Halted')
    {

      const mode = data.domain_type === 'hvm' ? 'pv' : 'hvm';
      console.log("Converting to " + mode);
      this.props.vm_convert(data.uuid, mode);
    }
  }

  onDetachVdi(vdi)
  {
    this.props.vdi_detach(this.props.match.params.uuid, vdi);
    //this.props.requestDiskInfo(this.props.match.params.uuid);
  }

  onAttachVdi(vdi)
  {
    this.props.vdi_attach(this.props.match.params.uuid, vdi);
    //this.props.requestDiskInfo(this.props.match.params.uuid);
  }

  componentDidMount()
  {

    const { props } = this;
    if (props.match) {
      if (props.vmWatch)
      {
        props.vmWatch(props.match.params.uuid);
      }
      if (!props.diskInfo.size) {
        props.requestDiskInfo(props.match.params.uuid);
      }
    }
  }


  render() {
    const data  = this.props.vm_data.get(this.props.match.params.uuid);
    if (!data) {
      return (
        <div>
          <h1>
            VM NOT FOUND
          </h1>
        </div>

      )
    }
    else {
      return (
        <div>
          <VmsettingsForm
            data={data}
            onHalt={this.onHalt}
            onReboot={this.onReboot}
            onConvertVm={this.onConvertVm}
            onAttachVdi={this.onAttachVdi}
            onDetachVdi={this.onDetachVdi}
            diskInfo={this.props.diskInfo}
          />
        </div>
      );
    }
  }
}

VMSettings.propTypes = {
  vm_data: IPT.map.isRequired,
  match: T.shape({
    params: T.shape({
      uuid: T.string.isRequired,
    }),
  }).isRequired,
  halt: T.func.isRequired,
  run: T.func.isRequired,
  reboot: T.func.isRequired,
  vm_convert: T.func.isRequired,
  vdi_detach: T.func.isRequired,
  vdi_attach: T.func.isRequired,
};

const mapStateToProps = createStructuredSelector({
  vm_data: makeSelectVmData(),
  diskInfo: makeSelectDiskInfo(),
});

const mapDispatchToProps = {
  halt,
  run,
  reboot,
  vm_convert,
  requestDiskInfo,
  vdi_detach,
  vdi_attach,
  vmWatch
};




const withConnect = connect(mapStateToProps, mapDispatchToProps);

const withReducer = injectReducer({ key: 'vmsettings', reducer });
const withSaga = injectSaga({ key: 'vmsettings', saga });

export default compose(
  withReducer,
  withSaga,
  withConnect,
)(VMSettings);

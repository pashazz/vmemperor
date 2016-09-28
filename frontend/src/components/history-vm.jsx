import store from 'store';
import React from 'react';

import { vm as VM } from '../api/vmemp-api';

class VMEntry extends React.Component {
  render() {
    const { name, status, details } = this.props;
    const color =
      status === -1 ? 'danger' :
      (status === 100 ? 'success' : null);
    return (
      <tr className={color}>
        <td>{name}</td>
        <td>
          {status > 0 ?
            <div className="progress">
              <div className="progress-bar" aria-valuenow={status} aria-valuemin="0" aria-valuemax="100" style={{width: `${status}%`}}>
                <span className="sr-only">{status}% Complete</span>
              </div>
            </div> : <b>Error</b>}
        </td>
        <td>{details}</td>
        <td>
          <button className="btn btn-danger" onClick={this.props.onStop}>Stop Tracking</button>
        </td>
      </tr>
    );
  }
}

class HistoryVM extends React.Component {
  constructor(props) {
    super(props);

    this.setStoreAndState = this.setStoreAndState.bind(this);
    this.removeTracking = this.removeTracking.bind(this);

    this.state = {
      vms: store.get('vm-history') || {}
    }
  }

  componentDidMount() {
    VM.status(Object.keys(store.get('vm-history')))
      .then(response => this.setStoreAndState(response));
    this.interval = setInterval(() => {
      VM.status(Object.keys(store.get('vm-history')))
        .then(response => this.setStoreAndState(response))
    }, 5000);
  }

  componentWillUnmount() {
    clearInterval(this.interval);
  }

  setStoreAndState(vms) {
    store.set('vm-history', vms);
    this.setState({vms: vms});
  }

  removeTracking(vmid) {
    return (e) => {
      e.preventDefault();
      let vms = store.get('vm-history');
      delete vms[vmid];
      this.setStoreAndState(vms);
    }
  }

  render() {
    return (
      <div className="table-responsive">
        <table className="table table-hover table-vcenter">
          <thead>
            <tr>
              <th className="col-sm-2">VM name</th>
              <th className="col-sm-4">Progress</th>
              <th className="col-sm-5">Status</th>
              <th className="col-sm-1"></th>
            </tr>
          </thead>
          <tbody>
            {Object.keys(this.state.vms).map(vmid =>
              <VMEntry key={vmid} {...this.state.vms[vmid]} onStop={this.removeTracking(vmid)} />)}
          </tbody>
        </table>
      </div>
    );
  }
}

export default HistoryVM;

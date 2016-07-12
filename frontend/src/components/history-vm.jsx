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
      vms: store.get('vm-history') || []
    }
  }

  componentDidMount() {
    VM.status(Object.keys(this.state.vms))
      .then(response => this.setStoreAndState(response));
    this.interval = setInterval(() => {
      VM.status(Object.keys(this.state.vms))
        .then(response => this.setStoreAndState(response))
    }, 5000);
  }

  componentWillUnmount() {
    clearInterval(this.interval);
  }

  setStoreAndState(vms) {
    store.set('vm-history', vms);
    this.setState({vms: store.get('vm-history')});
  }

  removeTracking(vm) {
    return (e) => {
      e.preventDefault();
      const vms = store.get('vm-history');
      this.setStoreAndState(vms.filter(v => v.id !== vm.id));
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
            {this.state.vms.map((vm, idx) =>
              <VMEntry key={idx} {...vm} onStop={this.removeTracking(vm)} />)}
          </tbody>
        </table>
      </div>
    );
  }
}

export default HistoryVM;

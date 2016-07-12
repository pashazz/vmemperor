import store from 'store';
import React from 'react';

import { vm as VM } from '../api/vmemp-api';

class VMEntry extends React.Component {
  render() {
    return (
      <tr>
        <td>1</td>
        <td>1</td>
        <td>1</td>
      </tr>
    );
  }
}

class HistoryVM extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      vms: store.get('vm-history') || []
    }
  }

  componentDidMount() {
    this.interval = setInterval(() => {
      VM.status(Object.keys(this.state.vms))
        .then(response => store.set('vm-history', response))
        .then(_ => this.setState({vms: store.get('vm-history')}))
    }, 5000);
  }

  componentWillUnmount() {
    clearInterval(this.interval);
  }

  render() {
    return (
      <div className="table-responsive">
        <table className="table table-hover table-vcenter">
          <thead>
            <tr>
              <th className="col-sm-2">VM name</th>
              <th className="col-sm-6">Progress</th>
              <th className="col-sm-4">Status</th>
            </tr>
          </thead>
          <tbody>
            {this.state.vms.map((vm, idx) => <VMEntry key={idx} {...vm}/>)}
          </tbody>
        </table>
      </div>
    );
  }
}

export default HistoryVM;

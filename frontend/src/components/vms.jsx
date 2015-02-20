var React = require('react'),
    Reflux = require('reflux'),
    Router = require('react-router');

var VMStore = require('../flux/vm-store'),
    VMActions = require('../flux/vm-actions');

var VMInfo = React.createClass({
  _start: function(e) {
    e.preventDefault();
    VMActions.start(this.props.vm);
  },

  render: function() {
    var actions = (this.props.vm.state == 'halted' ? <a className="btn btn-primary btn-xs" onClick={this._start}>start</a> : '');

    return (
      <tr>
        <td>{this.props.vm.name}</td>
        <td>{this.props.vm.ip}</td>
        <td>{this.props.vm.vcpus}</td>
        <td>{this.props.vm.RAM}</td>
        <td>{this.props.vm.state}</td>
        <td>{actions}</td>
      </tr>
    );
  }

});

var VMList = React.createClass({
  mixins: [Reflux.ListenerMixin],

  onVMChange: function() {
    this.setState({
      status: VMStore.status,
      vms: VMStore.vms
    });
  },

  componentDidMount: function() {
      this.listenTo(VMStore, this.onVMChange);
      VMActions.list();
  },

  getInitialState: function() {
    return {
      status: VMStore.status,
      vms: VMStore.vms
    };
  },

  renderStatus: function() {
    switch(this.state.status) {
      case 'PULL': return (<div>Pulling…</div>);
      case 'PUSH': return (<div>Pushing…</div>);
      case 'READY': return (<div>Up to date</div>);
    }
    return '';
  },

  render: function () {
    var tbody = this.state.vms.map(function(vm){
      return <VMInfo key={vm.id} vm={vm} />;
    });

    return (
      <div>
        {this.renderStatus()}
        <table className="table table-hover">
          <thead>
            <tr>
              <th>Virtual Machine</th>
              <th>IP</th>
              <th>VCPUs</th>
              <th>RAM</th>
              <th>State</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>{tbody}</tbody>
        </table>
      </div>
    );
  }
  
});

module.exports = VMList;
var React = require('react'),
    Reflux = require('reflux'),
    Router = require('react-router'),
    $ = require('jquery'),
    ts = require('tablesorter');

var VMStore = require('../flux/vm-store'),
    VMActions = require('../flux/vm-actions');

var VMInfo = React.createClass({
  _start: function(e) {
    e.preventDefault();
    VMActions.start(this.props.vm);
  },

  render: function() {
    var actions = (this.props.vm.state == 'halted' ? <a className="btn btn-primary btn-xs" onClick={this._start}>start</a> : '');
    var stateLabel = (this.props.vm.state == 'Halted' ? 
      <span className="label label-warning">Halted</span> : 
      <span className="label label-success">Running</span>);

    return (
      <tr>
        <td>{this.props.vm.name}</td>
        <td>{this.props.vm.ip}</td>
        <td>{this.props.vm.vcpus}</td>
        <td>{this.props.vm.RAM}</td>
        <td>{stateLabel}</td>
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

  setSortName: function() {
    VMActions.sort('name');
  },

  setSortIP: function() {
    VMActions.sort('ip');
  },

  setSortVCPUs: function() {
    VMActions.sort('vcpus');
  },

  setSortRAM: function() {
    VMActions.sort('RAM');
  },

  setSortState: function() {
    VMActions.sort('state');
  },

  renderStatus: function() {
    switch(this.state.status) {
      case 'PULL': return (<div className="col-md-12">Pulling…</div>);
      case 'PUSH': return (<div className="col-md-12">Pushing…</div>);
      case 'READY': return (<div className="col-md-12">Up to date</div>);
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
             <th onClick={this.setSortName}>Virtual Machine</th>
             <th onClick={this.setSortIP}>IP</th>
             <th onClick={this.setSortVCPUs}>VCPUs</th>
             <th onClick={this.setSortRAM}>RAM</th>
             <th onClick={this.setSortState}>State</th>
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
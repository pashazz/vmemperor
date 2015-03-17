var Reflux = require('reflux'),
    VMActions = require('./vm-actions'),
    AlertActions = require('./alert-actions'),
    VM = require('./vm-model');

var VMStore = Reflux.createStore({
  
  init: function() {
    // this.listenTo(VMActions.list, this.onList);
    // this.listenTo(VMActions.start, this.onStart);
    this.listenToMany(VMActions);
    
    this.status = '';
    this.vms = [];
  },

  length: function() {
    return this.vms.length;
  },

  // Listing VMs
  onList: function() {
    this.status = 'PULL';
    AlertActions.log('Getting VM list...');
    this.trigger();
  },

  onListCompleted: function(response) {
    this.vms = response.map(function(single) { return new VM(single); });
    this.status = 'READY';
    AlertActions.suc('Got VM list');
    this.trigger();
  },

  onListFailed: function(response) {
    AlertActions.err("Error while getting VM list!");
  },

  // Starting VM
  onStart: function(vm) {
    this.status = 'PUSH';
    AlertActions.log('Starting VM:' + vm.name);
    this.trigger();
  },

  onStartCompleted: function(response) {
    AlertActions.suc('VM started');
    VMActions.list(); 
  },

  onStartFailed: function(response) {
    AlertActions.err("Error while starting VM");
  },

  // Shutting down VM
  onShutdown: function(vm) {
    this.status = 'PUSH';
    AlertActions.log('Shutting down VM:' + vm.name);
    this.trigger();
  },

  onShutdownCompleted: function(response) {
    AlertActions.suc('VM shutdown');
    VMActions.list(); 
  },

  onShutdownFailed: function(response) {
    AlertActions.err("Error while shutting down VM:" + vm.name);
  }

});

module.exports = VMStore;

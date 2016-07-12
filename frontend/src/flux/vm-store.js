import Reflux from 'reflux';
import VMActions from './vm-actions';
import AlertActions from './alert-actions';
import VM from './vm-model';

const VMStore = Reflux.createStore({

  init() {
    this.listenToMany(VMActions);

    this.status = '';
    this.vms = [];
  },

  length() {
    return this.vms.length;
  },

  // Listing VMs
  onList() {
    this.status = 'PULL';
    AlertActions.log('Getting VM list...');
    this.trigger();
  },

  onListCompleted(response) {
    this.vms = response.map(data => new VM(data));
    this.status = 'READY';
    AlertActions.suc('Got VM list');
    this.trigger();
  },

  onListFailed(response) {
    AlertActions.err("Error while getting VM list!");
  },

  // Starting VM
  onStart(vm) {
    this.status = 'PUSH';
    AlertActions.log('Starting VM:' + vm.name);
    this.trigger();
  },

  onStartCompleted(response) {
    AlertActions.suc('VM started');
    VMActions.list();
  },

  onStartFailed(response) {
    AlertActions.err("Error while starting VM");
  },

  // Shutting down VM
  onShutdown(vm) {
    this.status = 'PUSH';
    AlertActions.log('Shutting down VM:' + vm.name);
    this.trigger();
  },

  onShutdownCompleted(response) {
    AlertActions.suc('VM shutdown');
    VMActions.list();
  },

  onShutdownFailed(response) {
    AlertActions.err("Error while shutting down VM");
  },

  // Creating VM
  onCreate(params) {
    this.status = 'PUSH';
    AlertActions.log('Creating new VM');
    this.trigger();
  },

  onCreateCompleted(response) {
    AlertActions.suc('VM created');
    VMActions.list();
  },

  onCreateFailed(response) {
    AlertActions.err("Error while creating VM");
  }

});

export default VMStore;

import Reflux from 'reflux';
import TemplateActions from './template-actions';
import AlertActions from './alert-actions';
import VMApi from '../api/vmemp-api';
import Template from './template-model';


const TemplateStore = Reflux.createStore({

  init() {
    this.listenToMany(TemplateActions);

    this.status = '';
    this.templates = [];
  },

  length() {
    return this.templates.length;
  },

  // List Templates
  onList() {
    this.status = 'PULL';
    AlertActions.log('Getting Template list...');
    this.trigger();
  },

  onListCompleted(response) {
    this.templates = response.map(data => new Template(data));
    this.status = 'READY';
    AlertActions.suc('Got Template list');
    this.trigger();
  },

  onListFailed(response) {
    AlertActions.err("Error while getting Template list!");
  },

  // Enable template
  onEnable() {
    this.status = 'PUSH';
    AlertActions.log('Enabling Template ...');
    this.trigger();
  },

  onEnableCompleted(response) {
    this.status = 'READY';
    AlertActions.suc('Template enabled');
    TemplateActions.list();
    this.trigger();
  },

  onEnableFailed(response) {
    AlertActions.err("Error while enabling Template!");
  },

  // Disable template
  onDisable() {
    this.status = 'PUSH';
    AlertActions.log('Disabling Template ...');
    TemplateActions.list();
    this.trigger();
  },

  onDisableCompleted(response) {
    this.status = 'READY';
    AlertActions.suc('Template disabled');
    this.trigger();
  },

  onDisableFailed(response) {
    AlertActions.err("Error while disabling Template!");
  }
});

export default TemplateStore;

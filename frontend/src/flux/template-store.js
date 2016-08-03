import Reflux from 'reflux';
import TemplateActions from './template-actions';
import AlertActions from './alert-actions';
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
    AlertActions.err('Error while getting Template list!');
  },

  // Update template
  onUpdate() {
    this.status = 'PUSH';
    AlertActions.log('Updating Template ...');
  },

  onUpdateCompleted(response) {
    this.status = 'READY';
    AlertActions.suc('Template updated');
    TemplateActions.list();
  },

  onUpdateFailed(response) {
    AlertActions.err('Error while updating Template!');
    TemplateActions.list();
  },

  // Enable template
  onEnable() {
    this.status = 'PUSH';
    AlertActions.log('Enabling Template ...');
  },

  onEnableCompleted(response) {
    this.status = 'READY';
    AlertActions.suc('Template enabled');
    TemplateActions.list();
  },

  onEnableFailed(response) {
    AlertActions.err('Error while enabling Template!');
    TemplateActions.list();
  },

  // Disable template
  onDisable() {
    this.status = 'PUSH';
    AlertActions.log('Disabling Template ...');
  },

  onDisableCompleted(response) {
    this.status = 'READY';
    AlertActions.suc('Template disabled');
    TemplateActions.list();
  },

  onDisableFailed(response) {
    AlertActions.err('Error while disabling Template!');
    TemplateActions.list();
  }
});

export default TemplateStore;

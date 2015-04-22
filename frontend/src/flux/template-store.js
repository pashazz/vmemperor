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

  onList() {
    this.status = 'PULL';
    AlertActions.log('Getting Template list...');
    this.trigger();
  },

  onListCompleted(response) {
    this.templates = response;
    this.status = 'READY';
    AlertActions.suc('Got Template list');
    this.trigger();
  },

  onListFailed(response) {
    AlertActions.err("Error while getting Template list!");
  }

});

export default TemplateStore;

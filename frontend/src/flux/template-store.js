var Reflux = require('reflux'),
    TemplateActions = require('./template-actions'),
    AlertActions = require('./alert-actions'),
    VMApi = require('../api/vmemp-api'),
    Template = require('./template-model');

var TemplateStore = Reflux.createStore({
  
  init: function() {
    this.listenToMany(TemplateActions);
    
    this.status = '';
    this.templates = [];
  },

  length: function() {
    return this.templates.length;
  },

  onList: function() {
    this.status = 'PULL';
    AlertActions.log('Getting Template list...');
    this.trigger();
  },

  onListCompleted: function(response) {
    this.templates = response;
    this.status = 'READY';
    AlertActions.suc('Got Template list');
    this.trigger();
  },

  onListFailed: function(response) {
    AlertActions.err("Error while getting Template list!");
  }

});

module.exports = TemplateStore;

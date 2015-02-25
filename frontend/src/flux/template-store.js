var Reflux = require('reflux'),
    TemplateActions = require('./template-actions'),
    AlertActions = require('./alert-actions'),
    VMApi = require('../api/vmemp-api');

var TemplateStore = Reflux.createStore({
  
  init: function() {
    this.listenTo(TemplateActions.list, this.listTemplates);
    
    this.status = '';
    this.templates = [];
  },

  length: function() {
    return this.templates.length;
  },

  listTemplates: function() {
    this.status = 'PULL';
    AlertActions.log('Getting Template list...');
    this.trigger();
    VMApi.listTemplates()
      .then(this.onListCompleted)
      .catch(function(response) {
        TemplateActions.listFail(response);
        AlertActions.err("Error while getting Template list!");
      });
  },

  onListCompleted: function(response) {
    this.templates = response.data;
    this.status = 'READY';
    AlertActions.suc('Got Template list');
    this.trigger();
  }

});

module.exports = TemplateStore;

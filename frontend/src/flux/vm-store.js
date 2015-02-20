var Reflux = require('reflux'),
    VMActions = require('./vm-actions'),
    VMApi = require('../api/vmemp-api');

var VMStore = Reflux.createStore({
  
  init: function() {
    this.listenTo(VMActions.list, this.listVMs);
    this.listenTo(VMActions.start, this.startVM);
    this.status = '';
    this.vms = [];
  },

  length: function() {
    return this.vms.length;
  },

  listVMs: function() {
    this.status = 'PULL';
    this.trigger();
    VMApi.listVMs(function(data){
      this.vms = data;
      this.status = 'READY';
      this.trigger();
      // VMActions.list.completed();
    }.bind(this));
  },

  startVM: function(vm) {
    this.status = 'PUSH';
    this.trigger();
    VMApi.startVM(vm, function(){
      this.status = 'READY';
      this.trigger();
    }.bind(this));
  }

});

var errorStore = Reflux.createStore({
    init: function() {
        this.listenTo(VMActions.list.failed, this.errCatched);
        this.listenTo(VMActions.start.failed, this.errCatched);
    },
    errCatched: function(payload) {
      console.log("Error catched ", payload);
    },
    getDefaultData: function() { return ""; }
});

module.exports = VMStore;

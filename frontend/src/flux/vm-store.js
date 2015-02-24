var Reflux = require('reflux'),
    VMActions = require('./vm-actions'),
    VMApi = require('../api/vmemp-api'),
    VM = require('./vm-model');

var VMStore = Reflux.createStore({
  
  init: function() {
    this.listenTo(VMActions.list, this.listVMs);
    this.listenTo(VMActions.start, this.startVM);
    this.listenTo(VMActions.shutdown, this.shutdownVM);
    this.listenTo(VMActions.sort, this.changeSort)
    this.sortField = '';
    this.sortOrder = 1;
    this.status = '';
    this.vms = [];
  },

  length: function() {
    return this.vms.length;
  },

  listVMs: function() {
    this.status = 'PULL';
    this.trigger();
    VMApi.listVMs()
      .then(this.onListCompleted)
      .fail(function(data) {
        VMActions.listFail(data)
      });
  },

  onListCompleted: function(data) {
    this.vms = data.map(function(single) { return new VM(single); });
    this.status = 'READY';
    this.trigger();
  },


  startVM: function(vm) {
    this.status = 'PUSH';
    this.trigger();
    VMApi.startVM(vm)
      .then(this.onStartCompleted)
      .fail(function(data) {
        VMActions.startFail(vm, data);
      });
  },

  onStartCompleted: function(data) {
    console.log(data);
    VMActions.list(); 
  },

  shutdownVM: function(vm) {
    this.status = 'PUSH';
    this.trigger();
    VMApi.shutdownVM(vm)
      .then(this.onShutdownCompleted)
      .fail(function(data) {
        VMActions.shutdownFail(vm, data);
      });
  },

  onShutdownCompleted: function(data) {
    console.log(data);
    VMActions.list(); 
  }

});

var errorStore = Reflux.createStore({

    init: function() {
      this.listenTo(VMActions.listFail, this.errCatched);
      this.listenTo(VMActions.startFail, this.errCatched);
      this.listenTo(VMActions.shutdownFail, this.errCatched);
    },

    errCatched: function(payload) {
      console.log("Error catched ", payload);
    },

    getDefaultData: function() { return ""; }
});

module.exports = VMStore;

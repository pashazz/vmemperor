var Reflux = require('reflux'),
    VMActions = require('./vm-actions'),
    VMApi = require('../api/vmemp-api'),
    VM = require('./vm-model');

var VMStore = Reflux.createStore({
  
  init: function() {
    this.listenTo(VMActions.list, this.listVMs);
    this.listenTo(VMActions.start, this.startVM);
    this.listenTo(VMActions.sort, this.changeSort)
    this.sortField = '';
    this.sortOrder = 1;
    this.status = '';
    this.vms = [];
  },

  length: function() {
    return this.vms.length;
  },

  changeSort: function(field) {
    if(this.sortField === field) {
      this.sortOrder = -this.sortOrder;
    } else {
      this.sortField = field;
      this.sortOrder = 1;
    }
    this.sortVMs();
    this.trigger();
  },

  sortVMs: function() {
    if (!(this.sortOrder === 1 || this.sortOrder === -1 || this.sortField != '')) {
      return ;
    }
    this.vms = this.vms.sort(function(a,b) {
      if (a[this.sortField] === b[this.sortField]) {
        return 0;
      };
      if (a[this.sortField] > b[this.sortField]) {
        return (this.sortOrder === 1) ? 1 : -1;
      };
      return (this.sortOrder === 1) ? -1 : 1;
    }.bind(this));
  },

  listVMs: function() {
    this.status = 'PULL';
    this.trigger();
    VMApi.listVMs()
      .then(this.onListCompleted)
      .fail(function() {
        VMActions.listFail()
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
    VMApi.startVM(vm, function(){
      this.status = 'READY';
      this.trigger();
    }.bind(this));
  }

});

var errorStore = Reflux.createStore({
    init: function() {
      this.listenTo(VMActions.listFail, this.errCatched);
      this.listenTo(VMActions.startFail, this.errCatched);
    },
    errCatched: function(payload) {
      console.log("Error catched ", payload);
    },
    getDefaultData: function() { return ""; }
});

module.exports = VMStore;

var VMActions = require('../flux/vm-actions'),
    $ = require('jquery');

var VMAPI = {  
    listVMs: function(callback) {
      return $.getJSON('/list-vms');
    },
    startVM: function(vm, callback) {
      setTimeout(function() {
        vms[vm.id-1].state = 'running'
        callback();
      }, 1000);
    },
    listTemlates: function(callback) {

    }
};

module.exports = VMAPI;
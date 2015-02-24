var VMActions = require('../flux/vm-actions'),
    $ = require('jquery');

var VMAPI = {  

    listVMs: function() {
      return $.getJSON('/list-vms');
    },

    startVM: function(vm) {
      return $.post('/start-vm', {
        vm_uuid: vm.id,
        endpoint_url: vm.endpoint_url,
        endpoint_description: vm.endpoint_description
      });
    },

    shutdownVM: function(vm) {
      return $.post('/shutdown-vm', {
        vm_uuid: vm.id,
        endpoint_url: vm.endpoint_url,
        endpoint_description: vm.endpoint_description
      });
    },

    listTemlates: function(callback) {

    }
};

module.exports = VMAPI;
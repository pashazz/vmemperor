var VMActions = require('../flux/vm-actions'),
    axios = require('axios');

VMAPI = {  

    listVMs: function() {
      return axios.get('/list-vms');
    },

    startVM: function(vm) {
      return axios.post('/start-vm', {
        vm_uuid: vm.id,
        endpoint_url: vm.endpoint_url,
        endpoint_description: vm.endpoint_description
      });
    },

    shutdownVM: function(vm) {
      return axios.post('/shutdown-vm', {
        vm_uuid: vm.id,
        endpoint_url: vm.endpoint_url,
        endpoint_description: vm.endpoint_description
      });
    },

    listTemplates: function() {
      return axios.get('/list-templates');
    }
};

module.exports = VMAPI;
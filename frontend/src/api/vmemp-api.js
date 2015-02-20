var VMActions = require('../flux/vm-actions');

var vms = [
        {
          id: 1,
          name: 'annotame',
          desc: 'Installed via xe CLI',
          ip: '172.31.156.167',
          vcpus: 1,
          RAM: '4096mb',
          state: 'halted'
        },
        {
          id: 2,
          name: 'egozoom',
          desc: 'Installed via xe CLI',
          ip: '172.31.78.158',
          vcpus: 1,
          RAM: '9000mb',
          state: 'running'
        }
      ];

setInterval(function() {
  if(vms[0].state == 'running') {
    vms[0].RAM = Math.floor(9000*Math.random()) + 'mb';  
    if(Math.random() > 0.9) {
      vms[0].state = 'halted';
    }
  }
  if(vms[1].state == 'running') {
    vms[1].RAM = Math.floor(9000*Math.random()) + 'mb';  
    if(Math.random() > 0.9) {
      vms[1].state = 'halted';
    }
  }
  VMActions.list();
}, 5000);

var VMAPI = {  
    listVMs: function(callback) {
      setTimeout(function() { 
        callback(vms);
      }, 1000);
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
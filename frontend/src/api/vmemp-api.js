var VMActions = require('../flux/vm-actions'),
    HTTP = require('axios');

var _session = null;

var loadFromCookie = function() {
  var cookies = document.cookie ? document.cookie.split('; ') : [];
  for (var i = cookies.length - 1; i >= 0; i--) {
    var parts = cookies[i].split('=');
    var name = parts.shift();
    if(name === 'session') {
      _session = parts.join('=');
      break;
    }
  };
  return _session;
};

VMAPI = {  

    session: function() {
      if (_session) {
        return _session;
      } else {
        return loadFromCookie();
      }
    },

    auth: function(data) {
      return HTTP.post('/auth', data)
    },

    logout: function() {
      return HTTP.get('/logout')
        .then(function(response) {
          _session = null;
        });
    },

    vms: function() {
      return HTTP.get('/list-vms');
    },

    vm_start: function(vm) {
      return HTTP.post('/start-vm', {
        vm_uuid: vm.id,
        endpoint_url: vm.endpoint_url,
        endpoint_description: vm.endpoint_description
      });
    },

    vm_shutdown: function(vm) {
      return HTTP.post('/shutdown-vm', {
        vm_uuid: vm.id,
        endpoint_url: vm.endpoint_url,
        endpoint_description: vm.endpoint_description
      });
    },

    templates: function() {
      return HTTP.get('/list-templates');
    }, 

    pools: function() {
      return HTTP.get('/list-pools');
    }, 
};

module.exports = VMAPI;
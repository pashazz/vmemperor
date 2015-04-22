var HTTP = require('./http');

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

var user = {
  session: function() {
    return (_session !== null) ? _session : loadFromCookie();
  },

  auth: function(data) {
    return HTTP.post('/auth', data);
  },

  logout: function() {
    return HTTP.get('/logout')
      .then(function(response) {
        _session = null;
      });
  }
};

var vm = {
  list: function() {
    return HTTP.get('/list-vms');
  },

  start: function(vm) {
    return HTTP.post('/start-vm', {
      vm_uuid: vm.id,
      endpoint_url: vm.endpoint_url,
      endpoint_description: vm.endpoint_description
    });
  },

  shutdown: function(vm) {
    return HTTP.post('/shutdown-vm', {
      vm_uuid: vm.id,
      endpoint_url: vm.endpoint_url,
      endpoint_description: vm.endpoint_description
    });
  }
};

var template = {
  list: function() {
    return HTTP.get('/list-templates');
  }
};

var pool = {
  list: function() {
    return HTTP.get('/list-pools');
  }
};

module.exports = {
  user: user,
  vm: vm,
  template: template,
  pool: pool
};

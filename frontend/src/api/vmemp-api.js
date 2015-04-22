import { GET, POST } from './http';

let _session = null;

const loadFromCookie = function() {
  let cookies = document.cookie ? document.cookie.split('; ') : [];
  for (let i = cookies.length - 1; i >= 0; i--) {
    let parts = cookies[i].split('=');
    let name = parts.shift();
    if(name === 'session') {
      _session = parts.join('=');
      break;
    }
  };
  return _session;
};

const user = {
  session() {
    return (_session !== null) ? _session : loadFromCookie();
  },

  auth(data) {
    return POST('/auth', data);
  },

  logout() {
    return GET('/logout')
      .then(function(response) {
        _session = null;
      });
  }
};

const vm = {
  list() {
    return GET('/list-vms');
  },

  start(vm) {
    return POST('/start-vm', {
      vm_uuid: vm.id,
      endpoint_url: vm.endpoint_url,
      endpoint_description: vm.endpoint_description
    });
  },

  shutdown(vm) {
    return POST('/shutdown-vm', {
      vm_uuid: vm.id,
      endpoint_url: vm.endpoint_url,
      endpoint_description: vm.endpoint_description
    });
  }
};

const template = {
  list() {
    return GET('/list-templates');
  }
};

const pool = {
  list() {
    return GET('/list-pools');
  }
};

export default { user, vm, template, pool }

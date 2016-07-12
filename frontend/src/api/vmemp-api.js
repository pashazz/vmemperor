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
  session: () =>
    (_session !== null) ? _session : loadFromCookie(),

  auth: (data) =>
    POST('/auth', data),

  logout: () =>
    GET('/logout').then(response => _session = null)
};

const vm = {
  list: () =>
    GET('/list-vms'),

  start: (vm) =>
    POST('/start-vm', {
      vm_uuid: vm.id,
      endpoint_url: vm.endpoint_url,
      endpoint_description: vm.endpoint_description
    }),

  shutdown: (vm) =>
    POST('/shutdown-vm', {
      vm_uuid: vm.id,
      endpoint_url: vm.endpoint_url,
      endpoint_description: vm.endpoint_description
    })
};

const template = {
  list: () =>
    GET('/list-templates')
};

const pool = {
  list: () =>
    GET('/list-pools')
};

export default { user, vm, template, pool }

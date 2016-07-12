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

  status: (ids) =>
    POST('/status-vm', {ids}),

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
    }),

  create: (params) =>
    POST('/create-vm', params)
};

const template = {
  list: () =>
    GET('/list-templates'),

  enable: (template) =>
    POST('/enable-template', {
      vm_uuid: template.id,
      endpoint_url: template.endpoint_url,
      endpoint_description: template.endpoint_description
    }),

  disable: (template) =>
    POST('/disable-template', {
      vm_uuid: template.id,
      endpoint_url: template.endpoint_url,
      endpoint_description: template.endpoint_description
    })
};

const pool = {
  list: () =>
    GET('/list-pools')
};

export default { user, vm, template, pool }

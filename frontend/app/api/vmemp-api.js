import { httpGet, httpPost } from './http';

let session = null;

function loadFromCookie() {
  const cookies = document.cookie ? document.cookie.split('; ') : [];
  for (let i = cookies.length - 1; i >= 0; i--) {
    const parts = cookies[i].split('=');
    const name = parts.shift();
    if (name === 'session') {
      session = parts.join('=');
      break;
    }
  }
  return session;
}

function nullifySession(pass) {
  session = null;
  return pass;
}

const user = {
  session() {
    return (session !== null) ? session : loadFromCookie();
  },

  auth(data) {
    return httpPost('/auth', data);
  },

  logout() {
    return httpGet('/logout').then(nullifySession);
  },
};

const vm = {
  list() {
    return httpGet('/list-vms');
  },

  status(ids) {
    return httpPost('/status-vm', { ids });
  },

  start(machine) {
    return httpPost('/start-vm', machine.toApi());
  },

  shutdown(machine) {
    return httpPost('/shutdown-vm', machine.toApi());
  },

  create(params) {
    return httpPost('/create-vm', params);
  },
};

const template = {
  list() {
    return httpGet('/list-templates');
  },

  enable(templ) {
    return httpPost('/enable-template', templ.toApi());
  },

  disable(templ) {
    return httpPost('/disable-template', templ.toApi());
  },

  update(templ) {
    return httpPost('/update-template', templ.toApi());
  },
};

const pool = {
  index() {
    return httpGet('/pool-index');
  },

  info() {
    return httpGet('/list-pools');
  },
};

export default {
  user,
  vm,
  template,
  pool,
};

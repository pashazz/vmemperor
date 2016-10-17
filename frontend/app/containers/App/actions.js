import {
  NEW_MESSAGE,
  AUTH,
  LOGOUT,
  SET_SESSION,
} from './constants';

function timestamp() {
  return +new Date();
}

export function auth(payload) {
  return {
    type: AUTH,
    payload,
  };
}

export function logout() {
  return {
    type: LOGOUT,
  };
}

export function setSession(session) {
  return {
    type: SET_SESSION,
    session,
  };
}

export function suc(text) {
  return {
    type: NEW_MESSAGE,
    message: {
      type: 'suc',
      text,
      timestamp: timestamp(),
    },
  };
}

export function warn(text) {
  return {
    type: NEW_MESSAGE,
    message: {
      type: 'warn',
      text,
      timestamp: timestamp(),
    },
  };
}

export function err(text) {
  return {
    type: NEW_MESSAGE,
    message: {
      type: 'err',
      text,
      timestamp: timestamp(),
    },
  };
}

export function info(text) {
  return {
    type: NEW_MESSAGE,
    message: {
      type: 'info',
      text,
      timestamp: timestamp(),
    },
  };
}

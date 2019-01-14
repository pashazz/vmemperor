import {
  NEW_MESSAGE,
  AUTH,
  LOGOUT,
  SET_SESSION,
  VMLIST_MESSAGE,
  VM_RUN_ERROR, VM_NOTIFICATION_INCREASE, VM_NOTIFICATION_DECREASE,
  VM_DELETE, VM_HALT, VM_RUN, ADD_TO_WAIT_LIST, REMOVE_FROM_WAIT_LIST, VM_REBOOT
} from './constants';

function timestamp() {
  return +new Date();
}


export function run(uuids)
{
  return {
    type: VM_RUN,
    uuids,

  }
}

export function halt(uuids) {
  return {
    type: VM_HALT,
    uuids,
  }

}
export function reboot(uuids) {
  return {
    type: VM_REBOOT,
    uuids,
  }
}

export function vm_delete(uuids) {
  return {
    type: VM_DELETE,
    uuids
  }
}

export function vm_convert(uuids) {
  return {
    type: VM_CONVERT,
    uuids
  }
}
export function addToWaitList(uuid, action, notifyId) {
  return {
    type: ADD_TO_WAIT_LIST,
    uuid, action, notifyId
  }
}

export function removeFromWaitList (uuid, action, notifyId) {
  return {
    type: REMOVE_FROM_WAIT_LIST,
    uuid, action, notifyId
  }
}



//TODO May we use it for another types of errors in the future?
export function vm_run_error(payload, date)
{
  const {message, details} = JSON.parse(payload);
  console.log("Error payload", payload);
  console.log("Error details: ", details);
  return {
    type: VM_RUN_ERROR,
    errorTitle: "Sorry, we couldn't launch VM",
    errorText: message,
    errorType: details[0],
    ref: details[1],
    errorDetailedText: details[2],
    date: date,
  }
}

export function vm_delete_error(payload, date)
{
  const {message, details} = JSON.parse(payload);
  console.log("Error payload", payload);
  console.log("Error details: ", details);

  return {
    type: VM_RUN_ERROR,
    errorTitle: "Sorry, we couldn't delete VM",
    errorText: message,
    errorType: details[0],
    ref: details[1],
    errorDetailedText: null,
    date: date,
  }
}

export function auth(login, password) {
  return {
    type: AUTH,
    login,
    password
  };
}

export function msgVmlist(message){
  return {
    type: VMLIST_MESSAGE,
    message
  }
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

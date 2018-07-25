import { take, call, put, select, all, takeEvery, takeLatest, apply, race} from 'redux-saga/effects';
import { eventChannel, END } from 'redux-saga';
import {AUTH, LOGOUT, AUTHENTICATED, LOGGED_OUT, VMLIST_URL, VMLIST_MESSAGE, REMOVE_FROM_WAIT_LIST} from './constants';
import { push, LOCATION_CHANGE} from 'react-router-redux';
import { makeSelectLocation } from './selectors';
import {authAgent} from "../PrivateRoute";
import {addToWaitList, msgVmlist, removeFromWaitList, vm_delete_error} from "./actions";
import { Server } from 'mock-socket';
import uuid from 'uuid';

import {startStopVm, destroyVm, reboot } from 'api/vm';
import {VM_DELETE, VM_HALT,  VM_RUN, VM_RUN_ERROR, VM_REBOOT} from "./constants";
import {vm_run_error, vmNotificationDecrease, vmNotificationIncrease, vm_deselect} from "./actions";
import React from 'react';
import { Map } from 'immutable';

import { actions } from 'react-redux-toastr';



const actionHandlers = Map({
  [VM_RUN]: {
    onError: vm_run_error,
    handler: function* (uuid) {
      const data = yield  call(startStopVm, uuid, true);
      console.log('vmRun: data:', data);
    },
    notificationTitle: "Starting VMs",
    status: 'running',
},
  [VM_HALT]: {
    onError: vm_run_error,
    handler: function* (uuid) {
      const data = yield  call(startStopVm, uuid, false);
      console.log('vmHalt: data:', data);
    },
    notificationTitle: "Stopping VMs",
    status: 'halted',
  },
  [VM_DELETE]: {
    onError: vm_delete_error,
    handler: function* (uuid) {
      const data = yield  call(destroyVm, uuid);
      console.log('vmHalt: data:', data);
    },
    notificationTitle: "Deleting VMs",
    status: 'removed',
  },
  [VM_REBOOT]: {
    onError: vm_run_error,
    handler: function* (uuid) {
      const data = yield call(reboot, uuid);
      console.log('vmReboot: data:', data);
    },
    notificationTitle: "Rebooting VMs",
    status: 'rebooted',
  },

});


function* showNotification(title, uuids) { //Show a toastr notification. Return its notifyId
  //Select vm names from store by uuids
  const selector = (state) => state.get('app').get('vm_data');
  const vm_data_map = yield select(selector);
  const names = uuids.map(uuid => vm_data_map.get(uuid).name_label);
  //Set up notification options
  const options = {
    id: uuid(),
    type: 'info',
    timeOut: 0,
    title,
    message: names.join('\n'),
    options: {
      showCloseButton: true,
    }
  };
  yield put(actions.add(options));
  return options.id;
}


function* handleActions (action){

  const handler = actionHandlers.get(action.type);
  const notifyId = yield showNotification(handler.notificationTitle, action.uuids);

  for (const uuid of action.uuids)
  {
    console.log("Notification id: ", notifyId, );
    yield addToWaitList(uuid, handler.status, notifyId);
    try {
      yield handler.handler(uuid);
    }
    catch (e)
    {
      if (e.response)
    {
      console.log(e.response);
      if (e.response.status === 400)
      {
        //Handle error
        if (e.response.data.details)
        {
          yield put(handler.onError(e.response.data.details));
        }
        else {
          console.error("Unhandled Response Error: ", e.response)
        }
      }
    }
    else {
      console.error(e);
      }
    }
    finally {
      yield put(removeFromWaitList(uuid, handler.status, notifyId));
    }
  }

}

export function* handleVMErrors(action)
{

  // select VM name from store by ref
  const selector = (state) => state.get('app').get('vm_data');
  const vm_data_map = yield select(selector);
  const vm_array = vm_data_map.valueSeq().toArray();
  let vmName = null;
  for (let value of vm_array)
  {
    console.log(value);
    if (value.ref === action.ref)
    {
      vmName = value.name_label;
      break;
    }
  }
  const {errorType, errorDetailedText} = action;
  let message = null;
  if (errorDetailedText)
  {
    message =  errorType + ": " + errorDetailedText;
  }
  else {
    message = errorType;
  }
  yield put(actions.add(
    {
      id: action.ref,
      type: 'error',
      title: action.errorTitle + ' "' + vmName +'"',
      message,
      options :
        {
          timeOut: 0,
          showCloseButton: true,
        }
    }));
}

function* handleRemoveFromWaitList(action) {
  const selector = (state) => state.get('app').get('waitList').get('notifications');
  const vm_notification_map =  yield select(selector);
  if (!vm_notification_map.has(action.notifyId))
  {
    yield put(actions.remove(action.notifyId));
  }
}

function* handleVmListMessage(action) {
  let { message }= action;
  let status = null;
  switch (message.type) {
    case 'add':
      //TODO Add a toaster from CreateVM
      return;
    case 'change':
      message = message.new_val;
      status = message.power_state.toLowerCase();
      break;
    case 'remove':
      message = message.old_val;
      status = 'removed';
      break;
    case 'initial':
      return;
  }
    const selector = (state) => state.get('app').get('waitList').get(status);
    const selection = yield select(selector);
    if (!selection)
    {
      console.error("BAD POWER STATE/STATUS " + status, "message.type=", message.type);
      return;
    }

    if (selection.has(message.uuid))
    {
      const notifyId = selection.get(message.uuid);
      yield removeFromWaitList(message.uuid, status, notifyId);
    }
    else{ //Handle rebooting
      if (status === 'halted')
      {
        const selector =  (state) => state.get('app').get('waitList').get("rebooted");
        const selection = yield select(selector);
        if (selection.has(message.uuid))
        {
          const notifyId = selection.get(message.uuid);
          //RemoveFromWaitList of rebooted moves it to running
          yield removeFromWaitList(message.uuid, status, notifyId);
        }
        }

    }
}

export function* loginFlow() {
  window.beforeLogin = '/';
  let previousSession = null;
  yield take(LOCATION_CHANGE);
  while (true) { // eslint-disable-line no-constant-condition
    console.log('while true ', new Date());
    const session = authAgent.getSession();
    let location = yield select(makeSelectLocation());
    location = location.pathname;

    if (session !== null)
    {
      if (session !== previousSession) {
        yield put({type: AUTHENTICATED});
      }
      if (previousSession === null) {
        console.log('writing new session');
        previousSession = session;
      }
      console.log('Session:', session);
      if (location === '/login')
      {
        if (window.beforeLogin === '/login' || window.beforeLogin === '/logout')
          window.beforeLogin = '/';
        yield put(push(window.beforeLogin))
      }
      else
      {
        window.beforeLogin = location;
      }
      yield take(LOGOUT);
      try {
        yield call([authAgent,authAgent.logout]);
        yield put({type : LOGGED_OUT});
      }
      catch (e)
      {
        console.log('logout error!', e);
      }
    }
    else
    {
      if (location !== '/login') {
        window.beforeLogin = location;
        yield put(push('/login'));
      }
      const { login, password} = yield take(AUTH);

      try { //context call
        yield call([authAgent,authAgent.auth], login, password);
      }
      catch(e)
      {
        console.log('login error!',e);
      }

    }
  }
}


function socketToChannel(socket) {
  /**
   * this function converts a websocket to a redux saga event channel
   */
  return eventChannel((emit) => {
    socket.onopen = () => {
      console.log('Connection estabished');
    };
    socket.onmessage = (event) => {
      const msg = event.data;
      emit({ message : msg, error : null });
    };
    socket.onclose = (event) => {
      console.log('event channel closed');
      emit(END); //close channel
    };
    socket.onerror = (event) => {
      emit ({message : null,
        error : event.error });

    }
    //Subscriber returns an unsubscribe function
    return () => {
      if (socket.readyState === socket.CONNECTING ||
          socket.readyState === socket.CONNECTED)
      socket.close();
      console.log('websocket closed');
    };
  });
}

function* channelToListenerVmlist(channel)
{
  /**
   * this function listens for VMList messages and puts an action
   */

    while (true) {
      const {message, error} = yield take(channel);
      if (error)
      {
        console.error("Error while getting VMList", error);

      }
      try {
        if (message.trim() !== "")
          yield put(msgVmlist(JSON.parse(message)));
      }
      catch (e)
      {
        console.warn("Error while parsing JSON: ", message);
      }
    }

}
/*
async function connectToWebsocket() {
  const server = new Server('ws://localhost:9999');
  const res = await axios.get("vmlist-example.json");
  const jsons = res.data.split('\n');
  let connCount = 0;
  server.on('connection', _server => {
    connCount++;

    jsons.map(json => {
      server.send(json);
    });
  });

  server.on('close', _server =>
  {
    connCount--;
    if (connCount <= 0) {

      server.stop();
      console.log("stopping server");
    }
  });

}
*/

export function* websocketFlow() {
    let socketChannel = null;
    //yield connectToWebsocket();
    console.log('starting websocket flow...');
    const sock = new WebSocket(
      ((window.location.protocol === "https:") ? "wss://" : "ws://")
      + window.location.host + VMLIST_URL);
    socketChannel = yield call(socketToChannel, sock);

    const {cancel} = yield race({ //run two effects simultaneously
        task: call(channelToListenerVmlist, socketChannel),
        cancel: take(LOGGED_OUT),
        }
    );
    if (cancel) {
      socketChannel.close();
      socketChannel = null;
    }
      //TODO: Bidirectional



}






function* watchLoginFlow() {
  //yield takeEvery(LOCATION_CHANGE, loginFlow);
  yield loginFlow();
}

function* watchWebsocketFlow(){
  yield takeEvery(AUTHENTICATED, websocketFlow);
}


// All sagas to be loaded
export default function* rootSaga () {


  yield takeEvery(VMLIST_MESSAGE, handleVmListMessage);
  //yield all[loginFlow()];
  //yield takeEvery(AUTH, authenticate);
  //yield takeEvery(LOGOUT, logout);
  yield takeEvery(VM_RUN, handleActions);
  yield takeEvery(VM_HALT, handleActions);
  yield takeEvery(VM_DELETE, handleActions);
  yield takeEvery(VM_REBOOT, handleActions);

  yield takeEvery(VM_RUN_ERROR, handleVMErrors);

  yield takeEvery(REMOVE_FROM_WAIT_LIST, handleRemoveFromWaitList);

  yield all([ watchLoginFlow(),
    watchWebsocketFlow() ]);
  //VM_HALT_ERROR: todo!
};



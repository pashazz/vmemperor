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

import { Map } from 'immutable';


import { actions } from 'react-redux-toastr';

import {taskstatus} from "../../api/task";


function* showNotification(title, uuids) {
  //Show a toastr notification. Return its notifyId
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


function* handleRemoveFromWaitList(action) {
  const selector = (state) => state.get('app').get('waitList').get('notifications');
  const vm_notification_map =  yield select(selector);
  if (!vm_notification_map.has(action.notifyId))
  {
    yield put(actions.remove(action.notifyId));
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


function* watchLoginFlow() {
  //yield takeEvery(LOCATION_CHANGE, loginFlow);
  yield loginFlow();
}


// All sagas to be loaded
export default function* rootSaga () {


  yield takeEvery(REMOVE_FROM_WAIT_LIST, handleRemoveFromWaitList);

  yield all([ watchLoginFlow()]);
};



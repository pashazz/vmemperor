import { take, call, put, select, all, takeEvery, takeLatest, apply} from 'redux-saga/effects';
import { AUTH, LOGOUT } from './constants';
import { push, LOCATION_CHANGE} from 'react-router-redux';
import { makeSelectLocation } from './selectors';
import {authAgent} from "../PrivateRoute";


export function* loginFlow() {
  window.beforeLogin = '/';
  while (true) { // eslint-disable-line no-constant-condition
    console.log('while true');
    const session = authAgent.getSession();
    let location = yield select(makeSelectLocation());
    location = location.pathname;

    if (session !== null)
    {
      console.log('Session:', session);
      if (location === '/login')
      {
        yield put(push(window.beforeLogin))
      }
      else
      {
        window.beforeLogin = location;
      }
      yield take(LOGOUT);
      try {
        yield call([authAgent,authAgent.logout]);
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



// All sagas to be loaded
export default function* rootSaga () {
  yield takeEvery(LOCATION_CHANGE, loginFlow)
  //yield all[loginFlow()];
  //yield takeEvery(AUTH, authenticate);
  //yield takeEvery(LOGOUT, logout);
};


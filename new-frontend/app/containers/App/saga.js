import { take, call, put, select, all, takeLatest} from 'redux-saga/effects';
import { AUTH, LOGOUT } from './constants';
import { push, LOCATION_CHANGE} from 'react-router-redux';
import { makeSelectLocation } from './selectors';
import {authAgent} from "../PrivateRoute";


export function* loginFlow() {
  window.beforeLogin = '/';
  //while (true) { // eslint-disable-line no-constant-condition
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
      yield call(authAgent.logout);
    }
    else
    {
      if (location !== '/login') {
        window.beforeLogin = location;
        yield put(push('/login'));
      }
      const { payload } = yield take(AUTH);
      yield call(authAgent.auth, payload);
    }
 // }
}

// All sagas to be loaded
export default function* rootSaga () {
  yield takeLatest(LOCATION_CHANGE, loginFlow)
};

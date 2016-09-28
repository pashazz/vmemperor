import { take, call, put, select } from 'redux-saga/effects';
import { AUTH, LOGOUT } from './constants';
import { push } from 'react-router-redux';
import { selectCurrentLocation } from './selectors';
import vmempAPI from 'api/vmemp-api';

export function* loginFlow() {
  window.beforeLogin = '/';
  while (true) { // eslint-disable-line no-constant-condition
    const session = yield call(vmempAPI.user.session);
    const location = yield select(selectCurrentLocation());
    if (session !== null) {
      if (location === '/login') {
        yield put(push(window.beforeLogin));
      } else {
        window.beforeLogin = location;
      }
      yield take(LOGOUT);
      yield call(vmempAPI.user.logout);
    } else {
      if (location !== '/login') {
        window.beforeLogin = location;
        yield put(push('/login'));
      }
      const { payload } = yield take(AUTH);
      yield call(vmempAPI.user.auth, payload);
    }
  }
}

// All sagas to be loaded
export default [
  loginFlow,
];

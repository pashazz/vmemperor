import { call, put, select, fork, take, cancel } from 'redux-saga/effects';
import { delay } from 'redux-saga';
import { LOCATION_CHANGE } from 'react-router-redux';
// import { CLEAR_VM } from './constants';
import { setVMStates } from './actions';
import { selectVMIds, selectVMs } from './selectors';
// import { info, suc, err } from 'containers/App/actions';
import localStorage from 'store';
import vmempAPI from 'api/vmemp-api';

export function* getVMStates(vmIds) {
  const response = yield call(vmempAPI.vm.status, vmIds);
  if (response.data) {
    yield put(setVMStates(response.data));
  }
}

export function* updateFlow() {
  while (true) { // eslint-disable-line no-constant-condition
    const vmIds = yield select(selectVMIds());
    if (vmIds.length > 0) {
      yield* getVMStates(vmIds);
      yield* saveLocal();
    }
    yield call(delay, 5000);
  }
}

export function* loadLocal() {
  const vms = localStorage.get('vm-history') || {};
  yield put(setVMStates(vms));
}

export function* saveLocal() {
  const vms = yield select(selectVMs());
  localStorage.set('vm-history', vms.toJS());
}

export function* mainFlow() {
  yield* loadLocal();
  const updateWatcher = yield fork(updateFlow);
  yield take(LOCATION_CHANGE);
  yield cancel(updateWatcher);
  yield* saveLocal();
}

// All sagas to be loaded
export default [
  mainFlow,
];

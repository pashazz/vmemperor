import { actionChannel, call, put, spawn, fork, take, cancel } from 'redux-saga/effects';
import { LOCATION_CHANGE } from 'react-router-redux';
import { RUN_VM_ACTION } from './constants';
import { setVMList } from './actions';
import { info, suc, err } from 'containers/App/actions';
import vmempAPI from 'api/vmemp-api';

export function* getVMList() {
  yield put(info('Getting VM list...'));
  const response = yield call(vmempAPI.vm.list);
  if (response.data) {
    yield put(suc('Got VM list'));
    yield put(setVMList(response.data));
  } else {
    yield put(err('Could not get VM list!'));
  }
}

export function* runSingleAction({ name, vm }) {
  yield put(info(`Trying to ${name} ${vm.name()}`));
  const response = yield call(vmempAPI.vm[name], vm);
  if (response.data) {
    yield put(suc(`For ${vm.name()}: ${response.data.details}`));
  }
  if (response.err) {
    yield put(err(`${name} failed for ${vm.name()}`));
  }
  yield spawn(getVMList);
}

export function* actionsFlow() {
  const chan = yield actionChannel(RUN_VM_ACTION);
  while (true) { // eslint-disable-line no-constant-condition
    const action = yield take(chan);
    yield spawn(runSingleAction, action);
  }
}

export function* mainFlow() {
  yield spawn(getVMList);
  const watcher = yield fork(actionsFlow);
  yield take(LOCATION_CHANGE);
  yield cancel(watcher);
}

// All sagas to be loaded
export default [
  mainFlow,
];

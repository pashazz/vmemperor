import { actionChannel, call, put, select, spawn, fork, take, cancel } from 'redux-saga/effects';
import { LOCATION_CHANGE } from 'react-router-redux';
import { CREATE_VM } from './constants';
import { setPools } from './actions';
import { makeSelectPools } from './selectors';
import { info, suc, err } from 'containers/App/actions';
import localStorage from 'store';
import list_pools from 'api/list_pools';

export function* getPoolList() {
  const currentPools = yield select(makeSelectPools());
  if (currentPools.size === 0) {
    const response = yield call(list_pools);
    if (response.data) {
      yield put(setPools(response.data));
    }
  }
}

function updateStorage({ uuid = false }) {
  if (uuid) {
    const vms = localStorage.get('vm-history') || {};
    localStorage.set('vm-history', { ...vms, [uuid]: {} });
  }
}

export function* runCreatinon(form) {
  yield put(info(`Trying to create ${form.hostname}`));
  const response = yield call(vmempAPI.vm.create, form);
  if (response.data) {
    yield put(suc(`For ${form.hostname}: ${response.data.details}`));
    updateStorage(response.data);
  }
  if (response.err) {
    yield put(err(`Creation failed for ${form.hostname}`));
  }
  yield spawn(getPoolList);
}

export function* actionsFlow() {
  const chan = yield actionChannel(CREATE_VM);
  while (true) { // eslint-disable-line no-constant-condition
    const { form } = yield take(chan);
    yield spawn(runCreatinon, form);
  }
}

export function* mainFlow() {
  yield spawn(getPoolList);
  const watcher = yield fork(actionsFlow);
  yield take(LOCATION_CHANGE);
  yield cancel(watcher);
}

// All sagas to be loaded
export default [
  mainFlow,
];

import { actionChannel, call, put, spawn, fork, take, cancel } from 'redux-saga/effects';
import { RUN_TEMPLATE_ACTION } from './constants';
import { LOCATION_CHANGE } from 'react-router-redux';
import { setTemplateList } from './actions';
import { info, suc, err } from 'containers/App/actions';
import vmempAPI from 'api/vmemp-api';

export function* getTemplateList() {
  yield put(info('Getting Template list...'));
  const response = yield call(vmempAPI.template.list);
  if (response.data) {
    yield put(suc('Got Template list'));
    yield put(setTemplateList(response.data));
  } else {
    yield put(err('Could not get Template list!'));
  }
}

export function* runSingleAction({ name, template }) {
  yield put(info(`Trying to ${name} ${template.name()}`));
  const response = yield call(vmempAPI.template[name], template);
  if (response.data) {
    yield put(suc(`For ${template.name()}: ${response.data.details}`));
  }
  if (response.err) {
    yield put(err(`${name} failed for ${template.name()}`));
  }
  yield spawn(getTemplateList);
}

export function* actionsFlow() {
  const chan = yield actionChannel(RUN_TEMPLATE_ACTION);
  while (true) { // eslint-disable-line no-constant-condition
    const action = yield take(chan);
    yield spawn(runSingleAction, action);
  }
}

export function* mainFlow() {
  yield spawn(getTemplateList);
  const watcher = yield fork(actionsFlow);
  yield take(LOCATION_CHANGE);
  yield cancel(watcher);
}

// All sagas to be loaded
export default [
  mainFlow,
];

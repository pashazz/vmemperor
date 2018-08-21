import { all, call, put, select } from 'redux-saga/effects';
import playbooks from "../../api/playbook";
import {setPlaybooks} from "./actions";

function* getPlaybooks() {
  const data = yield call(playbooks);
  yield put(setPlaybooks(data.data))
}


// Individual exports for testing
export default function* defaultSaga() {
  yield all([getPlaybooks()]);
}

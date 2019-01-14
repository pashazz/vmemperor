import { take, call, put, select, takeEvery } from 'redux-saga/effects';

import {vm_deselect} from "./actions";
import {VMLIST_MESSAGE} from "../App/constants";

function* handleVMRemoval(action) {
  if (action.message.type !== 'remove')
    return;

  yield put(vm_deselect(action.message.old_val.uuid));


}

export default  function* rootSaga () {
  yield takeEvery(VMLIST_MESSAGE, handleVMRemoval);
}

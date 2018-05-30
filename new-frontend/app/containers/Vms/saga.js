import { take, call, put, select, takeEvery } from 'redux-saga/effects';
import {startStopVm } from 'api/vm';
import {VM_RUN} from "./constants";

function* vmRun (action){
  try {
    const data = yield  call(startStopVm, action.uuid, true);
    console.log('vmRun: data:', data);
  }
  catch (e)
  {
    console.log("vmRun: exception: ", e);
  }



}

export default function* rootSaga() {
  yield takeEvery(VM_RUN, vmRun);
};

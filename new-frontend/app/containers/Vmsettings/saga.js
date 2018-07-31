 import { takeEvery, call, put, select } from 'redux-saga/effects';

// Individual exports for testing


import {VM_CONVERT, VM_REQUEST_DISKINFO} from "./constants";
import {VM_RUN_ERROR} from "../App/constants";
 import {convert} from "../../api/vm";
 import {vm_run_error} from "../App/actions";
 import {handleVMErrors} from '../App/saga';
 import {diskInfo} from "../../api/vm";
 import {setDiskInfo} from "./actions";

 const actionHandlers = {
  [VM_CONVERT]: {
    onError: vm_run_error,
    handler: function* (args)
    {
      const data = yield call(convert, args.uuid, args.mode);
      console.log("convert: data:", data);
    }
  }
};


 function* handleActions(action) {
   const {type, ...rest} = action;
   const handler = actionHandlers[type];
   console.log("vmsettings: handle" + type);
   try {
     yield handler.handler(rest);
   }
   catch (e) {
     if (e.response) {
       console.log(e.response);
       if (e.response.status === 400) {
         //Handle error
         if (e.response.data.details) {
           yield put(handler.onError(e.response.data.details));
         }
         else {
           console.error("Unhandled Response Error: ", e.response)
         }
       }
     }
   }
 }


 function* requestDiskInfo(action) {
   const {uuid} = action;
   const response = yield call(diskInfo, uuid);
   if (response.data) {
     yield put(setDiskInfo(response.data));
   }
 }



export default function* rootSaga() {
  // See example in containers/HomePage/saga.js
  yield takeEvery(VM_CONVERT, handleActions);
  yield takeEvery(VM_REQUEST_DISKINFO, requestDiskInfo);

}

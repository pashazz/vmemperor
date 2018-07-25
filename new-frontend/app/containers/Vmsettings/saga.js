 import { takeEvery, call, put, select } from 'redux-saga/effects';

// Individual exports for testing


import {VM_CONVERT} from "./constants";
import {VM_RUN_ERROR} from "../App/constants";
 import {convert} from "../../api/vm";
 import {vm_run_error} from "../App/actions";
 import {handleVMErrors} from '../App/saga';

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
   console.log("hello");
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



export default function* rootSaga() {
  // See example in containers/HomePage/saga.js
  yield takeEvery(VM_CONVERT, handleActions);

  yield takeEvery(VM_RUN_ERROR, handleVMErrors);

}

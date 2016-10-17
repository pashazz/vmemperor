// These are the pages you can go to.
// They are all wrapped in the App component, which should contain the navbar etc
// See http://blog.mxstbr.com/2016/01/react-apps-with-pages for more information
// about the code splitting business
import { getAsyncInjectors } from 'utils/asyncInjectors';

import login from 'containers/LoginPage/route';
import vms from 'containers/VMs/route';
import templates from 'containers/Templates/route';
import createVM from 'containers/CreateVM/route';
import history from 'containers/History/route';

export default function createRoutes(store) {
  // Create reusable async injectors using getAsyncInjectors factory
  const { injectReducer, injectSagas } = getAsyncInjectors(store); // eslint-disable-line no-unused-vars

  return [
    {
      path: '/',
      name: 'home',
      onEnter(next, replace) {
        replace('/vms');
      },
    },
    login(injectReducer, injectSagas),
    vms(injectReducer, injectSagas),
    templates(injectReducer, injectSagas),
    createVM(injectReducer, injectSagas),
    history(injectReducer, injectSagas),
  ];
}

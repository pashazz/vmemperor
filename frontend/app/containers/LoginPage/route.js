import { errorLoading, loadModule } from 'utils/asyncInjectors';

export default function route(injectReducer, injectSagas) {
  return {
    path: 'login',
    name: 'login',
    getComponent(nextState, cb) {
      const importModules = Promise.all([
        System.import('containers/LoginPage/reducer'),
        System.import('containers/LoginPage/sagas'),
        System.import('containers/LoginPage'),
      ]);

      const renderRoute = loadModule(cb);

      importModules.then(([reducer, sagas, component]) => {
        injectReducer('login', reducer.default);
        injectSagas(sagas.default);

        renderRoute(component);
      });

      importModules.catch(errorLoading);
    },
  };
}

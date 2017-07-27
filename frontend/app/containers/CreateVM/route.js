import { errorLoading, loadModule } from 'utils/asyncInjectors';

export default function route(injectReducer, injectSagas) {
  return {
    path: 'create-vm',
    name: 'createVM',
    getComponent(nextState, cb) {
      const importModules = Promise.all([
        System.import('containers/CreateVM/reducer'),
        System.import('containers/CreateVM/sagas'),
        System.import('containers/CreateVM'),
      ]);

      const renderRoute = loadModule(cb);

      importModules.then(([reducer, sagas, component]) => {
        injectReducer('create', reducer.default);
        injectSagas(sagas.default);

        renderRoute(component);
      });

      importModules.catch(errorLoading);
    },
  };
}

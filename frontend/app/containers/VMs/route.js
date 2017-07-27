import { errorLoading, loadModule } from 'utils/asyncInjectors';

export default function route(injectReducer, injectSagas) {
  return {
    path: 'vms',
    name: 'vms',
    getComponent(nextState, cb) {
      const importModules = Promise.all([
        System.import('containers/VMs/reducer'),
        System.import('containers/VMs/sagas'),
        System.import('containers/VMs'),
      ]);

      const renderRoute = loadModule(cb);

      importModules.then(([reducer, sagas, component]) => {
        injectReducer('vms', reducer.default);
        injectSagas(sagas.default);

        renderRoute(component);
      });

      importModules.catch(errorLoading);
    },
  };
}

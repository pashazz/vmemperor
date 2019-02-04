/**
 *
 * Asynchronously loads the component for Playbooks
 *
 */

import Loadable from 'react-loadable';

export default Loadable({
  loader: () => import('./index'),
  loading: () => null,
});

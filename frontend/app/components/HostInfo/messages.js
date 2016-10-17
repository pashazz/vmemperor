/*
 * HostInfo Messages
 *
 * This contains all the text for the HostInfo component.
 */
import { defineMessages } from 'react-intl';

export default defineMessages({
  host: {
    id: 'app.components.HostInfo.memory.total',
    defaultMessage: 'Host: {name}',
  },
  memory: {
    total: {
      id: 'app.components.HostInfo.memory.total',
      defaultMessage: 'Memory total',
    },
    available: {
      id: 'app.components.HostInfo.memory.available',
      defaultMessage: 'available',
    },
    free: {
      id: 'app.components.HostInfo.memory.free',
      defaultMessage: 'physically free',
    },
  },
  xen: {
    running: {
      id: 'app.components.HostInfo.xen.running',
      defaultMessage: 'Running VMs now',
    },
    software: {
      id: 'app.components.HostInfo.xen.software',
      defaultMessage: 'Software installed',
    },
    version: {
      id: 'app.components.HostInfo.xen.version',
      defaultMessage: 'Software version',
    },
    xenVersion: {
      id: 'app.components.HostInfo.xen.xenVersion',
      defaultMessage: 'Xen version',
    },
  },
  processor: {
    model: {
      id: 'app.components.HostInfo.processor.model',
      defaultMessage: 'Processor model',
    },
    frequency: {
      id: 'app.components.HostInfo.processor.frequency',
      defaultMessage: 'frequency',
    },
    cores: {
      id: 'app.components.HostInfo.processor.cores',
      defaultMessage: 'cores',
    },
  },
});

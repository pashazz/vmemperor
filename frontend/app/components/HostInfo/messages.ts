/*
 * HostInfo Messages
 *
 * This contains all the text for the HostInfo component.
 */
import { defineMessages } from 'react-intl';
import MessageDescriptor = ReactIntl.FormattedMessage.MessageDescriptor;

export default defineMessages({
  host: {
    id: 'app.components.HostInfo.memory.total',
    defaultMessage: 'Host: {name}',
  },
    memory_total: {
      id: 'app.components.HostInfo.memory.total',
      defaultMessage: 'Memory total',
    },
    memory_available: {
      id: 'app.components.HostInfo.memory.available',
      defaultMessage: 'available',
    },
    memory_free: {
      id: 'app.components.HostInfo.memory.free',
      defaultMessage: 'physically free',
    },


    vms_running: {
      id: 'app.components.HostInfo.xen.running',
      defaultMessage: 'Running VMs now',
    },
    product_name: {
      id: 'app.components.HostInfo.xen.software',
      defaultMessage: 'Product name',
    },
    product_version: {
      id: 'app.components.HostInfo.xen.version',
      defaultMessage: 'Product version',
    },
    xen_version: {
      id: 'app.components.HostInfo.xen.xenVersion',
      defaultMessage: 'Xen version',
    },
    processor_model: {
      id: 'app.components.HostInfo.processor.model',
      defaultMessage: 'Processor model',
    },
    processor_frequency: {
      id: 'app.components.HostInfo.processor.frequency',
      defaultMessage: 'frequency',
    },
    processor_cores: {
      id: 'app.components.HostInfo.processor.cores',
      defaultMessage: 'cores',
    },
});


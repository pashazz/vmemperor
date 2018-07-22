import { Record } from 'immutable';


const VM = Record(
  {
    name_label: '',
    name_description: '',
    networks: {},
    start_time: '',
    install_time: '',
    domain_type: '',
    access: [],
    disks: [],
    uuid: '',
    ref: '',
    memory_actual: '',

  });

export default VM;

//TODO: T.shape

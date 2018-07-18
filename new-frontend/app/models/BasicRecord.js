import { Record } from 'immutable';

//Format is determined in xenadapter/disk.py class ISO
const BasicRecord = Record({
  name_label: '',
  ref: '',
  uuid: ''
});

export default BasicRecord;

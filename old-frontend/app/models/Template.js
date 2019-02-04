import { Record } from 'immutable';
import T from 'prop-types';
import {Access} from "./types";

const Template = Record({
  hvm: false,
  name_label: '',
  os_kind: '',
  ref: '',
  uuid: '',

});

Template.prototype.shape = T.shape(
  {
    uuid: T.string.isRequired,
    name_label: T.string.isRequired,
    os_kind: T.oneOf(['', 'ubuntu', 'debian', 'centos']).isRequired,
    ref: T.string.isRequired,
    hvm: T.bool.isRequired,
  });

Template.prototype.key = () => { return this.uuid };

export default Template;

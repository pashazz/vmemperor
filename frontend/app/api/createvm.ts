import axios from 'axios'

export interface CreateVM {
  template: string, //Template UUID
  name_label: string, //Name label
  name_description: string, //Description
  storage: string, //S

}

const createvm = async (form) =>
{
  return await axios.post('api/createvm', form);
};

export default createvm;

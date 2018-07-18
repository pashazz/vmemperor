import axios from 'axios'
const createvm = async (form) =>
{
  return await axios.post('api/createvm', form);
};

export default createvm;

import axios from 'axios'
const playbooks = async () =>
{
  return await axios.get('/api/playbooks');
};

export default playbooks;
